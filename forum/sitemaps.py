from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.db.models import Q
from .models import Topic, Category, FreelanceJob, BlogPost, StudyRoom


class StaticViewSitemap(Sitemap):
    """Ana sayfa ve statik sayfalar için sitemap"""
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        pages = ['home', 'about', 'contact', 'gizlilik_politikasi', 'hangi_test', 'forum_index', 'uzman_dizini', 'blog_list', 'proje_talebi']
        from .models import SiteSettings
        if SiteSettings.load().feature_agentic_landing:
            pages.append('ai_cozumler')
        return pages

    def location(self, item):
        return reverse(item)


class TopicSitemap(Sitemap):
    """Forum konuları için sitemap — 1000+ görüntüleme VEYA en faydalı yanıtı
    işaretlenmiş (is_best_answer=True) konular. İkinci kriter, henüz trafik
    almamış ama küratörlü/cevaplanmış konuların (örn. Faz 12 seed içeriği)
    1000 görüntüleme tavuk-yumurta engeline takılmadan sitemap'e girmesini
    sağlar — cevapsız/düşük kaliteli gürültü yine dışarıda kalır."""
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Topic.objects.filter(
            Q(views__gte=1000) | Q(posts__is_best_answer=True)
        ).distinct().order_by('-views')

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


class StudyRoomSitemap(Sitemap):
    """Aktif çalışma odaları için sitemap — arşiv/onay bekleyen odalar dahil edilmez"""
    changefreq = 'daily'
    priority = 0.6

    def items(self):
        return StudyRoom.objects.filter(status='active').order_by('-created_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('studyroom_detail', kwargs={'slug': obj.slug})


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
