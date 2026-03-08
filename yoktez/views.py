from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from django.http import Http404
from functools import wraps

from .forms import YokTezSearchForm
from .models import YokTezSearchJob


def feature_required(flag_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            from forum.models import SiteSettings
            site = SiteSettings.load()
            if not getattr(site, f'feature_{flag_name}', True):
                raise Http404
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


@feature_required('yoktez')
@login_required
def yoktez_landing(request):
    user = request.user
    daily_count = YokTezSearchJob.daily_count_for_user(user)
    daily_limit = YokTezSearchJob.get_daily_limit(user)
    remaining = max(0, daily_limit - daily_count)

    if request.method == 'POST':
        form = YokTezSearchForm(request.POST)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if not user.profile.email_verified:
            if is_ajax:
                return JsonResponse({'error': 'E-posta doğrulaması gereklidir.'}, status=403)
            return render(request, 'yoktez/landing.html', {
                'form': form, 'remaining': remaining, 'daily_limit': daily_limit,
                'error': 'E-posta doğrulaması gereklidir.',
            })

        if remaining <= 0:
            msg = (f'Günlük arama limitiniz doldu ({daily_limit}/{daily_limit}). '
                   f'{"Premium üyelikle 7 aramaya yükseltebilirsiniz." if not user.profile.is_premium else "Yarın tekrar deneyebilirsiniz."}')
            if is_ajax:
                return JsonResponse({'error': msg}, status=429)
            return render(request, 'yoktez/landing.html', {
                'form': form, 'remaining': 0, 'daily_limit': daily_limit, 'error': msg,
            })

        if form.is_valid():
            cd = form.cleaned_data
            job = YokTezSearchJob.objects.create(
                user=user,
                tez_ad=cd.get('tez_ad', ''),
                yazar=cd.get('yazar', ''),
                danisman=cd.get('danisman', ''),
                universite=cd.get('universite', ''),
                tur=cd.get('tur', '0'),
                yil_baslangic=cd.get('yil_baslangic'),
                yil_bitis=cd.get('yil_bitis'),
                metin=cd.get('metin', ''),
            )

            from .services.job_runner import run_yoktez_job
            run_yoktez_job(str(job.id))

            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'job_id': str(job.id),
                    'remaining': remaining - 1,
                })
        else:
            if is_ajax:
                errors = [e for field_errors in form.errors.values() for e in field_errors]
                return JsonResponse({'error': errors[0] if errors else 'Geçersiz form.'}, status=400)

    else:
        form = YokTezSearchForm()

    active_job = YokTezSearchJob.objects.filter(
        user=user,
        status__in=['pending', 'running'],
    ).order_by('-created_at').first()

    return render(request, 'yoktez/landing.html', {
        'form': form,
        'remaining': remaining,
        'daily_limit': daily_limit,
        'active_job_id': str(active_job.id) if active_job else None,
    })


@login_required
@require_GET
def yoktez_job_status(request, job_id):
    from django.shortcuts import get_object_or_404
    job = get_object_or_404(YokTezSearchJob, id=job_id, user=request.user)

    resp = {'status': job.status, 'total_results': job.total_results}
    if job.status == 'completed':
        resp['demo_results'] = job.demo_results[:5]
        resp['all_results_file_url'] = job.all_results_file_url
    elif job.status == 'failed':
        resp['error'] = job.error_message
    return JsonResponse(resp)


@login_required
@require_GET
def yoktez_download(request, job_id):
    """S3'teki TXT dosyasını proxy ile indirtir (tarayıcıda açmaz)."""
    import requests as req_lib
    job = get_object_or_404(YokTezSearchJob, id=job_id, user=request.user)

    if not job.all_results_file_url:
        raise Http404

    try:
        s3_resp = req_lib.get(job.all_results_file_url, timeout=30, stream=True)
        s3_resp.raise_for_status()
    except Exception:
        raise Http404

    filename = f'yoktez_{job.id}.txt'
    response = HttpResponse(
        s3_resp.content,
        content_type='text/plain; charset=utf-8',
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
@require_POST
def yoktez_send_demo_email(request, job_id):
    from django.shortcuts import get_object_or_404
    job = get_object_or_404(YokTezSearchJob, id=job_id, user=request.user)

    if job.status not in ('completed',):
        return JsonResponse({'error': 'Sonuçlar henüz hazır değil.'}, status=400)
    if job.total_results == 0:
        return JsonResponse({'error': 'Arama sonucu bulunamadı, gönderilecek bir şey yok.'}, status=400)
    if job.demo_email_sent:
        return JsonResponse({'error': 'Demo sonuçlar zaten gönderildi.'}, status=400)

    from .services.job_runner import send_demo_email_async
    send_demo_email_async(str(job.id))
    return JsonResponse({'success': True, 'message': f'Sonuçlar {request.user.email} adresine gönderildi.'})


@login_required
@require_POST
def yoktez_cancel(request, job_id):
    """Devam eden taramayı iptal eder."""
    job = get_object_or_404(YokTezSearchJob, id=job_id, user=request.user)
    if job.status in ('pending', 'running'):
        job.status = 'failed'
        job.error_message = 'Kullanıcı tarafından iptal edildi.'
        job.save(update_fields=['status', 'error_message'])
    return JsonResponse({'success': True})
