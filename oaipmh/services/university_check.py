from django.db.models import F
from django.utils import timezone

from oaipmh.models import University
from oaipmh.services.scraper import OAIPMHScraper

# Canlı test için taranacak üst sınır — gerçek sonuç sayısını değil, endpoint'in
# çalışıp çalışmadığını öğrenmek yeterli, tüm arşivi çekmeye gerek yok.
TEST_MAX_RECORDS = 50


# last_result_count'ta "bağlantı/sunucu hatası" (connection refused, SSL, HTTP 5xx vb.)
# için kullanılan sentinel — gerçek "0 sonuç" (noRecordsMatch) ile karıştırılmasın.
CONNECTION_ERROR_SENTINEL = -1


def check_universities(limit=None):
    """
    Aktif University kayıtları için OAI-PMH endpoint'ine canlı test yapar
    (browse_university ile gerçek tarama); 0 sonuç dönenleri VEYA bağlantı/sunucu
    hatası alanları flagged_for_review=True yapar (last_result_count ile ayırt
    edilir: -1 = bağlantı hatası, 0 = gerçekten boş). Otomatik silme/deaktive
    etme YOK — kapatma kararını admin panelden insan verir.

    En eski test edilen (hiç test edilmemiş dahil) üniversiteler önce gelir —
    `limit` verildiğinde (ör. cron'un her çalıştırmasında) zamanla tüm listeyi
    round-robin tarar. Yeni işaretlenen (önceden flagged olmayan) üniversiteler
    varsa admin'e e-posta bildirimi gönderilir.
    """
    queryset = University.objects.filter(is_active=True).order_by(
        F('last_checked_at').asc(nulls_first=True)
    )
    if limit:
        queryset = queryset[:limit]

    scraper = OAIPMHScraper()
    results = []
    newly_flagged_empty = []
    newly_flagged_error = []

    for uni in queryset:
        try:
            total, _, _ = scraper.browse_university(uni, demo_limit=1, max_records=TEST_MAX_RECORDS)
        except Exception as e:
            was_flagged = uni.flagged_for_review
            uni.last_checked_at = timezone.now()
            uni.last_result_count = CONNECTION_ERROR_SENTINEL
            uni.flagged_for_review = True
            uni.save(update_fields=['last_checked_at', 'last_result_count', 'flagged_for_review'])

            if not was_flagged:
                newly_flagged_error.append(uni)

            results.append({
                'name': uni.name,
                'error': str(e),
                'flagged': True,
                'cleared': False,
            })
            continue

        was_flagged = uni.flagged_for_review
        uni.last_checked_at = timezone.now()
        uni.last_result_count = total
        uni.flagged_for_review = (total == 0)
        uni.save(update_fields=['last_checked_at', 'last_result_count', 'flagged_for_review'])

        if uni.flagged_for_review and not was_flagged:
            newly_flagged_empty.append(uni)

        results.append({
            'name': uni.name,
            'result_count': total,
            'flagged': uni.flagged_for_review,
            'cleared': was_flagged and total > 0,
        })

    if newly_flagged_empty or newly_flagged_error:
        from forum.email_utils import notify_admin_oaipmh_flagged_universities
        notify_admin_oaipmh_flagged_universities(newly_flagged_empty, newly_flagged_error)

    return results
