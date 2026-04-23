import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from forum.models import BlogCategory, BlogPost
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'SEO uyumlu stratejik blog yazılarını tohumlar (Görev 11)'

    def turkish_slugify(self, text):
        replacements = {
            'ı': 'i', 'İ': 'i', 'ğ': 'g', 'Ğ': 'g',
            'ü': 'u', 'Ü': 'u', 'ş': 's', 'Ş': 's',
            'ö': 'o', 'Ö': 'o', 'ç': 'c', 'Ç': 'c',
        }
        for src, dest in replacements.items():
            text = text.replace(src, dest)
        return slugify(text)

    def handle(self, *args, **kwargs):
        self.stdout.write('Kategoriler ve SEO uyumlu blog yazıları oluşturuluyor...')
        
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.first()

        # 1. Kategoriler
        categories = [
            {'name': 'İstatistik & SPSS', 'description': 'Akademik veri analizi rehberleri.'},
            {'name': 'Yapay Zeka & AI', 'description': 'Makine öğrenmesi ve NLP.'},
            {'name': 'Ekonometri', 'description': 'Finansal modelleme ve zaman serisi.'},
            {'name': 'Veri Bilimi', 'description': 'Python, R ve veri görselleştirme.'},
            {'name': 'İçerik & Editörlük', 'description': 'Akademik yazım ve nitel analiz.'}
        ]
        
        cat_objs = {}
        for cat in categories:
            obj, _ = BlogCategory.objects.get_or_create(
                slug=self.turkish_slugify(cat['name']),
                defaults={'name': cat['name'], 'description': cat['description']}
            )
            cat_objs[cat['name']] = obj

        # 2. Blog Yazıları (Görev 11 Stratejisi)
        posts = [
            {
                'title': 'SPSS ile Normallik Testi: Hangi Durumda Hangi Test Kullanılmalı?',
                'category': 'İstatistik & SPSS',
                'excerpt': 'Tez yazımında en çok kafa karıştıran Kolmogorov-Smirnov ve Shapiro-Wilk testlerinin doğru kullanımı.',
                'content': '<p>Örneklem büyüklüğünüz 50\'den küçükse Shapiro-Wilk, büyükse Kolmogorov-Smirnov kullanmalısınız. Aksi halde Tip 1 hataya düşebilirsiniz...</p>'
            },
            {
                'title': 'Python ile Sentiment Analizi (Duygu Analizi) Nasıl Yapılır?',
                'category': 'Yapay Zeka & AI',
                'excerpt': 'Sosyal medya verilerini veya müşteri yorumlarını Hugging Face ve BERT modelleri ile analiz etme rehberi.',
                'content': '<p>NLTK veya spaCy yerine, modern Türkçe NLP projelerinde BERTurk modelini kullanarak duygu analizi başarınızı %90\'ların üzerine çıkarabilirsiniz...</p>'
            },
            {
                'title': 'Panel Veri Ekonometrisinde Model Seçimi: Stata mı EViews mi?',
                'category': 'Ekonometri',
                'excerpt': 'Sabit ve rassal etkiler (Fixed/Random Effects) modellerinde Hausman testi uygulaması ve yazılım seçimi.',
                'content': '<p>EViews kullanıcı dostu bir arayüz sunarken, Stata özellikle dinamik panel veri (Arellano-Bond GMM) analizlerinde rakipsizdir...</p>'
            },
            {
                'title': 'Akademik Makale Editörlüğünde Dikkat Edilecek 10 Kritik Nokta',
                'category': 'İçerik & Editörlük',
                'excerpt': 'Q1 dergilerden ret almanızı engelleyecek, APA 7 standartlarına uygun akademik yazım ve editörlük sırları.',
                'content': '<p>Bir makalenin reddedilme sebeplerinin %40\'ı zayıf metodoloji anlatımı ve hedef derginin yazım kurallarına (formatting) uyulmamasıdır...</p>'
            },
            {
                'title': 'ChatGPT ve LLM\'ler Akademik Araştırmalarda Nasıl Etik Kullanılır?',
                'category': 'Yapay Zeka & AI',
                'excerpt': 'Yapay zekayı makale yazdırmak için değil, literatür taramak ve kodları debug etmek için kullanmanın sınırları.',
                'content': '<p>LLM\'lerin ürettiği metinler (halüsinasyonlar) doğrudan kullanılamaz. Ancak "Prompt Engineering" ile mükemmel bir araştırma asistanı yaratabilirsiniz...</p>'
            },
            {
                'title': 'Veri Bilimciler İçin A/B Testi Tasarımı ve İstatistiksel Güç',
                'category': 'Veri Bilimi',
                'excerpt': 'Sektördeki veri bilimcilerin ürün kararlarını alırken kullandığı A/B testlerinin matematiksel altyapısı.',
                'content': '<p>Sadece p değerine bakmak yanıltıcıdır. Etki büyüklüğü (Effect Size) ve istatistiksel güç (Power) hesaplanmadan A/B testi sonlandırılmamalıdır...</p>'
            },
            {
                'title': 'Nitel Veri Analizinde MAXQDA ve NVivo Karşılaştırması',
                'category': 'İçerik & Editörlük',
                'excerpt': 'Derinlemesine mülakatları kodlarken hangi nitel analiz yazılımı projenize daha uygun?',
                'content': '<p>MAXQDA görselleştirme ve karma yöntemler (Mixed Methods) konusunda öne çıkarken, NVivo devasa veri setlerinin yönetiminde güçlüdür...</p>'
            }
        ]

        for post in posts:
            slug = self.turkish_slugify(post['title'])
            if not BlogPost.objects.filter(slug=slug).exists():
                BlogPost.objects.create(
                    title=post['title'],
                    slug=slug,
                    author=admin_user,
                    category=cat_objs[post['category']],
                    excerpt=post['excerpt'],
                    content=post['content'],
                    status='published',
                    views=random.randint(150, 1200)
                )
                
        self.stdout.write(self.style.SUCCESS('✅ SEO uyumlu blog yazıları başarıyla tohumlandı!'))