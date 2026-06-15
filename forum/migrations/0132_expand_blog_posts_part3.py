from django.db import migrations

# 0131 sonrası hâlâ 800 altında kalan 8 yazı için son eklemeler.
# Her PATCH_* değişkeni <hr> etiketinden önce eklenir.

PATCH_26 = """
<h2>Kısmi Eta Kare ve Tam Eta Kare Farkı</h2>
<p>SPSS'te iki yönlü veya çok yönlü ANOVA sonuçlarında <em>Partial Eta Squared</em> (kısmi eta kare, η²p) raporlanır. Kısmi eta kare, bir faktörün yalnızca kendi varyansına ve hata varyansına oranını verir; diğer faktörlerin varyansını payda dışında tutar. Bu nedenle çok faktörlü modellerde η²p değerleri, tam eta kare değerlerinden daha yüksek çıkar ve hatta tüm faktörlerin η²p değerleri toplandığında 1'i aşabilir. Tek yönlü ANOVA'da bu ayrım önemsizdir; kısmi ve tam eta kare değerleri eşittir. Tezinizde hangi eta kare türünü kullandığınızı belirtmek, okuyucunun sonuçları doğru yorumlamasını sağlar.</p>
"""

PATCH_27 = """
<h2>Çift Yönlü Hipotezde Güç ve Örneklem</h2>
<p>Güç analizi yaparken yönlü hipotez (tek yönlü, α = .05 / one-tailed) ile yönsüz hipotez (çift yönlü, α = .025 her kuyruk) arasındaki fark örneklem büyüklüğünü etkiler. Yönlü hipotez daha az katılımcıyla aynı gücü sağlar; ancak yanlış yönde bir etki bulunduğunda yönlü testi geçerli kabul etmek mümkün değildir. Sosyal bilimlerde standart uygulama çift yönlü hipotez olup G*Power'da <em>Two tails</em> seçeneği işaretlenerek hesaplama yapılmalıdır.</p>
"""

PATCH_28 = """
<h2>İç Tutarlılık ile Test-Tekrar Test Güvenilirliği Farkı</h2>
<p>Cronbach Alpha, iç tutarlılık (internal consistency) güvenilirliğini ölçer; ölçeğin maddelerinin birbiriyle ne ölçüde uyumlu olduğunu inceler. Bu, güvenilirliğin yalnızca bir türüdür. Test-tekrar test güvenilirliği ise aynı ölçeğin farklı zamanlarda uygulanmasından elde edilen sonuçların kararlılığını değerlendirir ve Pearson korelasyonu ile ifade edilir. Davranışsal tutumlar gibi zaman içinde değişebilen yapılar için her iki güvenilirlik türünü raporlamak metodolojik derinlik sağlar. Tez kapsamında genellikle iç tutarlılık yeterli kabul edilir; uzunlamasına veya test-tekrar test tasarımı içeren çalışmalarda her iki değerin raporlanması beklenir.</p>
"""

PATCH_32 = """
<h2>Eksik Veri Oranı ve Örneklem Gücü</h2>
<p>Eksik veri yalnızca yanlılık riski yaratmakla kalmaz, aynı zamanda örneklem büyüklüğünü azaltarak istatistiksel gücü düşürür. Liste silme yönteminde her eksik gözlem analizden tamamen çıkarılır; %15 eksik veri bile başlangıçta güç analizine göre belirlenmiş örneklem büyüklüğünü yetersiz kılabilir. Bu nedenle veri toplama aşamasında eksik yanıt oranını en aza indirmeye yönelik önlemler almak — hatırlatma e-postaları, teşvik unsurları, kısa anket tasarımı — araştırma gücünü korumak açısından kritiktir. Tezde bu önlemlerin belirtilmesi de veri kalitesine gösterilen özeni yansıtır.</p>
"""

PATCH_33 = """
<h2>Hangi Program Hangi Dergi Standardına Uygun?</h2>
<p>Uluslararası dergilere makale gönderiyorsanız program seçimi raporlama gereksinimlerini de etkiler. <em>Psychological Science</em> ve <em>Journal of Experimental Psychology</em> gibi dergiler tekrar üretilebilirlik (reproducibility) politikaları kapsamında analiz kodlarının ek dosya olarak sunulmasını talep etmeye başlamıştır. Bu bağlamda R ve Python, kod paylaşımını doğal olarak destekler; SPSS menü işlemleri ise yeniden üretilemez. Eğer uluslararası yayın hedefliyorsanız en azından analizlerinizi R veya Python kodu olarak da belgelemeniz uzun vadede değerli bir yatırım olacaktır.</p>

<h2>Tercih Anketi: Sosyal Bilimciler Ne Kullanıyor?</h2>
<p>Son yıllarda yapılan metodoloji anketleri sosyal bilimlerde program kullanım dağılımının değiştiğini göstermektedir. SPSS hâlâ en yaygın araç olsa da R kullanımı özellikle klinik psikoloji ve eğitim araştırmalarında hızla artmaktadır. Türkiye'deki yüksek lisans ve doktora tezlerinde SPSS baskınlığını korumakta; ancak uluslararası işbirliği içeren projelerde R giderek daha fazla tercih edilmektedir. Araştırma ortamınızı ve hedeflerinizi göz önünde bulundurarak bir seçim yapın — hiçbir program evrensel olarak "doğru" değildir.</p>
"""

PATCH_34 = """
<h2>Ücretsiz Araçlarla Tez Analizi: Pratik Özet</h2>
<p>Tez analizleriniz için SPSS'e ihtiyaç duymadan kaliteli ve savunulabilir sonuçlar üretmek mümkündür. Şu pratik kuralı izleyin: temel analizler (t-testi, ANOVA, korelasyon, regresyon, Cronbach Alpha) için <strong>jamovi veya Analizus</strong>, Bayesyen analiz veya meta-analiz için <strong>JASP</strong>, yapısal eşitlik modellemesi veya çok düzeyli modelleme için <strong>R</strong> kullanın. Bu araçların tamamı ücretsiz, çapraz platform (Windows/Mac/Linux) ve güncel akademik standartlara uyumludur. Danışmanınız SPSS çıktısına alışkınsa jamovi'nin SPSS'e benzer arayüzü adaptasyonu kolaylaştırır; gerekirse aynı analizi jamovi ve SPSS'in ücretsiz deneme sürümüyle karşılaştırmalı olarak gösterebilirsiniz.</p>
"""

PATCH_35 = """
<h2>Savunma Günü Protokolü</h2>
<p>Savunma gününde teknik hazırlığın yanı sıra sunuş biçimi de değerlendirilir. Tablo ve grafikleri sunarken önce "ne" sorusunu (bulgu), ardından "ne anlama gelir" sorusunu (yorum) yanıtlayın. Jüri üyelerine yöneltilen sorularda yanıt vermeden önce soruyu bir cümleyle tekrarlayın; bu hem düşünme süresi kazandırır hem de jüriye sorusunun doğru anlaşıldığını gösterir. Bilmediğiniz bir şeyi biliyormuş gibi sunmak en riskli davranıştır; <em>"Bu konuyu tezimde ele almadım, ancak alanyazına göre şöyle değerlendirilebilir"</em> ifadesi her zaman daha güvenilir karşılanır.</p>
"""

PATCHES = [
    ('anova-sonucu-tezde-nasil-raporlanir-apa-formati', PATCH_26),
    ('t-testi-tablosu-teze-nasil-eklenir', PATCH_27),
    ('cronbach-alpha-guvenilirlik-bulgulari-nasil-yazilir', PATCH_28),
    ('eksik-veri-missing-data-tezde-nasil-ele-alinir', PATCH_32),
    ('spss-mi-r-mi-tez-icin-hangisi-daha-kolay', PATCH_33),
    ('ucretsiz-spss-alternatifi-var-mi-tez-icin-en-iyi-secenekler', PATCH_34),
    ('tez-savunmasinda-istatistik-sorulari-nasil-cevaplanir', PATCH_35),
]


def finalize_content(apps, schema_editor):
    import re
    BlogPost = apps.get_model('forum', 'BlogPost')
    for slug, patch in PATCHES:
        try:
            post = BlogPost.objects.get(slug=slug)
        except BlogPost.DoesNotExist:
            print(f'  UYARI: {slug} bulunamadı')
            continue

        content = post.content
        hr_pos = content.rfind('<hr>')
        post.content = (content[:hr_pos] + patch + content[hr_pos:]) if hr_pos != -1 else content + patch
        post.save()

        text = re.sub(r'<[^>]+>', ' ', post.content)
        wc = len(text.split())
        status = '✓' if wc >= 800 else '✗'
        print(f'  {status} {slug[:50]} ({wc} kelime)')


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0131_expand_blog_posts_part2'),
    ]

    operations = [
        migrations.RunPython(finalize_content, migrations.RunPython.noop),
    ]
