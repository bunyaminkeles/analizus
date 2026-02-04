"""
Dinamik storage backend seçimi
Production'da S3, development'ta FileSystem kullanır
"""
from django.conf import settings


def get_storage():
    """
    Ayarlara göre doğru storage backend'ini döndürür.
    Model field'larında storage=get_storage olarak kullanılır.
    """
    if not settings.DEBUG and getattr(settings, 'AWS_ACCESS_KEY_ID', None):
        from storages.backends.s3boto3 import S3Boto3Storage
        return S3Boto3Storage()
    else:
        from django.core.files.storage import FileSystemStorage
        return FileSystemStorage()
