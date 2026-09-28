"""
Bibliometrik analiz iş yürütücüsü.
Daemon thread içinde parse → analyze → PDF → S3 → email akışını yönetir.
"""
import gc
import threading
import logging

from django.core.mail import EmailMessage
from django.conf import settings
from django.db import close_old_connections
from django.utils.translation import gettext

from forum.i18n_utils import recipient_language

logger = logging.getLogger(__name__)

# Upload tipi işler için dosya içerikleri bellekte tutulur (enqueue öncesi set edilir)
_pending_file_contents: dict = {}


def _in_user_language(job_id: str, body) -> None:
    """Worker thread'i dili bilmez → iş, başlatan kullanıcının dil tercihiyle
    (Profile.preferred_language) çalışır: PDF rapor, hata mesajları ve e-postalar o dilde.
    Sunucu yeniden başlasa da kaybolmaz (dil profilde)."""
    from bibliometrics.models import BibliometricJob
    job = BibliometricJob.objects.select_related('user__profile').filter(id=job_id).first()
    with recipient_language(getattr(job, 'user', None)):
        body(job_id)


def _execute_job(job_id: str) -> None:
    """Global kuyruk worker'ı — upload tipi analiz (kullanıcının dilinde)."""
    _in_user_language(job_id, _execute_job_body)


def _execute_job_openalex(job_id: str) -> None:
    """Global kuyruk worker'ı — OpenAlex tipi analiz (kullanıcının dilinde)."""
    _in_user_language(job_id, _execute_job_openalex_body)


def _execute_job_body(job_id: str) -> None:
    """Upload tipi analiz, senkron."""
    from bibliometrics.models import BibliometricJob
    from bibliometrics.services.parser import parse_file, _deduplicate_and_filter
    from bibliometrics.services.analyzer import run_all_analyses
    from bibliometrics.services.pdf_builder import build_demo_pdf, build_full_pdf
    from bibliometrics.services.report_notes import build_report_notes
    from forum.s3_utils import upload_bytes_to_s3

    close_old_connections()
    file_content = _pending_file_contents.pop(job_id, None)

    try:
        job = BibliometricJob.objects.get(id=job_id)

        if file_content is None:
            job.mark_failed(gettext('Dosya içeriği bulunamadı. Lütfen dosyayı tekrar yükleyin.'))
            return

        job.mark_running()

        contents = file_content if isinstance(file_content, list) else [file_content]
        all_records = []
        fmt = 'csv_auto'
        stats = {}
        for content in contents:
            recs, detected_fmt = parse_file(content, stats=stats)
            all_records.extend(recs)
            fmt = detected_fmt

        records = _deduplicate_and_filter(all_records, stats) if len(contents) > 1 else all_records

        if not records:
            job.mark_failed(gettext('Dosyadan kayıt okunamadı. Format desteklenmiyor olabilir.'))
            return

        skipped = []
        figures = run_all_analyses(records, skipped=skipped)
        if not figures:
            job.mark_failed(gettext('Analizler üretilemedi. Veri yetersiz olabilir.'))
            return

        notes = build_report_notes(records, stats=stats, skipped=skipped, source={
            'kind': 'file',
            'format': dict(BibliometricJob.FORMAT_CHOICES).get(fmt, fmt),
            'files': len(contents),
        })
        demo_pdf_bytes = build_demo_pdf(figures[:3], total_records=len(records), filename=job.original_filename)
        full_pdf_bytes = build_full_pdf(figures, total_records=len(records), filename=job.original_filename,
                                        notes=notes)

        n_figures = len(figures)
        del figures
        gc.collect()

        demo_url = upload_bytes_to_s3(demo_pdf_bytes, f'bibliometrics/demo/{job.id}.pdf', 'application/pdf')
        full_url = upload_bytes_to_s3(full_pdf_bytes, f'bibliometrics/full/{job.id}.pdf', 'application/pdf')

        close_old_connections()
        job.mark_completed(
            total_records=len(records),
            file_format=fmt,
            demo_pdf_url=demo_url or '',
            full_pdf_url=full_url or '',
        )
        job._demo_pdf_bytes = demo_pdf_bytes
        logger.info(f'[bibliometrics] Job {job_id} tamamlandı. {len(records)} kayıt, {n_figures} analiz.')

    except BibliometricJob.DoesNotExist:
        logger.error(f'[bibliometrics] Job bulunamadı: {job_id}')
    except Exception as e:
        logger.error(f'[bibliometrics] Job hatası [{job_id}]: {e}', exc_info=True)
        try:
            close_old_connections()
            job = BibliometricJob.objects.get(id=job_id)
            job.mark_failed(str(e))
        except Exception:
            pass


def _execute_job_openalex_body(job_id: str) -> None:
    """OpenAlex tipi analiz, senkron."""
    close_old_connections()
    from bibliometrics.models import BibliometricJob
    from bibliometrics.services.parser import parse_openalex_json
    from bibliometrics.services.analyzer import run_all_analyses
    from bibliometrics.services.pdf_builder import build_demo_pdf, build_full_pdf
    from bibliometrics.services.report_notes import build_report_notes
    from forum.models import SiteSettings
    from forum.s3_utils import upload_bytes_to_s3

    try:
        job = BibliometricJob.objects.select_related('alex_job').get(id=job_id)
        job.mark_running()

        alex_job = job.alex_job
        if not alex_job or not alex_job.all_results:
            job.mark_failed(gettext('OpenAlex verisi bulunamadı veya boş.'))
            return

        stats = {}
        records = parse_openalex_json(alex_job.all_results, stats=stats)
        if not records:
            job.mark_failed(gettext('OpenAlex verisinden kayıt okunamadı.'))
            return

        if len(records) < 100:
            job.mark_failed(gettext('Bibliometrik analiz için en az 100 kayıt gereklidir (bulunan: {count}).').format(count=len(records)))
            return

        skipped = []
        figures = run_all_analyses(records, skipped=skipped)
        if not figures:
            job.mark_failed(gettext('Analizler üretilemedi. Veri yetersiz olabilir.'))
            return

        # Sınır çekim anındaki değil şimdiki ayar — admin arada değiştirmediyse aynıdır
        notes = build_report_notes(records, stats=stats, skipped=skipped, source={
            'kind': 'openalex',
            'found': alex_job.total_results,
            'fetched': len(alex_job.all_results),
            'max_records': SiteSettings.load().scrap_max_records or 5000,
        })
        demo_pdf_bytes = build_demo_pdf(figures[:3], total_records=len(records), filename=job.original_filename)
        full_pdf_bytes = build_full_pdf(figures, total_records=len(records), filename=job.original_filename,
                                        notes=notes)

        n_figures = len(figures)
        del figures
        gc.collect()

        demo_url = upload_bytes_to_s3(demo_pdf_bytes, f'bibliometrics/demo/{job.id}.pdf', 'application/pdf')
        full_url = upload_bytes_to_s3(full_pdf_bytes, f'bibliometrics/full/{job.id}.pdf', 'application/pdf')

        close_old_connections()
        job.mark_completed(
            total_records=len(records),
            file_format='openalex_json',
            demo_pdf_url=demo_url or '',
            full_pdf_url=full_url or '',
        )

        logger.info(f'[bibliometrics] OpenAlex job {job_id} tamamlandı. {len(records)} kayıt, {n_figures} analiz.')
        send_demo_email_async(str(job.id), demo_pdf_bytes)

    except BibliometricJob.DoesNotExist:
        logger.error(f'[bibliometrics] Job bulunamadı: {job_id}')
    except Exception as e:
        logger.error(f'[bibliometrics] OpenAlex job hatası [{job_id}]: {e}', exc_info=True)
        try:
            job = BibliometricJob.objects.get(id=job_id)
            job.mark_failed(str(e))
        except Exception:
            pass


def run_bibliometric_job(job_id: str, file_content) -> None:
    """Dosya içeriğini bellekte saklar ve global kuyruğa ekler."""
    _pending_file_contents[job_id] = file_content
    from analizdestek.job_queue import enqueue
    enqueue('bibliometrics', job_id)


def run_bibliometric_job_from_openalex(job_id: str) -> None:
    """Global kuyruğa OpenAlex tipi bibliometrik analiz ekler."""
    from analizdestek.job_queue import enqueue
    enqueue('bibliometrics_openalex', job_id)


def _full_report_lines(site_url: str, job) -> list:
    """E-postalardaki "TAM RAPOR" bölümü — aktif dilde (recipient_language içinde çağrılır).
    TR: sipariş sayfası (Türk IBAN / TL). EN/DE: sipariş yok → proje talebi (kullanıcı kararı
    27 Eylül 2026)."""
    from django.urls import reverse
    from django.utils.translation import get_language
    lines = [
        '─' * 37,
        gettext('TAM RAPOR (15 Analiz)'),
        '─' * 37,
        '  • ' + gettext('Yayın Trendi + Büyüme Oranı'),
        '  • ' + gettext('En Verimli Yazarlar + Lotka Kanunu'),
        '  • ' + gettext('Anahtar Kelime Bulutu + Eş-Oluşum Ağı'),
        '  • ' + gettext('Anahtar Kelime Zaman Trendi'),
        '  • ' + gettext('En Çok Atıf Alan Yayınlar'),
        '  • ' + gettext('En Çok Yayın Yapılan Dergiler'),
        '  • ' + gettext('Kurum / Ülke Dağılımı + İşbirliği Ağı'),
        '  • ' + gettext('Yazar İşbirliği Ağı'),
        '  • ' + gettext('Yayın Türleri + Atıf Analizi + H-index'),
        '  • ' + gettext('Yıllık Atıf Trendi') + '\n',
    ]
    if (get_language() or 'tr')[:2] == 'tr':
        lines += [gettext('Sipariş oluşturmak için:'), f'  {site_url}/bibliometrics/siparis/{job.id}/\n']
    else:
        lines += [gettext('Tam rapor için proje talebi bırakın, ücretsiz değerlendirelim:'),
                  f"  {site_url}{reverse('proje_talebi')}?source=bibliometrics\n"]
    return lines


def _source_sentence(job) -> str:
    """OpenAlex kaynaklı işte kullanıcı dosya yüklemedi — cümle kaynağa göre."""
    if getattr(job, 'source', '') == 'openalex':
        return gettext('"{name}" OpenAlex aramanız başarıyla analiz edildi.').format(name=job.original_filename)
    return gettext('Yüklediğiniz "{name}" dosyası başarıyla analiz edildi.').format(name=job.original_filename)


def send_demo_email_async(job_id: str, demo_pdf_bytes: bytes = None) -> None:
    """Demo PDF emailini arka planda gönder."""

    def _run():
        from bibliometrics.models import BibliometricJob
        from bibliometrics.services.parser import parse_file
        from bibliometrics.services.analyzer import run_all_analyses
        from bibliometrics.services.pdf_builder import build_demo_pdf

        try:
            job = BibliometricJob.objects.get(id=job_id)
            user = job.user
            site_url = getattr(settings, 'SITE_URL', 'https://analizus.com')

            # PDF bytes yoksa S3'ten tekrar oluşturmak yerine yeniden üret (küçük dosya)
            pdf_bytes = demo_pdf_bytes
            if not pdf_bytes:
                logger.warning(f'[bibliometrics_email] Demo PDF bytes yok, email gönderilemiyor: {job_id}')
                return

            with recipient_language(user):
                subject = gettext('Bibliometrik Analiz - Demo Rapor')
                body_lines = [
                    gettext('Merhaba {name},').format(name=user.first_name or user.username) + '\n',
                    _source_sentence(job) + '\n',
                    gettext('Toplam Kayıt: {count}').format(count=job.total_records),
                    *([gettext('Dosya Formatı: {fmt}').format(fmt=job.get_file_format_display())] if job.source != 'openalex' else []),
                    '',
                    gettext('Demo raporunuz (3 temel analiz) ekte PDF olarak sunulmuştur.') + '\n',
                    *_full_report_lines(site_url, job),
                    '---',
                    gettext('Bu bir otomatik bildirimdir.'),
                    gettext('Analizus - Akademik Veri Üssü'),
                ]

            email = EmailMessage(
                subject=subject,
                body='\n'.join(body_lines),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email.attach(
                f'bibliometric_demo_{job.id}.pdf',
                pdf_bytes,
                'application/pdf',
            )
            email.send()

            job.demo_email_sent = True
            job.save(update_fields=['demo_email_sent'])
            logger.info(f'[bibliometrics_email] Demo email gönderildi: {user.email}')

        except Exception as e:
            logger.error(f'[bibliometrics_email] Demo email hatası [{job_id}]: {e}', exc_info=True)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()


def send_demo_email_via_url(job_id: str) -> None:
    """
    Demo PDF S3 URL'si ile email gönder (arka planda).
    Dosya içeriği olmadığında (tekrar yükleme yerine) URL ile bildirim yap.
    """
    def _run():
        from bibliometrics.models import BibliometricJob

        try:
            job = BibliometricJob.objects.get(id=job_id)
            user = job.user
            site_url = getattr(settings, 'SITE_URL', 'https://analizus.com')

            with recipient_language(user):
                subject = gettext('Bibliometrik Analiz - Demo Raporunuz Hazır')
                body_lines = [
                    gettext('Merhaba {name},').format(name=user.first_name or user.username),
                    '',
                    _source_sentence(job),
                    '',
                    gettext('Toplam Kayıt: {count}').format(count=job.total_records),
                    '',
                    gettext('Demo raporunuzu (3 analiz içeren PDF) aşağıdaki bağlantıdan indirebilirsiniz:'),
                    job.demo_pdf_url,
                    '',
                    gettext('Not: İndirme bağlantısı 3 gün geçerlidir.'),
                    '',
                    *_full_report_lines(site_url, job),
                    '---',
                    gettext('Analizus - Akademik Veri Üssü') + ' | analizus.com',
                ]

            email = EmailMessage(
                subject=subject,
                body='\n'.join(body_lines),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email.send()

            job.demo_email_sent = True
            job.save(update_fields=['demo_email_sent'])
            logger.info(f'[bibliometrics_email] Demo URL emaili gönderildi: {user.email}')

        except Exception as e:
            logger.error(f'[bibliometrics_email] URL email hatası [{job_id}]: {e}', exc_info=True)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()


def send_order_results_email(order_id: str) -> bool:
    """
    Sipariş onaylandıktan sonra tam raporu email ile gönder.
    Admin panelinden çağrılır (senkron).
    """
    from bibliometrics.models import BibliometricOrder
    from django.utils import timezone
    from forum.s3_utils import upload_bytes_to_s3

    try:
        order = BibliometricOrder.objects.select_related('job', 'user').get(id=order_id)
        job = order.job
        user = order.user
        site_url = getattr(settings, 'SITE_URL', 'https://analizus.com')

        if not job.full_pdf_url:
            logger.error(f'[bibliometrics_order_email] full_pdf_url boş: job={job.id}')
            return False

        # S3 URL'si varsa email body'ye yaz, PDF'i attachment olarak ekleyemeyiz (binary büyük olabilir)
        # Bunun yerine S3 URL'si veririz
        with recipient_language(user):
            subject = gettext('Bibliometrik Analiz - Tam Rapor Hazır!')
            body_lines = [
                gettext('Merhaba {name},').format(name=user.first_name or user.username) + '\n',
                gettext('Bibliometrik analiz siparişiniz onaylandı ve tam raporunuz hazırlandı.') + '\n',
                gettext('Sipariş No: #{number}').format(number=str(order.id)[:8]),
                gettext('Kaynak: {name}').format(name=job.original_filename),
                gettext('Toplam Kayıt: {count}').format(count=job.total_records),
                gettext('Ödenen Tutar: {amount} TL').format(amount=order.total_price) + '\n',
                gettext('Tam raporunuzu (15 analiz içeren PDF) aşağıdaki bağlantıdan indirebilirsiniz:'),
                f'  {job.full_pdf_url}\n',
                gettext('Not: İndirme bağlantısı 3 gün geçerlidir.') + '\n',
                '---',
                gettext('Bu bir otomatik bildirimdir.'),
                gettext('Analizus - Akademik Veri Üssü'),
            ]

        email_msg = EmailMessage(
            subject=subject,
            body='\n'.join(body_lines),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email_msg.send()

        order.results_email_sent = True
        order.results_email_sent_at = timezone.now()
        order.status = 'completed'
        order.save(update_fields=['results_email_sent', 'results_email_sent_at', 'status'])

        logger.info(f'[bibliometrics_order_email] Tam rapor emaili gönderildi: {user.email}')
        return True

    except BibliometricOrder.DoesNotExist:
        logger.error(f'[bibliometrics_order_email] Order bulunamadı: {order_id}')
        return False
    except Exception as e:
        logger.error(f'[bibliometrics_order_email] Hata [{order_id}]: {e}', exc_info=True)
        return False
