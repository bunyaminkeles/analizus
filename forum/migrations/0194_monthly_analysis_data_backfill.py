# Generated manually — veri migration'ı (RunPython)

from django.db import migrations


# Kademe adı → aylık analiz hakkı (araç başına). DONATION_TIER_NAME_MSGIDS ile aynı 4 isim.
TIER_CREDITS = {
    'Bronz Destekçi': 3,
    'Gümüş Destekçi': 5,
    'Altın Destekçi': 8,
    'Platin Destekçi': 15,
}


def set_tier_credits_and_backfill(apps, schema_editor):
    DonationTier = apps.get_model('forum', 'DonationTier')
    Donation = apps.get_model('forum', 'Donation')
    Profile = apps.get_model('forum', 'Profile')

    for tier in DonationTier.objects.all():
        credits = TIER_CREDITS.get(tier.name)
        if credits is not None:
            tier.monthly_analysis_credits = credits
            tier.save(update_fields=['monthly_analysis_credits'])

    # Eski tamamlanmış bağışlar için tier FK'yi best-effort doldur:
    # premium_days_promised değerine en yakın (<=) DonationTier eşleştirilir.
    tiers_by_days = list(DonationTier.objects.order_by('-premium_days'))
    for donation in Donation.objects.filter(status='completed', tier__isnull=True):
        days = donation.premium_days_promised or donation.premium_days_granted
        if not days:
            continue
        match = next((t for t in tiers_by_days if t.premium_days <= days), None)
        if match:
            donation.tier = match
            donation.save(update_fields=['tier'])

    # Şu an aktif Premium olan kullanıcılar için: en son tamamlanmış bağışının (artık tier'ı
    # dolu) kademesini profile.premium_tier'a yaz — "en yüksek kademe kalıcı" kuralı burada da
    # uygulanır (kullanıcının geçmiş bağışları arasında en yüksek min_amount'lu tier seçilir).
    for profile in Profile.objects.filter(account_type='Premium', premium_tier__isnull=True):
        best_tier = None
        for donation in profile.user.donations.filter(status='completed', tier__isnull=False).select_related('tier'):
            if best_tier is None or donation.tier.min_amount > best_tier.min_amount:
                best_tier = donation.tier
        if best_tier:
            profile.premium_tier = best_tier
            profile.save(update_fields=['premium_tier'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0193_monthly_analysis_tier_fields'),
    ]

    operations = [
        migrations.RunPython(set_tier_credits_and_backfill, noop_reverse),
    ]
