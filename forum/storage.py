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


def get_attachment_storage():
    """
    Kullanıcı tarafından yüklenen serbest ekler (DM/çalışma odası dosyaları)
    için storage. Content-Type istemci tarafından bildirildiği için
    sahteciliğe açık; S3'te Content-Disposition: attachment zorlanarak
    tarayıcının içeriği (gerçek tipi ne olursa olsun) inline render etmesi
    engellenir, yalnızca indirilir.
    """
    if not settings.DEBUG and getattr(settings, 'AWS_ACCESS_KEY_ID', None):
        from storages.backends.s3boto3 import S3Boto3Storage
        return S3Boto3Storage(object_parameters={'ContentDisposition': 'attachment'})
    else:
        from django.core.files.storage import FileSystemStorage
        return FileSystemStorage()
