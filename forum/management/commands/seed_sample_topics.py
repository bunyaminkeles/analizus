"""
Gerçek kullanıcılarla örnek forum konuları ve cevapları oluşturur.
Mevcut veriyi SİLMEZ, sadece ekler.

Kullanım:
    python manage.py seed_sample_topics
    docker compose exec web python manage.py seed_sample_topics
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from forum.models import Category, Topic, Post


# ─────────────────────────────────────────────
# İÇERİK — her madde bir konu + N cevap
# starter, replies[*].author → gerçek username'ler
# ─────────────────────────────────────────────
TOPICS = [
    {
        "category_slug": "spss-ve-amos",
        "subject": "SPSS'te Cronbach Alpha değerim neden düşük çıkıyor?",
        "starter": "Rabia",
        "first_post": (
            "Merhaba, tez anketimi SPSS'e girdim ve Cronbach Alpha değerim 0.58 çıkıyor. "
            "Ölçeğim 5'li Likert ve 12 maddeden oluşuyor. Güvenilirliği artırmak için ne yapabilirim? "
            "Madde-toplam korelasyonlarına baktım ama hangi maddeleri çıkarmalıyım konusunda emin olamadım."
        ),
        "replies": [
            {
                "author": "bunyamin",
                "message": (
                    "Merhaba Rabia Hanım. 0.58 değeri 'düşük güvenilirlik' sınırında. "
                    "İlk yapmanız gereken SPSS'te 'Madde Silindiğinde Alpha (Alpha if Item Deleted)' "
                    "sütununa bakmak. Eğer bir maddeyi sildiğinizde Alpha değeri 0.70'in üzerine çıkıyorsa "
                    "o maddeyi güvenle çıkarabilirsiniz. Hangi maddelerde bu durum var?"
                ),
                "is_best_answer": False,
            },
            {
                "author": "figen",
                "message": (
                    "Bende de geçen dönem benzer bir sorun yaşandı. "
                    "Ters kodlanmış madde var mı kontrol edin — o maddeleri çevirmeden analiz yapınca "
                    "Alpha çok düşüyor. SPSS'te Transform > Recode into Different Variables ile "
                    "ters maddeleri düzeltip tekrar deneyin."
                ),
                "is_best_answer": False,
            },
            {
                "author": "joseph",
                "message": (
                    "Another common reason: if your sample size is below 100, Cronbach Alpha tends to be "
                    "unstable. Also check the Inter-Item Correlation Matrix — items with correlations "
                    "below 0.2 are usually the culprits."
                ),
                "is_best_answer": False,
            },
            {
                "author": "open",
                "message": (
                    "Rabia hanım, Analizus'taki Cronbach Alpha aracını denediniz mi? "
                    "Madde-toplam korelasyonlarını ve 'silme sonrası Alpha' değerlerini otomatik "
                    "hesaplıyor, hangi maddeyi çıkarmanız gerektiğini çok net gösteriyor."
                ),
                "is_best_answer": False,
            },
            {
                "author": "Rabia",
                "message": (
                    "Herkese çok teşekkürler! Figen hanımın söylediği ters kodlama meselesini "
                    "gözden kaçırmışım. 3 maddeyi recode ettikten sonra Alpha 0.79'a yükseldi. "
                    "Bunyamin beyin önerdiği madde silme analizini de yapacağım. Çok yardımcı oldunuz!"
                ),
                "is_best_answer": False,
            },
        ],
    },
    {
        "category_slug": "python-ve-veri-bilimi",
        "subject": "Pandas ile eksik veri temizleme — en iyi yöntem hangisi?",
        "starter": "ben",
        "first_post": (
            "Veri setimde bazı sütunlarda eksik değerler var. "
            "dropna() mı kullansam yoksa ortalama ile doldurmak (fillna) daha mı doğru? "
            "Makale için hangisi daha kabul edilebilir bir yöntem?"
        ),
        "replies": [
            {
                "author": "bunyamin",
                "message": (
                    "İkisi de duruma göre doğru olabilir. Eksiklik oranı %5'ten azsa dropna() güvenlidir. "
                    "Fazlaysa ortalama/medyan ile doldurmak (imputation) tercih edilir. "
                    "Akademik çalışmada hangi yöntemi seçtiğini ve nedenini mutlaka metodoloji bölümünde belirtmelisin."
                ),
                "is_best_answer": True,
            },
            {
                "author": "joseph",
                "message": (
                    "For academic work I'd recommend Multiple Imputation (sklearn's IterativeImputer). "
                    "It's statistically more sound than simple mean imputation and reviewers appreciate it."
                ),
                "is_best_answer": False,
            },
            {
                "author": "beyza",
                "message": (
                    "Ben tezimde missingno kütüphanesi ile önce eksiklik haritasını görselleştirdim, "
                    "sonra MCAR/MAR/MNAR ayrımına göre yöntem seçtim. Hakemlerin beğendiği bir yaklaşım."
                ),
                "is_best_answer": False,
            },
        ],
    },
    {
        "category_slug": "tez-makale",
        "subject": "Tez savunması için slayt hazırlarken nelere dikkat etmeliyim?",
        "starter": "beyza",
        "first_post": (
            "Jüri önünde 20 dakika sunumum var. Bulgular bölümünü nasıl anlatmalıyım? "
            "Tablolar mı, grafikler mi daha etkili oluyor? Tecrübelerinizi paylaşır mısınız?"
        ),
        "replies": [
            {
                "author": "bunyamin",
                "message": (
                    "Slaytta tablo yerine grafik tercih et — jüri hızlı okur. "
                    "Her slayta tek mesaj koy, çok bilgi doldurmak dikkat dağıtıyor. "
                    "Bulgular bölümünde 'ne buldun' değil 'ne anlama geliyor' sorusunu cevapla."
                ),
                "is_best_answer": False,
            },
            {
                "author": "figen",
                "message": (
                    "Ben savunmamda her bulgu için bir 'So what?' kutusu ekledim slayta. "
                    "Yani istatistiğin hemen altına pratik anlamını tek cümleyle yazdım. "
                    "Jüri çok olumlu yorum yaptı."
                ),
                "is_best_answer": True,
            },
            {
                "author": "user",
                "message": (
                    "Zaman kontrolü çok önemli. 20 dakika için max 18-20 slayt. "
                    "Ev ödevini yapın — jürinin daha önce sorduğu soruları araştırın."
                ),
                "is_best_answer": False,
            },
            {
                "author": "joseph",
                "message": (
                    "Practice out loud at least 3 times before the defense. "
                    "You'll find the awkward transitions and fix them before the real thing."
                ),
                "is_best_answer": False,
            },
        ],
    },
    {
        "category_slug": "karsilastirma-testleri",
        "subject": "Bağımsız gruplar t-testi mi, Mann-Whitney U mu seçmeliyim?",
        "starter": "user",
        "first_post": (
            "İki grup arasında fark testi yapmam gerekiyor. "
            "Normallik testini yaptım, bir grubun p değeri 0.03 çıktı (Shapiro-Wilk). "
            "Bu durumda parametrik mi yoksa parametrik olmayan test mi kullanmalıyım?"
        ),
        "replies": [
            {
                "author": "bunyamin",
                "message": (
                    "p=0.03 normal dağılım varsayımının ihlal edildiğini gösteriyor. "
                    "Bu durumda Mann-Whitney U testi daha güvenli. "
                    "Ancak örneklem büyüklüğünüz 30'un üzerindeyse Merkezi Limit Teoremi gereği "
                    "t-testi de kabul edilebilir — bunu metodoloji bölümünde gerekçelendirmeniz yeterli."
                ),
                "is_best_answer": True,
            },
            {
                "author": "Rabia",
                "message": (
                    "Hocam, örneklem sayısı kaç olduğunu da paylaşabilirseniz daha net yönlendirme yapılabilir. "
                    "Küçük örneklemde (n<30) normallik ihlali çok daha kritik."
                ),
                "is_best_answer": False,
            },
            {
                "author": "open",
                "message": (
                    "Analizus'taki normallik testi aracını kullandıysanız zaten Shapiro-Wilk sonucunu "
                    "görselleştirmiş olmalısınız. Q-Q plot'a bakmanızı da öneririm — "
                    "tek başına p değeri yanıltıcı olabilir."
                ),
                "is_best_answer": False,
            },
        ],
    },
    {
        "category_slug": "iliski-analizi",
        "subject": "Pearson korelasyon katsayısını tezde nasıl raporlamalıyım?",
        "starter": "figen",
        "first_post": (
            "SPSS'te Pearson korelasyon analizi yaptım. r=0.67, p<0.001 çıktı. "
            "APA formatında bunu nasıl yazmalıyım? "
            "Ayrıca 'orta düzey ilişki' mi 'yüksek ilişki' mi demeliyim?"
        ),
        "replies": [
            {
                "author": "bunyamin",
                "message": (
                    "APA 7 formatı şöyle: r(98) = .67, p < .001 "
                    "(parantez içindeki sayı serbestlik derecesi = n-2). "
                    "Cohen (1988) sınıflandırmasına göre: r=0.67 'güçlü ilişki' kategorisindedir "
                    "(0.50 ve üzeri = güçlü). Tezde bunu referans vererek belirtebilirsiniz."
                ),
                "is_best_answer": True,
            },
            {
                "author": "beyza",
                "message": (
                    "Tezimde tam bu konuda hata yaptım ve hakemin düzeltme istedi. "
                    "APA'da ondalık sayılarda sıfır yazmıyoruz: '0.67' değil '.67' yazılıyor."
                ),
                "is_best_answer": False,
            },
            {
                "author": "joseph",
                "message": (
                    "Also report the confidence interval if possible — it's increasingly expected in APA. "
                    "In SPSS 27+ you can get 95% CI for Pearson r directly from the output."
                ),
                "is_best_answer": False,
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Gerçek kullanıcılarla örnek forum konuları ve cevapları ekler (mevcut veriyi silmez)."

    def handle(self, *args, **kwargs):
        user_cache = {}

        def get_user(username):
            if username not in user_cache:
                try:
                    user_cache[username] = User.objects.get(username=username)
                except User.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"  Kullanıcı bulunamadı: {username}, atlanıyor."))
                    return None
            return user_cache[username]

        created_topics = 0
        created_posts = 0

        for t in TOPICS:
            try:
                category = Category.objects.get(slug=t["category_slug"])
            except Category.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  Kategori bulunamadı: {t['category_slug']}, atlanıyor."))
                continue

            starter = get_user(t["starter"])
            if not starter:
                continue

            # Aynı başlık varsa tekrar oluşturma
            if Topic.objects.filter(subject=t["subject"]).exists():
                self.stdout.write(f"  Zaten var, atlanıyor: {t['subject'][:60]}")
                continue

            topic = Topic.objects.create(
                category=category,
                subject=t["subject"],
                starter=starter,
            )
            created_topics += 1

            Post.objects.create(
                topic=topic,
                created_by=starter,
                message=t["first_post"],
            )
            created_posts += 1

            for reply in t["replies"]:
                author = get_user(reply["author"])
                if not author:
                    continue
                Post.objects.create(
                    topic=topic,
                    created_by=author,
                    message=reply["message"],
                    is_best_answer=reply.get("is_best_answer", False),
                )
                created_posts += 1

            self.stdout.write(self.style.SUCCESS(f"  ✓ {t['subject'][:70]}"))

        self.stdout.write(self.style.SUCCESS(
            f"\nTamamlandı: {created_topics} konu, {created_posts} gönderi oluşturuldu."
        ))
