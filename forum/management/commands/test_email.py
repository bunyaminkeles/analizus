from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Sends a test email to the specified address to verify SMTP settings.'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='The recipient email address for the test.')

    def handle(self, *args, **kwargs):
        recipient_email = kwargs['email']
        self.stdout.write(self.style.WARNING(f"Attempting to send a test email to {recipient_email}..."))

        self.stdout.write("--- Using the following SMTP settings ---")
        self.stdout.write(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"EMAIL_HOST: {settings.EMAIL_HOST}")
        self.stdout.write(f"EMAIL_PORT: {settings.EMAIL_PORT}")
        self.stdout.write(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        self.stdout.write(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not Set')}")
        self.stdout.write(f"EMAIL_USE_SSL: {getattr(settings, 'EMAIL_USE_SSL', 'Not Set')}")
        self.stdout.write(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        self.stdout.write("-----------------------------------------")

        try:
            sent_count = send_mail(
                subject='[Analizus] Test Email',
                message='This is a test email from your Django application. If you received this, your SMTP settings are correct!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False,
            )
            if sent_count > 0:
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Successfully sent a test email to {recipient_email}!"
                ))
            else:
                 self.stdout.write(self.style.ERROR(
                    "❌ The command ran without errors, but send_mail() returned 0. The email was not sent."
                ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f"❌ Failed to send email. An error occurred:
"
            ))
            self.stdout.write(self.style.ERROR(str(e)))
            self.stdout.write(self.style.WARNING(
                "
Please double-check the SMTP environment variables in your Render dashboard. "
                "Common issues include incorrect password, host, port, or TLS/SSL settings."
            ))

