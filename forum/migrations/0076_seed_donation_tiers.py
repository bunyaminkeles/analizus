from django.db import migrations


TIERS = [
    {'name': 'Bronz Destekçi',  'min_amount': 100,  'premium_days': 30},
    {'name': 'Gümüş Destekçi', 'min_amount': 250,  'premium_days': 90},
    {'name': 'Altın Destekçi', 'min_amount': 500,  'premium_days': 180},
    {'name': 'Platin Destekçi','min_amount': 1000, 'premium_days': 365},
]


def seed_tiers(apps, schema_editor):
    DonationTier = apps.get_model('forum', 'DonationTier')
    for t in TIERS:
        DonationTier.objects.get_or_create(
            name=t['name'],
            defaults={
                'min_amount': t['min_amount'],
                'premium_days': t['premium_days'],
                'is_active': True,
            }
        )


def unseed_tiers(apps, schema_editor):
    DonationTier = apps.get_model('forum', 'DonationTier')
    DonationTier.objects.filter(name__in=[t['name'] for t in TIERS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0075_freelancejob_expected_duration'),
    ]

    operations = [
        migrations.RunPython(seed_tiers, unseed_tiers),
    ]
