from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.timesince import timesince
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