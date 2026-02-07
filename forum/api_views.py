import os
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.timesince import timesince
from django.core.management import call_command
from django.conf import settings
from .models import JobProposal, Profile, Notification
from .utils import send_realtime_notification


@login_required
@require_POST
def toggle_follow_user(request, username):
    """Bir kullanıcıyı takip et/takipten çık."""
    try:
        target_user = get_object_or_404(User, username=username)
        current_user_profile = request.user.profile
        target_profile = target_user.profile

        if target_user == request.user:
            return JsonResponse({'success': False, 'error': 'Kendinizi takip edemezsiniz.'})

        if target_profile in current_user_profile.following.all():
            # Takipten çık
            current_user_profile.following.remove(target_profile)
            is_following = False
        else:
            # Takip et
            current_user_profile.following.add(target_profile)
            is_following = True

            # Bildirim oluştur
            message = f"<b>{request.user.username}</b> sizi takip etmeye başladı."
            url = reverse('profile_detail', kwargs={'username': request.user.username})
            
            content_type = ContentType.objects.get_for_model(request.user)
            Notification.objects.create(
                recipient=target_user,
                sender=request.user,
                verb=message,
                content_type=content_type,
                object_id=request.user.pk
            )
            
            # Gerçek zamanlı bildirim gönder
            send_realtime_notification(target_user.id, message, url)
            
        # Güncel sayıları döndür
        follower_count = target_profile.followers.count()
        following_count = current_user_profile.following.count()
        
        return JsonResponse({
            'success': True, 
            'is_following': is_following, 
            'follower_count': follower_count,
            'following_count': following_count
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def widget_market_rates(request):
    """Altınkaynak verilerini JSON olarak döner"""
    data = get_altinkaynak_rates()
    return JsonResponse({'rates': data})

def widget_latest_proposals(request):
    """Analiz pazarındaki son teklifleri JSON olarak döner"""
    # Son 5 teklifi getir
    proposals = JobProposal.objects.select_related('job', 'expert').order_by('-created_at')[:5]

    data = []
    for p in proposals:
        data.append({
            'id': p.id,
            'job_title': p.job.title,
            'expert_name': p.expert.username,
            'price': f"{p.price:,.0f} ₺",
            'time_ago': timesince(p.created_at).split(',')[0] + " önce"
        })

    return JsonResponse({'proposals': data})


# ═══════════════════════════════════════════════════════════════════════════
# CRON JOB ENDPOINTS
# Render Cron Jobs veya external cron servisleri (cron-job.org) ile kullanılır
# ═══════════════════════════════════════════════════════════════════════════

def _verify_cron_secret(request):
    """Cron job isteklerini doğrular"""
    # Header veya query param olarak secret key kontrolü
    secret = request.headers.get('X-Cron-Secret') or request.GET.get('secret')
    expected_secret = os.environ.get('CRON_SECRET_KEY', 'default-dev-secret-change-in-prod')

    if secret != expected_secret:
        print(f"CRON AUTH ERROR: Gelen='{secret}', Beklenen='{expected_secret}'")

    return secret == expected_secret


@require_GET
def cron_generate_daily_quiz(request):
    """
    Günlük quiz soruları üretir.

    Kullanım:
    - Render Cron Job: GET /api/cron/daily-quiz/?secret=YOUR_SECRET
    - cron-job.org: Aynı URL, günlük olarak çağrılacak şekilde ayarlayın

    Environment Variables:
    - CRON_SECRET_KEY: Bu endpoint'i korumak için gizli anahtar
    - GROQ_API_KEY: Quiz soruları için AI API anahtarı
    """
    if not _verify_cron_secret(request):
        return JsonResponse({
            'success': False,
            'error': 'Unauthorized - Invalid or missing secret key'
        }, status=401)

    try:
        # Quiz soru sayısı (varsayılan 10)
        count = int(request.GET.get('count', 10))

        # Management komutunu çağır
        from io import StringIO
        out = StringIO()
        call_command('generate_daily_quiz', count=count, stdout=out)

        return JsonResponse({
            'success': True,
            'message': f'{count} quiz sorusu üretim talebi gönderildi',
            'output': out.getvalue()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def cron_update_badges_ranks(request):
    """
    Tüm kullanıcıların rozetlerini ve rütbelerini günceller.
    Haftalık olarak çalıştırılması önerilir.
    """
    if not _verify_cron_secret(request):
        return JsonResponse({
            'success': False,
            'error': 'Unauthorized'
        }, status=401)

    try:
        updated_count = 0
        for profile in Profile.objects.all():
            profile.check_and_award_badges()
            profile.update_rank()
            updated_count += 1

        return JsonResponse({
            'success': True,
            'message': f'{updated_count} kullanıcının rozetleri güncellendi'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def cron_cleanup_yoktez_s3(request):
    """
    3 günden eski, sipariş verilmemiş YÖK Tez dosyalarını S3'den siler.

    Kullanım:
    - GET /api/cron/cleanup-yoktez/?secret=YOUR_SECRET
    - Günlük cron job olarak çalıştırılmalıdır.
    """
    if not _verify_cron_secret(request):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    try:
        from yoktez.services.job_runner import cleanup_expired_s3_files
        deleted = cleanup_expired_s3_files(days=3)
        return JsonResponse({
            'success': True,
            'deleted_files': deleted,
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def cron_health_check(request):
    """
    Basit sağlık kontrolü endpoint'i.
    Cron servislerinin site durumunu kontrol etmesi için.
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'Analizus Forum',
        'version': '1.0'
    })


@require_GET
def admin_create_or_reset(request):
    """
    Admin kullanıcısı oluşturur veya şifresini sıfırlar.

    Kullanım:
    GET /api/admin-setup/?secret=YOUR_SECRET&username=admin&password=newpassword123&email=admin@example.com

    Devre dışı bırakmak için: Render'da ADMIN_SETUP_ENABLED=false ayarlayın
    """
    # Environment variable ile devre dışı bırakılabilir
    if os.environ.get('ADMIN_SETUP_ENABLED', 'true').lower() == 'false':
        return JsonResponse({
            'success': False,
            'error': 'Bu endpoint devre dışı bırakıldı'
        }, status=403)

    if not _verify_cron_secret(request):
        return JsonResponse({
            'success': False,
            'error': 'Unauthorized - Invalid secret key'
        }, status=401)

    username = request.GET.get('username', 'admin')
    password = request.GET.get('password')
    email = request.GET.get('email', 'info@analizus.com')

    if not password or len(password) < 8:
        return JsonResponse({
            'success': False,
            'error': 'Password gerekli ve en az 8 karakter olmalı'
        }, status=400)

    try:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email, 'is_staff': True, 'is_superuser': True}
        )

        if not created:
            # Mevcut kullanıcı - şifreyi güncelle
            user.is_staff = True
            user.is_superuser = True

        user.set_password(password)
        user.save()

        # Profile oluştur
        Profile.objects.get_or_create(user=user)

        return JsonResponse({
            'success': True,
            'message': f"Admin {'oluşturuldu' if created else 'güncellendi'}: {username}",
            'warning': 'GÜVENLİK: Bu endpoint\'i şimdi devre dışı bırakın!'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def run_initial_setup(request):
    """
    Veritabanı başlangıç verilerini oluşturur (kategoriler, rozetler, yetenekler vb.)

    Kullanım:
    GET /api/initial-setup/?secret=YOUR_SECRET

    Devre dışı bırakmak için: Render'da ADMIN_SETUP_ENABLED=false ayarlayın
    """
    if os.environ.get('ADMIN_SETUP_ENABLED', 'true').lower() == 'false':
        return JsonResponse({
            'success': False,
            'error': 'Bu endpoint devre dışı bırakıldı'
        }, status=403)

    if not _verify_cron_secret(request):
        return JsonResponse({
            'success': False,
            'error': 'Unauthorized - Invalid secret key'
        }, status=401)

    results = []

    try:
        # 1. Kategorileri oluştur
        call_command('setup_categories')
        results.append('Kategoriler oluşturuldu')
    except Exception as e:
        results.append(f'Kategoriler HATA: {str(e)[:50]}')

    try:
        # 2. Rozetleri oluştur
        call_command('create_badges')
        results.append('Rozetler oluşturuldu')
    except Exception as e:
        results.append(f'Rozetler HATA: {str(e)[:50]}')

    try:
        # 3. Yetenekleri oluştur
        call_command('populate_skills')
        results.append('Yetenekler oluşturuldu')
    except Exception as e:
        results.append(f'Yetenekler HATA: {str(e)[:50]}')

    return JsonResponse({
        'success': True,
        'message': 'Başlangıç kurulumu tamamlandı',
        'results': results
    })