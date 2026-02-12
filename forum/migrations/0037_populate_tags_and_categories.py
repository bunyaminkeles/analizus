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
    """Devre dışı bırakıldı - Section ve Category'ler artık admin panelden yönetiliyor"""
    pass


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
