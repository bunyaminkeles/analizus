import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class PubMedSearchJob(models.Model):
    """PubMed yayın arama görevi (demo: ücretsiz, günlük limitli). OpenAlex kalıbı: arama yalnız ilk
    sayfayı saklar, tam veri bibliometri istenince job_runner.ensure_full_results ile çekilir."""
    STATUS_CHOICES = (
        ('pending', 'Bekliyor'),
        ('running', 'Çalışıyor'),
        ('completed', 'Tamamlandı'),
        ('failed', 'Başarısız'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pubmed_searches')

    # Yapısal sorgu parçaları
    # [{"field": "title", "value": "machine learning", "operator": "AND"}, ...]
    query_parts = models.JSONField(default=list, verbose_name="Sorgu Parçaları")
    api_query = models.TextField(blank=True, verbose_name="Oluşturulan PubMed Sorgusu")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_results = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)

    demo_results = models.JSONField(default=list, blank=True)
    all_results = models.JSONField(default=list, blank=True)

    demo_file_url = models.URLField(max_length=500, blank=True, default='', verbose_name="Demo Dosya URL (S3)")

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    demo_email_sent = models.BooleanField(default=False)

    class Meta:
        verbose_name = "PubMed Arama (Demo)"
        verbose_name_plural = "PubMed Aramaları (Demo)"
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
        return PubMedSearchJob.objects.filter(
            user=user,
            created_at__date=today,
        ).count()

    @staticmethod
    def get_daily_limit(user):
        """OpenAlex ile aynı (kullanıcı kararı 29 Eylül 2026): admin sınırsız, diğerleri 3."""
        if user.is_staff or user.is_superuser:
            return 9999
        return 3

    def get_query_summary(self):
        from django.utils.translation import gettext  # aktif dilde (istek / kullanıcı dili)
        field_labels = {
            'title': gettext('Başlık'), 'tiab': gettext('Başlık/Özet'), 'author': gettext('Yazar'),
            'keyword': gettext('Anahtar Kelime'), 'mesh': gettext('MeSH Terimi'),
            'journal': gettext('Dergi/Kaynak'), 'affiliation': gettext('Kurum'), 'doi': 'DOI',
            'year': gettext('Yıl'), 'type': gettext('Yayın Türü'),
        }
        parts = []
        for p in self.query_parts:
            label = field_labels.get(p.get('field', ''), p.get('field', ''))
            parts.append(f"{label}: {p.get('value', '')}")
        return ' | '.join(parts)
