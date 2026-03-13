from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Topic, Category, FreelanceJob


class StaticViewSitemap(Sitemap):
    """Ana sayfa ve statik sayfalar için sitemap"""
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return ['home', 'about', 'contact', 'hangi_test', 'forum_index', 'uzman_dizini']

    def location(self, item):
        return reverse(item)


class TopicSitemap(Sitemap):
    """Forum konuları için sitemap"""
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Topic.objects.all().order_by('-created_at')

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return reverse('topic_detail', args=[obj.pk])


class CategorySitemap(Sitemap):
    """Kategoriler için sitemap"""
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return reverse('category_topics', args=[obj.slug])


class JobSitemap(Sitemap):
    """İş ilanları için sitemap"""
    changefreq = 'daily'

    def items(self):
        return FreelanceJob.objects.filter(status='open').order_by('-created_at')

    def priority(self, obj):
        """Vitrin ilanlarına (1.0) standart ilanlardan (0.8) daha yüksek öncelik ver"""
        return 1.0 if getattr(obj, 'is_featured', False) else 0.8

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return reverse('job_detail', args=[obj.pk])
