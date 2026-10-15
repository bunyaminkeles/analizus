from django.core.management.base import BaseCommand

from yoktez.services.university_check import check_universities


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
        results = check_universities(limit=options.get('limit'))

        errors = [r for r in results if 'error' in r]
        flagged = sum(1 for r in results if r.get('flagged'))
        cleared = sum(1 for r in results if r.get('cleared'))

        for r in results:
            if 'error' in r:
                self.stderr.write(f"{r['name']}: hata — {r['error']}")
            elif r['flagged']:
                self.stdout.write(self.style.WARNING(f"{r['name']} (ID {r['yok_id']}): 0 sonuç — incelemeye işaretlendi"))
            else:
                self.stdout.write(f"{r['name']} (ID {r['yok_id']}): {r['result_count']} sonuç")

        self.stdout.write(self.style.SUCCESS(
            f'Tamamlandı: {len(results) - len(errors)} üniversite test edildi, {flagged} işaretlendi, {cleared} temizlendi.'
        ))
