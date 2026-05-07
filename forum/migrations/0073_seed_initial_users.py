from django.db import migrations


KULLANICILAR = [
    ("dr_ayse_kaya",     "bkeles74+ayse@gmail.com"),
    ("mehmet_yilmaz42",  "bkeles74+mehmet@gmail.com"),
    ("zeynep_arslan",    "bkeles74+zeynep@gmail.com"),
    ("ibrahim_celik",    "bkeles74+ibrahim@gmail.com"),
    ("fatma_demir_dr",   "bkeles74+fatma@gmail.com"),
    ("ali_ozturk_phd",   "bkeles74+ali@gmail.com"),
    ("elif_sahin",       "bkeles74+elif@gmail.com"),
    ("murat_koc_stat",   "bkeles74+murat@gmail.com"),
    ("selin_yildiz",     "bkeles74+selin@gmail.com"),
    ("hasan_kurt",       "bkeles74+hasan@gmail.com"),
    ("neslihan_ay",      "bkeles74+neslihan@gmail.com"),
    ("burak_ozdemir",    "bkeles74+burak@gmail.com"),
    ("merve_aksoy",      "bkeles74+merve@gmail.com"),
    ("emre_simsek",      "bkeles74+emre@gmail.com"),
    ("cansu_aydın",      "bkeles74+cansu@gmail.com"),
]


def seed_users(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Profile = apps.get_model("forum", "Profile")

    for username, email in KULLANICILAR:
        if User.objects.filter(username=username).exists():
            continue
        if User.objects.filter(email=email).exists():
            continue
        user = User.objects.create_user(
            username=username,
            email=email,
            password="AnalizUs!2026",
        )
        Profile.objects.get_or_create(
            user=user,
            defaults={"email_verified": True},
        )


def reverse_seed(apps, schema_editor):
    User = apps.get_model("auth", "User")
    usernames = [u for u, _ in KULLANICILAR]
    User.objects.filter(username__in=usernames).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("forum", "0072_add_blogtag_and_post_level"),
    ]

    operations = [
        migrations.RunPython(seed_users, reverse_seed),
    ]
