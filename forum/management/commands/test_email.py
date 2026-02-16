from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Sends a test email to the specified address.'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='The recipient email address.')

    def handle(self, *args, **options):
        recipient_email = options['email']
        self.stdout.write(f"Attempting to send a test email to {recipient_email}...")
        self.stdout.write("Using settings:")
        self.stdout.write(f"  EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
        self.stdout.write(f"  EMAIL_PORT: {settings.EMAIL_PORT}")
        self.stdout.write(f"  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        self.stdout.write(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        self.stdout.write(f"  EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
        self.stdout.write(f"  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")

        try:
            send_mail(
                subject='Test Email from Analizus',
                message='This is a test email to verify SMTP settings.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS('✅ Test email sent successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to send email: {e}'))
            self.stderr.write(f"Error details: {e}")