from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os


class Command(BaseCommand):
    help = 'Otomatik admin oluşturur veya şifresini günceller'

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "bunyamin")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@analizus.com")
        password = os.getenv("ADMIN_PASSWORD") or os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if not password:
            self.stdout.write(self.style.ERROR(
                'ADMIN_PASSWORD veya DJANGO_SUPERUSER_PASSWORD env variable ayarlanmamış!'
            ))
            return

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS(f'Admin "{username}" oluşturuldu.'))
        else:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Admin "{username}" şifresi güncellendi.'))
