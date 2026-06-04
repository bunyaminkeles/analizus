import logging
import threading
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMessage
from django.db import close_old_connections
from semanticscholar.models import SemanticSearchJob
from forum.s3_utils import upload_to_s3

logger = logging.getLogger(__name__)


def _generate_results_txt(publication_list, job, is_demo=True):
    lines = [
        "Semantic Scholar Yayın Arama Sonuçları",
        "=" * 60,
        f"Sorgu: {job.get_query_summary()}",
        f"Toplam Bulunan Sonuç: {job.total_results}",
        f"Bu dosyadaki sonuç: {len(publication_list)} yayın",
        "=" * 60 + "\n",
    ]

    for i, pub in enumerate(publication_list, 1):
        lines.append(f"--- Yayın #{i} ---")
        lines.append(f"Başlık       : {pub.get('title', '')}")
        lines.append(f"Yazarlar     : {pub.get('authors', '')}")
        lines.append(f"Dergi/Kaynak : {pub.get('journal', '')}")
        lines.append(f"Yıl          : {pub.get('year', '')}")
        lines.append(f"DOI          : {pub.get('doi', '')}")
        lines.append(f"Tür          : {pub.get('type', '')}")
        lines.append(f"Atıf Sayısı  : {pub.get('cited_by_count', 0)}")
        if pub.get('institutions'):
            lines.append(f"Kurumlar     : {pub.get('institutions', '')}")
        if pub.get('fields_of_study'):
            fos = pub['fields_of_study']
            lines.append(f"Araştırma Al.: {'; '.join(fos) if isinstance(fos, list) else fos}")
        if pub.get('open_access_pdf'):
            lines.append(f"OA PDF       : {pub.get('open_access_pdf', '')}")
        if pub.get('abstract'):
            lines.append(f"Özet         : {pub.get('abstract', '')}")
        lines.append("")

    lines.append("=" * 60)
    lines.append(f"Toplam {job.total_results} yayın bulundu.")
    if is_demo:
        lines.append("Daha fazla sonuç için e-postanızdaki adımları takip ediniz.")
    lines.append("\n---\nAnalizus - www.analizus.com")

    return "\n".join(lines)


def _execute_job(job_id):
    from semanticscholar.services.scraper import SemanticScholarScraper

    close_old_connections()
    try:
        job = SemanticSearchJob.objects.get(id=job_id)
        job.mark_running()

        scraper = SemanticScholarScraper()
        total_count, demo_results, all_results, api_query = scraper.search(
            query_parts=job.query_parts,
            demo_limit=5,
        )

        close_old_connections()
        job.mark_completed(
            demo_results=demo_results,
            all_results=all_results,
            total_count=total_count,
            api_query=api_query,
        )

        try:
            demo_txt = _generate_results_txt(demo_results, job, is_demo=True)
            demo_s3_url = upload_to_s3(demo_txt, f"semanticscholar/demo/{job.id}.txt")

            all_txt = _generate_results_txt(all_results, job, is_demo=False)
            all_s3_url = upload_to_s3(all_txt, f"semanticscholar/full/{job.id}.txt")

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
            logger.error(f"S2 S3 yükleme hatası: {e}")

        logger.info(f"S2 job {job_id} tamamlandı: {total_count} sonuç")

    except Exception as e:
        logger.error(f"S2 job {job_id} başarısız: {e}")
        try:
            close_old_connections()
            job = SemanticSearchJob.objects.get(id=job_id)
            job.mark_failed(str(e))
        except Exception:
            pass


def run_scraping_job(job_id):
    from analizdestek.job_queue import enqueue
    enqueue('semanticscholar', str(job_id))


def send_demo_email_async(job_id):
    def _run():
        try:
            job = SemanticSearchJob.objects.get(id=job_id)
            send_demo_email(job)
        except SemanticSearchJob.DoesNotExist:
            logger.error(f"[s2_email] Job bulunamadı: {job_id}")
        except Exception as e:
            logger.error(f"[s2_email] Hata {job_id}: {e}", exc_info=True)

    t = threading.Thread(target=_run, daemon=True)
    t.start()


def send_demo_email(job):
    user = job.user
    to_email = user.email
    if not to_email:
        return False

    subject = f"Semantic Scholar Arama Sonuçları: {job.get_query_summary()}"
    site_url = getattr(settings, 'SITE_URL', 'https://www.analizus.com')

    body_lines = [
        f"Merhaba {user.first_name or user.username},\n",
        "Semantic Scholar arama sonuçlarınız hazırlanmıştır.\n",
        f"Sorgu: {job.get_query_summary()}",
        f"Toplam Sonuç: {job.total_results}\n",
    ]

    if job.all_results_file_url:
        body_lines.append("Tüm sonuçlarınızı aşağıdaki linkten indirebilirsiniz (geçici link):")
        body_lines.append(f"  {job.all_results_file_url}\n")
    else:
        body_lines.append("Tüm sonuçlara erişmek için sipariş sayfasını ziyaret edebilirsiniz:")
        body_lines.append(f"  {site_url}/semantic-scholar/siparis/{job.id}/\n")

    body_lines.append(f"---\nAnalizus - {site_url}")

    try:
        email = EmailMessage(
            subject=subject,
            body="\n".join(body_lines),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        if not job.all_results_file_url:
            demo_txt = _generate_results_txt(job.demo_results, job, is_demo=True)
            email.attach(
                f"semantic_scholar_{len(job.demo_results)}_sonuc.txt",
                demo_txt,
                'text/plain',
            )
        email.send()
        job.demo_email_sent = True
        job.save(update_fields=['demo_email_sent'])
        logger.info(f"S2 demo email gönderildi: {to_email}")
        return True
    except Exception as e:
        logger.error(f"S2 demo email gönderilemedi: {e}")
        return False


def send_order_results_email(order):
    user = order.user
    job = order.search_job
    to_email = user.email
    if not to_email:
        return False

    subject = f"Semantic Scholar Arama Sonuçları: {job.get_query_summary()}"
    lines = [
        f"Merhaba {user.first_name or user.username},\n",
        "Siparişiniz onaylanmış ve Semantic Scholar yayın sonuçlarınız hazırlanmıştır.\n",
        f"Sipariş No: #{str(order.id)[:8]}",
        f"Sorgu: {job.get_query_summary()}",
        f"Toplam Sonuç: {job.total_results}",
        f"Gönderilen Yayın Sayısı: {order.abstract_count}",
        f"Ödenen Tutar: {order.total_price} TL\n",
    ]
    if job.all_results_file_url:
        lines.append("Sonuçlarınızı aşağıdaki linkten indirebilirsiniz:")
        lines.append(f"  {job.all_results_file_url}\n")
    lines.append("\n---\nAnalizus - www.analizus.com")

    try:
        email = EmailMessage(
            subject=subject,
            body="\n".join(lines),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        email.send()
        order.results_email_sent = True
        order.results_email_sent_at = timezone.now()
        order.status = 'completed'
        order.save(update_fields=['results_email_sent', 'results_email_sent_at', 'status'])
        logger.info(f"S2 sipariş sonuçları gönderildi: {to_email}")
        return True
    except Exception as e:
        logger.error(f"S2 sipariş email gönderilemedi: {e}")
        return False
