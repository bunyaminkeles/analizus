from django.db import migrations


def create_default_tags(apps, schema_editor):
    """Varsayılan etiketleri oluştur"""
    TopicTag = apps.get_model('forum', 'TopicTag')

    # Yazılım tag'leri
    software_tags = [
        {'name': 'SPSS', 'slug': 'spss', 'icon': 'bi-bar-chart-fill', 'color': '#0066cc', 'tag_type': 'software', 'order': 1},
        {'name': 'Python', 'slug': 'python', 'icon': 'bi-code-slash', 'color': '#3776ab', 'tag_type': 'software', 'order': 2},
        {'name': 'R', 'slug': 'r', 'icon': 'bi-graph-up', 'color': '#276dc3', 'tag_type': 'software', 'order': 3},
        {'name': 'Excel', 'slug': 'excel', 'icon': 'bi-file-earmark-spreadsheet', 'color': '#217346', 'tag_type': 'software', 'order': 4},
        {'name': 'Jamovi', 'slug': 'jamovi', 'icon': 'bi-pie-chart', 'color': '#7f3f98', 'tag_type': 'software', 'order': 5},
        {'name': 'JASP', 'slug': 'jasp', 'icon': 'bi-pie-chart-fill', 'color': '#2e86de', 'tag_type': 'software', 'order': 6},
        {'name': 'Stata', 'slug': 'stata', 'icon': 'bi-diagram-3', 'color': '#1a5276', 'tag_type': 'software', 'order': 7},
        {'name': 'AMOS', 'slug': 'amos', 'icon': 'bi-diagram-2', 'color': '#5d6d7e', 'tag_type': 'software', 'order': 8},
    ]

    # Durum tag'leri
    status_tags = [
        {'name': 'Çözüldü', 'slug': 'cozuldu', 'icon': 'bi-check-circle-fill', 'color': '#28a745', 'tag_type': 'status', 'order': 100},
        {'name': 'Acil', 'slug': 'acil', 'icon': 'bi-exclamation-triangle-fill', 'color': '#dc3545', 'tag_type': 'status', 'order': 101},
        {'name': 'Tartışma', 'slug': 'tartisma', 'icon': 'bi-chat-dots', 'color': '#6c757d', 'tag_type': 'status', 'order': 102},
    ]

    for tag_data in software_tags + status_tags:
        TopicTag.objects.get_or_create(slug=tag_data['slug'], defaults=tag_data)


def create_new_categories(apps, schema_editor):
    """Yeni kategori yapısını oluştur"""
    Section = apps.get_model('forum', 'Section')
    Category = apps.get_model('forum', 'Category')

    # Yeni bölüm ve kategoriler
    new_structure = [
        {
            'title': 'Analiz Yöntemleri',
            'order': 1,
            'categories': [
                {'title': 'Betimsel & Keşifsel Analiz', 'slug': 'betimsel-kesifsel', 'description': 'Tanımlayıcı istatistikler, frekans dağılımları, grafikler', 'icon_class': 'bi-bar-chart'},
                {'title': 'Karşılaştırma Testleri', 'slug': 'karsilastirma-testleri', 'description': 't-testi, ANOVA, MANOVA, non-parametrik testler', 'icon_class': 'bi-arrows-collapse'},
                {'title': 'İlişki Analizi', 'slug': 'iliski-analizi', 'description': 'Korelasyon, regresyon, lojistik regresyon', 'icon_class': 'bi-bezier2'},
                {'title': 'Boyut İndirgeme', 'slug': 'boyut-indirgeme', 'description': 'Faktör analizi, PCA, kümeleme', 'icon_class': 'bi-layers'},
                {'title': 'Yapısal Eşitlik', 'slug': 'yapisal-esitlik', 'description': 'SEM, yol analizi, doğrulayıcı faktör analizi', 'icon_class': 'bi-diagram-3'},
                {'title': 'Nitel Analiz', 'slug': 'nitel-analiz', 'description': 'İçerik analizi, tematik analiz, nitel kodlama', 'icon_class': 'bi-file-text'},
            ]
        },
        {
            'title': 'Araçlar & Teknik',
            'order': 2,
            'categories': [
                {'title': 'Kurulum & Konfigürasyon', 'slug': 'kurulum-konfigurasyon', 'description': 'Yazılım kurulumu, ayarlar, lisanslama', 'icon_class': 'bi-gear'},
                {'title': 'Kod & Syntax Paylaşımı', 'slug': 'kod-syntax', 'description': 'Hazır kodlar, syntax örnekleri, scriptler', 'icon_class': 'bi-code-square'},
                {'title': 'Hata Çözümleri', 'slug': 'hata-cozumleri', 'description': 'Yazılım hataları, error mesajları, troubleshooting', 'icon_class': 'bi-bug'},
            ]
        },
        {
            'title': 'Akademik Destek',
            'order': 3,
            'categories': [
                {'title': 'Tez & Makale Süreci', 'slug': 'tez-makale', 'description': 'Akademik yazım, dergi seçimi, yayın süreci', 'icon_class': 'bi-journal-text'},
                {'title': 'Veri Toplama & Örneklem', 'slug': 'veri-toplama', 'description': 'Anket tasarımı, örneklem hesaplama, veri girişi', 'icon_class': 'bi-collection'},
                {'title': 'Etik & Metodoloji', 'slug': 'etik-metodoloji', 'description': 'Araştırma etiği, metodoloji seçimi, geçerlik-güvenirlik', 'icon_class': 'bi-shield-check'},
            ]
        },
    ]

    for section_data in new_structure:
        section, created = Section.objects.get_or_create(
            title=section_data['title'],
            defaults={'order': section_data['order']}
        )

        for cat_data in section_data['categories']:
            Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'section': section,
                    'title': cat_data['title'],
                    'description': cat_data['description'],
                    'icon_class': cat_data['icon_class'],
                }
            )


def reverse_func(apps, schema_editor):
    """Geri alma işlemi - tag'leri silme"""
    TopicTag = apps.get_model('forum', 'TopicTag')
    TopicTag.objects.filter(slug__in=[
        'spss', 'python', 'r', 'excel', 'jamovi', 'jasp', 'stata', 'amos',
        'cozuldu', 'acil', 'tartisma'
    ]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0036_add_topic_tags'),
    ]

    operations = [
        migrations.RunPython(create_default_tags, reverse_func),
        migrations.RunPython(create_new_categories, migrations.RunPython.noop),
    ]
