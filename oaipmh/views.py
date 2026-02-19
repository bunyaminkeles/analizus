import json
import logging
from datetime import timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone

from forum.models import SiteSettings
from .models import University, OAIPMHSearchJob, OAIPMHOrder
from .forms import OAIPMHKeywordForm, OAIPMHBrowseForm, OAIPMHOrderForm
from .services.job_runner import run_scraping_job, send_demo_email_async

logger = logging.getLogger(__name__)

IBAN_INFO = {
    'hesap_sahibi': 'Bünyamin Keleş',
    'iban': 'TR73 0003 2000 0000 0079 1034 65',
}


def _feature_check():
    site = SiteSettings.load()
    if not site.feature_oaipmh:
        raise Http404


def _check_email_verified(request):
    profile = getattr(request.user, 'profile', None)
    if profile and not profile.email_verified:
        return False
    return True


@login_required
def oaipmh_landing(request):
    _feature_check()

    if not _check_email_verified(request):
        return render(request, 'oaipmh/landing.html', {
            'email_not_verified': True,
            'keyword_form': OAIPMHKeywordForm(),
            'browse_form': OAIPMHBrowseForm(),
        })

    daily_used = OAIPMHSearchJob.daily_count_for_user(request.user)
    daily_limit = OAIPMHSearchJob.get_daily_limit(request.user)
    remaining = max(0, daily_limit - daily_used)

    if request.method == 'POST':
        search_type = request.POST.get('search_type', 'keyword')

        if remaining <= 0:
            return JsonResponse({'success': False, 'error': 'Günlük arama limitinize ulaştınız.'}, status=429)

        if search_type == 'keyword':
            form = OAIPMHKeywordForm(request.POST)
            if not form.is_valid():
                errors = '; '.join([str(e) for errs in form.errors.values() for e in errs])
                return JsonResponse({'success': False, 'error': errors}, status=400)
            selected_unis = form.cleaned_data.get('universities')
            job = OAIPMHSearchJob.objects.create(
                user=request.user,
                search_type='keyword',
                keyword=form.cleaned_data.get('keyword', ''),
                abstract_query=form.cleaned_data.get('abstract_query', ''),
                university_ids=[u.id for u in selected_unis] if selected_unis else [],
                year_from=form.cleaned_data.get('year_from'),
                year_to=form.cleaned_data.get('year_to'),
            )
        else:  # browse
            form = OAIPMHBrowseForm(request.POST)
            if not form.is_valid():
                return JsonResponse({'success': False, 'error': str(form.errors)}, status=400)
            job = OAIPMHSearchJob.objects.create(
                user=request.user,
                search_type='browse',
                university=form.cleaned_data['university'],
            )

        run_scraping_job(job.id)
        return JsonResponse({'success': True, 'job_id': str(job.id)})

    # 5 dakikadan uzun süre running/pending kalan job'ları stale say → failed yap
    stale_cutoff = timezone.now() - timedelta(minutes=5)
    OAIPMHSearchJob.objects.filter(
        user=request.user,
        status__in=['pending', 'running'],
        created_at__lt=stale_cutoff,
    ).update(status='failed', error_message='Sunucu yeniden başlatıldı veya zaman aşımı.')

    active_job = OAIPMHSearchJob.objects.filter(
        user=request.user,
        status__in=['pending', 'running'],
    ).order_by('-created_at').first()

    return render(request, 'oaipmh/landing.html', {
        'keyword_form': OAIPMHKeywordForm(),
        'browse_form': OAIPMHBrowseForm(),
        'daily_limit': daily_limit,
        'remaining': remaining,
        'active_job_id': str(active_job.id) if active_job else None,
        'active_job_type': active_job.search_type if active_job else None,
    })


@login_required
@require_GET
def oaipmh_job_status(request, job_id):
    _feature_check()
    job = get_object_or_404(OAIPMHSearchJob, id=job_id, user=request.user)

    data = {'status': job.status, 'total_results': job.total_results}

    if job.status == 'completed':
        data['demo_results'] = job.demo_results[:3]
        data['demo_email_sent'] = job.demo_email_sent
        data['query_summary'] = job.get_query_summary()
    elif job.status == 'failed':
        data['error'] = job.error_message

    return JsonResponse(data)


@login_required
@require_POST
def oaipmh_send_demo_email(request, job_id):
    _feature_check()
    job = get_object_or_404(OAIPMHSearchJob, id=job_id, user=request.user)

    if job.status != 'completed':
        return JsonResponse({'success': False, 'error': 'İş henüz tamamlanmadı.'}, status=400)
    if not job.demo_results:
        return JsonResponse({'success': False, 'error': 'Sonuç bulunamadı.'}, status=400)
    if job.demo_email_sent:
        return JsonResponse({'success': False, 'error': 'Demo email zaten gönderildi.'}, status=400)

    send_demo_email_async(job.id)
    return JsonResponse({'success': True})


@login_required
def oaipmh_order_page(request, job_id):
    _feature_check()
    job = get_object_or_404(OAIPMHSearchJob, id=job_id, user=request.user)

    if job.status != 'completed' or not job.demo_results:
        return redirect('oaipmh:landing')

    existing_order = OAIPMHOrder.objects.filter(search_job=job).first()
    total_price = OAIPMHOrder.calculate_price(job.total_results)

    if request.method == 'POST':
        if existing_order:
            return redirect('oaipmh:order_page', job_id=job_id)
        form = OAIPMHOrderForm(request.POST)
        if form.is_valid():
            count = min(form.cleaned_data['abstract_count'], job.total_results)
            price = OAIPMHOrder.calculate_price(count)
            OAIPMHOrder.objects.create(
                user=request.user,
                search_job=job,
                abstract_count=count,
                total_price=price,
                payment_note=form.cleaned_data.get('payment_note', ''),
            )
            return redirect('oaipmh:order_page', job_id=job_id)
    else:
        form = OAIPMHOrderForm(initial={'abstract_count': min(job.total_results, 100)})

    return render(request, 'oaipmh/order.html', {
        'job': job,
        'form': form,
        'existing_order': existing_order,
        'total_price': total_price,
        'iban_info': IBAN_INFO,
    })
