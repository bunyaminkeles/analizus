from django.conf import settings
from django.core.mail import send_mail
import logging
import threading

logger = logging.getLogger(__name__)


def send_email_async(subject, message, recipient_list):
    """
    Email gönderimini arka planda thread ile yapar (request timeout olmasın).
    Django EMAIL_BACKEND ayarını kullanır (AWS SES veya başka backend).
    """
    def _send():
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            logger.info(f"E-posta gonderildi: {recipient_list}")
        except Exception as e:
            logger.error(f"E-posta gonderim hatasi ({recipient_list}): {e}")

    thread = threading.Thread(target=_send)
    thread.daemon = True
    thread.start()


def send_topic_reply_notification(post, topic):
    """Bir konuya cevap yazildiginda konu sahibine email gonderir"""
    if post.created_by == topic.starter:
        return
    if not topic.starter.email:
        return
    if hasattr(topic.starter, 'profile') and not topic.starter.profile.email_on_reply:
        return

    subject = f"{post.created_by.username} konunuza cevap yazdi: {topic.subject}"
    message = f"""Merhaba {topic.starter.username},

"{topic.subject}" baslikli konunuza yeni bir cevap geldi!

Cevap Yazan: {post.created_by.username}
Mesaj: {post.message[:200]}...

Cevabin tamamini gormek icin:
https://analizus.com/topic/{topic.pk}/

---
Bu bir otomatik bildirimdir.
Analizus - Akademik Veri Ussu"""

    send_email_async(subject, message, [topic.starter.email])


def send_private_message_notification(sender, receiver, message_content):
    """Ozel mesaj geldiginde aliciya email gonderir"""
    if not receiver.email:
        return
    if hasattr(receiver, 'profile') and not receiver.profile.email_on_private_message:
        return

    subject = f"{sender.username} size ozel mesaj gonderdi"
    message = f"""Merhaba {receiver.username},

{sender.username} size yeni bir ozel mesaj gonderdi!

Mesaj Icerigi:
{message_content[:300]}...

Mesaji okumak ve cevaplamak icin:
https://analizus.com/inbox/

---
Bu bir otomatik bildirimdir.
Analizus - Akademik Veri Ussu"""

    send_email_async(subject, message, [receiver.email])


def send_mention_notification(mentioned_user, post, topic):
    """Bir mesajda @mention edildiginde kullaniciya email gonderir"""
    if not mentioned_user.email:
        return

    subject = f"{post.created_by.username} sizi bir tartismada etiketledi"
    message = f"""Merhaba {mentioned_user.username},

{post.created_by.username} sizi "{topic.subject}" konusunda etiketledi!

Konuya gitmek icin:
https://analizus.com/topic/{topic.pk}/

---
Analizus - Akademik Veri Ussu"""

    send_email_async(subject, message, [mentioned_user.email])
