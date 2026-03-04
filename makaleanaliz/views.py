import logging
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import MakaleAnaliz

logger = logging.getLogger(__name__)


@login_required
@require_POST
def create_from_dizin(request, dizin_job_id):
    """
    TR Dizin aramasından makale analizi başlat.
    POST /makaleanaliz/dizin/<dizin_job_id>/
    """
    from trdizin.models import DizinSearchJob

    try:
        dizin_job = DizinSearchJob.objects.get(id=dizin_job_id, user=request.user)
    except DizinSearchJob.DoesNotExist:
        return JsonResponse({'error': 'TR Dizin araması bulunamadı.'}, status=404)

    if dizin_job.status != 'completed':
        return JsonResponse(
            {'error': 'Analiz için tamamlanmış bir arama gereklidir.'},
            status=400,
        )

    record_count = len(dizin_job.all_results) if dizin_job.all_results else dizin_job.total_results
    if record_count < 5:
        return JsonResponse(
            {'error': f'Analiz için en az 5 sonuç gereklidir (bulunan: {record_count}).'},
            status=400,
        )

    # Günlük limit kontrolü
    limit = MakaleAnaliz.get_daily_limit(request.user)
    used = MakaleAnaliz.daily_count_for_user(request.user)
    if used >= limit:
        return JsonResponse(
            {'error': f'Günlük analiz limitinize ({limit}) ulaştınız.'},
            status=429,
        )

    # Mevcut analiz var mı kontrol et (aynı dizin_job için)
    existing = MakaleAnaliz.objects.filter(dizin_job=dizin_job, user=request.user).first()
    if existing and existing.status in ('pending', 'running'):
        return JsonResponse({'job_id': str(existing.id), 'already_running': True})
    if existing and existing.status == 'completed':
        return JsonResponse({'job_id': str(existing.id), 'already_completed': True})

    # Yeni analiz oluştur
    job = MakaleAnaliz.objects.create(
        user=request.user,
        dizin_job=dizin_job,
        query_summary=dizin_job.get_query_summary(),
    )

    from makaleanaliz.services.job_runner import run_makaleanaliz_job
    run_makaleanaliz_job(str(job.id))

    return JsonResponse({'job_id': str(job.id)})


@login_required
def makaleanaliz_status(request, job_id):
    """
    Analiz iş durumunu döndür.
    GET /makaleanaliz/status/<job_id>/
    """
    job = get_object_or_404(MakaleAnaliz, id=job_id, user=request.user)
    data = {
        'status': job.status,
        'total_records': job.total_records,
        'pdf_url': job.pdf_url,
        'error': job.error_message,
    }
    return JsonResponse(data)


@login_required
def makaleanaliz_results(request, job_id):
    """
    Analiz sonuç sayfası.
    GET /makaleanaliz/sonuc/<job_id>/
    """
    job = get_object_or_404(MakaleAnaliz, id=job_id, user=request.user)
    similar = (job.analysis_data or {}).get('similar', [])

    analyses_list = [
        'Yayın Türü Dağılımı (Pasta Grafik)',
        'Yıl × Yayın Türü Trendi (Stacked Bar)',
        'Dergi Bazında Üretkenlik (Top 15)',
        'TF-IDF Anahtar Kelimeler (Başlık + Özet)',
        'Son 5 Yıl Yayın Trendi + Büyüme Oranı',
        'LDA Konu Modelleme (Gizli Konular)',
        'Anahtar Kelime Bulutu',
    ]
    context = {
        'job': job,
        'similar': similar,
        'analyses_list': analyses_list,
    }
    return render(request, 'makaleanaliz/results.html', context)
