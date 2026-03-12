"""
Pytest konfigürasyonu — testler SQLite kullanır, production DB'ye dokunmaz.
"""
import django
from django.conf import settings


def pytest_configure(config):
    """Test sürecinde DATABASE_URL'yi SQLite'a yönlendir."""
    import os
    os.environ['DATABASE_URL'] = 'sqlite:///test_db.sqlite3'
    os.environ.setdefault('CRON_SECRET_KEY', 'test-cron-secret')
    os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-pytest')
    os.environ.setdefault('DEBUG', 'True')
