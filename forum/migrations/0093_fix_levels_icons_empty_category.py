from django.db import migrations


def fix(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    BlogCategory = apps.get_model('forum', 'BlogCategory')

    # 1. Boş sluglu bozuk kategoriyi temizle (eski name= hatası — 0080 migrasyonu)
    empty_cats = BlogCategory.objects.filter(slug='')
    if empty_cats.exists():
        spss_cat, _ = BlogCategory.objects.get_or_create(
            slug='spss-rehberleri',
            defaults={'name': 'SPSS Rehberleri', 'icon': 'bi-bar-chart-line', 'color': '#3b82f6'},
        )
        BlogPost.objects.filter(category__slug='').update(category=spss_cat)
        empty_cats.delete()

    # 2. Kategori ikonlarını düzelt (sadece hâlâ bi-folder defaultu olanlar)
    icon_map = {
        'ekonometri-veri-politikasi':     ('bi-graph-up-arrow',  '#0ea5e9'),
        'saglik-verisi-bilim-politikasi': ('bi-heart-pulse',     '#ec4899'),
        'saglik-istatistigi':             ('bi-activity',        '#ec4899'),
        'veri-guvenligi-arastirma-etigi': ('bi-shield-lock',    '#f59e0b'),
        'veri-guvenligi-etik':            ('bi-shield-lock',    '#f59e0b'),
        'spss-rehberleri':                ('bi-bar-chart-line',  '#3b82f6'),
    }
    for slug, (icon, color) in icon_map.items():
        BlogCategory.objects.filter(slug=slug, icon='bi-folder').update(icon=icon, color=color)

    # 3. Seviye atamaları — slug bazlı (tüm ortamlarda çalışır)
    BlogPost.objects.filter(slug__in=[
        'cronbach-alpha-degeri-tezde-nasil-raporlanir',
        'cronbach-alpha-degeri-kac-olmali-tezde-nasil-yorumlanir-raporlanir',
        'normallik-testi-sonuclari-nasil-yorumlanir-shapiro-wilk-kolmogorov-smirnov',
        'spsste-t-testi-adim-adim-bagimsiz-ve-bagimli-orneklem-karsilastirmasi',
        'acimlayici-ve-dogrulayici-faktor-analizi-afa-dfa-arasindaki-farklar',
        'tezde-yapilan-en-sik-10-istatistik-hatasi-ve-nasil-onlenir',
    ]).update(level='beginner')

    BlogPost.objects.filter(slug__in=[
        'chatgpty-e-tezini-yazdirmak-bilim-midir-yoksa-akademinin-olum-sertifikasi-mi',
        'p-degeri-krizinin-100-yilinda-istatistiksel-anlamlilik-bilimi-yanlis-mi-yonlendirdi',
        'yayinla-ya-da-yok-ol-caginda-akademisyenin-sessiz-intihari-predatory-dergiler',
        'turkiyenin-akademik-uretimi-nereye-gidiyor-openalex-ve-tr-dizin-verileriyle',
        'veri-sahteliginden-veri-seffafligina-open-science-hareketi-ve-turkiyede-acik-veri',
        'tez-verilerini-google-driveda-tutmak-suc-mu-kvkk-gdpr',
        'saglikta-veri-krizi-turkiyede-klinik-arastirmalarin-verisi-neden-hep-kayip',
        'survival-analizi-101-kaplan-meier-cox-regresyon-ve-tedavi-etkili-mi',
    ]).update(level='intermediate')

    BlogPost.objects.filter(slug__in=[
        'anonimlestirme-yanilgisi-isimsiz-veri-setlerinden-kimlik-yeniden-nasil-insa-ediliyor',
        'enflasyon-verilerine-guveniyor-muyuz-tuik-enag-resmi-veri-tartismasi',
    ]).update(level='advanced')

    # 4. Sunucuda konsolide edilmiş kategorilerdeki yazılar için seviye ata
    #    (slug eşleşmesi olmayan yazıları, kategori bazlı yakalar)
    for cat_slug, level in [
        ('akademi-ve-yapay-zeka', 'intermediate'),
        ('saglik-ve-yapay-zeka',  'intermediate'),
        ('istatistik',            'advanced'),    # SEM, Güç Analizi, Regresyon vs AI
    ]:
        BlogPost.objects.filter(category__slug=cat_slug, level='').update(level=level)


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0092_blog_enflasyon_verilerine_guveniyor_muyuz'),
    ]

    operations = [
        migrations.RunPython(fix, migrations.RunPython.noop),
    ]
