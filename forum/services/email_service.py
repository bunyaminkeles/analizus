"""
E-posta gönderme servisi
Django'nun email backend'i üzerinden gönderim (Gmail SMTP / AWS SES)
"""
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings
import logging
import threading

logger = logging.getLogger(__name__)


class EmailService:
    """E-posta gönderme işlemlerini yöneten servis"""

    @staticmethod
    def is_configured():
        """E-posta backend'inin yapılandırılıp yapılandırılmadığını kontrol eder"""
        backend = getattr(settings, 'EMAIL_BACKEND', '')
        if 'ses' in backend.lower():
            return bool(getattr(settings, 'AWS_ACCESS_KEY_ID', ''))
        # SMTP backend (Gmail vb.)
        return bool(getattr(settings, 'EMAIL_HOST_USER', ''))

    @staticmethod
    def get_base_url():
        """Site URL'sini döndürür"""
        return getattr(settings, 'SITE_URL', 'http://localhost:8000')

    @classmethod
    def _send_email(cls, to_email, subject, html_content, plain_content):
        """
        Django email backend ile e-posta gönderir (arka planda)

        Args:
            to_email: Alıcı e-posta adresi
            subject: E-posta konusu
            html_content: HTML içerik
            plain_content: Düz metin içerik

        Returns:
            bool: Gönderim başlatıldı mı
        """
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@analizus.com')

        def _send():
            try:
                send_mail(
                    subject=subject,
                    message=plain_content,
                    from_email=from_email,
                    recipient_list=[to_email],
                    html_message=html_content,
                    fail_silently=False,
                )
                logger.info(f"E-posta gönderildi: {to_email}")
            except Exception as e:
                logger.error(f"E-posta gönderme hatası ({to_email}): {e}")

        thread = threading.Thread(target=_send, daemon=True)
        thread.start()
        return True

    @classmethod
    def send_verification_email(cls, user, verification_token):
        """
        Kullanıcıya e-posta doğrulama linki gönderir

        Args:
            user: User modeli instance
            verification_token: EmailVerification modeli instance

        Returns:
            bool: Gönderim başarılı mı
        """
        verification_url = f"{cls.get_base_url()}/verify-email/{verification_token.token}/"

        context = {
            'user': user,
            'verification_url': verification_url,
            'site_name': 'Analizus',
            'expires_hours': 24,
        }

        subject = 'Analizus - E-posta Adresinizi Doğrulayın'

        # E-posta yapılandırılmamışsa skip et
        if not cls.is_configured():
            logger.warning(f"E-posta yapılandırılmamış. Kullanıcı: {user.username}")
            return False

        # HTML template
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
        """
        Doğrulama sonrası hoş geldin e-postası gönderir

        Args:
            user: User modeli instance

        Returns:
            bool: Gönderim başarılı mı
        """
        context = {
            'user': user,
            'site_url': cls.get_base_url(),
            'site_name': 'Analizus',
        }

        subject = 'Analizus\'a Hoş Geldiniz!'

        # E-posta yapılandırılmamışsa skip et
        if not cls.is_configured():
            logger.warning(f"E-posta yapılandırılmamış. Hoş geldin e-postası gönderilemedi: {user.username}")
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
        """
        Tekrar doğrulama e-postası gönderir (kullanıcı talep ettiğinde)

        Args:
            user: User modeli instance
            verification_token: EmailVerification modeli instance

        Returns:
            bool: Gönderim başarılı mı
        """
        # Aynı verification_email fonksiyonunu kullanabiliriz
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
