from django.conf import settings
from forum.models import Profile, Notification, PrivateMessage


def profile_context(request):
    """
    Kullanıcı profili, okunmamış bildirim sayısı gibi genel bilgileri
    tüm templatelere gönderen context processor.
    """
    context = {
        'GOOGLE_ANALYTICS_ID': getattr(settings, 'GOOGLE_ANALYTICS_ID', '')
    }
    if request.user.is_authenticated:
        try:
            profile, created = Profile.objects.get_or_create(user=request.user)
            unread_notifications = Notification.objects.filter(recipient=request.user, is_read=False).count()
            unread_private_messages = PrivateMessage.objects.filter(receiver=request.user, is_read=False).count()
            
            context.update({
                'user_profile': profile,
                'unread_notifications_count': unread_notifications,
                'unread_private_messages_count': unread_private_messages,
            })
        except Profile.DoesNotExist:
            pass
    return context


def google_analytics(request):
    """Google Analytics ID'yi tüm template'lere geçirir"""
    return {'GOOGLE_ANALYTICS_ID': getattr(settings, 'GOOGLE_ANALYTICS_ID', '')}