import json
import re
from django.core.management.base import BaseCommand
from forum.models import QuizQuestion
from forum.services.ai_service import groq_service

class Command(BaseCommand):
    help = 'Grok AI kullanarak günlük 20 quiz sorusu oluşturur ve veritabanına kaydeder.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Grok AI ile günlük quiz üretimi başlatılıyor...")

        # AI için Prompt
        prompt = """
        Sen uzman bir veri bilimi eğitmenisin. Aşağıdaki alanlarda toplam 20 adet özgün, öğretici ve akademik kalitede çoktan seçmeli quiz sorusu oluştur:
        Alanlar: SPSS, Python, R Programlama, İstatistik, Akademik Yazım, Makine Öğrenmesi.

        Çıktıyı SADECE geçerli bir JSON listesi olarak ver. Başka hiçbir metin, açıklama veya markdown formatı kullanma.
        
        JSON formatı her soru için şöyle olmalıdır:
        {
            "question": "Soru metni buraya",
            "option_a": "A şıkkı",
            "option_b": "B şıkkı",
            "option_c": "C şıkkı",
            "option_d": "D şıkkı",
            "correct_answer": "A", 
            "explanation": "Doğru cevabın ve konunun kısa açıklaması",
            "category": "Kategori Adı (Örn: SPSS, Python, R, Istatistik, Genel)",
            "difficulty": "Zorluk (Easy, Medium, Hard)"
        }
        """

        try:
            # AI Servisinden yanıt al
            result = groq_service.generate_response(prompt)
            
            if not result['success']:
                self.stdout.write(self.style.ERROR(f"AI Servis Hatası: {result.get('error')}"))
                return

            response_text = result['response']

            # JSON temizleme (Markdown bloklarını kaldır)
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = response_text

            questions_data = json.loads(json_str)

            if not isinstance(questions_data, list):
                self.stdout.write(self.style.ERROR("AI geçerli bir soru listesi döndürmedi."))
                return

            count = 0
            for q in questions_data:
                QuizQuestion.objects.create(
                    question=q.get('question'),
                    option_a=q.get('option_a'),
                    option_b=q.get('option_b'),
                    option_c=q.get('option_c'),
                    option_d=q.get('option_d'),
                    correct_answer=q.get('correct_answer', 'A'),
                    explanation=q.get('explanation', ''),
                    category=q.get('category', 'Genel'),
                    difficulty=q.get('difficulty', 'Medium')
                )
                count += 1

            self.stdout.write(self.style.SUCCESS(f"İşlem tamamlandı: {count} yeni soru eklendi."))

        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR("AI yanıtı geçerli bir JSON formatında değil."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Beklenmeyen hata: {str(e)}"))