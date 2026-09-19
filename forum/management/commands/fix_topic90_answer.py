"""
YÖK Tez veri kazıma konusundaki (topic pk=90) admin cevabını, samimi
"hocam merhaba" tonundan daha yapılandırılmış/profesyonel bir metne
günceller. Tek seferlik içerik düzeltmesi.

Kullanım:
    docker compose exec web python manage.py fix_topic90_answer
"""
from django.core.management.base import BaseCommand
from forum.models import Topic

NEW_ANSWER = (
    "Merhaba,\n\n"
    "Analizus YÖK Tez veri kazıma aracı, YÖK Ulusal Tez Merkezi'nden anahtar kelime, "
    "yazar veya danışman bazında arama yapmanızı ve sonuçları Excel/TXT formatında "
    "indirmenizi sağlıyor.\n\n"
    "Demo modunda her arama için en yeni 5 sonuç gösteriliyor. Bunun sebebi teknik bir "
    "kısıtlama değil, YÖK'ün kendi sunucusundaki rate-limiting korumasıdır: aynı IP'den "
    "kısa aralıklarla çok sayıda istek gönderilmesi (örneğin kendi Python/Selenium "
    "scriptinizle toplu çekim denemesi) IP'nizin geçici olarak engellenmesine yol "
    "açabiliyor. Bu riski platform tarafında biz üstleniyoruz.\n\n"
    "Aradığınız kritere uyan toplam sonuç sayısını arama ekranında görebilirsiniz. Tüm "
    "veri setine ihtiyacınız varsa: (1) üst menüden Proje Talebi oluşturun, kriterinizi "
    "belirtin, (2) talep planlamaya alınır, işlem öncesi/sonrası e-posta ile "
    "bilgilendirilirsiniz, (3) tam veri seti Excel formatında iletilir.\n\n"
    "Başka bir sorunuz olursa yazabilirsiniz."
)


class Command(BaseCommand):
    help = "topic/90 (YÖK Tez veri kazıma) admin cevabını günceller — tek seferlik."

    def handle(self, *args, **options):
        try:
            topic = Topic.objects.get(pk=90)
        except Topic.DoesNotExist:
            self.stderr.write(self.style.ERROR("Topic pk=90 bulunamadı, ortamlar arası pk farklı olabilir."))
            return

        post = topic.posts.filter(created_by__username="admin").order_by("created_at").last()
        if post is None:
            self.stderr.write(self.style.ERROR("admin kullanıcısına ait post bulunamadı."))
            return

        self.stdout.write(f"Eski mesaj (ilk 60 karakter): {post.message[:60]!r}")
        post.message = NEW_ANSWER
        post.save(update_fields=["message"])
        self.stdout.write(self.style.SUCCESS("Güncellendi."))
