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

def _handle_upload(request, tool):
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

    job = IstatistikJob.objects.create(
        user=request.user if request.user.is_authenticated else None,
        tool=tool,
        original_filename=file.name,
        is_demo=not request.user.is_authenticated,
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
