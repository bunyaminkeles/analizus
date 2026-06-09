import threading
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

from django.core.mail import EmailMessage
from django.conf import settings
from django.db import close_old_connections

logger = logging.getLogger(__name__)


def _execute_job(job_id: str) -> None:
    """Global kuyruk worker'ı tarafından çağrılır — senkron çalışır."""
    from yoktez.models import YokTezSearchJob
    from yoktez.services.scraper import search, generate_results_txt
    from forum.s3_utils import upload_to_s3

    close_old_connections()
    try:
        job = YokTezSearchJob.objects.get(id=job_id)
        job.status = 'running'
        job.save(update_fields=['status'])

        with ThreadPoolExecutor(max_workers=1) as ex:
            future = ex.submit(
                search,
                tez_ad=job.tez_ad,
                yazar=job.yazar,
                danisman=job.danisman,
                tur=job.tur or '0',
                yil_baslangic=job.yil_baslangic,
                yil_bitis=job.yil_bitis,
                metin=job.metin,
                demo_limit=5,
            )
            try:
                total, demo_records = future.result(timeout=300)  # 5 dk max
            except FuturesTimeout:
                future.cancel()
                raise Exception('Zaman aşımı: YÖK Tez 5 dakikadan uzun yanıt vermedi.')

        # İptal edildiyse kaydetme
        close_old_connections()
        job.refresh_from_db(fields=['status'])
        if job.status == 'failed':
            logger.info(f'YÖK Tez job {job_id} iptal edilmişti, sonuç kaydedilmedi.')
            return

        job.status = 'completed'
        job.total_results = total
        job.demo_results = demo_records
        from django.utils import timezone
        job.completed_at = timezone.now()
        job.save(update_fields=['status', 'total_results', 'demo_results', 'completed_at'])

        if demo_records:
            try:
                txt = generate_results_txt(demo_records, job)
                s3_url = upload_to_s3(txt, f'yoktez/demo/{job.id}.txt')
                if s3_url:
                    job.all_results_file_url = s3_url
                    job.save(update_fields=['all_results_file_url'])
            except Exception as e:
                logger.warning(f'YÖK Tez S3 yükleme hatası: {e}')

        logger.info(f'YÖK Tez job {job_id} tamamlandı: {total} sonuç')

    except YokTezSearchJob.DoesNotExist:
        logger.error(f'YÖK Tez job bulunamadı: {job_id}')
    except Exception as e:
        logger.error(f'YÖK Tez job hatası [{job_id}]: {e}', exc_info=True)
        try:
            j = YokTezSearchJob.objects.get(id=job_id)
            j.status = 'failed'
            j.error_message = str(e)
            j.save(update_fields=['status', 'error_message'])
        except Exception:
            pass


def run_yoktez_job(job_id: str) -> None:
    from analizdestek.job_queue import enqueue
    enqueue('yoktez', job_id)


def send_demo_email_async(job_id: str) -> None:
    def _run():
        from yoktez.models import YokTezSearchJob
        close_old_connections()
        try:
            job = YokTezSearchJob.objects.get(id=job_id)

            body_lines = [
                f'YÖK Tez aramanızın örnek sonuçları hazır.',
                f'',
                f'Sorgu: {job.get_query_summary()}',
                f'Toplam bulunan: {job.total_results} tez',
                f'Aşağıda en yeni 5 tezin bilgileri yer almaktadır.',
                f'',
            ]
            for i, r in enumerate(job.demo_results, 1):
                body_lines.append(f'{i}. {r.get("title", "(Başlık yok)")}')
                body_lines.append(f'   Yazar: {r.get("author", "-")} | Yıl: {r.get("year", "-")}')
                body_lines.append(f'   Üniversite: {r.get("university", "-")}')
                abstract = r.get('abstract_tr') or r.get('abstract_en', '')
                if abstract:
                    trimmed = abstract[:500].rstrip()
                    if len(abstract) > 500:
                        trimmed += '…'
                    body_lines.append(f'   Özet: {trimmed}')
                body_lines.append('')

            body_lines.append('─' * 40)
            body_lines.append('Tüm veriye ihtiyacınız varsa:')
            body_lines.append('  https://www.analizus.com/proje-talebi/?source=yoktez')
            body_lines.append('  adresinden talep oluşturabilirsiniz.')

            email = EmailMessage(
                subject=f'YÖK Tez Arama Sonuçları — {job.get_query_summary()[:50]}',
                body='\n'.join(body_lines),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[job.user.email],
            )
            email.send()

            job.demo_email_sent = True
            job.save(update_fields=['demo_email_sent'])
            logger.info(f'YÖK Tez demo email gönderildi: job={job_id}')

        except Exception as e:
            logger.error(f'YÖK Tez email hatası [{job_id}]: {e}')

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
