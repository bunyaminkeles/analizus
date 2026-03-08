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

logger = logging.getLogger(__name__)

# Upload tipi işler için dosya içerikleri bellekte tutulur (enqueue öncesi set edilir)
_pending_file_contents: dict = {}


def _execute_job(job_id: str) -> None:
    """Global kuyruk worker'ı tarafından çağrılır — upload tipi analiz, senkron."""
    from bibliometrics.models import BibliometricJob
    from bibliometrics.services.parser import parse_file, _deduplicate_and_filter
    from bibliometrics.services.analyzer import run_all_analyses
    from bibliometrics.services.pdf_builder import build_demo_pdf, build_full_pdf
    from forum.s3_utils import upload_bytes_to_s3

    close_old_connections()
    file_content = _pending_file_contents.pop(job_id, None)

    try:
        job = BibliometricJob.objects.get(id=job_id)

        if file_content is None:
            job.mark_failed('Dosya içeriği bulunamadı. Lütfen dosyayı tekrar yükleyin.')
            return

        job.mark_running()

        contents = file_content if isinstance(file_content, list) else [file_content]
        all_records = []
        fmt = 'csv_auto'
        for content in contents:
            recs, detected_fmt = parse_file(content)
            all_records.extend(recs)
            fmt = detected_fmt

        records = _deduplicate_and_filter(all_records) if len(contents) > 1 else all_records

        if not records:
            job.mark_failed('Dosyadan kayıt okunamadı. Format desteklenmiyor olabilir.')
            return

        figures = run_all_analyses(records)
        if not figures:
            job.mark_failed('Analizler üretilemedi. Veri yetersiz olabilir.')
            return

        demo_pdf_bytes = build_demo_pdf(figures[:3], total_records=len(records), filename=job.original_filename)
        full_pdf_bytes = build_full_pdf(figures, total_records=len(records), filename=job.original_filename)

        n_figures = len(figures)
        try:
            import matplotlib.pyplot as plt
            plt.close('all')
        except Exception:
            pass
        del figures
        gc.collect()

        demo_url = upload_bytes_to_s3(demo_pdf_bytes, f'bibliometrics/demo/{job.id}.pdf', 'application/pdf')
        full_url = upload_bytes_to_s3(full_pdf_bytes, f'bibliometrics/full/{job.id}.pdf', 'application/pdf')

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
            job = BibliometricJob.objects.get(id=job_id)
            job.mark_failed(str(e))
        except Exception:
            pass


def _execute_job_openalex(job_id: str) -> None:
    """Global kuyruk worker'ı tarafından çağrılır — OpenAlex tipi analiz, senkron."""
    close_old_connections()
    from bibliometrics.models import BibliometricJob
    from bibliometrics.services.parser import parse_openalex_json
    from bibliometrics.services.analyzer import run_all_analyses
    from bibliometrics.services.pdf_builder import build_demo_pdf, build_full_pdf
    from forum.s3_utils import upload_bytes_to_s3

    try:
        job = BibliometricJob.objects.select_related('alex_job').get(id=job_id)
        job.mark_running()

        alex_job = job.alex_job
        if not alex_job or not alex_job.all_results:
            job.mark_failed('OpenAlex verisi bulunamadı veya boş.')
            return

        records = parse_openalex_json(alex_job.all_results)
        if not records:
            job.mark_failed('OpenAlex verisinden kayıt okunamadı.')
            return

        if len(records) < 100:
            job.mark_failed(f'Bibliometrik analiz için en az 100 kayıt gereklidir (bulunan: {len(records)}).')
            return

        figures = run_all_analyses(records)
        if not figures:
            job.mark_failed('Analizler üretilemedi. Veri yetersiz olabilir.')
            return

        demo_pdf_bytes = build_demo_pdf(figures[:3], total_records=len(records), filename=job.original_filename)
        full_pdf_bytes = build_full_pdf(figures, total_records=len(records), filename=job.original_filename)

        n_figures = len(figures)
        try:
            import matplotlib.pyplot as plt
            plt.close('all')
        except Exception:
            pass
        del figures
        gc.collect()

        demo_url = upload_bytes_to_s3(demo_pdf_bytes, f'bibliometrics/demo/{job.id}.pdf', 'application/pdf')
        full_url = upload_bytes_to_s3(full_pdf_bytes, f'bibliometrics/full/{job.id}.pdf', 'application/pdf')

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

            subject = f'Bibliometrik Analiz - Demo Rapor'
            body_lines = [
                f'Merhaba {user.first_name or user.username},\n',
                f'Yüklediğiniz "{job.original_filename}" dosyası başarıyla analiz edildi.\n',
                f'Toplam Kayıt: {job.total_records}',
                f'Dosya Formatı: {job.get_file_format_display()}\n',
                f'Demo raporunuz (3 temel analiz) ekte PDF olarak sunulmuştur.\n',
                f'─────────────────────────────────────',
                f'TAM RAPOR (15 Analiz)',
                f'─────────────────────────────────────',
                f'  • Yayın Trendi + Büyüme Oranı',
                f'  • En Verimli Yazarlar + Lotka Kanunu',
                f'  • Anahtar Kelime Bulutu + Eş-Oluşum Ağı',
                f'  • Anahtar Kelime Zaman Trendi',
                f'  • En Çok Atıf Alan Yayınlar',
                f'  • En Çok Yayın Yapılan Dergiler',
                f'  • Kurum / Ülke Dağılımı + İşbirliği Ağı',
                f'  • Yazar İşbirliği Ağı',
                f'  • Yayın Türleri + Atıf Analizi + H-index',
                f'  • Yıllık Atıf Trendi\n',
                f'Sipariş oluşturmak için:',
                f'  {site_url}/bibliometrics/siparis/{job.id}/\n',
                f'---',
                f'Bu bir otomatik bildirimdir.',
                f'Analizus - Akademik Veri Üssü',
            ]

            email = EmailMessage(
                subject=subject,
                body='\n'.join(body_lines),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email.attach(
                f'bibliometrik_demo_{job.original_filename}.pdf',
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

            from bibliometrics.models import BibliometricOrder
            price = BibliometricOrder.calculate_price(job.total_records)
            order_url = f'{site_url}/bibliometrics/siparis/{job.id}/'

            subject = 'Bibliometrik Analiz - Demo Raporunuz Hazir'
            body_lines = [
                f'Merhaba {user.first_name or user.username},',
                '',
                f'"{job.original_filename}" dosyaniz basariyla analiz edildi.',
                '',
                f'Toplam Kayit : {job.total_records}',
                f'Format       : {job.get_file_format_display()}',
                '',
                'Demo raporunuzu (3 analiz iceren PDF) asagidaki linkten indirebilirsiniz:',
                job.demo_pdf_url,
                '',
                'Not: Indirme linki 3 gun gecerlidir.',
                '',
                '===========================================',
                f'TAM RAPOR (15 Analiz) - {price} TL',
                '===========================================',
                '  - Yayin Trendi + Buyume Orani',
                '  - En Verimli Yazarlar + Lotka Kanunu',
                '  - Anahtar Kelime Bulutu + Es-Olusum Agi',
                '  - Anahtar Kelime Zaman Trendi',
                '  - En Cok Atif Alan Yayinlar',
                '  - En Cok Yayin Yapilan Dergiler',
                '  - Kurum/Ulke Dagilimi + Isbirligi Agi',
                '  - Yazar Isbirligi Agi',
                '  - Yayin Turleri + Atif Analizi + H-index',
                '  - Yillik Atif Trendi',
                '',
                'Siparis olusturmak icin:',
                order_url,
                '',
                '---',
                'Analizus - Akademik Veri Ustu | analizus.com',
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
        subject = f'Bibliometrik Analiz - Tam Rapor Hazır!'
        body_lines = [
            f'Merhaba {user.first_name or user.username},\n',
            f'Bibliometrik analiz siparişiniz onaylandı ve tam raporunuz hazırlandı.\n',
            f'Sipariş No: #{str(order.id)[:8]}',
            f'Dosya: {job.original_filename}',
            f'Toplam Kayıt: {job.total_records}',
            f'Ödenen Tutar: {order.total_price} TL\n',
            f'Tam raporunuzu (15 analiz içeren PDF) aşağıdaki linkten indirebilirsiniz:',
            f'  {job.full_pdf_url}\n',
            f'Not: İndirme linki 3 gün geçerlidir.\n',
            f'---',
            f'Bu bir otomatik bildirimdir.',
            f'Analizus - Akademik Veri Üssü',
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
