import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from forum.models import Profile

# Modeli dinamik import ediyoruz, eğer models.py'ye eklemediyseniz hata vermesin diye uyaracağız
try:
    from forum.models import SuccessStory
except ImportError:
    SuccessStory = None

class Command(BaseCommand):
    help = 'Başarı hikayelerini (Success Stories) veritabanına yükler'

    def handle(self, *args, **kwargs):
        if not SuccessStory:
            self.stdout.write(self.style.ERROR("❌ HATA: 'SuccessStory' modeli bulunamadı! Lütfen önce forum/models.py dosyasına bu modeli ekleyin."))
            return

        self.stdout.write("✨ Başarı hikayeleri yükleniyor...")
        
        # Mükerrer kayıtları önlemek için eski hikayeleri temizle
        SuccessStory.objects.all().delete()

        # 1. HİKAYE: Ayşe K. (Prompt'taki Örnek)
        user_ayse, _ = User.objects.get_or_create(username="Ayse_K")
        if _:
            user_ayse.set_password("1234")
            user_ayse.first_name = "Ayşe"
            user_ayse.last_name = "K."
            user_ayse.save()
            Profile.objects.create(user=user_ayse, title="Eğitim Bilimleri YL", account_type="Standard")

        story1 = SuccessStory.objects.create(
            user=user_ayse,
            quote="3 ay önce SPSS'i ilk kez açtığımda panik atak geçirdim. Analizus sayesinde korkumu yendim ve analizlerimi kendim yaptım!",
            achievements=[
                "Faktör analizi yaptım",
                "Cronbach Alpha > 0.90 oldu",
                "Tezimi savundum (95/100!)",
                "Danışmanım övdü 🎉"
            ],
            resources=[
                "SPSS Temel Eğitim serisi",
                "Dr_Mehmet'in 15 yanıtı",
                "Canlı Office Hours (3 kez)"
            ],
            likes_count=1245,
            comments_count=67,
            is_featured=True  # BU HAFTANIN HİKAYESİ
        )
        self.stdout.write(f"✅ Eklendi: {user_ayse.username} (Haftanın Hikayesi)")

        # 2. HİKAYE: Can V. (R Studio Başarısı)
        user_can, _ = User.objects.get_or_create(username="Can_Veri")
        if _:
            user_can.set_password("1234")
            user_can.first_name = "Can"
            user_can.last_name = "V."
            user_can.save()
            Profile.objects.create(user=user_can, title="Ekonometri Doktora", account_type="Premium")

        story2 = SuccessStory.objects.create(
            user=user_can,
            quote="R Studio'da kod yazmak bana imkansız geliyordu. Buradaki 'Kopyala-Yapıştır-Düzenle' mantığını öğrenince her şey değişti.",
            achievements=[
                "ggplot2 ile yayın kalitesinde grafik",
                "Zaman serisi analizi tamamlandı",
                "Hakem revizyonlarını 2 günde bitirdim"
            ],
            resources=[
                "R Studio Hızlı Başlangıç",
                "Hata Kodları Kütüphanesi",
                "AnalizBot'un kod düzeltmeleri"
            ],
            likes_count=892,
            comments_count=45,
            is_featured=False
        )
        self.stdout.write(f"✅ Eklendi: {user_can.username}")

        # 3. HİKAYE: Zeynep T. (Nitel Analiz)
        user_zeynep, _ = User.objects.get_or_create(username="Zeynep_Nitel")
        if _:
            user_zeynep.set_password("1234")
            user_zeynep.first_name = "Zeynep"
            user_zeynep.last_name = "T."
            user_zeynep.save()
            Profile.objects.create(user=user_zeynep, title="Sosyoloji Araştırmacısı", account_type="Standard")

        story3 = SuccessStory.objects.create(
            user=user_zeynep,
            quote="Mülakat deşifreleri arasında boğulmuştum. MAXQDA ipuçları sayesinde 1 aylık işi 1 haftada bitirdim.",
            achievements=[
                "20 mülakat kodlandı",
                "Kod haritası oluşturuldu",
                "Makale taslağı bitti"
            ],
            resources=[
                "Nitel Analiz Atölyesi",
                "Forumdaki 'Kodlama Ağacı' tartışması"
            ],
            likes_count=560,
            comments_count=23,
            is_featured=False
        )
        self.stdout.write(f"✅ Eklendi: {user_zeynep.username}")
        self.stdout.write(self.style.SUCCESS("🎉 Tüm başarı hikayeleri yüklendi!"))