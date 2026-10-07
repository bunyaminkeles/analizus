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
