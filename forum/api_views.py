import os
import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)
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
    """İlan sahibine ait son teklifleri döner. Sadece giriş yapmış ve kendi ilanları olan kullanıcılara."""
    if not request.user.is_authenticated:
        return JsonResponse({'proposals': []})

    if request.user.is_staff or request.user.is_superuser:
        proposals = JobProposal.objects.select_related('job', 'expert').order_by('-created_at')[:5]
    else:
        # Yalnızca bu kullanıcının ilanlarına gelen teklifler
        proposals = JobProposal.objects.select_related('job', 'expert').filter(
            job__owner=request.user
        ).order_by('-created_at')[:5]

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
        logger.warning(f"CRON AUTH ERROR: Gelen='{secret}', Beklenen='{expected_secret}'")

    return secret == expected_secret


@require_GET
def cron_cleanup_s3_files(request):
    """
    7 günden eski TR Dizin, OpenAlex ve OAI-PMH dosyalarını S3'den siler.

    Kullanım:
    - GET /api/cron/cleanup-s3/?secret=YOUR_SECRET
    - Günlük cron job olarak çalıştırılmalıdır.
    """
    if not _verify_cron_secret(request):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    try:
        from trdizin.services.job_runner import cleanup_expired_trdizin_s3_files as cleanup_trdizin
        from openalex.services.job_runner import cleanup_expired_openalex_s3_files as cleanup_openalex
        from oaipmh.services.job_runner import cleanup_expired_oaipmh_s3_files as cleanup_oaipmh

        trdizin_deleted = cleanup_trdizin(days=7)
        openalex_deleted = cleanup_openalex(days=7)
        oaipmh_deleted = cleanup_oaipmh(days=7)

        return JsonResponse({
            'success': True,
            'deleted_files': {
                'trdizin': trdizin_deleted,
                'openalex': openalex_deleted,
                'oaipmh': oaipmh_deleted,
            },
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def cron_cleanup_attachments(request):
    """
    90 günden eski DM ve oda mesajı dosyalarını siler.

    Kullanım:
    - GET /api/cron/cleanup-attachments/?secret=YOUR_SECRET
    - Haftalık cron job olarak çalıştırılmalıdır.
    """
    if not _verify_cron_secret(request):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    from django.utils import timezone
    from datetime import timedelta
    from forum.models import PrivateMessage, StudyRoomPost

    cutoff = timezone.now() - timedelta(days=90)
    dm_deleted = 0
    room_deleted = 0

    for msg in PrivateMessage.objects.filter(created_at__lt=cutoff).exclude(attachment=''):
        try:
            msg.attachment.storage.delete(msg.attachment.name)
            msg.attachment = ''
            msg.save(update_fields=['attachment'])
            dm_deleted += 1
        except Exception:
            pass

    for post in StudyRoomPost.objects.filter(created_at__lt=cutoff).exclude(file=''):
        try:
            post.file.storage.delete(post.file.name)
            post.file = ''
            post.save(update_fields=['file'])
            room_deleted += 1
        except Exception:
            pass

    return JsonResponse({
        'success': True,
        'deleted_files': {
            'dm_attachments': dm_deleted,
            'room_post_files': room_deleted,
        },
        'cutoff_days': 90,
    })


@require_GET
def cron_cleanup_pageviews(request):
    """
    5 günden eski sayfa ziyaret loglarını özetleyip siler.

    Kullanım:
    - GET /api/cron/cleanup-pageviews/?secret=YOUR_SECRET
    - Günlük cron job olarak çalıştırılmalıdır.
    """
    if not _verify_cron_secret(request):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    try:
        from datetime import date, timedelta
        from django.db import transaction
        from django.db.models import Count
        from analytics.models import PageView, PageViewSummary

        retention_days = int(request.GET.get('days', 5))
        cutoff = date.today() - timedelta(days=retention_days)
        old_qs = PageView.objects.filter(timestamp__date__lt=cutoff)
        total_old = old_qs.count()

        if total_old == 0:
            return JsonResponse({'success': True, 'deleted': 0, 'summaries_updated': 0})

        aggregates = list(
            old_qs
            .values('timestamp__date', 'user_id', 'path', 'tab_name')
            .annotate(visit_count=Count('id'))
        )

        upserted = 0
        with transaction.atomic():
            for row in aggregates:
                obj, created = PageViewSummary.objects.get_or_create(
                    date=row['timestamp__date'],
                    user_id=row['user_id'],
                    path=row['path'],
                    defaults={
                        'tab_name': row['tab_name'],
                        'visit_count': row['visit_count'],
                    },
                )
                if not created:
                    obj.visit_count += row['visit_count']
                    obj.save(update_fields=['visit_count'])
                upserted += 1
            deleted_count, _ = old_qs.delete()

        return JsonResponse({
            'success': True,
            'deleted': deleted_count,
            'summaries_updated': upserted,
            'retention_days': retention_days,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_GET
def cron_cleanup_session_datasets(request):
    """
    2 saatten eski, RAM'de duran istatistik araçları session veri setlerini siler.

    Kullanım:
    - GET /api/cron/cleanup-session-datasets/?secret=YOUR_SECRET
    - Saatlik cron job olarak çalıştırılmalıdır.
    """
    if not _verify_cron_secret(request):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    try:
        from istatistik.services.job_runner import cleanup_expired_session_datasets
        deleted = cleanup_expired_session_datasets()
        return JsonResponse({'success': True, 'deleted': deleted})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_GET
def admin_queue_status(request):
    """Admin dashboard için kuyruk durumu JSON endpoint'i (sadece staff)."""
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    from django.utils.timesince import timesince as _timesince
    try:
        from tezanaliz.models import TezAnaliz
        from makaleanaliz.models import MakaleAnaliz
        from yoktez.models import YokTezSearchJob
        from openalex.models import AlexSearchJob
        from trdizin.models import DizinSearchJob
        from bibliometrics.models import BibliometricJob

        sections = [
            ('Tez Analizi', TezAnaliz),
            ('Makale Analizi', MakaleAnaliz),
            ('YÖK Tez', YokTezSearchJob),
            ('OpenAlex', AlexSearchJob),
            ('TR Dizin', DizinSearchJob),
            ('Bibliometrik', BibliometricJob),
        ]

        rows = []
        for label, Model in sections:
            for job in Model.objects.filter(status='running').select_related('user').order_by('created_at'):
                rows.append({
                    'type': label,
                    'status': 'running',
                    'status_label': 'Çalışıyor',
                    'user': job.user.username if job.user_id else '-',
                    'since': _timesince(job.created_at),
                    'id_short': str(job.id)[:8],
                })
            for job in Model.objects.filter(status='pending').select_related('user').order_by('created_at'):
                rows.append({
                    'type': label,
                    'status': 'pending',
                    'status_label': 'Bekliyor',
                    'user': job.user.username if job.user_id else '-',
                    'since': _timesince(job.created_at),
                    'id_short': str(job.id)[:8],
                })

        return JsonResponse({
            'rows': rows,
            'running_count': sum(1 for r in rows if r['status'] == 'running'),
            'pending_count': sum(1 for r in rows if r['status'] == 'pending'),
        })
    except Exception as e:
        return JsonResponse({'rows': [], 'running_count': 0, 'pending_count': 0, 'error': str(e)})


@require_GET
def cron_health_check(request):
    """
    Sistem sağlık kontrolü: DB, S3, Redis durumunu kontrol eder.
    """
    checks = {}
    overall = 'healthy'

    # DB kontrolü
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        checks['db'] = 'ok'
    except Exception as e:
        checks['db'] = f'error: {e}'
        overall = 'degraded'

    # Redis kontrolü
    try:
        from django.core.cache import cache
        cache.set('health_check', '1', timeout=5)
        assert cache.get('health_check') == '1'
        checks['redis'] = 'ok'
    except Exception as e:
        checks['redis'] = f'error: {e}'
        overall = 'degraded'

    # S3 kontrolü
    try:
        import boto3
        from django.conf import settings as django_settings
        s3 = boto3.client(
            's3',
            aws_access_key_id=django_settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=django_settings.AWS_SECRET_ACCESS_KEY,
            region_name=django_settings.AWS_S3_REGION_NAME,
        )
        s3.head_bucket(Bucket=getattr(django_settings, 'AWS_STORAGE_BUCKET_NAME', 'analizus-files'))
        checks['s3'] = 'ok'
    except Exception as e:
        checks['s3'] = f'error: {e}'
        overall = 'degraded'

    return JsonResponse({
        'status': overall,
        'service': 'Analizus Forum',
        'checks': checks,
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

@require_GET
def cron_process_account_deletions(request):
    """
    deletion_requested_at üzerinden 30 gün geçmiş hesapları anonimleştirir
    ve DM kayıtlarını siler.

    Kullanım:
    - GET /api/cron/process-account-deletions/?secret=YOUR_SECRET
    - Günlük cron job olarak çalıştırılmalıdır.
    """
    if not _verify_cron_secret(request):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    from django.utils import timezone
    from datetime import timedelta
    import secrets
    from forum.models import Profile, PrivateMessage

    cutoff = timezone.now() - timedelta(days=30)
    profiles = Profile.objects.filter(
        deletion_requested_at__isnull=False,
        deletion_requested_at__lte=cutoff,
    ).select_related('user')

    processed = 0
    for profile in profiles:
        user = profile.user
        token = secrets.token_hex(6)

        # Kullanıcı temel bilgilerini anonimleştir
        user.email = f'deleted_{token}@deleted.invalid'
        user.username = f'deleted_{token}'
        user.first_name = ''
        user.last_name = ''
        user.set_unusable_password()
        user.save()

        # Avatar ve kapak fotoğrafını sil
        for field in (profile.avatar, profile.cover_image):
            if field:
                try:
                    field.storage.delete(field.name)
                except Exception:
                    pass

        # Profil kişisel alanlarını temizle
        profile.avatar = None
        profile.cover_image = None
        profile.bio = ''
        profile.phone_number = ''
        profile.linkedin = ''
        profile.twitter = ''
        profile.github = ''
        profile.orcid = ''
        profile.google_scholar = ''
        profile.website = ''
        profile.title = ''
        profile.location = ''
        profile.university = ''
        profile.department = ''
        profile.academic_title = ''
        profile.onboarding_interests = []
        profile.onboarding_tools = []
        profile.deletion_requested_at = None  # işlem tamamlandı, tekrar çalışmasın
        profile.save()

        # DM kayıtlarını sil
        PrivateMessage.objects.filter(sender=user).delete()
        PrivateMessage.objects.filter(receiver=user).delete()

        processed += 1

    return JsonResponse({
        'success': True,
        'processed': processed,
        'cutoff_days': 30,
    })
