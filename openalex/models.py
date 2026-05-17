import uuid
from datetime import timedelta
from django.db import models
from django.conf import settings
from django.utils import timezone


class AlexSearchJob(models.Model):
    """OpenAlex yayın arama görevi (demo: ücretsiz, günlük limitli)"""
    STATUS_CHOICES = (
        ('pending', 'Bekliyor'),
        ('running', 'Çalışıyor'),
        ('completed', 'Tamamlandı'),
        ('failed', 'Başarısız'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='alex_searches')

    # Yapısal sorgu parçaları
    # [{"field": "title", "value": "machine learning", "operator": "AND"}, ...]
    query_parts = models.JSONField(default=list, verbose_name="Sorgu Parçaları")
    api_query = models.TextField(blank=True, verbose_name="Oluşturulan API Sorgusu")

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
        verbose_name = "OpenAlex Arama (Demo)"
        verbose_name_plural = "OpenAlex Aramaları (Demo)"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        query_short = self.api_query[:60] if self.api_query else str(self.query_parts)[:60]
        return f"{self.user.username} - {query_short} ({self.get_status_display()})"

    def mark_running(self):
        self.status = 'running'
        self.save(update_fields=['status'])

    def mark_completed(self, demo_results, all_results, total_count, api_query):
        self.status = 'completed'
        self.demo_results = demo_results
        self.all_results = all_results
        self.total_results = total_count
        self.api_query = api_query
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'demo_results', 'all_results', 'total_results', 'api_query', 'completed_at'])

    def mark_failed(self, error_msg):
        self.status = 'failed'
        self.error_message = error_msg
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'completed_at'])

    @staticmethod
    def daily_count_for_user(user):
        today = timezone.now().date()
        return AlexSearchJob.objects.filter(
            user=user,
            created_at__date=today,
        ).count()

    @staticmethod
    def get_daily_limit(user):
        """Admin: sınırsız, diğerleri: 3"""
        if user.is_staff or user.is_superuser:
            return 9999
        return 3

    def get_query_summary(self):
        parts = []
        for p in self.query_parts:
            field_labels = {
                'title': 'Başlık', 'abstract': 'Özet', 'author': 'Yazar',
                'keyword': 'Anahtar Kelime', 'journal': 'Dergi/Kaynak',
                'institution': 'Kurum', 'doi': 'DOI', 'year': 'Yıl',
                'type': 'Yayın Türü',
            }
            label = field_labels.get(p.get('field', ''), p.get('field', ''))
            parts.append(f"{label}: {p.get('value', '')}")
        return ' | '.join(parts)


class AlexOrder(models.Model):
    """Ücretli OpenAlex yayın sipariş (IBAN ödeme + admin onayı)"""
    STATUS_CHOICES = (
        ('pending_payment', 'Ödeme Bekleniyor'),
        ('payment_review', 'Ödeme İnceleniyor'),
        ('approved', 'Onaylandı'),
        ('processing', 'İşleniyor'),
        ('completed', 'Tamamlandı - Gönderildi'),
        ('cancelled', 'İptal'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='alex_orders')
    search_job = models.ForeignKey(AlexSearchJob, on_delete=models.CASCADE, related_name='orders')

    abstract_count = models.PositiveIntegerField(verbose_name="İstenen Yayın Sayısı")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Toplam Tutar (TL)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment')

    payment_note = models.TextField(blank=True, verbose_name="Ödeme Açıklaması")
    admin_note = models.TextField(blank=True, verbose_name="Admin Notu")

    results_email_sent = models.BooleanField(default=False)
    results_email_sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "OpenAlex Siparişi"
        verbose_name_plural = "OpenAlex Siparişleri"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"#{str(self.id)[:8]} - {self.user.username} - {self.abstract_count} yayın - {self.get_status_display()}"

    @staticmethod
    def calculate_price(abstract_count):
        """İlk 100 yayın = 250 TL, sonraki her 100 = 100 TL"""
        if abstract_count <= 0:
            return 0
        if abstract_count <= 100:
            return 250
        extra = abstract_count - 100
        extra_blocks = (extra + 99) // 100
        return 250 + (extra_blocks * 100)

    @property
    def is_overdue(self):
        if self.status == 'approved' and self.approved_at:
            return timezone.now() > self.approved_at + timedelta(hours=24)
        return False


class AlexSearchJobProxy(AlexSearchJob):
    class Meta:
        proxy = True
        app_label = 'oaipmh'
        verbose_name = 'OpenAlex Arama İşi'
        verbose_name_plural = 'OpenAlex Arama İşleri'
