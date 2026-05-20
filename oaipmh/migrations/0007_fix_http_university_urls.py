from django.db import migrations


HTTP_TO_HTTPS = {
    'http://dspace.akdeniz.edu.tr/oai/request': 'https://dspace.akdeniz.edu.tr/oai/request',
    'http://dspace.cu.edu.tr/oai/request': 'https://dspace.cu.edu.tr/oai/request',
    'http://acikerisim.usak.edu.tr/oai/request': 'https://acikerisim.usak.edu.tr/oai/request',
}


def fix_urls(apps, schema_editor):
    University = apps.get_model('oaipmh', 'University')
    for old_url, new_url in HTTP_TO_HTTPS.items():
        University.objects.filter(oai_url=old_url).update(oai_url=new_url)


def reverse_urls(apps, schema_editor):
    University = apps.get_model('oaipmh', 'University')
    for old_url, new_url in HTTP_TO_HTTPS.items():
        University.objects.filter(oai_url=new_url).update(oai_url=old_url)


class Migration(migrations.Migration):

    dependencies = [
        ('oaipmh', '0006_oaipmhorder_oaipmh_oaip_status_ddad4e_idx_and_more'),
    ]

    operations = [
        migrations.RunPython(fix_urls, reverse_urls),
    ]
