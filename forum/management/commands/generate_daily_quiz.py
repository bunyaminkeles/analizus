import json
import re
from django.core.management.base import BaseCommand
from forum.models import QuizQuestion, Category
from forum.services.ai_service import groq_service

class Command(BaseCommand):
    help = 'Groq AI kullanarak günlük 20 quiz sorusu oluşturur ve veritabanına kaydeder.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Groq AI ile günlük quiz üretimi başlatılıyor...")

        # Kategorileri veritabanından dinamik olarak al
        try:
            category_titles = list(Category.objects.values_list('title', flat=True))
            if not category_titles:
                self.stdout.write(self.style.ERROR("Veritabanında hiç kategori bulunamadı. Lütfen önce kategorileri oluşturun."))
                return
            
            # Kategorileri bir stringe dönüştür
            alanlar = ", ".join(category_titles)
            self.stdout.write(f"Şu alanlar için sorular üretilecek: {alanlar}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Kategoriler alınırken hata oluştu: {e}"))
            return

        # AI için Prompt
        prompt = f"""
        Sen uzman bir veri bilimi ve istatistik eğitmenisin. Aşağıdaki alanlarda, her biri için dengeli sayıda olmak üzere, toplam 20 adet özgün, öğretici ve akademik kalitede çoktan seçmeli quiz sorusu oluştur:
        Alanlar: {alanlar}.

        Çıktıyı SADECE geçerli bir JSON listesi olarak ver. Başka hiçbir metin, açıklama veya markdown formatı kullanma. JSON, bir 'questions' anahtarı altında bir liste içermelidir.
        
        JSON formatı her soru için şöyle olmalıdır:
        {{
          "questions": [
            {{
                "question": "Soru metni buraya",
                "option_a": "A şıkkı",
                "option_b": "B şıkkı",
                "option_c": "C şıkkı",
                "option_d": "D şıkkı",
                "correct_answer": "A", 
                "explanation": "Doğru cevabın ve konunun kısa, öğretici açıklaması.",
                "category": "Kategori Adı (örneğin, {category_titles[0] if category_titles else 'SPSS'})",
                "difficulty": "Zorluk (easy, medium, hard)"
            }}
          ]
        }}
        """

        try:
            # AI Servisinden yanıt al
            result = groq_service.generate_response(prompt)
            
            if not result['success']:
                self.stdout.write(self.style.ERROR(f"AI Servis Hatası: {result.get('error')}"))
                return

            response_text = result['response']

            # JSON temizleme (Markdown bloklarını ve preamble'ı kaldır)
            json_match = re.search(r'{\s*"questions":\s*\[.*\]\s*}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                self.stdout.write(self.style.ERROR("AI yanıtında 'questions' anahtarı ile başlayan geçerli bir JSON yapısı bulunamadı."))
                self.stdout.write(f"Alınan yanıt: {response_text}")
                return

            data = json.loads(json_str)
            questions_data = data.get("questions", [])

            if not isinstance(questions_data, list):
                self.stdout.write(self.style.ERROR("AI geçerli bir soru listesi döndürmedi."))
                return
            
            # Modeldeki geçerli choice değerlerini al
            valid_categories = [choice[0] for choice in QuizQuestion.CATEGORY_CHOICES]
            valid_difficulties = [choice[0] for choice in QuizQuestion.DIFFICULTY_CHOICES]

            created_count = 0
            for q_data in questions_data:
                # Gelen veriyi doğrula ve temizle
                category = q_data.get('category', 'statistics').lower()
                if category not in valid_categories:
                    self.stdout.write(self.style.WARNING(f"Geçersiz kategori '{category}', 'statistics' olarak ayarlandı."))
                    category = 'statistics'

                difficulty = q_data.get('difficulty', 'medium').lower()
                if difficulty not in valid_difficulties:
                    self.stdout.write(self.style.WARNING(f"Geçersiz zorluk '{difficulty}', 'medium' olarak ayarlandı."))
                    difficulty = 'medium'
                
                correct_answer = q_data.get('correct_answer', 'A').upper()
                if correct_answer not in ['A', 'B', 'C', 'D']:
                    correct_answer = 'A'

                QuizQuestion.objects.create(
                    question=q_data.get('question', 'Eksik Soru'),
                    option_a=q_data.get('option_a', 'Eksik şık'),
                    option_b=q_data.get('option_b', 'Eksik şık'),
                    option_c=q_data.get('option_c', 'Eksik şık'),
                    option_d=q_data.get('option_d', 'Eksik şık'),
                    correct_answer=correct_answer,
                    explanation=q_data.get('explanation', ''),
                    category=category,
                    difficulty=difficulty
                )
                created_count += 1

            self.stdout.write(self.style.SUCCESS(f"İşlem tamamlandı: {created_count} yeni soru eklendi."))

        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR("AI yanıtı geçerli bir JSON formatında değil."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Beklenmeyen hata: {str(e)}"))