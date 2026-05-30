from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Topic, Category, FreelanceJob, BlogPost


class StaticViewSitemap(Sitemap):
    """Ana sayfa ve statik sayfalar için sitemap"""
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return ['home', 'about', 'contact', 'hangi_test', 'forum_index', 'uzman_dizini', 'blog_list']

    def location(self, item):
        return reverse(item)


class TopicSitemap(Sitemap):
    """Forum konuları için sitemap — sadece 1000+ görüntüleme alanlar"""
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Topic.objects.filter(views__gte=1000).order_by('-views')

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


class BlogPostSitemap(Sitemap):
    """Yayınlanmış blog yazıları için sitemap"""
    changefreq = 'monthly'
    priority = 0.9

    def items(self):
        return BlogPost.objects.filter(status='published').order_by('-published_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('blog_detail', kwargs={'slug': obj.slug})


class IstatistikSitemap(Sitemap):
    """İstatistik araç landing sayfaları için sitemap"""
    changefreq = 'monthly'
    priority = 0.9

    def items(self):
        return [
            'cronbach',
            'normallik',
            'betimsel',
            'korelasyon',
            'orneklem',
            'ttesti',
            'anova',
            'mann-whitney',
            'kruskal-wallis',
            'ki-kare',
            'lineer-regresyon',
            'lojistik-regresyon',
            'friedman',
            'tekrarli-anova',
            'karar-agaci',
            'svm',
            'afa',
            'wilcoxon',
        ]

    def location(self, item):
        return f'/analiz/{item}/'


class ToolsSitemap(Sitemap):
    """Diğer araç landing sayfaları için sitemap"""
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return [
            ('yoktez', 'landing'),
            ('trdizin', 'landing'),
            ('openalex', 'landing'),
            ('oaipmh', 'landing'),
            ('bibliometrics', 'landing'),
            ('semanticscholar', 'landing'),
        ]

    def location(self, item):
        namespace, name = item
        return reverse(f'{namespace}:{name}')
