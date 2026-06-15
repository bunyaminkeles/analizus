from django.db import migrations

# Her yazı için ~100–150 kelimelik son ek; hepsini 800+ kelimeye taşır.

PATCHES = {
    'chatgpty-e-tezini-yazdirmak-bilim-midir-yoksa-akademinin-olum-sertifikasi-mi': """
<h2>Sonuç: Araştırmacının Sorumluluğu</h2>
<p>Yapay zekanın akademik süreçlere entegrasyonu kaçınılmazdır; ancak bu entegrasyonun sınırlarını bilim insanlarının belirlemesi gerekmektedir. Bir yapay zeka aracı ne kadar gelişmiş olursa olsun, araştırmanın entelektüel ve etik sorumluluğu araştırmacıya aittir. Literatürü eleştirel gözle okumak, metodolojik kararları gerekçelendirmek ve bulguları bağlamında yorumlamak insani bir yetkinliktir; bu yetkinliği devre dışı bırakan her kullanım akademik özgünlüğü zedeler. Uzun vadede yapay zekayı etik ve şeffaf biçimde kullanan araştırmacılar hem itibar hem de beceri açısından öne çıkacaktır.</p>
""",
    'yayinla-ya-da-yok-ol-caginda-akademisyenin-sessiz-intihari-predatory-dergiler': """
<h2>Sonuç: Bilim mi, İtibar Ekonomisi mi?</h2>
<p>Akademik değerlendirme sistemlerinin dönüşümü tek bir araştırmacının gücü dahilinde değildir; ancak her birey hem kendi çalışmalarında niteliği ön planda tutarak hem de predatory dergilere ve atıf kartellerine bilinçli biçimde mesafe koyarak bu dönüşüme katkı sağlayabilir. Bilimsel bilginin toplumsal değeri, yayın sayısından değil o yayınların gerçek dünyaya kattığı anlayıştan gelir. Bu perspektifi korumak, "yayınla ya da yok ol" baskısı altında en değerli akademik direnç biçimidir.</p>
""",
    'turkiyenin-akademik-uretimi-nereye-gidiyor-openalex-ve-tr-dizin-verileriyle': """
<h2>Sonuç ve Değerlendirme</h2>
<p>Türkiye'nin akademik üretimindeki nicel artış, ülkenin global bilim arenasındaki görünürlüğünü artırmaktadır; ancak bu artışın niteliksel boyutta sürdürülebilir olması için politika değişikliği zorunludur. Araştırma değerlendirme sistemlerinin atıf sayısı ve endeks bazlı kriterlerden gerçek bilimsel etki ölçütlerine evrilmesi, hem bireysel araştırmacıları hem de kurumları daha özgün ve derinlikli çalışmalar üretmeye yönlendirecektir. ORCID entegrasyonu, açık erişim politikaları ve uluslararası işbirliği teşvikleri bu dönüşümün pratik araçlarıdır; bu araçları bireysel düzeyde benimsemek, sistemsel değişimi aşağıdan yukarıya inşa etmek anlamına gelir.</p>
""",
    'tez-verilerini-google-driveda-tutmak-suc-mu-kvkk-gdpr': """
<h2>Sonuç: Bilinçli Bir Araştırmacı Olmak</h2>
<p>Kişisel veri güvenliği, artık yalnızca hukuk ve BT departmanlarının değil, her araştırmacının gündeminde yer alması gereken bir sorumluluk alanıdır. Tez sürecinde bu sorumluluğu ciddiye almak yalnızca yasal uyumu değil, araştırma katılımcılarına karşı etik bir yükümlülüğü de yerine getirmek anlamına gelir. Veriyi güvenli saklamak, gerektiğinde anonimleştirmek ve şeffaf bir rıza süreci yürütmek; araştırma kalitesini hem metodolojik hem de etik açıdan güçlendiren temel uygulamalardır.</p>
""",
    'anonimlestirme-yanilgisi-isimsiz-veri-setlerinden-kimlik-yeniden-nasil-insa-ediliyor': """
<h2>Sonuç: Anonimliğin Sınırlarını Tanımak</h2>
<p>Anonimleştirme bir çözüm değil, risk yönetimi aracıdır. Hiçbir yöntem %100 güvence sunamaz; ancak k-anonimlik, diferansiyel gizlilik ve sentetik veri teknikleri riski kabul edilebilir düzeye indirme kapasitesine sahiptir. Araştırmacıların bu teknikleri kendi çalışmalarına uyarlamaları akademik bir zorunluluk olmaktan çıkıp etik bir sorumluluk hâline gelmektedir. Veri mahremiyetine gösterilen bu özen, uzun vadede katılımcı güvenini pekiştirir ve araştırma ekosisteminin sürdürülebilirliğini destekler.</p>
""",
    'saglikta-veri-krizi-turkiyede-klinik-arastirmalarin-verisi-neden-hep-kayip': """
<h2>Sonuç: Verisiz Bilim Olmaz</h2>
<p>Sağlık verisine erişim, bilimsel ilerlemenin temel altyapısıdır. Türkiye'nin e-Nabız gibi güçlü bir altyapıya sahip olmasına karşın bu veriden yeterince yararlanılamaması, ciddi bir fırsat maliyeti doğurmaktadır. Bürokratik engellerin kaldırılması, şeffaf başvuru süreçlerinin oluşturulması ve uluslararası veri paylaşım standartlarının benimsenmesi hem bilimsel hem de toplumsal fayda yaratacaktır. Bu dönüşüm tek bir kurumun değil; sağlık politikacıları, araştırmacılar, etik kurullar ve sivil toplumun ortak çabasıyla mümkün olacaktır.</p>
""",
    'survival-analizi-101-kaplan-meier-cox-regresyon-ve-tedavi-etkili-mi': """
<h2>Sonuç: Zamanı Bir Değişken Olarak Modellemek</h2>
<p>Survival analizi, "olayın gerçekleşip gerçekleşmediği" sorusunun ötesine geçerek "ne zaman gerçekleştiğini" inceleyen güçlü bir araç ailesidir. Kaplan-Meier eğrisi ile görselleştirme, Log-rank testi ile grup karşılaştırması ve Cox regresyonu ile çok değişkenli modelleme; bu üç yöntem birbirini tamamlayan bir analiz silsilesi oluşturur. Sağlıktan sosyal bilimlere, mühendislikten eğitim araştırmalarına uzanan geniş uygulama alanıyla survival analizi, zaman boyutunu dikkate alan her araştırmacının repertuarında yer alması gereken bir metodolojik araçtır.</p>
""",
    'enflasyon-verilerine-guveniyor-muyuz-tuik-enag-resmi-veri-tartismasi': """
<h2>Sonuç: Eleştirel Veri Okuryazarlığı</h2>
<p>Enflasyon verisi tartışması, istatistiksel metodoloji ile kurumsal güven arasındaki derin bağı gözler önüne sermektedir. Bir araştırmacı veya politika analisti olarak bu tartışmaya katılmanın en sağlıklı yolu metodolojik şeffaflığı talep etmek ve kendi analizlerinizde kullandığınız veri kaynağını, yöntemini ve kısıtlarını açıkça belgelemektir. Eleştirel veri okuryazarlığı, rakamları sorgulamayı değil; rakamların nasıl üretildiğini anlamayı ve bu anlayışla yorumlar geliştirmeyi gerektirir.</p>
""",
    'normallik-testi-saglanmazsa-hangi-test-kullanilir': """
<h2>Sonuç: Normallik Testinin Ötesi</h2>
<p>Normallik testi, istatistiksel analizin bir ön koşulu olarak değil; daha büyük bir karar sürecinin parçası olarak ele alınmalıdır. Sadece p değerine bakarak parametrik ya da non-parametrik ayrımı yapmak sığ bir yaklaşımdır; örneklem büyüklüğü, çarpıklık-basıklık değerleri, histogram ve teorik gerekçe birlikte değerlendirilmelidir. Doğru analizi doğru gerekçeyle seçip tezde şeffaflıkla raporlamak, yöntemsel olgunluğun en belirgin göstergesidir.</p>
""",
    'bagimsiz-mi-bagimli-mi-t-testi-fark-ne-zaman-onemli': """
<h2>Bağımlı Tasarımın Güç Avantajı</h2>
<p>Bağımlı (eşleştirilmiş) t-testi, bağımsız t-testine kıyasla genellikle daha yüksek istatistiksel güce sahiptir. Bunun nedeni, bireyler arası farklılıkların (bireyden bireye değişen taban puan farkları) hesaplamadan çıkarılmasıdır; bu sayede hata varyansı azalır ve aynı etki büyüklüğünü daha küçük bir örneklemle tespit etmek mümkün hâle gelir. Bu güç avantajı, boylamsal ve müdahale çalışmalarında bağımlı tasarımı tercih etmenin istatistiksel gerekçesini oluşturur. Araştırma sorunuz ön-test/son-test karşılaştırmasına izin veriyorsa bağımlı tasarımı seçmek hem metodolojik hem de pratik açıdan daha verimlidir.</p>
""",
    'ki-kare-mi-lojistik-regresyon-mu-ikisinin-farki-ne': """
<h2>Sonuç: Araştırma Sorusu Analizi Belirler</h2>
<p>Ki-kare ve lojistik regresyon, kategorik veri analizinin iki temel aracıdır; ancak birbirinin alternatifi değil, tamamlayıcısıdır. "İki kategorik değişken ilişkili mi?" sorusu ki-kareyi, "hangi faktörler bir sonucu öngörür?" sorusu lojistik regresyonu işaret eder. Araştırma sorunuzu analiz yöntemine değil, analiz yöntemini araştırma sorunuza uydurmak metodolojik açıdan doğru yaklaşımdır. Bu ayrımı tezin Yöntem bölümünde açıkça gerekçelendirmek, savunmada jüri güvenini pekiştirecektir.</p>
""",
    'p-degeri-0-05-ten-buyuk-cikti-tezime-ne-yazarim': """
<h2>Sonuç: Anlamsız Bulgu Değersiz Bulgu Değildir</h2>
<p>İstatistiksel anlamlılık eşiğine ulaşamamak, araştırmanın başarısız olduğu anlamına gelmez. Dürüstçe raporlanmış, güç analizi ile desteklenmiş ve etki büyüklüğüyle bütünleştirilmiş null bulgular, akademik bilgi birikimine değerli katkı sağlar. Null sonuçların yayımlanmasından kaçınılması yayın yanlılığına (publication bias) yol açarak meta-analizleri ve sistematik derlemeleri çarpıtmaktadır. Bu anlayışla, p &gt; .05 bulan her araştırmacı bulgusunu titizlikle raporlayıp paylaşmakla hem bireysel akademik sorumluluğunu hem de bilimin kolektif bütünlüğünü korumuş olur.</p>
""",
    'r-kare-dusuk-cikinca-regresyon-modeli-gecersiz-mi': """
<h2>Sonuç: R²'yi Doğru Bağlamda Değerlendirmek</h2>
<p>R² tek başına bir modelin değerini belirleyemez; alanın standartları, teorik gerekçe ve F testinin anlamlılığı birlikte değerlendirilmelidir. Sosyal bilimlerde R² = 0.12, kontrollü fizik deneylerinde zayıf bir model işaretiyken, insan davranışını inceleyen bir çalışmada anlamlı bir başlangıç bulgusudur. Modelin içeriği savunulabilir, katsayılar teorik beklentilerle örtüşüyor ve F testi anlamlıysa; düşük R² bulguyu çürütmez, yalnızca açıklanamayan varyansın başka faktörlerde bulunduğunu gösterir. Bu gerçeği tezinizde tartışmak metodolojik olgunluğun somut bir göstergesidir.</p>
""",
    'korelasyon-yuksek-ama-anlamsiz-bu-nasil-olur': """
<h2>Sonuç: Korelasyonu Bütünsel Okumak</h2>
<p>Korelasyon analizi, iki değişken arasındaki doğrusal ilişkinin yönünü ve gücünü ölçen değerli bir araçtır; ancak tek başına p değeri bu bilgiyi tamamıyla aktaramaz. Güven aralığı, etki büyüklüğü sınıflandırması, örneklem büyüklüğünün analiz gücüne katkısı ve olası karıştırıcı değişkenler birlikte değerlendirildiğinde korelasyon bulgusu çok daha zengin ve savunulabilir bir yoruma kavuşur. Yüksek ama anlamsız korelasyon bulgusu ise araştırmacıyı örneklem planlamasını gözden geçirmeye ve daha büyük bir çalışma tasarlamaya yönlendiren önemli bir metodolojik bilgidir.</p>
""",
    'tez-icin-kac-anket-doldurulmali-orneklem-buyuklugu-nasil-hesaplanir': """
<h2>Sonuç: Örneklem Büyüklüğü Tezin Temeli</h2>
<p>Örneklem büyüklüğü kararı, araştırmanın metodolojik güvenilirliğini doğrudan etkileyen temel bir tasarım sorunudur. "Yeterli mi?" sorusunun cevabı sezgisel tahminlerle değil, güç analizi ve alan standardıyla belirlenen istatistiksel gerekçelerle verilmelidir. Tezin Yöntem bölümünde bu hesabın şeffaflıkla raporlanması, danışman ve jüri güvenini pekiştirir; olası "örneklem küçük" eleştirilerini büyük ölçüde etkisizleştirir. Araştırmaya başlamadan önce yapılan güç analizi, tüm sürecin en değerli metodolojik yatırımlarından biridir.</p>
""",
}


def finalize_batch2(apps, schema_editor):
    import re
    BlogPost = apps.get_model('forum', 'BlogPost')
    ok = fail = 0
    for slug, patch in PATCHES.items():
        try:
            post = BlogPost.objects.get(slug=slug)
        except BlogPost.DoesNotExist:
            print(f'  UYARI: {slug[:50]} bulunamadı')
            continue
        content = post.content
        hr_pos = content.rfind('<hr>')
        post.content = (content[:hr_pos] + patch + content[hr_pos:]) if hr_pos != -1 else content + patch
        post.save()
        text = re.sub(r'<[^>]+>', ' ', post.content)
        wc = len(text.split())
        s = '✓' if wc >= 800 else '✗'
        if wc >= 800:
            ok += 1
        else:
            fail += 1
        print(f'  {s} {wc:4d} | {slug[:50]}')
    print(f'\n  Başarılı: {ok} | Eksik: {fail}')


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0135_expand_blog_batch2_part2'),
    ]

    operations = [
        migrations.RunPython(finalize_batch2, migrations.RunPython.noop),
    ]
