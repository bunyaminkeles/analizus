import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class YokTezSearchJob(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Bekliyor'),
        ('running', 'Çalışıyor'),
        ('completed', 'Tamamlandı'),
        ('failed', 'Başarısız'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='yoktez_searches')

    # Arama parametreleri
    tez_ad = models.CharField(max_length=300, blank=True, verbose_name='Tez Adı')
    yazar = models.CharField(max_length=200, blank=True, verbose_name='Yazar')
    danisman = models.CharField(max_length=200, blank=True, verbose_name='Danışman')
    universite = models.CharField(max_length=200, blank=True, verbose_name='Üniversite')
    tur = models.CharField(max_length=10, blank=True, verbose_name='Tez Türü')  # '0'=hepsi, '1'=YL, '2'=Doktora
    yil_baslangic = models.IntegerField(null=True, blank=True, verbose_name='Başlangıç Yılı')
    yil_bitis = models.IntegerField(null=True, blank=True, verbose_name='Bitiş Yılı')
    metin = models.CharField(max_length=300, blank=True, verbose_name='Özet/Metin')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_results = models.IntegerField(default=0)
    demo_results = models.JSONField(default=list, blank=True)
    all_results = models.JSONField(default=list, blank=True)
    all_results_file_url = models.URLField(max_length=500, blank=True, default='')
    demo_email_sent = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'YÖK Tez Araması'
        verbose_name_plural = 'YÖK Tez Aramaları'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.tez_ad or self.yazar or 'Genel'} ({self.get_status_display()})"

    def get_query_summary(self):
        parts = []
        if self.tez_ad:
            parts.append(f'Başlık: "{self.tez_ad}"')
        if self.yazar:
            parts.append(f'Yazar: "{self.yazar}"')
        if self.metin:
            parts.append(f'Özet: "{self.metin}"')
        if self.yil_baslangic or self.yil_bitis:
            parts.append(f'({self.yil_baslangic or "?"}-{self.yil_bitis or "?"})')
        return ' | '.join(parts) if parts else 'Genel Tarama'

    @staticmethod
    def daily_count_for_user(user):
        today = timezone.now().date()
        return YokTezSearchJob.objects.filter(user=user, created_at__date=today).count()

    @staticmethod
    def get_daily_limit(user):
        if user.is_staff or user.is_superuser:
            return 9999
        return 3
