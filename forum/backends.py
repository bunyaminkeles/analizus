"""
Resend HTTP API email backend for Django.
Render SMTP portlarını blokluyor, bu yüzden HTTP API kullanıyoruz.
"""
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


class ResendBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        import resend
        resend.api_key = settings.RESEND_API_KEY

        sent = 0
        for msg in email_messages:
            try:
                params = {
                    "from": msg.from_email,
                    "to": list(msg.to),
                    "subject": msg.subject,
                    "text": msg.body,
                }
                # EmailMultiAlternatives'da HTML content olabilir
                for content, mimetype in getattr(msg, 'alternatives', []):
                    if mimetype == "text/html":
                        params["html"] = content
                # Attachment desteği
                if msg.attachments:
                    params["attachments"] = []
                    for attachment in msg.attachments:
                        filename, content, mimetype = attachment
                        if isinstance(content, str):
                            content = content.encode('utf-8')
                        params["attachments"].append({
                            "filename": filename,
                            "content": list(content),
                        })
                resend.Emails.send(params)
                sent += 1
            except Exception as e:
                if not self.fail_silently:
                    raise
        return sent
