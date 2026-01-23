import json
import os
from django.core.management.base import BaseCommand
from forum.models import QuizQuestion


class Command(BaseCommand):
    help = 'quiz_soruları klasöründen soruları import eder'

    def handle(self, *args, **options):
        quiz_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'quiz_soruları')

        if not os.path.exists(quiz_dir):
            self.stdout.write(self.style.ERROR(f'Klasör bulunamadı: {quiz_dir}'))
            return

        # Dosya adı → kategori eşleştirmesi
        category_map = {
            'spss': 'spss',
            'python': 'python',
            'r': 'r',
            'istatistik': 'statistics',
            'araştırma': 'methodology',
            'metodoloji': 'methodology',
        }

        added = 0
        skipped = 0

        for filename in os.listdir(quiz_dir):
            if not filename.endswith('.txt'):
                continue

            # Dosya adından kategori belirle
            file_lower = filename.lower()
            category = 'statistics'  # varsayılan
            for key, cat in category_map.items():
                if key in file_lower:
                    category = cat
                    break

            filepath = os.path.join(quiz_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    questions = json.load(f)
            except json.JSONDecodeError as e:
                self.stdout.write(self.style.ERROR(f'{filename}: JSON hatası - {e}'))
                continue

            for q in questions:
                # Duplicate kontrolü (soru metni)
                if QuizQuestion.objects.filter(question=q['question']).exists():
                    skipped += 1
                    continue

                QuizQuestion.objects.create(
                    question=q['question'],
                    option_a=q['option_a'],
                    option_b=q['option_b'],
                    option_c=q['option_c'],
                    option_d=q['option_d'],
                    correct_answer=q['correct_answer'],
                    category=category,
                    topic=q.get('category', ''),
                    difficulty=q.get('difficulty', 'medium'),
                    explanation=q.get('explanation', ''),
                )
                added += 1

            self.stdout.write(f'{filename} işlendi')

        self.stdout.write(self.style.SUCCESS(f'Tamamlandı: {added} eklendi, {skipped} atlandı (duplicate)'))
