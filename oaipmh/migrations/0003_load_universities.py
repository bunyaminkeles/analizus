from django.db import migrations

UNIVERSITIES = [
    {"university": "ODTÜ", "domain": "metu.edu.tr", "oai_url": "https://dspace.metu.edu.tr/oai/request", "repo_name": "OpenMETU"},
    {"university": "İTÜ", "domain": "itu.edu.tr", "oai_url": "https://dspace.itu.edu.tr/oai/request", "repo_name": "İTÜ Academic Archive"},
    {"university": "Dokuz Eylül Üniversitesi", "domain": "deu.edu.tr", "oai_url": "https://acikerisim.deu.edu.tr/oai/request", "repo_name": "DSpace at Dokuz Eylul University"},
    {"university": "Akdeniz Üniversitesi", "domain": "akdeniz.edu.tr", "oai_url": "http://dspace.akdeniz.edu.tr/oai/request", "repo_name": "Akdeniz Üniversitesi DSpace"},
    {"university": "Çukurova Üniversitesi", "domain": "cu.edu.tr", "oai_url": "http://dspace.cu.edu.tr/oai/request", "repo_name": "Cukurova University Institutional Repository"},
    {"university": "Uludağ Üniversitesi", "domain": "uludag.edu.tr", "oai_url": "https://acikerisim.uludag.edu.tr/oai/request", "repo_name": "Bursa Uludag University"},
    {"university": "Sakarya Üniversitesi", "domain": "sakarya.edu.tr", "oai_url": "https://acikerisim.sakarya.edu.tr/oai/request", "repo_name": "Sakarya Üniversitesi"},
    {"university": "Fırat Üniversitesi", "domain": "firat.edu.tr", "oai_url": "https://openaccess.firat.edu.tr/oai/request", "repo_name": "DSpace@Firat University"},
    {"university": "Mersin Üniversitesi", "domain": "mersin.edu.tr", "oai_url": "https://acikerisim.mersin.edu.tr/oai/request", "repo_name": "Mersin Üniversitesi Kurumsal Akademik Arşiv"},
    {"university": "Muğla Sıtkı Koçman Üniversitesi", "domain": "mu.edu.tr", "oai_url": "https://acikerisim.mu.edu.tr/oai/request", "repo_name": "Muğla Sıtkı Koçman University Institutional Repository"},
    {"university": "Afyon Kocatepe Üniversitesi", "domain": "aku.edu.tr", "oai_url": "https://acikerisim.aku.edu.tr/oai/request", "repo_name": "Afyon Kocatape University Institutional Repository"},
    {"university": "Kafkas Üniversitesi", "domain": "kafkas.edu.tr", "oai_url": "https://acikerisim.kafkas.edu.tr/oai/request", "repo_name": "Kafkas University Institutional Repository"},
    {"university": "Giresun Üniversitesi", "domain": "giresun.edu.tr", "oai_url": "https://acikerisim.giresun.edu.tr/oai/request", "repo_name": "Giresun University Institutional Repository"},
    {"university": "Ordu Üniversitesi", "domain": "odu.edu.tr", "oai_url": "https://earsiv.odu.edu.tr/oai/request", "repo_name": "Ordu Üniversitesi Açık Arşiv Sistemi"},
    {"university": "Isparta Uygulamalı Bilimler Üniversitesi", "domain": "isparta.edu.tr", "oai_url": "https://acikerisim.isparta.edu.tr/oai/request", "repo_name": "ISUBU DSpace"},
    {"university": "Uşak Üniversitesi", "domain": "usak.edu.tr", "oai_url": "http://acikerisim.usak.edu.tr/oai/request", "repo_name": "Usak University Institutional Repository"},
    {"university": "Düzce Üniversitesi", "domain": "duzce.edu.tr", "oai_url": "https://acikerisim.duzce.edu.tr/oai/request", "repo_name": "Düzce University Institutional Repository"},
    {"university": "Zonguldak Bülent Ecevit Üniversitesi", "domain": "beun.edu.tr", "oai_url": "https://acikarsiv.beun.edu.tr/oai/request", "repo_name": "BEUN"},
    {"university": "Sabancı Üniversitesi", "domain": "sabanciuniv.edu", "oai_url": "https://research.sabanciuniv.edu/cgi/oai2", "repo_name": "Sabanci University Research Database"},
]


def load_universities(apps, schema_editor):
    University = apps.get_model('oaipmh', 'University')
    for ep in UNIVERSITIES:
        University.objects.update_or_create(
            domain=ep['domain'],
            defaults={
                'name': ep['university'],
                'oai_url': ep['oai_url'],
                'repo_name': ep.get('repo_name', ''),
                'is_active': True,
            }
        )


def unload_universities(apps, schema_editor):
    University = apps.get_model('oaipmh', 'University')
    domains = [ep['domain'] for ep in UNIVERSITIES]
    University.objects.filter(domain__in=domains).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('oaipmh', '0002_add_abstract_query_university_ids'),
    ]

    operations = [
        migrations.RunPython(load_universities, reverse_code=unload_universities),
    ]
