import logging
import threading
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.translation import gettext
from forum.i18n_utils import recipient_language
from django.db import close_old_connections
from openalex.models import AlexSearchJob
from forum.s3_utils import delete_from_s3, upload_to_s3

logger = logging.getLogger(__name__)


def _generate_alex_results_txt(publication_list, job, is_demo=True):
    """OpenAlex yayın sonuçlarını TXT olarak üretir — metnin dili aktif dil (indirme isteği ya da
    arka planda işi başlatan kullanıcının dili). Etiket hizası çevrilen etiket uzunluğuna göre."""
    L = {
        'title': gettext('Başlık'), 'authors': gettext('Yazarlar'), 'journal': gettext('Dergi/Kaynak'),
        'year': gettext('Yıl'), 'doi': 'DOI', 'type': gettext('Tür'), 'cited': gettext('Atıf Sayısı'),
        'inst': gettext('Kurumlar'), 'keywords': gettext('Anahtar Kelimeler'), 'abstract': gettext('Özet'),
    }
    w = max(len(v) for v in L.values())
    row = lambda key, value: f"{L[key].ljust(w)} : {value}"
    lines = [
        gettext("OpenAlex Yayın Arama Sonuçları"),
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
        lines.append(row('inst', pub.get('institutions', '')))
        if pub.get('keywords'):
            lines.append(row('keywords', ', '.join(pub['keywords'][:10])))
        abstract = pub.get('abstract', '')
        if abstract:
            lines.append(row('abstract', abstract))
        lines.append("")

    lines.append("=" * 60)
    lines.append(gettext("Toplam {total} yayın bulundu.").format(total=job.total_results))
    if is_demo:
        lines.append(gettext("Daha fazla sonuç için e-postanızdaki adımları takip ediniz."))
    lines.append("\n---\nAnalizus - www.analizus.com")

    return "\n".join(lines)

def _full_results_lines(site_url, order_url):
    """Demo e-postasında "tüm sonuçlar" satırları — aktif dil (recipient_language) içinde çağrılır.
    TR: sipariş sayfası (Türk IBAN / TL havale). EN/DE: sipariş yok → proje talebi (kullanıcı
    kararı 27 Eylül 2026)."""
    from django.urls import reverse
    from django.utils.translation import get_language
    if (get_language() or 'tr')[:2] == 'tr':
        return [gettext("Tüm sonuçlara erişmek için sipariş sayfasını ziyaret edebilirsiniz:"), f"  {order_url}\n"]
    return [gettext("Tam veri seti için proje talebi bırakın, ücretsiz değerlendirelim:"),
            f"  {site_url}{reverse('proje_talebi')}?source=tool\n"]


def _execute_job(job_id):
    """Global kuyruk worker'ı tarafından çağrılır. Worker thread'i dili bilmez → iş, başlatan
    kullanıcının dil tercihiyle (Profile.preferred_language) çalışır: arka planda üretilen TXT
    dosyaları ve hata mesajları o dilde olur; sunucu yeniden başlasa da kaybolmaz."""
    from openalex.models import AlexSearchJob
    job = AlexSearchJob.objects.select_related('user__profile').filter(id=job_id).first()
    with recipient_language(getattr(job, 'user', None)):
        _execute_job_body(job_id)


def _execute_job_body(job_id):
    """Global kuyruk worker'ı tarafından çağrılır — senkron çalışır."""
    from openalex.models import AlexSearchJob
    from openalex.services.scraper import OpenAlexScraper

    close_old_connections()
    try:
        job = AlexSearchJob.objects.get(id=job_id)
        job.mark_running()

        # Yalnız ilk sayfa (1 istek) — tam veri bibliometri/sipariş istenince ensure_full_results ile
        # çekilir (OpenAlex günlük bütçesi; kullanıcı kararı 28 Eylül 2026)
        from openalex.services.scraper import MAX_PER_PAGE
        scraper = OpenAlexScraper()
        total_count, demo_results, all_results, api_query = scraper.search(
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
            demo_txt = _generate_alex_results_txt(demo_results, job, is_demo=True)
            demo_s3_url = upload_to_s3(demo_txt, f"openalex/demo/{job.id}.txt")
            if demo_s3_url:
                job.demo_file_url = demo_s3_url
                job.save(update_fields=['demo_file_url'])
        except Exception as e:
            logger.error(f"OpenAlex S3 yükleme hatası: {e}")

        logger.info(f"OpenAlex Scraping job {job_id} tamamlandı: {total_count} sonuç")

    except Exception as e:
        logger.error(f"OpenAlex Scraping job {job_id} başarısız: {e}")
        try:
            close_old_connections()
            job = AlexSearchJob.objects.get(id=job_id)
            job.mark_failed(str(e))
        except Exception:
            pass


def run_scraping_job(job_id):
    from analizdestek.job_queue import enqueue
    enqueue('openalex', str(job_id))


def ensure_full_results(job, limit=None):
    """Arama yalnız ilk sayfayı saklar; bibliometri/sipariş öncesi eksik kısmı OpenAlex'ten çeker.
    Hedef = min(toplam sonuç, limit, admin ayarı scrap_max_records). Veri zaten yeterliyse istek
    atılmaz. Sayfalama hatasında kısmi veri kaydedilir (sonraki çağrı yeniden dener); ilk istekte
    hata olursa istisna yükselir. Returns: hedefe ulaşıldı mı (bool)."""
    from forum.models import SiteSettings
    from openalex.services.scraper import OpenAlexScraper

    max_records = SiteSettings.load().scrap_max_records or 5000
    target = min(job.total_results, limit or max_records, max_records)
    if len(job.all_results or []) >= target:
        return True

    _total, _demo, results, _q = OpenAlexScraper().search(
        query_parts=job.query_parts, demo_limit=0, max_results=target,
    )
    close_old_connections()
    if len(results) > len(job.all_results or []):
        job.all_results = results
        job.save(update_fields=['all_results'])
    logger.info(f"OpenAlex tam veri: job {job.id} — {len(job.all_results)}/{target} kayıt")
    return len(job.all_results) >= target


def run_order_job(order_id):
    """Admin onayından sonra sipariş verisini arka planda hazırlat (tam veri çekimi ~30–60 sn)."""
    from analizdestek.job_queue import enqueue
    enqueue('openalex_order', str(order_id))


def _execute_order(order_id):
    """Onaylı sipariş: ödenen yayın sayısı (abstract_count) kadar veri çek → TXT → S3 → e-posta.
    Veri eksik kalırsa e-posta gönderilmez; sipariş 'approved'a döner ve hata admin notuna yazılır
    (admin aksiyonu tekrar çalıştırılabilir)."""
    from openalex.models import AlexOrder
    close_old_connections()
    order = AlexOrder.objects.select_related('user__profile', 'search_job').filter(id=order_id).first()
    if not order or order.status != 'processing':
        return
    job = order.search_job
    try:
        ensure_full_results(job, limit=order.abstract_count)
        records = (job.all_results or [])[:order.abstract_count]
        if len(records) < order.abstract_count:
            raise RuntimeError(f"Veri eksik: {len(records)}/{order.abstract_count} kayıt alınabildi")
        with recipient_language(order.user):
            txt = _generate_alex_results_txt(records, job, is_demo=False)
        download_url = upload_to_s3(txt, f"openalex/orders/{order.id}.txt")
        if not download_url:
            raise RuntimeError("S3 yüklemesi başarısız")
        if not send_order_results_email(order, download_url):
            raise RuntimeError("E-posta gönderilemedi")
    except Exception as e:
        logger.error(f"OpenAlex sipariş {order_id} hazırlanamadı: {e}", exc_info=True)
        close_old_connections()
        order.status = 'approved'
        order.admin_note = (order.admin_note + "\n" if order.admin_note else "") + \
            f"[{timezone.now():%d.%m.%Y %H:%M}] Otomatik gönderim başarısız: {e}"
        order.save(update_fields=['status', 'admin_note'])


def send_demo_email_async(job_id):
    """Background thread'de demo email gönder."""
    def _run():
        from openalex.models import AlexSearchJob
        logger.info(f"[openalex_async_email] Starting background email task for job {job_id}")
        try:
            job = AlexSearchJob.objects.get(id=job_id)
            send_demo_email(job)
        except AlexSearchJob.DoesNotExist:
            logger.error(f"[openalex_async_email] Job not found: {job_id}")
        except Exception as e:
            logger.error(f"[openalex_async_email] Unhandled exception for job {job_id}: {e}", exc_info=True)

    thread = threading.Thread(target=_run)
    thread.daemon = True
    thread.start()
    logger.info(f"[openalex_async_email] Email task for job {job_id} started in background.")


def send_demo_email(job):
    """Demo arama sonuçlarını (5 kayıt ek dosya + sipariş linki) kullanıcıya gönder."""
    user = job.user
    to_email = user.email

    if not to_email:
        logger.warning(f"Kullanıcının emaili yok: {user.username}")
        return False

    site_url = getattr(settings, 'SITE_URL', 'https://www.analizus.com')

    # Alıcının kayıtlı dilinde (Profile.preferred_language)
    with recipient_language(user):
        subject = gettext("OpenAlex Arama Sonuçları: %(query)s") % {'query': job.get_query_summary()}
        body_lines = [
            gettext("Merhaba %(name)s,") % {'name': user.first_name or user.username} + "\n",
            gettext("OpenAlex arama sonuçlarınız hazırlanmıştır.") + "\n",
            gettext("Sorgu: %(query)s") % {'query': job.get_query_summary()},
            gettext("Toplam Sonuç: %(total)s") % {'total': job.total_results} + "\n",
            *_full_results_lines(site_url, f"{site_url}/openalex/siparis/{job.id}/"),
            f"---\nAnalizus - {site_url}",
        ]

    try:
        email = EmailMessage(
            subject=subject,
            body="\n".join(body_lines),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        demo_txt = _generate_alex_results_txt(job.demo_results, job, is_demo=True)
        email.attach(
            f"openalex_{len(job.demo_results)}_sonuc.txt",
            demo_txt,
            'text/plain',
        )
        email.send()

        job.demo_email_sent = True
        job.save(update_fields=['demo_email_sent'])

        logger.info(f"OpenAlex email gönderildi: {to_email}")
        return True
    except Exception as e:
        logger.error(f"OpenAlex email gönderilemedi: {e}")
        return False


def send_order_results_email(order, download_url):
    """Onaylanan siparişin sonuçlarını (sipariş TXT'si, S3 linki) kullanıcıya gönder."""
    user = order.user
    job = order.search_job
    to_email = user.email

    if not to_email:
        return False

    # Alıcının kayıtlı dilinde (Profile.preferred_language)
    with recipient_language(user):
        subject = gettext("OpenAlex Arama Sonuçları: %(query)s") % {'query': job.get_query_summary()}
        lines = [
            gettext("Merhaba %(name)s,") % {'name': user.first_name or user.username} + "\n",
            gettext("Siparişiniz onaylanmış ve OpenAlex yayın sonuçlarınız hazırlanmıştır.") + "\n",
            gettext("Sipariş No: #%(order)s") % {'order': str(order.id)[:8]},
            gettext("Sorgu: %(query)s") % {'query': job.get_query_summary()},
            gettext("Toplam Sonuç: %(total)s") % {'total': job.total_results},
            gettext("Gönderilen Yayın Sayısı: %(count)s") % {'count': order.abstract_count},
            gettext("Ödenen Tutar: %(amount)s TL") % {'amount': order.total_price} + "\n",
        ]

        if download_url:
            lines.append(gettext("Sonuçlarınızı aşağıdaki linkten indirebilirsiniz:"))
            lines.append(f"  {download_url}\n")

    lines.append(f"\n---\nAnalizus - www.analizus.com")

    body = "\n".join(lines)

    try:
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        email.send()

        order.results_email_sent = True
        order.results_email_sent_at = timezone.now()
        order.status = 'completed'
        order.save(update_fields=['results_email_sent', 'results_email_sent_at', 'status'])

        logger.info(f"OpenAlex sipariş sonuçları gönderildi: {to_email} ({order.abstract_count} yayın)")
        return True
    except Exception as e:
        logger.error(f"OpenAlex sipariş email gönderilemedi: {e}")
        return False


def cleanup_expired_openalex_s3_files(days=7):
    """7 günden eski openalex/ altındaki tüm dosyaları S3'den siler."""
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

        for prefix in ['openalex/demo/', 'openalex/full/', 'openalex/orders/']:
            paginator = s3.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
                for obj in page.get('Contents', []):
                    last_modified = obj['LastModified']
                    if last_modified < cutoff:
                        s3.delete_object(Bucket=bucket, Key=obj['Key'])
                        logger.info(f"S3 temizlik: silindi {obj['Key']}")
                        deleted_count += 1
    except Exception as e:
        logger.error(f"S3 temizlik hatası (openalex): {e}")

    # DB'deki URL referanslarını da temizle
    try:
        AlexSearchJob.objects.filter(
            created_at__lt=cutoff,
        ).exclude(
            demo_file_url='', all_results_file_url=''
        ).update(demo_file_url='', all_results_file_url='')
    except Exception as e:
        logger.error(f"DB temizlik hatası (openalex): {e}")

    logger.info(f"S3 temizlik (openalex): {deleted_count} dosya silindi")
    return deleted_count
