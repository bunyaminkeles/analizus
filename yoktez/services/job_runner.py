import json
import threading
import logging
import uuid
from datetime import timedelta
import boto3
from botocore.exceptions import ClientError
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# Doğru banka bilgileri (bağış sistemiyle aynı)
BANK_INFO = {
    'hesap_sahibi': 'Bünyamin Keleş',
    'iban': 'TR73 0003 2000 0000 0079 1034 65',
}


def _get_s3_client():
    """Boto3 S3 client döndürür."""
    return boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )


def _generate_results_txt(tez_list, job, is_demo=True):
    """Tez sonuçlarını txt formatında oluşturur."""
    lines = [
        f"YÖK Tez Arama Sonuçları",
        f"{'='*60}",
        f"Bilim Alanı: {job.konu}",
        f"Anahtar Kelimeler: {', '.join(job.keywords)}",
        f"Toplam Bulunan Sonuç: {job.total_results}",
        f"Bu dosyadaki sonuç: {len(tez_list)} tez",
        f"{'='*60}\n",
    ]

    for i, tez in enumerate(tez_list, 1):
        lines.append(f"--- Tez #{i} ---")
        lines.append(f"Tez No    : {tez.get('tez_no', '')}")
        lines.append(f"Yıl       : {tez.get('yil', '')}")
        lines.append(f"Başlık    : {tez.get('baslik', '')}")
        lines.append(f"Üniversite: {tez.get('universite', '')}")
        lines.append(f"Tez Türü  : {tez.get('tez_turu', '')}")
        lines.append(f"Konu      : {tez.get('konu', '')}")
        if tez.get('ozet_tr'):
            lines.append(f"Özet (TR) : {tez['ozet_tr']}")
        if tez.get('ozet_en'):
            lines.append(f"Özet (EN) : {tez['ozet_en']}")
        lines.append("")

    lines.append(f"{'='*60}")
    lines.append(f"Toplam {job.total_results} tez bulundu.")
    if is_demo:
        lines.append(f"Daha fazla sonuç için epostanızdaki adımları takip ediniz.")
    lines.append(f"\n---\nAnalizus - www.analizus.com")

    return "\n".join(lines)


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


def run_scraping_job(job_id):
    """Background thread'de scraping job çalıştır."""

    def _run():
        from yoktez.models import TezSearchJob
        from yoktez.services.scraper import YokTezScraper

        try:
            job = TezSearchJob.objects.get(id=job_id)
            job.mark_running()

            scraper = YokTezScraper(headless=True)
            total_count, demo_results, all_results = scraper.search(
                konu=job.konu,
                keywords=job.keywords,
                demo_limit=3,
            )

            job.mark_completed(
                demo_results=demo_results,
                all_results=all_results,
                total_count=total_count,
            )

            # Sonuçları txt olarak S3'e yükle
            try:
                # Demo sonuçları (3 tez)
                demo_txt = _generate_results_txt(demo_results, job, is_demo=True)
                demo_s3_key = f"yoktez/demo/{job.id}.txt"
                demo_s3_url = upload_to_s3(demo_txt, demo_s3_key)

                # TÜM sonuçları da S3'e yükle
                all_txt = _generate_results_txt(all_results, job, is_demo=False)
                all_s3_key = f"yoktez/full/{job.id}.txt"
                all_s3_url = upload_to_s3(all_txt, all_s3_key)

                update_fields = []
                if demo_s3_url:
                    job.demo_file_url = demo_s3_url
                    update_fields.append('demo_file_url')
                if all_s3_url:
                    job.all_results_file_url = all_s3_url
                    update_fields.append('all_results_file_url')
                if update_fields:
                    job.save(update_fields=update_fields)
            except Exception as e:
                logger.error(f"S3 yükleme hatası: {e}")

            logger.info(f"Scraping job {job_id} tamamlandı: {total_count} sonuç")

        except Exception as e:
            logger.error(f"Scraping job {job_id} başarısız: {e}")
            try:
                job = TezSearchJob.objects.get(id=job_id)
                job.mark_failed(str(e))
            except Exception:
                pass

    thread = threading.Thread(target=_run)
    thread.daemon = True
    thread.start()


def send_demo_email_async(job_id):
    """Background thread'de demo email gönder."""
    def _run():
        from yoktez.models import TezSearchJob
        logger.info(f"[async_email] Starting background email task for job {job_id}")
        try:
            job = TezSearchJob.objects.get(id=job_id)
            logger.info(f"[async_email] Found job {job_id}, calling send_demo_email.")
            send_demo_email(job)

        except TezSearchJob.DoesNotExist:
            logger.error(f"[async_email] Job not found: {job_id}")
        except Exception as e:
            logger.error(f"[async_email] Unhandled exception in email thread for job {job_id}: {e}", exc_info=True)

    thread = threading.Thread(target=_run)
    thread.daemon = True
    thread.start()
    logger.info(f"[async_email] Email task for job {job_id} has been started in the background.")


def send_demo_email(job):
    """Demo sonuçları txt dosyası olarak kullanıcının emailine gönder.
    Email body'de tez bilgileri açık olarak yer almaz, txt ek olarak gönderilir."""
    user = job.user
    to_email = user.email

    if not to_email:
        logger.warning(f"Kullanıcının emaili yok: {user.username}")
        return False

    subject = f"YÖK Tez Arama - Demo Sonuçlar: {job.konu}"

    # Txt dosya içeriğini oluştur
    txt_content = _generate_results_txt(job.demo_results, job, is_demo=True)

    # Email body: Tez bilgileri açık olarak YER ALMAZ
    lines = [
        f"Merhaba {user.first_name or user.username},\n",
        f"YÖK Tez Tarama aracıyla yaptığınız arama sonuçları hazırlanmıştır.\n",
        f"Bilim Alanı: {job.konu}",
        f"Anahtar Kelimeler: {', '.join(job.keywords)}",
        f"Toplam Bulunan Sonuç: {job.total_results}",
        f"Demo Sonuç: {len(job.demo_results)} tez\n",
        f"Demo sonuçlar bu e-postaya txt dosyası olarak eklenmiştir.\n",
    ]

    # Toplam tez sayısına göre fiyat hesapla
    from yoktez.models import TezOrder
    total_price = TezOrder.calculate_price(job.total_results)

    lines.append(f"{'='*60}")
    lines.append(f"\n--- TÜM SONUÇLARI ALMAK İÇİN ---\n")
    lines.append(f"Toplam {job.total_results} abstract için tahmini ücret: {total_price} TL\n")
    lines.append(f"Fiyatlandırma:")
    lines.append(f"  * İlk 100 abstract  : 250 TL")
    lines.append(f"  * Sonraki her 100   : +100 TL")
    lines.append(f"")
    lines.append(f"Banka Bilgileri:")
    lines.append(f"  Hesap Sahibi : {BANK_INFO['hesap_sahibi']}")
    lines.append(f"  IBAN         : {BANK_INFO['iban']}")
    lines.append(f"  Açıklama     : YÖK Tez - {user.username}")
    lines.append(f"")
    site_url = getattr(settings, 'SITE_URL', 'https://www.analizus.com')
    lines.append(f"Ödeme yaptıktan sonra siparişinizi oluşturun:")
    lines.append(f"  {site_url}/yoktez/siparis/{job.id}/")
    lines.append(f"")
    lines.append(f"Siparişiniz onaylandıktan sonra sonuçlar 24 saat")
    lines.append(f"içinde bu e-posta adresine gönderilecektir.")
    lines.append(f"\n---\nAnalizus - {site_url}")

    body = "\n".join(lines)

    try:
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        email.attach(
            f"yoktez_demo_{job.konu}.txt",
            txt_content,
            'text/plain',
        )
        email.send()

        job.demo_email_sent = True
        job.save(update_fields=['demo_email_sent'])
        logger.info(f"Demo email gönderildi: {to_email}")
        return True
    except Exception as e:
        logger.error(f"Demo email gönderilemedi: {e}")
        return False


def send_order_results_email(order):
    """Onaylanan siparişin tüm sonuçlarını txt dosyası olarak S3'e yükleyip kullanıcıya gönder."""
    user = order.user
    job = order.search_job
    to_email = user.email

    if not to_email:
        return False

    subject = f"YÖK Tez Arama Sonuçları: {job.konu} - {', '.join(job.keywords)}"

    # İstenen sayıda sonucu al
    results_to_send = job.all_results[:order.abstract_count]

    # Txt dosya oluştur
    txt_content = _generate_results_txt(results_to_send, job, is_demo=False)

    # S3'e yükle
    s3_key = f"yoktez/orders/{order.id}.txt"
    s3_url = upload_to_s3(txt_content, s3_key)

    lines = [
        f"Merhaba {user.first_name or user.username},\n",
        f"Siparişiniz onaylanmış ve tez sonuçlarınız hazırlanmıştır.\n",
        f"Sipariş No: #{str(order.id)[:8]}",
        f"Bilim Alanı: {job.konu}",
        f"Anahtar Kelimeler: {', '.join(job.keywords)}",
        f"Toplam Sonuç: {job.total_results}",
        f"Gönderilen Abstract: {order.abstract_count}",
        f"Ödenen Tutar: {order.total_price} TL\n",
    ]

    if s3_url:
        lines.append(f"Sonuçlarınızı aşağıdaki linkten indirebilirsiniz:")
        lines.append(f"  {s3_url}\n")

    lines.append(f"Sonuçlar ayrıca bu e-postaya txt dosyası olarak eklenmiştir.")
    lines.append(f"\n---\nAnalizus - www.analizus.com")

    body = "\n".join(lines)

    try:
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        email.attach(
            f"yoktez_{job.konu}_{len(results_to_send)}_sonuc.txt",
            txt_content,
            'text/plain',
        )
        email.send()

        order.results_email_sent = True
        order.results_email_sent_at = timezone.now()
        order.status = 'completed'
        order.save(update_fields=['results_email_sent', 'results_email_sent_at', 'status'])

        logger.info(f"Sipariş sonuçları gönderildi: {to_email} ({order.abstract_count} abstract)")
        return True
    except Exception as e:
        logger.error(f"Sipariş email gönderilemedi: {e}")
        return False


def check_overdue_orders():
    """24 saat geçmiş onaylı ama gönderilmemiş siparişler için admin'i uyar."""
    from yoktez.models import TezOrder

    cutoff = timezone.now() - timedelta(hours=24)
    overdue = TezOrder.objects.filter(
        status='approved',
        approved_at__lt=cutoff,
        results_email_sent=False,
    )

    if not overdue.exists():
        return

    lines = [
        "UYARI: Aşağıdaki YÖK Tez siparişleri 24 saati aşmış ve henüz gönderilmemiştir:\n",
    ]
    for order in overdue:
        lines.append(f"  - Sipariş #{str(order.id)[:8]}")
        lines.append(f"    Kullanıcı: {order.user.username} ({order.user.email})")
        lines.append(f"    Konu: {order.search_job.konu}")
        lines.append(f"    Abstract: {order.abstract_count}")
        lines.append(f"    Onay Tarihi: {order.approved_at.strftime('%d/%m/%Y %H:%M')}")
        lines.append("")

    body = "\n".join(lines)

    try:
        email = EmailMessage(
            subject=f"[UYARI] {overdue.count()} YÖK Tez siparişi 24 saati aştı!",
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=['info@analizus.com'],
        )
        email.send()
        logger.warning(f"{overdue.count()} gecikmiş sipariş için admin uyarısı gönderildi")
    except Exception as e:
        logger.error(f"Admin uyarı emaili gönderilemedi: {e}")


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


def cleanup_expired_s3_files(days=3):
    """3 günden eski yoktez/ altındaki tüm dosyaları S3'den siler.
    DB'ye değil, S3'deki dosya tarihine bakar."""
    deleted_count = 0
    cutoff = timezone.now() - timedelta(days=days)

    try:
        s3 = _get_s3_client()
        bucket = settings.AWS_STORAGE_BUCKET_NAME

        for prefix in ['yoktez/demo/', 'yoktez/full/', 'yoktez/orders/']:
            paginator = s3.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
                for obj in page.get('Contents', []):
                    last_modified = obj['LastModified']
                    # timezone-aware karşılaştırma
                    if last_modified < cutoff:
                        s3.delete_object(Bucket=bucket, Key=obj['Key'])
                        logger.info(f"S3 temizlik: silindi {obj['Key']}")
                        deleted_count += 1
    except Exception as e:
        logger.error(f"S3 temizlik hatası (yoktez): {e}")

    # DB'deki URL referanslarını da temizle
    try:
        from yoktez.models import TezSearchJob
        TezSearchJob.objects.filter(
            created_at__lt=cutoff,
        ).exclude(
            demo_file_url='', all_results_file_url=''
        ).update(demo_file_url='', all_results_file_url='')
    except Exception as e:
        logger.error(f"DB temizlik hatası (yoktez): {e}")

    logger.info(f"S3 temizlik (yoktez): {deleted_count} dosya silindi")
    return deleted_count
