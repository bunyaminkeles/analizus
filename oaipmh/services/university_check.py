from django.db.models import F
from django.utils import timezone

from oaipmh.models import University
from oaipmh.services.scraper import OAIPMHScraper

# Canlı test için taranacak üst sınır — gerçek sonuç sayısını değil, endpoint'in
# çalışıp çalışmadığını öğrenmek yeterli, tüm arşivi çekmeye gerek yok.
TEST_MAX_RECORDS = 50


def check_universities(limit=None):
    """
    Aktif University kayıtları için OAI-PMH endpoint'ine canlı test yapar
    (browse_university ile gerçek tarama); 0 sonuç dönenleri
    flagged_for_review=True yapar. Otomatik silme/deaktive etme YOK —
    kapatma kararını admin panelden insan verir.

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
    newly_flagged = []

    for uni in queryset:
        try:
            total, _, _ = scraper.browse_university(uni, demo_limit=1, max_records=TEST_MAX_RECORDS)
        except Exception as e:
            results.append({'name': uni.name, 'error': str(e)})
            continue

        was_flagged = uni.flagged_for_review
        uni.last_checked_at = timezone.now()
        uni.last_result_count = total
        uni.flagged_for_review = (total == 0)
        uni.save(update_fields=['last_checked_at', 'last_result_count', 'flagged_for_review'])

        if uni.flagged_for_review and not was_flagged:
            newly_flagged.append(uni)

        results.append({
            'name': uni.name,
            'result_count': total,
            'flagged': uni.flagged_for_review,
            'cleared': was_flagged and total > 0,
        })

    if newly_flagged:
        from forum.email_utils import notify_admin_oaipmh_flagged_universities
        notify_admin_oaipmh_flagged_universities(newly_flagged)

    return results
