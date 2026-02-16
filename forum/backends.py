"""
Resend HTTP API email backend for Django.
Render SMTP portlarını blokluyor, bu yüzden HTTP API kullanıyoruz.
"""
import resend
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


class ResendBackend(BaseEmailBackend):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        resend.api_key = settings.RESEND_API_KEY

    def send_messages(self, email_messages):
        sent = 0
        for msg in email_messages:
            try:
                params = {
                    "from": msg.from_email,
                    "to": list(msg.to),
                    "subject": msg.subject,
                    "text": msg.body,
                }
                if msg.alternatives:
                    for content, mimetype in msg.alternatives:
                        if mimetype == "text/html":
                            params["html"] = content
                resend.Emails.send(params)
                sent += 1
            except Exception as e:
                if not self.fail_silently:
                    raise
        return sent
