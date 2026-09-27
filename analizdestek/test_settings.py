"""
Test ortamı için Django settings.
Production DB'ye bağlanmaz — SQLite kullanır.
"""
from .settings import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}

# Test'te hızlı şifre hash
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

# Email'i bellekte tut (gönderme)
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Cron secret
import os
os.environ.setdefault('CRON_SECRET_KEY', 'test-cron-secret')

# Statik: testler collectstatic manifest'ine bağımlı olmasın (Django testleri DEBUG=False
# çalıştırır → manifest storage hash'li ad ister, manifest yoksa her sayfa 500 olur).
STORAGES = {
    **STORAGES,
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}
