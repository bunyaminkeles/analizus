import logging
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages

from .forms import BibliometricUploadForm, BibliometricOrderForm
from .models import BibliometricJob, BibliometricOrder

logger = logging.getLogger(__name__)


def feature_required(flag_name):
    """Feature flag kapalıysa 404 döner."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            from forum.models import SiteSettings
            site = SiteSettings.load()
            if not getattr(site, f'feature_{flag_name}', False):
                raise Http404
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


@login_required
@feature_required('bibliometrics')
def bibliometrics_landing(request):
    user = request.user

    # Email doğrulama kontrolü
    if hasattr(user, 'profile') and not user.profile.email_verified:
        messages.warning(request, 'Bibliometrik analiz kullanmak için e-posta adresinizi doğrulamanız gerekiyor.')
        return redirect('profile_edit')

    daily_limit = BibliometricJob.get_daily_limit(user)
    daily_used = BibliometricJob.daily_count_for_user(user)
    remaining = daily_limit - daily_used

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if remaining <= 0:
            return JsonResponse({
                'status': 'error',
                'error': f'Günlük analiz limitinize ({daily_limit}) ulaştınız. Yarın tekrar deneyiniz.',
            }, status=429)

        form = BibliometricUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            errors = '; '.join(
                f'{field}: {", ".join(errs)}'
                for field, errs in form.errors.items()
            )
            return JsonResponse({'status': 'error', 'error': errors}, status=400)

        uploaded_file = form.cleaned_data['file']
        try:
            file_content = uploaded_file.read().decode('utf-8', errors='replace')
        except Exception as e:
            return JsonResponse({'status': 'error', 'error': f'Dosya okunamadı: {e}'}, status=400)

        # Job oluştur
        job = BibliometricJob.objects.create(
            user=user,
            original_filename=uploaded_file.name,
        )

        # Arka planda çalıştır
        from .services.job_runner import run_bibliometric_job
        run_bibliometric_job(str(job.id), file_content)

        return JsonResponse({
            'status': 'started',
            'job_id': str(job.id),
            'remaining': remaining - 1,
            'daily_limit': daily_limit,
        })

    # Son 10 analiz (geçmiş)
    recent_jobs = BibliometricJob.objects.filter(user=user).order_by('-created_at')[:10]

    return render(request, 'bibliometrics/landing.html', {
        'daily_limit': daily_limit,
        'daily_used': daily_used,
        'remaining': remaining,
        'recent_jobs': recent_jobs,
        'form': BibliometricUploadForm(),
    })


@login_required
@feature_required('bibliometrics')
@require_GET
def bibliometrics_job_status(request, job_id):
    job = get_object_or_404(BibliometricJob, id=job_id, user=request.user)
    data = {
        'status': job.status,
        'total_records': job.total_records,
        'file_format': job.get_file_format_display() if job.file_format else '',
    }
    if job.status == 'failed':
        data['error'] = job.error_message
    elif job.status == 'completed':
        data['demo_pdf_url'] = job.demo_pdf_url
        data['demo_email_sent'] = job.demo_email_sent
        data['has_order'] = job.orders.filter(
            status__in=['pending_payment', 'payment_review', 'approved', 'processing', 'completed']
        ).exists()
    return JsonResponse(data)


@login_required
@feature_required('bibliometrics')
@require_POST
def bibliometrics_send_demo(request, job_id):
    job = get_object_or_404(BibliometricJob, id=job_id, user=request.user)

    if job.status != 'completed':
        return JsonResponse({'status': 'error', 'error': 'Analiz henüz tamamlanmadı.'}, status=400)

    if job.demo_email_sent:
        return JsonResponse({'status': 'already_sent', 'message': 'Demo rapor daha önce gönderildi.'})

    if not request.user.email:
        return JsonResponse({'status': 'error', 'error': 'Hesabınızda email adresi tanımlı değil.'}, status=400)

    # Demo PDF'i S3'ten değil, tekrar oluştur (küçük dosya)
    try:
        from .services.analyzer import run_all_analyses
        from .services.pdf_builder import build_demo_pdf
        from .services.parser import parse_file

        # job'ın file_content'i yok (DB'de tutmuyoruz) —
        # S3'te full_pdf_url varsa, demo PDF'i yeniden üretmek yerine
        # sadece URL'yi emaile ekle
        if job.demo_pdf_url:
            # Demo PDF'i yeniden üretmeye gerek yok, S3 URL'si yeterli
            from .services.job_runner import send_demo_email_via_url
            send_demo_email_via_url(str(job.id))
        else:
            return JsonResponse({'status': 'error', 'error': 'Demo PDF oluşturulamamış.'}, status=500)

    except Exception as e:
        logger.error(f'Demo email hatası: {e}')
        return JsonResponse({'status': 'error', 'error': 'Email gönderilemedi.'}, status=500)

    return JsonResponse({'status': 'sent', 'message': f'{request.user.email} adresine demo rapor gönderildi.'})


@login_required
@feature_required('bibliometrics')
def bibliometrics_order_page(request, job_id):
    job = get_object_or_404(BibliometricJob, id=job_id, user=request.user)

    if job.status != 'completed':
        messages.error(request, 'Analiz tamamlanmadan sipariş oluşturamazsınız.')
        return redirect('bibliometrics:landing')

    # Mevcut sipariş var mı?
    existing_order = job.orders.exclude(status='cancelled').first()

    price = BibliometricOrder.calculate_price(job.total_records)

    if request.method == 'POST' and not existing_order:
        form = BibliometricOrderForm(request.POST)
        if form.is_valid():
            BibliometricOrder.objects.create(
                user=request.user,
                job=job,
                total_price=price,
                payment_note=form.cleaned_data.get('payment_note', ''),
            )
            messages.success(request, 'Siparişiniz alındı! Ödeme onayından sonra tam rapor emailinize gönderilecek.')
            return redirect('bibliometrics:order_page', job_id=job_id)
    else:
        form = BibliometricOrderForm()

    # Fiyat kırılımı (template için)
    import math
    price_breakdown = [('İlk 500 kayıt', 500)]
    if job.total_records > 500:
        extra = math.ceil((job.total_records - 500) / 500)
        for i in range(1, extra + 1):
            start = 500 * i + 1
            end   = 500 * (i + 1)
            price_breakdown.append((f'{start:,}–{end:,}. kayıtlar', 400))

    return render(request, 'bibliometrics/order.html', {
        'job': job,
        'existing_order': existing_order,
        'form': form,
        'price': price,
        'price_breakdown': price_breakdown,
    })
