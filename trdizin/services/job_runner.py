import logging
import threading
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
        abstract = pub.get('abstract_tr') or pub.get('abstract_en') or ''
        if abstract:
            lines.append(f"Özet      : {abstract}")
        lines.append("")

    lines.append(f"{'='*60}")
    lines.append(f"Toplam {job.total_results} yayın bulundu.")
    if is_demo:
        lines.append(f"Daha fazla sonuç için epostanızdaki adımları takip ediniz.")
    lines.append(f"\n---\nAnalizus - www.analizus.com")

    return "\n".join(lines)


def run_scraping_job(job_id):
    """Background thread'de TR Dizin scraping job çalıştır."""

    def _run():
        from trdizin.models import DizinSearchJob
        from trdizin.services.scraper import TRDizinScraper

        try:
            job = DizinSearchJob.objects.get(id=job_id)
            job.mark_running()

            scraper = TRDizinScraper()
            total_count, demo_results, all_results, lucene_query = scraper.search(
                query_parts=job.query_parts,
                demo_limit=5,
            )

            job.mark_completed(
                demo_results=demo_results,
                all_results=all_results,
                total_count=total_count,
                lucene_query=lucene_query,
            )

            # Sonuçları txt olarak S3'e yükle
            try:
                # Demo sonuçları
                demo_txt = _generate_dizin_results_txt(demo_results, job, is_demo=True)
                demo_s3_key = f"trdizin/demo/{job.id}.txt"
                demo_s3_url = upload_to_s3(demo_txt, demo_s3_key)

                # TÜM sonuçları da S3'e yükle
                all_txt = _generate_dizin_results_txt(all_results, job, is_demo=False)
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
                logger.error(f"TR Dizin S3 yükleme hatası: {e}")

            logger.info(f"TR Dizin Scraping job {job_id} tamamlandı: {total_count} sonuç")

        except Exception as e:
            logger.error(f"TR Dizin Scraping job {job_id} başarısız: {e}")
            try:
                job = DizinSearchJob.objects.get(id=job_id)
                job.mark_failed(str(e))
            except Exception:
                pass

    thread = threading.Thread(target=_run)
    thread.daemon = True
    thread.start()


def send_demo_email_async(job_id):
    """Background thread'de demo email gönder."""
    def _run():
        from trdizin.models import DizinSearchJob
        logger.info(f"[trdizin_async_email] Starting background email task for job {job_id}")
        try:
            job = DizinSearchJob.objects.get(id=job_id)
            send_demo_email(job)
        except DizinSearchJob.DoesNotExist:
            logger.error(f"[trdizin_async_email] Job not found: {job_id}")
        except Exception as e:
            logger.error(f"[trdizin_async_email] Unhandled exception for job {job_id}: {e}", exc_info=True)

    thread = threading.Thread(target=_run)
    thread.daemon = True
    thread.start()
    logger.info(f"[trdizin_async_email] Email task for job {job_id} started in background.")


def send_demo_email(job):
    """Demo sonuçları txt dosyası olarak kullanıcının emailine gönder.
    Email body'de yayın bilgileri açık olarak yer almaz, txt ek olarak gönderilir."""
    user = job.user
    to_email = user.email

    if not to_email:
        logger.warning(f"Kullanıcının emaili yok: {user.username}")
        return False

    subject = f"TR Dizin Arama - Demo Sonuçlar: {job.get_query_summary()}"

    demo_txt = _generate_dizin_results_txt(job.demo_results, job, is_demo=True)

    body_lines = [
        f"Merhaba {user.first_name or user.username},\n",
        f"TR Dizin aracıyla yaptığınız arama sonuçları hazırlanmıştır.\n",
        f"Sorgu: {job.get_query_summary()}",
        f"Toplam Bulunan Sonuç: {job.total_results}",
        f"Demo Sonuç: {len(job.demo_results)} yayın\n",
        f"Demo sonuçlar bu e-postaya txt dosyası olarak eklenmiştir.\n",
    ]

    # Fiyat bilgisi
    from trdizin.models import DizinOrder
    total_price = DizinOrder.calculate_price(job.total_results)

    IBAN_INFO = {
        'hesap_sahibi': 'Bünyamin Keleş',
        'iban': 'TR73 0003 2000 0000 0079 1034 65',
    }

    body_lines.append(f"{'='*60}")
    body_lines.append(f"\n--- TÜM SONUÇLARI ALMAK İÇİN ---\n")
    body_lines.append(f"Toplam {job.total_results} yayın için tahmini ücret: {total_price} TL\n")
    body_lines.append(f"Fiyatlandırma:")
    body_lines.append(f"  * İlk 100 yayın    : 250 TL")
    body_lines.append(f"  * Sonraki her 100   : +100 TL")
    body_lines.append(f"")
    body_lines.append(f"Banka Bilgileri:")
    body_lines.append(f"  Hesap Sahibi : {IBAN_INFO['hesap_sahibi']}")
    body_lines.append(f"  IBAN         : {IBAN_INFO['iban']}")
    body_lines.append(f"  Açıklama     : TR Dizin - {user.username}")
    body_lines.append(f"")
    site_url = getattr(settings, 'SITE_URL', 'https://www.analizus.com')
    body_lines.append(f"Ödeme yaptıktan sonra siparişinizi oluşturun:")
    body_lines.append(f"  {site_url}/trdizin/siparis/{job.id}/")
    body_lines.append(f"")
    body_lines.append(f"Siparişiniz onaylandıktan sonra sonuçlar 24 saat")
    body_lines.append(f"içinde bu e-posta adresine gönderilecektir.")
    body_lines.append(f"\n---\nAnalizus - {site_url}")

    try:
        email = EmailMessage(
            subject=subject,
            body="\n".join(body_lines),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        email.attach(
            f"trdizin_demo_{len(job.demo_results)}_sonuc.txt",
            demo_txt,
            'text/plain',
        )
        email.send()

        job.demo_email_sent = True
        job.save(update_fields=['demo_email_sent'])

        logger.info(f"TR Dizin demo email gönderildi: {to_email}")
        return True
    except Exception as e:
        logger.error(f"TR Dizin demo email gönderilemedi: {e}")
        return False


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
        job_changed = False

        if job.demo_file_url:
            s3_key = f"trdizin/demo/{job.id}.txt"
            if delete_from_s3(s3_key):
                job.demo_file_url = ''
                job_changed = True
                deleted_count += 1

        if job.all_results_file_url:
            s3_key = f"trdizin/full/{job.id}.txt"
            if delete_from_s3(s3_key):
                job.all_results_file_url = ''
                job_changed = True
                deleted_count += 1

        if job_changed:
            job.save(update_fields=['demo_file_url', 'all_results_file_url'])

    logger.info(f"TR Dizin S3 temizlik: {deleted_count} dosya silindi ({expired_jobs.count()} expired job)")
    return deleted_count