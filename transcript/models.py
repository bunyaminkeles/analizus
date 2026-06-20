from django.db import models
from django.contrib.auth.models import User


class TranscriptSettings(models.Model):
    """Singleton — admin panelinden yönetilen global ayarlar."""
    max_minutes_admin = models.PositiveIntegerField(
        default=120,
        verbose_name="Admin maksimum dakika",
        help_text="Admin/staff kullanıcılar için izin verilen maksimum video süresi (dakika). Standart kullanıcılar bu değerin yarısını kullanabilir.",
    )


    class Meta:
        verbose_name = "Transcript Ayarları"
        verbose_name_plural = "Transcript Ayarları"

    def __str__(self):
        return f"Transcript Ayarları (admin maks: {self.max_minutes_admin} dk)"

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def max_minutes_for(self, user):
        if user.is_staff or user.is_superuser:
            return self.max_minutes_admin
        return self.max_minutes_admin // 2


class TranscriptJob(models.Model):
    STATUS_PENDING = "pending"
    STATUS_RUNNING = "running"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Bekliyor"),
        (STATUS_RUNNING, "İşleniyor"),
        (STATUS_COMPLETED, "Tamamlandı"),
        (STATUS_FAILED, "Hata"),
    ]

    DELIVERY_DOWNLOAD = "download"
    DELIVERY_EMAIL = "email"
    DELIVERY_CHOICES = [
        (DELIVERY_DOWNLOAD, "İndir (TXT)"),
        (DELIVERY_EMAIL, "E-posta ile gönder"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transcript_jobs")
    video_url = models.URLField(verbose_name="Video URL")
    video_id = models.CharField(max_length=64, blank=True)
    video_title = models.CharField(max_length=512, blank=True)
    video_duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    language_requested = models.CharField(max_length=10, blank=True, help_text="Boşsa otomatik seçilir")
    language_used = models.CharField(max_length=10, blank=True)
    translated = models.BooleanField(default=False)
    delivery = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default=DELIVERY_DOWNLOAD)
    email_address = models.EmailField(blank=True)
    transcript_text = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Transcript İşi"
        verbose_name_plural = "Transcript İşleri"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} — {self.video_id} ({self.status})"

    @property
    def duration_minutes(self):
        if self.video_duration_seconds:
            return self.video_duration_seconds / 60
        return None
