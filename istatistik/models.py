import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


TOOL_CHOICES = [
    ('cronbach', 'Güvenilirlik Analizi (Cronbach Alpha)'),
    ('normallik', 'Normallik Testi'),
    ('betimsel', 'Betimleyici İstatistik'),
    ('korelasyon', 'Korelasyon Matrisi'),
    ('ttesti', 't-Testi'),
    ('anova', 'Tek Yönlü ANOVA'),
]

STATUS_CHOICES = [
    ('pending', 'Bekliyor'),
    ('running', 'Çalışıyor'),
    ('completed', 'Tamamlandı'),
    ('failed', 'Hata'),
]


class IstatistikJob(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='istatistik_jobs',
    )
    tool = models.CharField(max_length=20, choices=TOOL_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    original_filename = models.CharField(max_length=255, blank=True)
    result_data = models.JSONField(null=True, blank=True)
    pdf_url = models.URLField(max_length=500, blank=True)
    error_message = models.TextField(blank=True)

    options = models.JSONField(default=dict, blank=True)  # araç seçenekleri, ör: {'method': 'pearson'}

    is_demo = models.BooleanField(default=True)  # login olmadan = True

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'İstatistik İş'
        verbose_name_plural = 'İstatistik İşler'

    def __str__(self):
        user_str = self.user.username if self.user else 'Anonim'
        return f'{self.get_tool_display()} — {user_str} ({self.status})'

    def mark_running(self):
        self.status = 'running'
        self.save(update_fields=['status'])

    def mark_completed(self, result_data=None, pdf_url=''):
        self.status = 'completed'
        self.result_data = result_data
        self.pdf_url = pdf_url
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'result_data', 'pdf_url', 'completed_at'])

    def mark_failed(self, error_message=''):
        self.status = 'failed'
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message'])

    @staticmethod
    def get_daily_limit(user):
        if user is None or not user.is_authenticated:
            return 3  # anonim: 3 analiz/gün
        if user.is_staff or user.is_superuser:
            return 9999
        if hasattr(user, 'profile') and user.profile.is_premium:
            return 20
        return 5

    @staticmethod
    def daily_count_for_user(user):
        if user is None or not user.is_authenticated:
            return 0  # IP bazlı limit view'da ratelimit ile yönetilir
        today = timezone.now().date()
        return IstatistikJob.objects.filter(
            user=user,
            created_at__date=today,
        ).count()
