from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_GET
from django_ratelimit.decorators import ratelimit
from functools import wraps

from .models import IstatistikJob


def feature_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from forum.models import SiteSettings
        site = SiteSettings.load()
        if not getattr(site, 'feature_istatistik', True):
            raise Http404
        return view_func(request, *args, **kwargs)
    return wrapper


PROMO_BASE = {
    'promo_steps': [
        'CSV veya Excel dosyanızı yükleyin.',
        'Analiz otomatik olarak saniyeler içinde tamamlanır.',
        'Sonuçları ekranda görün ve PDF olarak indirin.',
    ],
}


@feature_required
@ratelimit(key='ip', rate='10/h', method='POST', block=True)
def cronbach_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
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
        return _handle_upload(request, 'cronbach')

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
    })


@feature_required
@ratelimit(key='ip', rate='10/h', method='POST', block=True)
def normallik_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
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
        return _handle_upload(request, 'normallik')

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
    })


@feature_required
@ratelimit(key='ip', rate='10/h', method='POST', block=True)
def betimsel_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
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
        return _handle_upload(request, 'betimsel')

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
    })


@feature_required
@ratelimit(key='ip', rate='10/h', method='POST', block=True)
def korelasyon_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
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
        method = request.POST.get('method', 'pearson')
        if method not in ('pearson', 'spearman', 'kendall'):
            method = 'pearson'
        return _handle_upload(request, 'korelasyon', options={'method': method})

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
    })


@feature_required
def orneklem_landing(request):
    if request.method == 'POST':
        return _handle_orneklem_calc(request)
    return render(request, 'istatistik/orneklem.html', {
        'tool_title': 'Örneklem Büyüklüğü Hesaplayıcı',
    })


@feature_required
@ratelimit(key='ip', rate='10/h', method='POST', block=True)
def ttesti_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
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
    })


@feature_required
@ratelimit(key='ip', rate='10/h', method='POST', block=True)
def anova_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
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
    })


def _handle_group_tool_post(request, tool):
    """t-testi ve ANOVA için iki adımlı POST yönetimi.
    Adım 1: 'step=preview' — dosyayı parse et, sütun isimlerini döndür.
    Adım 2: 'step=run'     — sütun seçimiyle job oluştur ve kuyruğa ekle.
    """
    step = request.POST.get('step', 'preview')
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if step == 'preview':
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({'error': 'Dosya seçilmedi.'}, status=400)
        if not file.name.lower().endswith(('.csv', '.xlsx', '.xls')):
            return JsonResponse({'error': 'CSV veya Excel dosyası yükleyin.'}, status=400)
        if file.size > 10 * 1024 * 1024:
            return JsonResponse({'error': 'Dosya 10 MB\'ı aşamaz.'}, status=400)

        content = file.read()
        from .services.job_runner import _parse_file, store_file_content
        import uuid
        try:
            df = _parse_file(content, file.name)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)

        preview_id = str(uuid.uuid4())
        store_file_content('preview_' + preview_id, content)

        numeric_cols = list(df.select_dtypes(include='number').columns)
        all_cols = list(df.columns)

        return JsonResponse({
            'success': True,
            'preview_id': preview_id,
            'filename': file.name,
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
@ratelimit(key='ip', rate='10/h', method='POST', block=True)
def mann_whitney_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
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
    })


@feature_required
@ratelimit(key='ip', rate='10/h', method='POST', block=True)
def kruskal_wallis_landing(request):
    if not request.user.is_authenticated:
        return render(request, 'service_promo.html', {
            **PROMO_BASE,
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
    })


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

    if file.size > 10 * 1024 * 1024:  # 10 MB
        return JsonResponse({'error': 'Dosya boyutu 10 MB\'ı aşamaz.'}, status=400)

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
