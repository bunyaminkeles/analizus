from django.contrib.auth.models import User
from django.db import models


class EmailBroadcast(models.Model):
    """Admin panelden seçili kullanıcılara gönderilen toplu e-posta kaydı."""
    sent_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='email_broadcasts_sent')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    recipients = models.ManyToManyField(User, related_name='email_broadcasts_received', blank=True)
    recipient_count = models.PositiveIntegerField(default=0)
    sent_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Gönderilen E-posta'
        verbose_name_plural = 'Gönderilen E-postalar'

    def __str__(self):
        return f'{self.subject} ({self.sent_count}/{self.recipient_count})'


class NurtureEmailLog(models.Model):
    """Sayfa gezintisine göre otomatik gönderilen öneri e-postalarının kaydı.

    Aynı kullanıcıya en fazla 14 günde bir gönderilmesini sağlamak için
    (cooldown) ve admin'den izlenebilir olması için tutulur.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nurture_emails_received')
    trigger_date = models.DateField(verbose_name="Tetikleyen son ziyaret tarihi")
    tool_labels = models.CharField(max_length=500, verbose_name="Tetikleyen araçlar")
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'Otomatik Öneri E-postası'
        verbose_name_plural = 'Otomatik Öneri E-postaları'

    def __str__(self):
        return f'{self.user.username} — {self.trigger_date} ({self.tool_labels})'
