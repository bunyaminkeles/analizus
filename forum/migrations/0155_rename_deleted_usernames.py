"""Anonimleştirilmiş hesapların kullanıcı adını okunur biçime çevirir:
`deleted_<hex>` → `silinmis-kullanici-<hex>` (kullanıcı kararı, 25 Eylül 2026).

Yalnızca hesap silme cron'unun ürettiği hesaplar (e-posta `@deleted.invalid`)
etkilenir — kendine `deleted_...` adı seçmiş gerçek kullanıcılara dokunulmaz.
Veri migration'ı; şema değişmez.
"""
from django.db import migrations


def forwards(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    qs = User.objects.filter(username__startswith='deleted_', email__endswith='@deleted.invalid')
    for user in qs.iterator():
        user.username = 'silinmis-kullanici-' + user.username[len('deleted_'):]
        user.save(update_fields=['username'])


def backwards(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    qs = User.objects.filter(username__startswith='silinmis-kullanici-', email__endswith='@deleted.invalid')
    for user in qs.iterator():
        user.username = 'deleted_' + user.username[len('silinmis-kullanici-'):]
        user.save(update_fields=['username'])


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0154_profile_preferred_language'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
