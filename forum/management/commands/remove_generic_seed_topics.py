"""
Faz 12 — seed_forum.py'nin genai_topics/dl_topics/nlp_topics içinden gelen,
sitenin "AI'a güvenme, doğrulat" konumlanmasıyla çelişen jenerik AI konularını
(sabit/uydurma views değerleriyle) kaldırır. Tek seferlik ama idempotent —
konu zaten yoksa sessizce atlar.

Kullanım:
    python manage.py remove_generic_seed_topics
    docker compose exec web python manage.py remove_generic_seed_topics
"""
from django.core.management.base import BaseCommand
from forum.models import Topic


SUBJECTS_TO_REMOVE = [
    "Fine-tuning vs RAG: Şirket verilerimle LLM'i nasıl özelleştirmeliyim?",
    "Prompt Engineering: LLM'lerden en iyi sonucu alma teknikleri",
    "Açık kaynak LLM'ler (LLaMA, Mistral) ile neler yapılabilir?",
    "LLM Halüsinasyonu: Yapay zekanın uydurduğu bilgileri nasıl tespit ederim?",
    "GPU olmadan Deep Learning çalışılabilir mi?",
    "LLM'leri akademik araştırmalarda kullanmanın etik sınırları nerede?",
]


class Command(BaseCommand):
    help = "seed_forum.py'deki jenerik/uydurma-views'lı 6 AI konusunu siler."

    def handle(self, *args, **options):
        deleted_count = 0
        for subject in SUBJECTS_TO_REMOVE:
            deleted, _ = Topic.objects.filter(subject=subject).delete()
            if deleted:
                deleted_count += 1
                self.stdout.write(self.style.SUCCESS(f"  ✓ silindi: {subject[:70]}"))
            else:
                self.stdout.write(f"  zaten yok, atlanıyor: {subject[:70]}")

        self.stdout.write(self.style.SUCCESS(f"\nTamamlandı: {deleted_count} konu silindi."))
