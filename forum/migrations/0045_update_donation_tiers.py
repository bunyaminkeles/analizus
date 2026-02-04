from django.db import migrations


def update_tiers(apps, schema_editor):
    DonationTier = apps.get_model('forum', 'DonationTier')

    # Mevcut tier'ları temizle ve yeniden oluştur
    DonationTier.objects.all().delete()

    tiers = [
        {'min_amount': 50, 'premium_days': 7, 'name': 'Bronz Destekçi'},
        {'min_amount': 100, 'premium_days': 15, 'name': 'Gümüş Destekçi'},
        {'min_amount': 250, 'premium_days': 30, 'name': 'Altın Destekçi'},
        {'min_amount': 500, 'premium_days': 90, 'name': 'Platin Destekçi'},
    ]

    for tier_data in tiers:
        DonationTier.objects.create(is_active=True, **tier_data)


def reverse_tiers(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0044_edu_proposal_expires'),
    ]

    operations = [
        migrations.RunPython(update_tiers, reverse_tiers),
    ]
