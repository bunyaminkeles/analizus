import logging
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMessage
from trdizin.models import DizinSearchJob
from yoktez.services.job_runner import delete_from_s3, upload_to_s3

logger = logging.getLogger(__name__)

def _generate_dizin_results_txt(publication_list, job, is_demo=True):
    """TR Dizin yayın sonuçlarını txt formatında oluşturur."""
    lines = [
        f"TR Dizin Yayın Arama Sonuçları",
        f"{'='*60}",
        f"Sorgu: {job.get_query_summary()}",
        f"Toplam Bulunan Sonuç: {job.total_results}",
        f"Bu dosyadaki sonuç: {len(publication_list)} yayın",
        f"{'='*60}\n",
    ]

    for i, pub in enumerate(publication_list, 1):
        lines.append(f"--- Yayın #{i} ---")
        lines.append(f"Başlık    : {pub.get('title', '')}")
        lines.append(f"Yazarlar  : {pub.get('authors', '')}")
        lines.append(f"Dergi     : {pub.get('journal', '')}")
        lines.append(f"Yıl       : {pub.get('year', '')}")
        lines.append(f"DOI       : {pub.get('doi', '')}")
        if pub.get('abstract'):
            lines.append(f"Özet      : {pub['abstract']}")
        lines.append("")

    lines.append(f"{'='*60}")
    lines.append(f"Toplam {job.total_results} yayın bulundu.")
    if is_demo:
        lines.append(f"Daha fazla sonuç için epostanızdaki adımları takip ediniz.")
    lines.append(f"\n---\nAnalizus - www.analizus.com")

    return "\n".join(lines)


def send_order_results_email(order):
    """Onaylanan siparişin tüm sonuçlarını txt dosyası olarak S3'e yükleyip kullanıcıya gönder."""
    user = order.user
    job = order.search_job
    to_email = user.email

    if not to_email:
        return False

    subject = f"TR Dizin Arama Sonuçları: {job.get_query_summary()}"

    # İstenen sayıda sonucu al
    results_to_send = job.all_results[:order.abstract_count]

    # Txt dosya oluştur
    txt_content = _generate_dizin_results_txt(results_to_send, job, is_demo=False)

    # S3'e yükle
    s3_key = f"trdizin/orders/{order.id}.txt"
    s3_url = upload_to_s3(txt_content, s3_key)

    lines = [
        f"Merhaba {user.first_name or user.username},\n",
        f"Siparişiniz onaylanmış ve TR Dizin yayın sonuçlarınız hazırlanmıştır.\n",
        f"Sipariş No: #{str(order.id)[:8]}",
        f"Sorgu: {job.get_query_summary()}",
        f"Toplam Sonuç: {job.total_results}",
        f"Gönderilen Yayın Sayısı: {order.abstract_count}",
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

        logger.info(f"TR Dizin sipariş sonuçları gönderildi: {to_email} ({order.abstract_count} yayın)")
        return True
    except Exception as e:
        logger.error(f"TR Dizin sipariş email gönderilemedi: {e}")
        return False


def cleanup_expired_trdizin_s3_files(days=3):
    """3 günden eski, sipariş oluşturulmamış demo/full dosyalarını S3'den siler.
    Cron job olarak günlük çalıştırılabilir."""

    cutoff = timezone.now() - timezone.timedelta(days=days)

    # 3 günden eski, sipariş verilmemiş aramalar
    expired_jobs = DizinSearchJob.objects.filter(
        created_at__lt=cutoff,
        status='completed',
    ).exclude(
        orders__status__in=['pending_payment', 'payment_review', 'approved', 'processing', 'completed']
    )

    deleted_count = 0
    for job in expired_jobs:
        # Demo dosyasını sil
        if job.demo_file_url:
            s3_key = f"trdizin/demo/{job.id}.txt"
            if delete_from_s3(s3_key):
                job.demo_file_url = ''
                deleted_count += 1

        # Tüm sonuçlar dosyasını sil
        if job.all_results_file_url:
            s3_key = f"trdizin/full/{job.id}.txt"
            if delete_from_s3(s3_key):
                job.all_results_file_url = ''
                deleted_count += 1

        # Save changes to the job if any files were deleted
        if deleted_count > 0:
            job.save()

    logger.info(f"TR Dizin S3 temizlik: {deleted_count} dosya silindi ({expired_jobs.count()} expired job)")
    return deleted_count
