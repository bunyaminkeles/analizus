import requests
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

class SendGridBackend(BaseEmailBackend):
    """
    Django'nun send_mail fonksiyonunu SendGrid Web API'ye yönlendirir.
    """
    def send_messages(self, email_messages):
        sent_count = 0
        for message in email_messages:
            if self._send(message):
                sent_count += 1
        return sent_count

    def _send(self, email_message):
        if not settings.SENDGRID_API_KEY:
            return False
        
        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "personalizations": [{"to": [{"email": recipient} for recipient in email_message.to]}],
            "from": {"email": email_message.from_email},
            "subject": email_message.subject,
            "content": [{"type": "text/plain", "value": email_message.body}]
        }
        
        # HTML içerik varsa ekle
        if hasattr(email_message, 'alternatives'):
            for content, mimetype in email_message.alternatives:
                if mimetype == 'text/html':
                    data["content"].append({"type": "text/html", "value": content})
                    break
        
        try:
            response = requests.post(url, headers=headers, json=data)
            return response.status_code in [200, 201, 202]
        except:
            return False