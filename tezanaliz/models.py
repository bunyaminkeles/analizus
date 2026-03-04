import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class TezAnaliz(models.Model):
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
        related_name='tez_analizler',
    )
    yok_job = models.ForeignKey(
        'yoktez.YokTezSearchJob',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analizler',
    )

    # Arama parametreleri (yok_job silinse bile kalsın)
    tez_ad = models.CharField(max_length=300, blank=True)
    yazar = models.CharField(max_length=200, blank=True)
    universite = models.CharField(max_length=200, blank=True)
    tur = models.CharField(max_length=10, blank=True)
    yil_baslangic = models.IntegerField(null=True, blank=True)
    yil_bitis = models.IntegerField(null=True, blank=True)
    metin = models.CharField(max_length=300, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_records = models.IntegerField(default=0)
    records = models.JSONField(default=list, blank=True)
    analysis_data = models.JSONField(default=dict, blank=True)  # benzer tezler vb.

    pdf_url = models.URLField(max_length=500, blank=True, default='')
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Tez Analizi'
        verbose_name_plural = 'Tez Analizleri'
        ordering = ['-created_at']

    def __str__(self):
        q = self.tez_ad or self.metin or 'Genel'
        return f'{self.user.username} — {q[:50]} ({self.get_status_display()})'

    def get_query_summary(self):
        parts = []
        if self.tez_ad:
            parts.append(f'Başlık: "{self.tez_ad}"')
        if self.yazar:
            parts.append(f'Yazar: "{self.yazar}"')
        if self.metin:
            parts.append(f'Özet: "{self.metin}"')
        if self.universite:
            parts.append(f'Üniversite: "{self.universite}"')
        if self.yil_baslangic or self.yil_bitis:
            parts.append(f'({self.yil_baslangic or "?"}-{self.yil_bitis or "?"})')
        return ' | '.join(parts) if parts else 'Genel Tarama'

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
        return TezAnaliz.objects.filter(user=user, created_at__date=today).count()

    @staticmethod
    def get_daily_limit(user):
        if user.is_staff or user.is_superuser:
            return 9999
        if hasattr(user, 'profile') and user.profile.is_premium:
            return 5
        return 1
