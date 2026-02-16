from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from functools import wraps

from .forms import TezSearchForm, TezOrderForm
from .models import TezSearchJob, TezOrder
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

# IBAN bilgileri (bağış sistemiyle aynı)
IBAN_INFO = {
    'hesap_sahibi': 'Bünyamin Keleş',
    'iban': 'TR73 0003 2000 0000 0079 1034 65',
}


@feature_required('yoktez')
@login_required
def yoktez_landing(request):
    """Landing page: form + demo arama."""
    form = TezSearchForm()
    user = request.user

    # Günlük limit kontrolü
    daily_count = TezSearchJob.daily_count_for_user(user)
    daily_limit = TezSearchJob.get_daily_limit(user)
    remaining = max(0, daily_limit - daily_count)

    if request.method == 'POST':
        form = TezSearchForm(request.POST)
        if form.is_valid():
            # E-posta doğrulanmış mı?
            if not user.profile.email_verified:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': 'Tez tarama için e-posta doğrulaması gereklidir. Profil sayfanızdan e-postanızı doğrulayın.'
                    }, status=403)
                return render(request, 'yoktez/landing.html', {
                    'form': form,
                    'error': 'Tez tarama için e-posta doğrulaması gereklidir.',
                    'remaining': remaining,
                    'daily_limit': daily_limit,
                })

            # Limit aşıldı mı?
            if remaining <= 0:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': f'Günlük demo limitiniz doldu ({daily_limit}/{daily_limit}). '
                                 f'{"Premium üyelikle 7 aramaya yükseltebilirsiniz." if not user.profile.is_premium else "Yarın tekrar deneyebilirsiniz."}'
                    }, status=429)
                return render(request, 'yoktez/landing.html', {
                    'form': form,
                    'error': 'Günlük demo limitiniz doldu.',
                    'remaining': 0,
                    'daily_limit': daily_limit,
                })

            konu = form.cleaned_data['konu']
            keywords = [kw for kw in [
                form.cleaned_data['keyword1'],
                form.cleaned_data.get('keyword2', ''),
                form.cleaned_data.get('keyword3', ''),
            ] if kw.strip()]

            job = TezSearchJob.objects.create(
                user=user,
                konu=konu,
                keywords=keywords,
            )
            run_scraping_job(job.id)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'started', 'job_id': str(job.id), 'remaining': remaining - 1, 'daily_limit': daily_limit})

            return render(request, 'yoktez/landing.html', {
                'form': form,
                'job_id': str(job.id),
                'remaining': remaining - 1,
                'daily_limit': daily_limit,
            })

    return render(request, 'yoktez/landing.html', {
        'form': form,
        'remaining': remaining,
        'daily_limit': daily_limit,
    })


@login_required
@require_GET
def yoktez_job_status(request, job_id):
    """AJAX: job durumu + demo sonuçlar."""
    job = get_object_or_404(TezSearchJob, id=job_id, user=request.user)

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
def yoktez_send_demo_email(request, job_id):
    """Demo sonuçları kullanıcının kayıtlı emailine gönder."""
    job = get_object_or_404(TezSearchJob, id=job_id, user=request.user)

    if job.status != 'completed' or not job.demo_results:
        return JsonResponse({'error': 'Sonuçlar henüz hazır değil.'}, status=400)

    if job.demo_email_sent:
        return JsonResponse({'error': 'Demo sonuçlar zaten gönderildi.'}, status=400)

    from .services.job_runner import send_demo_email_async
    send_demo_email_async(job.id)

    return JsonResponse({'success': True, 'message': f'Demo sonuçların {request.user.email} adresine gönderilmesi için işlem başlatıldı.'})


@login_required
def yoktez_order_page(request, job_id):
    """Sipariş sayfası: GET=form göster, POST=sipariş oluştur."""
    job = get_object_or_404(TezSearchJob, id=job_id, user=request.user)

    if job.status != 'completed' or job.total_results == 0:
        return render(request, 'yoktez/order.html', {
            'job': job,
            'error': 'Bu arama için henüz sonuç yok.',
        })

    # Zaten sipariş var mı?
    existing_order = TezOrder.objects.filter(search_job=job, user=request.user).first()
    if existing_order:
        return render(request, 'yoktez/order.html', {
            'job': job,
            'existing_order': existing_order,
        })

    if request.method == 'POST':
        form = TezOrderForm(request.POST)
        if form.is_valid():
            abstract_count = min(form.cleaned_data['abstract_count'], job.total_results)
            price = TezOrder.calculate_price(abstract_count)

            order = TezOrder.objects.create(
                user=request.user,
                search_job=job,
                abstract_count=abstract_count,
                total_price=price,
                payment_note=form.cleaned_data.get('payment_note', ''),
                status='pending_payment',
            )
            return render(request, 'yoktez/order.html', {
                'job': job,
                'existing_order': order,
                'success': True,
            })

    return render(request, 'yoktez/order.html', {
        'job': job,
    })


from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings

def debug_email_test(request):
    """
    Geçici test view'ı. E-posta ayarlarını test etmek için.
    Bu view ve ilişkili URL, sorun çözüldükten sonra SİLİNMELİDİR.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        admin_user = User.objects.filter(is_superuser=True).order_by('pk').first()
        if not admin_user or not admin_user.email:
            return HttpResponse("Hata: E-posta gönderecek bir admin kullanıcısı (superuser) bulunamadı veya adminin e-postası kayıtlı değil.", status=500)
        recipient_email = admin_user.email
    except Exception as e:
        return HttpResponse(f"Hata: Admin kullanıcısı aranırken bir sorun oluştu: {e}", status=500)

    response_lines = []
    response_lines.append("<h1>E-posta Gönderim Testi</h1>")
    response_lines.append("<p>Bu sayfa, Django e-posta ayarlarınızı test etmek için oluşturulmuştur.</p>")
    response_lines.append(f"<p><b>Test e-postası gönderilecek adres:</b> {recipient_email}</p>")
    response_lines.append("<hr>")
    
    response_lines.append("<h2>Kullanılan Ayarlar:</h2>")
    response_lines.append("<ul>")
    response_lines.append(f"<li><b>EMAIL_HOST:</b> {settings.EMAIL_HOST}</li>")
    response_lines.append(f"<li><b>EMAIL_PORT:</b> {settings.EMAIL_PORT}</li>")
    response_lines.append(f"<li><b>EMAIL_HOST_USER:</b> {settings.EMAIL_HOST_USER}</li>")
    response_lines.append(f"<li><b>EMAIL_USE_TLS:</b> {getattr(settings, 'EMAIL_USE_TLS', 'Not Set')}</li>")
    response_lines.append(f"<li><b>EMAIL_USE_SSL:</b> {getattr(settings, 'EMAIL_USE_SSL', 'Not Set')}</li>")
    response_lines.append(f"<li><b>DEFAULT_FROM_EMAIL:</b> {settings.DEFAULT_FROM_EMAIL}</li>")
    response_lines.append("</ul><hr>")

    response_lines.append("<h2>Gönderim Sonucu:</h2>")

    try:
        sent_count = send_mail(
            subject='[Analizus] Test Email',
            message='This is a test email from your Django application. If you received this, your SMTP settings are correct!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        if sent_count > 0:
            response_lines.append("<p style='color:green; font-weight:bold;'>✅ BAŞARILI!</p>")
            response_lines.append(f"<p>Test e-postası başarıyla {recipient_email} adresine gönderildi.</p>")
        else:
            response_lines.append("<p style='color:orange; font-weight:bold;'>⚠️ BAŞARISIZ!</p>")
            response_lines.append("<p>Komut hatasız çalıştı ancak e-posta gönderilemedi (send_mail 0 döndürdü).</p>")

    except Exception as e:
        response_lines.append("<p style='color:red; font-weight:bold;'>❌ HATA!</p>")
        response_lines.append("<p>E-posta gönderilirken bir istisna (exception) oluştu:</p>")
        response_lines.append(f"<pre style='background-color:#f0f0f0; padding:10px; border:1px solid #ccc;'>{e}</pre>")
        response_lines.append("<hr><p><b>Öneri:</b> Lütfen Render panelindeki ortam değişkenlerinizi (environment variables) kontrol edin. Özellikle `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS` ve `DEFAULT_FROM_EMAIL` değerlerinin doğruluğundan emin olun.</p>")

    return HttpResponse("<br>".join(response_lines))
