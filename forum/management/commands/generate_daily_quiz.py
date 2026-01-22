import os
import json
import random
from django.core.management.base import BaseCommand, CommandError
from forum.models import QuizQuestion

try:
    from groq import Groq
except ImportError:
    Groq = None


# Quiz için sabit kategoriler (QuizQuestion.CATEGORY_CHOICES ile uyumlu)
QUIZ_CATEGORIES = {
    'spss': 'SPSS (İstatistiksel analiz yazılımı, veri yönetimi, syntax komutları)',
    'python': 'Python (Pandas, NumPy, SciPy, istatistiksel analiz, veri bilimi)',
    'r': 'R Programlama (tidyverse, ggplot2, istatistiksel modelleme)',
    'statistics': 'İstatistik Teorisi (hipotez testleri, regresyon, ANOVA, korelasyon, olasılık)',
    'methodology': 'Araştırma Metodolojisi (örnekleme, ölçek geliştirme, geçerlilik, güvenilirlik)',
}

DIFFICULTY_LEVELS = ['easy', 'medium', 'hard']


class Command(BaseCommand):
    help = 'Groq AI kullanarak istatistik quiz soruları oluşturur.'

    def add_arguments(self, parser):
        parser.add_argument('--category', type=str, choices=list(QUIZ_CATEGORIES.keys()),
                          help='Belirli bir kategori için soru üret (spss, python, r, statistics, methodology)')
        parser.add_argument('--count', type=int, default=10, help='Üretilecek soru sayısı')
        parser.add_argument('--difficulty', type=str, choices=DIFFICULTY_LEVELS,
                          help='Zorluk seviyesi (easy, medium, hard)')

    def handle(self, *args, **kwargs):
        self.stdout.write("🎯 İstatistik Arena - Quiz Soru Üretimi Başlatılıyor...")

        if not Groq:
            raise CommandError("❌ Groq kütüphanesi eksik. 'pip install groq' çalıştırın.")

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise CommandError("❌ GROQ_API_KEY bulunamadı. .env dosyasını kontrol edin.")

        client = Groq(api_key=api_key)

        # Kategori seçimi
        target_category = kwargs.get('category')
        if target_category:
            selected_categories = {target_category: QUIZ_CATEGORIES[target_category]}
            self.stdout.write(self.style.SUCCESS(f"📌 Hedef Kategori: {target_category.upper()}"))
        else:
            # Rastgele 2-3 kategori seç
            keys = random.sample(list(QUIZ_CATEGORIES.keys()), k=random.randint(2, 3))
            selected_categories = {k: QUIZ_CATEGORIES[k] for k in keys}
            self.stdout.write(f"🎲 Seçilen Kategoriler: {', '.join(keys)}")

        # Zorluk seçimi
        target_difficulty = kwargs.get('difficulty')
        if target_difficulty:
            difficulties = [target_difficulty]
        else:
            difficulties = DIFFICULTY_LEVELS  # Karışık zorluk

        count = kwargs.get('count')

        # Kategori açıklamalarını hazırla
        category_descriptions = "\n".join([
            f"- {key}: {desc}" for key, desc in selected_categories.items()
        ])

        prompt = f"""Sen uzman bir istatistik ve veri bilimi eğitmenisin.
Aşağıdaki kategorilerde toplam {count} adet çoktan seçmeli quiz sorusu hazırla.

KATEGORİLER (sadece bunlardan seç):
{category_descriptions}

ZORLUK SEVİYELERİ: {', '.join(difficulties)}

KURALLAR:
1. Her soru için mutlaka category, difficulty ve explanation alanlarını doldur
2. Sorular Türkçe olmalı
3. Şıklar kısa ve net olmalı (max 100 karakter)
4. Explanation kısmında neden o cevabın doğru olduğunu kısaca açıkla
5. Zorluk dağılımı dengeli olsun

Çıktıyı SADECE geçerli JSON formatında ver:
{{
    "questions": [
        {{
            "category": "kategori_kodu (spss/python/r/statistics/methodology)",
            "difficulty": "easy/medium/hard",
            "question": "Soru metni?",
            "options": {{
                "A": "Seçenek A",
                "B": "Seçenek B",
                "C": "Seçenek C",
                "D": "Seçenek D"
            }},
            "correct_answer": "A/B/C/D",
            "explanation": "Bu cevap doğrudur çünkü..."
        }}
    ]
}}
"""

        try:
            self.stdout.write("⏳ Groq AI soruları hazırlıyor...")
            completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Sen bir JSON API'sin. Sadece geçerli JSON döndür, başka metin yazma."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"},
                temperature=0.7
            )

            response_text = completion.choices[0].message.content.strip()
            data = json.loads(response_text)
            questions_data = data.get("questions", [])

            if not questions_data:
                raise CommandError("❌ AI geçerli soru üretemedi.")

            # Veritabanına kaydet
            saved_count = 0
            category_counts = {}

            for q_data in questions_data:
                category = q_data.get('category', 'statistics')
                difficulty = q_data.get('difficulty', 'medium')

                # Kategori validasyonu
                if category not in QUIZ_CATEGORIES:
                    category = 'statistics'

                # Zorluk validasyonu
                if difficulty not in DIFFICULTY_LEVELS:
                    difficulty = 'medium'

                try:
                    QuizQuestion.objects.create(
                        category=category,
                        difficulty=difficulty,
                        question=q_data.get('question', 'Eksik Soru'),
                        option_a=q_data['options']['A'],
                        option_b=q_data['options']['B'],
                        option_c=q_data['options']['C'],
                        option_d=q_data['options']['D'],
                        correct_answer=q_data.get('correct_answer', 'A').upper(),
                        explanation=q_data.get('explanation', ''),
                    )
                    saved_count += 1
                    category_counts[category] = category_counts.get(category, 0) + 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"⚠️ Soru kaydedilemedi: {str(e)[:50]}"))

            # Sonuç özeti
            self.stdout.write(self.style.SUCCESS(f"\n✅ {saved_count} yeni soru eklendi!"))
            self.stdout.write("📊 Kategori dağılımı:")
            for cat, cnt in category_counts.items():
                self.stdout.write(f"   - {cat}: {cnt} soru")

        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"❌ JSON parse hatası: {str(e)}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Hata: {str(e)}"))
