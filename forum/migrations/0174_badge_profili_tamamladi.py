# "Profili Tamamladı" rozetini migration ile oluşturur — create_badges komutu deploy.sh'de
# yalnız kategori sayısı 0 ise çalışıyor (Render'ın canlı DB'si dolu olduğu için atlanıyor,
# shell erişimi de yok). Migration'lar her deploy'da koşulsuz çalıştığı için güvenilir yol bu.
from django.db import migrations


def create_badge(apps, schema_editor):
    Badge = apps.get_model('forum', 'Badge')
    Badge.objects.update_or_create(
        slug='profili-tamamladi',
        defaults={
            'name': 'Profili Tamamladı',
            'description': 'Profilini %100 doldurdu',
            'icon': 'bi-person-check-fill',
            'color': '#10b981',
            'badge_type': 'achievement',
            'points_required': 0,
        },
    )


def delete_badge(apps, schema_editor):
    Badge = apps.get_model('forum', 'Badge')
    Badge.objects.filter(slug='profili-tamamladi').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0173_servicepage_sections_expand'),
    ]

    operations = [
        migrations.RunPython(create_badge, delete_badge),
    ]
