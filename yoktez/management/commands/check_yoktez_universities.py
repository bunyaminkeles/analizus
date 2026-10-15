from django.core.management.base import BaseCommand
from django.utils import timezone

from yoktez.models import YokTezUniversite
from yoktez.services.scraper import search

TEST_KEYWORD = 'eğitim'


class Command(BaseCommand):
    help = (
        "Her aktif YokTezUniversite için YÖK Tez'e canlı test araması yapar; "
        "0 sonuç dönenleri flagged_for_review=True yapar. Otomatik silme/deaktive "
        "etme YOK — kapatma kararını admin panelden insan verir."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit', type=int, default=None,
            help='Yalnızca ilk N üniversiteyi test et (ilk kurulum/deneme için)',
        )

    def handle(self, *args, **options):
        qs = YokTezUniversite.objects.filter(is_active=True).order_by('name')
        limit = options.get('limit')
        if limit:
            qs = qs[:limit]

        tested = flagged = cleared = 0
        for uni in qs:
            try:
                total, _ = search(tez_ad=TEST_KEYWORD, universite_id=uni.yok_id, demo_limit=1)
            except Exception as e:
                self.stderr.write(f'{uni.name}: hata — {e}')
                continue

            tested += 1
            uni.last_checked_at = timezone.now()
            uni.last_result_count = total
            if total == 0:
                uni.flagged_for_review = True
                flagged += 1
                self.stdout.write(self.style.WARNING(f'{uni.name} (ID {uni.yok_id}): 0 sonuç — incelemeye işaretlendi'))
            else:
                if uni.flagged_for_review:
                    cleared += 1
                uni.flagged_for_review = False
                self.stdout.write(f'{uni.name} (ID {uni.yok_id}): {total} sonuç')
            uni.save(update_fields=['last_checked_at', 'last_result_count', 'flagged_for_review'])

        self.stdout.write(self.style.SUCCESS(
            f'Tamamlandı: {tested} üniversite test edildi, {flagged} işaretlendi, {cleared} temizlendi.'
        ))
