from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
import logging
from .utils import send_realtime_notification

logger = logging.getLogger(__name__)

from .models import Post, PrivateMessage, Notification, PostLike, Topic, Badge
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


@receiver(post_save, sender=PrivateMessage)
def private_message_post_save(sender, instance, created, **kwargs):
    """Yeni özel mesaj geldiğinde bildirim gönder"""
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

            # Gerçek zamanlı bildirim (opsiyonel)
            send_realtime_notification(recipient.id, message, url)
        except Exception as e:
            logger.error(f"Özel mesaj bildirimi oluşturulamadı: {e}")


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

        # Yardımsever: 10 soruya cevap verdi
        if user.posts.count() >= 10:
            badge = Badge.objects.filter(slug='yardimsever').first()
            if badge:
                profile.badges.add(badge)

        # Konu Açıcı: 5 konu açtı
        if user.topics.count() >= 5:
            badge = Badge.objects.filter(slug='konu-acici').first()
            if badge:
                profile.badges.add(badge)

        # En İyi Cevap: Bir cevabı "En Faydalı" seçildi
        if user.posts.filter(is_best_answer=True).exists():
            badge = Badge.objects.filter(slug='en-iyi-cevap').first()
            if badge:
                profile.badges.add(badge)

        # Çözüm Ustası: 10 kez "En Faydalı Cevap"
        best_answer_count = user.posts.filter(is_best_answer=True).count()
        if best_answer_count >= 10:
            badge = Badge.objects.filter(slug='cozum-ustasi').first()
            if badge:
                profile.badges.add(badge)

        # Popüler Yazar: Bir konusu 1000+ görüntülendi
        if user.topics.filter(views__gte=1000).exists():
            badge = Badge.objects.filter(slug='populer-yazar').first()
            if badge:
                profile.badges.add(badge)

        # Beğenilen Yazar: Toplam 50 beğeni aldı
        total_likes = sum(p.likes for p in user.posts.all())
        if total_likes >= 50:
            badge = Badge.objects.filter(slug='begenilen-yazar').first()
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
        # Kategori bazlı rozetler (10 doğru cevap)
        category_badge_map = {
            'spss': 'spss-uzmani',
            'python': 'python-ninja',
            'r': 'r-ustadi',
            'statistics': 'istatistik-ustasi',
            'methodology': 'metodoloji-gurusu',
        }

        if category and correct_count >= 10:
            badge_slug = category_badge_map.get(category)
            if badge_slug:
                badge = Badge.objects.filter(slug=badge_slug).first()
                if badge:
                    profile.badges.add(badge)

        # Quiz Şampiyonu: 100 toplam doğru
        if total_correct >= 100:
            badge = Badge.objects.filter(slug='quiz-sampiyonu').first()
            if badge:
                profile.badges.add(badge)

        # Quiz Efsanesi: 500 toplam doğru
        if total_correct >= 500:
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
