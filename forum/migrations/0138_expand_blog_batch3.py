from django.db import migrations

APPENDIXES = {
    'cronbach-alpha-degeri-tezde-nasil-raporlanir': """
<h2>APA 7 Formatında Cronbach Alfa Raporlama</h2>
<p>Tezde güvenilirlik analizi sonuçlarını doğru biçimde sunmak, jüri ve okuyucuların ölçeğe güven duymasını sağlar. APA 7. baskı formatında Cronbach alfa şöyle raporlanır: <em>"Ölçeğin Cronbach alfa iç tutarlılık katsayısı α = .87 olarak hesaplanmıştır (N = 312)."</em> Parantez içinde örneklem büyüklüğü verilmeli; değer noktalı olarak yazılmalıdır (0.87 değil, .87).</p>

<h2>Alt Boyutlar İçin Raporlama</h2>
<p>Çok boyutlu ölçeklerde her alt boyutun alfa değeri ayrı ayrı raporlanmalıdır. Bunu bir tablo ile sunmak hem okunabilirliği artırır hem de yer kazandırır:</p>
<table class="ax-table">
  <thead>
    <tr><th>Alt Boyut</th><th>Madde Sayısı</th><th>Cronbach α</th></tr>
  </thead>
  <tbody>
    <tr><td>Duygusal Bağlılık</td><td>5</td><td>.84</td></tr>
    <tr><td>Devam Bağlılığı</td><td>4</td><td>.79</td></tr>
    <tr><td>Normatif Bağlılık</td><td>5</td><td>.81</td></tr>
    <tr><td>Toplam</td><td>14</td><td>.88</td></tr>
  </tbody>
</table>

<h2>Düşük Alfa Durumunda Yapılacaklar</h2>
<p>Alfa değeri beklentinin altında çıktığında paniklemek yerine sistematik bir madde analizi yürütülmelidir. SPSS'te "Item-Total Statistics" tablosundaki <em>"Corrected Item-Total Correlation"</em> sütunu her maddenin ölçekle uyumunu gösterir; bu değeri .30'un altında olan maddeler revize edilmeli veya çıkarılmalıdır. <em>"Cronbach's Alpha if Item Deleted"</em> sütunu ise hangi maddenin çıkarılması durumunda alfa değerinin artacağını belirtir. Bir veya iki madde çıkarıldıktan sonra alfa .70 veya üzerine yükseliyorsa bu analiz ve gerekçesi tezin yöntem bölümüne eklenmelidir.</p>

<h2>Kabul Edilebilir Alfa Eşikleri</h2>
<p>George ve Mallery'nin (2003) önerdiği standartlara göre: α ≥ .90 mükemmel, α ≥ .80 iyi, α ≥ .70 kabul edilebilir, α ≥ .60 sorgulanabilir, α &lt; .60 zayıftır. Sosyal bilim araştırmalarında genellikle α ≥ .70 yeterli sayılırken, klinik ölçeklerde α ≥ .80 beklenir. Danışmanınızın ve hedef derginizin standartlarını da gözetmek gerekir.</p>
""",

    'normallik-testi-sonuclari-nasil-yorumlanir-shapiro-wilk-kolmogorov-smirnov': """
<h2>Hangi Test, Ne Zaman?</h2>
<p>Shapiro-Wilk ve Kolmogorov-Smirnov (K-S) testleri aynı soruyu farklı güç düzeyinde yanıtlar. Shapiro-Wilk, özellikle küçük ve orta örneklemlerde (n &lt; 2000) daha güçlüdür ve tercih edilir. K-S testi ise büyük veri setlerinde kullanılabilir; ancak bu testlerin her ikisi de büyük örneklemlerde son derece hassaslaşır ve pratikte önemsiz sapmalar bile anlamlı çıkar.</p>

<h2>Örneklem Büyüklüğünün Kritik Etkisi</h2>
<p>n &lt; 50 ise: Shapiro-Wilk'in düşük güç nedeniyle p &gt; .05 vermesi sık görülür; gözden kaçan normallik sapmaları olabilir. n = 50–200 aralığında: Shapiro-Wilk güvenilir bir karar verir; p &lt; .05 pratikte anlamlı sapma demektir. n &gt; 200 ise: Her iki test de neredeyse her zaman p &lt; .05 verir — bu durumda p değerini değil çarpıklık/basıklık istatistiklerini ve grafiksel yöntemleri esas alın.</p>

<h2>Çarpıklık ve Basıklık Değerleri</h2>
<p>Normallikten sapmanın şiddetini ölçmek için çarpıklık (skewness) ve basıklık (kurtosis) istatistiklerini standart hatayla karşılaştırın: |z| = değer/standart hata. |z| &lt; 1.96 → hafif sapma (α = .05), |z| &lt; 3.29 → orta sapma (α = .001). Alternatif olarak Kim (2013) kabul kriterlerini kullanabilirsiniz: |çarpıklık| &lt; 2 ve |basıklık| &lt; 7 büyük örneklemlerde kabul edilebilirdir.</p>

<h2>Görsel Yöntemler: Q-Q Plot ve Histogram</h2>
<p>Histogram uç değerleri ve genel şekli hızlıca gösterir. Normal Q-Q Plot ise normallik hakkında en bilgilendirici grafiksel araçtır: gözlem noktaları referans çizgisine yakınsa dağılım normale yakındır. Sistematik S-eğrisi yoğun çarpıklığı, referans çizgisinden sapan uç noktalar aykırı değerleri işaret eder. Tezin yöntem bölümüne bu grafiklerin yorumunu eklemeniz beklenir.</p>

<h2>Normallik Sağlanmıyorsa Karar Süreci</h2>
<p>Sapma tespit edildiğinde üç seçenek değerlendirilmelidir: (1) Merkezi Limit Teoremi — n ≥ 30 ve sapma hafif ise parametrik testler genellikle sağlamdır; (2) Dönüşüm — log, karekök veya Box-Cox dönüşümü deneyebilirsiniz, ancak yorum güçleşir; (3) Non-parametrik testler — Mann-Whitney U, Kruskal-Wallis veya Wilcoxon gibi dağılımdan bağımsız testlere geçin. Her durumda kararın gerekçesini tezde şeffaflıkla belirtmek metodolojik olgunluğun göstergesidir.</p>
""",

    'spsste-t-testi-adim-adim-bagimsiz-ve-bagimli-orneklem-karsilastirmasi': """
<h2>SPSS Çıktısını Okuma: Bağımsız Örneklem t-Testi</h2>
<p>Analiz çalıştırıldıktan sonra SPSS iki tablo üretir. İlk tabloda (Group Statistics) grup ortalamaları, standart sapmalar ve örneklem büyüklükleri yer alır. İkinci tabloda (Independent Samples Test) önce Levene testi görülür: p &gt; .05 ise varyanslar eşit kabul edilir ve "Equal variances assumed" satırı okunur; p &lt; .05 ise "Equal variances not assumed" (Welch düzeltmesi) satırı esas alınır. t değeri, serbestlik derecesi (df) ve Sig. (2-tailed) değeri buradan okunur.</p>

<h2>APA 7 Formatında Raporlama</h2>
<p>Bağımsız t-testi APA formatında şöyle yazılır: <em>"Deney grubu (M = 78.4, SD = 9.2) kontrol grubuna (M = 71.6, SD = 10.5) kıyasla anlamlı biçimde yüksek puan almıştır, t(98) = 3.21, p = .002, d = 0.68."</em> Cohen's d etki büyüklüğü SPSS çıktısına eklenmez; formülden hesaplanmalıdır: d = (M₁ − M₂) / SDhavuzlanmış.</p>

<h2>Bağımlı t-Testi SPSS Çıktısı</h2>
<p>Bağımlı t-testinde tek tablo üretilir (Paired Samples Test). "Mean" sütunu ön-test ile son-test arasındaki fark ortalamasını, "t" ve "Sig." ise bu farkın istatistiksel anlamlılığını gösterir. APA raporlama: <em>"Eğitim sonrasında katılımcıların tutum puanları anlamlı biçimde artmıştır (M_fark = 6.3, SD = 4.8), t(49) = 9.28, p &lt; .001, d = 1.31."</em></p>

<h2>Varsayım Kontrolü Tablosu</h2>
<table class="ax-table">
  <thead>
    <tr><th>Varsayım</th><th>Test/Yöntem</th><th>SPSS Menüsü</th></tr>
  </thead>
  <tbody>
    <tr><td>Bağımsızlık</td><td>Tasarım gereği</td><td>—</td></tr>
    <tr><td>Normallik</td><td>Shapiro-Wilk (n &lt; 50)</td><td>Analyze → Descriptive → Explore</td></tr>
    <tr><td>Varyans homojenliği</td><td>Levene testi</td><td>t-testi çıktısında otomatik</td></tr>
    <tr><td>Aykırı değer</td><td>Boxplot</td><td>Graphs → Legacy Dialogs → Boxplot</td></tr>
  </tbody>
</table>

<h2>Sonuç: Çıktıyı Teze Taşımak</h2>
<p>SPSS çıktısını direkt kopyalamak yerine APA stilinde metin ve tablo oluşturmak gerekir. t, df, p ve etki büyüklüğü değerlerini metin içinde veya tabloda raporlayın; ekler bölümüne ham SPSS çıktısı eklenebilir ancak asıl bulgu bölümünde yorumlanmış değerler yer almalıdır.</p>
""",

    'acimlayici-ve-dogrulayici-faktor-analizi-afa-dfa-arasindaki-farklar': """
<h2>AFA: Keşfetmek için</h2>
<p>Açımlayıcı Faktör Analizi (AFA / EFA), verinin altında yatan yapıyı ön kısıtlama koymadan araştırır. Hangi maddenin hangi faktörü ölçtüğü önceden bilinmiyorsa AFA tercih edilir. Ölçek geliştirme çalışmalarının ilk aşamasında, pilot çalışmalarda ve daha önce Türkçeye uyarlanmamış ölçeklerde AFA zorunludur. Analiz, faktör sayısını ve madde yüklerini istatistiksel olarak belirler.</p>

<h2>DFA: Doğrulamak için</h2>
<p>Doğrulayıcı Faktör Analizi (DFA / CFA), önceden teorik veya ampirik olarak belirlenmiş bir yapının veriyle uyumunu test eder. Daha önce AFA ile yapısı belirlenen veya başka kültürlerde doğrulanan bir ölçeği uyarlarken DFA kullanılır. "Bu ölçeğin 3 faktörlü yapısı bizim örneklemimizde de geçerli mi?" sorusunu yanıtlar.</p>

<h2>Uyum İndeksleri: DFA Sonuçlarını Raporlamak</h2>
<table class="ax-table">
  <thead>
    <tr><th>İndeks</th><th>İyi Uyum</th><th>Kabul Edilebilir Uyum</th></tr>
  </thead>
  <tbody>
    <tr><td>χ²/df</td><td>&lt; 2</td><td>&lt; 5</td></tr>
    <tr><td>CFI</td><td>≥ .95</td><td>≥ .90</td></tr>
    <tr><td>TLI</td><td>≥ .95</td><td>≥ .90</td></tr>
    <tr><td>RMSEA</td><td>≤ .05</td><td>≤ .08</td></tr>
    <tr><td>SRMR</td><td>≤ .05</td><td>≤ .10</td></tr>
  </tbody>
</table>

<h2>Hangi Yazılım, Hangi Analiz?</h2>
<p>AFA için SPSS (Factor Analysis menüsü) ve R'da <code>psych</code> paketi yaygın kullanılır. DFA için SPSS tek başına yetersizdir; AMOS, R'da <code>lavaan</code>, Mplus veya SmartPLS gibi yapısal denklem modelleme yazılımları gereklidir. Tez bütçesi kısıtlıysa ücretsiz <code>lavaan</code> + RStudio kombinasyonu tercih edilebilir.</p>

<h2>Yaygın Hatalar</h2>
<p>En sık karşılaşılan hata, aynı veriyle önce AFA sonra DFA yapmaktır — bu istatistiksel olarak hatalıdır çünkü DFA'nın amacı bağımsız bir veriyi doğrulamaktır. Doğru yol: veriyi ikiye bölün, yarısıyla AFA yapın, diğer yarısıyla DFA'yı doğrulayın ya da bağımsız bir örneklemle doğrulama çalışması yürütün.</p>
""",

    'tezde-yapilan-en-sik-10-istatistik-hatasi-ve-nasil-onlenir': """
<h2>1–5. Sıradaki Hatalar</h2>
<ol>
  <li><strong>Normallik testini atlama:</strong> Parametrik test uygulamadan önce Shapiro-Wilk veya Q-Q plot ile normallik mutlaka kontrol edilmelidir.</li>
  <li><strong>p &lt; .05 = etki büyük sanmak:</strong> p değeri yalnızca şans eseri sonuç olup olmadığını söyler. Cohen's d, η², r gibi etki büyüklükleri olmadan sonuç eksik kalır.</li>
  <li><strong>Çoklu karşılaştırmalarda Bonferroni uygulamamak:</strong> 5 grup arası farkları ikişer ikişer t-testi ile karşılaştırmak Tip I hata oranını şişirir; ANOVA sonrası post-hoc düzeltme zorunludur.</li>
  <li><strong>N+1 sorunu — küçük örneklem:</strong> Güç analizi yapılmadan toplanan veri yetersiz güçte kalır; sonuç ne kadar olumlu olursa olsun anlamlı çıkmayabilir.</li>
  <li><strong>Aykırı değerleri görmezden gelmek:</strong> Ortalama bazlı analizler (t, ANOVA, regresyon) aykırı değerlere duyarlıdır; boxplot ile tespit edip raporlamak gerekir.</li>
</ol>

<h2>6–10. Sıradaki Hatalar</h2>
<ol start="6">
  <li><strong>Korelasyonu nedensellik saymak:</strong> "A arttığında B artıyor" ifadesi yalnızca ilişkiyi tanımlar; neden-sonuç ilişkisi deneysel tasarım veya uzunlamasına çalışma gerektirir.</li>
  <li><strong>Eksik veriyi silmek:</strong> Listwise deletion örneklemi sistematik olarak saptırabilir; SPSS'te Multiple Imputation veya R'da <code>mice</code> paketi tercih edilmelidir.</li>
  <li><strong>Regresyonda çoklu doğrusal bağlantı:</strong> VIF &gt; 10 veya Tolerance &lt; .10 çoklu doğrusal bağlantıyı işaret eder; bu varsayım ihlali raporlanmalıdır.</li>
  <li><strong>Güvenilirlik analizi olmadan ölçek kullanmak:</strong> Bir ölçeğin daha önce güvenilir bulunmuş olması, sizin örnekleminizde de güvenilir olacağını garanti etmez; Cronbach alfa mutlaka hesaplanmalıdır.</li>
  <li><strong>Sonuç tablosu yerine ham SPSS çıktısı koymak:</strong> Tezin bulgu bölümüne ham ekran görüntüsü değil, APA uyumlu özet tablolar ait olur.</li>
</ol>

<h2>Hızlı Kontrol Listesi</h2>
<p>Tezi teslim etmeden önce her analiz için şu soruları yanıtlayın: (1) Varsayımları kontrol ettim mi? (2) Etki büyüklüğünü raporladım mı? (3) Örneklem büyüklüğünü güç analiziyle gerekçelendirdim mi? (4) Aykırı değerleri ele aldım mı? (5) Sonuçları APA formatında sundum mu? Bu beş soruya "evet" cevabı verebildiğinizde metodolojik savunma hazırlığınız tamamdır.</p>
""",

    'p-degeri-krizinin-100-yilinda-istatistiksel-anlamlilik-bilimi-yanlis-mi-yonlendirdi': """
<h2>p Değerinin Kısa Tarihi</h2>
<p>Ronald Fisher 1925'te p &lt; .05 eşiğini kesin bir karar kuralı olarak değil, araştırmacının takdirine bırakılmış sezgisel bir kılavuz olarak önerdi. Jerzy Neyman ve Egon Pearson ise aynı dönemde Tip I/Tip II hata dengesini vurgulayan farklı bir çerçeve geliştirdi. Bu iki yaklaşım yıllar içinde harmanlanarak "p &lt; .05 ise anlamlı" şeklinde yarım kalan bir pratiğe dönüştü; Fisher'in kendisi bu çarpıtmaya itiraz etti.</p>

<h2>Ne Yanlış Gitti?</h2>
<p>Temel sorun, p değerinin taşıdığı sınırlı bilginin gerçeği tam yansıtır gibi yorumlanmasıdır. p = .04 bulan bir araştırma "anlamlı" olarak yayımlanır; p = .06 bulan aynı kalitede bir araştırma "anlamsız" ilan edilir. Bu yapay sınır, (1) yayın yanlılığını (publication bias), (2) p-hacking ve HARKing (Hypothesizing After Results are Known) gibi araştırma esnekliği sorunlarını ve (3) düşük replikasyon oranlarını beraberinde getirdi.</p>

<h2>Replikasyon Krizi</h2>
<p>2015 yılında Nosek ve ark. koordinasyonuyla yürütülen Replikasyon Projesi, 100 psikoloji çalışmasının yalnızca %39'unun özgün bulgularını koruduğunu ortaya koydu. Tıp, nörobilim ve sosyal bilimlerde benzer bulgular raporlandı. Bu kriz, p değerine dayalı karar mantığının tek başına yetersiz olduğunu tartışmasız biçimde ortaya koydu.</p>

<h2>Alternatif Yaklaşımlar</h2>
<ul>
  <li><strong>Etki büyüklüğü + güven aralığı:</strong> Cohen's d, η², r değerlerini %95 güven aralıklarıyla birlikte raporlayın — hem pratik önemi hem belirsizliği gösterir.</li>
  <li><strong>Bayes faktörü (BF):</strong> H₀ ve H₁ arasındaki kanıt oranını verir; BF &gt; 10 güçlü kanıt anlamına gelir.</li>
  <li><strong>Ön kayıt (pre-registration):</strong> AsPredicted.org veya OSF üzerinden hipotez ve analiz planını veriye bakmadan kaydedin; bu p-hacking'i önler.</li>
  <li><strong>NHST'ye ek olarak:</strong> p değerini tamamen terk etmek zorunda değilsiniz — ancak etki büyüklüğü, güven aralığı ve örneklem büyüklüğü ile birlikte yorumlayın.</li>
</ul>

<h2>Sonuç: Araştırmacı Ne Yapmalı?</h2>
<p>p değeri bir karar kuralı değil, olasılık ifadesidir. Tezinizde p &lt; .05 eşiği bulguların kısmi destekleyicisi olarak gösterilebilir; ancak etki büyüklüğü ve %95 güven aralığı olmadan eksik kalır. Ön kayıt yaparak şeffaflığı artırmak, replique edilebilir bilimin en pratik bireysel katkısıdır. p değeri krizi araştırmacılara bir uyarı değil, metodolojik genişleme daveti sunar.</p>
""",

    'veri-sahteliginden-veri-seffafligina-open-science-hareketi-ve-turkiyede-acik-veri': """
<h2>Open Science Nedir?</h2>
<p>Açık Bilim (Open Science), araştırma sürecinin tüm bileşenlerini — veriyi, kodu, materyalleri, ön kayıtları ve çıktıları — kamuoyuyla şeffaf biçimde paylaşmayı hedefleyen bir felsefe ve pratikler bütünüdür. Bu hareket, 2010'ların başında artan replikasyon krizi baskısı, yayın yanlılığı eleştirileri ve araştırma hilesine yönelik kamuoyu ilgisiyle ivme kazandı.</p>

<h2>Temel Bileşenler</h2>
<ul>
  <li><strong>Açık erişim (Open Access):</strong> Yayınları paywallsız erişilebilir kılmak — arXiv, PsyArXiv, TR Dizin açık erişim koleksiyonları.</li>
  <li><strong>Açık veri (Open Data):</strong> Ham veri setlerini OSF, Zenodo, Figshare gibi havuzlarda paylaşmak; FAIR ilkeleri (Findable, Accessible, Interoperable, Reusable) rehber alınır.</li>
  <li><strong>Açık materyal (Open Materials):</strong> Anket formları, deney prosedürleri ve analiz kodlarının paylaşımı.</li>
  <li><strong>Ön kayıt (Pre-registration):</strong> Veri toplamadan önce hipotez ve analiz planını zaman damgasıyla kaydetmek — OSF Registries, AsPredicted.org.</li>
</ul>

<h2>Türkiye'de Açık Bilim Durumu</h2>
<p>Türkiye'nin ulusal açık erişim politikası henüz olgunlaşma aşamasındadır. TÜBİTAK, 2020'den itibaren desteklediği projelerde açık erişim yayın zorunluluğunu genişletmektedir. TR Dizin açık erişim desteği sunan ulusal dergileri ön plana çıkarmakta; OpenAlex ise ülkemizin uluslararası görünürlüğünü bibliyometrik olarak izlemeye olanak tanımaktadır. Bununla birlikte, araştırma veri depolarının yaygınlaşması, etik kurul süreçlerinin açık veriye uyumu ve veri anonimleştirme altyapısının güçlendirilmesi Türkiye'nin önündeki acil gündem maddeleridir.</p>

<h2>Araştırmacı için Pratik Adımlar</h2>
<ol>
  <li>ORCID kimliği oluşturun ve tüm yayınlarınızı bağlayın.</li>
  <li>Tez verinizi OSF veya Zenodo'da depolayın; bağlantıyı teze ve yayına ekleyin.</li>
  <li>Analizleri yeniden üretilebilir biçimde (R Markdown, Jupyter Notebook) hazırlayın.</li>
  <li>Hazır olduğunuzda çalışmanızı ön kaydedin — bu hem güvenilirliği artırır hem de CV değeri taşır.</li>
</ol>

<h2>Sonuç: Şeffaflık Rekabet Avantajıdır</h2>
<p>Açık bilim pratiklerini benimseyen araştırmacılar, atıf alma oranı, uluslararası işbirliği ve araştırma etkisi açısından geleneksel araştırmalara kıyasla avantaj sağladığını gösteren kanıtlar artmaktadır. Tüm verinizi paylaşmak zorunda değilsiniz — gizlilik gerektiren klinik veriler buna dahil edilmez; ancak paylaşılabilir her bileşeni açık tutmak hem bilime hem de akademik itibarınıza yatırımdır.</p>
""",

    'cronbach-alpha-0-6-cikti-ne-yapmaliyim': """
<h2>α = .60 ile Ne Yapılır?</h2>
<p>Cronbach alfa değerinin .60 çıkması birçok araştırmacıyı paniğe sürükler; oysa doğru eylem bir madde analizinden geçer. Bu değer George ve Mallery (2003) sınıflandırmasında "sorgulanabilir" (questionable) kategorisindedir — kötü değil, ama güçlendirilebilir demektir.</p>

<h2>Madde Analizi Adım Adım</h2>
<p>SPSS'te Analyze → Scale → Reliability Analysis menüsüne girin, tüm maddeleri seçin ve "Statistics" düğmesinden "Item" ve "Scale if item deleted" seçeneklerini aktif edin. Elde edilen tabloda iki sütuna odaklanın:</p>
<ul>
  <li><strong>Corrected Item-Total Correlation:</strong> .30'un altındaki her madde ölçekle düşük uyum içindedir. Bu maddeler için madde ifadesini, ölçüm dilini (ters madde mi?) ve veri girişini kontrol edin.</li>
  <li><strong>Cronbach's Alpha if Item Deleted:</strong> Mevcut alfa değerinizden yüksek bir değer gösteren madde, ölçeği zayıflatan bir unsurdur. Teorik gerekçe de yoksa bu maddeyi çıkarmayı değerlendirin.</li>
</ul>

<h2>Kaç Madde Silinebilir?</h2>
<p>Bu sorunun kesin bir yanıtı yoktur; ancak pratikte şu kural benimsenebilir: Alt boyutunuzda beş veya daha fazla madde kalıyorsa sorunlu maddeleri çıkarabilirsiniz. Çıkarma sonrası α ≥ .70'e ulaşılıyorsa bu işlemi yöntem bölümünde şeffaflıkla açıklayın ve gerekçelendirin.</p>

<h2>Ölçeğin Orijinal Formu Kullanılıyorsa</h2>
<p>Mevcut, standart bir ölçek kullanıyorsanız madde çıkarmak yapı geçerliliğini bozar ve karşılaştırılabilirliği engeller. Bu durumda ölçeği olduğu gibi kullanıp düşük alfa değerini bir kısıt olarak raporlayın; güvenilirlik sorununun muhtemel kaynağı olarak (a) örneklemin homojenliği, (b) ölçeğin kültürel uyumu veya (c) belirli alt gruba özgü anlam kayması gibi gerekçeleri tartışın.</p>

<h2>Omega (ω) Katsayısı Alternatif mi?</h2>
<p>McDonald'ın omega katsayısı, Cronbach alfanın bazı kısıtlamalarını (özellikle tau-equivalence varsayımı) aşar ve daha doğru güvenilirlik kestirimi sağlar. R'da <code>psych</code> paketiyle kolayca hesaplanır. Bazı dergiler artık omega değerini de talep etmektedir; danışmanınıza bildirin.</p>

<h2>Sonuç</h2>
<p>α = .60, araştırmanın bitmesi değil; güvenilirlik analizinin başlaması gerektiğini gösteren bir sinyaldir. Sistematik madde analizi, gerekçeli silme veya güçlendirme, ve dürüst raporlama ile α değerini metodolojik bir zafiyet olmaktan çıkarıp olgunluk göstergesine dönüştürebilirsiniz.</p>
""",

    'shapiro-wilk-p-0-049-normal-dagitim-var-mi-yok-mu': """
<h2>p = .049 Ne Demektir?</h2>
<p>Shapiro-Wilk testi H₀: "dağılım normal" hipotezini sınar. p = .049, eğer dağılım gerçekten normal olsaydı bu test istatistiğini veya daha aşırısını gözlemleme olasılığının %4.9 olduğu anlamına gelir. α = .05 eşiğinde H₀ reddedilir — teknik olarak "normallik yok" kararı verilir. Ancak bu karar pratik açıdan ne kadar anlamlı?</p>

<h2>Örneklem Büyüklüğü Karar Değiştirir</h2>
<p>Shapiro-Wilk testi örneklem büyüdükçe giderek hassaslaşır. n = 30'da tespit edemeyeceği bir sapmaları n = 200'de kolaylıkla anlamlı bulur. Bu yüzden p = .049 bulgusu örneklem büyüklüğüne göre çok farklı yorumlanır:</p>
<ul>
  <li><strong>n &lt; 50:</strong> Test zaten düşük güçtedir, .049 gerçek sapmanın işareti olabilir — grafikleri inceleyin.</li>
  <li><strong>n = 50–150:</strong> p = .049 borderline'dır; çarpıklık/basıklık değerleri ve Q-Q plot belirleyici olur.</li>
  <li><strong>n &gt; 150:</strong> p = .049 büyük ihtimalle pratikte önemsiz küçük bir sapma; parametrik testler sağlamdır.</li>
</ul>

<h2>Ne Yapılmalı: Karar Akışı</h2>
<ol>
  <li>Çarpıklık ve basıklık değerlerini kontrol edin: |çarpıklık| &lt; 1 ve |basıklık| &lt; 3 ise normal dışılık pratikte çok hafif demektir.</li>
  <li>Q-Q Plot'a bakın: Noktalar referans çizgisinden sistematik olarak sapıyor mu, yoksa uçlarda mı?</li>
  <li>Aykırı değer var mı? Boxplot ile kontrol edin; bir-iki aykırı değer tüm testi etkileyebilir.</li>
  <li>Örneklem boyutunuzu göz önünde bulundurun: n ≥ 30 ve sapma hafif ise Merkezi Limit Teoremi gereği parametrik testler geçerlidir.</li>
  <li>Her iki durumda da (parametrik kaldıysanız da, non-parametriğe geçtiyseniz de) kararınızı tezde gerekçelendirin.</li>
</ol>

<h2>Her İki Analizi Raporlamak</h2>
<p>Belirsizlik yüksekse hem parametrik hem non-parametrik analizi çalıştırıp sonuçların tutarlılığını raporlayabilirsiniz: <em>"Shapiro-Wilk testi sınır değerde anlamlılık göstermesi nedeniyle (p = .049) hem bağımsız örneklem t-testi hem de Mann-Whitney U testi uygulanmış; her iki analiz de benzer sonuçlar vermiştir (p &lt; .01)."</em> Bu yaklaşım bulgularınızın sağlamlığını pekiştirir.</p>

<h2>Sonuç</h2>
<p>p = .049, "normallik kesinlikle yok" veya "her şey yolunda" demek değildir. Grafiksel yöntemler, çarpıklık/basıklık istatistikleri ve örneklem büyüklüğü birlikte değerlendirildiğinde bu borderline değerin pratik önemi netleşir. İstatistiksel karar ile pratik karar her zaman örtüşmez; araştırmacı ikisi arasındaki bu ayrımı anlayıp tezinde açıklayan kişidir.</p>
""",

    'regresyon-analizi-tez-bulgular-bolumune-nasil-aktarilir': """
<h2>Temel Raporlama Tablosu</h2>
<p>Doğrusal regresyon bulgularını APA standardında bir tablo ile sunmak hem okunabilirliği artırır hem de jüri beklentilerini karşılar. Tabloda yer alması gereken sütunlar: Değişken, B (standardize edilmemiş katsayı), SE B (standart hata), β (standardize edilmiş katsayı), t ve p.</p>
<table class="ax-table">
  <thead>
    <tr><th>Değişken</th><th>B</th><th>SE B</th><th>β</th><th>t</th><th>p</th></tr>
  </thead>
  <tbody>
    <tr><td>Sabit</td><td>12.34</td><td>3.21</td><td>—</td><td>3.84</td><td>&lt; .001</td></tr>
    <tr><td>Yaş</td><td>0.45</td><td>0.12</td><td>.31</td><td>3.75</td><td>&lt; .001</td></tr>
    <tr><td>Eğitim düzeyi</td><td>1.82</td><td>0.54</td><td>.24</td><td>3.37</td><td>.001</td></tr>
    <tr><td>Deneyim (yıl)</td><td>0.23</td><td>0.19</td><td>.09</td><td>1.21</td><td>.228</td></tr>
  </tbody>
</table>
<p>Tablo altına not ekleyin: <em>Not. R² = .41, Düzeltilmiş R² = .39, F(3, 196) = 45.3, p &lt; .001.</em></p>

<h2>Metin İçi Raporlama</h2>
<p>Tabloyu anlatan metin kısa ama tam olmalıdır: <em>"Model istatistiksel olarak anlamlıdır, F(3, 196) = 45.3, p &lt; .001, ve varyansın %41'ini (düzeltilmiş R² = .39) açıklamaktadır. Yaş (β = .31, p &lt; .001) ve eğitim düzeyi (β = .24, p = .001) bağımlı değişkeni anlamlı biçimde yordamaktadır. Deneyim yılının yordayıcı etkisi anlamlı değildir (β = .09, p = .228)."</em></p>

<h2>Varsayım Kontrolleri</h2>
<p>Bulgular bölümü veya yöntem bölümü sonunda varsayım kontrolleri raporlanmalıdır:</p>
<ul>
  <li><strong>Çoklu doğrusal bağlantı:</strong> Tüm VIF değerleri &lt; 10, Tolerance &gt; .10.</li>
  <li><strong>Otokorelasyon:</strong> Durbin-Watson = 1.94 (1.5–2.5 aralığında kabul edilebilir).</li>
  <li><strong>Normallik (artıklar):</strong> Standardize artıkların histogramı ve P-P plot normal dağılıma yakındır.</li>
  <li><strong>Eşit varyans (homoscedasticity):</strong> Artık-yordanan değer saçılma grafiği rastgele dağılım göstermektedir.</li>
</ul>

<h2>Logistik Regresyon Farkı</h2>
<p>Lojistik regresyonda B yerine Exp(B) = Odds Ratio raporlanır; R² yerine Nagelkerke R² veya Cox-Snell R² kullanılır. Model uyumu için Hosmer-Lemeshow testi de tabloya eklenebilir. Bu tablo yapısını danışmanınızla ve hedef derginizin yazım kılavuzuyla karşılaştırın.</p>

<h2>Sonuç</h2>
<p>Regresyon analizi en bilgilendirici istatistiksel araçlardan biridir; ancak raporlanması en çok hata yapılan alanlardan biridir. B, SE, β, t ve p değerlerini ayrı sütunlarda tabloya yansıtmak, varsayım ihlallerini dürüstçe belgelemek ve yorumu metin içinde desteklemek — bu üç unsur bir araya geldiğinde bulgular bölümünüz hem metodolojik hem de akademik açıdan eksiksiz olacaktır.</p>
""",

    'analizus-veri-kazima-yok-tez-tr-dizin-openalex': """
<h2>Analizus Neden Veri Kazımıyor?</h2>
<p>Analizus, TR Dizin ve OpenAlex gibi veri kaynaklarına web scraping (veri kazıma) ile değil, resmi API'ler ve veri paylaşım anlaşmaları aracılığıyla erişim sağlar. Bu tercih yalnızca teknik değil, etik ve hukuki bir karardır: veri kazıma platform hizmet koşullarını ihlal edebilir, kaynak veritabanının performansını olumsuz etkiler ve veri doğruluğu konusunda güvensizlik yaratır.</p>

<h2>TR Dizin Verisi Nasıl Kullanılıyor?</h2>
<p>TR Dizin, Türkiye'nin ulusal akademik atıf ve dizin veritabanıdır. Analizus'ta TR Dizin verisine erişim, TÜBİTAK ULAKBİM ile kurumsal işbirliği protokolü çerçevesinde yürütülür. Bu yapı şu avantajları sağlar:</p>
<ul>
  <li>Verinin güvenilirlik ve güncelleme döngüsü kaynak kurumun kontrolündedir.</li>
  <li>Yazara ait meta veri (isim, kurum, ORCID) olabildiğince doğru yansıtılır.</li>
  <li>Olası yanlışlıklar Analizus'a değil, kaynağa atfedilerek düzeltilebilir.</li>
</ul>

<h2>OpenAlex: Açık Kaynak Bibliyometri</h2>
<p>OpenAlex, Microsoft Academic Graph'ın kapanmasının ardından Our Research tarafından geliştirilen açık erişimli bir akademik veri kaynağıdır. 250 milyonun üzerinde çalışma, yazar ve kurum kaydı içeren bu kaynak tamamen açık erişimlidir ve kısıtlama olmaksızın API erişimi sunar. Analizus, uluslararası yayın ve atıf verilerini OpenAlex API üzerinden çeker; bu veri Türkiye'nin global akademik konumunu izlemek ve araştırmacıların uluslararası görünürlüğünü değerlendirmek için kullanılır.</p>

<h2>Araştırmacı için Ne Anlam İfade Eder?</h2>
<p>Analizus'ta görünen verinin kaynağı her zaman etiketlenir: TR Dizin mi, OpenAlex mı, kullanıcı tarafından girilen mi? Bu şeffaflık, araştırmacının elindeki sayının nereden geldiğini bilmesini ve buna göre yorumlamasını sağlar. Bir atıf sayısı düşük görünüyorsa kaynak, veri sağlayıcısının güncelliğiyle ilgili olabilir; bu bağlamda Analizus destek ekibine bildirim yapılabilir.</p>

<h2>Tez İçin Analizus Verisi Kullanmak</h2>
<p>Analizus'tan alınan istatistikler tezde kaynak olarak gösterilirken şu biçim önerilir: <em>Analizus. (2026). [Araştırmacı/kurum adı] bibliyometrik analizi [veri seti]. https://analizus.com</em> OpenAlex verisi için doğrudan kaynak göstermek istenirse: <em>Priem, J., Piwowar, H., &amp; Orr, R. (2022). OpenAlex: A fully-open index of the world's research output. arXiv. https://doi.org/10.48550/arXiv.2205.01833</em></p>

<h2>Sonuç</h2>
<p>Veri bütünlüğü, Analizus'un tasarım önceliğidir. Kazıma yerine resmi kanallar kullanmak kısa vadede ek operasyonel yük getirse de uzun vadede verinin doğruluğunu ve platformun güvenilirliğini garanti eder. Araştırmacılar bu veri altyapısından yararlanırken kaynağın her zaman TR Dizin veya OpenAlex gibi denetlenebilir bir noktaya izlenebileceğini bilmelidir.</p>
""",
}


def expand_batch3(apps, schema_editor):
    import re
    BlogPost = apps.get_model('forum', 'BlogPost')
    ok = fail = 0
    for slug, appendix in APPENDIXES.items():
        try:
            post = BlogPost.objects.get(slug=slug)
        except BlogPost.DoesNotExist:
            print(f'  UYARI: {slug[:55]} bulunamadı')
            continue
        content = post.content
        hr_pos = content.rfind('<hr>')
        post.content = (content[:hr_pos] + appendix + content[hr_pos:]) if hr_pos != -1 else content + appendix
        post.save()
        text = re.sub(r'<[^>]+>', ' ', post.content)
        wc = len(text.split())
        s = '✓' if wc >= 800 else '✗'
        if wc >= 800:
            ok += 1
        else:
            fail += 1
        print(f'  {s} {wc:4d} | {slug[:55]}')
    print(f'\n  Başarılı: {ok} | Eksik: {fail}')


class Migration(migrations.Migration):
    dependencies = [('forum', '0137_finalize_last4')]
    operations = [migrations.RunPython(expand_batch3, migrations.RunPython.noop)]
