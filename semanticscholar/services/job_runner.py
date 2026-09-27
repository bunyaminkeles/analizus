import logging
import threading
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.translation import gettext
from forum.i18n_utils import recipient_language
from django.db import close_old_connections
from semanticscholar.models import SemanticSearchJob
from forum.s3_utils import upload_to_s3

logger = logging.getLogger(__name__)


def _generate_results_txt(publication_list, job, is_demo=True):
    """Semantic Scholar yayın sonuçlarını TXT olarak üretir — metnin dili aktif dil (indirme isteği ya da
    arka planda işi başlatan kullanıcının dili). Etiket hizası çevrilen etiket uzunluğuna göre."""
    L = {
        'title': gettext('Başlık'), 'authors': gettext('Yazarlar'), 'journal': gettext('Dergi/Kaynak'),
        'year': gettext('Yıl'), 'doi': 'DOI', 'type': gettext('Tür'), 'cited': gettext('Atıf Sayısı'),
        'inst': gettext('Kurumlar'), 'fos': gettext('Araştırma Alanları'), 'oa': 'OA PDF', 'abstract': gettext('Özet'),
    }
    w = max(len(v) for v in L.values())
    row = lambda key, value: f"{L[key].ljust(w)} : {value}"
    lines = [
        gettext("Semantic Scholar Yayın Arama Sonuçları"),
        "=" * 60,
        gettext("Sorgu: {query}").format(query=job.get_query_summary()),
        gettext("Toplam Bulunan Sonuç: {total}").format(total=job.total_results),
        gettext("Bu dosyadaki sonuç: {count} yayın").format(count=len(publication_list)),
        "=" * 60 + "\n",
    ]

    for i, pub in enumerate(publication_list, 1):
        lines.append(gettext("--- Yayın #{n} ---").format(n=i))
        lines.append(row('title', pub.get('title', '')))
        lines.append(row('authors', pub.get('authors', '')))
        lines.append(row('journal', pub.get('journal', '')))
        lines.append(row('year', pub.get('year', '')))
        lines.append(row('doi', pub.get('doi', '')))
        lines.append(row('type', pub.get('type', '')))
        lines.append(row('cited', pub.get('cited_by_count', 0)))
        if pub.get('institutions'):
            lines.append(row('inst', pub.get('institutions', '')))
        if pub.get('fields_of_study'):
            fos = pub['fields_of_study']
            lines.append(row('fos', '; '.join(fos) if isinstance(fos, list) else fos))
        if pub.get('open_access_pdf'):
            lines.append(row('oa', pub.get('open_access_pdf', '')))
        if pub.get('abstract'):
            lines.append(row('abstract', pub.get('abstract', '')))
        lines.append("")

    lines.append("=" * 60)
    lines.append(gettext("Toplam {total} yayın bulundu.").format(total=job.total_results))
    if is_demo:
        lines.append(gettext("Daha fazla sonuç için e-postanızdaki adımları takip ediniz."))
    lines.append("\n---\nAnalizus - www.analizus.com")

    return "\n".join(lines)

def _execute_job(job_id):
    """Global kuyruk worker'ı tarafından çağrılır. Worker thread'i dili bilmez → iş, başlatan
    kullanıcının dil tercihiyle (Profile.preferred_language) çalışır: arka planda üretilen TXT
    dosyaları ve hata mesajları o dilde olur; sunucu yeniden başlasa da kaybolmaz."""
    from semanticscholar.models import SemanticSearchJob
    job = SemanticSearchJob.objects.select_related('user__profile').filter(id=job_id).first()
    with recipient_language(getattr(job, 'user', None)):
        _execute_job_body(job_id)


def _execute_job_body(job_id):
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

    site_url = getattr(settings, 'SITE_URL', 'https://www.analizus.com')

    # Alıcının kayıtlı dilinde (Profile.preferred_language)
    with recipient_language(user):
        subject = gettext("Semantic Scholar Arama Sonuçları: %(query)s") % {'query': job.get_query_summary()}
        body_lines = [
            gettext("Merhaba %(name)s,") % {'name': user.first_name or user.username} + "\n",
            gettext("Semantic Scholar arama sonuçlarınız hazırlanmıştır.") + "\n",
            gettext("Sorgu: %(query)s") % {'query': job.get_query_summary()},
            gettext("Toplam Sonuç: %(total)s") % {'total': job.total_results} + "\n",
        ]
        # TR: sipariş; EN/DE: proje talebi (openalex job_runner'daki ortak yardımcı)
        from openalex.services.job_runner import _full_results_lines
        body_lines.extend(_full_results_lines(site_url, f"{site_url}/semantic-scholar/siparis/{job.id}/"))
    body_lines.append(f"---\nAnalizus - {site_url}")

    try:
        email = EmailMessage(
            subject=subject,
            body="\n".join(body_lines),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
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

    # Alıcının kayıtlı dilinde (Profile.preferred_language)
    with recipient_language(user):
        subject = gettext("Semantic Scholar Arama Sonuçları: %(query)s") % {'query': job.get_query_summary()}
        lines = [
            gettext("Merhaba %(name)s,") % {'name': user.first_name or user.username} + "\n",
            gettext("Siparişiniz onaylanmış ve Semantic Scholar yayın sonuçlarınız hazırlanmıştır.") + "\n",
            gettext("Sipariş No: #%(order)s") % {'order': str(order.id)[:8]},
            gettext("Sorgu: %(query)s") % {'query': job.get_query_summary()},
            gettext("Toplam Sonuç: %(total)s") % {'total': job.total_results},
            gettext("Gönderilen Yayın Sayısı: %(count)s") % {'count': order.abstract_count},
            gettext("Ödenen Tutar: %(amount)s TL") % {'amount': order.total_price} + "\n",
        ]
        if job.all_results_file_url:
            lines.append(gettext("Sonuçlarınızı aşağıdaki linkten indirebilirsiniz:"))
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
