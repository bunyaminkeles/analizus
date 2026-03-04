import logging
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import TezAnaliz

logger = logging.getLogger(__name__)


@login_required
def tezanaliz_landing(request):
    """
    Tez & Makale Analizi ana sayfası.
    YÖK Tez arama formu + sonuçlar (indir / analiz yap) + geçmiş analizler.
    Form POST'u /yoktez/ AJAX endpoint'ine gider.
    """
    from yoktez.forms import YokTezSearchForm
    from yoktez.models import YokTezSearchJob

    user = request.user
    daily_count = YokTezSearchJob.daily_count_for_user(user)
    daily_limit = YokTezSearchJob.get_daily_limit(user)
    remaining = max(0, daily_limit - daily_count)

    form = YokTezSearchForm()
    past_jobs = TezAnaliz.objects.filter(user=user).order_by('-created_at')[:8]

    context = {
        'form': form,
        'remaining': remaining,
        'daily_limit': daily_limit,
        'past_jobs': past_jobs,
    }
    return render(request, 'tezanaliz/landing.html', context)


@login_required
@require_POST
def create_from_yoktez(request, yok_job_id):
    """
    YÖK Tez aramasından tez analizi başlat.
    POST /tezanaliz/yok/<yok_job_id>/
    """
    from yoktez.models import YokTezSearchJob

    try:
        yok_job = YokTezSearchJob.objects.get(id=yok_job_id, user=request.user)
    except YokTezSearchJob.DoesNotExist:
        return JsonResponse({'error': 'YÖK Tez araması bulunamadı.'}, status=404)

    if yok_job.total_results < 10:
        return JsonResponse(
            {'error': f'Analiz için en az 10 sonuç gereklidir (bulunan: {yok_job.total_results}).'},
            status=400,
        )

    # Günlük limit kontrolü
    limit = TezAnaliz.get_daily_limit(request.user)
    used = TezAnaliz.daily_count_for_user(request.user)
    if used >= limit:
        return JsonResponse(
            {'error': f'Günlük analiz limitinize ({limit}) ulaştınız.'},
            status=429,
        )

    # Mevcut analiz var mı kontrol et (aynı yok_job için)
    existing = TezAnaliz.objects.filter(yok_job=yok_job, user=request.user).first()
    if existing and existing.status in ('pending', 'running'):
        return JsonResponse({'job_id': str(existing.id), 'already_running': True})
    if existing and existing.status == 'completed':
        return JsonResponse({'job_id': str(existing.id), 'already_completed': True})

    # Yeni analiz oluştur
    job = TezAnaliz.objects.create(
        user=request.user,
        yok_job=yok_job,
        tez_ad=yok_job.tez_ad,
        yazar=yok_job.yazar,
        universite=yok_job.universite,
        tur=yok_job.tur,
        yil_baslangic=yok_job.yil_baslangic,
        yil_bitis=yok_job.yil_bitis,
        metin=yok_job.metin,
    )

    from tezanaliz.services.job_runner import run_tezanaliz_job
    run_tezanaliz_job(str(job.id))

    return JsonResponse({'job_id': str(job.id)})


@login_required
def tezanaliz_status(request, job_id):
    """
    Analiz iş durumunu döndür.
    GET /tezanaliz/status/<job_id>/
    """
    job = get_object_or_404(TezAnaliz, id=job_id, user=request.user)
    data = {
        'status': job.status,
        'total_records': job.total_records,
        'pdf_url': job.pdf_url,
        'error': job.error_message,
    }
    return JsonResponse(data)


@login_required
def tezanaliz_results(request, job_id):
    """
    Analiz sonuç sayfası.
    GET /tezanaliz/sonuc/<job_id>/
    """
    job = get_object_or_404(TezAnaliz, id=job_id, user=request.user)
    similar = (job.analysis_data or {}).get('similar', [])

    analyses_list = [
        'Tez Türlerine Göre Dağılım (Pasta Grafik)',
        'Yıllara Göre Tez Türü Trendi (Stacked Bar)',
        'Üniversite Bazında Üretkenlik (Top 15)',
        'TF-IDF Anahtar Kelimeler (Başlık + Özet)',
        'Son 5 Yıl Tez Trendi + Büyüme Oranı',
        'LDA Konu Modelleme (Gizli Konular)',
        'Konu & Dizin Terimleri Kelime Bulutu',
    ]
    context = {
        'job': job,
        'similar': similar,
        'analyses_list': analyses_list,
    }
    return render(request, 'tezanaliz/results.html', context)
