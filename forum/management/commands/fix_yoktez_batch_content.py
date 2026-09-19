"""
reseed_forum_topics --count 6, düzeltmeden önceki (yanlış) içerikle bir kez
çalıştırılmış, sonra düzeltilmiş TOPICS listesiyle tekrar çalıştırılmıştı.
Sonuç: 2 konu artık ÇİFT var (eski yanlış içerikli + yeni doğru içerikli
aynı konu iki ayrı topic pk'sinde), 1 konunun (subject hiç değişmediği için)
tek kopyası var ama içeriği hâlâ eski/yanlış.

Bu komut:
  1) "sonuç 0 çıkıyor" konusunun post içeriğini yerinde düzeltir (subject aynı
     kaldığı için tek kopya var, silme gerekmez).
  2) Diğer iki konuda, yeni-doğru başlıklı kopya zaten var olduğu için eski
     yanlış kopyayı SİLER (yeniden yazmaz — mükerrer subject'e düşmemek için).

Tek seferlik, idempotent (ikinci çalıştırmada bulacağı bir şey kalmaz).

Kullanım:
    docker compose exec web python manage.py fix_yoktez_batch_content
"""
from django.core.management.base import BaseCommand
from forum.models import Topic

CONTENT_FIX = {
    "starter_username": "AkademikKariyer",
    "subject": "YÖK Tez aramasında sonuç 0 çıkıyor, arama neden boş dönüyor?",
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
}

# (eski/yanlış subject, güvenlik kontrolü için beklenen yeni/doğru subject)
DUPLICATES_TO_DELETE = [
    (
        "YÖK Tez'de aynı danışmanın tüm tezlerini tek listede nasıl toplarım?",
        "YÖK Tez'de sadece doktora tezlerini görmek istiyorum, 'Tez Türü' filtresi nasıl çalışıyor?",
    ),
    (
        "YÖK Tez'den çektiğim verileri bibliyometrik analize nasıl aktarırım?",
        "YÖK Tez arama sonuçlarını Excel yerine e-posta ile almak ne işe yarar, ikisi farklı veri mi veriyor?",
    ),
]


class Command(BaseCommand):
    help = "Yanlış içerikle oluşmuş/çiftlenmiş yöktez forum konularını temizler — tek seferlik."

    def handle(self, *args, **options):
        # 1) İçerik düzeltmesi (subject aynı kaldığı için tek kopya var)
        try:
            topic = Topic.objects.get(subject=CONTENT_FIX["subject"])
        except Topic.DoesNotExist:
            self.stderr.write(self.style.WARNING(f"Bulunamadı: {CONTENT_FIX['subject'][:70]}"))
        except Topic.MultipleObjectsReturned:
            self.stderr.write(self.style.ERROR(f"Birden fazla eşleşme, elle kontrol edin: {CONTENT_FIX['subject'][:70]}"))
        else:
            starter_post = topic.posts.filter(created_by__username=CONTENT_FIX["starter_username"]).order_by("created_at").first()
            admin_post = topic.posts.filter(created_by__username="admin").order_by("created_at").last()
            if starter_post is None or admin_post is None:
                self.stderr.write(self.style.ERROR(f"Post(lar) bulunamadı: {CONTENT_FIX['subject'][:70]}"))
            else:
                starter_post.message = CONTENT_FIX["first_post"]
                starter_post.save(update_fields=["message"])
                admin_post.message = CONTENT_FIX["answer"]
                admin_post.save(update_fields=["message"])
                self.stdout.write(self.style.SUCCESS(f"İçerik düzeltildi: {CONTENT_FIX['subject'][:70]}"))

        # 2) Mükerrer eski/yanlış konuları sil (yeni/doğru kopya var olduğu doğrulanarak)
        for old_subject, new_subject in DUPLICATES_TO_DELETE:
            if not Topic.objects.filter(subject=new_subject).exists():
                self.stderr.write(self.style.ERROR(
                    f"Yeni kopya bulunamadı, silme atlandı (önce reseed_forum_topics çalıştırın): {new_subject[:70]}"
                ))
                continue
            deleted, _ = Topic.objects.filter(subject=old_subject).delete()
            if deleted:
                self.stdout.write(self.style.SUCCESS(f"Eski mükerrer konu silindi: {old_subject[:70]}"))
            else:
                self.stdout.write(f"Zaten yok (temiz): {old_subject[:70]}")
