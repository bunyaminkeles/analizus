from django.conf import settings
from forum.models import Profile, Notification, PrivateMessage, SiteSettings


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
    """Google Analytics ID ve site verification kodlarını tüm template'lere geçirir"""
    return {
        'GOOGLE_ANALYTICS_ID': getattr(settings, 'GOOGLE_ANALYTICS_ID', ''),
        'GOOGLE_SITE_VERIFICATION': getattr(settings, 'GOOGLE_SITE_VERIFICATION', ''),
        'BING_SITE_VERIFICATION': getattr(settings, 'BING_SITE_VERIFICATION', ''),
    }


def feature_flags(request):
    """Feature flag'leri tüm template'lere geçirir"""
    site = SiteSettings.load()
    return {
        'features': {
            'blog': site.feature_blog,
            'market': site.feature_market,
            'ai_assistant': site.feature_ai_assistant,
            'trdizin': site.feature_trdizin,
            'openalex': site.feature_openalex,
            'oaipmh': site.feature_oaipmh,
            'quiz': site.feature_quiz,
            'messaging': site.feature_messaging,
            'donation': site.feature_donation,
            'success_stories': site.feature_success_stories,
            'bibliometrics': site.feature_bibliometrics,
            'yoktez': site.feature_yoktez,
        }
    }