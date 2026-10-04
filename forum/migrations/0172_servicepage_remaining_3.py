# Faz 4 kalan 3 hizmet sayfası: akademik-danismanlik, nitel-analiz, veri-ve-yapay-zeka.
# is_active=False varsayılan — admin elle açar (Nicel Analiz pilotuyla aynı kural). Korumalı:
# slug zaten varsa dokunmaz.
from django.db import migrations

# Nicel Analiz'deki (0171) ile birebir aynı metin — ortak süreç/etik açıklaması, tekrar kasıtlı.
PROCESS_TEXT = (
    'İlan açarsınız, uzmanlar teklif verir, teklifleri karşılaştırıp seçersiniz, iş tamamlanınca '
    'değerlendirirsiniz.'
)
ETHICS_TEXT = (
    'Analizus bir yazım hizmeti değildir; burada bulduğunuz uzmanlar sürecinize rehberlik eder. '
    'Akademik dürüstlük kurallarına uymak sizin sorumluluğunuzdadır.'
)
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

PAGES = [
    {
        'order': 2,
        'slug': 'akademik-danismanlik',
        'title': 'Tez ve Akademik Süreçlerinizde Danışmanlık Desteği',
        'meta_title': 'Tez ve Akademik Danışmanlık Desteği',
        'meta_description': (
            'Tez sürecinizde yöntem seçimi, etik kurul başvurusu ve makale hazırlığında deneyimli '
            'akademisyenlerden danışmanlık desteği alın. Teklif alın, karşılaştırın.'
        ),
        'intro': (
            'Tez önerisinden etik kurul başvurusuna, yöntem seçiminden makale hazırlığına kadar '
            "sürecinizin her adımında deneyimli akademisyenlerden danışmanlık alın. Analizus bir "
            'yazım hizmeti değildir — sürecinize rehberlik eden uzmanlarla sizi buluşturur.'
        ),
        'sections': [
            {'order': 1, 'anchor': 'tez-onerisi', 'title': 'Tez Önerisi',
             'body': 'Araştırma sorusu, kapsam ve yöntem seçiminde tez önerisi aşamasına destek.',
             'job_categories': ['Tez önerisi desteği']},
            {'order': 2, 'anchor': 'tez-danismanligi', 'title': 'Tez Danışmanlığı',
             'body': 'Tez yazım sürecinde yöntem ve yapı konusunda danışmanlık.',
             'job_categories': ['Tez danışmanlığı']},
            {'order': 3, 'anchor': 'etik-kurul', 'title': 'Etik Kurul Başvurusu',
             'body': 'Etik kurul başvuru dosyası hazırlığında yönlendirme.',
             'job_categories': ['Etik kurul desteği']},
            {'order': 4, 'anchor': 'makale-hazirligi', 'title': 'Makale Hazırlığı',
             'body': 'Akademik makale hazırlığında yöntem ve yapı danışmanlığı.',
             'job_categories': ['Makale desteği']},
            {'order': 5, 'anchor': 'metin-editorlugu', 'title': 'Metin Editörlüğü',
             'body': 'Akademik metinlerde dil, anlatım ve format düzenlemesi.',
             'job_categories': ['Metin Editörlüğü']},
            {'order': 6, 'anchor': 'anket-tasarimi', 'title': 'Anket Tasarımı',
             'body': 'Araştırmanıza uygun anket formu oluşturma desteği.',
             'job_categories': ['Anket oluşturma desteği']},
        ],
    },
    {
        'order': 3,
        'slug': 'nitel-analiz',
        'title': 'Nitel Araştırma ve İçerik Analizi Desteği',
        'meta_title': 'Nitel Analiz Desteği: MAXQDA, NVivo, İçerik Analizi',
        'meta_description': (
            "Görüşme, odak grup ve doküman verilerinizin nitel analizini MAXQDA ve NVivo'ya hakim "
            'uzmanlarla yapın. İçerik ve konu analizinde teklif alın.'
        ),
        'intro': (
            'Görüşme kayıtları, odak grup verileri ya da doküman setlerinizin kodlanması ve '
            'analizinde MAXQDA, NVivo deneyimine sahip uzmanlardan destek alın.'
        ),
        'sections': [
            {'order': 1, 'anchor': 'icerik-analizi', 'title': 'İçerik Analizi',
             'body': 'Metin, görüşme ve doküman verilerinde sistematik içerik analizi.',
             'job_categories': ['Nitel veri analizi']},
            {'order': 2, 'anchor': 'konu-analizi', 'title': 'Konu (Tematik) Analizi',
             'body': 'Veride tekrarlayan tema ve örüntülerin belirlenmesi.',
             'job_categories': []},
            {'order': 3, 'anchor': 'maxqda', 'title': 'MAXQDA ile Kodlama',
             'body': 'MAXQDA yazılımıyla nitel veri kodlama ve analiz.',
             'job_categories': ['MAXQDA ile nitel veri analizi']},
            {'order': 4, 'anchor': 'nvivo', 'title': 'NVivo ile Kodlama',
             'body': 'NVivo yazılımıyla nitel veri kodlama ve analiz.',
             'job_categories': ['NVIVO ile nitel veri analizi']},
        ],
    },
    {
        'order': 4,
        'slug': 'veri-ve-yapay-zeka',
        'title': 'Python, Makine Öğrenmesi ve Veri Bilimi Desteği',
        'meta_title': 'Veri Bilimi ve Yapay Zeka Desteği: Python, ML',
        'meta_description': (
            'Python, makine öğrenmesi, NLP ve büyük veri projelerinizde uzman veri bilimcilerle '
            'çalışın. Akademik ve kurumsal projeler için teklif alın.'
        ),
        'intro': (
            'Veri setinizi modellemek, tahmin kurmak ya da NLP/metin analizi yapmak için Python ve '
            'makine öğrenmesi konusunda deneyimli uzmanlarla eşleşin.'
        ),
        'sections': [
            {'order': 1, 'anchor': 'veri-temizleme-buyuk-veri', 'title': 'Veri Temizleme & Büyük Veri',
             'body': 'Büyük veri setlerinin temizlenmesi, birleştirilmesi ve işlenmesi.',
             'job_categories': ['Büyük veri analizi']},
            {'order': 2, 'anchor': 'makine-ogrenmesi', 'title': 'Makine Öğrenmesi',
             'body': 'Sınıflandırma ve tahmin modelleri için makine öğrenmesi destekli analiz.',
             'job_categories': ['Makine öğrenmesi modellemesi']},
            {'order': 3, 'anchor': 'yapay-zeka-modelleme', 'title': 'Yapay Zeka Modelleme',
             'body': 'Araştırma ve uygulama projeleri için yapay zeka modeli geliştirme.',
             'job_categories': ['Yapay zekâ modelleme']},
            {'order': 4, 'anchor': 'nlp', 'title': 'Doğal Dil İşleme (NLP)',
             'body': 'Metin madenciliği ve doğal dil işleme projelerinde destek.',
             'job_categories': ['NLP Modelleme']},
            {'order': 5, 'anchor': 'python-veri-analizi', 'title': 'Python ile Veri Analizi',
             'body': 'Python ile veri işleme, analiz ve otomasyon.',
             'job_categories': ['Python ile veri analizi']},
            {'order': 6, 'anchor': 'veri-gorsellestirme', 'title': 'Veri Görselleştirme',
             'body': 'Power BI ve Tableau ile etkileşimli gösterge panelleri ve raporlama.',
             'job_categories': ['PowerBI ile veri analizi', 'Tableau ile veri analizi']},
        ],
    },
]


def create_pages(apps, schema_editor):
    ServicePage = apps.get_model('forum', 'ServicePage')
    ServicePageSection = apps.get_model('forum', 'ServicePageSection')
    ServicePageFAQ = apps.get_model('forum', 'ServicePageFAQ')
    JobCategory = apps.get_model('forum', 'JobCategory')

    for p in PAGES:
        if ServicePage.objects.filter(slug=p['slug']).exists():
            continue

        page = ServicePage.objects.create(
            slug=p['slug'], title=p['title'], meta_title=p['meta_title'],
            meta_description=p['meta_description'], intro=p['intro'],
            process_text=PROCESS_TEXT, ethics_text=ETHICS_TEXT,
            is_active=False, order=p['order'],
        )
        for s in p['sections']:
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


def delete_pages(apps, schema_editor):
    ServicePage = apps.get_model('forum', 'ServicePage')
    ServicePage.objects.filter(slug__in=[p['slug'] for p in PAGES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0171_servicepage_nicel_analiz_pilot'),
    ]

    operations = [
        migrations.RunPython(create_pages, delete_pages),
    ]
