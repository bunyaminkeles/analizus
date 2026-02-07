import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class TezSearchJob(models.Model):
    """Demo arama görevi (ücretsiz, günlük limitli)"""
    STATUS_CHOICES = (
        ('pending', 'Bekliyor'),
        ('running', 'Çalışıyor'),
        ('completed', 'Tamamlandı'),
        ('failed', 'Başarısız'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tez_searches')
    konu = models.CharField(max_length=200, verbose_name="Bilim Alanı")
    keywords = models.JSONField(default=list, verbose_name="Anahtar Kelimeler")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_results = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)

    demo_results = models.JSONField(default=list, blank=True)
    all_results = models.JSONField(default=list, blank=True)

    demo_file_url = models.URLField(max_length=500, blank=True, default='', verbose_name="Demo Dosya URL (S3)")
    all_results_file_url = models.URLField(max_length=500, blank=True, default='', verbose_name="Tüm Sonuçlar Dosya URL (S3)")

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    demo_email_sent = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Tez Arama (Demo)"
        verbose_name_plural = "Tez Aramaları (Demo)"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.konu} ({self.get_status_display()})"

    def mark_running(self):
        self.status = 'running'
        self.save(update_fields=['status'])

    def mark_completed(self, demo_results, all_results, total_count):
        self.status = 'completed'
        self.demo_results = demo_results
        self.all_results = all_results
        self.total_results = total_count
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'demo_results', 'all_results', 'total_results', 'completed_at'])

    def mark_failed(self, error_msg):
        self.status = 'failed'
        self.error_message = error_msg
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'completed_at'])

    @staticmethod
    def daily_count_for_user(user):
        """Kullanıcının bugünkü demo arama sayısı"""
        today = timezone.now().date()
        return TezSearchJob.objects.filter(
            user=user,
            created_at__date=today,
        ).count()

    @staticmethod
    def get_daily_limit(user):
        """Normal: 3, Premium: 7"""
        if hasattr(user, 'profile') and user.profile.is_premium:
            return 7
        return 3


class TezOrder(models.Model):
    """Ücretli tez sipariş (IBAN ödeme + admin onayı)"""
    STATUS_CHOICES = (
        ('pending_payment', 'Ödeme Bekleniyor'),
        ('payment_review', 'Ödeme İnceleniyor'),
        ('approved', 'Onaylandı'),
        ('processing', 'İşleniyor'),
        ('completed', 'Tamamlandı - Gönderildi'),
        ('cancelled', 'İptal'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tez_orders')
    search_job = models.ForeignKey(TezSearchJob, on_delete=models.CASCADE, related_name='orders')

    abstract_count = models.PositiveIntegerField(verbose_name="İstenen Abstract Sayısı")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Toplam Tutar (TL)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment')

    # Ödeme bilgileri
    payment_note = models.TextField(blank=True, verbose_name="Ödeme Açıklaması")
    admin_note = models.TextField(blank=True, verbose_name="Admin Notu")

    # Email gönderim takibi
    results_email_sent = models.BooleanField(default=False)
    results_email_sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Tez Siparişi"
        verbose_name_plural = "Tez Siparişleri"
        ordering = ['-created_at']

    def __str__(self):
        return f"#{str(self.id)[:8]} - {self.user.username} - {self.abstract_count} abstract - {self.get_status_display()}"

    @staticmethod
    def calculate_price(abstract_count):
        """İlk 100 abstract = 250 TL, sonraki her 100 = 100 TL"""
        if abstract_count <= 0:
            return 0
        if abstract_count <= 100:
            return 250
        extra = abstract_count - 100
        extra_blocks = (extra + 99) // 100  # yukarı yuvarla
        return 250 + (extra_blocks * 100)

    @property
    def is_overdue(self):
        """Onaylandıktan sonra 24 saat geçti mi ve henüz gönderilmedi mi?"""
        if self.status == 'approved' and self.approved_at:
            return timezone.now() > self.approved_at + timezone.timedelta(hours=24)
        return False
