import logging
import threading
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.translation import gettext
from forum.i18n_utils import recipient_language
from django.db import close_old_connections
from pubmed.models import PubMedSearchJob
from forum.s3_utils import upload_to_s3

logger = logging.getLogger(__name__)


def _generate_pubmed_results_txt(publication_list, job):
    """PubMed yayın sonuçlarını TXT olarak üretir — aktif dilde. Etiket hizası çevrilen etiket uzunluğuna göre."""
    L = {
        'title': gettext('Başlık'), 'authors': gettext('Yazarlar'), 'journal': gettext('Dergi/Kaynak'),
        'year': gettext('Yıl'), 'doi': 'DOI', 'pmid': 'PMID', 'type': gettext('Tür'),
        'inst': gettext('Kurumlar'), 'keywords': gettext('Anahtar Kelimeler'), 'mesh': gettext('MeSH Terimleri'),
        'abstract': gettext('Özet'),
    }
    w = max(len(v) for v in L.values())
    row = lambda key, value: f"{L[key].ljust(w)} : {value}"
    lines = [
        gettext("PubMed Yayın Arama Sonuçları"),
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
        lines.append(row('pmid', pub.get('pmid', '')))
        lines.append(row('type', pub.get('type', '')))
        lines.append(row('inst', pub.get('institutions', '')))
        if pub.get('keywords'):
            lines.append(row('keywords', ', '.join(pub['keywords'][:10])))
        if pub.get('mesh_terms'):
            lines.append(row('mesh', ', '.join(pub['mesh_terms'][:10])))
        if pub.get('abstract'):
            lines.append(row('abstract', pub['abstract']))
        lines.append("")

    lines.append("=" * 60)
    lines.append(gettext("Toplam {total} yayın bulundu.").format(total=job.total_results))
    lines.append("\n---\nAnalizus - www.analizus.com")
    return "\n".join(lines)


def _execute_job(job_id):
    """Global kuyruk worker'ı tarafından çağrılır. Worker thread'i dili bilmez → iş, başlatan
    kullanıcının dil tercihiyle (Profile.preferred_language) çalışır."""
    job = PubMedSearchJob.objects.select_related('user__profile').filter(id=job_id).first()
    with recipient_language(getattr(job, 'user', None)):
        _execute_job_body(job_id)


def _execute_job_body(job_id):
    """Senkron: yalnız ilk sayfa (esearch + 1 efetch) → demo TXT → S3."""
    from pubmed.services.scraper import PubMedScraper, MAX_PER_PAGE

    close_old_connections()
    try:
        job = PubMedSearchJob.objects.get(id=job_id)
        job.mark_running()

        total_count, demo_results, all_results, api_query = PubMedScraper().search(
            query_parts=job.query_parts,
            demo_limit=5,
            max_results=MAX_PER_PAGE,
        )

        close_old_connections()
        job.mark_completed(
            demo_results=demo_results,
            all_results=all_results,
            total_count=total_count,
            api_query=api_query,
        )

        try:
            demo_txt = _generate_pubmed_results_txt(demo_results, job)
            demo_s3_url = upload_to_s3(demo_txt, f"pubmed/demo/{job.id}.txt")
            if demo_s3_url:
                job.demo_file_url = demo_s3_url
                job.save(update_fields=['demo_file_url'])
        except Exception as e:
            logger.error(f"PubMed S3 yükleme hatası: {e}")

        logger.info(f"PubMed job {job_id} tamamlandı: {total_count} sonuç")

    except Exception as e:
        # Ham hata (URL, HTTP kodu) kullanıcıya gösterilmez — ayrıntı logda
        logger.error(f"PubMed job {job_id} başarısız: {e}", exc_info=True)
        try:
            close_old_connections()
            job = PubMedSearchJob.objects.get(id=job_id)
            job.mark_failed(gettext('Bir hata oluştu, lütfen tekrar deneyin.'))
        except Exception:
            pass


def run_scraping_job(job_id):
    from analizdestek.job_queue import enqueue
    enqueue('pubmed', str(job_id))


def ensure_full_results(job, limit=None):
    """Arama yalnız ilk sayfayı saklar; bibliometri öncesi eksik kısmı PubMed'den çeker.
    Hedef = min(toplam sonuç, limit, admin ayarı scrap_max_records, 10.000). Veri zaten yeterliyse
    istek atılmaz. Sayfalama hatasında kısmi veri kaydedilir; ilk istekte hata olursa istisna yükselir.
    Returns: hedefe ulaşıldı mı (bool)."""
    from forum.models import SiteSettings
    from pubmed.services.scraper import PubMedScraper, EUTILS_MAX_RETRIEVABLE

    max_records = SiteSettings.load().scrap_max_records or 5000
    target = min(job.total_results, limit or max_records, max_records, EUTILS_MAX_RETRIEVABLE)
    if len(job.all_results or []) >= target:
        return True

    _total, _demo, results, _q = PubMedScraper().search(
        query_parts=job.query_parts, demo_limit=0, max_results=target,
    )
    close_old_connections()
    if len(results) > len(job.all_results or []):
        job.all_results = results
        job.save(update_fields=['all_results'])
    logger.info(f"PubMed tam veri: job {job.id} — {len(job.all_results)}/{target} kayıt")
    return len(job.all_results) >= target


def send_demo_email_async(job_id):
    """Background thread'de demo email gönder."""
    def _run():
        try:
            job = PubMedSearchJob.objects.select_related('user__profile').get(id=job_id)
            send_demo_email(job)
        except PubMedSearchJob.DoesNotExist:
            logger.error(f"[pubmed_async_email] Job not found: {job_id}")
        except Exception as e:
            logger.error(f"[pubmed_async_email] Unhandled exception for job {job_id}: {e}", exc_info=True)

    thread = threading.Thread(target=_run)
    thread.daemon = True
    thread.start()


def send_demo_email(job):
    """Demo arama sonuçlarını (5 kayıt ek dosya) gönder. PubMed'de sipariş yok (kullanıcı kararı
    29 Eylül 2026) → tüm dillerde tam veri için proje talebi."""
    from django.urls import reverse
    user = job.user
    to_email = user.email
    if not to_email:
        logger.warning(f"Kullanıcının emaili yok: {user.username}")
        return False

    site_url = getattr(settings, 'SITE_URL', 'https://www.analizus.com')

    with recipient_language(user):
        subject = gettext("PubMed Arama Sonuçları: %(query)s") % {'query': job.get_query_summary()}
        body_lines = [
            gettext("Merhaba %(name)s,") % {'name': user.first_name or user.username} + "\n",
            gettext("PubMed arama sonuçlarınız hazırlanmıştır.") + "\n",
            gettext("Sorgu: %(query)s") % {'query': job.get_query_summary()},
            gettext("Toplam Sonuç: %(total)s") % {'total': job.total_results} + "\n",
            gettext("Tam veri seti için proje talebi bırakın, ücretsiz değerlendirelim:"),
            f"  {site_url}{reverse('proje_talebi')}?source=tool\n",
            f"---\nAnalizus - {site_url}",
        ]
        demo_txt = _generate_pubmed_results_txt(job.demo_results, job)

    try:
        email = EmailMessage(
            subject=subject,
            body="\n".join(body_lines),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        email.attach(f"pubmed_{len(job.demo_results)}_sonuc.txt", demo_txt, 'text/plain')
        email.send()

        job.demo_email_sent = True
        job.save(update_fields=['demo_email_sent'])
        logger.info(f"PubMed email gönderildi: {to_email}")
        return True
    except Exception as e:
        logger.error(f"PubMed email gönderilemedi: {e}")
        return False


def cleanup_expired_pubmed_s3_files(days=7):
    """7 günden eski pubmed/ altındaki dosyaları S3'den siler (cron bağlantısı Faz 2: forum/api_views)."""
    import boto3
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
        paginator = s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket, Prefix='pubmed/'):
            for obj in page.get('Contents', []):
                if obj['LastModified'] < cutoff:
                    s3.delete_object(Bucket=bucket, Key=obj['Key'])
                    deleted_count += 1
    except Exception as e:
        logger.error(f"S3 temizlik hatası (pubmed): {e}")

    try:
        PubMedSearchJob.objects.filter(created_at__lt=cutoff).exclude(demo_file_url='').update(demo_file_url='')
    except Exception as e:
        logger.error(f"DB temizlik hatası (pubmed): {e}")

    logger.info(f"S3 temizlik (pubmed): {deleted_count} dosya silindi")
    return deleted_count
