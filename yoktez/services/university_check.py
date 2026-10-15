from django.db.models import F
from django.utils import timezone

from yoktez.models import YokTezUniversite
from yoktez.services.scraper import search

TEST_KEYWORD = 'eğitim'


def check_universities(limit=None):
    """
    Aktif YokTezUniversite kayıtları için YÖK Tez'e canlı test araması yapar;
    0 sonuç dönenleri flagged_for_review=True yapar. Otomatik silme/deaktive
    etme YOK — kapatma kararını admin panelden insan verir.

    En eski test edilen (hiç test edilmemiş dahil) üniversiteler önce gelir —
    `limit` verildiğinde (ör. cron'un her çalıştırmasında) zamanla tüm listeyi
    round-robin tarar, tek seferde hepsini test etmeye çalışıp zaman aşımına
    takılmaz.
    """
    queryset = YokTezUniversite.objects.filter(is_active=True).order_by(
        F('last_checked_at').asc(nulls_first=True)
    )
    if limit:
        queryset = queryset[:limit]

    results = []
    for uni in queryset:
        try:
            total, _ = search(tez_ad=TEST_KEYWORD, universite_id=uni.yok_id, demo_limit=1)
        except Exception as e:
            results.append({'name': uni.name, 'error': str(e)})
            continue

        was_flagged = uni.flagged_for_review
        uni.last_checked_at = timezone.now()
        uni.last_result_count = total
        uni.flagged_for_review = (total == 0)
        uni.save(update_fields=['last_checked_at', 'last_result_count', 'flagged_for_review'])

        results.append({
            'name': uni.name,
            'yok_id': uni.yok_id,
            'result_count': total,
            'flagged': uni.flagged_for_review,
            'cleared': was_flagged and total > 0,
        })

    return results
