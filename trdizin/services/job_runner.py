import threading
import logging
import boto3
from botocore.exceptions import ClientError
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

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


def _generate_results_txt(results, job, is_demo=True):
    """Yayın sonuçlarını txt formatında oluşturur."""
    query_summary = job.get_query_summary() if hasattr(job, 'get_query_summary') else job.lucene_query
    lines = [
        f"TR Dizin Yayın Arama Sonuçları",
        f"{'='*60}",
        f"Sorgu: {query_summary}",
        f"Toplam Bulunan Sonuç: {job.total_results}",
        f"Bu dosyadaki sonuç: {len(results)} yayın",
        f"{'='*60}\n",
    ]

    for i, pub in enumerate(results, 1):
        lines.append(f"--- Yayın #{i} ---")
        lines.append(f"Başlık     : {pub.get('title', '')}")
        lines.append(f"Yazarlar   : {pub.get('authors', '')}")
        lines.append(f"Yıl        : {pub.get('year', '')}")
        lines.append(f"Dergi      : {pub.get('journal', '')}")
        if pub.get('doi'):
            lines.append(f"DOI        : {pub['doi']}")
        if pub.get('publication_type'):
            lines.append(f"Yayın Türü : {pub['publication_type']}")
        if pub.get('access_type'):
            lines.append(f"Erişim     : {pub['access_type']}")
        if pub.get('keywords_tr'):
            lines.append(f"Anahtar Kel: {', '.join(pub['keywords_tr'])}")
        if pub.get('abstract_tr'):
            lines.append(f"Özet (TR)  : {pub['abstract_tr']}")
        if pub.get('abstract_en'):
            lines.append(f"Abstract   : {pub['abstract_en']}")
        lines.append("")

    lines.append(f"{'='*60}")
    lines.append(f"Toplam {job.total_results} yayın bulundu.")
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
    """Background thread'de TR Dizin arama job'ı çalıştır."""

    def _run():
        from trdizin.models import DizinSearchJob
        from trdizin.services.scraper import TRDizinScraper

        try:
            job = DizinSearchJob.objects.get(id=job_id)
            job.mark_running()

            scraper = TRDizinScraper()
            total_count, demo_results, all_results, lucene_query = scraper.search(
                query_parts=job.query_parts,
                demo_limit=3,
            )

            # Lucene sorgusunu kaydet
            job.lucene_query = lucene_query
            job.save(update_fields=['lucene_query'])

            job.mark_completed(
                demo_results=demo_results,
                all_results=all_results,
                total_count=total_count,
            )

            # Sonuçları txt olarak S3'e yükle
            try:
                demo_txt = _generate_results_txt(demo_results, job, is_demo=True)
                demo_s3_key = f"trdizin/demo/{job.id}.txt"
                demo_s3_url = upload_to_s3(demo_txt, demo_s3_key)

                all_txt = _generate_results_txt(all_results, job, is_demo=False)
                all_s3_key = f"trdizin/full/{job.id}.txt"
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

            logger.info(f"TR Dizin job {job_id} tamamlandı: {total_count} sonuç")

        except Exception as e:
            logger.error(f"TR Dizin job {job_id} başarısız: {e}")
            try:
                job = DizinSearchJob.objects.get(id=job_id)
                job.mark_failed(str(e))
            except Exception:
                pass

    thread = threading.Thread(target=_run)
    thread.daemon = True
    thread.start()


def send_demo_email(job):
    """Demo sonuçları txt dosyası olarak kullanıcının emailine gönder."""
    user = job.user
    to_email = user.email

    if not to_email:
        logger.warning(f"Kullanıcının emaili yok: {user.username}")
        return False

    query_summary = job.get_query_summary()
    subject = f"TR Dizin Yayın Arama - Demo Sonuçlar"

    txt_content = _generate_results_txt(job.demo_results, job, is_demo=True)

    lines = [
        f"Merhaba {user.first_name or user.username},\n",
        f"TR Dizin Yayın Tarama aracıyla yaptığınız arama sonuçları hazırlanmıştır.\n",
        f"Sorgu: {query_summary}",
        f"Toplam Bulunan Sonuç: {job.total_results}",
        f"Demo Sonuç: {len(job.demo_results)} yayın\n",
        f"Demo sonuçlar bu e-postaya txt dosyası olarak eklenmiştir.\n",
    ]

    from trdizin.models import DizinOrder
    total_price = DizinOrder.calculate_price(job.total_results)

    lines.append(f"{'='*60}")
    lines.append(f"\n--- TÜM SONUÇLARI ALMAK İÇİN ---\n")
    lines.append(f"Toplam {job.total_results} yayın için tahmini ücret: {total_price} TL\n")
    lines.append(f"Fiyatlandırma:")
    lines.append(f"  * İlk 100 yayın    : 250 TL")
    lines.append(f"  * Sonraki her 100   : +100 TL")
    lines.append(f"")
    lines.append(f"Banka Bilgileri:")
    lines.append(f"  Hesap Sahibi : {BANK_INFO['hesap_sahibi']}")
    lines.append(f"  IBAN         : {BANK_INFO['iban']}")
    lines.append(f"  Açıklama     : TR Dizin - {user.username}")
    lines.append(f"")
    site_url = getattr(settings, 'SITE_URL', 'https://www.analizus.com')
    lines.append(f"Ödeme yaptıktan sonra siparişinizi oluşturun:")
    lines.append(f"  {site_url}/trdizin/siparis/{job.id}/")
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
            f"trdizin_demo_sonuclar.txt",
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
    """Onaylanan siparişin tüm sonuçlarını txt dosyası olarak gönder."""
    user = order.user
    job = order.search_job
    to_email = user.email

    if not to_email:
        return False

    query_summary = job.get_query_summary()
    subject = f"TR Dizin Yayın Arama Sonuçları - Sipariş #{str(order.id)[:8]}"

    results_to_send = job.all_results[:order.abstract_count]

    txt_content = _generate_results_txt(results_to_send, job, is_demo=False)

    # S3'e yükle
    s3_key = f"trdizin/orders/{order.id}.txt"
    s3_url = upload_to_s3(txt_content, s3_key)

    lines = [
        f"Merhaba {user.first_name or user.username},\n",
        f"Siparişiniz onaylanmış ve yayın sonuçlarınız hazırlanmıştır.\n",
        f"Sipariş No: #{str(order.id)[:8]}",
        f"Sorgu: {query_summary}",
        f"Toplam Sonuç: {job.total_results}",
        f"Gönderilen Yayın: {len(results_to_send)}",
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
            f"trdizin_{len(results_to_send)}_sonuc.txt",
            txt_content,
            'text/plain',
        )
        email.send()

        order.results_email_sent = True
        order.results_email_sent_at = timezone.now()
        order.status = 'completed'
        order.save(update_fields=['results_email_sent', 'results_email_sent_at', 'status'])

        logger.info(f"Sipariş sonuçları gönderildi: {to_email} ({len(results_to_send)} yayın)")
        return True
    except Exception as e:
        logger.error(f"Sipariş email gönderilemedi: {e}")
        return False


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
    """3 günden eski, sipariş oluşturulmamış demo/full dosyalarını S3'den siler."""
    from trdizin.models import DizinSearchJob

    cutoff = timezone.now() - timezone.timedelta(days=days)

    expired_jobs = DizinSearchJob.objects.filter(
        created_at__lt=cutoff,
        status='completed',
    ).exclude(
        orders__status__in=['pending_payment', 'payment_review', 'approved', 'processing', 'completed']
    )

    deleted_count = 0
    for job in expired_jobs:
        if job.demo_file_url:
            s3_key = f"trdizin/demo/{job.id}.txt"
            if delete_from_s3(s3_key):
                job.demo_file_url = ''
                deleted_count += 1

        if job.all_results_file_url:
            s3_key = f"trdizin/full/{job.id}.txt"
            if delete_from_s3(s3_key):
                job.all_results_file_url = ''
                deleted_count += 1

        if not job.demo_file_url and not job.all_results_file_url:
            job.save(update_fields=['demo_file_url', 'all_results_file_url'])
        elif not job.demo_file_url:
            job.save(update_fields=['demo_file_url'])
        elif not job.all_results_file_url:
            job.save(update_fields=['all_results_file_url'])

    logger.info(f"TR Dizin S3 temizlik: {deleted_count} dosya silindi ({expired_jobs.count()} expired job)")
    return deleted_count
