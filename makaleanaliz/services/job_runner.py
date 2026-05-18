"""
TR Dizin Makale Analizi iş yürütücüsü.
DizinSearchJob.all_results verisini kullanır (yeniden fetch gerekmez).
Global kuyruk (analizdestek.job_queue) üzerinden seri çalışır — aynı anda 1 iş.
"""
import gc
import threading
import logging

from django.core.mail import EmailMessage
from django.db import close_old_connections
from django.conf import settings

logger = logging.getLogger(__name__)


def _execute_job(job_id: str) -> None:
    """
    Makale analizi işini senkron olarak çalıştırır.
    Global worker thread tarafından çağrılır.
    """
    close_old_connections()
    from makaleanaliz.models import MakaleAnaliz
    from makaleanaliz.services.analyzer import run_all_analyses, compute_similar_articles
    from makaleanaliz.services.pdf_builder import build_pdf
    from forum.s3_utils import upload_bytes_to_s3

    try:
        job = MakaleAnaliz.objects.get(id=job_id)
    except MakaleAnaliz.DoesNotExist:
        logger.error(f'[makaleanaliz] Job bulunamadı: {job_id}')
        return

    # Duplicate-safe: sadece pending işleri çalıştır
    if job.status != 'pending':
        logger.info(f'[makaleanaliz] Job {job_id} zaten {job.status}, atlanıyor.')
        return

    try:
        job.mark_running()

        # 1. Veriyi kaynak job'dan al
        from forum.models import SiteSettings
        max_records = SiteSettings.load().analiz_max_records or 500

        if job.dizin_job:
            records = list(job.dizin_job.all_results or [])
            source_label = 'TR Dizin'
        elif job.oai_job:
            records = list(job.oai_job.all_results or [])
            source_label = 'Üniversite Tez Arşivi'
        else:
            job.mark_failed('Analiz kaynağı bulunamadı.')
            return

        if not records:
            job.mark_failed(
                f'{source_label} verisi bulunamadı. '
                'Yeni bir arama yaparak tekrar deneyin.'
            )
            return
        records = records[:max_records]

        if len(records) < 5:
            job.mark_failed(
                f'Analiz için en az 5 kayıt gereklidir (bulunan: {len(records)}). '
                'Arama kriterlerini genişletin.'
            )
            return

        # 2. Benzer makaleler hesapla
        query_text = job.get_query_summary()
        similar = compute_similar_articles(records, query_text, top_n=10)
        job.analysis_data = {'similar': similar}
        job.save(update_fields=['analysis_data'])

        # 3. Analizler
        figures = run_all_analyses(records)
        if not figures:
            job.mark_failed('Analizler üretilemedi. Veri yetersiz olabilir.')
            return

        # 4. PDF oluştur
        pdf_bytes = build_pdf(
            figures,
            total_records=len(records),
            query_summary=job.get_query_summary(),
        )

        # 5. Figürleri serbest bırak
        n_figures = len(figures)
        try:
            import matplotlib.pyplot as plt
            plt.close('all')
        except Exception:
            pass
        del figures
        gc.collect()

        # 6. S3'e yükle
        s3_key = f'makaleanaliz/pdf/{job.id}.pdf'
        pdf_url = upload_bytes_to_s3(pdf_bytes, s3_key, 'application/pdf')

        # 7. Job'ı tamamla
        close_old_connections()
        job.mark_completed(total_records=len(records), pdf_url=pdf_url or '')

        logger.info(
            f'[makaleanaliz] Job {job_id} tamamlandı. '
            f'{len(records)} kayıt, {n_figures} analiz.'
        )

        # 8. Email gönder
        send_completion_email_async(str(job.id), pdf_url)

    except Exception as e:
        logger.error(f'[makaleanaliz] Job hatası [{job_id}]: {e}', exc_info=True)
        try:
            close_old_connections()
            from makaleanaliz.models import MakaleAnaliz as _MakaleAnaliz
            _MakaleAnaliz.objects.get(id=job_id).mark_failed(str(e))
        except Exception:
            pass


def run_makaleanaliz_job(job_id: str) -> None:
    """Makale analizi işini global kuyruğa ekler."""
    from analizdestek.job_queue import enqueue
    enqueue('makaleanaliz', job_id)


def send_completion_email_async(job_id: str, pdf_url: str = '') -> None:
    """Analiz tamamlandığında PDF URL'si ile email gönder."""

    def _run():
        from makaleanaliz.models import MakaleAnaliz
        try:
            job = MakaleAnaliz.objects.get(id=job_id)
            user = job.user
            site_url = getattr(settings, 'SITE_URL', 'https://analizus.com')
            result_url = f'{site_url}/makaleanaliz/sonuc/{job.id}/'

            subject = f'TR Dizin Makale Analizi Tamamlandı — {job.get_query_summary()[:50]}'
            body_lines = [
                f'Merhaba {user.first_name or user.username},',
                '',
                f'"{job.get_query_summary()}" sorgunuz için makale analizi tamamlandı.',
                '',
                f'Toplam Analiz Edilen Makale: {job.total_records}',
                '',
                'Analiz sonuçlarınızı ve PDF raporunuzu görüntülemek için:',
                f'  {result_url}',
                '',
            ]
            if pdf_url:
                body_lines += [
                    'PDF raporunuzu doğrudan indirmek için:',
                    f'  {pdf_url}',
                    '',
                    'Not: İndirme linki 3 gün geçerlidir.',
                    '',
                ]
            body_lines += [
                '---',
                'Bu bir otomatik bildirimdir.',
                'Analizus — Akademik Veri Üssü  |  analizus.com',
            ]

            email = EmailMessage(
                subject=subject,
                body='\n'.join(body_lines),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email.send()
            logger.info(f'[makaleanaliz] Tamamlanma emaili gönderildi: {user.email}')

        except Exception as e:
            logger.error(f'[makaleanaliz] Email hatası [{job_id}]: {e}', exc_info=True)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
