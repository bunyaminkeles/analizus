"""
E-posta gönderme servisi - Django Mail Backend
Django'nun EMAIL_BACKEND ayarını kullanarak e-posta gönderir.
Bu, arkadaki servisin (örn: AWS SES, SendGrid, SMTP) settings.py'dan değiştirilebilmesini sağlar.
"""
import os
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """E-posta gönderme işlemlerini yöneten servis (Django mail backend aracılığıyla)"""

    @staticmethod
    def is_configured():
        """E-posta gönderme altyapısının ayarlı olduğunu varsayarız."""
        # AWS S3 için kullanılan kimlik bilgileri SES için de geçerli olabilir.
        # Bu, e-posta özelliğinin aktif olup olmadığını kontrol eder.
        return bool(os.getenv('AWS_ACCESS_KEY_ID'))

    @staticmethod
    def get_base_url():
        """Site URL'sini döndürür"""
        return getattr(settings, 'SITE_URL', 'http://localhost:8000')

    @classmethod
    def _send_email(cls, to_email, subject, html_content, plain_content):
        """
        Django'nun send_mail fonksiyonunu kullanarak e-posta gönderir.
        EMAIL_BACKEND'de tanımlı olan servisi (örn: AWS SES) kullanır.
        """
        try:
            from_email = settings.DEFAULT_FROM_EMAIL
            
            send_mail(
                subject=subject,
                message=plain_content,
                from_email=from_email,
                recipient_list=[to_email],
                html_message=html_content,
                fail_silently=False,
            )
            
            logger.info(f"E-posta gönderildi: {to_email} (Konu: {subject})")
            return True

        except Exception as e:
            logger.error(f"E-posta gönderme hatası ({to_email}): {e}")
            return False

    @classmethod
    def send_verification_email(cls, user, verification_token):
        """Kullanıcıya e-posta doğrulama linki gönderir"""
        if not cls.is_configured():
            logger.warning(f"E-posta servisi yapılandırılmamış. Doğrulama maili gönderilemedi: {user.username}")
            return False

        verification_url = f"{cls.get_base_url()}/verify-email/{verification_token.token}/"
        context = {
            'user': user,
            'verification_url': verification_url,
            'site_name': 'Analizus',
            'expires_hours': 24,
        }
        subject = 'Analizus - E-posta Adresinizi Doğrulayın'
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
        if not cls.is_configured():
            logger.warning(f"E-posta servisi yapılandırılmamış. Hoş geldin maili gönderilemedi: {user.username}")
            return False
            
        context = {
            'user': user,
            'site_url': cls.get_base_url(),
            'site_name': 'Analizus',
        }
        subject = 'Analizus\'a Hoş Geldiniz!'
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
        plain_content = strip_tags(html_content)

        return cls._send_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content,
            plain_content=plain_content
        )