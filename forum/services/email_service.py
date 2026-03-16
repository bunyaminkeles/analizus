"""
E-posta gönderme servisi - Django Mail
"""
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core.mail import send_mail
import logging
import threading

logger = logging.getLogger(__name__)


class EmailService:
    """E-posta gönderme işlemlerini yöneten servis (Django Mail)"""

    @staticmethod
    def is_configured():
        """E-posta ayarlarının yapılıp yapılmadığını kontrol eder"""
        # Resend HTTP API kullanılıyorsa (Render ortamı)
        if getattr(settings, 'RESEND_API_KEY', None):
            return True
        # SMTP kullanılıyorsa (lokal ortam)
        return all([
            settings.EMAIL_HOST,
            settings.EMAIL_PORT,
            settings.EMAIL_HOST_USER,
            settings.EMAIL_HOST_PASSWORD
        ])

    @staticmethod
    def get_base_url():
        """Site URL'sini döndürür"""
        return getattr(settings, 'SITE_URL', 'http://localhost:8000')

    @classmethod
    def _send_email(cls, to_email, subject, html_content, plain_content):
        """Django'nun send_mail fonksiyonunu kullanarak arka planda e-posta gönderir."""
        
        def _send():
            try:
                send_mail(
                    subject,
                    plain_content,
                    settings.DEFAULT_FROM_EMAIL,
                    [to_email],
                    html_message=html_content,
                    fail_silently=False
                )
                logger.info(f"E-posta gönderildi: {to_email}")
            except Exception as e:
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
            logger.warning(f"E-posta ayarları yapılmamış! Doğrulama maili gönderilemedi. Kullanıcı: {user.username}")
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
            logger.warning(f"E-posta ayarları yapılmamış! Hoş geldin e-postası gönderilemedi: {user.username}")
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
