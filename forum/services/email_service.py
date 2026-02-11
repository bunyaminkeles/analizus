"""
E-posta gönderme servisi - SendGrid HTTP API
"""
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import requests
import logging
import threading

logger = logging.getLogger(__name__)

SENDGRID_API_URL = 'https://api.sendgrid.com/v3/mail/send'


class EmailService:
    """E-posta gönderme işlemlerini yöneten servis (SendGrid HTTP API)"""

    @staticmethod
    def is_configured():
        """SendGrid yapılandırılmış mı kontrol eder"""
        return bool(getattr(settings, 'SENDGRID_API_KEY', ''))

    @staticmethod
    def get_base_url():
        """Site URL'sini döndürür"""
        return getattr(settings, 'SITE_URL', 'http://localhost:8000')

    @classmethod
    def _send_email(cls, to_email, subject, html_content, plain_content):
        """SendGrid HTTP API ile e-posta gönderir (arka planda)"""
        from_email = settings.DEFAULT_FROM_EMAIL

        def _send():
            try:
                payload = {
                    "personalizations": [{"to": [{"email": to_email}]}],
                    "from": {"email": from_email, "name": "Analizus"},
                    "subject": subject,
                    "content": [
                        {"type": "text/plain", "value": plain_content},
                        {"type": "text/html", "value": html_content},
                    ]
                }
                headers = {
                    "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
                    "Content-Type": "application/json",
                }
                resp = requests.post(SENDGRID_API_URL, json=payload, headers=headers, timeout=10)

                if resp.status_code in (200, 202):
                    print(f"✅ E-posta gönderildi: {to_email}")
                    logger.info(f"E-posta gönderildi: {to_email}")
                else:
                    print(f"❌ SendGrid hatası ({to_email}): {resp.status_code} {resp.text}")
                    logger.error(f"SendGrid hatası ({to_email}): {resp.status_code} {resp.text}")
            except Exception as e:
                print(f"❌ E-posta gönderme hatası ({to_email}): {e}")
                logger.error(f"E-posta gönderme hatası ({to_email}): {e}")

        thread = threading.Thread(target=_send, daemon=True)
        thread.start()
        return True

    @classmethod
    def send_verification_email(cls, user, verification_token):
        """Kullanıcıya e-posta doğrulama linki gönderir"""
        verification_url = f"{cls.get_base_url()}/verify-email/{verification_token.token}/"

        context = {
            'user': user,
            'verification_url': verification_url,
            'site_name': 'Analizus',
            'expires_hours': 24,
        }

        subject = 'Analizus - E-posta Adresinizi Doğrulayın'

        if not cls.is_configured():
            print(f"⚠️ SendGrid yapılandırılmamış! SENDGRID_API_KEY boş. Kullanıcı: {user.username}")
            return False

        html_message = render_to_string('forum/emails/verification_email.html', context)
        plain_message = strip_tags(html_message)

        return cls._send_email(
            to_email=user.email,
            subject=subject,
            html_content=html_message,
            plain_content=plain_message
        )

    @classmethod
    def send_welcome_email(cls, user):
        """Doğrulama sonrası hoş geldin e-postası gönderir"""
        context = {
            'user': user,
            'site_url': cls.get_base_url(),
            'site_name': 'Analizus',
        }

        subject = 'Analizus\'a Hoş Geldiniz!'

        if not cls.is_configured():
            print(f"⚠️ SendGrid yapılandırılmamış! Hoş geldin e-postası gönderilemedi: {user.username}")
            return False

        html_message = render_to_string('forum/emails/welcome_email.html', context)
        plain_message = strip_tags(html_message)

        return cls._send_email(
            to_email=user.email,
            subject=subject,
            html_content=html_message,
            plain_content=plain_message
        )

    @classmethod
    def send_resend_verification_email(cls, user, verification_token):
        """Tekrar doğrulama e-postası gönderir"""
        return cls.send_verification_email(user, verification_token)

    @classmethod
    def send_edu_welcome_email(cls, user):
        """EDU mail ile giriş yapan kullanıcıya bilgilendirme maili"""
        if not cls.is_configured():
            return False

        subject = 'Analizus - Doğrulanmış Akademisyen Rozeti Kazandınız!'
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #0ea5e9;">Tebrikler {user.username}!</h2>
            <p>EDU uzantılı mail adresiniz ile giriş yaptığınız için <strong>Doğrulanmış Akademisyen</strong> rozeti kazandınız!</p>
            <p>Ayrıca <strong>3 gün boyunca teklif verme hakkına</strong> sahipsiniz.</p>
            <p>İyi çalışmalar,<br>Analizus Ekibi</p>
        </div>
        """
        plain_content = f"Tebrikler {user.username}! EDU mail ile giriş yaptığınız için Doğrulanmış Akademisyen rozeti kazandınız. 3 gün teklif verme hakkınız var."

        return cls._send_email(user.email, subject, html_content, plain_content)
