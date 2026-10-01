from django.db import migrations

# SEO Faz 1 devamı (1 Ekim 2026). Üç tür değişiklik; hepsi korumalı — canlıdaki metin beklenen
# eski hâlde değilse (admin'den elle düzeltilmişse) dokunulmaz:
#   1) SEO_META: <title>/meta description (alan doluysa yazılmaz)
#   2) REWRITES: içerik baştan yazılır — yalnız MARKER hâlâ içerikteyse
#      - veri kazıma yazısı: "Neden Veri Kazımıyor?" çelişkisi + gerçek dışı ULAKBİM protokolü iddiası
#      - nitel yazısı: yapay zekâ sohbet artığı cümle, tekrarlı H2, kod bloğuna dönüşmüş liste
#   3) T_TABLE: t-testi yazısına t dağılımı kritik değer tablosu ("t tablosu" sorgusu) — ilk bölümden sonra

SEO_META = {
    't-testi-tablosu-teze-nasil-eklenir': (
        't Tablosu (Kritik Değerler) ve t-Testi APA Raporlama',
        "t dağılımı kritik değer tablosu (df 1–∞; α .10, .05, .01) ve SPSS t-testi sonuçlarını teze ekleme: "
        "APA tablo formatı, Levene yorumu ve Cohen's d.",
    ),
    'ucretsiz-spss-alternatifi-var-mi-tez-icin-en-iyi-secenekler': (
        'Ücretsiz SPSS Alternatifleri: jamovi, JASP ve R',
        'SPSS benzeri ücretsiz istatistik programları jamovi, JASP ve R karşılaştırması: tez için hangi '
        'analizde hangisi uygun, jamovi ile ilk analiz adım adım.',
    ),
    'survival-analizi-101-kaplan-meier-cox-regresyon-ve-tedavi-etkili-mi': (
        'Kaplan-Meier ve Cox Regresyon: Sağkalım Analizi Rehberi',
        'Sağkalım (survival) analizi nedir? Sansürlü veri, Kaplan-Meier eğrisi ve log-rank testi, Cox '
        'regresyon varsayımları, SPSS adımları ve hazard ratio raporlama.',
    ),
    'shapiro-wilk-p-0-049-normal-dagitim-var-mi-yok-mu': (
        'Shapiro-Wilk p=0.049: Normal Dağılım Var mı?',
        "Shapiro-Wilk p değeri .05'in hemen altında çıktıysa ne yapmalı? Büyük örneklem duyarlılığı, "
        'kontrol edilecek 3 ek ölçüt, karar algoritması ve APA yazımı.',
    ),
    'analizus-veri-kazima-yok-tez-tr-dizin-openalex': (
        'Literatür İçin Veri Kazıma: YÖK Tez, TR Dizin, OpenAlex',
        "YÖK Tez, TR Dizin ve OpenAlex'ten tez ve makale künyelerini sınırlı ve kurallı biçimde toplayın; "
        'özetler üzerinden konu ve içerik analizi yapın.',
    ),
    'nitel-arastirma-yontemleri': (
        'Kısa Nitel Mülakat: 30 Dakikada Etkili Görüşme Rehberi',
        'Zamanı kısıtlı katılımcılarla 30 dakikalık nitel mülakat: görüşme öncesi hazırlık, süre yönetimi, '
        'sık karşılaşılan zorluklar ve yöntem bölümünde raporlama.',
    ),
}

KAZIMA_CONTENT = """\
<h2>Literatür Taramasında Veri Kazıma (Scraping) Nedir?</h2>
<p>Tez veya makale yazarken araştırmacıların en çok vaktini ve enerjisini alan aşama şüphesiz literatür taramasıdır. Belirli bir konuda yazılmış makaleleri veya tezleri tek tek aramak, başlıklarını kopyalamak, özetlerini okumak ve bu verileri bir Excel dosyasına elle işlemek haftalar sürebilir. <strong>Veri kazıma (web scraping)</strong>, herkese açık kaynaklardaki bu bilgilerin yazılımla sistematik biçimde toplanmasıdır. Analizus, YÖK Ulusal Tez Merkezi, TR Dizin ve OpenAlex için bu işi kod yazmadan yapmanızı sağlayan araçlar sunar.</p>

<h2><a href="/yoktez/">YÖK Tez Arama ve Tarama Aracı →</a></h2>
<p>Türkiye'de yazılmış lisansüstü tezlerin resmî kaynağı olan YÖK Ulusal Tez Merkezi, bibliyometrik çalışmalar ve alan taramaları için zengin bir havuzdur; ancak sonuçları toplu olarak dışa aktarma imkânı sunmaz. <a href="/yoktez/">Analizus'un YÖK Tez aracı</a> ile:</p>
<ul>
  <li>Anahtar kelime, yazar veya danışmana göre arama yapıp eşleşen tezlerin künyelerini (yazar, danışman, yıl, üniversite, enstitü, tür, konu) listeleyebilirsiniz.</li>
  <li>Tezlerin Türkçe ve İngilizce özetlerini künyeyle birlikte alabilirsiniz.</li>
  <li>Sonuçları Excel (.xlsx) veya TXT olarak indirip SPSS, R veya Python'a aktarabilirsiniz.</li>
</ul>
<p>Ücretsiz kullanımda toplam sonuç sayısını ve en yeni kayıtları görürsünüz; tüm sonuç listesine ihtiyaç duyarsanız sipariş oluşturabilirsiniz.</p>
<p><a href="/yoktez/" class="btn btn-sm btn-outline-success">YÖK Tez Aracını Kullan →</a></p>

<h2><a href="/trdizin/">TR Dizin Makale Arama Aracı →</a></h2>
<p>TÜBİTAK ULAKBİM tarafından yönetilen TR Dizin, Türkiye merkezli ulusal hakemli dergilerin dizinidir; doçentlik başvuruları ve yerel literatür taramaları için temel kaynaklardan biridir. <a href="/trdizin/">Analizus'un TR Dizin aracı</a> ile:</p>
<ul>
  <li>Başlık, özet, yazar ve anahtar kelime alanlarında gelişmiş arama yapıp makalelerin başlık, özet, yazar, kurum ve dergi bilgilerini listeleyebilirsiniz.</li>
  <li>Bir konunun yıllara göre nasıl geliştiğini incelemek (trend ve frekans analizi) için ham veri setinizi oluşturabilirsiniz.</li>
</ul>
<p><a href="/trdizin/" class="btn btn-sm btn-outline-primary">TR Dizin Aracını Kullan →</a></p>

<h2><a href="/openalex/">OpenAlex ile Uluslararası Literatür →</a></h2>
<p><strong>OpenAlex</strong>, 240 milyondan fazla akademik yayını kapsayan, verileri CC0 lisansıyla herkese açık bir bibliyografik veri tabanıdır ve Web of Science ile Scopus'a ücretsiz bir alternatif olarak kullanılmaktadır. <a href="/openalex/">Analizus'un OpenAlex aracı</a> ile:</p>
<ul>
  <li>Makale, kitap ve bildirilerin üst verilerini başlık, yazar, dergi, kurum ve yıl gibi alanlarda arayabilirsiniz.</li>
  <li>Atıf sayılarını sonuç listesinde görebilir; h-indeks ve ortalama atıf gibi metriklere <a href="/bibliometrics/">Bibliometrik Analiz</a> raporuyla ulaşabilirsiniz.</li>
  <li>VOSviewer veya CiteSpace gibi programlarda <em>ağ analizi</em> ve <em>ortak yazarlık</em> çalışmaları için veri setinizi hazırlayabilirsiniz.</li>
</ul>
<p><a href="/openalex/" class="btn btn-sm btn-outline-info">OpenAlex Aracını Kullan →</a></p>

<h2>Analizus Veriyi Nasıl Toplar? Sınırlı ve Amaca Yönelik Kazıma</h2>
<p>Analizus veri kazıma yapar; ancak bunu sınırlı ve amaca yönelik biçimde yapar. Temel ilkelerimiz şunlardır:</p>
<ul>
  <li><strong>Yalnızca herkese açık bilgiler:</strong> Kaynakların herkese açık arama arayüzlerinde görünen künye ve özet bilgileri toplanır; giriş gerektiren alanlara erişilmez.</li>
  <li><strong>Tam metin toplu indirilmez:</strong> Tezlerin ve makalelerin tam metinleri (PDF) toplanmaz; tam metne erişim kaynak kurumun kuralları ve yazarın izinleri çerçevesinde kalır.</li>
  <li><strong>Kaynağa yük bindirilmez:</strong> İstekler arasında bekleme süresi bırakılır; kaynak yoğunluk bildirirse istekler yavaşlatılır.</li>
  <li><strong>Resmî arayüz varsa o kullanılır:</strong> OpenAlex verileri resmî API üzerinden, TR Dizin verileri TR Dizin'in herkese açık arama arayüzü üzerinden alınır.</li>
</ul>

<h2>Toplanan Veriyle Ne Yapılır? Metinsel Analizler</h2>
<p>Amaç ham veriyi biriktirmek değil, bir araştırma sorusuna yanıt üretmektir. YÖK Tez sonuçları üzerinden çalışan <strong>Tez Analizi</strong> raporu, tezlerin künye ve özetlerinden yola çıkarak şu analizleri üretir:</p>
<ul>
  <li>Yıllara ve tez türüne göre dağılım, üniversitelere göre üretkenlik</li>
  <li>Anahtar kelime analizi (TF-IDF) ve kelime bulutu</li>
  <li>Konu modelleme (LDA) ile öne çıkan araştırma temaları</li>
  <li>Araştırma konunuza en çok benzeyen tezlerin listesi</li>
</ul>
<p>Bu analizler tam metne değil, künye ve özetlere dayanır; bu nedenle bir alanın genel görünümünü çıkarmak için uygundur. Tam metin üzerinde içerik analizi veya nitel bir çalışma planlıyorsanız <a href="/proje-talebi/">proje talebi</a> oluşturarak uzman desteği alabilirsiniz.</p>

<h2>Tezde Nasıl Yazılır (APA Formatı)</h2>
<p>Bibliyometrik bir tez veya sistematik derleme (systematic review) yazıyorsanız, veriyi nasıl elde ettiğinizi yöntem bölümünde açıkça belirtmelisiniz. Örnek:</p>
<p><em>"Bu araştırmanın veri seti, [tarih] tarihinde Analizus araçları kullanılarak oluşturulmuştur. Belirlenen anahtar kelimeler çerçevesinde YÖK Ulusal Tez Merkezi ve OpenAlex veri tabanlarından ilgili eserlerin üst verileri (başlık, yazar, yıl, özet ve kurum bilgileri) toplanmış ve Excel formatında dışa aktarılmıştır."</em></p>
<p>OpenAlex verisi için kaynak göstermek isterseniz: <em>Priem, J., Piwowar, H., &amp; Orr, R. (2022). OpenAlex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. arXiv. https://doi.org/10.48550/arXiv.2205.01833</em></p>

<h2>Verileri Yorumlarken Dikkat Edilecekler</h2>
<p>Her kaynağın kapsamı ve güncelleme sıklığı farklıdır: TR Dizin yalnızca dizinlediği dergileri, OpenAlex ise kendi indekslediği kaynakları kapsar; bazı kayıtlarda özet veya atıf bilgisi eksik olabilir. Sayıları yorumlarken verinin hangi kaynaktan ve hangi tarihte alındığını not edin; bulgularınızı bu sınırlılıkla birlikte raporlayın.</p>

<h2>Sonuç</h2>
<p>Veri kazıma, literatür taramasının zaman alan kısmını kısaltır; doğru kullanıldığında araştırmacıya alanın genel resmini görme imkânı verir. Analizus bu işi herkese açık kaynaklarla sınırlı, kaynağa saygılı ve şeffaf biçimde yapar; toplanan veriyi künye ve özet düzeyinde metinsel analizlere dönüştürür.</p>
<hr>
<small>
<strong>Kaynakça:</strong><br>
Priem, J., Piwowar, H., &amp; Orr, R. (2022). OpenAlex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. arXiv. https://doi.org/10.48550/arXiv.2205.01833<br>
TÜBİTAK ULAKBİM. TR Dizin. https://trdizin.gov.tr<br>
Yükseköğretim Kurulu (YÖK). Ulusal Tez Merkezi. https://tez.yok.gov.tr
</small>
"""

NITEL_CONTENT = """\
<p>Nitel araştırmalarda mülakatlar geleneksel olarak uzun ve yüz yüze yürütülür. Dijitalleşme ve pandemiyle birlikte çevrim içi ve daha kısa görüşmeler yaygınlaştı. Özellikle ulaşılması zor ve zamanı kısıtlı katılımcılarla (yoğun profesyoneller, yöneticiler, sağlık çalışanları) çalışırken 30 dakikalık bir görüşme, uzun bir görüşmeye hiç ulaşamamaktan daha değerli veri sağlayabilir. Ancak kısa formatın işe yaraması iyi bir hazırlığa bağlıdır.</p>

<h2>Görüşme Öncesi Hazırlık</h2>
<p>30 dakikalık bir süreyi en iyi şekilde değerlendirmek için mülakat öncesinde şu uyarlamalar yapılmalıdır:</p>
<ul>
  <li><strong>Randevu ve iletişim:</strong> Katılımcıları gereksiz e-posta trafiğiyle yormayın. Sabit saatler önermek yerine katılımcıdan uygun olduğu 2–3 zaman dilimini isteyin.</li>
  <li><strong>Onam formu:</strong> Uzun yasal metinler yerine soru-cevap biçiminde (ör. "Gizliliğim nasıl korunacak?") hazırlanmış kısa bir dijital onam formu, katılımı kolaylaştırır. Formun etik kurul onaylı metinle uyumlu olması gerekir.</li>
  <li><strong>Soru tasarımı:</strong> 30 dakikalık bir görüşme için en fazla 4–5 ana soru planlayın. Katılımcı ana dilinde konuşmuyorsa soruları ekran paylaşımıyla göstermek odaklanmayı kolaylaştırır.</li>
  <li><strong>Pilot görüşme:</strong> Kısa görüşmede her dakika değerlidir. Teknik aksaklıkları önlemek ve süre planını sınamak için mutlaka bir deneme görüşmesi yapın.</li>
</ul>

<h2>Görüşme Sırasında Zaman Yönetimi</h2>
<p>Görüşme başladığında süreyi verimli kullanmak için şu teknikler önerilir:</p>
<ul>
  <li><strong>Kısa giriş:</strong> Tanışma ve etik bilgilendirme kısmını 5–7 dakikayla sınırlayın.</li>
  <li><strong>Not yerine kayıt:</strong> Katılımcının onayıyla ses kaydı alın; not tutmakla zaman kaybetmek yerine sohbete odaklanmak veri derinliğini artırır.</li>
  <li><strong>Kibar yönlendirme:</strong> Katılımcı konu dışına çıktığında nazikçe ana soruya dönmenizi sağlayacak hazır ifadeler belirleyin (ör. "Bu çok ilginç; buna sonra dönmek üzere, … konusuna geri gelirsek").</li>
</ul>

<h2>Karşılaşılabilecek Zorluklar ve Çözümleri</h2>
<table>
  <thead><tr><th>Zorluk</th><th>Çözüm</th></tr></thead>
  <tbody>
    <tr><td>Yüzeysel yanıtlar</td><td>"Nasıl?" ve "Neden?" gibi derinleştirme soruları önceden hazırlayın.</td></tr>
    <tr><td>Zayıf bağ kurma</td><td>Görüşmeye atmosferi yumuşatacak bir–iki ısınma sorusuyla başlayın.</td></tr>
    <tr><td>Eksik temalar</td><td>Veri doygunluğuna ulaşılmadıysa katılımcı sayısını artırın.</td></tr>
    <tr><td>Yönlendirme (onaylama) yanlılığı</td><td>Zaman baskısıyla katılımcıyı yönlendirmemek için yarı yapılandırılmış, standart sorular kullanın.</td></tr>
  </tbody>
</table>

<h2>Yöntem Bölümünde Nasıl Yazılır?</h2>
<p>Kısa görüşme formatını kullandıysanız bunu yöntem bölümünde gerekçesiyle belirtin: görüşme süresini, soru sayısını, görüşmenin çevrim içi mi yüz yüze mi yapıldığını, kayıt yöntemini ve veri doygunluğuna nasıl karar verdiğinizi açıkça yazın. Örnek:</p>
<p><em>"Katılımcıların yoğun çalışma programları göz önünde bulundurularak görüşmeler çevrim içi ortamda, yaklaşık 30 dakika süren yarı yapılandırılmış görüşmeler biçiminde yürütülmüştür. Görüşme formu dört ana sorudan oluşmuş, görüşmeler katılımcıların onayıyla ses kaydına alınmıştır."</em></p>

<h2>Sonuç</h2>
<p>Kısa mülakatlar, uzun görüşmelerin yerini tamamen tutmaz; ancak zamanı kısıtlı katılımcılara ulaşmanın gerçekçi bir yoludur. Soru sayısını sınırlamak, pilot görüşme yapmak, görüşme sırasında süreyi bilinçli yönetmek ve sınırlılıkları yöntem bölümünde açıkça raporlamak, bu formatla da güvenilir nitel veri toplamanızı sağlar. Görüşme verilerinizin kodlanması ve tematik analizi için <a href="/uzmanlar/">uzman desteği</a> alabilirsiniz.</p>
"""

REWRITES = {
    'analizus-veri-kazima-yok-tez-tr-dizin-openalex': ('Analizus Neden Veri Kazımıyor?', KAZIMA_CONTENT),
    'nitel-arastirma-yontemleri': ('tasarlamamı ister misiniz', NITEL_CONTENT),
}

T_TABLE_SLUG = 't-testi-tablosu-teze-nasil-eklenir'
T_TABLE_MARKER = 't Dağılımı Kritik Değer Tablosu'
T_TABLE = """\
<h2>t Dağılımı Kritik Değer Tablosu (t Tablosu)</h2>
<p>"t tablosu" denince çoğu zaman t dağılımının kritik değerleri kastedilir. Elle hesaplama yaptığınızda, hesapladığınız t değerinin mutlak değeri tablodaki kritik değerden büyükse sonuç ilgili anlamlılık düzeyinde anlamlıdır. Satırı serbestlik derecesine (df) göre seçin: bağımsız örneklem t-testinde df = n<sub>1</sub> + n<sub>2</sub> − 2, bağımlı (eşleştirilmiş) t-testinde ve tek örneklem t-testinde df = n − 1. Tablodaki df değeriniz yoksa bir alttaki (daha küçük) df satırını kullanmak daha temkinlidir.</p>
<table>
  <thead>
    <tr><th>df</th><th>İki yönlü α = .10<br>(tek yönlü .05)</th><th>İki yönlü α = .05<br>(tek yönlü .025)</th><th>İki yönlü α = .01<br>(tek yönlü .005)</th></tr>
  </thead>
  <tbody>
    <tr><td>1</td><td>6.314</td><td>12.706</td><td>63.657</td></tr>
    <tr><td>2</td><td>2.920</td><td>4.303</td><td>9.925</td></tr>
    <tr><td>3</td><td>2.353</td><td>3.182</td><td>5.841</td></tr>
    <tr><td>4</td><td>2.132</td><td>2.776</td><td>4.604</td></tr>
    <tr><td>5</td><td>2.015</td><td>2.571</td><td>4.032</td></tr>
    <tr><td>6</td><td>1.943</td><td>2.447</td><td>3.707</td></tr>
    <tr><td>7</td><td>1.895</td><td>2.365</td><td>3.499</td></tr>
    <tr><td>8</td><td>1.860</td><td>2.306</td><td>3.355</td></tr>
    <tr><td>9</td><td>1.833</td><td>2.262</td><td>3.250</td></tr>
    <tr><td>10</td><td>1.812</td><td>2.228</td><td>3.169</td></tr>
    <tr><td>11</td><td>1.796</td><td>2.201</td><td>3.106</td></tr>
    <tr><td>12</td><td>1.782</td><td>2.179</td><td>3.055</td></tr>
    <tr><td>13</td><td>1.771</td><td>2.160</td><td>3.012</td></tr>
    <tr><td>14</td><td>1.761</td><td>2.145</td><td>2.977</td></tr>
    <tr><td>15</td><td>1.753</td><td>2.131</td><td>2.947</td></tr>
    <tr><td>16</td><td>1.746</td><td>2.120</td><td>2.921</td></tr>
    <tr><td>17</td><td>1.740</td><td>2.110</td><td>2.898</td></tr>
    <tr><td>18</td><td>1.734</td><td>2.101</td><td>2.878</td></tr>
    <tr><td>19</td><td>1.729</td><td>2.093</td><td>2.861</td></tr>
    <tr><td>20</td><td>1.725</td><td>2.086</td><td>2.845</td></tr>
    <tr><td>21</td><td>1.721</td><td>2.080</td><td>2.831</td></tr>
    <tr><td>22</td><td>1.717</td><td>2.074</td><td>2.819</td></tr>
    <tr><td>23</td><td>1.714</td><td>2.069</td><td>2.807</td></tr>
    <tr><td>24</td><td>1.711</td><td>2.064</td><td>2.797</td></tr>
    <tr><td>25</td><td>1.708</td><td>2.060</td><td>2.787</td></tr>
    <tr><td>26</td><td>1.706</td><td>2.056</td><td>2.779</td></tr>
    <tr><td>27</td><td>1.703</td><td>2.052</td><td>2.771</td></tr>
    <tr><td>28</td><td>1.701</td><td>2.048</td><td>2.763</td></tr>
    <tr><td>29</td><td>1.699</td><td>2.045</td><td>2.756</td></tr>
    <tr><td>30</td><td>1.697</td><td>2.042</td><td>2.750</td></tr>
    <tr><td>40</td><td>1.684</td><td>2.021</td><td>2.704</td></tr>
    <tr><td>60</td><td>1.671</td><td>2.000</td><td>2.660</td></tr>
    <tr><td>80</td><td>1.664</td><td>1.990</td><td>2.639</td></tr>
    <tr><td>100</td><td>1.660</td><td>1.984</td><td>2.626</td></tr>
    <tr><td>120</td><td>1.658</td><td>1.980</td><td>2.617</td></tr>
    <tr><td>∞</td><td>1.645</td><td>1.960</td><td>2.576</td></tr>
  </tbody>
</table>
<p><small>Değerler t dağılımının ters birikimli dağılım fonksiyonundan üç ondalık basamakla hesaplanmıştır; ∞ satırı standart normal dağılım değerleridir.</small></p>
<p>SPSS ve benzeri programlar p değerini doğrudan verdiği için bulgularınızı raporlarken kritik değere ihtiyaç duymazsınız; tablo daha çok elle hesaplama, sınav ve sonuçları kontrol etmek içindir. t-testini kendi verinizle yapmak için <a href="/analiz/ttesti/">ücretsiz t-Testi aracını</a> kullanabilirsiniz.</p>

"""


def forwards(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    for slug, (title, description) in SEO_META.items():
        post = BlogPost.objects.filter(slug=slug).first()
        if post is None:
            print(f'  UYARI: {slug[:55]} bulunamadı')
            continue
        fields = []
        if not post.meta_title:
            post.meta_title = title
            fields.append('meta_title')
        if not post.meta_description:
            post.meta_description = description
            fields.append('meta_description')
        if fields:
            post.save(update_fields=fields)
        print(f"  {'✓' if fields else '='} meta {slug[:50]} {fields or 'dolu, dokunulmadı'}")

    for slug, (marker, content) in REWRITES.items():
        post = BlogPost.objects.filter(slug=slug).first()
        if post is None:
            print(f'  UYARI: {slug[:55]} bulunamadı')
        elif marker in post.content:
            post.content = content
            post.save(update_fields=['content'])
            print(f'  ✓ içerik yenilendi {slug[:50]}')
        else:
            print(f'  = içerik beklenen eski hâlde değil, dokunulmadı {slug[:50]}')

    post = BlogPost.objects.filter(slug=T_TABLE_SLUG).first()
    if post is None:
        print(f'  UYARI: {T_TABLE_SLUG} bulunamadı')
    elif T_TABLE_MARKER in post.content:
        print('  = t tablosu zaten var')
    else:
        first = post.content.find('</h2>')
        second = post.content.find('<h2', first) if first != -1 else -1
        if second == -1:
            hr = post.content.rfind('<hr>')
            second = hr if hr != -1 else len(post.content)
        post.content = post.content[:second] + T_TABLE + post.content[second:]
        post.save(update_fields=['content'])
        print('  ✓ t tablosu eklendi')


class Migration(migrations.Migration):
    dependencies = [('forum', '0162_blog_seo_meta_ctr')]
    # Geri alma içeriği eski hâline döndürmez (eski metin hatalıydı); deploy öncesi DB yedeği esas.
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
