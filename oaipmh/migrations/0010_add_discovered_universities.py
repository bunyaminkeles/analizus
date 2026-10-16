from django.db import migrations

# 16 Ekim 2026 — hipo-labs/tripbuddy "world_universities_and_domains" listesindeki
# 173 TR domain'i acikerisim/dspace/earsiv/acikarsiv/openaccess alt alan adı +
# /oai/request ve /server/oai/request kalıplarıyla tarayıp (0003'teki 19 hariç)
# gerçekten ListRecords'ta kayıt dönenler. Veri döndürmeyen adaylar (Ankara,
# Başkent, Bingöl, Çankırı Karatekin, Nevşehir Hacı Bektaş Veli, Sağlık
# Bilimleri, Kırklareli, THK, Antalya Bilim) Kafkas ile aynı durumda —
# OAI-PMH yanıt veriyor ama boş/bozuk, bu yüzden eklenmedi.
UNIVERSITIES = [
    {"university": "Anadolu Üniversitesi", "domain": "anadolu.edu.tr", "oai_url": "https://acikerisim.anadolu.edu.tr/server/oai/request", "repo_name": "Anadolu Üniversitesi"},
    {"university": "Ahi Evran Üniversitesi", "domain": "ahievran.edu.tr", "oai_url": "https://openaccess.ahievran.edu.tr/server/oai/request", "repo_name": "Kirsehir Ahi Evran University Institutional Repository"},
    {"university": "Bahçeşehir Üniversitesi", "domain": "bahcesehir.edu.tr", "oai_url": "https://acikerisim.bahcesehir.edu.tr/server/oai/request", "repo_name": "DSpace at Bahcesehir University"},
    {"university": "Balıkesir Üniversitesi", "domain": "balikesir.edu.tr", "oai_url": "https://acikerisim.balikesir.edu.tr/server/oai/request", "repo_name": "Balikesir University Institutional Repository"},
    {"university": "İstanbul Beykent Üniversitesi", "domain": "beykent.edu.tr", "oai_url": "https://earsiv.beykent.edu.tr/server/oai/request", "repo_name": "İstanbul Beykent Univeristy Institutional Repository"},
    {"university": "Çağ Üniversitesi", "domain": "cag.edu.tr", "oai_url": "https://openaccess.cag.edu.tr/server/oai/request", "repo_name": "Çağ University Institutional Repository"},
    {"university": "İstanbul Kültür Üniversitesi", "domain": "iku.edu.tr", "oai_url": "https://openaccess.iku.edu.tr/server/oai/request", "repo_name": "Istanbul Kultur University"},
    {"university": "İzmir Yüksek Teknoloji Enstitüsü", "domain": "iyte.edu.tr", "oai_url": "https://openaccess.iyte.edu.tr/server/oai/request", "repo_name": "İzmir Yüksek Teknoloji Enstitüsü"},
    {"university": "Marmara Üniversitesi", "domain": "marmara.edu.tr", "oai_url": "https://acikerisim.marmara.edu.tr/server/oai/request", "repo_name": "Marmara Üniversitesi DSpace"},
    {"university": "Ondokuz Mayıs Üniversitesi", "domain": "omu.edu.tr", "oai_url": "https://acikerisim.omu.edu.tr/server/oai/request", "repo_name": "Ondokuz Mayis University Institutional Repository"},
    {"university": "Niğde Ömer Halisdemir Üniversitesi", "domain": "ohu.edu.tr", "oai_url": "https://acikerisim.ohu.edu.tr/server/oai/request", "repo_name": "Niğde Ömer Halisdemir University Institutional Repository"},
    {"university": "Süleyman Demirel Üniversitesi", "domain": "sdu.edu.tr", "oai_url": "https://acikerisim.sdu.edu.tr/oai/request", "repo_name": "Süleyman Demirel Üniversitesi Akademik Arşiv Sistemi"},
    {"university": "Yeditepe Üniversitesi", "domain": "yeditepe.edu.tr", "oai_url": "https://openaccess.yeditepe.edu.tr/oai/request", "repo_name": "Yeditepe Üniversitesi Kurumsal Akademik Arşiv"},
    {"university": "Adıyaman Üniversitesi", "domain": "adiyaman.edu.tr", "oai_url": "https://dspace.adiyaman.edu.tr/server/oai/request", "repo_name": "Adiyaman University Institutional Repository"},
    {"university": "Ağrı İbrahim Çeçen Üniversitesi", "domain": "agri.edu.tr", "oai_url": "https://acikerisim.agri.edu.tr/oai/request", "repo_name": "Ağrı İbrahim Çeçen Üniversitesi Kurumsal Akademik Arşiv"},
    {"university": "Ardahan Üniversitesi", "domain": "ardahan.edu.tr", "oai_url": "https://acikerisim.ardahan.edu.tr/oai/request", "repo_name": "Ardahan University Institutional Repository"},
    {"university": "Artvin Çoruh Üniversitesi", "domain": "artvin.edu.tr", "oai_url": "https://openaccess.artvin.edu.tr/server/oai/request", "repo_name": "Artvin Çoruh University Institutional Repository"},
    {"university": "Bandırma Onyedi Eylül Üniversitesi", "domain": "bandirma.edu.tr", "oai_url": "https://acikerisim.bandirma.edu.tr/oai/request", "repo_name": "Bandırma Onyedi Eylül Üniversitesi Kurumsal Akademik Arşiv"},
    {"university": "Bartın Üniversitesi", "domain": "bartin.edu.tr", "oai_url": "https://acikerisim.bartin.edu.tr/server/oai/request", "repo_name": "Bartın University Institutional Repository"},
    {"university": "Bayburt Üniversitesi", "domain": "bayburt.edu.tr", "oai_url": "https://openaccess.bayburt.edu.tr/server/oai/request", "repo_name": "Bayburt University Institutional Repository"},
    {"university": "Bursa Teknik Üniversitesi", "domain": "btu.edu.tr", "oai_url": "https://dspace.btu.edu.tr/server/oai/request", "repo_name": "Bursa Teknik University Institutional Repository"},
    {"university": "Erzurum Teknik Üniversitesi", "domain": "erzurum.edu.tr", "oai_url": "https://acikerisim.erzurum.edu.tr/server/oai/request", "repo_name": "Erzurum Teknik Üniversitesi"},
    {"university": "Gebze Teknik Üniversitesi", "domain": "gtu.edu.tr", "oai_url": "https://acikerisim.gtu.edu.tr/server/oai/request", "repo_name": "Gebze Tecnical University Institutional Repository"},
    {"university": "Gümüşhane Üniversitesi", "domain": "gumushane.edu.tr", "oai_url": "https://acikerisim.gumushane.edu.tr/oai/request", "repo_name": "Gümüşhane University Institutional Repository"},
    {"university": "İskenderun Teknik Üniversitesi", "domain": "iste.edu.tr", "oai_url": "https://openaccess.iste.edu.tr/server/oai/request", "repo_name": "İskenderun Technical University Institutional Repository"},
    {"university": "Kastamonu Üniversitesi", "domain": "kastamonu.edu.tr", "oai_url": "https://acikerisim.kastamonu.edu.tr/server/oai/request", "repo_name": "Kastamonu Üniversitesi DSpace"},
    {"university": "Burdur Mehmet Akif Ersoy Üniversitesi", "domain": "mehmetakif.edu.tr", "oai_url": "https://acikerisim.mehmetakif.edu.tr/server/oai/request", "repo_name": "DSpace at MAKÜ"},
    {"university": "Mimar Sinan Güzel Sanatlar Üniversitesi", "domain": "msgsu.edu.tr", "oai_url": "https://acikerisim.msgsu.edu.tr/oai/request", "repo_name": "Mimar Sinan Fine Arts University Institutional Repository"},
    {"university": "Osmaniye Korkut Ata Üniversitesi", "domain": "osmaniye.edu.tr", "oai_url": "https://openaccess.osmaniye.edu.tr/server/oai/request", "repo_name": "Osmaniye Korkut Ata University Institutional Repository"},
    {"university": "Recep Tayyip Erdoğan Üniversitesi", "domain": "erdogan.edu.tr", "oai_url": "https://acikerisim.erdogan.edu.tr/server/oai/request", "repo_name": "Recep Tayyip Erdoğan University Institutional Repository"},
    {"university": "Sinop Üniversitesi", "domain": "sinop.edu.tr", "oai_url": "https://acikerisim.sinop.edu.tr/server/oai/request", "repo_name": "Sinop University Institutional Repository"},
    {"university": "Şırnak Üniversitesi", "domain": "sirnak.edu.tr", "oai_url": "https://openaccess.sirnak.edu.tr/server/oai/request", "repo_name": "Şırnak University Institutional Repository"},
    {"university": "Acıbadem Mehmet Ali Aydınlar Üniversitesi", "domain": "acibadem.edu.tr", "oai_url": "https://openaccess.acibadem.edu.tr/server/oai/request", "repo_name": "DSpace at Acıbadem"},
    {"university": "Bezmiâlem Vakıf Üniversitesi", "domain": "bezmialem.edu.tr", "oai_url": "https://openaccess.bezmialem.edu.tr/server/oai/request", "repo_name": "Bezmialem Vakıf Üniversitesi"},
    {"university": "Biruni Üniversitesi", "domain": "biruni.edu.tr", "oai_url": "https://acikerisim.biruni.edu.tr/oai/request", "repo_name": "Biruni University Institutional Repository"},
    {"university": "Avrasya Üniversitesi", "domain": "avrasya.edu.tr", "oai_url": "https://acikerisim.avrasya.edu.tr/oai/request", "repo_name": "Avrasya University Open Access"},
    {"university": "Hasan Kalyoncu Üniversitesi", "domain": "hku.edu.tr", "oai_url": "https://openaccess.hku.edu.tr/server/oai/request", "repo_name": "Hasan Kalyoncu University Institutional Repository"},
    {"university": "İstanbul 29 Mayıs Üniversitesi", "domain": "29mayis.edu.tr", "oai_url": "https://openaccess.29mayis.edu.tr/oai/request", "repo_name": "29 Mayis University"},
    {"university": "İstanbul Esenyurt Üniversitesi", "domain": "esenyurt.edu.tr", "oai_url": "https://acikerisim.esenyurt.edu.tr/server/oai/request", "repo_name": "İstanbul Esenyurt University Institutional Repository"},
    {"university": "İstanbul Gelişim Üniversitesi", "domain": "gelisim.edu.tr", "oai_url": "https://acikerisim.gelisim.edu.tr/server/oai/request", "repo_name": "İstanbul Gelişim University Institutional Repository"},
    {"university": "İstanbul Rumeli Üniversitesi", "domain": "rumeli.edu.tr", "oai_url": "https://acikerisim.rumeli.edu.tr/oai/request", "repo_name": "İstanbul Rumeli Üniversitesi"},
    {"university": "KTO Karatay Üniversitesi", "domain": "karatay.edu.tr", "oai_url": "https://acikerisim.karatay.edu.tr/oai/request", "repo_name": "KTO Karatay Üniversitesi Kurumsal Akademik Arşiv"},
    {"university": "Sanko Üniversitesi", "domain": "sanko.edu.tr", "oai_url": "https://acikerisim.sanko.edu.tr/oai/request", "repo_name": "Sanko Üniversitesi Kurumsal Akademik Arsiv"},
    {"university": "Üsküdar Üniversitesi", "domain": "uskudar.edu.tr", "oai_url": "https://openaccess.uskudar.edu.tr/oai/request", "repo_name": "Üsküdar Üniversitesi DSpace"},
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
        ('oaipmh', '0009_university_flagged_for_review_and_more'),
    ]

    operations = [
        migrations.RunPython(load_universities, reverse_code=unload_universities),
    ]
