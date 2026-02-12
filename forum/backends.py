import base64
import logging
import re
import requests
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)


class SendGridBackend(BaseEmailBackend):
    """
    Django'nun send_mail / EmailMessage fonksiyonlarını SendGrid Web API'ye yönlendirir.
    Attachments desteği dahil.
    """
    def send_messages(self, email_messages):
        sent_count = 0
        for message in email_messages:
            if self._send(message):
                sent_count += 1
        return sent_count

    @staticmethod
    def _parse_from_email(raw):
        """'Display Name <email>' formatından email ve name'i ayırır"""
        match = re.match(r'^(.+?)\s*<(.+?)>$', raw)
        if match:
            return match.group(2).strip(), match.group(1).strip()
        return raw.strip(), 'Analizus'

    def _send(self, email_message):
        api_key = getattr(settings, 'SENDGRID_API_KEY', '')
        if not api_key:
            print(f"⚠️ SENDGRID_API_KEY ayarlanmamış! Email gönderilemedi: {email_message.to}")
            return False

        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        email_addr, sender_name = self._parse_from_email(email_message.from_email)
        data = {
            "personalizations": [{"to": [{"email": recipient} for recipient in email_message.to]}],
            "from": {"email": email_addr, "name": sender_name},
            "subject": email_message.subject,
            "content": [{"type": "text/plain", "value": email_message.body}]
        }

        # HTML içerik varsa ekle (EmailMultiAlternatives)
        if hasattr(email_message, 'alternatives'):
            for content, mimetype in email_message.alternatives:
                if mimetype == 'text/html':
                    data["content"].append({"type": "text/html", "value": content})
                    break

        # Attachment desteği
        if email_message.attachments:
            attachments = []
            for attachment in email_message.attachments:
                if isinstance(attachment, tuple) and len(attachment) == 3:
                    filename, content, mimetype = attachment
                    if isinstance(content, str):
                        content = content.encode('utf-8')
                    attachments.append({
                        "content": base64.b64encode(content).decode('ascii'),
                        "filename": filename,
                        "type": mimetype or "application/octet-stream",
                    })
            if attachments:
                data["attachments"] = attachments

        try:
            response = requests.post(url, headers=headers, json=data, timeout=15)
            if response.status_code in (200, 202):
                print(f"✅ Email gönderildi (backend): {email_message.to}")
                logger.info(f"Email gönderildi (backend): {email_message.to}")
                return True
            else:
                print(f"❌ SendGrid hatası (backend): {response.status_code} {response.text}")
                logger.error(f"SendGrid hatası (backend): {response.status_code} {response.text}")
                return False
        except Exception as e:
            print(f"❌ Email gönderim hatası (backend): {e}")
            logger.error(f"Email gönderim hatası (backend): {e}")
            return False
