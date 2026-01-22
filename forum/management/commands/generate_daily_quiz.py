import os
import json
import random
from django.core.management.base import BaseCommand, CommandError
from forum.models import QuizQuestion, Category

# Groq kütüphanesini doğrudan kullanalım (Service katmanındaki olası hataları bypass etmek için)
try:
    from groq import Groq
except ImportError:
    Groq = None

class Command(BaseCommand):
    help = 'Groq AI kullanarak belirlenen konularda quiz soruları oluşturur.'

    def add_arguments(self, parser):
        parser.add_argument('--category', type=str, help='Soru üretilecek özel kategori adı (örn: "Python")')
        parser.add_argument('--count', type=int, default=10, help='Üretilecek soru sayısı')

    def handle(self, *args, **kwargs):
        self.stdout.write("🤖 2050 Vizyonu: Otomatik Soru Üretim Modülü Başlatılıyor...")

        if not Groq:
            raise CommandError("❌ Groq kütüphanesi eksik. 'pip install groq' çalıştırın.")

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise CommandError("❌ GROQ_API_KEY bulunamadı. .env dosyasını kontrol edin.")

        client = Groq(api_key=api_key)

        # 1. KATEGORİ SEÇİMİ
        target_category_name = kwargs.get('category')
        selected_categories = []

        if target_category_name:
            # Admin manuel olarak bir konu belirttiyse
            cat = Category.objects.filter(title__icontains=target_category_name).first()
            if cat:
                selected_categories = [cat]
                self.stdout.write(self.style.SUCCESS(f"🎯 Hedef Kategori: {cat.title}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ '{target_category_name}' bulunamadı. Rastgele seçilecek."))
        
        if not selected_categories:
            # Otomatik mod: Rastgele 3 kategori seç (Hepsini seçince AI kafası karışabiliyor)
            all_cats = list(Category.objects.all())
            if not all_cats:
                raise CommandError("❌ Veritabanında hiç kategori yok.")
            selected_categories = random.sample(all_cats, k=min(len(all_cats), 3))
            self.stdout.write(f"🎲 Otomatik Seçilen Konular: {', '.join([c.title for c in selected_categories])}")

        # 2. AI İÇİN PROMPT HAZIRLIĞI
        count = kwargs.get('count')
        topics_str = ", ".join([c.title for c in selected_categories])
        
        prompt = f"""
        Sen uzman bir veri bilimi eğitmenisin. Aşağıdaki konularda toplam {count} adet, akademik kalitede, öğretici, çoktan seçmeli quiz sorusu hazırla.
        Konular: {topics_str}

        Çıktıyı SADECE geçerli bir JSON formatında ver. Başka hiçbir metin yazma.
        JSON şeması şu şekilde olmalıdır:
        {{
            "questions": [
                {{
                    "category_title": "Konu Başlığı (Listeden seç)",
                    "question": "Soru metni",
                    "options": {{
                        "A": "Seçenek A",
                        "B": "Seçenek B",
                        "C": "Seçenek C",
                        "D": "Seçenek D"
                    }},
                    "correct_answer": "A",
                    "explanation": "Doğru cevabın kısa açıklaması",
                    "difficulty": "medium"
                }}
            ]
        }}
        """

        # 3. AI İLE İLETİŞİM
        try:
            self.stdout.write("⏳ AI soruları hazırlıyor...")
            completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Sen bir JSON API'sin. Sadece JSON döndür."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}
            )
            
            response_text = completion.choices[0].message.content.strip()
            data = json.loads(response_text)
            questions_data = data.get("questions", [])

            if not questions_data:
                raise CommandError("❌ AI geçerli soru üretemedi.")
            
            # 4. VERİTABANINA KAYIT
            saved_count = 0
            for q_data in questions_data:
                # Kategoriyi eşleştir
                cat_title = q_data.get('category_title', '')
                category_obj = next((c for c in selected_categories if c.title.lower() in cat_title.lower()), selected_categories[0])
                
                QuizQuestion.objects.create(
                    category=category_obj.slug,
                    question=q_data.get('question', 'Eksik Soru'),
                    option_a=q_data['options']['A'],
                    option_b=q_data['options']['B'],
                    option_c=q_data['options']['C'],
                    option_d=q_data['options']['D'],
                    correct_answer=q_data.get('correct_answer', 'A'),
                    explanation=q_data.get('explanation', ''),
                    difficulty=q_data.get('difficulty', 'medium')
                )
                saved_count += 1

            self.stdout.write(self.style.SUCCESS(f"✅ İşlem Tamamlandı! {saved_count} yeni soru veritabanına eklendi."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Bir hata oluştu: {str(e)}"))