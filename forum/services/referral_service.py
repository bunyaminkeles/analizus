from datetime import timedelta
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

REFERRAL_REPUTATION_BONUS = 50
REFERRAL_WAIT_HOURS = 48

REFERRAL_BADGE_MILESTONES = [
    (1,  'davetci',         'Davetçi',          'bi-person-plus',  '#22c55e', 'special'),
    (5,  'topluluk-elcisi', 'Topluluk Elçisi',   'bi-people-fill',  '#a855f7', 'special'),
    (10, 'buyukelci',       'Büyükelçi',         'bi-award-fill',   '#eab308', 'special'),
]

MAX_REWARDED_FROM_SAME_IP = 2


def _get_premium_days(total_rewarded_before):
    """Azalan getiri: 1-5 → 20 gün, 6-10 → 10 gün, 11+ → 5 gün"""
    if total_rewarded_before < 5:
        return 20
    elif total_rewarded_before < 10:
        return 10
    return 5


def check_and_award_referral(referral_use):
    """
    Referred kullanıcı için tüm koşulları kontrol et; sağlanmışsa referrer'ı ödüllendir.
    Returns True if reward was given.
    """
    from forum.models import ReferralUse, Badge

    if referral_use.rewarded or referral_use.flagged:
        return False

    referred = referral_use.referred
    referrer = referral_use.referrer

    # Koşul 1: e-posta doğrulandı mı?
    try:
        if not referred.profile.email_verified:
            return False
    except Exception:
        return False

    # Koşul 2: 48 saat geçti mi?
    if (timezone.now() - referred.date_joined).total_seconds() < REFERRAL_WAIT_HOURS * 3600:
        return False

    # Koşul 3: en az 1 quiz sorusu çözüldü mü?
    quiz_score = referred.quiz_scores.first()
    if not quiz_score or quiz_score.total_points == 0:
        return False

    # Abuse kontrolü: aynı IP'den kaç ödül verildi?
    same_ip_rewarded = ReferralUse.objects.filter(
        referrer=referrer,
        ip_address=referral_use.ip_address,
        rewarded=True,
    ).count()
    if same_ip_rewarded >= MAX_REWARDED_FROM_SAME_IP:
        referral_use.flagged = True
        referral_use.save(update_fields=['flagged'])
        logger.warning(f"Referral flagged (IP abuse): referrer={referrer.username}, ip={referral_use.ip_address}")
        return False

    # Toplam ödüllendirilmiş sayısı (bu ödül öncesi)
    total_rewarded_before = ReferralUse.objects.filter(referrer=referrer, rewarded=True).count()
    days = _get_premium_days(total_rewarded_before)

    # Referral'ı onayla
    referral_use.qualified_at = timezone.now()
    referral_use.rewarded = True
    referral_use.premium_days_awarded = days
    referral_use.reputation_awarded = REFERRAL_REPUTATION_BONUS
    referral_use.save(update_fields=['qualified_at', 'rewarded', 'premium_days_awarded', 'reputation_awarded'])

    # 1. Premium uzat
    try:
        profile = referrer.profile
        now = timezone.now()
        if profile.premium_expires_at and profile.premium_expires_at > now:
            profile.premium_expires_at += timedelta(days=days)
        else:
            profile.premium_expires_at = now + timedelta(days=days)
        profile.account_type = 'Premium'
        profile.reputation += REFERRAL_REPUTATION_BONUS
        profile.save(update_fields=['account_type', 'premium_expires_at', 'reputation'])
        profile.check_and_award_badges()
    except Exception as e:
        logger.error(f"Referral premium/rep hatası: {e}")
        return False

    # 2. Rozet kademesi
    total_now = total_rewarded_before + 1
    _award_referral_badge(referrer, total_now)

    # 3. Referrer'a bildirim
    _notify_referral_reward(referrer, referred, days, total_now)

    return True


def _award_referral_badge(referrer, total_rewarded):
    """Milestone rozet ver."""
    from forum.models import Badge
    for milestone, slug, name, icon, color, badge_type in REFERRAL_BADGE_MILESTONES:
        if total_rewarded == milestone:
            badge, _ = Badge.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'description': f'{milestone} kişiyi platforma davet etti',
                    'icon': icon,
                    'color': color,
                    'badge_type': badge_type,
                    'points_required': 0,
                },
            )
            referrer.profile.badges.add(badge)
            break


def _notify_referral_reward(referrer, referred, days, total_now):
    """Referrer'a gerçek zamanlı bildirim + Notification kaydı."""
    try:
        from forum.models import Notification
        from forum.utils import send_realtime_notification
        from django.urls import reverse

        verb = f"davetiniz doğrulandı — +{days} gün premium kazandınız! (Toplam: {total_now} geçerli davet)"
        Notification.objects.create(
            recipient=referrer,
            sender=referred,
            verb=verb,
        )
        url = reverse('referral_dashboard')
        send_realtime_notification(referrer.id, verb, url)
    except Exception as e:
        logger.warning(f"Referral bildirim hatası: {e}")


def notify_referral_registered(referrer, referred):
    """Referred kullanıcı kayıt olduğunda referrer'a anlık bildirim."""
    try:
        from forum.utils import send_realtime_notification
        from django.urls import reverse
        msg = f"{referred.username} davet bağlantınızla kayıt oldu (e-posta doğrulaması bekleniyor)"
        send_realtime_notification(referrer.id, msg, reverse('referral_dashboard'))
    except Exception as e:
        logger.warning(f"Referral kayıt bildirimi hatası: {e}")
