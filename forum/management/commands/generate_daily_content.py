import os
import json
import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from django.db.models import Q
from django.contrib.auth.models import User
from forum.models import Category, DailyTip, QuizQuestion

# Groq kütüphanesini kullanacağız (pip install groq)
try:
    from groq import Groq
except ImportError:
    Groq = None

class Command(BaseCommand):
    help = 'Groq AI kullanarak Günün İpucu ve Quiz Sorusu üretir ve veritabanına kaydeder.'

    def add_arguments(self, parser):
        parser.add_argument('--topic', type=str, help='İçerik üretilecek özel konu başlığı (örn: "Python")')

    def handle(self, *args, **kwargs):
        if not Groq:
            self.stdout.write(self.style.ERROR("Groq kütüphanesi yüklü değil. 'pip install groq' çalıştırın."))
            return

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            self.stdout.write(self.style.ERROR("GROQ_API_KEY çevre değişkeni bulunamadı."))
            return

        self.client = Groq(api_key=api_key)
        
        # Admin kullanıcısını bul (içerik oluşturucu olarak atamak için)
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR("Admin kullanıcısı bulunamadı."))
            return

        # KONU BELİRLEME MANTIĞI
        topic_title = kwargs.get('topic')
        topic_slug = None

        if topic_title:
            self.stdout.write(f"🎯 Manuel Hedef Konu: {topic_title}")
            # Varsa veritabanından slug'ını bulmaya çalış
            cat = Category.objects.filter(title__icontains=topic_title).first()
            topic_slug = cat.slug if cat else slugify(topic_title)
            if cat: topic_title = cat.title # Başlığı DB'deki düzgün haliyle güncelle
        else:
            # Otomatik Seçim: "Sohbet", "Duyuru" gibi teknik olmayanları hariç tut
            excluded_keywords = ['Sohbet', 'Duyuru', 'Tanışma', 'Lounge', 'Kurallar', 'Hakkımızda', 'Öneri']
            query = Q()
            for keyword in excluded_keywords:
                query |= Q(title__icontains=keyword)
            
            # 1. Adım: Teknik olmayanları ele (Aday Havuzu)
            candidates = Category.objects.exclude(query)
            
            # 2. Adım (Akıllı): Son 3 günde içerik üretilen kategorileri pas geç (Çeşitlilik)
            recent_date = timezone.now().date() - timedelta(days=3)
            recent_titles = DailyTip.objects.filter(publish_date__gte=recent_date).values_list('category', flat=True)
            
            smart_candidates = candidates.exclude(title__in=recent_titles)

            # Eğer akıllı filtre sonucunda aday kalırsa onları kullan, kalmazsa (hepsi yeniyse) eski havuza dön
            if smart_candidates.exists():
                candidates = smart_candidates

            if not candidates.exists():
                self.stdout.write(self.style.ERROR("Hiç uygun kategori bulunamadı."))
                return
            
            selected_category = random.choice(list(candidates))
            topic_title = selected_category.title
            topic_slug = selected_category.slug
            self.stdout.write(f"🎲 Rastgele Seçilen Kategori: {topic_title}")

        # 1. GÜNÜN İPUCUNU ÜRET
        self.generate_daily_tip(topic_title, topic_slug, admin_user)

        # 2. QUIZ SORUSU ÜRET
        self.generate_quiz_question(topic_title, topic_slug)

    def generate_daily_tip(self, topic_title, topic_slug, user):
        self.stdout.write("💡 Günün ipucu üretiliyor...")
        
        prompt = f"""
        {topic_title} konusu hakkında araştırmacılar ve öğrenciler için pratik, az bilinen ve 'hayat kurtarıcı' nitelikte kısa bir ipucu yaz.
        
        Kurallar:
        - Sadece bilgi içeriğini yaz (Başlık veya 'İpucu:' gibi önekler kullanma).
        - Akademik ama samimi bir dil kullan.
        - Maksimum 2-3 cümle olsun.
        - Doğrudan konuya gir.
        """

        try:
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
            )
            content = completion.choices[0].message.content.strip()

            # Veritabanına kaydet
            DailyTip.objects.create(
                title=f"{topic_title} Hakkında İpucu",
                category=topic_slug,
                content=content,
                created_by=user,
                publish_date=timezone.now().date(),
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS("✅ Günün ipucu kaydedildi."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"İpucu üretilirken hata: {e}"))

    def generate_quiz_question(self, topic_title, topic_slug):
        self.stdout.write("❓ Quiz sorusu üretiliyor...")

        # JSON formatında çıktı istiyoruz
        prompt = f"""
        {topic_title} konusu hakkında orta zorlukta, çoktan seçmeli bir soru hazırla.
        Çıktıyı SADECE aşağıdaki JSON formatında ver, başka hiçbir metin yazma:
        {{
            "question": "Soru metni buraya",
            "option_a": "A şıkkı",
            "option_b": "B şıkkı",
            "option_c": "C şıkkı",
            "option_d": "D şıkkı",
            "correct_answer": "A", 
            "difficulty": "medium"
        }}
        Not: correct_answer sadece 'A', 'B', 'C' veya 'D' harfi olmalı.
        """

        try:
            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Sen bir JSON API'sin. Sadece geçerli JSON döndür."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"} # Groq JSON modu
            )
            
            response_content = completion.choices[0].message.content.strip()
            data = json.loads(response_content)

            # Veritabanına kaydet
            QuizQuestion.objects.create(
                category=topic_slug,
                question=data['question'],
                option_a=data['option_a'],
                option_b=data['option_b'],
                option_c=data['option_c'],
                option_d=data['option_d'],
                correct_answer=data['correct_answer'],
                difficulty=data.get('difficulty', 'medium')
            )
            self.stdout.write(self.style.SUCCESS("✅ Quiz sorusu kaydedildi."))

        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR("AI geçerli JSON üretmedi."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Soru üretilirken hata: {e}"))
