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
    from yoktez.services.yok_universities import get_universite_id
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
                universite_id=get_universite_id(job.universite),
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
        _notify_job_completed(job_id)

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
        else:
            _notify_job_failed(job_id, str(e))


def run_yoktez_job(job_id: str) -> None:
    from analizdestek.job_queue import enqueue
    enqueue('yoktez', job_id)


def _notify_job_completed(job_id: str) -> None:
    """İş tamamlanınca otomatik e-posta + in-app bildirim gönderir (8 Ekim 2026)."""
    from yoktez.models import YokTezSearchJob
    close_old_connections()
    try:
        job = YokTezSearchJob.objects.get(id=job_id)
    except YokTezSearchJob.DoesNotExist:
        return

    from forum.models import Notification
    from forum.utils import send_realtime_notification

    if job.total_results:
        message = f'YÖK Tez aramanız tamamlandı: "{job.get_query_summary()}" — {job.total_results} sonuç bulundu.'
    else:
        message = f'YÖK Tez aramanız tamamlandı: "{job.get_query_summary()}" — sonuç bulunamadı.'

    try:
        # target: job.user (job.id UUID — Notification.object_id PositiveIntegerField'a sığmıyor,
        # zaten hiçbir şablon notification.target'ı render etmiyor, url ayrı geçiliyor)
        Notification.objects.create(
            recipient=job.user,
            sender=None,
            verb=message,
            target=job.user,
        )
        send_realtime_notification(job.user.id, message, '/yoktez/')
    except Exception as e:
        logger.error(f'YÖK Tez tamamlanma bildirimi oluşturulamadı [{job_id}]: {e}')

    if job.demo_results:
        send_demo_email_async(job_id)


def _notify_job_failed(job_id: str, error_message: str) -> None:
    """İş başarısız olunca e-posta + in-app bildirim gönderir (8 Ekim 2026)."""
    from yoktez.models import YokTezSearchJob
    close_old_connections()
    try:
        job = YokTezSearchJob.objects.get(id=job_id)
    except YokTezSearchJob.DoesNotExist:
        return

    from forum.models import Notification
    from forum.utils import send_realtime_notification

    message = f'YÖK Tez aramanız başarısız oldu: "{job.get_query_summary()}". Lütfen tekrar deneyin.'

    try:
        Notification.objects.create(
            recipient=job.user,
            sender=None,
            verb=message,
            target=job.user,
        )
        send_realtime_notification(job.user.id, message, '/yoktez/')
    except Exception as e:
        logger.error(f'YÖK Tez başarısızlık bildirimi oluşturulamadı [{job_id}]: {e}')

    def _send_failure_email():
        try:
            EmailMessage(
                subject=f'YÖK Tez Araması Başarısız — {job.get_query_summary()[:50]}',
                body=(
                    'Merhaba,\n\n'
                    'YÖK Tez aramanız tamamlanamadı.\n\n'
                    f'Sorgu: {job.get_query_summary()}\n'
                    f'Hata: {error_message}\n\n'
                    'Lütfen https://www.analizus.com/yoktez/ adresinden tekrar deneyebilirsiniz.\n'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[job.user.email],
            ).send()
        except Exception as e:
            logger.error(f'YÖK Tez başarısızlık e-postası gönderilemedi [{job_id}]: {e}')

    threading.Thread(target=_send_failure_email, daemon=True).start()


def send_demo_email_async(job_id: str) -> None:
    def _run():
        from yoktez.models import YokTezSearchJob
        close_old_connections()
        try:
            job = YokTezSearchJob.objects.get(id=job_id)

            # Tam, doğru biçimlendirilmiş sonuçlar zaten /yoktez/ sayfasında (TR başlık + danışman dahil)
            # gösteriliyor — e-posta içeriği tekrarlamaz, yalnız oraya yönlendirir (8 Ekim 2026,
            # önceki sürümdeki yinelenen döngü yalnız İngilizce başlık gösteriyordu, danışman hiç yoktu).
            body_lines = [
                f'YÖK Tez aramanızın örnek sonuçları hazır.',
                f'',
                f'Sorgu: {job.get_query_summary()}',
                f'Toplam bulunan: {job.total_results} tez',
                f'',
                f'En yeni 5 tezin başlık, yazar, danışman, üniversite ve özet bilgilerini görmek,',
                f'TXT/Excel olarak indirmek için:',
                f'  https://www.analizus.com/yoktez/',
                f'',
                f'Bu sonuçlara bu sayfadan 3 gün boyunca erişebilirsiniz; bu sürenin sonunda otomatik',
                f'olarak silinir.',
                f'',
                f'─' * 40,
                f'Tüm veriye ihtiyacınız varsa:',
                f'  https://www.analizus.com/proje-talebi/?source=yoktez',
                f'  adresinden talep oluşturabilirsiniz.',
            ]

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


def cleanup_expired_yoktez_s3_files(days=3):
    """3 günden eski yoktez/demo/ altındaki tüm dosyaları S3'den siler.
    DB'ye değil, S3'deki dosya tarihine bakar (trdizin/openalex/oaipmh/pubmed ile aynı kalıp)."""
    import boto3
    from django.utils import timezone
    from datetime import timedelta
    from yoktez.models import YokTezSearchJob

    deleted_count = 0
    cutoff = timezone.now() - timedelta(days=days)

    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        bucket = settings.AWS_STORAGE_BUCKET_NAME

        paginator = s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket, Prefix='yoktez/demo/'):
            for obj in page.get('Contents', []):
                last_modified = obj['LastModified']
                if last_modified < cutoff:
                    s3.delete_object(Bucket=bucket, Key=obj['Key'])
                    logger.info(f"S3 temizlik: silindi {obj['Key']}")
                    deleted_count += 1
    except Exception as e:
        logger.error(f"S3 temizlik hatası (yoktez): {e}")

    # DB'deki URL referansını da temizle
    try:
        YokTezSearchJob.objects.filter(
            created_at__lt=cutoff,
        ).exclude(all_results_file_url='').update(all_results_file_url='')
    except Exception as e:
        logger.error(f"DB temizlik hatası (yoktez): {e}")

    logger.info(f"S3 temizlik (yoktez): {deleted_count} dosya silindi")
    return deleted_count
