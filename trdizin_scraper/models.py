from django.db import models

class TrdizinArticle(models.Model):
    """
    TR Dizin'den çekilen bir makalenin verilerini temsil eder.
    """
    trdizin_id = models.CharField(max_length=100, unique=True, verbose_name="TR Dizin ID")
    title = models.TextField(verbose_name="Başlık")
    authors = models.JSONField(default=list, verbose_name="Yazarlar")
    publication_year = models.PositiveIntegerField(null=True, blank=True, verbose_name="Yayın Yılı")
    journal = models.CharField(max_length=500, blank=True, verbose_name="Dergi")
    abstract = models.TextField(blank=True, verbose_name="Özet")
    keywords = models.JSONField(default=list, verbose_name="Anahtar Kelimeler")
    scraped_at = models.DateTimeField(auto_now_add=True, verbose_name="Çekilme Tarihi")
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "TR Dizin Makalesi"
        verbose_name_plural = "TR Dizin Makaleleri"
        ordering = ['-publication_year']