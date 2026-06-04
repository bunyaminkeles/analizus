from django.contrib.auth.models import User
from django.db import models


class PageView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='page_views', db_index=True)
    path = models.CharField(max_length=200)
    tab_name = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Sayfa Ziyareti'
        verbose_name_plural = 'Sayfa Ziyaretleri'

    def __str__(self):
        return f'{self.user.username} → {self.tab_name} ({self.timestamp:%Y-%m-%d %H:%M})'


class PageViewSummary(models.Model):
    """Ham loglar silinince burada kalıcı özet tutulur."""
    date = models.DateField(db_index=True)
    path = models.CharField(max_length=200)
    tab_name = models.CharField(max_length=100)
    visit_count = models.PositiveIntegerField(default=0)
    unique_users = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['date', 'path']
        ordering = ['-date', '-visit_count']
        verbose_name = 'Ziyaret Özeti'
        verbose_name_plural = 'Ziyaret Özetleri'

    def __str__(self):
        return f'{self.date} | {self.tab_name} | {self.visit_count} ziyaret'
