"""
reseed_forum_topics --count 6 düzeltmeden önceki (yanlış) içerikle çalıştırılmıştı:
Danışman arama alanı ve "Analiz Yap" butonu iddiaları gerçek yoktez/forms.py ve
landing.html ile uyuşmuyordu. Bu komut, o 3 konuyu production'da yerinde (aynı
topic pk/URL korunarak) düzeltilmiş metinle günceller. Tek seferlik.

Kullanım:
    docker compose exec web python manage.py fix_yoktez_batch_content
"""
from django.core.management.base import BaseCommand
from forum.models import Topic

FIXES = [
    {
        "starter_username": "AkademikKariyer",
        "old_subject": "YÖK Tez aramasında sonuç 0 çıkıyor, arama neden boş dönüyor?",
        "new_subject": "YÖK Tez aramasında sonuç 0 çıkıyor, arama neden boş dönüyor?",
        "first_post": (
            "Tez konumu 'Tez Adı / Anahtar Kelime' alanına yazıp aradım ama '0 sonuç' "
            "diyor, ama YÖK Tez'in kendi sitesinde aynı kelimeyle onlarca tez buluyorum. "
            "Analizus'taki arama neden farklı sonuç veriyor, bir yazım kuralı mı var?"
        ),
        "answer": (
            "En sık sebep Türkçe karakter farkı: YÖK Tez veritabanı bazı kayıtlarda "
            "'ş, ç, ğ, ö, ü, ı' harflerini, bazılarında ASCII karşılıklarını (s, c, g, o, u, "
            "i) barındırıyor. Aynı terimi hem orijinal Türkçe hem ASCII haliyle aramanızı "
            "öneririm. İkinci sık sebep: 'Tez Adı / Anahtar Kelime' alanı yalnızca başlıkta "
            "geçen kelimeleri tarar; aradığınız kavram başlıkta değil tezin özetinde "
            "geçiyorsa sonuç boş döner — aynı terimi 'Özet/Metin' alanına da girip deneyin, "
            "çoğu zaman sonuç oradan gelir. Üçüncü olarak Başlangıç/Bitiş Yılı aralığının "
            "aradığınız dönemi dışlamadığından emin olun; varsayılan aralık dışındaki "
            "tezler otomatik elenir."
        ),
    },
    {
        "starter_username": "Literatur_Tarama",
        "old_subject": "YÖK Tez'de aynı danışmanın tüm tezlerini tek listede nasıl toplarım?",
        "new_subject": "YÖK Tez'de sadece doktora tezlerini görmek istiyorum, 'Tez Türü' filtresi nasıl çalışıyor?",
        "first_post": (
            "Bir konuda hem yüksek lisans hem doktora tezi çıkıyor, ben sadece doktora "
            "tezlerini incelemek istiyorum. 'Tez Türü' filtresini 'Doktora' seçtiğimde "
            "bazı tezlerin listeden kaybolduğunu fark ettim — bu doğru mu çalışıyor, yoksa "
            "filtre bir şeyi mi kaçırıyor?"
        ),
        "answer": (
            "Doğru çalışıyor — 'Tez Türü' filtresi YÖK'ün kendi sınıflandırmasına göre "
            "süzme yapıyor (Yüksek Lisans, Doktora, Tıpta Uzmanlık, Sanatta Yeterlik). "
            "'Doktora' seçtiğinizde yüksek lisans tezleri listeden düşer, bu beklenen "
            "davranış. Belirli bir tezin YÖK'ün kendi sitesinde doktora olarak görünüp "
            "bizim sonuçlarımızda görünmediğini düşünüyorsanız iki olası sebep var: "
            "Başlangıç/Bitiş Yılı aralığı o tezi kapsam dışı bırakıyor olabilir (aralığı "
            "geniş tutun), ya da YÖK'ün kendi veritabanında o tezin türü farklı kodlanmış "
            "olabilir (nadir ama olur). İlk denemenizde 'Tez Türü'nü 'Hepsi' bırakıp sadece "
            "anahtar kelimeyle arayın, sonuç listesindeki tez türü etiketlerini gözle "
            "kontrol ederek doğrulayın."
        ),
    },
    {
        "starter_username": "VeriBilimci_A",
        "old_subject": "YÖK Tez'den çektiğim verileri bibliyometrik analize nasıl aktarırım?",
        "new_subject": "YÖK Tez arama sonuçlarını Excel yerine e-posta ile almak ne işe yarar, ikisi farklı veri mi veriyor?",
        "first_post": (
            "YÖK Tez aracında arama yaptıktan sonra ekranda 'E-posta Gönder', 'TXT İndir' "
            "ve 'Excel İndir' seçenekleri çıkıyor. Excel'i zaten tarayıcıdan "
            "indirebiliyorken e-posta seçeneği ne işe yarıyor, farklı bir veri mi "
            "gönderiyor?"
        ),
        "answer": (
            "Üçü de aynı sonuç setini farklı teslim şekilleriyle sunuyor, veri içeriği "
            "aynı. 'Excel İndir' ve 'TXT İndir' sonucu doğrudan tarayıcınıza indirir; "
            "'E-posta Gönder' ise aynı Excel dosyasını hesabınıza kayıtlı e-posta adresine "
            "gönderir — özellikle mobil cihazdan çalışıyorsanız ya da sonucu ayrı bir "
            "yerde (başka bilgisayar, arşiv klasörü) tutmak istiyorsanız pratik oluyor. "
            "Demo modunda gösterilen 5 sonuç, hangi teslim şeklini seçerseniz seçin aynı "
            "kapsamdadır; toplam sonuç sayısı arama ekranının üstünde ayrıca belirtilir. "
            "Şunu da netleştireyim: bu Excel dosyasını bizim bibliyometrik analiz "
            "modülümüze doğrudan yükleyemezsiniz — o modül WoS/Scopus/BibTeX/OpenAlex "
            "formatlarını okuyor, YÖK Tez'in çıktısı (tez no, başlık, yazar, danışman, "
            "üniversite, yıl, özet) bu şemayla uyumlu değil, atıf/işbirliği ağı verisi de "
            "içermiyor. YÖK Tez sonuçlarıyla yapabileceğiniz şey, kendi Excel'inizde "
            "yıl/üniversite/tez türü kırılımında betimsel istatistik (sayım, yüzde, basit "
            "grafik) çıkarmaktır; atıf temelli bibliyometrik analiz için WoS/Scopus gibi "
            "farklı bir kaynaktan veri almanız gerekir."
        ),
    },
]


class Command(BaseCommand):
    help = "Yanlış içerikle oluşmuş 3 yöktez forum konusunu yerinde düzeltir — tek seferlik."

    def handle(self, *args, **options):
        for fix in FIXES:
            try:
                topic = Topic.objects.get(subject=fix["old_subject"])
            except Topic.DoesNotExist:
                self.stderr.write(self.style.WARNING(
                    f"Bulunamadı (zaten düzeltilmiş veya hiç oluşmamış olabilir): {fix['old_subject'][:70]}"
                ))
                continue
            except Topic.MultipleObjectsReturned:
                self.stderr.write(self.style.ERROR(
                    f"Birden fazla eşleşme, elle kontrol edin: {fix['old_subject'][:70]}"
                ))
                continue

            starter_post = topic.posts.filter(created_by__username=fix["starter_username"]).order_by("created_at").first()
            admin_post = topic.posts.filter(created_by__username="admin").order_by("created_at").last()

            if starter_post is None or admin_post is None:
                self.stderr.write(self.style.ERROR(f"Post(lar) bulunamadı: {fix['old_subject'][:70]}"))
                continue

            starter_post.message = fix["first_post"]
            starter_post.save(update_fields=["message"])
            admin_post.message = fix["answer"]
            admin_post.save(update_fields=["message"])

            if topic.subject != fix["new_subject"]:
                topic.subject = fix["new_subject"]
                topic.save(update_fields=["subject"])

            self.stdout.write(self.style.SUCCESS(f"Güncellendi: {fix['new_subject'][:70]}"))
