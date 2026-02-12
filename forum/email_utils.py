"""
E-posta bildirim yardımcıları - SendGrid HTTP API
"""
from django.conf import settings
import requests
import logging
import threading

logger = logging.getLogger(__name__)

SENDGRID_API_URL = 'https://api.sendgrid.com/v3/mail/send'


def send_email_async(subject, message, recipient_list):
    """
    SendGrid HTTP API ile arka planda email gönderir.
    """
    api_key = getattr(settings, 'SENDGRID_API_KEY', '')
    if not api_key:
        print(f"⚠️ SENDGRID_API_KEY ayarlanmamış! Email gönderilemedi: {recipient_list}")
        logger.warning(f"SENDGRID_API_KEY ayarlanmamış! Email gönderilemedi: {recipient_list}")
        return

    from_email = settings.DEFAULT_FROM_EMAIL

    def _send():
        for to_email in recipient_list:
            try:
                payload = {
                    "personalizations": [{"to": [{"email": to_email}]}],
                    "from": {"email": from_email, "name": "Analizus"},
                    "subject": subject,
                    "content": [
                        {"type": "text/plain", "value": message},
                    ]
                }
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }
                resp = requests.post(SENDGRID_API_URL, json=payload, headers=headers, timeout=10)

                if resp.status_code in (200, 202):
                    print(f"✅ Bildirim e-postası gönderildi: {to_email}")
                    logger.info(f"Bildirim e-postası gönderildi: {to_email}")
                else:
                    print(f"❌ SendGrid hatası ({to_email}): {resp.status_code} {resp.text}")
                    logger.error(f"SendGrid hatası ({to_email}): {resp.status_code} {resp.text}")
            except Exception as e:
                print(f"❌ E-posta gönderim hatası ({to_email}): {e}")
                logger.error(f"E-posta gönderim hatası ({to_email}): {e}")

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
