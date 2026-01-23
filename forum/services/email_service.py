"""
E-posta gönderme servisi - SendGrid Web API
Render.com'un SMTP engelini aşmak için HTTP tabanlı API kullanılıyor
"""
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """E-posta gönderme işlemlerini yöneten servis (SendGrid Web API)"""

    @staticmethod
    def is_configured():
        """SendGrid API key'in yapılandırılıp yapılandırılmadığını kontrol eder"""
        return bool(getattr(settings, 'SENDGRID_API_KEY', ''))

    @staticmethod
    def get_base_url():
        """Site URL'sini döndürür"""
        return getattr(settings, 'SITE_URL', 'http://localhost:8000')

    @classmethod
    def _send_email_via_sendgrid(cls, to_email, subject, html_content, plain_content):
        """
        SendGrid Web API ile e-posta gönderir (SMTP yerine HTTP)

        Args:
            to_email: Alıcı e-posta adresi
            subject: E-posta konusu
            html_content: HTML içerik
            plain_content: Düz metin içerik

        Returns:
            bool: Gönderim başarılı mı
        """
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail

            api_key = getattr(settings, 'SENDGRID_API_KEY', '')
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@analizus.com')

            message = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content,
                plain_text_content=plain_content
            )

            sg = SendGridAPIClient(api_key)
            response = sg.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"SendGrid ile e-posta gönderildi: {to_email} (status: {response.status_code})")
                return True
            else:
                logger.error(f"SendGrid hata döndürdü: {response.status_code} - {response.body}")
                return False

        except ImportError:
            logger.error("SendGrid paketi yüklü değil. 'pip install sendgrid' çalıştırın.")
            return False
        except Exception as e:
            # SendGrid'den dönen detaylı hata mesajını logla (403 nedenini görmek için)
            if hasattr(e, 'body'):
                try:
                    # Hata gövdesi genellikle bytes formatındadır
                    error_body = e.body.decode('utf-8')
                    logger.error(f"SendGrid API Hata Detayı: {error_body}")
                    print(f"SendGrid API Hata Detayı: {error_body}")
                except Exception:
                    pass
            logger.error(f"SendGrid e-posta gönderme hatası ({to_email}): {e}")
            return False

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
            logger.warning(f"SendGrid API key yapılandırılmamış. Kullanıcı: {user.username}")
            return False

        # HTML template
        html_message = render_to_string('forum/emails/verification_email.html', context)
        plain_message = strip_tags(html_message)

        return cls._send_email_via_sendgrid(
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
            logger.warning(f"SendGrid API key yapılandırılmamış. Hoş geldin e-postası gönderilemedi: {user.username}")
            return False

        html_message = render_to_string('forum/emails/welcome_email.html', context)
        plain_message = strip_tags(html_message)

        return cls._send_email_via_sendgrid(
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
