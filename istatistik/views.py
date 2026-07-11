from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_GET
from django_ratelimit.decorators import ratelimit
from django.conf import settings as django_settings
from functools import wraps

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
    ('Ön Analizler', [
        ('betimsel',  'Betimleyici İstatistik',       'bi-clipboard2-data',    'success',  'betimsel'),
        ('normallik', 'Normallik Testi',               'bi-activity',           'warning',  'normallik'),
        ('orneklem',  'Örneklem Hesaplayıcı',          'bi-calculator-fill',    'info',     'orneklem'),
    ]),
    ('Geçerlik & Güvenirlik', [
        ('cronbach',  'Cronbach Alpha',                'bi-shield-check',       'primary',  'cronbach'),
        ('afa',       'Açıklayıcı Faktör Analizi',     'bi-diagram-3',          'info',     'afa'),
    ]),
    ('İlişki Analizleri', [
        ('korelasyon', 'Korelasyon Matrisi',           'bi-grid-3x3',           'info',     'korelasyon'),
        ('ki_kare',   'Ki-Kare Testi',                 'bi-table',              'warning',  'ki-kare'),
    ]),
    ('Fark Analizleri', [
        ('ttesti',         't-Testi',                  'bi-distribute-horizontal', 'primary', 'ttesti'),
        ('anova',          'Tek Yönlü ANOVA',           'bi-bar-chart-steps',   'danger',   'anova'),
        ('mann_whitney',   'Mann-Whitney U',            'bi-arrow-left-right',  'warning',  'mann-whitney'),
        ('kruskal_wallis', 'Kruskal-Wallis H',          'bi-funnel',            'teal',     'kruskal-wallis'),
        ('wilcoxon',       'Wilcoxon İşaret Testi',     'bi-arrows-collapse',   'info',     'wilcoxon'),
        ('friedman',       'Friedman Testi',            'bi-bar-chart-steps',   'success',  'friedman'),
        ('tekrarli_anova', 'Tekrarlayan Ölçümler ANOVA','bi-arrow-repeat',      'primary',  'tekrarli-anova'),
    ]),
    ('Regresyon Analizleri', [
        ('lineer_regresyon',  'Çoklu Doğrusal Regresyon', 'bi-graph-up-arrow',  'primary',  'lineer-regresyon'),
        ('lojistik_regresyon','Lojistik Regresyon',        'bi-bezier2',         'success',  'lojistik-regresyon'),
    ]),
    ('Makine Öğrenmesi', [
        ('karar_agaci', 'Karar Ağacı', 'bi-diagram-2', 'purple', 'karar-agaci'),
        ('svm', 'Destek Vektör Makinesi', 'bi-cpu', 'teal', 'svm'),
    ]),
]


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
        'CSV veya Excel dosyanızı yükleyin.',
        'Analiz otomatik olarak saniyeler içinde tamamlanır.',
        'Sonuçları ekranda görün ve PDF olarak indirin.',
    ],
}


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def cronbach_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('cronbach'),
            'promo_title': 'Güvenilirlik Analizi — Cronbach Alpha',
            'promo_icon': 'bi-shield-check',
            'promo_color': 'primary',
            'promo_description': 'Anket ölçeğinizin iç tutarlılığını ölçün. CSV/Excel dosyanızı yükleyin; Cronbach Alpha katsayısı, madde-toplam korelasyonları ve madde çıkarma tablosu PDF olarak hazır.',
            'promo_features': [
                {'icon': 'bi-upload', 'title': 'Kolay Yükleme', 'desc': 'CSV veya Excel dosyanızı sürükle-bırak ile yükleyin. Her sütun bir madde, her satır bir katılımcı olmalıdır.'},
                {'icon': 'bi-calculator', 'title': 'Cronbach Alpha', 'desc': 'α katsayısı ve "Kabul Edilemez / Düşük / Kabul Edilebilir / İyi / Mükemmel" yorumu otomatik hesaplanır.'},
                {'icon': 'bi-table', 'title': 'Madde İstatistikleri', 'desc': 'Her madde için ortalama, standart sapma, düzeltilmiş madde-toplam korelasyonu ve madde silinince alpha tablosu.'},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': 'PDF Rapor', 'desc': 'Tüm sonuçlar düzenli tablolar halinde PDF olarak indirilebilir.'},
            ],
        })

    if request.method == 'POST':
        return _handle_group_tool_post(request, 'cronbach')

    active_job = _get_active_job(request.user, 'cronbach')
    return render(request, 'istatistik/cronbach.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': 'Güvenilirlik Analizi — Cronbach Alpha',
        'tool_icon': 'bi-shield-check',
        'tool_color': 'primary',
        'tool_description': 'Anket ölçeğinizin iç tutarlılığını ölçün. Her sütun bir madde, her satır bir katılımcı olmalıdır.',
        'tool_hints': [
            'Her sütun bir ölçek maddesi olmalıdır (örn. S1, S2, S3…).',
            'Her satır bir katılımcıyı temsil etmelidir.',
            'Başlık satırı otomatik algılanır.',
            'Boş hücreler (NA) satırdan çıkarılır.',
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
            'promo_title': 'Normallik Testi',
            'promo_icon': 'bi-bell-curve',
            'promo_color': 'warning',
            'promo_description': '"Parametrik mi, non-parametrik mi?" sorusunu yanıtlayın. Shapiro-Wilk testi, çarpıklık/basıklık değerleri ve Q-Q plot içeren PDF raporu saniyeler içinde alın.',
            'promo_features': [
                {'icon': 'bi-graph-up', 'title': 'Shapiro-Wilk Testi', 'desc': 'Her değişken için W istatistiği ve p-değeri hesaplanır. p < 0.05 normal dağılımdan sapma anlamına gelir.'},
                {'icon': 'bi-bar-chart-steps', 'title': 'Çarpıklık & Basıklık', 'desc': 'Skewness ve kurtosis değerleri ±1.96 ve ±2.58 kritik sınırlarıyla yorumlanır.'},
                {'icon': 'bi-scatter-chart', 'color': 'info', 'title': 'Q-Q Plot', 'desc': 'Her değişken için görsel normallik grafiği PDF\'e eklenir.'},
                {'icon': 'bi-check-circle-fill', 'color': 'success', 'title': 'Otomatik Öneri', 'desc': '"Parametrik test kullanılabilir" veya "Non-parametrik test önerilir" kararı otomatik verilir.'},
            ],
        })

    if request.method == 'POST':
        return _handle_group_tool_post(request, 'normallik')

    active_job = _get_active_job(request.user, 'normallik')
    return render(request, 'istatistik/normallik.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': 'Normallik Testi',
        'tool_icon': 'bi-activity',
        'tool_color': 'warning',
        'tool_description': 'Shapiro-Wilk testi, çarpıklık/basıklık ve Q-Q plot ile değişkenlerinizin normal dağılıma uygunluğunu test edin.',
        'tool_hints': [
            'Her sütun ayrı bir değişken olarak analiz edilir.',
            'Shapiro-Wilk testi N ≤ 5000 için; üzerinde D\'Agostino-Pearson kullanılır.',
            'p ≥ 0.05 → normal dağılım varsayımı reddedilemez.',
            'Hem istatistiksel hem görsel (Q-Q plot) sonuçlar PDF\'e eklenir.',
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
            'promo_title': 'Betimleyici İstatistik Raporu',
            'promo_icon': 'bi-clipboard2-data',
            'promo_color': 'success',
            'promo_description': 'Verinizi yükleyin; frekans tabloları, ortalama, standart sapma ve grafikler otomatik oluşsun. Tez bulgular bölümünüzün ilk sayfası hazır.',
            'promo_features': [
                {'icon': 'bi-list-ol', 'title': 'Frekans Tabloları', 'desc': 'Kategorik değişkenler için frekans ve yüzde dağılım tabloları otomatik oluşturulur.'},
                {'icon': 'bi-calculator-fill', 'color': 'primary', 'title': 'Merkezi Eğilim', 'desc': 'Sürekli değişkenler için n, ortalama, standart sapma, min, max, medyan, Q1-Q3 hesaplanır.'},
                {'icon': 'bi-bar-chart-fill', 'title': 'Otomatik Grafikler', 'desc': 'Kategorik değişkenler için çubuk grafik, sürekli değişkenler için histogram PDF\'e eklenir.'},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': 'Hazır PDF Rapor', 'desc': 'Tüm tablolar ve grafikler düzenli formatta PDF olarak indirilir.'},
            ],
        })

    if request.method == 'POST':
        return _handle_group_tool_post(request, 'betimsel')

    active_job = _get_active_job(request.user, 'betimsel')
    return render(request, 'istatistik/betimsel.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': 'Betimleyici İstatistik Raporu',
        'tool_icon': 'bi-clipboard2-data',
        'tool_color': 'success',
        'tool_description': 'Verinizdeki her sütun için frekans tabloları, merkezi eğilim ölçüleri ve grafikler otomatik oluşturulur.',
        'tool_hints': [
            'Kategorik değişkenler (≤10 farklı değer veya metin) → frekans tablosu + çubuk grafik.',
            'Sürekli sayısal değişkenler → ortalama, SS, medyan, Q1-Q3 + histogram.',
            'Başlık satırı otomatik algılanır.',
            'Boş hücreler (NA) değişken bazında çıkarılır.',
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
            'promo_title': 'Korelasyon Matrisi',
            'promo_icon': 'bi-grid-3x3',
            'promo_color': 'info',
            'promo_description': 'Değişkenleriniz arasındaki ilişkileri tek bakışta görün. Pearson, Spearman veya Kendall yöntemiyle p-değerleri ve ısı haritası içeren PDF raporu saniyeler içinde alın.',
            'promo_features': [
                {'icon': 'bi-table', 'title': 'Korelasyon Tablosu', 'desc': 'Tüm değişken çiftleri için r katsayısı ve p-değeri hesaplanır. p < 0.05 anlamlı ilişkiyi gösterir.'},
                {'icon': 'bi-grid-fill', 'color': 'info', 'title': 'Isı Haritası', 'desc': 'Korelasyon katsayıları renk skalasıyla görselleştirilir. Güçlü ilişkiler anında fark edilir.'},
                {'icon': 'bi-sliders', 'title': 'Üç Yöntem', 'desc': 'Pearson (parametrik), Spearman (non-parametrik sıralı) veya Kendall (küçük örneklem) yöntemlerinden seçin.'},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': 'PDF Rapor', 'desc': 'Tablo ve ısı haritası düzenli formatta PDF olarak indirilir.'},
            ],
        })

    if request.method == 'POST':
        return _handle_group_tool_post(request, 'korelasyon')

    active_job = _get_active_job(request.user, 'korelasyon')
    return render(request, 'istatistik/korelasyon.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': 'Korelasyon Matrisi',
        'tool_icon': 'bi-grid-3x3',
        'tool_color': 'info',
        'tool_description': 'Değişkenleriniz arasındaki ilişkileri Pearson, Spearman veya Kendall yöntemiyle hesaplayın. Her sütun bir değişken, her satır bir gözlem olmalıdır.',
        'tool_hints': [
            'Her sütun bir değişkeni temsil etmelidir.',
            'Pearson: normal dağılımlı sürekli veriler için.',
            'Spearman: sıralı veriler veya normallik varsayımı sağlanmıyorsa.',
            'Kendall: küçük örneklem veya çok sayıda bağlı sıra olduğunda.',
        ],
        **_console_ctx('korelasyon', request),
    })


@feature_required
def orneklem_landing(request):
    if request.method == 'POST':
        return _handle_orneklem_calc(request)
    return render(request, 'istatistik/orneklem.html', {
        'tool_title': 'Örneklem Büyüklüğü Hesaplayıcı',
        **_console_ctx('orneklem', request),
    })


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def ttesti_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('ttesti'),
            'promo_title': 't-Testi',
            'promo_icon': 'bi-distribute-horizontal',
            'promo_color': 'purple',
            'promo_description': 'İki grup arasındaki ortalama farkını test edin. Bağımsız veya bağımlı örneklem t-testi, Cohen\'s d etki büyüklüğü ve %95 güven aralığı ile PDF raporu alın.',
            'promo_features': [
                {'icon': 'bi-people-fill', 'title': 'Bağımsız Örneklem', 'desc': 'Farklı iki grubun ortalamalarını karşılaştırın. Levene testi ile varyans homojenliği otomatik kontrol edilir.'},
                {'icon': 'bi-arrow-left-right', 'title': 'Bağımlı Örneklem', 'desc': 'Aynı gruba ait iki ölçüm arasındaki farkı test edin (öntest-sontest, eşleştirilmiş).'},
                {'icon': 'bi-rulers', 'title': 'Etki Büyüklüğü', 'desc': 'Cohen\'s d katsayısı ve %95 güven aralığı otomatik hesaplanır.'},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': 'PDF Rapor', 'desc': 'Grup istatistikleri ve test sonuçları düzenli tablolar halinde PDF\'e aktarılır.'},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'ttesti')
    return render(request, 'istatistik/ttesti.html', {
        'active_job_id': str(_get_active_job(request.user, 'ttesti').id) if _get_active_job(request.user, 'ttesti') else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': 't-Testi',
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
            'promo_title': 'Tek Yönlü ANOVA',
            'promo_icon': 'bi-bar-chart-steps',
            'promo_color': 'danger',
            'promo_description': 'Üç veya daha fazla grubun ortalamalarını karşılaştırın. Tukey/Bonferroni post-hoc testleri ve η² etki büyüklüğü ile tam bir ANOVA raporu alın.',
            'promo_features': [
                {'icon': 'bi-bar-chart-fill', 'title': 'Tek Yönlü ANOVA', 'desc': 'F istatistiği, serbestlik dereceleri ve p-değeri otomatik hesaplanır.'},
                {'icon': 'bi-search', 'color': 'warning', 'title': 'Post-Hoc Testler', 'desc': 'Hangi gruplar arasında fark var? Tukey veya Bonferroni post-hoc testi ile belirleyin.'},
                {'icon': 'bi-rulers', 'title': 'Etki Büyüklüğü', 'desc': 'Eta-kare (η²) ile etki büyüklüğü raporlanır.'},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': 'PDF Rapor', 'desc': 'Grup istatistikleri, ANOVA tablosu ve post-hoc sonuçları PDF\'e aktarılır.'},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'anova')
    return render(request, 'istatistik/anova.html', {
        'active_job_id': str(_get_active_job(request.user, 'anova').id) if _get_active_job(request.user, 'anova') else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': 'Tek Yönlü ANOVA',
        'tool_icon': 'bi-bar-chart-steps',
        'tool_color': 'danger',
        **_console_ctx('anova', request),
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
                return JsonResponse({'error': 'Oturum verisi bulunamadı. Lütfen dosyayı tekrar yükleyin.'}, status=400)
            content, original_filename = stored
        elif file:
            if not file.name.lower().endswith(('.csv', '.xlsx', '.xls')):
                return JsonResponse({'error': 'CSV veya Excel dosyası yükleyin.'}, status=400)
            if file.size > django_settings.MAX_UPLOAD_SIZE:
                return JsonResponse({'error': 'Dosya boyutu 5 MB sınırını aşıyor.'}, status=400)
            content = file.read()
            original_filename = file.name
        else:
            return JsonResponse({'error': 'Dosya seçilmedi.'}, status=400)

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

        return JsonResponse({
            'success': True,
            'preview_id': preview_id,
            'filename': original_filename,
            'columns': all_cols,
            'numeric_cols': numeric_cols,
            'n_rows': len(df),
        })

    elif step == 'run':
        if request.user.is_authenticated:
            remaining = _daily_remaining(request.user)
            if remaining <= 0:
                return JsonResponse({'error': 'Günlük analiz limitiniz doldu.'}, status=429)
            if not request.user.profile.email_verified:
                return JsonResponse({'error': 'E-posta doğrulaması gereklidir.'}, status=403)

        preview_id = request.POST.get('preview_id', '')
        filename = request.POST.get('filename', 'dosya')
        from .services.job_runner import _pending_file_contents, store_file_content

        content = _pending_file_contents.pop('preview_' + preview_id, None)
        if content is None:
            return JsonResponse({'error': 'Önizleme süresi doldu. Lütfen dosyayı tekrar yükleyin.'}, status=400)

        if tool == 'ttesti':
            options = {
                'test_type': request.POST.get('test_type', 'independent'),
                'group_col': request.POST.get('group_col', ''),
                'dep_col': request.POST.get('dep_col', ''),
                'col1': request.POST.get('col1', ''),
                'col2': request.POST.get('col2', ''),
            }
        elif tool == 'anova':
            options = {
                'group_col': request.POST.get('group_col', ''),
                'dep_col': request.POST.get('dep_col', ''),
                'posthoc': request.POST.get('posthoc', 'tukey'),
            }
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
        from .services.job_runner import run_job
        store_file_content(str(job.id), content)
        run_job(str(job.id))
        return JsonResponse({'success': True, 'job_id': str(job.id)})

    return JsonResponse({'error': 'Geçersiz adım.'}, status=400)


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def mann_whitney_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('mann_whitney'),
            'promo_title': 'Mann-Whitney U Testi',
            'promo_icon': 'bi-distribute-horizontal',
            'promo_color': 'warning',
            'promo_description': 'İki bağımsız grubun dağılımını karşılaştırın. Normallik varsayımı gerekmez. Medyan farkı, sıra ortalamaları ve rank-biserial etki büyüklüğü ile PDF raporu alın.',
            'promo_features': [
                {'icon': 'bi-people-fill', 'title': 'Non-Parametrik', 'desc': 'Normallik varsayımı sağlanmadığında t-testine güçlü bir alternatif.'},
                {'icon': 'bi-bar-chart-line', 'title': 'Sıra Analizi', 'desc': 'Medyanlar ve ortalama sıralar raporlanır.'},
                {'icon': 'bi-rulers', 'title': 'Etki Büyüklüğü', 'desc': 'Rank-biserial korelasyon (r) ile etki büyüklüğü hesaplanır.'},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': 'PDF Rapor', 'desc': 'Sonuçlar düzenli tablolar halinde PDF olarak indirilir.'},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'mann_whitney')
    active_job = _get_active_job(request.user, 'mann_whitney')
    return render(request, 'istatistik/mann_whitney.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': 'Mann-Whitney U Testi',
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
            'promo_title': 'Kruskal-Wallis H Testi',
            'promo_icon': 'bi-bar-chart-steps',
            'promo_color': 'teal',
            'promo_description': 'Üç veya daha fazla bağımsız grubun dağılımını non-parametrik olarak karşılaştırın. Bonferroni düzeltmeli post-hoc testleri ve η² etki büyüklüğü ile PDF raporu alın.',
            'promo_features': [
                {'icon': 'bi-bar-chart-fill', 'title': '3+ Grup', 'desc': 'ANOVA\'nın parametrik olmayan alternatifi. Normallik gerekmez.'},
                {'icon': 'bi-search', 'color': 'warning', 'title': 'Post-Hoc', 'desc': 'Anlamlı fark bulunursa çiftli Mann-Whitney U + Bonferroni düzeltmesi uygulanır.'},
                {'icon': 'bi-rulers', 'title': 'Etki Büyüklüğü', 'desc': 'Eta-kare (η²) ile etki büyüklüğü raporlanır.'},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': 'PDF Rapor', 'desc': 'Grup istatistikleri ve post-hoc sonuçları PDF\'e aktarılır.'},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'kruskal_wallis')
    active_job = _get_active_job(request.user, 'kruskal_wallis')
    return render(request, 'istatistik/kruskal_wallis.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': 'Kruskal-Wallis H Testi',
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
            'promo_title': 'Ki-Kare Testi',
            'promo_icon': 'bi-grid-3x3',
            'promo_color': 'purple',
            'promo_description': 'İki kategorik değişken arasındaki ilişkiyi test edin. Çapraz tablo ve Cramér\'s V etki büyüklüğü ile PDF raporu alın.',
            'promo_features': [
                {'icon': 'bi-grid-3x3', 'title': 'Bağımsızlık Testi', 'desc': 'Pearson\'s Ki-Kare testi ile iki kategorik değişken arasındaki ilişki sınanır.'},
                {'icon': 'bi-table', 'color': 'info', 'title': 'Çapraz Tablo', 'desc': 'Gözlenen frekanslar ve satır/sütun toplamları ile tam çapraz tablo.'},
                {'icon': 'bi-rulers', 'title': 'Cramér\'s V', 'desc': 'Etki büyüklüğü V katsayısı ile ilişkinin gücü raporlanır.'},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': 'PDF Rapor', 'desc': 'APA formatında raporlanabilir sonuçlar PDF olarak indirilir.'},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'ki_kare')
    active_job = _get_active_job(request.user, 'ki_kare')
    return render(request, 'istatistik/ki_kare.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': 'Ki-Kare Testi',
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
            'promo_title': 'Çoklu Doğrusal Regresyon',
            'promo_icon': 'bi-graph-up-arrow',
            'promo_color': 'primary',
            'promo_description': 'Bir veya birden fazla bağımsız değişkenin sürekli bir bağımlı değişkeni ne kadar açıkladığını analiz edin. R², F testi, standardize beta ve VIF dahil tam OLS regresyon raporu.',
            'promo_features': [
                {'icon': 'bi-graph-up-arrow', 'title': 'OLS Regresyon', 'desc': 'R², düzeltilmiş R², F istatistiği ve model anlamlılığı otomatik hesaplanır.'},
                {'icon': 'bi-table', 'color': 'info', 'title': 'Katsayı Tablosu', 'desc': 'Her yordayıcı için B, β (standardize), SE, t, p ve %95 güven aralığı raporlanır.'},
                {'icon': 'bi-exclamation-triangle', 'color': 'warning', 'title': 'VIF (Çoklu Bağlantı)', 'desc': 'Variance Inflation Factor ile çoklu bağlantı sorunu kontrol edilir.'},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': 'PDF Rapor', 'desc': 'APA formatında raporlanabilir sonuçlar PDF olarak indirilir.'},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'lineer_regresyon')
    active_job = _get_active_job(request.user, 'lineer_regresyon')
    return render(request, 'istatistik/lineer_regresyon.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': 'Çoklu Doğrusal Regresyon',
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
            'promo_title': 'Lojistik Regresyon',
            'promo_icon': 'bi-diagram-3',
            'promo_color': 'success',
            'promo_description': 'İkili (binary) bir sonuç değişkenini yordayın. Odds Ratio, Nagelkerke R² ve sınıflandırma tablosu ile tam lojistik regresyon raporu.',
            'promo_features': [
                {'icon': 'bi-toggles', 'title': 'Binary Sonuç', 'desc': '0/1 veya iki kategorili bağımlı değişken ile çalışır. Kategorik yordayıcılar otomatik dummy\'e dönüştürülür.'},
                {'icon': 'bi-table', 'color': 'info', 'title': 'Odds Ratio', 'desc': 'Her yordayıcı için B, SE, Wald, p ve Exp(B) = Odds Ratio %95 GA ile raporlanır.'},
                {'icon': 'bi-check2-square', 'color': 'warning', 'title': 'Sınıflandırma', 'desc': 'Model doğruluğu ve sınıflandırma tablosu (TP, TN, FP, FN) gösterilir.'},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': 'PDF Rapor', 'desc': 'Nagelkerke R², model χ² ve APA formatında raporlanabilir sonuçlar PDF olarak indirilir.'},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'lojistik_regresyon')
    active_job = _get_active_job(request.user, 'lojistik_regresyon')
    return render(request, 'istatistik/lojistik_regresyon.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': 'Lojistik Regresyon',
        'tool_icon': 'bi-diagram-3',
        'tool_color': 'success',
        **_console_ctx('lojistik_regresyon', request),
    })


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def karar_agaci_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('karar_agaci'),
            'promo_title': 'Karar Ağacı Sınıflandırması',
            'promo_icon': 'bi-diagram-2',
            'promo_color': 'purple',
            'promo_description': 'Veri setinizdeki kategorik hedef değişkeni sınıflandırın. Özellik önemi, confusion matrix ve ağaç yapısı görselleştirmesiyle tam ML raporu.',
            'promo_features': [
                {'icon': 'bi-diagram-2', 'title': 'Ağaç Modeli', 'desc': 'Gini veya Entropy kriteri ile karar ağacı eğitilir. Maksimum derinliği kendiniz belirleyebilirsiniz.'},
                {'icon': 'bi-bar-chart-steps', 'color': 'warning', 'title': 'Özellik Önemi', 'desc': 'Hangi değişkenin sınıflandırmaya en çok katkı yaptığı sıralı tablo ile gösterilir.'},
                {'icon': 'bi-grid-3x3', 'color': 'info', 'title': 'Confusion Matrix', 'desc': 'Test seti üzerindeki doğruluk, kesinlik, duyarlılık ve F1 skoru raporlanır.'},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': 'PDF Rapor', 'desc': 'Ağaç yapısı, metrikler ve APA formatında raporlama cümlesi PDF olarak indirilir.'},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'karar_agaci')
    active_job = _get_active_job(request.user, 'karar_agaci')
    return render(request, 'istatistik/karar_agaci.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': 'Karar Ağacı Sınıflandırması',
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
            'promo_title': 'Destek Vektör Makinesi (SVM)',
            'promo_icon': 'bi-cpu',
            'promo_color': 'teal',
            'promo_description': 'Veri setinizdeki kategorik hedef değişkeni yüksek doğrulukla sınıflandırın. RBF, Doğrusal ve Polinom kernel seçenekleriyle confusion matrix ve permutation importance dahil tam ML raporu.',
            'promo_features': [
                {'icon': 'bi-cpu', 'title': 'SVM Modeli', 'desc': 'RBF, Doğrusal veya Polinom kernel ve C düzenleme parametresiyle Destek Vektör Makinesi eğitilir.'},
                {'icon': 'bi-bar-chart-steps', 'color': 'warning', 'title': 'Permutation Importance', 'desc': 'Her değişkenin sınıflandırmaya gerçek katkısı permütasyon yöntemiyle hesaplanır ve sıralanır.'},
                {'icon': 'bi-grid-3x3', 'color': 'info', 'title': 'Confusion Matrix', 'desc': 'Test seti üzerindeki doğruluk, kesinlik, duyarlılık ve F1 skoru raporlanır.'},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': 'PDF Rapor', 'desc': 'Metrikler, confusion matrix ve APA formatında raporlama cümlesi PDF olarak indirilir.'},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'svm')
    active_job = _get_active_job(request.user, 'svm')
    return render(request, 'istatistik/svm.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': 'Destek Vektör Makinesi (SVM)',
        'tool_icon': 'bi-cpu',
        'tool_color': 'teal',
        **_console_ctx('svm', request),
    })


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def afa_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('afa'),
            'promo_title': 'Açıklayıcı Faktör Analizi (AFA)',
            'promo_icon': 'bi-diagram-2',
            'promo_color': 'info',
            'promo_description': 'Ölçek geçerliğini kanıtlayın. KMO, Bartlett testi, faktör yük matrisi ve açıklanan varyans tablosu ile tam AFA raporu.',
            'promo_features': [
                {'icon': 'bi-grid-3x3', 'title': 'Faktör Yapısı', 'desc': 'Varimax rotasyonlu faktör yük matrisi ile her maddenin hangi faktöre yüklendiğini görün.'},
                {'icon': 'bi-bar-chart-steps', 'color': 'warning', 'title': 'KMO & Bartlett', 'desc': 'Örneklem yeterliliği (KMO) ve Bartlett küresellik testi ile faktör analizine uygunluğu sınayın.'},
                {'icon': 'bi-percent', 'color': 'success', 'title': 'Açıklanan Varyans', 'desc': 'Her faktörün açıkladığı varyans yüzdesi ve kümülatif varyans tablosu.'},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': 'PDF Rapor', 'desc': 'APA formatında raporlanabilir tablo ve yorum içeren PDF indirilir.'},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'afa')
    active_job = _get_active_job(request.user, 'afa')
    return render(request, 'istatistik/afa.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        'tool_title': 'Açıklayıcı Faktör Analizi (AFA)',
        'tool_icon': 'bi-diagram-2',
        'tool_color': 'info',
        'tool_description': 'Ölçek geçerliğini sınayın. Her sütun bir madde, her satır bir katılımcı olmalıdır.',
        'tool_hints': [
            'Her sütun bir ölçek maddesi olmalıdır (örn. M1, M2…).',
            'Tüm sütunlar sayısal olmalıdır (Likert vb.).',
            'Faktör sayısı otomatik belirlenir (özdeğer > 1 kuralı).',
            'En az 3 madde ve 10 katılımcı gereklidir.',
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
            'promo_title': 'Wilcoxon İşaret Testi',
            'promo_icon': 'bi-arrow-left-right',
            'promo_color': 'warning',
            'promo_description': 'İki bağımlı (eşleştirilmiş) ölçümü karşılaştırın. Bağımlı t-testinin parametrik olmayan alternatifi.',
            'promo_features': [
                {'icon': 'bi-bar-chart-steps', 'title': 'W İstatistiği', 'desc': 'Wilcoxon W istatistiği ve p değeri ile iki ölçüm arasındaki farkı sınayın.'},
                {'icon': 'bi-arrows-collapse', 'color': 'warning', 'title': 'Etki Büyüklüğü', 'desc': 'Rank-biserial korelasyon (r) ile etki büyüklüğünü hesaplayın.'},
                {'icon': 'bi-table', 'color': 'success', 'title': 'Betimsel Tablo', 'desc': 'Her ölçüm için medyan, ortalama ve fark istatistikleri.'},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': 'PDF Rapor', 'desc': 'APA formatında otomatik rapor cümlesi ve PDF indirme.'},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'wilcoxon')
    active_job = _get_active_job(request.user, 'wilcoxon')
    return render(request, 'istatistik/wilcoxon.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        **_console_ctx('wilcoxon', request),
    })


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def friedman_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('friedman'),
            'promo_title': 'Friedman Testi',
            'promo_icon': 'bi-bar-chart-steps',
            'promo_color': 'success',
            'promo_description': '3 veya daha fazla bağımlı (eşleştirilmiş) ölçümü karşılaştırın. Tekrarlayan ölçümler ANOVA\'nın parametrik olmayan alternatifi.',
            'promo_features': [
                {'icon': 'bi-bar-chart-steps', 'title': 'χ² İstatistiği', 'desc': 'Friedman χ² istatistiği, serbestlik derecesi ve p değeri ile ölçümler arası farkı sınayın.'},
                {'icon': 'bi-rulers', 'color': 'success', 'title': "Kendall's W", 'desc': "Etki büyüklüğü Kendall's W katsayısı ile raporlanır."},
                {'icon': 'bi-diagram-3', 'color': 'warning', 'title': 'Post-Hoc', 'desc': 'Anlamlı bulunursa Bonferroni düzeltmeli pairwise Wilcoxon karşılaştırmaları.'},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': 'PDF Rapor', 'desc': 'APA formatında hazır raporlama cümlesi ve PDF indirme.'},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'friedman')
    active_job = _get_active_job(request.user, 'friedman')
    return render(request, 'istatistik/friedman.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
        **_console_ctx('friedman', request),
    })


@feature_required
@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def tekrarli_anova_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
            'seo_guide': SEO_CONTENT.get('tekrarli_anova'),
            'promo_title': 'Tekrarlayan Ölçümler ANOVA',
            'promo_icon': 'bi-graph-up-arrow',
            'promo_color': 'primary',
            'promo_description': 'Aynı katılımcıların 3+ farklı koşulda/zamanda ölçüldüğü verileri analiz edin. F istatistiği, η² etki büyüklüğü ve Bonferroni post-hoc ile PDF raporu alın.',
            'promo_features': [
                {'icon': 'bi-graph-up-arrow', 'title': 'F İstatistiği', 'desc': 'Tekrarlayan ölçümler ANOVA ile F istatistiği, serbestlik derecesi ve p değeri hesaplanır.'},
                {'icon': 'bi-rulers', 'color': 'primary', 'title': 'Etki Büyüklüğü (η²)', 'desc': 'Partial eta-squared (η²) ile etki büyüklüğü raporlanır.'},
                {'icon': 'bi-diagram-3', 'color': 'warning', 'title': 'Post-Hoc', 'desc': 'Bonferroni düzeltmeli bağımlı t-testi ile hangi ölçüm çiftlerinin farklılaştığı belirlenir.'},
                {'icon': 'bi-file-earmark-pdf-fill', 'color': 'danger', 'title': 'PDF Rapor', 'desc': 'ANOVA tablosu, post-hoc ve APA formatında otomatik raporlama cümlesi.'},
            ],
        })
    if request.method == 'POST':
        return _handle_group_tool_post(request, 'tekrarli_anova')
    active_job = _get_active_job(request.user, 'tekrarli_anova')
    return render(request, 'istatistik/tekrarli_anova.html', {
        'active_job_id': str(active_job.id) if active_job else None,
        'daily_remaining': _daily_remaining(request.user),
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
        return JsonResponse({'error': 'Dosya seçilmedi.'}, status=400)
    if not file.name.lower().endswith(('.csv', '.xlsx', '.xls')):
        return JsonResponse({'error': 'CSV veya Excel dosyası yükleyin.'}, status=400)
    if file.size > django_settings.MAX_UPLOAD_SIZE:
        return JsonResponse({'error': 'Dosya boyutu 5 MB sınırını aşıyor.'}, status=400)

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
    return render(request, 'istatistik/analiz_hub.html', {
        'tool_categories': TOOL_CATEGORIES,
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
        'karar-agaci': karar_agaci_landing,
        'svm': svm_landing,
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
        return JsonResponse({'error': f'Hesaplama hatası: {e}'}, status=500)


@require_GET
def job_status(request, job_id):
    """AJAX polling: job durumu + sonuç."""
    filters = {'id': job_id}
    if request.user.is_authenticated:
        filters['user'] = request.user

    job = get_object_or_404(IstatistikJob, **filters)

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
            msg = 'Günlük analiz limitiniz doldu.'
            return JsonResponse({'error': msg}, status=429) if is_ajax else \
                   JsonResponse({'error': msg}, status=429)

        if not request.user.profile.email_verified:
            msg = 'E-posta doğrulaması gereklidir.'
            return JsonResponse({'error': msg}, status=403)

    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': 'Dosya seçilmedi.'}, status=400)

    allowed_ext = ('.csv', '.xlsx', '.xls')
    if not file.name.lower().endswith(allowed_ext):
        return JsonResponse({'error': 'Yalnızca CSV veya Excel (.xlsx/.xls) dosyası yükleyebilirsiniz.'}, status=400)

    if file.size > django_settings.MAX_UPLOAD_SIZE:  # 10 MB
        return JsonResponse({'error': 'Dosya boyutu 5 MB sınırını aşıyor.'}, status=400)

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
