from django.db import migrations


def fix(apps, schema_editor):
    BlogPost     = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')

    kategori, _ = BlogCategory.objects.get_or_create(
        slug='istatistik-101',
        defaults={'name': 'İstatistik 101', 'icon': 'bi-bar-chart', 'color': '#00d2ff'},
    )

    BlogPost.objects.filter(
        slug='cronbach-alpha-degeri-tezde-nasil-raporlanir'
    ).update(
        excerpt='Cronbach Alpha (α), tez ve akademik araştırmalarda ölçek güvenilirliğini ölçen iç tutarlılık katsayısıdır. .70 eşiği, APA raporlama kuralları ve madde silme analizi hakkında kapsamlı rehber.',
        category=kategori,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0077_blog_cronbach_alpha'),
    ]

    operations = [
        migrations.RunPython(fix, migrations.RunPython.noop),
    ]
