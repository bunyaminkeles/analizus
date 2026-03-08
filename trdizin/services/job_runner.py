import logging
import threading
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMessage
from django.db import close_old_connections
from trdizin.models import DizinSearchJob
from forum.s3_utils import delete_from_s3, upload_to_s3

logger = logging.getLogger(__name__)

def _generate_dizin_results_txt(publication_list, job, is_demo=True):
    """TR Dizin yayın sonuçlarını txt formatında oluşturur."""
    lines = [
        f"TR Dizin Yayın Arama Sonuçları",
        f"{'='*60}",
        f"Sorgu: {job.get_query_summary()}",
        f"Toplam Bulunan Sonuç: {job.total_results}",
        f"Bu dosyadaki sonuç: {len(publication_list)} yayın",
        f"{'='*60}\n",
    ]

    for i, pub in enumerate(publication_list, 1):
        lines.append(f"--- Yayın #{i} ---")
        lines.append(f"Başlık    : {pub.get('title', '')}")
        lines.append(f"Yazarlar  : {pub.get('authors', '')}")
        lines.append(f"Dergi     : {pub.get('journal', '')}")
        lines.append(f"Yıl       : {pub.get('year', '')}")
        lines.append(f"DOI       : {pub.get('doi', '')}")
        abstract = pub.get('abstract_tr') or pub.get('abstract_en') or ''
        if abstract:
            lines.append(f"Özet      : {abstract}")
        lines.append("")

    lines.append(f"{'='*60}")
    lines.append(f"Toplam {job.total_results} yayın bulundu.")
    if is_demo:
        lines.append(f"Daha fazla sonuç için epostanızdaki adımları takip ediniz.")
    lines.append(f"\n---\nAnalizus - www.analizus.com")

    return "\n".join(lines)


def _execute_job(job_id):
    """Global kuyruk worker'ı tarafından çağrılır — senkron çalışır."""
    from trdizin.models import DizinSearchJob
    from trdizin.services.scraper import TRDizinScraper

    close_old_connections()
    try:
        job = DizinSearchJob.objects.get(id=job_id)
        job.mark_running()

        scraper = TRDizinScraper()
        total_count, demo_results, all_results, lucene_query = scraper.search(
            query_parts=job.query_parts,
            demo_limit=5,
        )

        job.mark_completed(
            demo_results=demo_results,
            all_results=all_results,
            total_count=total_count,
            lucene_query=lucene_query,
        )

        try:
            demo_txt = _generate_dizin_results_txt(demo_results, job, is_demo=True)
            demo_s3_url = upload_to_s3(demo_txt, f"trdizin/demo/{job.id}.txt")

            all_txt = _generate_dizin_results_txt(all_results, job, is_demo=False)
            all_s3_url = upload_to_s3(all_txt, f"trdizin/full/{job.id}.txt")

            update_fields = []
            if demo_s3_url:
                job.demo_file_url = demo_s3_url
                update_fields.append('demo_file_url')
            if all_s3_url:
                job.all_results_file_url = all_s3_url
                update_fields.append('all_results_file_url')
            if update_fields:
                job.save(update_fields=update_fields)
        except Exception as e:
            logger.error(f"TR Dizin S3 yükleme hatası: {e}")

        logger.info(f"TR Dizin Scraping job {job_id} tamamlandı: {total_count} sonuç")

    except Exception as e:
        logger.error(f"TR Dizin Scraping job {job_id} başarısız: {e}")
        try:
            job = DizinSearchJob.objects.get(id=job_id)
            job.mark_failed(str(e))
        except Exception:
            pass


def run_scraping_job(job_id):
    from analizdestek.job_queue import enqueue
    enqueue('trdizin', str(job_id))


def send_demo_email_async(job_id):
    """Background thread'de demo email gönder."""
    def _run():
        from trdizin.models import DizinSearchJob
        logger.info(f"[trdizin_async_email] Starting background email task for job {job_id}")
        try:
            job = DizinSearchJob.objects.get(id=job_id)
            send_demo_email(job)
        except DizinSearchJob.DoesNotExist:
            logger.error(f"[trdizin_async_email] Job not found: {job_id}")
        except Exception as e:
            logger.error(f"[trdizin_async_email] Unhandled exception for job {job_id}: {e}", exc_info=True)

    thread = threading.Thread(target=_run)
    thread.daemon = True
    thread.start()
    logger.info(f"[trdizin_async_email] Email task for job {job_id} started in background.")


def send_demo_email(job):
    """Arama sonuçlarını (tüm sonuçlar S3 linki ile) kullanıcının emailine gönder."""
    user = job.user
    to_email = user.email

    if not to_email:
        logger.warning(f"Kullanıcının emaili yok: {user.username}")
        return False

    subject = f"TR Dizin Arama Sonuçları: {job.get_query_summary()}"
    site_url = getattr(settings, 'SITE_URL', 'https://www.analizus.com')

    body_lines = [
        f"Merhaba {user.first_name or user.username},\n",
        f"TR Dizin arama sonuçlarınız hazırlanmıştır.\n",
        f"Sorgu: {job.get_query_summary()}",
        f"Toplam Sonuç: {job.total_results}\n",
    ]

    if job.all_results_file_url:
        body_lines.append(f"Tüm sonuçlarınızı aşağıdaki linkten indirebilirsiniz (geçici link):")
        body_lines.append(f"  {job.all_results_file_url}\n")

    body_lines.append(f"\n---\nAnalizus - {site_url}")

    try:
        email = EmailMessage(
            subject=subject,
            body="\n".join(body_lines),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        if not job.all_results_file_url:
            demo_txt = _generate_dizin_results_txt(job.demo_results, job, is_demo=False)
            email.attach(
                f"trdizin_{len(job.demo_results)}_sonuc.txt",
                demo_txt,
                'text/plain',
            )
        email.send()

        job.demo_email_sent = True
        job.save(update_fields=['demo_email_sent'])

        logger.info(f"TR Dizin email gönderildi: {to_email}")
        return True
    except Exception as e:
        logger.error(f"TR Dizin email gönderilemedi: {e}")
        return False


def send_order_results_email(order):
    """Onaylanan siparişin sonuçlarını S3 linki ile kullanıcıya gönder."""
    user = order.user
    job = order.search_job
    to_email = user.email

    if not to_email:
        return False

    subject = f"TR Dizin Arama Sonuçları: {job.get_query_summary()}"

    lines = [
        f"Merhaba {user.first_name or user.username},\n",
        f"Siparişiniz onaylanmış ve TR Dizin yayın sonuçlarınız hazırlanmıştır.\n",
        f"Sipariş No: #{str(order.id)[:8]}",
        f"Sorgu: {job.get_query_summary()}",
        f"Toplam Sonuç: {job.total_results}",
        f"Gönderilen Yayın Sayısı: {order.abstract_count}",
        f"Ödenen Tutar: {order.total_price} TL\n",
    ]

    download_url = job.all_results_file_url
    if download_url:
        lines.append(f"Sonuçlarınızı aşağıdaki linkten indirebilirsiniz:")
        lines.append(f"  {download_url}\n")

    lines.append(f"\n---\nAnalizus - www.analizus.com")

    body = "\n".join(lines)

    try:
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        email.send()

        order.results_email_sent = True
        order.results_email_sent_at = timezone.now()
        order.status = 'completed'
        order.save(update_fields=['results_email_sent', 'results_email_sent_at', 'status'])

        logger.info(f"TR Dizin sipariş sonuçları gönderildi: {to_email} ({order.abstract_count} yayın)")
        return True
    except Exception as e:
        logger.error(f"TR Dizin sipariş email gönderilemedi: {e}")
        return False


def cleanup_expired_trdizin_s3_files(days=3):
    """3 günden eski trdizin/ altındaki tüm dosyaları S3'den siler.
    DB'ye değil, S3'deki dosya tarihine bakar."""
    import boto3
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

        for prefix in ['trdizin/demo/', 'trdizin/full/', 'trdizin/orders/']:
            paginator = s3.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
                for obj in page.get('Contents', []):
                    last_modified = obj['LastModified']
                    if last_modified < cutoff:
                        s3.delete_object(Bucket=bucket, Key=obj['Key'])
                        logger.info(f"S3 temizlik: silindi {obj['Key']}")
                        deleted_count += 1
    except Exception as e:
        logger.error(f"S3 temizlik hatası (trdizin): {e}")

    # DB'deki URL referanslarını da temizle
    try:
        DizinSearchJob.objects.filter(
            created_at__lt=cutoff,
        ).exclude(
            demo_file_url='', all_results_file_url=''
        ).update(demo_file_url='', all_results_file_url='')
    except Exception as e:
        logger.error(f"DB temizlik hatası (trdizin): {e}")

    logger.info(f"S3 temizlik (trdizin): {deleted_count} dosya silindi")
    return deleted_count