import logging
from django.utils import timezone
from trdizin.models import DizinSearchJob
from yoktez.services.job_runner import delete_from_s3 # Re-use the S3 deletion function

logger = logging.getLogger(__name__)

def cleanup_expired_trdizin_s3_files(days=3):
    """3 günden eski, sipariş oluşturulmamış demo/full dosyalarını S3'den siler.
    Cron job olarak günlük çalıştırılabilir."""
    
    cutoff = timezone.now() - timezone.timedelta(days=days)

    # 3 günden eski, sipariş verilmemiş aramalar
    expired_jobs = DizinSearchJob.objects.filter(
        created_at__lt=cutoff,
        status='completed',
    ).exclude(
        orders__status__in=['pending_payment', 'payment_review', 'approved', 'processing', 'completed']
    )

    deleted_count = 0
    for job in expired_jobs:
        # Demo dosyasını sil
        if job.demo_file_url:
            s3_key = f"trdizin/demo/{job.id}.txt"
            if delete_from_s3(s3_key):
                job.demo_file_url = ''
                deleted_count += 1

        # Tüm sonuçlar dosyasını sil
        if job.all_results_file_url:
            s3_key = f"trdizin/full/{job.id}.txt"
            if delete_from_s3(s3_key):
                job.all_results_file_url = ''
                deleted_count += 1

        # Save changes to the job if any files were deleted
        if deleted_count > 0:
            job.save()

    logger.info(f"TR Dizin S3 temizlik: {deleted_count} dosya silindi ({expired_jobs.count()} expired job)")
    return deleted_count