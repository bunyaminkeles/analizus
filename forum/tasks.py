from celery import shared_task
from django.utils import timezone
from .models import FreelanceJob

@shared_task
def check_featured_jobs_expiration():
    """
    Süresi dolan (featured_until < şimdi) vitrin ilanlarını kontrol eder
    ve normal ilana çevirir.
    """
    now = timezone.now()
    expired_jobs = FreelanceJob.objects.filter(
        is_featured=True,
        featured_until__lte=now
    )
    
    count = expired_jobs.count()
    if count > 0:
        # Toplu güncelleme ile vitrinden düşür
        expired_jobs.update(is_featured=False)
        return f"{count} adet ilanın vitrin süresi doldu ve normal ilana çevrildi."
    
    return "Süresi dolan vitrin ilanı bulunamadı."