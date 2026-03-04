import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class University(models.Model):
    name = models.CharField(max_length=200, verbose_name="Üniversite Adı")
    domain = models.CharField(max_length=100, verbose_name="Domain")
    oai_url = models.URLField(verbose_name="OAI-PMH URL")
    repo_name = models.CharField(max_length=200, blank=True, verbose_name="Repo Adı")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    class Meta:
        verbose_name = "Üniversite"
        verbose_name_plural = "Üniversiteler"
        ordering = ['name']

    def __str__(self):
        return self.name


class OAIPMHSearchJob(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Bekliyor'),
        ('running', 'Çalışıyor'),
        ('completed', 'Tamamlandı'),
        ('failed', 'Başarısız'),
    ]
    SEARCH_TYPE_CHOICES = [
        ('keyword', 'Anahtar Kelime Araması'),
        ('browse', 'Üniversite Tez Taraması'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='oaipmh_jobs')
    search_type = models.CharField(max_length=10, choices=SEARCH_TYPE_CHOICES, default='keyword')

    # Keyword modu alanları
    keyword = models.CharField(max_length=300, blank=True, verbose_name="Başlık Filtresi")
    abstract_query = models.CharField(max_length=300, blank=True, verbose_name="Özet Filtresi")
    university_ids = models.JSONField(default=list, blank=True, verbose_name="Seçili Üniversite ID'leri")
    year_from = models.IntegerField(null=True, blank=True, verbose_name="Başlangıç Yılı")
    year_to = models.IntegerField(null=True, blank=True, verbose_name="Bitiş Yılı")

    # Browse modu alanı
    university = models.ForeignKey(
        University, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='browse_jobs', verbose_name="Üniversite"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_results = models.PositiveIntegerField(default=0)
    demo_results = models.JSONField(default=list)
    all_results = models.JSONField(default=list)
    demo_file_url = models.URLField(blank=True)
    all_results_file_url = models.URLField(blank=True)
    demo_email_sent = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Arama İşi"
        verbose_name_plural = "Arama İşleri"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_search_type_display()} - {self.status}"

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
        self.save(update_fields=['status', 'error_message'])

    def get_query_summary(self):
        if self.search_type == 'keyword':
            parts = []
            if self.keyword:
                parts.append(f'Başlık:"{self.keyword}"')
            if self.abstract_query:
                parts.append(f'Özet:"{self.abstract_query}"')
            if self.year_from or self.year_to:
                parts.append(f"({self.year_from or '?'}-{self.year_to or '?'})")
            if self.university_ids:
                parts.append(f"[{len(self.university_ids)} üniversite]")
            return ' | '.join(parts) if parts else 'Genel Tarama'
        else:
            return f"{self.university.name if self.university else '?'} - Tüm Tezler"

    @classmethod
    def daily_count_for_user(cls, user):
        today = timezone.now().date()
        return cls.objects.filter(user=user, created_at__date=today).count()

    @classmethod
    def get_daily_limit(cls, user):
        """Admin: ∞, Premium: 7, Normal: 1"""
        if user.is_staff or user.is_superuser:
            return 9999
        if hasattr(user, 'profile') and user.profile.is_premium:
            return 7
        return 1


class OAIPMHOrder(models.Model):
    STATUS_CHOICES = [
        ('pending_payment', 'Ödeme Bekleniyor'),
        ('payment_review', 'Ödeme İncelemede'),
        ('approved', 'Onaylandı'),
        ('completed', 'Tamamlandı'),
        ('cancelled', 'İptal Edildi'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='oaipmh_orders')
    search_job = models.ForeignKey(OAIPMHSearchJob, on_delete=models.CASCADE, related_name='orders')
    abstract_count = models.PositiveIntegerField(verbose_name="İstenen Kayıt Sayısı")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Toplam Fiyat (TL)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment')
    payment_note = models.TextField(blank=True, verbose_name="Ödeme Notu")
    admin_note = models.TextField(blank=True, verbose_name="Admin Notu")
    results_email_sent = models.BooleanField(default=False)
    results_email_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Sipariş"
        verbose_name_plural = "Siparişler"
        ordering = ['-created_at']

    def __str__(self):
        return f"Sipariş #{str(self.id)[:8]} - {self.user.username}"

    @staticmethod
    def calculate_price(abstract_count):
        if abstract_count <= 0:
            return 0
        price = 250
        if abstract_count > 100:
            extra = ((abstract_count - 1) // 100)
            price += extra * 100
        return price


from yoktez.models import YokTezSearchJob  # noqa: E402


class YokTezSearchJobProxy(YokTezSearchJob):
    class Meta:
        proxy = True
        verbose_name = 'YÖK Tez Araması'
        verbose_name_plural = 'YÖK Tez Aramaları'
