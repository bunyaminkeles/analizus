"""
E-posta bildirim yardımcıları
"""
from django.core.mail import send_mail
from django.conf import settings
import threading
import logging

logger = logging.getLogger(__name__)


def send_email_async(subject, message, recipient_list, html_message=None):
    """
    Django'nun send_mail fonksiyonunu kullanarak arka planda e-posta gönderir.
    """
    def _send():
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                fail_silently=False,
                html_message=html_message
            )
            for recipient in recipient_list:
                logger.info(f"E-posta başarıyla gönderildi: {recipient}")
        except Exception as e:
            logger.error(f"E-posta gönderim hatası: {e}")

    thread = threading.Thread(target=_send, daemon=True)
    thread.start()


def send_topic_reply_notification(post, topic):
    """Bir konuya cevap yazıldığında konu sahibine email gönderir"""
    if post.created_by == topic.starter:
        return
    if not topic.starter.email:
        return
    if hasattr(topic.starter, 'profile') and not topic.starter.profile.email_on_reply:
        return

    subject = f"{post.created_by.username} konunuza cevap yazdı: {topic.subject}"
    message = f"""Merhaba {topic.starter.username},

"{topic.subject}" başlıklı konunuza yeni bir cevap geldi!

Cevap Yazan: {post.created_by.username}
Mesaj: {post.message[:200]}...

Cevabın tamamını görmek için:
https://analizus.com/topic/{topic.pk}/

---
Bu bir otomatik bildirimdir.
Analizus - Akademik Veri Üssü"""

    send_email_async(subject, message, [topic.starter.email])


def send_private_message_notification(sender, receiver, message_content):
    """Özel mesaj geldiğinde alıcıya email gönderir"""
    if not receiver.email:
        return
    if hasattr(receiver, 'profile') and not receiver.profile.email_on_private_message:
        return

    subject = f"{sender.username} size özel mesaj gönderdi"
    message = f"""Merhaba {receiver.username},

{sender.username} size yeni bir özel mesaj gönderdi!

Mesaj İçeriği:
{message_content[:300]}...

Mesajı okumak ve cevaplamak için:
https://analizus.com/inbox/

---
Bu bir otomatik bildirimdir.
Analizus - Akademik Veri Üssü"""

    send_email_async(subject, message, [receiver.email])


def send_mention_notification(mentioned_user, post, topic):
    """Bir mesajda @mention edildiğinde kullanıcıya email gönderir"""
    if not mentioned_user.email:
        return

    subject = f"{post.created_by.username} sizi bir tartışmada etiketledi"
    message = f"""Merhaba {mentioned_user.username},

{post.created_by.username} sizi "{topic.subject}" konusunda etiketledi!

Konuya gitmek için:
https://analizus.com/topic/{topic.pk}/

---
Analizus - Akademik Veri Üssü"""

    send_email_async(subject, message, [mentioned_user.email])
