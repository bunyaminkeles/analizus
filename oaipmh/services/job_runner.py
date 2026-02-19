import logging
import threading
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMessage
from forum.s3_utils import upload_to_s3, delete_from_s3

logger = logging.getLogger(__name__)

IBAN_INFO = {
    'hesap_sahibi': 'Bünyamin Keleş',
    'iban': 'TR73 0003 2000 0000 0079 1034 65',
}


def _generate_results_txt(record_list, job, is_demo=True):
    lines = [
        "Üniversite Tez Arşivi Arama Sonuçları",
        "=" * 60,
        f"Arama Türü  : {job.get_search_type_display()}",
        f"Sorgu       : {job.get_query_summary()}",
        f"Toplam Sonuç: {job.total_results}",
        f"Bu dosya    : {len(record_list)} kayıt",
        "=" * 60 + "\n",
    ]
    for i, rec in enumerate(record_list, 1):
        lines.append(f"--- Kayıt #{i} ---")
        lines.append(f"Başlık      : {rec.get('title', '')}")
        lines.append(f"Yazarlar    : {rec.get('authors', '')}")
        lines.append(f"Yıl         : {rec.get('year', '')}")
        lines.append(f"Üniversite  : {rec.get('university', '')}")
        lines.append(f"Tür         : {rec.get('type', '')}")
        if rec.get('subject'):
            lines.append(f"Konu        : {rec['subject']}")
        if rec.get('abstract'):
            lines.append(f"Özet        : {rec['abstract']}")
        if rec.get('link'):
            lines.append(f"Link        : {rec['link']}")
        lines.append("")

    lines.append("=" * 60)
    lines.append(f"Toplam {job.total_results} kayıt bulundu.")
    if is_demo:
        lines.append("Daha fazla sonuç için e-postanızdaki adımları takip ediniz.")
    lines.append("\n---\nAnalizus - www.analizus.com")
    return "\n".join(lines)


def run_scraping_job(job_id):
    """Background thread'de OAI-PMH scraping job çalıştır."""
    def _run():
        from oaipmh.models import OAIPMHSearchJob, University
        from oaipmh.services.scraper import OAIPMHScraper

        try:
            job = OAIPMHSearchJob.objects.get(id=job_id)
            job.mark_running()

            scraper = OAIPMHScraper()

            if job.search_type == 'keyword':
                if job.university_ids:
                    universities = University.objects.filter(id__in=job.university_ids, is_active=True)
                else:
                    universities = University.objects.filter(is_active=True)
                total_count, demo_results, all_results = scraper.search_keyword(
                    universities=universities,
                    keyword=job.keyword,
                    abstract_query=job.abstract_query,
                    year_from=job.year_from,
                    year_to=job.year_to,
                    demo_limit=5,
                )
            else:  # browse
                total_count, demo_results, all_results = scraper.browse_university(
                    university=job.university,
                    demo_limit=5,
                )

            job.mark_completed(
                demo_results=demo_results,
                all_results=all_results,
                total_count=total_count,
            )

            # S3'e yükle
            try:
                demo_txt = _generate_results_txt(demo_results, job, is_demo=True)
                demo_url = upload_to_s3(demo_txt, f"oaipmh/demo/{job.id}.txt")

                all_txt = _generate_results_txt(all_results, job, is_demo=False)
                all_url = upload_to_s3(all_txt, f"oaipmh/full/{job.id}.txt")

                update_fields = []
                if demo_url:
                    job.demo_file_url = demo_url
                    update_fields.append('demo_file_url')
                if all_url:
                    job.all_results_file_url = all_url
                    update_fields.append('all_results_file_url')
                if update_fields:
                    job.save(update_fields=update_fields)
            except Exception as e:
                logger.error(f"OAI-PMH S3 yükleme hatası: {e}")

            logger.info(f"OAI-PMH job {job_id} tamamlandı: {total_count} sonuç")

        except Exception as e:
            logger.error(f"OAI-PMH job {job_id} başarısız: {e}")
            try:
                from oaipmh.models import OAIPMHSearchJob
                job = OAIPMHSearchJob.objects.get(id=job_id)
                job.mark_failed(str(e))
            except Exception:
                pass

    thread = threading.Thread(target=_run)
    thread.daemon = True
    thread.start()


def send_demo_email_async(job_id):
    """Background thread'de demo email gönder."""
    def _run():
        from oaipmh.models import OAIPMHSearchJob
        try:
            job = OAIPMHSearchJob.objects.get(id=job_id)
            send_demo_email(job)
        except OAIPMHSearchJob.DoesNotExist:
            logger.error(f"[oaipmh_email] Job bulunamadı: {job_id}")
        except Exception as e:
            logger.error(f"[oaipmh_email] Hata job {job_id}: {e}", exc_info=True)

    thread = threading.Thread(target=_run)
    thread.daemon = True
    thread.start()


def send_demo_email(job):
    """Demo sonuçlarını txt olarak kullanıcıya email ile gönder."""
    user = job.user
    to_email = user.email
    if not to_email:
        return False

    subject = f"Üniversite Tez Arşivi - Demo Sonuçlar: {job.get_query_summary()}"
    demo_txt = _generate_results_txt(job.demo_results, job, is_demo=True)

    from oaipmh.models import OAIPMHOrder
    total_price = OAIPMHOrder.calculate_price(job.total_results)
    site_url = getattr(settings, 'SITE_URL', 'https://www.analizus.com')

    body_lines = [
        f"Merhaba {user.first_name or user.username},\n",
        f"Üniversite Tez Arşivi aramasının sonuçları hazırlandı.\n",
        f"Sorgu       : {job.get_query_summary()}",
        f"Toplam Sonuç: {job.total_results}",
        f"Demo Sonuç  : {len(job.demo_results)} kayıt\n",
        f"Demo sonuçlar bu e-postaya txt dosyası olarak eklenmiştir.\n",
        "=" * 60,
        "\n--- TÜM SONUÇLARI ALMAK İÇİN ---\n",
        f"Toplam {job.total_results} kayıt için tahmini ücret: {total_price} TL\n",
        "Fiyatlandırma:",
        "  * İlk 100 kayıt    : 250 TL",
        "  * Sonraki her 100  : +100 TL",
        "",
        "Banka Bilgileri:",
        f"  Hesap Sahibi : {IBAN_INFO['hesap_sahibi']}",
        f"  IBAN         : {IBAN_INFO['iban']}",
        f"  Açıklama     : ÜniTez - {user.username}",
        "",
        "Ödeme yaptıktan sonra siparişinizi oluşturun:",
        f"  {site_url}/oaipmh/siparis/{job.id}/",
        "",
        "Siparişiniz onaylandıktan sonra sonuçlar 24 saat",
        "içinde bu e-posta adresine gönderilecektir.",
        f"\n---\nAnalizus - {site_url}",
    ]

    try:
        email = EmailMessage(
            subject=subject,
            body="\n".join(body_lines),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        email.attach(
            f"unitez_demo_{len(job.demo_results)}_sonuc.txt",
            demo_txt,
            'text/plain',
        )
        email.send()
        job.demo_email_sent = True
        job.save(update_fields=['demo_email_sent'])
        logger.info(f"OAI-PMH demo email gönderildi: {to_email}")
        return True
    except Exception as e:
        logger.error(f"OAI-PMH demo email gönderilemedi: {e}")
        return False


def send_order_results_email(order):
    """Onaylanan siparişin sonuçlarını email ile gönder."""
    user = order.user
    job = order.search_job
    to_email = user.email
    if not to_email:
        return False

    results_to_send = job.all_results[:order.abstract_count]
    txt_content = _generate_results_txt(results_to_send, job, is_demo=False)

    s3_key = f"oaipmh/orders/{order.id}.txt"
    s3_url = upload_to_s3(txt_content, s3_key)
    site_url = getattr(settings, 'SITE_URL', 'https://www.analizus.com')

    lines = [
        f"Merhaba {user.first_name or user.username},\n",
        f"Siparişiniz onaylandı ve tez sonuçlarınız hazırlandı.\n",
        f"Sipariş No  : #{str(order.id)[:8]}",
        f"Sorgu       : {job.get_query_summary()}",
        f"Toplam Sonuç: {job.total_results}",
        f"Gönderilen  : {order.abstract_count} kayıt",
        f"Ödenen Tutar: {order.total_price} TL\n",
    ]
    if s3_url:
        lines.append(f"Sonuçları aşağıdaki linkten indirebilirsiniz:")
        lines.append(f"  {s3_url}\n")
    lines.append("Sonuçlar ayrıca bu e-postaya txt dosyası olarak eklenmiştir.")
    lines.append(f"\n---\nAnalizus - {site_url}")

    try:
        email = EmailMessage(
            subject=f"Üniversite Tez Arşivi Sonuçları: {job.get_query_summary()}",
            body="\n".join(lines),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        email.attach(
            f"unitez_{len(results_to_send)}_sonuc.txt",
            txt_content,
            'text/plain',
        )
        email.send()

        order.results_email_sent = True
        order.results_email_sent_at = timezone.now()
        order.status = 'completed'
        order.save(update_fields=['results_email_sent', 'results_email_sent_at', 'status'])
        logger.info(f"OAI-PMH sipariş sonuçları gönderildi: {to_email}")
        return True
    except Exception as e:
        logger.error(f"OAI-PMH sipariş email gönderilemedi: {e}")
        return False


def cleanup_expired_oaipmh_s3_files(days=3):
    """3 günden eski oaipmh/ S3 dosyalarını siler."""
    import boto3
    from botocore.exceptions import ClientError
    deleted_count = 0
    cutoff = timezone.now() - timedelta(days=days)

    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        bucket = settings.AWS_STORAGE_BUCKET_NAME
        for prefix in ['oaipmh/demo/', 'oaipmh/full/', 'oaipmh/orders/']:
            paginator = s3.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
                for obj in page.get('Contents', []):
                    if obj['LastModified'] < cutoff:
                        s3.delete_object(Bucket=bucket, Key=obj['Key'])
                        deleted_count += 1
    except Exception as e:
        logger.error(f"S3 temizlik hatası (oaipmh): {e}")

    try:
        from oaipmh.models import OAIPMHSearchJob
        OAIPMHSearchJob.objects.filter(created_at__lt=cutoff).exclude(
            demo_file_url='', all_results_file_url=''
        ).update(demo_file_url='', all_results_file_url='')
    except Exception as e:
        logger.error(f"DB temizlik hatası (oaipmh): {e}")

    logger.info(f"S3 temizlik (oaipmh): {deleted_count} dosya silindi")
    return deleted_count
