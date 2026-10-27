from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_GET
from django_ratelimit.decorators import ratelimit
from django.conf import settings as django_settings
from functools import wraps
from django.utils.translation import gettext, gettext_lazy

from .models import IstatistikJob
from .seo_content import SEO_CONTENT


def feature_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from forum.models import SiteSettings
        site = SiteSettings.load()
        if not getattr(site, 'feature_istatistik', True):
            raise Http404
        return view_func(request, *args, **kwargs)
    return wrapper


TOOL_CATEGORIES = [
    (gettext_lazy('Ön Analizler'), [
        ('betimsel',  gettext_lazy('Betimleyici İstatistik'),       'bi-clipboard2-data',    'success',  'betimsel'),
        ('normallik', gettext_lazy('Normallik Testi'),               'bi-activity',           'warning',  'normallik'),
        ('orneklem',  gettext_lazy('Örneklem Hesaplayıcı'),          'bi-calculator-fill',    'info',     'orneklem'),
    ]),
    (gettext_lazy('Geçerlik & Güvenirlik'), [
        ('cronbach',  gettext_lazy('Cronbach Alpha'),                'bi-shield-check',       'primary',  'cronbach'),
        ('afa',       gettext_lazy('Açıklayıcı Faktör Analizi'),     'bi-diagram-3',          'info',     'afa'),
    ]),
    (gettext_lazy('İlişki Analizleri'), [
        ('korelasyon', gettext_lazy('Korelasyon Matrisi'),           'bi-grid-3x3',           'info',     'korelasyon'),
        ('ki_kare',   gettext_lazy('Ki-Kare Testi'),                 'bi-table',              'warning',  'ki-kare'),
    ]),
    (gettext_lazy('Fark Analizleri'), [
        ('ttesti',         gettext_lazy('t-Testi'),                  'bi-distribute-horizontal', 'primary', 'ttesti'),
        ('anova',          gettext_lazy('Tek Yönlü ANOVA'),           'bi-bar-chart-steps',   'danger',   'anova'),
        ('mann_whitney',   gettext_lazy('Mann-Whitney U'),            'bi-arrow-left-right',  'warning',  'mann-whitney'),
        ('kruskal_wallis', gettext_lazy('Kruskal-Wallis H'),          'bi-funnel',            'teal',     'kruskal-wallis'),
        ('wilcoxon',       gettext_lazy('Wilcoxon İşaret Testi'),     'bi-arrows-collapse',   'info',     'wilcoxon'),
        ('friedman',       gettext_lazy('Friedman Testi'),            'bi-bar-chart-steps',   'success',  'friedman'),
        ('tekrarli_anova', gettext_lazy('Tekrarlayan Ölçümler ANOVA'),'bi-arrow-repeat',      'primary',  'tekrarli-anova'),
        ('manova',         gettext_lazy('Çok Değişkenli Varyans Analizi (MANOVA)'), 'bi-layers', 'purple', 'manova'),
    ]),
    (gettext_lazy('Regresyon Analizleri'), [
        ('lineer_regresyon',  gettext_lazy('Çoklu Doğrusal Regresyon'), 'bi-graph-up-arrow',  'primary',  'lineer-regresyon'),
        ('lojistik_regresyon',gettext_lazy('Lojistik Regresyon'),        'bi-bezier2',         'success',  'lojistik-regresyon'),
        ('mediation',         gettext_lazy('Aracılık Analizi (Mediation)'), 'bi-diagram-3-fill', 'purple', 'mediation'),
        ('moderation',        gettext_lazy('Düzenleyici Değişken Analizi (Moderation)'), 'bi-sliders', 'purple', 'moderation'),
        ('sagkalim',          gettext_lazy('Sağkalım Analizi (Kaplan-Meier / Cox)'), 'bi-heart-pulse', 'danger', 'sagkalim'),
        ('roc',               gettext_lazy('ROC Eğrisi / Tanısal Tarama'), 'bi-bullseye', 'info', 'roc'),
    ]),
    (gettext_lazy('Makine Öğrenmesi'), [
        ('karar_agaci', gettext_lazy('Karar Ağacı'), 'bi-diagram-2', 'purple', 'karar-agaci'),
        ('svm', gettext_lazy('Destek Vektör Makinesi'), 'bi-cpu', 'teal', 'svm'),
        ('kumeleme', gettext_lazy('Kümeleme Analizi (K-means / Hiyerarşik)'), 'bi-bounding-box-circles', 'info', 'kumeleme'),
    ]),
]

# Faz 5 (SEO iç linkleme): her kategori grubu ilgili /hizmetler/<slug>/ sayfasına eşlenir —
# nitel-analiz/akademik-danismanlik'e eşleşen araç yok (Faz 3'teki blog eşlemesiyle aynı durum).
_TOOL_GROUP_SERVICE_SLUGS = [
    'nicel-analiz', 'nicel-analiz', 'nicel-analiz', 'nicel-analiz', 'nicel-analiz', 'veri-ve-yapay-zeka',
]
_SERVICE_PAGE_TITLES = {
    'nicel-analiz': gettext_lazy('Nicel Analiz'),
    'veri-ve-yapay-zeka': gettext_lazy('Veri Bilimi ve Yapay Zeka'),
}
for _slug, (_group_label, _tools) in zip(_TOOL_GROUP_SERVICE_SLUGS, TOOL_CATEGORIES):
    for _tool in _tools:
        SEO_CONTENT.setdefault(_tool[0], {})['related_service'] = {
            'slug': _slug,
            'title': _SERVICE_PAGE_TITLES[_slug],
        }


def _console_ctx(active_tool, request=None):
    ctx = {
        'active_tool': active_tool,
        'tool_categories': TOOL_CATEGORIES,
        'max_upload_mb': django_settings.MAX_UPLOAD_SIZE // (1024 * 1024),
        'seo_guide': SEO_CONTENT.get(active_tool),
    }
    if request:
        ctx['session_dataset_name'] = request.session.get('_ax_dataset_name', '')
    return ctx


PROMO_BASE = {
    'promo_steps': [
        gettext_lazy('CSV veya Excel dosyanızı yükleyin.'),
        gettext_lazy('Analiz otomatik olarak saniyeler içinde tamamlanır.'),
        gettext_lazy('Sonuçları ekranda görün ve PDF olarak indirin.'),
    ],
}


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def cronbach_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('cronbach'),
            'promo_title': gettext('Güvenilirlik Analizi — Cronbach Alpha'),
            'promo_icon': 'bi-shield-check',
            'promo_color': 'primary',
            'promo_egitim_konu': 'olcek-gelistirme',
            'promo_description': gettext('Anket ölçeğinizin iç tutarlılığını ölçün. CSV/Excel dosyanızı yükleyin; Cronbach Alpha katsayısı, madde-toplam korelasyonları ve madde çıkarma tablosu PDF olarak hazır.'),
            'promo_features': [
                {'icon': 'bi-upload', 'title': gettext('Kolay Yükleme'), 'desc': gettext('CSV veya Excel dosyanızı sürükle-bırak ile yükleyin. Her sütun bir madde, her satır bir katılımcı olmalıdır.')},
                {'icon': 'bi-calculator', 'title': gettext('Cronbach Alpha'), 'desc': gettext('α katsayısı ve "Kabul Edilemez / Düşük / Kabul Edilebilir / İyi / Mükemmel" yorumu otomatik hesaplanır.')},
                {'icon': 'bi-table', 'title': gettext('Madde İstatistikleri'), 'desc': gettext('Her madde için ortalama, standart sapma, düzeltilmiş madde-toplam korelasyonu ve madde silinince alpha tablosu.')},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': gettext('PDF Rapor'), 'desc': gettext('Tüm sonuçlar düzenli tablolar halinde PDF olarak indirilebilir.')},
            ],
        })

    if request.method == 'POST':
        return _handle_group_tool_post(request, 'cronbach')

    active_job = _get_active_job(request.user, 'cronbach')
    return render(request, 'istatistik/cronbach.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': gettext('Güvenilirlik Analizi — Cronbach Alpha'),
        'tool_icon': 'bi-shield-check',
        'tool_color': 'primary',
        'tool_description': gettext('Anket ölçeğinizin iç tutarlılığını ölçün. Her sütun bir madde, her satır bir katılımcı olmalıdır.'),
        'tool_hints': [
            gettext('Her sütun bir ölçek maddesi olmalıdır (örn. S1, S2, S3…).'),
            gettext('Her satır bir katılımcıyı temsil etmelidir.'),
            gettext('Başlık satırı otomatik algılanır.'),
            gettext('Boş hücreler (NA) satırdan çıkarılır.'),
        ],
        **_console_ctx('cronbach', request),
    })


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def normallik_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('normallik'),
            'promo_title': gettext('Normallik Testi'),
            'promo_icon': 'bi-bell-curve',
            'promo_color': 'warning',
            'promo_description': gettext('"Parametrik mi, non-parametrik mi?" sorusunu yanıtlayın. Shapiro-Wilk testi, çarpıklık/basıklık değerleri ve Q-Q plot içeren PDF raporu saniyeler içinde alın.'),
            'promo_features': [
                {'icon': 'bi-graph-up', 'title': gettext('Shapiro-Wilk Testi'), 'desc': gettext('Her değişken için W istatistiği ve p-değeri hesaplanır. p < 0.05 normal dağılımdan sapma anlamına gelir.')},
                {'icon': 'bi-bar-chart-steps', 'title': gettext('Çarpıklık & Basıklık'), 'desc': gettext('Skewness ve kurtosis değerleri ±1.96 ve ±2.58 kritik sınırlarıyla yorumlanır.')},
                {'icon': 'bi-scatter-chart', 'color': 'info', 'title': gettext('Q-Q Plot'), 'desc': gettext('Her değişken için görsel normallik grafiği PDF\'e eklenir.')},
                {'icon': 'bi-check-circle-fill', 'color': 'success', 'title': gettext('Otomatik Öneri'), 'desc': gettext('"Parametrik test kullanılabilir" veya "Non-parametrik test önerilir" kararı otomatik verilir.')},
            ],
        })

    if request.method == 'POST':
        return _handle_group_tool_post(request, 'normallik')

    active_job = _get_active_job(request.user, 'normallik')
    return render(request, 'istatistik/normallik.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': gettext('Normallik Testi'),
        'tool_icon': 'bi-activity',
        'tool_color': 'warning',
        'tool_description': gettext('Shapiro-Wilk testi, çarpıklık/basıklık ve Q-Q plot ile değişkenlerinizin normal dağılıma uygunluğunu test edin.'),
        'tool_hints': [
            gettext('Her sütun ayrı bir değişken olarak analiz edilir.'),
            gettext('Shapiro-Wilk testi N ≤ 5000 için; üzerinde D\'Agostino-Pearson kullanılır.'),
            gettext('p ≥ 0.05 → normal dağılım varsayımı reddedilemez.'),
            gettext('Hem istatistiksel hem görsel (Q-Q plot) sonuçlar PDF\'e eklenir.'),
        ],
        **_console_ctx('normallik', request),
    })


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def betimsel_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('betimsel'),
            'promo_title': gettext('Betimleyici İstatistik Raporu'),
            'promo_icon': 'bi-clipboard2-data',
            'promo_color': 'success',
            'promo_description': gettext('Verinizi yükleyin; frekans tabloları, ortalama, standart sapma ve grafikler otomatik oluşsun. Raporunuzun bulgular bölümünün ilk sayfası hazır.'),
            'promo_features': [
                {'icon': 'bi-list-ol', 'title': gettext('Frekans Tabloları'), 'desc': gettext('Kategorik değişkenler için frekans ve yüzde dağılım tabloları otomatik oluşturulur.')},
                {'icon': 'bi-calculator-fill', 'color': 'primary', 'title': gettext('Merkezi Eğilim'), 'desc': gettext('Sürekli değişkenler için n, ortalama, standart sapma, min, max, medyan, Q1-Q3 hesaplanır.')},
                {'icon': 'bi-bar-chart-fill', 'title': gettext('Otomatik Grafikler'), 'desc': gettext('Kategorik değişkenler için çubuk grafik, sürekli değişkenler için histogram PDF\'e eklenir.')},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': gettext('Hazır PDF Rapor'), 'desc': gettext('Tüm tablolar ve grafikler düzenli formatta PDF olarak indirilir.')},
            ],
        })

    if request.method == 'POST':
        return _handle_group_tool_post(request, 'betimsel')

    active_job = _get_active_job(request.user, 'betimsel')
    return render(request, 'istatistik/betimsel.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': gettext('Betimleyici İstatistik Raporu'),
        'tool_icon': 'bi-clipboard2-data',
        'tool_color': 'success',
        'tool_description': gettext('Verinizdeki her sütun için frekans tabloları, merkezi eğilim ölçüleri ve grafikler otomatik oluşturulur.'),
        'tool_hints': [
            gettext('Kategorik değişkenler (≤10 farklı değer veya metin) → frekans tablosu + çubuk grafik.'),
            gettext('Sürekli sayısal değişkenler → ortalama, SS, medyan, Q1-Q3 + histogram.'),
            gettext('Başlık satırı otomatik algılanır.'),
            gettext('Boş hücreler (NA) değişken bazında çıkarılır.'),
        ],
        **_console_ctx('betimsel', request),
    })


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def korelasyon_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('korelasyon'),
            'promo_title': gettext('Korelasyon Matrisi'),
            'promo_icon': 'bi-grid-3x3',
            'promo_color': 'info',
            'promo_description': gettext('Değişkenleriniz arasındaki ilişkileri tek bakışta görün. Pearson, Spearman veya Kendall yöntemiyle p-değerleri ve ısı haritası içeren PDF raporu saniyeler içinde alın.'),
            'promo_features': [
                {'icon': 'bi-table', 'title': gettext('Korelasyon Tablosu'), 'desc': gettext('Tüm değişken çiftleri için r katsayısı ve p-değeri hesaplanır. p < 0.05 anlamlı ilişkiyi gösterir.')},
                {'icon': 'bi-grid-fill', 'color': 'info', 'title': gettext('Isı Haritası'), 'desc': gettext('Korelasyon katsayıları renk skalasıyla görselleştirilir. Güçlü ilişkiler anında fark edilir.')},
                {'icon': 'bi-sliders', 'title': gettext('Üç Yöntem'), 'desc': gettext('Pearson (parametrik), Spearman (non-parametrik sıralı) veya Kendall (küçük örneklem) yöntemlerinden seçin.')},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': gettext('PDF Rapor'), 'desc': gettext('Tablo ve ısı haritası düzenli formatta PDF olarak indirilir.')},
            ],
        })

    if request.method == 'POST':
        return _handle_group_tool_post(request, 'korelasyon')

    active_job = _get_active_job(request.user, 'korelasyon')
    return render(request, 'istatistik/korelasyon.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': gettext('Korelasyon Matrisi'),
        'tool_icon': 'bi-grid-3x3',
        'tool_color': 'info',
        'tool_description': gettext('Değişkenleriniz arasındaki ilişkileri Pearson, Spearman veya Kendall yöntemiyle hesaplayın. Her sütun bir değişken, her satır bir gözlem olmalıdır.'),
        'tool_hints': [
            gettext('Her sütun bir değişkeni temsil etmelidir.'),
            gettext('Pearson: normal dağılımlı sürekli veriler için.'),
            gettext('Spearman: sıralı veriler veya normallik varsayımı sağlanmıyorsa.'),
            gettext('Kendall: küçük örneklem veya çok sayıda bağlı sıra olduğunda.'),
        ],
        **_console_ctx('korelasyon', request),
    })


@feature_required
def orneklem_landing(request):
    if request.method == 'POST':
        return _handle_orneklem_calc(request)
    return render(request, 'istatistik/orneklem.html', {
        'tool_title': gettext('Örneklem Büyüklüğü Hesaplayıcı'),
        **_console_ctx('orneklem', request),
    })


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def ttesti_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('ttesti'),
            'promo_title': gettext('t-Testi'),
            'promo_icon': 'bi-distribute-horizontal',
            'promo_color': 'purple',
            'promo_egitim_konu': 'spss-uygulamali',
            'promo_description': gettext('İki grup arasındaki ortalama farkını test edin. Bağımsız veya bağımlı örneklem t-testi, Cohen\'s d etki büyüklüğü ve %95 güven aralığı ile PDF raporu alın.'),
            'promo_features': [
                {'icon': 'bi-people-fill', 'title': gettext('Bağımsız Örneklem'), 'desc': gettext('Farklı iki grubun ortalamalarını karşılaştırın. Levene testi ile varyans homojenliği otomatik kontrol edilir.')},
                {'icon': 'bi-arrow-left-right', 'title': gettext('Bağımlı Örneklem'), 'desc': gettext('Aynı gruba ait iki ölçüm arasındaki farkı test edin (öntest-sontest, eşleştirilmiş).')},
                {'icon': 'bi-rulers', 'title': gettext('Etki Büyüklüğü'), 'desc': gettext('Cohen\'s d katsayısı ve %95 güven aralığı otomatik hesaplanır.')},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': gettext('PDF Rapor'), 'desc': gettext('Grup istatistikleri ve test sonuçları düzenli tablolar halinde PDF\'e aktarılır.')},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'ttesti')
    return render(request, 'istatistik/ttesti.html', {
        'active_job_id': str(_get_active_job(request.user, 'ttesti').id) if _get_active_job(request.user, 'ttesti') else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': gettext('t-Testi'),
        'tool_icon': 'bi-distribute-horizontal',
        'tool_color': 'purple',
        **_console_ctx('ttesti', request),
    })


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def anova_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('anova'),
            'promo_title': gettext('Tek Yönlü ANOVA'),
            'promo_icon': 'bi-bar-chart-steps',
            'promo_color': 'danger',
            'promo_description': gettext('Üç veya daha fazla grubun ortalamalarını karşılaştırın. Tukey/Bonferroni post-hoc testleri ve η² etki büyüklüğü ile tam bir ANOVA raporu alın.'),
            'promo_features': [
                {'icon': 'bi-bar-chart-fill', 'title': gettext('Tek Yönlü ANOVA'), 'desc': gettext('F istatistiği, serbestlik dereceleri ve p-değeri otomatik hesaplanır.')},
                {'icon': 'bi-search', 'color': 'warning', 'title': gettext('Post-Hoc Testler'), 'desc': gettext('Hangi gruplar arasında fark var? Tukey veya Bonferroni post-hoc testi ile belirleyin.')},
                {'icon': 'bi-rulers', 'title': gettext('Etki Büyüklüğü'), 'desc': gettext('Eta-kare (η²) ile etki büyüklüğü raporlanır.')},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': gettext('PDF Rapor'), 'desc': gettext('Grup istatistikleri, ANOVA tablosu ve post-hoc sonuçları PDF\'e aktarılır.')},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'anova')
    return render(request, 'istatistik/anova.html', {
        'active_job_id': str(_get_active_job(request.user, 'anova').id) if _get_active_job(request.user, 'anova') else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': gettext('Tek Yönlü ANOVA'),
        'tool_icon': 'bi-bar-chart-steps',
        'tool_color': 'danger',
        **_console_ctx('anova', request),
    })


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def manova_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('manova'),
            'promo_title': gettext('Çok Değişkenli Varyans Analizi (MANOVA)'),
            'promo_icon': 'bi-layers',
            'promo_color': 'purple',
            'promo_description': gettext('Bir grup değişkeninin 2 veya daha fazla bağımlı değişken üzerindeki ortak etkisini tek seferde test edin. Wilks\' Lambda dahil tüm çok değişkenli testler, takip ANOVA\'ları ve Box\'s M testi ile tam rapor.'),
            'promo_features': [
                {'icon': 'bi-layers', 'title': gettext('Çok Değişkenli Testler'), 'desc': gettext('Wilks\' Lambda, Pillai\'s Trace, Hotelling-Lawley Trace ve Roy\'s Largest Root — SPSS ile aynı tablo.')},
                {'icon': 'bi-diagram-3', 'color': 'warning', 'title': gettext('Takip ANOVA\'ları'), 'desc': gettext('MANOVA anlamlıysa her bağımlı değişken için Bonferroni düzeltmeli takip ANOVA\'ları otomatik hesaplanır.')},
                {'icon': 'bi-grid-3x3', 'color': 'success', 'title': gettext('Box\'s M Testi'), 'desc': gettext('Kovaryans matrisi homojenliği varsayımı test edilir.')},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': gettext('PDF Rapor'), 'desc': gettext('Profil grafiği, çok değişkenli test tablosu ve APA formatında raporlama cümlesi PDF olarak indirilir.')},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'manova')
    active_job = _get_active_job(request.user, 'manova')
    return render(request, 'istatistik/manova.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': gettext('Çok Değişkenli Varyans Analizi (MANOVA)'),
        'tool_icon': 'bi-layers',
        'tool_color': 'purple',
        **_console_ctx('manova', request),
    })


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def sagkalim_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('sagkalim'),
            'promo_title': gettext('Sağkalım Analizi (Kaplan-Meier / Cox Regresyon)'),
            'promo_icon': 'bi-heart-pulse',
            'promo_color': 'danger',
            'promo_description': gettext('Süre/olay verinizi Kaplan-Meier ile tanımlayıcı olarak veya Cox Regresyon ile çoklu değişkenli olarak analiz edin. Sağkalım eğrisi, log-rank testi, hazard oranları ve oransal tehlikeler varsayım testi ile tam rapor.'),
            'promo_features': [
                {'icon': 'bi-graph-down', 'title': gettext('Kaplan-Meier Eğrisi'), 'desc': gettext('Medyan sağkalım süresi, opsiyonel grup karşılaştırması ve log-rank testi.')},
                {'icon': 'bi-bezier2', 'color': 'warning', 'title': gettext('Cox Regresyon'), 'desc': gettext('Çoklu kovaryat ile hazard oranları (HR), %95 güven aralığı ve concordance index.')},
                {'icon': 'bi-shield-check', 'color': 'success', 'title': gettext('Varsayım Testi'), 'desc': gettext('Oransal tehlikeler (proportional hazards) varsayımı Schoenfeld rezidüleri ile test edilir.')},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': gettext('PDF Rapor'), 'desc': gettext('Sağkalım eğrisi grafiği ve APA formatında raporlama cümlesi PDF olarak indirilir.')},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'sagkalim')
    active_job = _get_active_job(request.user, 'sagkalim')
    return render(request, 'istatistik/sagkalim.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': gettext('Sağkalım Analizi (Kaplan-Meier / Cox Regresyon)'),
        'tool_icon': 'bi-heart-pulse',
        'tool_color': 'danger',
        **_console_ctx('sagkalim', request),
    })


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def roc_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('roc'),
            'promo_title': gettext('ROC Eğrisi / Tanısal Tarama Analizi'),
            'promo_icon': 'bi-bullseye',
            'promo_color': 'info',
            'promo_description': gettext('Bir tanı testinin/biyobelirtecin ayırt edicilik gücünü AUC, optimal kesim noktası ve duyarlılık/özgüllük tablosu ile ölçün. İki testi DeLong testiyle karşılaştırma seçeneği dahil.'),
            'promo_features': [
                {'icon': 'bi-graph-up', 'title': gettext('ROC Eğrisi & AUC'), 'desc': gettext('AUC değeri Hanley-McNeil %95 güven aralığı ile raporlanır.')},
                {'icon': 'bi-bullseye', 'color': 'warning', 'title': gettext('Optimal Kesim Noktası'), 'desc': gettext('Youden J indeksine göre en iyi kesim noktası ve o noktadaki duyarlılık/özgüllük/PPV/NPV/LR+/LR- tablosu.')},
                {'icon': 'bi-arrow-left-right', 'color': 'success', 'title': gettext('İki Test Karşılaştırma'), 'desc': gettext('Aynı örneklemdeki iki testin AUC farkı DeLong testiyle sınanır.')},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': gettext('PDF Rapor'), 'desc': gettext('ROC eğrisi grafiği ve APA formatında raporlama cümlesi PDF olarak indirilir.')},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'roc')
    active_job = _get_active_job(request.user, 'roc')
    return render(request, 'istatistik/roc.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': gettext('ROC Eğrisi / Tanısal Tarama Analizi'),
        'tool_icon': 'bi-bullseye',
        'tool_color': 'info',
        **_console_ctx('roc', request),
    })


def _handle_group_tool_post(request, tool):
    """t-testi ve ANOVA için iki adımlı POST yönetimi.
    Adım 1: 'step=preview' — dosyayı parse et, sütun isimlerini döndür.
    Adım 2: 'step=run'     — sütun seçimiyle job oluştur ve kuyruğa ekle.
    """
    step = request.POST.get('step', 'preview')
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if step == 'preview':
        from .services.job_runner import _parse_file, store_file_content, save_session_dataset, get_session_dataset
        import uuid

        use_session = request.POST.get('use_session') == 'true'
        file = request.FILES.get('file')

        if use_session:
            session_key = request.session.session_key
            stored = get_session_dataset(session_key) if session_key else None
            if not stored:
                return JsonResponse({'error': gettext('Oturum verisi bulunamadı. Lütfen dosyayı tekrar yükleyin.')}, status=400)
            content, original_filename = stored
        elif file:
            if not file.name.lower().endswith(('.csv', '.xlsx', '.xls')):
                return JsonResponse({'error': gettext('CSV veya Excel dosyası yükleyin.')}, status=400)
            if file.size > django_settings.MAX_UPLOAD_SIZE:
                return JsonResponse({'error': gettext('Dosya boyutu 5 MB sınırını aşıyor.')}, status=400)
            content = file.read()
            original_filename = file.name
        else:
            return JsonResponse({'error': gettext('Dosya seçilmedi.')}, status=400)

        try:
            df = _parse_file(content, original_filename)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)

        # Dosyayı session'a kaydet (her yüklemede güncelle)
        if file and not use_session:
            if not request.session.session_key:
                request.session.create()
            save_session_dataset(request.session.session_key, content, original_filename)
            request.session['_ax_dataset_name'] = original_filename
            request.session.modified = True

        preview_id = str(uuid.uuid4())
        store_file_content('preview_' + preview_id, content)

        numeric_cols = list(df.select_dtypes(include='number').columns)
        all_cols = list(df.columns)

        response_data = {
            'success': True,
            'preview_id': preview_id,
            'filename': original_filename,
            'columns': all_cols,
            'numeric_cols': numeric_cols,
            'n_rows': len(df),
        }
        if tool in ('lojistik_regresyon', 'sagkalim', 'roc'):
            # Kullanıcının hedef kategoriyi (y=1 / olay) seçebilmesi için binary sütunların değerleri
            response_data['category_values'] = {
                col: sorted(str(v) for v in df[col].dropna().unique())
                for col in all_cols if df[col].nunique() == 2
            }
        return JsonResponse(response_data)

    elif step == 'run':
        if request.user.is_authenticated:
            remaining = _daily_remaining(request.user)
            if remaining <= 0:
                return JsonResponse({'error': gettext('Günlük analiz limitiniz doldu.')}, status=429)
            if not request.user.profile.email_verified:
                return JsonResponse({'error': gettext('E-posta doğrulaması gereklidir.')}, status=403)

        preview_id = request.POST.get('preview_id', '')
        filename = request.POST.get('filename', 'dosya')
        from .services.job_runner import _pending_file_contents, store_file_content

        content = _pending_file_contents.pop('preview_' + preview_id, None)
        if content is None:
            return JsonResponse({'error': gettext('Önizleme süresi doldu. Lütfen dosyayı tekrar yükleyin.')}, status=400)

        if tool == 'ttesti':
            options = {
                'test_type': request.POST.get('test_type', 'independent'),
                'group_col': request.POST.get('group_col', ''),
                'dep_col': request.POST.get('dep_col', ''),
                'col1': request.POST.get('col1', ''),
                'col2': request.POST.get('col2', ''),
                'test_value': request.POST.get('test_value', ''),
            }
        elif tool == 'anova':
            options = {
                'group_col': request.POST.get('group_col', ''),
                'dep_col': request.POST.get('dep_col', ''),
                'posthoc': request.POST.get('posthoc', 'tukey'),
            }
        elif tool == 'manova':
            options = {
                'group_col': request.POST.get('group_col', ''),
                'dep_cols': request.POST.getlist('dep_cols'),
            }
        elif tool == 'sagkalim':
            method = request.POST.get('method', 'kaplan_meier')
            if method not in ('kaplan_meier', 'cox'):
                method = 'kaplan_meier'
            options = {
                'method': method,
                'duration_col': request.POST.get('duration_col', ''),
                'event_col': request.POST.get('event_col', ''),
                'event_category': request.POST.get('event_category', ''),
            }
            if method == 'kaplan_meier':
                options['group_col'] = request.POST.get('group_col', '')
            else:
                options['covariate_cols'] = request.POST.getlist('covariate_cols')
        elif tool == 'roc':
            mode = request.POST.get('mode', 'single')
            if mode not in ('single', 'compare'):
                mode = 'single'
            options = {
                'mode': mode,
                'test_col': request.POST.get('test_col', ''),
                'ref_col': request.POST.get('ref_col', ''),
                'positive_category': request.POST.get('positive_category', ''),
            }
            if mode == 'compare':
                options['test_col2'] = request.POST.get('test_col2', '')
        elif tool in ('cronbach', 'normallik', 'betimsel'):
            cols = request.POST.getlist('columns')
            options = {'columns': cols} if cols else {}
        elif tool == 'korelasyon':
            method = request.POST.get('method', 'pearson')
            if method not in ('pearson', 'spearman', 'kendall'):
                method = 'pearson'
            cols = request.POST.getlist('columns')
            options = {'method': method}
            if cols:
                options['columns'] = cols
        elif tool == 'karar_agaci':
            max_d = request.POST.get('max_depth', '5').strip()
            t_size = request.POST.get('test_size', '0.2').strip()
            criterion = request.POST.get('criterion', 'gini')
            if criterion not in ('gini', 'entropy'):
                criterion = 'gini'
            options = {
                'target_col': request.POST.get('target_col', ''),
                'feature_cols': request.POST.getlist('feature_cols'),
                'max_depth': int(max_d) if max_d.isdigit() else 5,
                'test_size': float(t_size) if t_size else 0.2,
                'criterion': criterion,
            }
        elif tool in ('lineer_regresyon', 'lojistik_regresyon'):
            options = {
                'dep_col': request.POST.get('dep_col', ''),
                'indep_cols': request.POST.getlist('indep_cols'),
            }
            if tool == 'lojistik_regresyon':
                options['target_category'] = request.POST.get('target_category', '')
        elif tool == 'mediation':
            options = {
                'x_col': request.POST.get('x_col', ''),
                'm_col': request.POST.get('m_col', ''),
                'y_col': request.POST.get('y_col', ''),
            }
        elif tool == 'moderation':
            options = {
                'x_col': request.POST.get('x_col', ''),
                'w_col': request.POST.get('w_col', ''),
                'y_col': request.POST.get('y_col', ''),
            }
        elif tool == 'afa':
            cols = request.POST.getlist('columns')
            n_factors_raw = request.POST.get('n_factors', '').strip()
            rotation = request.POST.get('rotation', 'varimax')
            if rotation not in ('varimax', 'promax', 'oblimin'):
                rotation = 'varimax'
            options = {'rotation': rotation}
            if cols:
                options['columns'] = cols
            if n_factors_raw.isdigit() and int(n_factors_raw) > 0:
                options['n_factors'] = int(n_factors_raw)
        elif tool == 'kumeleme':
            cols = request.POST.getlist('columns')
            method = request.POST.get('method', 'kmeans')
            if method not in ('kmeans', 'hierarchical'):
                method = 'kmeans'
            n_clusters_raw = request.POST.get('n_clusters', '').strip()
            options = {'method': method}
            if cols:
                options['columns'] = cols
            if n_clusters_raw.isdigit() and int(n_clusters_raw) > 0:
                options['n_clusters'] = int(n_clusters_raw)
        elif tool == 'wilcoxon':
            options = {
                'col1': request.POST.get('col1', ''),
                'col2': request.POST.get('col2', ''),
            }
        elif tool in ('friedman', 'tekrarli_anova'):
            cols = request.POST.getlist('columns')
            options = {'columns': cols} if cols else {}
        else:  # mann_whitney, kruskal_wallis
            options = {
                'group_col': request.POST.get('group_col', ''),
                'dep_col': request.POST.get('dep_col', ''),
            }

        job = IstatistikJob.objects.create(
            user=request.user if request.user.is_authenticated else None,
            tool=tool,
            original_filename=filename,
            is_demo=not request.user.is_authenticated,
            options=options,
        )
        if not request.user.is_authenticated:
            demo_job_ids = request.session.get('demo_job_ids', [])
            demo_job_ids.append(str(job.id))
            request.session['demo_job_ids'] = demo_job_ids[-20:]
        from .services.job_runner import run_job
        store_file_content(str(job.id), content)
        run_job(str(job.id))
        return JsonResponse({'success': True, 'job_id': str(job.id)})

    return JsonResponse({'error': gettext('Geçersiz adım.')}, status=400)


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def mann_whitney_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('mann_whitney'),
            'promo_title': gettext('Mann-Whitney U Testi'),
            'promo_icon': 'bi-distribute-horizontal',
            'promo_color': 'warning',
            'promo_description': gettext('İki bağımsız grubun dağılımını karşılaştırın. Normallik varsayımı gerekmez. Medyan farkı, sıra ortalamaları ve rank-biserial etki büyüklüğü ile PDF raporu alın.'),
            'promo_features': [
                {'icon': 'bi-people-fill', 'title': gettext('Non-Parametrik'), 'desc': gettext('Normallik varsayımı sağlanmadığında t-testine güçlü bir alternatif.')},
                {'icon': 'bi-bar-chart-line', 'title': gettext('Sıra Analizi'), 'desc': gettext('Medyanlar ve ortalama sıralar raporlanır.')},
                {'icon': 'bi-rulers', 'title': gettext('Etki Büyüklüğü'), 'desc': gettext('Rank-biserial korelasyon (r) ile etki büyüklüğü hesaplanır.')},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': gettext('PDF Rapor'), 'desc': gettext('Sonuçlar düzenli tablolar halinde PDF olarak indirilir.')},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'mann_whitney')
    active_job = _get_active_job(request.user, 'mann_whitney')
    return render(request, 'istatistik/mann_whitney.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': gettext('Mann-Whitney U Testi'),
        'tool_icon': 'bi-distribute-horizontal',
        'tool_color': 'warning',
        **_console_ctx('mann_whitney', request),
    })


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def kruskal_wallis_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('kruskal_wallis'),
            'promo_title': gettext('Kruskal-Wallis H Testi'),
            'promo_icon': 'bi-bar-chart-steps',
            'promo_color': 'teal',
            'promo_description': gettext('Üç veya daha fazla bağımsız grubun dağılımını non-parametrik olarak karşılaştırın. Bonferroni düzeltmeli post-hoc testleri ve η² etki büyüklüğü ile PDF raporu alın.'),
            'promo_features': [
                {'icon': 'bi-bar-chart-fill', 'title': gettext('3+ Grup'), 'desc': gettext('ANOVA\'nın parametrik olmayan alternatifi. Normallik gerekmez.')},
                {'icon': 'bi-search', 'color': 'warning', 'title': gettext('Post-Hoc'), 'desc': gettext('Anlamlı fark bulunursa Dunn testi + Bonferroni düzeltmesi uygulanır.')},
                {'icon': 'bi-rulers', 'title': gettext('Etki Büyüklüğü'), 'desc': gettext('Eta-kare (η²) ile etki büyüklüğü raporlanır.')},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': gettext('PDF Rapor'), 'desc': gettext('Grup istatistikleri ve post-hoc sonuçları PDF\'e aktarılır.')},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'kruskal_wallis')
    active_job = _get_active_job(request.user, 'kruskal_wallis')
    return render(request, 'istatistik/kruskal_wallis.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': gettext('Kruskal-Wallis H Testi'),
        'tool_icon': 'bi-bar-chart-steps',
        'tool_color': 'teal',
        **_console_ctx('kruskal_wallis', request),
    })


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def ki_kare_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('ki_kare'),
            'promo_title': gettext('Ki-Kare Testi'),
            'promo_icon': 'bi-grid-3x3',
            'promo_color': 'purple',
            'promo_description': gettext('İki kategorik değişken arasındaki ilişkiyi test edin. Çapraz tablo ve Cramér\'s V etki büyüklüğü ile PDF raporu alın.'),
            'promo_features': [
                {'icon': 'bi-grid-3x3', 'title': gettext('Bağımsızlık Testi'), 'desc': gettext('Pearson\'s Ki-Kare testi ile iki kategorik değişken arasındaki ilişki sınanır.')},
                {'icon': 'bi-table', 'color': 'info', 'title': gettext('Çapraz Tablo'), 'desc': gettext('Gözlenen frekanslar ve satır/sütun toplamları ile tam çapraz tablo.')},
                {'icon': 'bi-rulers', 'title': gettext('Cramér\'s V'), 'desc': gettext('Etki büyüklüğü V katsayısı ile ilişkinin gücü raporlanır.')},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': gettext('PDF Rapor'), 'desc': gettext('APA formatında raporlanabilir sonuçlar PDF olarak indirilir.')},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'ki_kare')
    active_job = _get_active_job(request.user, 'ki_kare')
    return render(request, 'istatistik/ki_kare.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': gettext('Ki-Kare Testi'),
        'tool_icon': 'bi-grid-3x3',
        'tool_color': 'purple',
        **_console_ctx('ki_kare', request),
    })


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def lineer_regresyon_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('lineer_regresyon'),
            'promo_title': gettext('Çoklu Doğrusal Regresyon'),
            'promo_icon': 'bi-graph-up-arrow',
            'promo_color': 'primary',
            'promo_description': gettext('Bir veya birden fazla bağımsız değişkenin sürekli bir bağımlı değişkeni ne kadar açıkladığını analiz edin. R², F testi, standardize beta ve VIF dahil tam OLS regresyon raporu.'),
            'promo_features': [
                {'icon': 'bi-graph-up-arrow', 'title': gettext('OLS Regresyon'), 'desc': gettext('R², düzeltilmiş R², F istatistiği ve model anlamlılığı otomatik hesaplanır.')},
                {'icon': 'bi-table', 'color': 'info', 'title': gettext('Katsayı Tablosu'), 'desc': gettext('Her yordayıcı için B, β (standardize), SE, t, p ve %95 güven aralığı raporlanır.')},
                {'icon': 'bi-exclamation-triangle', 'color': 'warning', 'title': gettext('VIF (Çoklu Bağlantı)'), 'desc': gettext('Variance Inflation Factor ile çoklu bağlantı sorunu kontrol edilir.')},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': gettext('PDF Rapor'), 'desc': gettext('APA formatında raporlanabilir sonuçlar PDF olarak indirilir.')},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'lineer_regresyon')
    active_job = _get_active_job(request.user, 'lineer_regresyon')
    return render(request, 'istatistik/lineer_regresyon.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': gettext('Çoklu Doğrusal Regresyon'),
        'tool_icon': 'bi-graph-up-arrow',
        'tool_color': 'primary',
        **_console_ctx('lineer_regresyon', request),
    })


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def lojistik_regresyon_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('lojistik_regresyon'),
            'promo_title': gettext('Lojistik Regresyon'),
            'promo_icon': 'bi-diagram-3',
            'promo_color': 'success',
            'promo_description': gettext('İkili (binary) bir sonuç değişkenini yordayın. Odds Ratio, Nagelkerke R² ve sınıflandırma tablosu ile tam lojistik regresyon raporu.'),
            'promo_features': [
                {'icon': 'bi-toggles', 'title': gettext('Binary Sonuç'), 'desc': gettext('0/1 veya iki kategorili bağımlı değişken ile çalışır. Kategorik yordayıcılar otomatik dummy\'e dönüştürülür.')},
                {'icon': 'bi-table', 'color': 'info', 'title': gettext('Odds Ratio'), 'desc': gettext('Her yordayıcı için B, SE, Wald, p ve Exp(B) = Odds Ratio %95 GA ile raporlanır.')},
                {'icon': 'bi-check2-square', 'color': 'warning', 'title': gettext('Sınıflandırma'), 'desc': gettext('Model doğruluğu ve sınıflandırma tablosu (TP, TN, FP, FN) gösterilir.')},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': gettext('PDF Rapor'), 'desc': gettext('Nagelkerke R², model χ² ve APA formatında raporlanabilir sonuçlar PDF olarak indirilir.')},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'lojistik_regresyon')
    active_job = _get_active_job(request.user, 'lojistik_regresyon')
    return render(request, 'istatistik/lojistik_regresyon.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': gettext('Lojistik Regresyon'),
        'tool_icon': 'bi-diagram-3',
        'tool_color': 'success',
        **_console_ctx('lojistik_regresyon', request),
    })


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def mediation_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('mediation'),
            'promo_title': gettext('Aracılık Analizi (Mediation)'),
            'promo_icon': 'bi-diagram-3-fill',
            'promo_color': 'purple',
            'promo_description': gettext('Bir bağımsız değişkenin bağımlı değişken üzerindeki etkisinin bir aracı (mediator) değişken üzerinden ne kadar ilettiğini test edin. Bootstrap güven aralığı ve Sobel testi ile SPSS Process/Hayes\'e karşılık gelen tam bir aracılık raporu.'),
            'promo_features': [
                {'icon': 'bi-diagram-3', 'title': gettext('a, b, c, c\' Yolları'), 'desc': gettext('Toplam etki, dolaylı yol ve M kontrol edildiğinde kalan direkt etki ayrı ayrı hesaplanır.')},
                {'icon': 'bi-arrow-repeat', 'color': 'info', 'title': gettext('Bootstrap Güven Aralığı'), 'desc': gettext('Dolaylı etkinin (a×b) anlamlılığı 5000 yeniden örneklemeli bootstrap %95 GA ile test edilir — Hayes/Process yöntemiyle aynı mantık.')},
                {'icon': 'bi-rulers', 'color': 'warning', 'title': gettext('Sobel Testi'), 'desc': gettext('Klasik Sobel z testi ek doğrulama olarak raporlanır.')},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': gettext('PDF Rapor'), 'desc': gettext('Tam/kısmi aracılık sonucu ve APA formatında raporlama cümlesi PDF olarak indirilir.')},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'mediation')
    active_job = _get_active_job(request.user, 'mediation')
    return render(request, 'istatistik/mediation.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': gettext('Aracılık Analizi (Mediation)'),
        'tool_icon': 'bi-diagram-3-fill',
        'tool_color': 'purple',
        'tool_description': gettext('X\'in Y üzerindeki etkisinin M aracı değişkeni üzerinden ne kadarının iletildiğini test edin.'),
        'tool_hints': [
            gettext('Bağımsız değişken (X) sayısal veya 2 kategorili olabilir.'),
            gettext('Aracı (M) ve bağımlı (Y) değişkenler sayısal/sürekli olmalıdır.'),
            gettext('En az 20 gözlem (satır) önerilir.'),
            gettext('Dolaylı etkinin anlamlılığı bootstrap %95 güven aralığı ile test edilir.'),
        ],
        **_console_ctx('mediation', request),
    })


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def moderation_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('moderation'),
            'promo_title': gettext('Düzenleyici Değişken Analizi (Moderation)'),
            'promo_icon': 'bi-sliders',
            'promo_color': 'purple',
            'promo_description': gettext('X\'in Y üzerindeki etkisinin bir düzenleyici (moderatör) değişkene bağlı olarak ne zaman güçlendiğini veya zayıfladığını test edin. Basit eğimler, etkileşim grafiği ve APA formatında raporlama ile SPSS Process/Hayes\'e karşılık gelen tam bir düzenleyici değişken raporu.'),
            'promo_features': [
                {'icon': 'bi-sliders', 'title': gettext('Etkileşim Terimi (X×W)'), 'desc': gettext('Aiken & West (1991) merkezleme standardıyla X, W ve etkileşim terimlerinin etkisi ayrı ayrı hesaplanır.')},
                {'icon': 'bi-graph-up', 'color': 'info', 'title': gettext('Basit Eğimler (Simple Slopes)'), 'desc': gettext('X\'in Y üzerindeki etkisi W\'nin düşük/orta/yüksek (veya 2 kategorili) düzeylerinde ayrı ayrı raporlanır.')},
                {'icon': 'bi-bar-chart-line', 'color': 'warning', 'title': gettext('Etkileşim Grafiği'), 'desc': gettext('X-Y ilişkisinin W düzeylerine göre nasıl değiştiğini gösteren görsel grafik otomatik oluşturulur.')},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': gettext('PDF Rapor'), 'desc': gettext('Katsayılar, basit eğimler tablosu ve APA formatında raporlama cümlesi PDF olarak indirilir.')},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'moderation')
    active_job = _get_active_job(request.user, 'moderation')
    return render(request, 'istatistik/moderation.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': gettext('Düzenleyici Değişken Analizi (Moderation)'),
        'tool_icon': 'bi-sliders',
        'tool_color': 'purple',
        'tool_description': gettext('X\'in Y üzerindeki etkisinin W düzenleyici değişkenine bağlı olarak ne zaman güçlendiğini veya zayıfladığını test edin.'),
        'tool_hints': [
            gettext('Bağımsız (X) ve bağımlı (Y) değişkenler sayısal/sürekli olmalıdır.'),
            gettext('Düzenleyici değişken (W) sayısal veya 2 kategorili olabilir.'),
            gettext('En az 30 gözlem (satır) önerilir.'),
            gettext('Düzenleme etkisinin anlamlılığı etkileşim teriminin (X×W) p değeri ile test edilir.'),
        ],
        **_console_ctx('moderation', request),
    })


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def karar_agaci_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('karar_agaci'),
            'promo_title': gettext('Karar Ağacı Sınıflandırması'),
            'promo_icon': 'bi-diagram-2',
            'promo_color': 'purple',
            'promo_egitim_konu': 'makine-ogrenmesi',
            'promo_description': gettext('Veri setinizdeki kategorik hedef değişkeni sınıflandırın. Özellik önemi, confusion matrix ve ağaç yapısı görselleştirmesiyle tam ML raporu.'),
            'promo_features': [
                {'icon': 'bi-diagram-2', 'title': gettext('Ağaç Modeli'), 'desc': gettext('Gini veya Entropy kriteri ile karar ağacı eğitilir. Maksimum derinliği kendiniz belirleyebilirsiniz.')},
                {'icon': 'bi-bar-chart-steps', 'color': 'warning', 'title': gettext('Özellik Önemi'), 'desc': gettext('Hangi değişkenin sınıflandırmaya en çok katkı yaptığı sıralı tablo ile gösterilir.')},
                {'icon': 'bi-grid-3x3', 'color': 'info', 'title': gettext('Confusion Matrix'), 'desc': gettext('Test seti üzerindeki doğruluk, kesinlik, duyarlılık ve F1 skoru raporlanır.')},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': gettext('PDF Rapor'), 'desc': gettext('Ağaç yapısı, metrikler ve APA formatında raporlama cümlesi PDF olarak indirilir.')},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'karar_agaci')
    active_job = _get_active_job(request.user, 'karar_agaci')
    return render(request, 'istatistik/karar_agaci.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': gettext('Karar Ağacı Sınıflandırması'),
        'tool_icon': 'bi-diagram-2',
        'tool_color': 'purple',
        **_console_ctx('karar_agaci', request),
    })


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def svm_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('svm'),
            'promo_title': gettext('Destek Vektör Makinesi (SVM)'),
            'promo_icon': 'bi-cpu',
            'promo_color': 'teal',
            'promo_description': gettext('Veri setinizdeki kategorik hedef değişkeni yüksek doğrulukla sınıflandırın. RBF, Doğrusal ve Polinom kernel seçenekleriyle confusion matrix ve permutation importance dahil tam ML raporu.'),
            'promo_features': [
                {'icon': 'bi-cpu', 'title': gettext('SVM Modeli'), 'desc': gettext('RBF, Doğrusal veya Polinom kernel ve C düzenleme parametresiyle Destek Vektör Makinesi eğitilir.')},
                {'icon': 'bi-bar-chart-steps', 'color': 'warning', 'title': gettext('Permutation Importance'), 'desc': gettext('Her değişkenin sınıflandırmaya gerçek katkısı permütasyon yöntemiyle hesaplanır ve sıralanır.')},
                {'icon': 'bi-grid-3x3', 'color': 'info', 'title': gettext('Confusion Matrix'), 'desc': gettext('Test seti üzerindeki doğruluk, kesinlik, duyarlılık ve F1 skoru raporlanır.')},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': gettext('PDF Rapor'), 'desc': gettext('Metrikler, confusion matrix ve APA formatında raporlama cümlesi PDF olarak indirilir.')},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'svm')
    active_job = _get_active_job(request.user, 'svm')
    return render(request, 'istatistik/svm.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': gettext('Destek Vektör Makinesi (SVM)'),
        'tool_icon': 'bi-cpu',
        'tool_color': 'teal',
        **_console_ctx('svm', request),
    })


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def kumeleme_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('kumeleme'),
            'promo_title': gettext('Kümeleme Analizi (K-means / Hiyerarşik)'),
            'promo_icon': 'bi-bounding-box-circles',
            'promo_color': 'info',
            'promo_egitim_konu': 'makine-ogrenmesi',
            'promo_description': gettext('Veri setinizdeki gözlemleri benzerliklerine göre otomatik gruplara ayırın. K-means veya Hiyerarşik (Ward) yöntemle, silhouette skoruna göre otomatik küme sayısı önerisi ve küme profili tablosuyla tam rapor.'),
            'promo_features': [
                {'icon': 'bi-bounding-box-circles', 'title': gettext('İki Yöntem'), 'desc': gettext('K-means veya Hiyerarşik (Ward bağlantı) kümeleme yöntemlerinden birini seçin.')},
                {'icon': 'bi-sliders', 'color': 'warning', 'title': gettext('Otomatik k Seçimi'), 'desc': gettext('Küme sayısını belirtmezseniz silhouette skoruna göre en uygun k otomatik seçilir.')},
                {'icon': 'bi-table', 'color': 'success', 'title': gettext('Küme Profili'), 'desc': gettext('Her kümenin büyüklüğü ve değişken ortalamaları tablo halinde raporlanır.')},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': gettext('PDF Rapor'), 'desc': gettext('Diyagnostik grafik, dağılım grafiği ve APA formatında raporlama cümlesi PDF olarak indirilir.')},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'kumeleme')
    active_job = _get_active_job(request.user, 'kumeleme')
    return render(request, 'istatistik/kumeleme.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': gettext('Kümeleme Analizi (K-means / Hiyerarşik)'),
        'tool_icon': 'bi-bounding-box-circles',
        'tool_color': 'info',
        **_console_ctx('kumeleme', request),
    })


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def afa_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('afa'),
            'promo_title': gettext('Açıklayıcı Faktör Analizi (AFA)'),
            'promo_icon': 'bi-diagram-2',
            'promo_color': 'info',
            'promo_description': gettext('Ölçek geçerliğini kanıtlayın. KMO, Bartlett testi, faktör yük matrisi ve açıklanan varyans tablosu ile tam AFA raporu.'),
            'promo_features': [
                {'icon': 'bi-grid-3x3', 'title': gettext('Faktör Yapısı'), 'desc': gettext('Varimax rotasyonlu faktör yük matrisi ile her maddenin hangi faktöre yüklendiğini görün.')},
                {'icon': 'bi-bar-chart-steps', 'color': 'warning', 'title': gettext('KMO & Bartlett'), 'desc': gettext('Örneklem yeterliliği (KMO) ve Bartlett küresellik testi ile faktör analizine uygunluğu sınayın.')},
                {'icon': 'bi-percent', 'color': 'success', 'title': gettext('Açıklanan Varyans'), 'desc': gettext('Her faktörün açıkladığı varyans yüzdesi ve kümülatif varyans tablosu.')},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': gettext('PDF Rapor'), 'desc': gettext('APA formatında raporlanabilir tablo ve yorum içeren PDF indirilir.')},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'afa')
    active_job = _get_active_job(request.user, 'afa')
    return render(request, 'istatistik/afa.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': gettext('Açıklayıcı Faktör Analizi (AFA)'),
        'tool_icon': 'bi-diagram-2',
        'tool_color': 'info',
        'tool_description': gettext('Ölçek geçerliğini sınayın. Her sütun bir madde, her satır bir katılımcı olmalıdır.'),
        'tool_hints': [
            gettext('Her sütun bir ölçek maddesi olmalıdır (örn. M1, M2…).'),
            gettext('Tüm sütunlar sayısal olmalıdır (Likert vb.).'),
            gettext('Faktör sayısı otomatik belirlenir (özdeğer > 1 kuralı).'),
            gettext('En az 3 madde ve 10 katılımcı gereklidir.'),
        ],
        **_console_ctx('afa', request),
    })


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def wilcoxon_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('wilcoxon'),
            'promo_title': gettext('Wilcoxon İşaret Testi'),
            'promo_icon': 'bi-arrow-left-right',
            'promo_color': 'warning',
            'promo_description': gettext('İki bağımlı (eşleştirilmiş) ölçümü karşılaştırın. Bağımlı t-testinin parametrik olmayan alternatifi.'),
            'promo_features': [
                {'icon': 'bi-bar-chart-steps', 'title': gettext('W İstatistiği'), 'desc': gettext('Wilcoxon W istatistiği ve p değeri ile iki ölçüm arasındaki farkı sınayın.')},
                {'icon': 'bi-arrows-collapse', 'color': 'warning', 'title': gettext('Etki Büyüklüğü'), 'desc': gettext('Rank-biserial korelasyon (r) ile etki büyüklüğünü hesaplayın.')},
                {'icon': 'bi-table', 'color': 'success', 'title': gettext('Betimsel Tablo'), 'desc': gettext('Her ölçüm için medyan, ortalama ve fark istatistikleri.')},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': gettext('PDF Rapor'), 'desc': gettext('APA formatında otomatik rapor cümlesi ve PDF indirme.')},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'wilcoxon')
    active_job = _get_active_job(request.user, 'wilcoxon')
    return render(request, 'istatistik/wilcoxon.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': gettext('Wilcoxon İşaret Testi'),
        **_console_ctx('wilcoxon', request),
    })


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def friedman_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('friedman'),
            'promo_title': gettext('Friedman Testi'),
            'promo_icon': 'bi-bar-chart-steps',
            'promo_color': 'success',
            'promo_description': gettext('3 veya daha fazla bağımlı (eşleştirilmiş) ölçümü karşılaştırın. Tekrarlayan ölçümler ANOVA\'nın parametrik olmayan alternatifi.'),
            'promo_features': [
                {'icon': 'bi-bar-chart-steps', 'title': gettext('χ² İstatistiği'), 'desc': gettext('Friedman χ² istatistiği, serbestlik derecesi ve p değeri ile ölçümler arası farkı sınayın.')},
                {'icon': 'bi-rulers', 'color': 'success', 'title': gettext("Kendall's W"), 'desc': gettext("Etki büyüklüğü Kendall's W katsayısı ile raporlanır.")},
                {'icon': 'bi-diagram-3', 'color': 'warning', 'title': gettext('Post-Hoc'), 'desc': gettext('Anlamlı bulunursa Bonferroni düzeltmeli pairwise Wilcoxon karşılaştırmaları.')},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': gettext('PDF Rapor'), 'desc': gettext('APA formatında hazır raporlama cümlesi ve PDF indirme.')},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'friedman')
    active_job = _get_active_job(request.user, 'friedman')
    return render(request, 'istatistik/friedman.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': gettext('Friedman Testi'),
        **_console_ctx('friedman', request),
    })


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def tekrarli_anova_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('tekrarli_anova'),
            'promo_title': gettext('Tekrarlayan Ölçümler ANOVA'),
            'promo_icon': 'bi-graph-up-arrow',
            'promo_color': 'primary',
            'promo_description': gettext('Aynı katılımcıların 3+ farklı koşulda/zamanda ölçüldüğü verileri analiz edin. F istatistiği, η² etki büyüklüğü ve Bonferroni post-hoc ile PDF raporu alın.'),
            'promo_features': [
                {'icon': 'bi-graph-up-arrow', 'title': gettext('F İstatistiği'), 'desc': gettext('Tekrarlayan ölçümler ANOVA ile F istatistiği, serbestlik derecesi ve p değeri hesaplanır.')},
                {'icon': 'bi-rulers', 'color': 'primary', 'title': gettext('Etki Büyüklüğü (η²)'), 'desc': gettext('Partial eta-squared (η²) ile etki büyüklüğü raporlanır.')},
                {'icon': 'bi-diagram-3', 'color': 'warning', 'title': gettext('Post-Hoc'), 'desc': gettext('Bonferroni düzeltmeli bağımlı t-testi ile hangi ölçüm çiftlerinin farklılaştığı belirlenir.')},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': gettext('PDF Rapor'), 'desc': gettext('ANOVA tablosu, post-hoc ve APA formatında otomatik raporlama cümlesi.')},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'tekrarli_anova')
    active_job = _get_active_job(request.user, 'tekrarli_anova')
    return render(request, 'istatistik/tekrarli_anova.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': gettext('Tekrarlayan Ölçümler ANOVA'),
        **_console_ctx('tekrarli_anova', request),
    })


def clear_session_dataset(request):
    """Session'daki veri setini temizle."""
    from django.views.decorators.http import require_POST
    if request.method != 'POST':
        from django.http import HttpResponseNotAllowed
        return HttpResponseNotAllowed(['POST'])
    from .services.job_runner import _session_datasets
    session_key = request.session.session_key
    if session_key:
        _session_datasets.pop(session_key, None)
    request.session.pop('_ax_dataset_name', None)
    request.session.modified = True
    return JsonResponse({'ok': True})


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def hero_upload(request):
    """Ana sayfa hero dropzone'undan gelen dosyayı session veri setine kaydeder.
    Böylece kullanıcı /analiz/<slug>/ araç sayfasına geçtiğinde dosyayı
    tekrar yüklemesine gerek kalmaz (mevcut session dataset mekanizması)."""
    if request.method != 'POST':
        from django.http import HttpResponseNotAllowed
        return HttpResponseNotAllowed(['POST'])

    from .services.job_runner import _parse_file, save_session_dataset

    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': gettext('Dosya seçilmedi.')}, status=400)
    if not file.name.lower().endswith(('.csv', '.xlsx', '.xls')):
        return JsonResponse({'error': gettext('CSV veya Excel dosyası yükleyin.')}, status=400)
    if file.size > django_settings.MAX_UPLOAD_SIZE:
        return JsonResponse({'error': gettext('Dosya boyutu 5 MB sınırını aşıyor.')}, status=400)

    content = file.read()
    try:
        _parse_file(content, file.name)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    if not request.session.session_key:
        request.session.create()
    save_session_dataset(request.session.session_key, content, file.name)
    request.session['_ax_dataset_name'] = file.name
    request.session.modified = True

    return JsonResponse({'success': True, 'filename': file.name})


def analiz_hub(request):
    tool_category_groups = [
        {
            'cat_name': cat_name,
            'tools': tools,
            'service_slug': slug,
            'service_title': _SERVICE_PAGE_TITLES.get(slug),
        }
        for slug, (cat_name, tools) in zip(_TOOL_GROUP_SERVICE_SLUGS, TOOL_CATEGORIES)
    ]
    return render(request, 'istatistik/analiz_hub.html', {
        'tool_categories': TOOL_CATEGORIES,
        'tool_category_groups': tool_category_groups,
        'from_hero': request.GET.get('from') == 'hero',
    })


def analiz_redirect(request):
    from django.shortcuts import redirect
    return redirect('istatistik:betimsel', permanent=False)


@feature_required
def analiz_console(request, tool_slug):
    """Unified /analiz/<slug>/ entry point — delegates to the matching landing view."""
    _SLUG_MAP = {
        'betimsel': betimsel_landing,
        'normallik': normallik_landing,
        'orneklem': orneklem_landing,
        'cronbach': cronbach_landing,
        'afa': afa_landing,
        'korelasyon': korelasyon_landing,
        'ki-kare': ki_kare_landing,
        'ttesti': ttesti_landing,
        'anova': anova_landing,
        'mann-whitney': mann_whitney_landing,
        'kruskal-wallis': kruskal_wallis_landing,
        'wilcoxon': wilcoxon_landing,
        'friedman': friedman_landing,
        'tekrarli-anova': tekrarli_anova_landing,
        'lineer-regresyon': lineer_regresyon_landing,
        'lojistik-regresyon': lojistik_regresyon_landing,
        'mediation': mediation_landing,
        'moderation': moderation_landing,
        'karar-agaci': karar_agaci_landing,
        'svm': svm_landing,
        'kumeleme': kumeleme_landing,
        'manova': manova_landing,
        'sagkalim': sagkalim_landing,
        'roc': roc_landing,
    }
    view_fn = _SLUG_MAP.get(tool_slug)
    if not view_fn:
        raise Http404
    return view_fn(request)


def _handle_orneklem_calc(request):
    from .services.orneklem import calculate
    try:
        test_type = request.POST.get('test_type', '')
        effect_size = float(request.POST.get('effect_size', 0))
        alpha = float(request.POST.get('alpha', 0.05))
        power = float(request.POST.get('power', 0.80))
        groups = int(request.POST.get('groups', 2))
        result = calculate(test_type, effect_size, alpha, power, groups)
        return JsonResponse({'success': True, 'result': result})
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': gettext('Hesaplama hatası: %(e)s') % {'e': e}}, status=500)


@require_GET
def job_status(request, job_id):
    """AJAX polling: job durumu + sonuç."""
    job = get_object_or_404(IstatistikJob, id=job_id)

    if job.user_id is not None:
        if not request.user.is_authenticated or request.user.pk != job.user_id:
            raise Http404
    elif str(job.id) not in request.session.get('demo_job_ids', []):
        raise Http404

    resp = {'status': job.status}
    if job.status == 'completed':
        resp['pdf_url'] = job.pdf_url
        resp['result_data'] = job.result_data
        if request.user.is_authenticated:
            resp['daily_remaining'] = _daily_remaining(request.user)
    elif job.status == 'failed':
        resp['error'] = job.error_message
    return JsonResponse(resp)


# ── Yardımcı fonksiyonlar ──────────────────────────────────────────────────

def _handle_upload(request, tool, options=None):
    """POST: dosyayı al, job oluştur, kuyruğa ekle."""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.user.is_authenticated:
        remaining = _daily_remaining(request.user)
        if remaining <= 0:
            msg = gettext('Günlük analiz limitiniz doldu.')
            return JsonResponse({'error': msg}, status=429) if is_ajax else \
                   JsonResponse({'error': msg}, status=429)

        if not request.user.profile.email_verified:
            msg = gettext('E-posta doğrulaması gereklidir.')
            return JsonResponse({'error': msg}, status=403)

    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': gettext('Dosya seçilmedi.')}, status=400)

    allowed_ext = ('.csv', '.xlsx', '.xls')
    if not file.name.lower().endswith(allowed_ext):
        return JsonResponse({'error': gettext('Yalnızca CSV veya Excel (.xlsx/.xls) dosyası yükleyebilirsiniz.')}, status=400)

    if file.size > django_settings.MAX_UPLOAD_SIZE:  # 10 MB
        return JsonResponse({'error': gettext('Dosya boyutu 5 MB sınırını aşıyor.')}, status=400)

    content = file.read()

    from .services.job_runner import _parse_file
    try:
        df = _parse_file(content, file.name)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    from .services.data_validator import validate_dataframe
    warnings = validate_dataframe(df, tool)
    if warnings and request.POST.get('confirm_warnings', 'false').lower() != 'true':
        return JsonResponse({'warnings': warnings, 'confirm_warnings': True})

    job = IstatistikJob.objects.create(
        user=request.user if request.user.is_authenticated else None,
        tool=tool,
        original_filename=file.name,
        is_demo=not request.user.is_authenticated,
        options=options or {},
    )

    if not request.user.is_authenticated:
        demo_job_ids = request.session.get('demo_job_ids', [])
        demo_job_ids.append(str(job.id))
        request.session['demo_job_ids'] = demo_job_ids[-20:]

    from .services.job_runner import store_file_content, run_job
    store_file_content(str(job.id), content)
    run_job(str(job.id))

    return JsonResponse({'success': True, 'job_id': str(job.id)})


def _get_active_job(user, tool):
    if not user.is_authenticated:
        return None
    return IstatistikJob.objects.filter(
        user=user,
        tool=tool,
        status__in=['pending', 'running'],
    ).order_by('-created_at').first()


def _daily_remaining(user):
    limit = IstatistikJob.get_daily_limit(user)
    used = IstatistikJob.daily_count_for_user(user)
    return max(0, limit - used)
