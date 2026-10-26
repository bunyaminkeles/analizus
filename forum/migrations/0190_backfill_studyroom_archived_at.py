# Faz 3 backfill — bu özellikten önce zaten 'archived' olan odalar
# archived_at=NULL kalıyordu, bu yüzden retention cron'una hiç girmiyordu.
# ends_at değerini archived_at için proxy olarak kullanıyoruz.

from django.db import migrations, models


def backfill_archived_at(apps, schema_editor):
    StudyRoom = apps.get_model('forum', 'StudyRoom')
    StudyRoom.objects.filter(
        status='archived', archived_at__isnull=True
    ).update(archived_at=models.F('ends_at'))


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0189_roomexportauditlog'),
    ]

    operations = [
        migrations.RunPython(backfill_archived_at, noop_reverse),
    ]
