# Faz 4 pilot içeriği: /hizmetler/nicel-analiz/ — is_active=False, SiteSettings.feature_hizmet_sayfalari=False
# varsayılan olarak kalır; sayfa yalnız admin ikisini de elle açınca görünür. Korumalı: slug zaten varsa dokunmaz.
from django.db import migrations


SECTIONS = [
    {
        'order': 1, 'anchor': 'on-analizler', 'title': 'Ön Analizler',
        'body': 'Veri temizleme, eksik veri ve betimsel istatistiklerle analiz sürecine sağlam bir başlangıç.',
        'job_categories': [],
    },
    {
        'order': 2, 'anchor': 'gecerlik-guvenirlik', 'title': 'Geçerlik & Güvenirlik',
        'body': 'Ölçek geliştirme ve uyarlama çalışmalarında geçerlik-güvenirlik analizleri.',
        'job_categories': ['Geçerlik & güvenirlik analizleri'],
    },
    {
        'order': 3, 'anchor': 'iliski-korelasyon', 'title': 'İlişki & Korelasyon',
        'body': 'Değişkenler arası ilişkilerin korelasyon analizleriyle incelenmesi.',
        'job_categories': ['SPSS ile veri analizi', 'R ile veri analizi'],
    },
    {
        'order': 4, 'anchor': 'fark-testleri', 'title': 'Fark Testleri',
        'body': 'Gruplar arası farkların t-testi, ANOVA ve non-parametrik testlerle değerlendirilmesi.',
        'job_categories': ['SPSS ile veri analizi'],
    },
    {
        'order': 5, 'anchor': 'regresyon-sem', 'title': 'Regresyon & Yapısal Eşitlik Modelleme',
        'body': 'Regresyon modelleri ve SmartPLS/AMOS ile yapısal eşitlik modellemesi (SEM).',
        'job_categories': ['SmartPLS analizleri', 'AMOS (Path analizi)'],
    },
    {
        'order': 6, 'anchor': 'zaman-serisi-ekonometri', 'title': 'Zaman Serisi & Ekonometri',
        'body': 'EViews ile ekonometrik modelleme ve zaman serisi analizleri.',
        'job_categories': ['EViews analizleri', 'Zaman serisi analizleri'],
    },
    {
        'order': 7, 'anchor': 'makine-ogrenmesi', 'title': 'Makine Öğrenmesi',
        'body': 'Sınıflandırma ve tahmin modelleri için makine öğrenmesi destekli analiz.',
        'job_categories': ['Makine öğrenmesi modellemesi'],
    },
]

FAQS = [
    {
        'order': 1,
        'question': 'Verilerimi nasıl paylaşacağım?',
        'answer': 'İlan açtıktan sonra teklif veren uzmanla platform mesajlaşması üzerinden iletişime geçer, verinizi güvenle paylaşırsınız.',
    },
    {
        'order': 2,
        'question': 'Analiz sonucunu nasıl teslim alırım?',
        'answer': 'Uzmanla aranızdaki anlaşmaya göre rapor, çıktı dosyaları ve yorumlar teslim edilir.',
    },
]


def create_nicel_analiz(apps, schema_editor):
    ServicePage = apps.get_model('forum', 'ServicePage')
    ServicePageSection = apps.get_model('forum', 'ServicePageSection')
    ServicePageFAQ = apps.get_model('forum', 'ServicePageFAQ')
    JobCategory = apps.get_model('forum', 'JobCategory')

    if ServicePage.objects.filter(slug='nicel-analiz').exists():
        return

    page = ServicePage.objects.create(
        slug='nicel-analiz',
        title='İstatistiksel Analiz ve Nicel Veri Analizi Desteği',
        meta_title='SPSS, R, EViews ile Nicel Analiz Desteği',
        meta_description=(
            "Tezinizin veya araştırmanızın istatistiksel analizini SPSS, R, EViews, SmartPLS'e hakim uzman "
            "analistlere bırakın. Teklif alın, karşılaştırın, siz seçin."
        ),
        intro=(
            'SPSS, R, EViews, SmartPLS ve ileri istatistiksel yöntemlerle — verinizi gönderin, alanında uzman '
            'analistler sizin adınıza analiz edip raporlasın. Analizus\'ta uzmanlar teklif verir, siz '
            'karşılaştırıp seçersiniz.'
        ),
        process_text=(
            'İlan açarsınız, uzmanlar teklif verir, teklifleri karşılaştırıp seçersiniz, iş tamamlanınca '
            'değerlendirirsiniz.'
        ),
        ethics_text=(
            'Analizus bir yazım hizmeti değildir; burada bulduğunuz uzmanlar verinizi analiz eder ve yöntem '
            'konusunda sizi yönlendirir. Akademik dürüstlük kurallarına uymak sizin sorumluluğunuzdadır.'
        ),
        is_active=False,
        order=1,
    )

    for s in SECTIONS:
        section = ServicePageSection.objects.create(
            service_page=page, order=s['order'], anchor=s['anchor'], title=s['title'], body=s['body'],
        )
        if s['job_categories']:
            cats = JobCategory.objects.filter(title__in=s['job_categories'], is_active=True)
            section.related_job_categories.set(cats)

    for f in FAQS:
        ServicePageFAQ.objects.create(
            service_page=page, order=f['order'], question=f['question'], answer=f['answer'],
        )


def delete_nicel_analiz(apps, schema_editor):
    ServicePage = apps.get_model('forum', 'ServicePage')
    ServicePage.objects.filter(slug='nicel-analiz').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0170_servicepage_sitesettings_feature_hizmet_sayfalari_and_more'),
    ]

    operations = [
        migrations.RunPython(create_nicel_analiz, delete_nicel_analiz),
    ]
