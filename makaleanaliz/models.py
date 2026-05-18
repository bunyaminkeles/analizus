import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class MakaleAnaliz(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Bekliyor'),
        ('running', 'Çalışıyor'),
        ('completed', 'Tamamlandı'),
        ('failed', 'Başarısız'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='makale_analizler',
    )
    dizin_job = models.ForeignKey(
        'trdizin.DizinSearchJob',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analizler',
    )
    oai_job = models.ForeignKey(
        'oaipmh.OAIPMHSearchJob',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analizler',
    )

    # Sorgu özeti (dizin_job silinse bile kalsın)
    query_summary = models.CharField(max_length=500, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_records = models.IntegerField(default=0)
    analysis_data = models.JSONField(default=dict, blank=True)  # benzer makaleler vb.

    pdf_url = models.URLField(max_length=500, blank=True, default='')
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Makale Analizi'
        verbose_name_plural = 'Makale Analizleri'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} — {self.query_summary[:50]} ({self.get_status_display()})'

    def get_query_summary(self):
        if self.query_summary:
            return self.query_summary
        if self.dizin_job:
            return self.dizin_job.get_query_summary()
        return 'Genel Tarama'

    def mark_running(self):
        self.status = 'running'
        self.save(update_fields=['status'])

    def mark_completed(self, total_records, pdf_url=''):
        self.status = 'completed'
        self.total_records = total_records
        self.pdf_url = pdf_url
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'total_records', 'pdf_url', 'completed_at'])

    def mark_failed(self, error):
        self.status = 'failed'
        self.error_message = str(error)
        self.save(update_fields=['status', 'error_message'])

    @staticmethod
    def daily_count_for_user(user):
        today = timezone.now().date()
        return MakaleAnaliz.objects.filter(user=user, created_at__date=today).count()

    @staticmethod
    def get_daily_limit(user):
        if user.is_staff or user.is_superuser:
            return 9999
        if hasattr(user, 'profile') and user.profile.is_premium:
            return 5
        return 1
