from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from functools import wraps

from .forms import DizinSearchForm, DizinOrderForm
from .models import DizinSearchJob, DizinOrder
from .services.job_runner import run_scraping_job


def feature_required(flag_name):
    """Decorator: SiteSettings'deki feature flag kapalıysa 404 döner."""
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


IBAN_INFO = {
    'hesap_sahibi': 'Bünyamin Keleş',
    'iban': 'TR73 0003 2000 0000 0079 1034 65',
}


@feature_required('trdizin')
@login_required
def trdizin_landing(request):
    """Landing page: gelişmiş arama formu + demo arama."""
    form = DizinSearchForm()
    user = request.user

    daily_count = DizinSearchJob.daily_count_for_user(user)
    daily_limit = DizinSearchJob.get_daily_limit(user)
    remaining = max(0, daily_limit - daily_count)

    if request.method == 'POST':
        form = DizinSearchForm(request.POST)
        if form.is_valid():
            if not user.profile.email_verified:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': 'TR Dizin tarama için e-posta doğrulaması gereklidir. Profil sayfanızdan e-postanızı doğrulayın.'
                    }, status=403)
                return render(request, 'trdizin/landing.html', {
                    'form': form,
                    'error': 'TR Dizin tarama için e-posta doğrulaması gereklidir.',
                    'remaining': remaining,
                    'daily_limit': daily_limit,
                })

            if remaining <= 0:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': f'Günlük demo limitiniz doldu ({daily_limit}/{daily_limit}). '
                                 f'{"Premium üyelikle 7 aramaya yükseltebilirsiniz." if not user.profile.is_premium else "Yarın tekrar deneyebilirsiniz."}'
                    }, status=429)
                return render(request, 'trdizin/landing.html', {
                    'form': form,
                    'error': 'Günlük demo limitiniz doldu.',
                    'remaining': 0,
                    'daily_limit': daily_limit,
                })

            query_parts = form.cleaned_data['query_parts_json']

            job = DizinSearchJob.objects.create(
                user=user,
                query_parts=query_parts,
            )
            run_scraping_job(job.id)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'started',
                    'job_id': str(job.id),
                    'remaining': remaining - 1,
                    'daily_limit': daily_limit,
                })

            return render(request, 'trdizin/landing.html', {
                'form': form,
                'job_id': str(job.id),
                'remaining': remaining - 1,
                'daily_limit': daily_limit,
            })
        else:
            # Form validation hatası
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = form.errors.get('query_parts_json', ['Geçersiz sorgu.'])
                return JsonResponse({'error': errors[0]}, status=400)

    return render(request, 'trdizin/landing.html', {
        'form': form,
        'remaining': remaining,
        'daily_limit': daily_limit,
    })


@login_required
@require_GET
def trdizin_job_status(request, job_id):
    """AJAX: job durumu + demo sonuçlar."""
    job = get_object_or_404(DizinSearchJob, id=job_id, user=request.user)

    response = {
        'status': job.status,
        'total_results': job.total_results,
    }
    if job.status == 'completed':
        response['demo_results'] = job.demo_results[:3]
    elif job.status == 'failed':
        response['error'] = job.error_message

    return JsonResponse(response)


@login_required
@require_POST
def trdizin_send_demo_email(request, job_id):
    """Demo sonuçları kullanıcının kayıtlı emailine gönder."""
    job = get_object_or_404(DizinSearchJob, id=job_id, user=request.user)

    if job.status != 'completed' or not job.demo_results:
        return JsonResponse({'error': 'Sonuçlar henüz hazır değil.'}, status=400)

    if job.demo_email_sent:
        return JsonResponse({'error': 'Demo sonuçlar zaten gönderildi.'}, status=400)

    from .services.job_runner import send_demo_email_async
    send_demo_email_async(job.id)

    return JsonResponse({'success': True, 'message': f'Demo sonuçların {request.user.email} adresine gönderilmesi için işlem başlatıldı.'})


@login_required
def trdizin_order_page(request, job_id):
    """Sipariş sayfası: GET=form göster, POST=sipariş oluştur."""
    job = get_object_or_404(DizinSearchJob, id=job_id, user=request.user)

    if job.status != 'completed' or job.total_results == 0:
        return render(request, 'trdizin/order.html', {
            'job': job,
            'error': 'Bu arama için henüz sonuç yok.',
        })

    # Zaten sipariş var mı?
    existing_order = DizinOrder.objects.filter(search_job=job, user=request.user).first()
    if existing_order:
        return render(request, 'trdizin/order.html', {
            'job': job,
            'existing_order': existing_order,
        })

    if request.method == 'POST':
        form = DizinOrderForm(request.POST)
        if form.is_valid():
            abstract_count = min(form.cleaned_data['abstract_count'], job.total_results)
            price = DizinOrder.calculate_price(abstract_count)

            order = DizinOrder.objects.create(
                user=request.user,
                search_job=job,
                abstract_count=abstract_count,
                total_price=price,
                payment_note=form.cleaned_data.get('payment_note', ''),
                status='pending_payment',
            )
            return render(request, 'trdizin/order.html', {
                'job': job,
                'existing_order': order,
                'success': True,
            })

    return render(request, 'trdizin/order.html', {
        'job': job,
    })


