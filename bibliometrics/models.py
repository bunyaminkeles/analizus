import uuid
from datetime import timedelta
from django.db import models
from django.conf import settings
from django.utils import timezone


class BibliometricJob(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Bekliyor'),
        ('running', 'Çalışıyor'),
        ('completed', 'Tamamlandı'),
        ('failed', 'Başarısız'),
    )

    FORMAT_CHOICES = (
        ('bibtex', 'BibTeX (.bib)'),
        ('csv_wos', 'Web of Science CSV'),
        ('csv_scopus', 'Scopus CSV'),
        ('csv_auto', 'CSV (Otomatik)'),
        ('openalex_json', 'OpenAlex (Otomatik)'),
        ('openalex_txt', 'OpenAlex TXT'),
    )

    SOURCE_UPLOAD = 'upload'
    SOURCE_OPENALEX = 'openalex'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='biblio_jobs')

    original_filename = models.CharField(max_length=255, blank=True)
    file_format = models.CharField(max_length=20, choices=FORMAT_CHOICES, blank=True)
    source = models.CharField(max_length=20, default='upload')  # 'upload' | 'openalex'
    alex_job = models.ForeignKey(
        'openalex.AlexSearchJob',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='biblio_jobs',
    )
    total_records = models.PositiveIntegerField(default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)

    demo_pdf_url = models.URLField(max_length=500, blank=True, default='', verbose_name='Demo PDF URL (S3)')
    full_pdf_url = models.URLField(max_length=500, blank=True, default='', verbose_name='Tam Rapor PDF URL (S3)')

    demo_email_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Bibliometrik Analiz'
        verbose_name_plural = 'Bibliometrik Analizler'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.original_filename} ({self.get_status_display()})'

    def mark_running(self):
        self.status = 'running'
        self.save(update_fields=['status'])

    def mark_completed(self, total_records, file_format, demo_pdf_url='', full_pdf_url=''):
        self.status = 'completed'
        self.total_records = total_records
        self.file_format = file_format
        self.demo_pdf_url = demo_pdf_url
        self.full_pdf_url = full_pdf_url
        self.completed_at = timezone.now()
        self.save(update_fields=[
            'status', 'total_records', 'file_format',
            'demo_pdf_url', 'full_pdf_url', 'completed_at',
        ])

    def mark_failed(self, error_msg):
        self.status = 'failed'
        self.error_message = error_msg
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'completed_at'])

    @staticmethod
    def daily_count_for_user(user):
        today = timezone.now().date()
        return BibliometricJob.objects.filter(
            user=user,
            created_at__date=today,
        ).count()

    @staticmethod
    def get_daily_limit(user):
        """Admin: ∞, Premium: 5, Normal: 2"""
        if user.is_staff or user.is_superuser:
            return 9999
        if hasattr(user, 'profile') and user.profile.is_premium:
            return 5
        return 2


class BibliometricOrder(models.Model):
    STATUS_CHOICES = (
        ('pending_payment', 'Ödeme Bekleniyor'),
        ('payment_review', 'Ödeme İnceleniyor'),
        ('approved', 'Onaylandı'),
        ('processing', 'İşleniyor'),
        ('completed', 'Tamamlandı - Gönderildi'),
        ('cancelled', 'İptal'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='biblio_orders')
    job = models.ForeignKey(BibliometricJob, on_delete=models.CASCADE, related_name='orders')

    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=500, verbose_name='Toplam Tutar (TL)')

    @staticmethod
    def calculate_price(total_records: int):
        """
        Fiyatlar SiteSettings'den alınır:
        0-500      → biblio_price_500
        501-2000   → biblio_price_2000
        2001-3000  → biblio_price_3000
        3001-4000  → biblio_price_4000
        4001-5000  → biblio_price_5000
        5000+      → None (admin ile iletişim)
        """
        from forum.models import SiteSettings
        s = SiteSettings.load()
        if total_records <= 500:
            return s.biblio_price_500
        elif total_records <= 2000:
            return s.biblio_price_2000
        elif total_records <= 3000:
            return s.biblio_price_3000
        elif total_records <= 4000:
            return s.biblio_price_4000
        elif total_records <= 5000:
            return s.biblio_price_5000
        return None  # 5000+ → admin ile iletişim
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment')

    payment_note = models.TextField(blank=True, verbose_name='Ödeme Açıklaması')
    admin_note = models.TextField(blank=True, verbose_name='Admin Notu')

    results_email_sent = models.BooleanField(default=False)
    results_email_sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Bibliometrik Analiz Siparişi'
        verbose_name_plural = 'Bibliometrik Analiz Siparişleri'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'#{str(self.id)[:8]} - {self.user.username} - {self.get_status_display()}'

    @property
    def is_overdue(self):
        if self.status == 'approved' and self.approved_at:
            return timezone.now() > self.approved_at + timedelta(hours=24)
        return False
