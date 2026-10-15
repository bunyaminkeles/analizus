from django.db import migrations

from yoktez.services.yok_universities import UNIVERSITE_ID_BY_NAME


def seed_universities(apps, schema_editor):
    YokTezUniversite = apps.get_model('yoktez', 'YokTezUniversite')
    for name, yok_id in UNIVERSITE_ID_BY_NAME.items():
        YokTezUniversite.objects.update_or_create(
            name=name,
            defaults={'yok_id': yok_id, 'is_active': True},
        )


def unseed_universities(apps, schema_editor):
    YokTezUniversite = apps.get_model('yoktez', 'YokTezUniversite')
    YokTezUniversite.objects.filter(name__in=UNIVERSITE_ID_BY_NAME.keys()).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('yoktez', '0005_yoktezuniversite'),
    ]

    operations = [
        migrations.RunPython(seed_universities, reverse_code=unseed_universities),
    ]
