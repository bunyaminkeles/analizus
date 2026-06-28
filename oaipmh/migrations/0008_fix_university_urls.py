from django.db import migrations

URL_UPDATES = [
    # Çukurova ve Uşak — HTTPS desteklemiyor, HTTP'ye dön
    (
        'https://dspace.cu.edu.tr/oai/request',
        'http://dspace.cu.edu.tr/oai/request',
        None,
    ),
    (
        'https://acikerisim.usak.edu.tr/oai/request',
        'http://acikerisim.usak.edu.tr/oai/request',
        None,
    ),
    # Uludağ ve BEUN — DSpace 7'ye geçmiş, /server/oai/request kullanıyor
    (
        'https://acikerisim.uludag.edu.tr/oai/request',
        'https://acikerisim.uludag.edu.tr/server/oai/request',
        None,
    ),
    (
        'https://acikarsiv.beun.edu.tr/oai/request',
        'https://acikarsiv.beun.edu.tr/server/oai/request',
        None,
    ),
]

# Akdeniz ve Fırat — sunucu erişilemez veya WAF engelliyor
DEACTIVATE_DOMAINS = ['akdeniz.edu.tr', 'firat.edu.tr']


def apply(apps, schema_editor):
    University = apps.get_model('oaipmh', 'University')
    for old_url, new_url, _ in URL_UPDATES:
        University.objects.filter(oai_url=old_url).update(oai_url=new_url)
    University.objects.filter(domain__in=DEACTIVATE_DOMAINS).update(is_active=False)


def revert(apps, schema_editor):
    University = apps.get_model('oaipmh', 'University')
    for old_url, new_url, _ in URL_UPDATES:
        University.objects.filter(oai_url=new_url).update(oai_url=old_url)
    University.objects.filter(domain__in=DEACTIVATE_DOMAINS).update(is_active=True)


class Migration(migrations.Migration):

    dependencies = [
        ('oaipmh', '0007_fix_http_university_urls'),
    ]

    operations = [
        migrations.RunPython(apply, reverse_code=revert),
    ]
