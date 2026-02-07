import json
import threading
import logging
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


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


def send_demo_email(job):
    """Demo sonuçları (3 tez) kullanıcının kayıtlı emailine gönder."""
    user = job.user
    to_email = user.email

    if not to_email:
        logger.warning(f"Kullanıcının emaili yok: {user.username}")
        return

    subject = f"YÖK Tez Arama - Demo Sonuçlar: {job.konu}"

    lines = [
        f"Merhaba {user.first_name or user.username},\n",
        f"YÖK Tez Tarama aracıyla yaptığınız arama sonuçları aşağıdadır.\n",
        f"Bilim Alanı: {job.konu}",
        f"Anahtar Kelimeler: {', '.join(job.keywords)}",
        f"Toplam Bulunan Sonuç: {job.total_results}",
        f"Gönderilen (Demo): {len(job.demo_results)} tez\n",
        f"{'='*60}\n",
    ]

    for i, tez in enumerate(job.demo_results, 1):
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
    lines.append(f"\nToplam {job.total_results} tez bulundu.")
    lines.append(f"\n--- TÜM SONUÇLARI ALMAK İÇİN ---")
    lines.append(f"")
    lines.append(f"Fiyatlandırma:")
    lines.append(f"  * İlk 100 abstract  : 250 TL")
    lines.append(f"  * Sonraki her 100   : +100 TL")
    lines.append(f"")
    lines.append(f"Banka Bilgileri:")
    lines.append(f"  Banka : Ziraat Bankası")
    lines.append(f"  IBAN  : TR00 0000 0000 0000 0000 0000 00")
    lines.append(f"  Ad    : Analizus")
    lines.append(f"  Açıklama: YÖK Tez - {user.username}")
    lines.append(f"")
    lines.append(f"Ödeme yaptıktan sonra siparişinizi oluşturun:")
    lines.append(f"  https://www.analizus.com/yoktez/siparis/{job.id}/")
    lines.append(f"")
    lines.append(f"Siparişiniz onaylandıktan sonra sonuçlar 24 saat")
    lines.append(f"içinde bu e-posta adresine gönderilecektir.")
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

        job.demo_email_sent = True
        job.save(update_fields=['demo_email_sent'])
        logger.info(f"Demo email gönderildi: {to_email}")
    except Exception as e:
        logger.error(f"Demo email gönderilemedi: {e}")


def send_order_results_email(order):
    """Onaylanan siparişin tüm sonuçlarını kullanıcıya gönder."""
    user = order.user
    job = order.search_job
    to_email = user.email

    if not to_email:
        return False

    subject = f"YÖK Tez Arama Sonuçları: {job.konu} - {', '.join(job.keywords)}"

    lines = [
        f"Merhaba {user.first_name or user.username},\n",
        f"Siparişiniz onaylanmış ve tez sonuçlarınız hazırlanmıştır.\n",
        f"Sipariş No: #{str(order.id)[:8]}",
        f"Bilim Alanı: {job.konu}",
        f"Anahtar Kelimeler: {', '.join(job.keywords)}",
        f"Toplam Sonuç: {job.total_results}",
        f"Gönderilen Abstract: {order.abstract_count}",
        f"Ödenen Tutar: {order.total_price} TL\n",
        f"Sonuçlar bu e-postaya JSON dosyası olarak eklenmiştir.",
        f"\n---\nAnalizus - www.analizus.com",
    ]

    body = "\n".join(lines)
    results_to_send = job.all_results[:order.abstract_count]
    json_data = json.dumps(results_to_send, ensure_ascii=False, indent=2)

    try:
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        email.attach(
            f"yoktez_{job.konu}_{len(results_to_send)}_sonuc.json",
            json_data,
            'application/json',
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

    cutoff = timezone.now() - timezone.timedelta(hours=24)
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
