from django.db import migrations


def create_default_tiers(apps, schema_editor):
    DonationTier = apps.get_model('forum', 'DonationTier')

    # Varsayılan katmanları oluştur (yoksa)
    default_tiers = [
        {'min_amount': 50, 'premium_days': 7, 'name': 'Bronz'},
        {'min_amount': 100, 'premium_days': 30, 'name': 'Gümüş'},
        {'min_amount': 200, 'premium_days': 90, 'name': 'Altın'},
    ]

    for tier_data in default_tiers:
        DonationTier.objects.get_or_create(
            min_amount=tier_data['min_amount'],
            defaults={
                'premium_days': tier_data['premium_days'],
                'name': tier_data['name'],
                'is_active': True
            }
        )


def reverse_tiers(apps, schema_editor):
    # Rollback için - silme yapmıyoruz, sadece pass
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0031_add_donation_tier'),
    ]

    operations = [
        migrations.RunPython(create_default_tiers, reverse_tiers),
    ]
