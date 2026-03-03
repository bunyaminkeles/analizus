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

        # Çoklu dosya desteği: tüm yüklenen dosyaları al
        from .forms import _validate_file
        uploaded_files = request.FILES.getlist('file')
        if not uploaded_files:
            return JsonResponse({'status': 'error', 'error': 'Dosya seçilmedi.'}, status=400)

        file_contents = []
        filenames = []
        for uf in uploaded_files:
            try:
                _validate_file(uf)
                content = uf.read().decode('utf-8', errors='replace')
                file_contents.append(content)
                filenames.append(uf.name)
            except Exception as e:
                return JsonResponse({'status': 'error', 'error': f'{uf.name}: {e}'}, status=400)

        original_filename = ', '.join(filenames) if len(filenames) > 1 else filenames[0]

        # Job oluştur
        job = BibliometricJob.objects.create(
            user=user,
            original_filename=original_filename[:255],
        )

        # Arka planda çalıştır (çoklu dosya içerikleri birleştirilecek)
        from .services.job_runner import run_bibliometric_job
        run_bibliometric_job(str(job.id), file_contents)

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
        price = BibliometricOrder.calculate_price(job.total_records)
        data['price'] = price
        data['contact_admin'] = price is None  # 5000+ kayıt
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
@require_POST
def bibliometrics_from_openalex(request, alex_job_id):
    """
    OpenAlex arama sonuçlarından bibliometrik analiz başlat.
    Kullanıcı en az 100 sonuçlu bir AlexSearchJob'a sahip olmalıdır.
    """
    from openalex.models import AlexSearchJob

    user = request.user

    if hasattr(user, 'profile') and not user.profile.email_verified:
        return JsonResponse({'status': 'error', 'error': 'E-posta doğrulaması gereklidir.'}, status=403)

    daily_limit = BibliometricJob.get_daily_limit(user)
    daily_used = BibliometricJob.daily_count_for_user(user)
    if daily_used >= daily_limit:
        return JsonResponse(
            {'status': 'error', 'error': f'Günlük analiz limitinize ({daily_limit}) ulaştınız.'},
            status=429,
        )

    alex_job = get_object_or_404(AlexSearchJob, id=alex_job_id, user=user)

    if alex_job.status != 'completed':
        return JsonResponse(
            {'status': 'error', 'error': 'OpenAlex araması henüz tamamlanmadı.'}, status=400
        )

    if alex_job.total_results < 100:
        return JsonResponse(
            {
                'status': 'error',
                'error': (
                    f'Bibliometrik analiz için en az 100 sonuç gereklidir '
                    f'(bulunan: {alex_job.total_results}).'
                ),
            },
            status=400,
        )

    if not alex_job.all_results:
        return JsonResponse(
            {'status': 'error', 'error': 'OpenAlex verisi bulunamadı.'}, status=400
        )

    # Aynı OpenAlex araması için başarılı/devam eden bir analiz var mı?
    existing = BibliometricJob.objects.filter(
        alex_job=alex_job, user=user
    ).exclude(status='failed').first()
    if existing:
        return JsonResponse({
            'status': 'exists',
            'job_id': str(existing.id),
            'job_status': existing.status,
            'message': 'Bu arama için zaten bir bibliometrik analiz mevcut.',
        })

    query_summary = alex_job.get_query_summary()
    job = BibliometricJob.objects.create(
        user=user,
        original_filename=f'OpenAlex: {query_summary}'[:255],
        source='openalex',
        alex_job=alex_job,
    )

    from .services.job_runner import run_bibliometric_job_from_openalex
    run_bibliometric_job_from_openalex(str(job.id))

    return JsonResponse({
        'status': 'started',
        'job_id': str(job.id),
        'message': 'Bibliometrik analiz başlatıldı.',
    })


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
