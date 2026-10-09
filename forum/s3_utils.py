import logging
import boto3
from botocore.exceptions import ClientError
from django.conf import settings

logger = logging.getLogger(__name__)


def _get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )


def upload_to_s3(content, s3_key):
    """İçeriği S3'e yükler ve public URL döndürür."""
    try:
        s3 = _get_s3_client()
        s3.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=s3_key,
            Body=content.encode('utf-8'),
            ContentType='text/plain; charset=utf-8',
        )
        url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{s3_key}"
        logger.info(f"S3'e yüklendi: {url}")
        return url
    except ClientError as e:
        logger.error(f"S3 yükleme hatası: {e}")
        return None


def upload_bytes_to_s3(content_bytes: bytes, s3_key: str, content_type: str = 'application/octet-stream'):
    """Binary içeriği (PDF, PNG vb.) S3'e yükler ve public URL döndürür."""
    try:
        s3 = _get_s3_client()
        s3.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=s3_key,
            Body=content_bytes,
            ContentType=content_type,
        )
        url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{s3_key}"
        logger.info(f"S3'e yüklendi (binary): {url}")
        return url
    except ClientError as e:
        logger.error(f"S3 binary yükleme hatası: {e}")
        return None


def delete_from_s3(s3_key):
    """S3'den tek bir dosyayı siler."""
    try:
        s3 = _get_s3_client()
        s3.delete_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=s3_key,
        )
        logger.info(f"S3'den silindi: {s3_key}")
        return True
    except ClientError as e:
        logger.error(f"S3 silme hatası: {e}")
        return False


def cleanup_s3_prefix(prefix, days):
    """Verilen S3 prefix'i altında `days` günden eski dosyaları siler.
    Her prefix kendi try/except'inde çalışır — bir prefix'teki hata diğerlerini etkilemez
    (önceden tüm prefix'ler tek try/except içindeydi, biri patlayınca kalanlar o çalıştırmada atlanıyordu)."""
    from datetime import timedelta
    from django.utils import timezone

    deleted_count = 0
    cutoff = timezone.now() - timedelta(days=days)
    try:
        s3 = _get_s3_client()
        bucket = settings.AWS_STORAGE_BUCKET_NAME
        paginator = s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get('Contents', []):
                if obj['LastModified'] < cutoff:
                    s3.delete_object(Bucket=bucket, Key=obj['Key'])
                    deleted_count += 1
    except Exception as e:
        logger.error(f"S3 temizlik hatası ({prefix}): {e}")

    logger.info(f"S3 temizlik ({prefix}): {deleted_count} dosya silindi")
    return deleted_count
