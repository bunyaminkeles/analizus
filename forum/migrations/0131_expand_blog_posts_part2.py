from django.db import migrations

# 0130 migration'ından sonra hâlâ 800 kelime altında kalan yazılar için
# ek bölümler. Her EXTRA_* değişkeni, ilgili yazının <hr> etiketinden önce eklenir.

EXTRA_19 = """
<h2>Özet: Doğru Testi Seçmek İçin 4 Adım</h2>
<ol>
  <li><strong>Grup sayısını belirleyin:</strong> 2 grup → t-testi veya Mann-Whitney U; 3+ grup → ANOVA veya Kruskal-Wallis.</li>
  <li><strong>Normalliği kontrol edin:</strong> Shapiro-Wilk (N &lt; 50) veya KS testi; çarpıklık ve basıklık değerlerine bakın.</li>
  <li><strong>Varyans homojenliğini kontrol edin:</strong> Levene testi p &gt; .05 ise ANOVA devam eder; p ≤ .05 ise Welch ANOVA.</li>
  <li><strong>Etki büyüklüğünü hesaplayın:</strong> ANOVA için η², Mann-Whitney U için rank-biserial r — her ikisi de zorunludur.</li>
</ol>
<p>Bu dört adımı takip ettiğinizde hem doğru analizi seçersiniz hem de danışmanınızın ve jürinizin metodoloji sorularını güvenle yanıtlarsınız.</p>
"""

EXTRA_22 = """
<h2>Pratik Karar Akışı: VIF Sonucunda Ne Yapmalısınız?</h2>
<p>VIF değerlerini elde ettiğinizde şu sırayla ilerleyin:</p>
<ol>
  <li><strong>VIF &lt; 5 ise:</strong> Sorun yok, analizi raporlayın ve devam edin.</li>
  <li><strong>5 ≤ VIF &lt; 10 ise:</strong> Orta düzey sorun; korelasyon matrisini inceleyin, teorik gerekçenizi güçlendirin ve tezde belirtin. Danışmanınıza danışın.</li>
  <li><strong>VIF ≥ 10 ise:</strong> Ciddi sorun. Yüksek korelasyonlu değişken çiftini belirleyin ve şu seçeneklerden birini uygulayın: (a) Teorik açıdan daha az önemli değişkeni çıkarın. (b) Değişkenleri birleştirerek bileşik skor oluşturun. (c) Ridge regresyona geçin.</li>
</ol>
<p>Tezde sonucu ne olursa olsun şeffaf olun: <em>"VIF değerleri 1.12 ile 9.87 arasında değişmiş olup 5.0 eşiğini aşan iki değişken [adları] için tolerans değerleri (.11 ve .14) incelenmiş ve model yorumlanmaya devam edilmiştir."</em></p>
<p>Multicollinearity'nin tespiti ve yönetimi, veri analizi sürecinizin metodolojik olgunluğunu yansıtır. Sorunu bulmak ve raporlamak, sorunu gizlemekten her zaman daha değerlidir.</p>
"""

EXTRA_26 = """
<h2>Tek Yönlü ve Çok Yönlü ANOVA: Raporlama Farkı</h2>
<p>Bu yazıda ele alınan örnekler tek yönlü (one-way) ANOVA için geçerlidir; yalnızca bir bağımsız grup değişkeni incelenmektedir. Çok yönlü (factorial) ANOVA'da iki veya daha fazla bağımsız değişken aynı anda analiz edilir ve etkileşim (interaction) terimi raporlamaya eklenir.</p>
<p>Çok yönlü ANOVA APA raporlama örneği: <em>"Cinsiyet ve eğitim durumunun iş tatmini üzerindeki etkisi 2×3 faktöriyel ANOVA ile incelenmiştir. Cinsiyetin ana etkisi anlamlı bulunmuştur, F(1, 114) = 6.21, p = .014, η² = .052. Eğitim durumunun ana etkisi de anlamlı bulunmuştur, F(2, 114) = 9.14, p &lt; .001, η² = .138. Cinsiyet × eğitim etkileşimi ise anlamlı değildir, F(2, 114) = 1.43, p = .243, η² = .025."</em></p>

<h2>ANOVA Raporlama Kontrol Listesi</h2>
<ul>
  <li>☐ F değeri, serbestlik dereceleriyle birlikte yazıldı: F(2, 117) = 8.43</li>
  <li>☐ p değeri doğru formatta: p = .001 veya p &lt; .001</li>
  <li>☐ Etki büyüklüğü raporlandı: η² veya ω²</li>
  <li>☐ Her grubun N, M ve SD değerleri tabloda verildi</li>
  <li>☐ Anlamlı ANOVA'nın ardından post-hoc testi yapıldı ve raporlandı</li>
  <li>☐ Levene testi sonucu belirtildi</li>
</ul>
"""

EXTRA_27 = """
<h2>Tek Yönlü Hipotez mi, İki Yönlü Hipotez mi?</h2>
<p>SPSS t-testi çıktısında "Sig. (2-tailed)" ifadesini görürsünüz. Araştırmanızda yönlü bir hipotez varsa — örneğin "A grubu B grubundan <em>yüksek</em> olacaktır" — bazı kaynaklar tek yönlü p değerinin (Sig. / 2) kullanılabileceğini belirtir. Ancak büyük çoğunluk iki yönlü testi standart olarak benimser. Tezinizde tek yönlü hipotez testini tercih ederseniz bunu açıkça belirtin; aksi hâlde SPSS'teki iki yönlü (2-tailed) değeri doğrudan kullanın.</p>

<h2>Word'de APA Uyumlu Tablo Oluşturma</h2>
<p>Tezinize eklediğiniz tablonun APA 7 uyumlu olması için dikkat edilmesi gereken noktalar:</p>
<ul>
  <li>Tablo numarası ve başlığı tablonun <em>üstünde</em> yer almalıdır (örn. <em>Tablo 3</em>, bir sonraki satırda italik başlık).</li>
  <li>Sütun başlıkları ortalanabilir; hücre içerikleri genellikle sağa veya sola hizalanır.</li>
  <li>APA tablolarında dikey çizgi (sütun arası ızgara) kullanılmaz; yalnızca üst başlık ve alt sınır çizgileri bulunur.</li>
  <li>Tabloda kullanılan kısaltmalar (M, SD, d) tablo altında <em>Not.</em> satırıyla açıklanır.</li>
</ul>
<p>Word'de tablo oluştururken Tasarım sekmesinde "Tablo Izgarası" stilini seçip ardından dikey çizgileri kaldırmak en hızlı APA-uyumlu görünümü sağlar.</p>
"""

EXTRA_28 = """
<h2>Güvenilirlik Analizi Ne Zaman Yapılır?</h2>
<p>Güvenilirlik analizi araştırma sürecinin <em>veri toplama sonrası, asıl analizler öncesi</em> aşamasında yapılır. Sıralaması önemlidir: önce geçerlik (faktör analizi), ardından güvenilirlik (Cronbach Alpha). Bazı danışmanlar güvenilirliği Yöntem bölümünde, bazıları ise Bulgular'ın ilk başlığı olarak raporlamayı tercih eder; danışmanınızın formatını öğrenin.</p>
<p>Çok boyutlu ölçeklerde her alt boyut için ayrı güvenilirlik analizi yapılmalıdır. Tüm maddeleri birleştirip tek bir alpha değeri hesaplamak, ölçeğin faktör yapısını görmezden gelir ve metodolojik bir hata sayılır.</p>

<h2>Güvenilirlik Bulgusunu Önceki Çalışmalarla Karşılaştırmak</h2>
<p>Güvenilirlik değerinizi yalnızca mutlak eşiklerle (α ≥ .70) değil, ölçeği geliştiren veya aynı ölçeği kullanan önceki çalışmalarla da karşılaştırın. Örneğin: <em>"Mevcut çalışmada güvenilirlik katsayısı α = .82 olarak bulunmuş; bu değer ölçeği geliştiren Meyer ve Allen'ın (1991) raporladığı α = .85 ile Wasti'nin (2000) Türk örneklemindeki α = .79 değerleriyle uyumludur."</em> Bu karşılaştırma ölçek seçiminizin geçerliğini güçlendirir.</p>
"""

EXTRA_31 = """
<h2>Örneklem Büyüklüğünün Test Seçimine Etkisi</h2>
<p>Küçük örneklemlerde (N &lt; 30) normallik testleri yetersiz güce sahiptir; gerçekte normal olmayan bir dağılımı gözden kaçırabilir. Bu durumda histogram ve Q-Q grafiği görsel inceleme açısından daha bilgilendiricidir. Büyük örneklemlerde (N &gt; 200) ise normallik testleri aşırı hassas hâle gelir; gerçekte çok küçük sapmaları dahi anlamlı bulur. Bu nedenle parametrik/non-parametrik karar sürecinde örneklem büyüklüğü, normallik testi p değeri ile birlikte değerlendirilmelidir.</p>
<p>Merkezi Limit Teoremi uyarınca N ≥ 30 olan gruplarda örneklem ortalamasının dağılımı normal dağılıma yaklaşır. Bu nedenle bazı kaynaklarda "N ≥ 30 ise parametrik test kullanılabilir" yargısı yer alır. Ancak bu kural aşırı basitleştirilmiştir; ciddi çarpıklık (|skewness| &gt; 1.5) veya uç değer varlığında daha büyük örneklemlerde de non-parametrik test tercih edilebilir.</p>

<h2>Tezde İki Yaklaşımı Birlikte Raporlamak</h2>
<p>Yöntemsel şeffaflık açısından bazı araştırmacılar hem parametrik hem non-parametrik sonuçları yan yana sunar. Sonuçlar tutarlıysa güçlü bir metodolojik destek sağlar; farklı çıkarsa bulgular bölümünde fark tartışılır. Örnek metin: <em>"Dağılımın normallik sınırında seyretmesi nedeniyle hem t-testi [t(78) = 2.34, p = .022, d = 0.52] hem de Mann-Whitney U testi [U = 612, p = .019, r = .26] uygulanmış; her iki testin de gruplar arasında anlamlı farklılığa işaret ettiği görülmüştür."</em></p>
"""

EXTRA_32 = """
<h2>Eksik Veri İçin Duyarlılık Analizi</h2>
<p>Eksik veri yönteminizin sonuçları etkileyip etkilemediğini doğrulamak için duyarlılık analizi (sensitivity analysis) yapılabilir. Bunun için aynı analizi farklı eksik veri yöntemiyle tekrarlayın: örneğin liste silme ile elde ettiğiniz sonuçları çoklu atama sonuçlarıyla karşılaştırın. Temel bulgular iki yöntemde de tutarlıysa sonuçların eksik veri yöntemine duyarsız olduğu sonucuna varabilirsiniz. Bu karşılaştırma tezde kısa bir paragraf ya da tablo hâlinde sunulabilir ve metodolojik özeni gösterir.</p>

<h2>MNAR Durumunda Seçenekler</h2>
<p>Eksik verinin rastgele olmadığı (MNAR) durum en zorlu senaryodur; yani kişiler belirli bir nedenle yanıt vermiyordur (örneğin yüksek gelirli bireyler gelirlerini açıklamak istemiyordur). Bu durumda hiçbir standart istatistiksel yöntem yanlılığı tamamen gidermez. Seçenekler: (1) MNAR mekanizmasını modelleyen Heckman seçim modeli, (2) pattern-mixture modellemesi, (3) bulgu bölümünde olası yanlılık yönünü açıkça tartışmak. Lisans ve yüksek lisans düzeyindeki çalışmalar için en pratik yaklaşım üçüncü seçenektir: eksik verinin olası yönlü etkisini kısıtlılıklar bölümünde şeffaflıkla tartışın.</p>
"""

EXTRA_33 = """
<h2>Çıktı Kalitesi ve Yayın Süreci</h2>
<p>SPSS çıktıları "yayına hazır" değildir; doğrudan yapıştırılamaz. Her programdan elde edilen grafik ve tabloların APA formatına uyarlanması gerekir. Bu açıdan R ve Python daha esnektir: ggplot2 (R) veya matplotlib/seaborn (Python) ile üretilen grafikler vektör biçiminde (PDF, SVG) kaydedilebilir ve dergilerin yüksek çözünürlük gereksinimlerini karşılar. SPSS grafikleri raster formatında çıktı verir ve çözünürlük sorunları yaşatabilir. Yayın hedefi olan araştırmacılar için grafik kalitesi program seçiminde belirleyici bir faktördür.</p>

<h2>Tez Sonrasında Hangi Program?</h2>
<p>Tezinizi tamamladıktan sonra da araştırma yapacaksanız uzun vadeli program yatırımı yapmak mantıklıdır. Akademik kariyere devam edecekseniz R veya Python öğrenmek hem sizi güçlendirir hem de uluslararası akademik çevrelerde standart araçlarla çalışmanızı sağlar. Endüstriye geçecekseniz Python istatistik + makine öğrenmesi birleşimi çok değerli bir beceri kümesidir. Tezinizi tamamlayıp SPSS ile bitirmek ve ardından R öğrenmek tamamen makul bir stratejidir; iki aracın yarattığı metodolojik çatışma yoktur.</p>
"""

EXTRA_34 = """
<h2>Google Colab ile Ücretsiz Bulut Tabanlı Python İstatistiği</h2>
<p>Kurulum yapmak istemiyorsanız Google Colab (colab.research.google.com) Python ortamını tarayıcıda ücretsiz sunar. Hesabınızla giriş yapın, yeni bir not defteri açın ve doğrudan istatistik kütüphanelerini kullanmaya başlayın:</p>
<pre><code>import scipy.stats as stats
import pandas as pd

df = pd.read_csv('verim.csv')
t_stat, p_val = stats.ttest_ind(df['grup1'], df['grup2'])
print(f't = {t_stat:.3f}, p = {p_val:.3f}')</code></pre>
<p>Colab'ın avantajı: kurulum yok, ücretsiz GPU erişimi, Google Drive entegrasyonu. Dezavantajı: sürekli internet bağlantısı gerektirir ve oturum zaman aşımına uğrar. Temel istatistik analizleri için yeterlidir; uzun süren hesaplamalarda yerel kurulum daha güvenilirdir.</p>

<h2>Hangi Programa Geçmeliyim? Karar Rehberi</h2>
<table>
  <thead><tr><th>Durum</th><th>Öneri</th></tr></thead>
  <tbody>
    <tr><td>SPSS lisansım yok, temel analizler yapacağım</td><td>jamovi (en hızlı başlangıç)</td></tr>
    <tr><td>Bayesyen analiz veya gelişmiş testler gerekiyor</td><td>JASP</td></tr>
    <tr><td>Uzun vadede akademik kariyer planlıyorum</td><td>R + RStudio</td></tr>
    <tr><td>Veri bilimi veya makine öğrenmesiyle birleştirmek istiyorum</td><td>Python + Colab</td></tr>
    <tr><td>Kurulum yapmak istemiyorum, hemen başlayacağım</td><td>Analizus veya Google Colab</td></tr>
  </tbody>
</table>
"""

EXTRA_35 = """
<h2>Jürinin Sormayacağı Ama Hazır Olmanız Gereken Sorular</h2>
<p>Deneyimli jüri üyeleri zaman zaman standart soruların dışına çıkar. Bu sorulara hazırlıklı olmak sizi öne çıkarır:</p>
<ul>
  <li><em>"Bu çalışmayı tekrarlasaydınız ne farklı yapardınız?"</em> — Kısıtlılıklarınızı dürüstçe ifade etmek ve alternatif tasarım seçeneklerini önermeniz metodolojik olgunluğunuzu gösterir.</li>
  <li><em>"Bulgularınızın pratik önemi nedir?"</em> — İstatistiksel anlamlılığı pratik öneme çevirememe sık karşılaşılan bir eksikliktir; etki büyüklüğü ve gerçek dünya bağlamını hazır tutun.</li>
  <li><em>"Başka bir analiz yöntemi daha uygun olabilir miydi?"</em> — Alternatif yaklaşımları bilmek ve neden tercih etmediğinizi açıklamak yeterlidir; her alternatifin avantajını da özetleyin.</li>
</ul>
<p>Bilmediğiniz bir soruyla karşılaştığınızda en güçlü yanıt: <em>"Bu soruyu tezimde ele almadım; ancak [ilgili yaklaşım] üzerinden düşünmek gerekirse şöyle değerlendiririm..."</em> — Spekülasyon değil, çerçevelenmiş düşünce yürütme olarak sunun.</p>
"""


ADDITIONS = [
    ('anova-mi-mann-whitney-mi-hangisini-secmeliyim', EXTRA_19),
    ('vif-degeri-yuksek-cikti-cok-dogrusal-baglanti-ne-demek', EXTRA_22),
    ('anova-sonucu-tezde-nasil-raporlanir-apa-formati', EXTRA_26),
    ('t-testi-tablosu-teze-nasil-eklenir', EXTRA_27),
    ('cronbach-alpha-guvenilirlik-bulgulari-nasil-yazilir', EXTRA_28),
    ('likert-olcegine-hangi-istatistik-testi-uygulanir', EXTRA_31),
    ('eksik-veri-missing-data-tezde-nasil-ele-alinir', EXTRA_32),
    ('spss-mi-r-mi-tez-icin-hangisi-daha-kolay', EXTRA_33),
    ('ucretsiz-spss-alternatifi-var-mi-tez-icin-en-iyi-secenekler', EXTRA_34),
    ('tez-savunmasinda-istatistik-sorulari-nasil-cevaplanir', EXTRA_35),
]


def add_more_content(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    updated = 0
    for slug, extra in ADDITIONS:
        try:
            post = BlogPost.objects.get(slug=slug)
        except BlogPost.DoesNotExist:
            print(f'  UYARI: {slug} bulunamadı, atlanıyor.')
            continue

        content = post.content
        hr_pos = content.rfind('<hr>')
        if hr_pos != -1:
            post.content = content[:hr_pos] + extra + content[hr_pos:]
        else:
            post.content = content + extra
        post.save()

        import re
        text = re.sub(r'<[^>]+>', ' ', post.content)
        wc = len(text.split())
        status = '✓' if wc >= 800 else '✗'
        print(f'  {status} {slug[:50]} ({wc} kelime)')
        updated += 1
    print(f'  Toplam: {updated} yazı güncellendi.')


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0130_expand_thin_blog_posts'),
    ]

    operations = [
        migrations.RunPython(add_more_content, migrations.RunPython.noop),
    ]
