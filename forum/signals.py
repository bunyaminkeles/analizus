from django.db.models.signals import post_save, post_delete, pre_save
from datetime import timedelta
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone as tz
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
import logging
from .utils import send_realtime_notification
from .mention_utils import parse_mentions

logger = logging.getLogger(__name__)


def send_chat_message(message_instance):
    """Chat WebSocket'e mesaj gönder - anlık mesajlaşma için"""
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()
        if not channel_layer:
            return

        # Benzersiz oda adı oluştur (her iki kullanıcı için aynı)
        user_ids = sorted([message_instance.sender.id, message_instance.receiver.id])
        room_name = f'chat_{user_ids[0]}_{user_ids[1]}'

        # Attachment bilgileri
        attachment_type = ''
        attachment_url = ''
        attachment_name = message_instance.attachment_name or ''

        if message_instance.attachment:
            attachment_url = message_instance.attachment.url
            if attachment_name:
                ext = attachment_name.split('.')[-1].lower()
                if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                    attachment_type = 'image'
                elif ext == 'pdf':
                    attachment_type = 'pdf'
                else:
                    attachment_type = 'document'

        async_to_sync(channel_layer.group_send)(
            room_name,
            {
                'type': 'chat_message',
                'message': message_instance.message or '',
                'sender_id': message_instance.sender.id,
                'sender_username': message_instance.sender.username,
                'attachment_url': attachment_url,
                'attachment_name': attachment_name,
                'attachment_type': attachment_type,
                'timestamp': message_instance.created_at.strftime('%H:%M'),
                'message_id': message_instance.id,
            }
        )
    except Exception as e:
        logger.error(f"Chat WebSocket mesajı gönderilemedi: {e}")

from .models import Post, PrivateMessage, Notification, PostLike, Topic, Badge, FreelanceJob
from .models import Profile  # Profile modelini import et


@receiver(post_save, sender=Topic)
def add_reputation_on_new_topic(sender, instance, created, **kwargs):
    """Yeni bir konu oluşturulduğunda yazarına +5 puan ver"""
    if created:
        try:
            profile, created_profile = Profile.objects.get_or_create(user=instance.starter)
            profile.reputation += 5
            profile.save(update_fields=['reputation'])
        except Exception as e:
            logger.error(f"Yeni konu için itibar puanı eklenemedi: {e}")


@receiver(post_save, sender=Post)
def post_save_receiver(sender, instance, created, **kwargs):
    """Yeni post oluşturulduğunda ilgili işlemleri yap"""
    if created:
        # Cevabı yazan kullanıcıya +2 puan ver
        try:
            profile, created_profile = Profile.objects.get_or_create(user=instance.created_by)
            profile.reputation += 2
            profile.save(update_fields=['reputation'])
        except Exception as e:
            logger.error(f"Yeni cevap için itibar puanı eklenemedi: {e}")

        # Konu sahibine bildirim gönder (eğer cevap başkası tarafından yazıldıysa)
        if instance.topic.starter != instance.created_by:
            recipient = instance.topic.starter
            message = f"<b>{instance.created_by.username}</b>, '{instance.topic.subject}' konusuna yeni bir yanıt yazdı."
            url = instance.get_absolute_url()

            try:
                content_type = ContentType.objects.get_for_model(instance)
                Notification.objects.create(
                    recipient=recipient,
                    sender=instance.created_by,
                    verb=message,
                    content_type=content_type,
                    object_id=instance.pk
                )
                send_realtime_notification(recipient.id, message, url)
            except Exception as e:
                logger.error(f"Post bildirimi oluşturulamadı: {e}")

        # @mention bildirimleri
        try:
            mentioned_users = parse_mentions(instance.message)
            content_type = ContentType.objects.get_for_model(instance)
            url = instance.get_absolute_url()
            for mentioned_user in mentioned_users:
                # Kendini mention edene ve zaten bildirim giden konu sahibine gönderme
                if mentioned_user == instance.created_by:
                    continue
                if mentioned_user == instance.topic.starter:
                    continue
                mention_msg = f"<b>{instance.created_by.username}</b>, '{instance.topic.subject}' konusunda sizi etiketledi."
                Notification.objects.create(
                    recipient=mentioned_user,
                    sender=instance.created_by,
                    verb=mention_msg,
                    content_type=content_type,
                    object_id=instance.pk
                )
                send_realtime_notification(mentioned_user.id, mention_msg, url)
                # E-posta bildirimi
                from .email_utils import send_mention_notification
                send_mention_notification(mentioned_user, instance, instance.topic)
        except Exception as e:
            logger.error(f"Mention bildirimi oluşturulamadı: {e}")


@receiver(post_save, sender=PrivateMessage)
def private_message_post_save(sender, instance, created, **kwargs):
    """Yeni özel mesaj geldiğinde bildirim gönder ve chat'e düşür"""
    if created:
        recipient = instance.receiver
        message = f"<b>{instance.sender.username}</b>'den yeni bir özel mesajınız var."
        url = reverse('send_message', args=[instance.sender.username])

        try:
            # Notification oluştur
            content_type = ContentType.objects.get_for_model(instance)
            Notification.objects.create(
                recipient=recipient,
                sender=instance.sender,
                verb=message,
                content_type=content_type,
                object_id=instance.pk
            )

            # Gerçek zamanlı bildirim
            send_realtime_notification(recipient.id, message, url)

            # E-posta bildirimi gönder
            from .email_utils import send_private_message_notification
            send_private_message_notification(instance.sender, recipient, instance.message)

            # Anlık mesajlaşma - chat kutusuna düşür
            # WebSocket consumer'dan gelen mesajlar zaten doğrudan broadcast edilir
            if not getattr(instance, '_from_websocket', False):
                send_chat_message(instance)
        except Exception as e:
            logger.error(f"Özel mesaj bildirimi oluşturulamadı: {e}")

        # @mention bildirimleri (özel mesajda 3. kişi etiketlenirse)
        try:
            mentioned_users = parse_mentions(instance.message)
            content_type = ContentType.objects.get_for_model(instance)
            for mentioned_user in mentioned_users:
                # Gönderen, alıcı veya kendini mention edene bildirim gönderme
                if mentioned_user in (instance.sender, instance.receiver):
                    continue
                mention_msg = f"<b>{instance.sender.username}</b> bir mesajda sizi etiketledi."
                mention_url = reverse('send_message', args=[instance.sender.username])
                Notification.objects.create(
                    recipient=mentioned_user,
                    sender=instance.sender,
                    verb=mention_msg,
                    content_type=content_type,
                    object_id=instance.pk
                )
                send_realtime_notification(mentioned_user.id, mention_msg, mention_url)
        except Exception as e:
            logger.error(f"Özel mesaj mention bildirimi oluşturulamadı: {e}")


@receiver(post_save, sender=PostLike)
def add_reputation_on_like(sender, instance, created, **kwargs):
    """Bir gönderi beğenildiğinde yazarına +5 puan ver"""
    if created:
        try:
            profile = instance.post.created_by.profile
            profile.reputation += 5
            profile.save(update_fields=['reputation'])
        except Exception as e:
            logger.error(f"Like reputation eklenemedi: {e}")


@receiver(post_delete, sender=PostLike)
def remove_reputation_on_unlike(sender, instance, **kwargs):
    """Beğeni geri alınırsa puanı sil"""
    try:
        profile = instance.post.created_by.profile
        profile.reputation = max(0, profile.reputation - 5)
        profile.save(update_fields=['reputation'])
    except Exception as e:
        logger.error(f"Unlike reputation silinemedi: {e}")


@receiver(pre_save, sender=Post)
def capture_old_best_answer(sender, instance, **kwargs):
    """Post kaydedilmeden önceki 'is_best_answer' durumunu yakala"""
    if instance.pk:
        try:
            old_instance = Post.objects.get(pk=instance.pk)
            instance._old_is_best_answer = old_instance.is_best_answer
        except Post.DoesNotExist:
            pass


@receiver(post_save, sender=Post)
def handle_best_answer_reputation(sender, instance, created, **kwargs):
    """En iyi cevap seçildiğinde +20 puan ver, geri alınırsa sil"""
    if not created and hasattr(instance, '_old_is_best_answer'):
        try:
            if instance.is_best_answer and not instance._old_is_best_answer:
                profile = instance.created_by.profile
                profile.reputation += 20
                profile.save(update_fields=['reputation'])
                # En İyi Cevap rozeti ver
                check_and_award_participation_badges(profile)
            elif not instance.is_best_answer and instance._old_is_best_answer:
                profile = instance.created_by.profile
                profile.reputation = max(0, profile.reputation - 20)
                profile.save(update_fields=['reputation'])
        except Exception as e:
            logger.error(f"Best answer reputation güncellenemedi: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# OTOMATİK ROZET KAZANMA FONKSİYONLARI
# ═══════════════════════════════════════════════════════════════════════════

def check_and_award_participation_badges(profile):
    """Forum aktivitelerine göre katılım rozetlerini kontrol et ve ver"""
    try:
        user = profile.user

        # Yardımsever: 50 soruya cevap verdi
        if user.posts.count() >= 50:
            badge = Badge.objects.filter(slug='yardimsever').first()
            if badge:
                profile.badges.add(badge)

        # Konu Açıcı: 20 konu açtı
        if user.topics.count() >= 20:
            badge = Badge.objects.filter(slug='konu-acici').first()
            if badge:
                profile.badges.add(badge)

        # En İyi Cevap: Bir cevabı "En Faydalı" seçildi
        if user.posts.filter(is_best_answer=True).exists():
            badge = Badge.objects.filter(slug='en-iyi-cevap').first()
            if badge:
                profile.badges.add(badge)

        # Çözüm Ustası: 25 kez "En Faydalı Cevap"
        best_answer_count = user.posts.filter(is_best_answer=True).count()
        if best_answer_count >= 25:
            badge = Badge.objects.filter(slug='cozum-ustasi').first()
            if badge:
                profile.badges.add(badge)

        # Puan bazlı rozetleri de kontrol et
        profile.check_and_award_badges()
        profile.update_rank()

    except Exception as e:
        logger.error(f"Katılım rozeti kontrolünde hata: {e}")


def check_and_award_quiz_badges(profile, category=None, correct_count=0, total_correct=0):
    """Quiz performansına göre rozetleri kontrol et ve ver"""
    try:
        # Kategori bazlı rozetler (50 doğru cevap)
        category_badge_map = {
            'spss': 'spss-uzmani',
            'python': 'python-ninja',
            'r': 'r-ustadi',
            'statistics': 'istatistik-ustasi',
        }

        if category and correct_count >= 50:
            badge_slug = category_badge_map.get(category)
            if badge_slug:
                badge = Badge.objects.filter(slug=badge_slug).first()
                if badge:
                    profile.badges.add(badge)

        # Quiz Efsanesi: 1000 toplam doğru
        if total_correct >= 1000:
            badge = Badge.objects.filter(slug='quiz-efsanesi').first()
            if badge:
                profile.badges.add(badge)

    except Exception as e:
        logger.error(f"Quiz rozeti kontrolünde hata: {e}")


def check_and_award_trust_badge(profile):
    """Güvenilir üye rozetini kontrol et ve ver"""
    try:
        if profile.email_verified and profile.phone_verified and profile.linkedin_verified:
            badge = Badge.objects.filter(slug='guvenilir-uye').first()
            if badge:
                profile.badges.add(badge)
                return True
        return False
    except Exception as e:
        logger.error(f"Güvenilir üye rozeti kontrolünde hata: {e}")
        return False


# Signal: Yeni konu açıldığında rozet kontrolü
@receiver(post_save, sender=Topic)
def check_topic_badges(sender, instance, created, **kwargs):
    """Yeni konu açıldığında rozet kontrolü"""
    if created:
        try:
            profile = instance.starter.profile
            check_and_award_participation_badges(profile)
        except Exception as e:
            logger.error(f"Konu rozeti kontrolünde hata: {e}")


# Signal: Yeni cevap verildiğinde rozet kontrolü
@receiver(post_save, sender=Post)
def check_post_badges(sender, instance, created, **kwargs):
    """Yeni cevap verildiğinde rozet kontrolü"""
    if created:
        try:
            profile = instance.created_by.profile
            check_and_award_participation_badges(profile)
            check_forum_hero_badge(profile)
        except Exception as e:
            logger.error(f"Cevap rozeti kontrolünde hata: {e}")


# Signal: Beğeni alındığında rozet kontrolü
@receiver(post_save, sender=PostLike)
def check_like_badges(sender, instance, created, **kwargs):
    """Beğeni alındığında rozet kontrolü"""
    if created:
        try:
            profile = instance.post.created_by.profile
            check_and_award_participation_badges(profile)
        except Exception as e:
            logger.error(f"Beğeni rozeti kontrolünde hata: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# İŞ İLANI TAMAMLANDIĞINDA BAŞARI HİKAYESİ DAVETİ
# ═══════════════════════════════════════════════════════════════════════════

@receiver(pre_save, sender=FreelanceJob)
def capture_old_job_status(sender, instance, **kwargs):
    """FreelanceJob kaydedilmeden önceki status'u yakala"""
    if instance.pk:
        try:
            old = FreelanceJob.objects.get(pk=instance.pk)
            instance._old_status = old.status
        except FreelanceJob.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=FreelanceJob)
def send_success_story_invitation(sender, instance, created, **kwargs):
    """İlan completed olduğunda ilan sahibi ve uzmana başarı hikayesi daveti gönder"""
    if created:
        return

    old_status = getattr(instance, '_old_status', None)
    if old_status == 'completed' or instance.status != 'completed':
        return

    # İlan sahibi
    owner = instance.owner

    # Kabul edilen teklifteki uzman
    accepted_proposal = instance.proposals.filter(status='accepted').first()
    expert = accepted_proposal.expert if accepted_proposal else None

    # AnalizBot kullanıcısını bul
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        bot_user = User.objects.get(username='AnalizBot')
    except User.DoesNotExist:
        logger.warning("AnalizBot kullanıcısı bulunamadı, başarı hikayesi daveti gönderilemedi.")
        return

    story_url = f"/success-stories/?job={instance.pk}"
    message_text = (
        f"Tebrikler! \"{instance.title}\" ilanı başarıyla tamamlandı. 🎉\n\n"
        f"Deneyiminizi toplulukla paylaşmak ister misiniz? "
        f"Başarı hikayenizi yazarak diğer kullanıcılara ilham verebilirsiniz.\n\n"
        f"👉 Hikayenizi yazmak için: {story_url}"
    )

    recipients = [owner]
    if expert and expert != owner:
        recipients.append(expert)

    for recipient in recipients:
        try:
            PrivateMessage.objects.create(
                sender=bot_user,
                receiver=recipient,
                message=message_text,
            )
            logger.info(f"Başarı hikayesi daveti gönderildi: {recipient.username} (iş: {instance.pk})")
        except Exception as e:
            logger.error(f"Başarı hikayesi daveti gönderilemedi ({recipient.username}): {e}")


# ═══════════════════════════════════════════════════════════════════════════
# GÜNLÜK GİRİŞ STREAK
# ═══════════════════════════════════════════════════════════════════════════

@receiver(user_logged_in)
def update_login_streak(sender, request, user, **kwargs):
    """Her girişte streak'i güncelle"""
    try:
        profile = user.profile
        today = tz.now().date()

        if profile.last_login_streak_date == today:
            return  # Bugün zaten güncellendi

        if profile.last_login_streak_date == today - timedelta(days=1):
            profile.login_streak += 1
        else:
            profile.login_streak = 1  # Seri kırıldı

        if profile.login_streak > profile.max_login_streak:
            profile.max_login_streak = profile.login_streak

        profile.last_login_streak_date = today
        profile.save(update_fields=['login_streak', 'max_login_streak', 'last_login_streak_date'])

        # Streak rozeti: 7 gün üst üste
        if profile.login_streak >= 7:
            badge = Badge.objects.filter(slug='haftalik-seri').first()
            if badge:
                profile.badges.add(badge)
        # Streak rozeti: 30 gün üst üste
        if profile.login_streak >= 30:
            badge = Badge.objects.filter(slug='aylik-seri').first()
            if badge:
                profile.badges.add(badge)
    except Exception as e:
        logger.error(f"Login streak güncellenemedi: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# ANALİZ YAPINCA PUAN + ROZET
# ═══════════════════════════════════════════════════════════════════════════

def check_and_award_istatistik_badges(profile, total_completed):
    """İstatistik analizine göre rozetleri kontrol et ve ver"""
    try:
        if total_completed >= 1:
            badge = Badge.objects.filter(slug='ilk-analiz').first()
            if badge:
                profile.badges.add(badge)
        if total_completed >= 10:
            badge = Badge.objects.filter(slug='analiz-ustasi').first()
            if badge:
                profile.badges.add(badge)
    except Exception as e:
        logger.error(f"İstatistik rozeti kontrolünde hata: {e}")


def on_istatistik_job_completed(job):
    """IstatistikJob tamamlandığında çağrılır — puan ve rozet ver"""
    try:
        if not job.user:
            return
        profile, _ = Profile.objects.get_or_create(user=job.user)
        profile.reputation += 5
        profile.save(update_fields=['reputation'])
        profile.update_rank()

        from istatistik.models import IstatistikJob
        total_completed = IstatistikJob.objects.filter(
            user=job.user, status='completed'
        ).count()
        check_and_award_istatistik_badges(profile, total_completed)
    except Exception as e:
        logger.error(f"İstatistik job tamamlanma işlemi başarısız: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# FORUM KAHRAMANI ROZETİ
# ═══════════════════════════════════════════════════════════════════════════

def check_forum_hero_badge(profile):
    """100 gönderide Forum Kahramanı rozetini ver"""
    try:
        if profile.user.posts.count() >= 100:
            badge = Badge.objects.filter(slug='forum-kahramani').first()
            if badge:
                profile.badges.add(badge)
    except Exception as e:
        logger.error(f"Forum Kahramanı rozeti kontrolünde hata: {e}")
