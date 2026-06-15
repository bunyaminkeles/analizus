from django.db import migrations

# Her APPENDIX_* değişkeni, ilgili yazının <hr> etiketinden
# ÖNCE eklenecek yeni HTML bölümlerini içerir.

APPENDIX_19 = """
<h2>ANOVA'nın Üç Temel Varsayımı</h2>
<p>ANOVA uygulamadan önce üç varsayımı kontrol etmek zorunludur; bu varsayımlar sağlanmadan yapılan analiz güvenilmez sonuç üretir.</p>
<ol>
  <li><strong>Normallik:</strong> Her grubun bağımlı değişkeni normal dağılmalıdır. Shapiro-Wilk testi (N &lt; 50) veya Kolmogorov-Smirnov testi (N ≥ 50) kullanılır. p &gt; .05 normalliğin karşılandığını gösterir. Küçük sapmalarda ANOVA dayanıklıdır (robust), ancak ciddi çarpıklık varsa Kruskal-Wallis tercih edilmelidir.</li>
  <li><strong>Varyans Homojenliği:</strong> Tüm grupların varyansları birbirine eşit olmalıdır. SPSS çıktısındaki Levene's Test of Equality of Error Variances satırında p &gt; .05 ise homojenlik sağlanmıştır. p ≤ .05 ise Welch ANOVA kullanılır ve tezde "varyansların homojenliği sağlanmadığından Welch düzeltmesi uygulanmıştır" şeklinde belirtilir.</li>
  <li><strong>Bağımsızlık:</strong> Gözlemler birbirinden bağımsız olmalıdır. Aynı katılımcıdan birden fazla ölçüm alındıysa Tekrarlı Ölçüm ANOVA'ya geçilmelidir. Bu varsayım araştırma tasarımıyla güvence altına alınır; istatistiksel test gerektirmez.</li>
</ol>

<h2>Mann-Whitney U: Gerçekte Ne Ölçer?</h2>
<p>Mann-Whitney U testi sıklıkla "ortancaların eşitliğini test eder" biçiminde öğretilir; bu tanım pratik açıdan yeterlidir ancak teknik olarak eksiktir. Test, iki grup arasındaki <strong>stokastik üstünlüğü</strong> ölçer: birinci gruptan rastgele seçilen bir bireyin ikinci gruptan rastgele seçilen bir bireyden daha yüksek skor alma olasılığının 0.5'ten anlamlı biçimde farklı olup olmadığını sorgular.</p>
<p>Pratik sonucu şudur: iki grubun ortancası eşit olsa bile dağılım şekilleri farklıysa test anlamlı çıkabilir. Bu nedenle tezde "gruplar arasındaki fark ortanca puanlar temelinde değerlendirilmiştir" ifadesini kullanmak hem doğru hem de danışmanları ikna edici bulduğu bir ifadedir.</p>

<h2>SPSS'te Adım Adım Uygulama</h2>
<p><strong>Tek Yönlü ANOVA için:</strong> Analyze → Compare Means → One-Way ANOVA → bağımlı değişkeni <em>Dependent List</em>'e, grup değişkenini <em>Factor</em>'a ekleyin → Options: Descriptive ve Homogeneity of variance test seçeneklerini işaretleyin → Post Hoc: Tukey HSD veya Bonferroni seçin → OK.</p>
<p><strong>Mann-Whitney U için:</strong> Analyze → Nonparametric Tests → Legacy Dialogs → 2 Independent Samples → test değişkenini <em>Test Variable List</em>'e, gruplandırma değişkenini <em>Grouping Variable</em>'a ekleyin → Mann-Whitney U kutusunu işaretleyip <em>Define Groups</em>'ta 1 ve 2 değerlerini tanımlayın → OK.</p>

<h2>Etki Büyüklüğü: Hangi Değeri Raporlamalısınız?</h2>
<p>APA 7. baskı standardı yalnızca p değerini raporlamayı yeterli görmez; etki büyüklüğü zorunludur:</p>
<table>
  <thead><tr><th>Test</th><th>Etki Büyüklüğü</th><th>Küçük</th><th>Orta</th><th>Büyük</th></tr></thead>
  <tbody>
    <tr><td>ANOVA</td><td>η² (eta kare)</td><td>.01</td><td>.06</td><td>.14</td></tr>
    <tr><td>Mann-Whitney U</td><td>r (rank-biserial)</td><td>.10</td><td>.30</td><td>.50</td></tr>
  </tbody>
</table>
<p>Rank-biserial r değeri şu formülle hesaplanır: <em>r = 1 − (2U / n₁n₂)</em>. SPSS bu değeri otomatik vermez; <a href="/istatistik/mann-whitney/">Analizus Mann-Whitney aracı</a> etki büyüklüğünü otomatik hesaplar.</p>

<h2>Sık Yapılan 3 Hata</h2>
<ol>
  <li><strong>"2 grup → ANOVA" hatası:</strong> 2 gruplu karşılaştırmada ANOVA değil t-testi (parametrik) veya Mann-Whitney U (non-parametrik) kullanılmalıdır. ANOVA teknik olarak 2 grupta da çalışır ancak gereksizdir ve F = t² ilişkisi nedeniyle aynı sonucu verir.</li>
  <li><strong>"Normallik sağlanmadı → Mann-Whitney" hatası:</strong> 3+ grup ve normallik sağlanmamışsa Mann-Whitney U değil Kruskal-Wallis H testi yapılmalıdır. Mann-Whitney U yalnızca 2 grup için tasarlanmıştır.</li>
  <li><strong>Etki büyüklüğünü raporlamamak:</strong> F(2, 117) = 4.23, p = .017 yazmak yeterli değildir; η² = .068 eklenmesi zorunludur.</li>
</ol>
"""

APPENDIX_22 = """
<h2>Tolerance Değeri: VIF'in İkizi</h2>
<p>SPSS çıktısında VIF'in yanında Tolerance (Tolerans) değeri de görüntülenir. İkisi aynı bilgiyi farklı ölçekte verir: <em>Tolerance = 1 / VIF</em>. Tolerans değeri 0.10'un altına düştüğünde (yani VIF 10'u geçtiğinde) ciddi multicollinearity vardır. Bazı kaynaklar daha muhafazakâr bir eşik olan Tolerance &lt; 0.20 (VIF &gt; 5) uyarısını kullanır. Tezinizde her iki değeri de raporlamanız önerilir: <em>"VIF değerleri 1.12 ile 3.45 arasında, tolerans değerleri 0.29 ile 0.89 arasında seyretmiştir."</em></p>

<h2>Condition Index ile İleri Kontrol</h2>
<p>VIF ve Tolerance genel bir uyarı sistemi sunar; daha hassas teşhis için Condition Index kullanılabilir. SPSS'te Collinearity Diagnostics tablosunda yer alan Condition Index değeri 30'u aştığında ciddi multicollinearity, 15–30 arasında ise orta düzey sorun işareti olarak yorumlanır. Tez düzeyindeki çalışmalarda VIF kontrolü genellikle yeterlidir; Condition Index raporlaması doktora tezleri ve makale revizyonlarında daha çok istenir.</p>

<h2>SPSS'te Multicollinearity Kontrolü: Adım Adım</h2>
<p>Regresyon analizinizde VIF değerlerini görmek için şu adımları izleyin:</p>
<ol>
  <li>Analyze → Regression → Linear seçin.</li>
  <li>Bağımlı değişkeni <em>Dependent</em> kutusuna, bağımsız değişkenleri <em>Independent(s)</em> kutusuna ekleyin.</li>
  <li><em>Statistics</em> düğmesine tıklayın → <em>Collinearity diagnostics</em> kutusunu işaretleyin → Continue.</li>
  <li>OK'a basın. Çıktıda <em>Coefficients</em> tablosunun sağ bölümünde Tolerance ve VIF sütunlarını göreceksiniz.</li>
</ol>
<p>Eğer VIF değerlerinden biri 10'u aşıyorsa önce değişkenler arasındaki korelasyon matrisini inceleyin (Analyze → Correlate → Bivariate). Korelasyonu r &gt; .80 olan çiftler genellikle multicollinearity kaynağıdır.</p>

<h2>Multicollinearity'nin Gerçek Kaynakları</h2>
<p>Sorunun neden ortaya çıktığını anlamak, doğru çözümü seçmeyi kolaylaştırır:</p>
<ul>
  <li><strong>Aynı yapıyı ölçen iki ölçek:</strong> Duygusal tükenmişlik ve genel tükenmişlik puanları gibi kavramsal örtüşme varsa iki değişkeni birlikte modele almak VIF'i şişirir.</li>
  <li><strong>Türetilmiş değişken:</strong> Bir değişken diğerinin karesi veya çarpımı olduğunda doğal multicollinearity ortaya çıkar. Etkileşim terimleri içeren modellerde değişkenleri ortalamadan sapma (mean-centering) yöntemiyle dönüştürmek bu sorunu azaltır.</li>
  <li><strong>Küçük örneklem:</strong> Az sayıda gözlemle çok sayıda bağımsız değişken kullanıldığında VIF değerleri yapay biçimde yükselebilir. Kural olarak her bağımsız değişken için en az 10–15 gözlem önerilir.</li>
</ul>

<h2>Sık Yapılan Hatalar</h2>
<ol>
  <li><strong>VIF &gt; 10 kuralını mutlak saymak:</strong> Alan yazınında VIF için 5, 10 ve hatta 30 gibi farklı eşikler kullanılmaktadır. Danışmanınızın benimsediği eşiği ve kullandığınız alandaki standarttı belirtin.</li>
  <li><strong>Sorunu tezde gizlemek:</strong> Yüksek VIF bulduğunuzda bunu belirtmemek yöntemsel bir eksiklik sayılır. Sorunu ve aldığınız önlemi açıkça yazın.</li>
  <li><strong>Tüm değişkenleri silmek:</strong> Yüksek VIF'li tüm değişkenleri modelden çıkarmak teorik geçerliği zedeler. Önce teorik önem değerlendirmesi yapın, ardından istatistiksel karar verin.</li>
</ol>
"""

APPENDIX_26 = """
<h2>SPSS Çıktısını Adım Adım Okumak</h2>
<p>SPSS'te One-Way ANOVA çalıştırdığınızda iki temel tablo gelir. <em>Descriptives</em> tablosunda her grubun N, ortalama (Mean) ve standart sapması (Std. Deviation) yer alır; bunları teze aktarırken M ve SD sembollerini kullanın. <em>ANOVA</em> tablosunda ise Between Groups satırındaki F değerini ve Sig. sütunundaki p değerini okursunuz. Sig. &lt; .05 ise gruplar arasında anlamlı fark vardır. <em>Post Hoc Tests</em> tablosunda hangi grup çiftinin anlamlı farklılaştığını <em>Mean Difference</em> ve <em>Sig.</em> sütunundan okursunuz.</p>

<h2>Omega Kare (ω²): Eta Kareden Neden Daha İyi?</h2>
<p>Eta kare (η²) hesaplanması kolay ama yanlı bir tahmin sunar; özellikle küçük örneklemlerde etki büyüklüğünü olduğundan büyük gösterir. Omega kare (ω²), bu yanlılığı düzelten daha muhafazakâr bir katsayıdır. Hesabı:</p>
<p><em>ω² = (SS_arasında − df_arasında × MS_içinde) / (SS_toplam + MS_içinde)</em></p>
<p>Yayın sürecinde hakemler giderek artan sıklıkla ω² istemektedir. Tezinizde her ikisini birlikte raporlamak en güvenli yaklaşımdır: <em>"η² = .126, ω² = .112"</em>. Yorumlama eşikleri η² ile aynıdır: .01 küçük, .06 orta, .14 büyük etki.</p>

<h2>Tukey HSD ile Bonferroni Arasındaki Fark</h2>
<p>ANOVA anlamlı çıktıktan sonra hangi grupların farklılaştığını bulmak için post-hoc test seçimi yapılır:</p>
<table>
  <thead><tr><th>Test</th><th>Ne Zaman Kullanılır?</th><th>Avantaj</th><th>Dezavantaj</th></tr></thead>
  <tbody>
    <tr><td>Tukey HSD</td><td>Grup büyüklükleri eşit veya yakın, varyanslar homojen</td><td>Güçlü, Tip I hatayı iyi kontrol eder</td><td>Varyans homojenliği gerektirir</td></tr>
    <tr><td>Bonferroni</td><td>Az sayıda karşılaştırma veya varyanslar heterojen</td><td>Çok yönlü, esnek</td><td>Çok sayıda karşılaştırmada aşırı muhafazakâr</td></tr>
    <tr><td>Games-Howell</td><td>Varyanslar homojen değil (Levene p ≤ .05)</td><td>Homojenlik gerektirmez</td><td>SPSS'te ayrı menü</td></tr>
  </tbody>
</table>
<p>Sosyal bilim tezlerinde Tukey HSD en yaygın tercih olmakla birlikte danışmanınızın yönlendirmesi belirleyicidir. Varyanslar homojen değilse Games-Howell'ı tercih etmek metodolojik açıdan daha savunulabilirdir.</p>

<h2>Tablo Word'e Nasıl Aktarılır?</h2>
<p>SPSS çıktısındaki tabloyu Word'e aktarmanın en temiz yolu: SPSS çıktı penceresinde tabloya çift tıklayın → tabloyu seçin → sağ tık → Copy Special → Word Format seçin → Word'e yapıştırın. Bu yöntemle yazı tipi ve sütun genişlikleri korunur. Alternatif olarak tabloyu sıfırdan Word'de oluşturmak APA biçiminin tam karşılanmasını sağlar; SPSS çıktısını doğrudan kopyalamak genellikle biçimlendirme düzeltmesi gerektirir.</p>
"""

APPENDIX_27 = """
<h2>Bağımlı (Eşleştirilmiş) t-Testi Tablosu</h2>
<p>Aynı katılımcıdan ön-test ve son-test ölçümü aldıysanız bağımlı örneklem t-testi kullanırsınız. Tablo formatı bağımsız t-testinden farklıdır: tek grup üzerinde fark puanı raporlanır.</p>
<table>
  <thead><tr><th></th><th>M</th><th>SD</th><th>t</th><th>df</th><th>p</th><th>d</th></tr></thead>
  <tbody>
    <tr><td>Ön-test – Son-test Farkı</td><td>−8.4</td><td>6.1</td><td>−5.82</td><td>53</td><td>&lt;.001</td><td>0.79</td></tr>
  </tbody>
</table>
<p>Metin içi raporlama: <em>"Ön-test (M = 61.2, SD = 9.8) ve son-test (M = 69.6, SD = 8.3) puanları arasındaki fark istatistiksel olarak anlamlı bulunmuştur, t(53) = −5.82, p &lt; .001, d = 0.79. Etki büyüklüğü büyük düzeyde yorumlanmıştır (Cohen, 1988)."</em></p>

<h2>Cohen's d Nasıl Manuel Hesaplanır?</h2>
<p>SPSS bağımsız t-testi için Cohen's d değerini otomatik vermez. İki yöntemle hesaplayabilirsiniz:</p>
<p><strong>Yöntem 1 — Havuzlanmış SD:</strong> d = (M₁ − M₂) / SD_havuzlu</p>
<p>SD_havuzlu = √[(SD₁² + SD₂²) / 2]</p>
<p>Örnek: M₁ = 68.4, M₂ = 61.2, SD₁ = 9.2, SD₂ = 10.1 ise SD_havuzlu = √[(84.64 + 102.01) / 2] = √93.33 = 9.66; d = 7.2 / 9.66 = 0.75.</p>
<p><strong>Yöntem 2 — t değerinden:</strong> d = 2t / √df. Bu yöntem t ve df değerleri bilindiğinde hızlı hesaplama sağlar.</p>
<p>Cohen (1988) sınıflandırması: d = 0.20 küçük, d = 0.50 orta, d = 0.80 büyük etki.</p>

<h2>p Değerini Doğru Raporlama: Nüanslar</h2>
<p>APA 7. baskıda p değerini raporlarken dikkat edilmesi gereken kurallar:</p>
<ul>
  <li>p &lt; .001 eşiğinin altındaki değerler için "p &lt; .001" yazın; "p = .000" yazmayın (SPSS bunu gösterse de istatistiksel olarak imkânsızdır).</li>
  <li>p ≥ .001 olan değerleri üç ondalık basamakla tam olarak yazın: p = .023, p = .187.</li>
  <li>"p değeri anlamlı çıktı" yerine "istatistiksel olarak anlamlı fark bulunmuştur, p = .023" ifadesini kullanın.</li>
  <li>p önünde sıfır yazılmaz: ".023" değil "0.023"; APA standardı "p = .023" biçimindedir.</li>
</ul>

<h2>Sık Yapılan 4 Tablo Hatası</h2>
<ol>
  <li><strong>Levene testini atlama:</strong> SPSS iki satır halinde sonuç verir. Hangi satırı kullanacağınızı Levene testi belirlediğinden bu adımı raporlamak zorunludur.</li>
  <li><strong>Cohen's d yazmamak:</strong> Etki büyüklüğü olmayan t-testi tablosu APA 7 standardını karşılamaz.</li>
  <li><strong>Tabloyu hem metin içinde hem tabloda aynen tekrarlamak:</strong> Tablo sunulan değerleri metinde yeniden yazmayın; yalnızca yorumu ve sonucu ekleyin.</li>
  <li><strong>Tablo başlığını tablonun altına yazmak:</strong> APA formatında tablo başlıkları tablonun <em>üstünde</em>, italik ve numaralı olmalıdır.</li>
</ol>
"""

APPENDIX_28 = """
<h2>SPSS Çıktısından Güvenilirlik Değerlerini Okumak</h2>
<p>SPSS'te Analyze → Scale → Reliability Analysis yolunu izleyin, ölçek maddelerini <em>Items</em> kutusuna ekleyin, Model olarak Alpha seçin, ardından <em>Statistics</em>'te <em>Item</em>, <em>Scale</em> ve <em>Scale if item deleted</em> seçeneklerini işaretleyin. Çıktıda üç tablo gelir:</p>
<ul>
  <li><strong>Reliability Statistics:</strong> Genel Cronbach Alpha değeri ve madde sayısı burada yer alır.</li>
  <li><strong>Item-Total Statistics:</strong> Her maddenin madde-toplam korelasyonu (<em>Corrected Item-Total Correlation</em>) ve o madde silinirse alpha'nın ne olacağı (<em>Cronbach's Alpha if Item Deleted</em>) gösterilir.</li>
  <li><strong>Scale Statistics:</strong> Toplam ölçek ortalaması ve standart sapması yer alır.</li>
</ul>

<h2>Madde-Toplam Korelasyonu: Karar Kriteri</h2>
<p>Item-Total Statistics tablosundaki <em>Corrected Item-Total Correlation</em> sütunu, her maddenin ölçeğin geneliyle ne ölçüde uyumlu olduğunu gösterir. Genel kabul gören eşik değer r ≥ .30'dur. Bu değerin altında kalan maddeler ölçek bütünüyle tutarsız davranmaktadır ve çıkarılması düşünülmelidir.</p>
<p>Madde çıkarma kararını yalnızca düşük korelasyona dayandırmayın; maddenin teorik önemi de değerlendirilmelidir. Teorik olarak vazgeçilmez bir madde düşük korelasyon gösteriyorsa bunu tezde şeffaflıkla belirtip maddeyi koruyabilirsiniz.</p>

<h2>Hangi Madde Çıkarılır? İki Kural</h2>
<ol>
  <li><strong>Corrected Item-Total Correlation &lt; .30</strong> ise madde ölçekle yeterince uyuşmuyordur.</li>
  <li><strong>Cronbach's Alpha if Item Deleted</strong> değeri mevcut alpha'dan belirgin biçimde yüksekse (örneğin .70'ten .78'e yükseltiyorsa) maddenin çıkarılması gerekir.</li>
</ol>
<p>Her iki koşulun bir arada bulunması çıkarma kararını güçlendirir. Sadece birinin bulunması durumunda danışmanınızla görüşmeniz önerilir.</p>

<h2>Cronbach Alpha Düşükse Ne Yapılır?</h2>
<p>α &lt; .60 çıktığında panik yapmadan önce şu adımları deneyin:</p>
<ol>
  <li>Düşük madde-toplam korelasyonlu maddeleri çıkarın ve alpha değerinin değişimini izleyin.</li>
  <li>Ters kodlanması gereken maddelerin kodlanıp kodlanmadığını kontrol edin (Transform → Recode into Different Variables).</li>
  <li>Ölçeğin alt boyutlara ayrılıp ayrılmadığını değerlendirin; genel alpha düşük olsa da alt boyutların her birinin ayrı alpha değeri yeterli olabilir.</li>
  <li>Örneklemin ölçeğin geliştirildiği popülasyonla uyumlu olup olmadığını sorgulayın; kültürel uyumsuzluk alpha düşüklüğünün başlıca nedenlerinden biridir.</li>
</ol>

<h2>McDonald's Omega: Modern Alternatif</h2>
<p>Cronbach Alpha, tüm maddelerin ölçeği eşit ölçüde temsil ettiğini varsayar (tau-equivalence); bu varsayım çoğu ölçekte karşılanmaz. McDonald's Omega (ω), bu kısıtlamayı aşan ve son yıllarda methodoloji yazınında güçlü destek bulan bir güvenilirlik katsayısıdır. JASP ve R'ın <em>psych</em> paketi omega değerini hesaplar. Teziniz yayın sürecine girecekse veya doktora düzeyindeyse omega değerini ek gösterge olarak raporlamanız önerilir.</p>
"""

APPENDIX_31 = """
<h2>"Likert Maddesi" ile "Likert Ölçeği" Arasındaki Kritik Fark</h2>
<p>Rensis Likert'in özgün katkısı tek madde değil, birden fazla maddenin toplamından oluşan <em>ölçektir</em>. Tek bir "1–5 arası değerlendirin" sorusu Likert maddesidir; beş veya daha fazla böyle maddenin güvenilirliği kanıtlanmış toplamı ise Likert ölçeğidir. Bu ayrım test seçimini doğrudan etkiler: tek madde için non-parametrik testler önerilirken çok maddelik ve güvenilirliği yüksek ölçekler için parametrik testler kullanılabilir. Tezinizde tek soru mu, yoksa ölçek mi kullandığınızı açıkça belirtmek danışmanınızın ve jürinin güvenini artırır.</p>

<h2>Skewness ve Kurtosis: Parametrik Test Eşikleri</h2>
<p>Normallik testi (Shapiro-Wilk veya KS) p değeri ≤ .05 çıktığında parametrik testten vazgeçmek her zaman zorunlu değildir. Büyük örneklemlerde (N &gt; 100) bu testler küçük sapmalarda bile anlamlı sonuç verir. Bu durumda çarpıklık (skewness) ve basıklık (kurtosis) değerleri daha güvenilir bir kılavuzdur:</p>
<table>
  <thead><tr><th>Değer</th><th>Kabul Edilebilir Aralık</th><th>Aşıldığında</th></tr></thead>
  <tbody>
    <tr><td>Skewness</td><td>−1.0 ile +1.0</td><td>Non-parametrik test tercih edilmeli</td></tr>
    <tr><td>Kurtosis</td><td>−2.0 ile +2.0</td><td>Non-parametrik test tercih edilmeli</td></tr>
  </tbody>
</table>
<p>Tezde: <em>"Skewness değeri .43, kurtosis değeri −.67 olup dağılımın normal sınırlar içinde kaldığı değerlendirilmiş ve parametrik test tercih edilmiştir."</em></p>

<h2>Faktör Analizi ile İlişki</h2>
<p>Likert maddelerinden oluşan bir ölçeğe test uygulamadan önce faktör yapısını doğrulamak iyi uygulamadır. Açımlayıcı faktör analizi (AFA) veya doğrulayıcı faktör analizi (DFA) ölçeğin kaç boyutlu olduğunu ortaya koyar. Tek boyutlu bir ölçeğin toplam puanını kullanmak makul; çok boyutlu bir ölçeğin tüm maddelerini tek puanda toplamak ise hatalıdır. Bu durumda her alt boyut ayrı analiz edilmelidir.</p>

<h2>Hem Parametrik Hem Non-Parametrik: İkisini Birden Yapmak</h2>
<p>Bazı araştırmacılar sınırda kalan normallik bulgularında hem parametrik hem non-parametrik testin sonuçlarını raporlar. İki yöntem aynı sonucu veriyorsa bulgular güçlü; farklı sonuç veriyorsa non-parametrik sonuca ağırlık verilir ve bu tercih gerekçelendirilir. Bu yaklaşım özellikle keşifsel çalışmalarda ve Likert maddelerinin doğrudan analiz edildiği durumlarda metodolojik şeffaflık sağlar.</p>

<h2>Karar Özeti: Hızlı Referans</h2>
<p>Analiz öncesi kendinize üç soru sorun: (1) Tek madde mi, çok maddelik ölçek mi? (2) Normal dağılım sağlandı mı (skewness ve kurtosis değerlendirmesi dahil)? (3) Cronbach Alpha ≥ .70 mi? Bu üç sorunun yanıtı doğru testi belirler ve tezinizin Yöntem bölümünde bu gerekçeleri açıkça sunmanız jüri güvenini artırır.</p>
"""

APPENDIX_32 = """
<h2>SPSS'te Eksik Veri Analizi: Adım Adım</h2>
<p>Eksik veri oranını ve dağılımını SPSS ile şu şekilde inceleyebilirsiniz:</p>
<ol>
  <li><strong>Frekans analizi:</strong> Analyze → Descriptive Statistics → Frequencies → tüm değişkenleri seçin. Çıktıda her değişken için <em>Missing</em> satırı eksik gözlem sayısını ve yüzdesini verir.</li>
  <li><strong>Missing Value Analysis:</strong> Analyze → Missing Value Analysis → değişkenleri seçin → Descriptives bölümünde <em>Univariate statistics</em> işaretleyin. Bu yol her değişken için daha ayrıntılı eksik veri istatistikleri ve Little's MCAR testini sunar.</li>
  <li><strong>Pattern matrisi:</strong> Missing Value Analysis penceresinde <em>Patterns</em> sekmesini işaretleyin. Hangi gözlemlerin hangi değişkenlerde aynı anda eksik olduğunu gösteren bir görsel matris oluşturulur. Belirli bir katılımcı grubunun sistematik biçimde eksik yanıt verip vermediği bu matris incelenerek anlaşılır.</li>
</ol>

<h2>Little's MCAR Testi Nasıl Yorumlanır?</h2>
<p>Little's MCAR testi, H₀: "Eksik veri tamamen rastgeledir (MCAR)" hipotezini sınar. SPSS Missing Value Analysis çıktısında <em>Little's MCAR test</em> satırındaki Chi-Square ve Sig. değerlerini okursunuz:</p>
<ul>
  <li><strong>p &gt; .05:</strong> H₀ reddedilemez → MCAR varsayımı destekleniyor. Liste silme veya ortalama atama savunulabilir (eksiklik düşükse).</li>
  <li><strong>p ≤ .05:</strong> MCAR reddedildi → MAR veya MNAR olabilir. Çoklu atama (MI) veya FIML önerilir.</li>
</ul>
<p>Tezde: <em>"Little's MCAR testi istatistiksel olarak anlamlı bulunmamıştır (χ²(14) = 18.43, p = .189); bu sonuç eksik verinin tamamen rastgele dağıldığına işaret etmektedir."</em></p>

<h2>Çoklu Atama (Multiple Imputation) Sonrası Raporlama</h2>
<p>SPSS'te Multiple Imputation yolunu şöyle bulursunuz: Analyze → Multiple Imputation → Impute Missing Data Values. Önerilen atama sayısı (imputation count) genellikle 5–20 arasındadır; eksiklik oranı arttıkça bu sayıyı artırmak önerilir.</p>
<p>MI sonrası analizler her imputasyon için ayrı çalıştırılır ve sonuçlar Rubin kurallarıyla birleştirilir. SPSS bunu otomatik yapar; çıktıda <em>Pooled</em> satırı birleşik tahmini verir. Tezde: <em>"Eksik veriler SPSS Multiple Imputation prosedürüyle (m = 5 atama) doldurulmuş; analizler birleştirilmiş (pooled) katsayılar üzerinden raporlanmıştır."</em></p>

<h2>Sık Yapılan Hatalar</h2>
<ol>
  <li><strong>Eksik veri raporlamamak:</strong> Kaç gözlemin eksik olduğu ve bu veriyle nasıl başa çıkıldığı mutlaka Yöntem bölümünde belirtilmelidir.</li>
  <li><strong>Ortalama atamayı varsayılan çözüm olarak kullanmak:</strong> Ortalama atama (mean imputation) varyansı düşürür ve değişkenler arası korelasyonları zayıflatır; yalnızca %5'in altındaki MCAR durumlarında ve tartışmalı biçimde kabul görmektedir.</li>
  <li><strong>Liste silmeyi %20'nin üzerinde uygulamak:</strong> Eksik veri oranı yüksekse liste silme güç kaybına ve olası yanlılığa yol açar; bu durumda MI veya FIML tercih edilmelidir.</li>
</ol>
"""

APPENDIX_33 = """
<h2>Python: İstatistik İçin Üçüncü Bir Yol</h2>
<p>Son yıllarda <strong>Python</strong> sosyal bilimlerde de istatistik aracı olarak yaygınlaşmaktadır. <em>scipy.stats</em> kütüphanesi t-testi, ANOVA, Mann-Whitney U ve Ki-kare gibi temel testleri karşılar; <em>statsmodels</em> regresyon, faktör analizi ve zaman serisi için kapsamlı destek sunar; <em>pingouin</em> ise etki büyüklüğünü ve güç analizini otomatik hesaplar. Python'un avantajı tekrar üretilebilirlik ve veri temizliğini tek platformda yönetme imkânıdır. Dezavantajı ise R'dan da dik bir öğrenme eğrisi gerektirmesidir; tez düzeyinde SPSS veya R yeterliyse Python'a geçmek için güçlü bir neden yoktur.</p>

<h2>Her Program İçin Ücretsiz Öğrenme Kaynakları</h2>
<table>
  <thead><tr><th>Program</th><th>Kaynak</th><th>Format</th></tr></thead>
  <tbody>
    <tr><td>SPSS</td><td>Pallant, J. — SPSS Survival Manual</td><td>Kitap (kütüphaneden)</td></tr>
    <tr><td>SPSS</td><td>SPSS Tutorials (statistics.laerd.com)</td><td>Web, ücretsiz</td></tr>
    <tr><td>R</td><td>R for Data Science (r4ds.hadley.nz)</td><td>Web, ücretsiz</td></tr>
    <tr><td>R</td><td>Learning Statistics with R (Navarro)</td><td>PDF, ücretsiz</td></tr>
    <tr><td>Python</td><td>Pingouin dokümantasyonu (pingouin-stats.org)</td><td>Web, ücretsiz</td></tr>
  </tbody>
</table>

<h2>Danışman Faktörü: Göz Ardı Edilemez Gerçek</h2>
<p>Program seçimini teknik özelliklerden çok danışmanınızın alışkanlığı belirler. Danışmanınız SPSS çıktısına yıllarca bakmışsa R çıktısını "farklı formatlı" bularak güvenilirliğini sorgulaması olasıdır. Danışmanınızın hangi programı kullandığını ilk görüşmede öğrenin. Farklı bir program seçmek istiyorsanız gerekçenizi hazırlayın; "tekrar üretilebilirlik" ve "ücretsiz erişim" genellikle kabul gören gerekçelerdir.</p>

<h2>Karma Yaklaşım: SPSS + R Birlikte</h2>
<p>Pek çok araştırmacı veri temizliği ve temel analizler için SPSS, gelişmiş analizler ve yayın kalitesi görseller için R kullanır. Bu iki programlı yaklaşım çelişki yaratmaz; her analizi hangi programda yaptığınızı Yöntem bölümünde belirtmeniz yeterlidir: <em>"Tanımlayıcı istatistikler ve t-testi SPSS 26.0, yapısal eşitlik modellemesi ise R 4.3.1'deki lavaan paketi ile yürütülmüştür."</em></p>

<h2>Zaman Yatırımı: Hangisi Daha Hızlı Öğrenilir?</h2>
<p>Temel t-testi veya ANOVA yapabilmek için gereken süre tahmini: SPSS'te 1–2 saat (menü arayüzü sayesinde), jamovi veya JASP'ta 2–3 saat, R'da 10–20 saat (syntax öğrenme dahil), Python'da 20–40 saat. Bu süreler programlama geçmişi olmayan öğrenciler içindir. Eğer tezinizin analiz aşamasına bir ay kaldıysa R veya Python'dan başlamak yerine SPSS veya jamovi ile ilerlemek daha sağduyulu bir karardır.</p>
"""

APPENDIX_34 = """
<h2>jamovi ile İlk Analiz: Adım Adım</h2>
<p>jamovi ücretsiz ve açık kaynak; Windows, Mac ve Linux için jamovi.org adresinden indirilebilir. Kurulum yaklaşık 5 dakika sürer, ek bağımlılık gerekmez.</p>
<ol>
  <li>jamovi'yi açın → sol üstteki üç nokta simgesiyle veri dosyanızı (.sav, .csv veya .xlsx) açın.</li>
  <li>Üst menüden <em>T-Tests</em> seçeneğini tıklayın → <em>Independent Samples T-Test</em> seçin.</li>
  <li>Bağımlı değişkeni <em>Dependent Variables</em> kutusuna, grup değişkenini <em>Grouping Variable</em> kutusuna sürükleyin.</li>
  <li>Sağdaki seçeneklerden <em>Effect size</em> (Cohen's d) ve <em>Descriptives</em> kutucuklarını işaretleyin.</li>
  <li>Sonuçlar anında sağ panelde görüntülenir; tablolar Word veya PDF'e aktarılabilir.</li>
</ol>
<p>jamovi'nin en büyük avantajlarından biri, her analizin altında otomatik oluşturulan R kodunu göstermesidir (<em>Syntax mode</em> etkinleştirildiğinde). Bu sayede hem menü kolaylığından hem de tekrar üretilebilirlikten yararlanılır.</p>

<h2>JASP: Bayesyen İstatistik Avantajı</h2>
<p>JASP (jasp-stats.org) açık kaynak ve ücretsiz bir programdır; arayüzü SPSS'e oldukça benzer. Sıradan frekansçı (frequentist) analizlerin yanı sıra Bayesyen alternatiflerini tek tıkla sunar. Örneğin bağımsız t-testi yaparken "Bayesian Independent Samples T-Test" seçeneğiyle Bayes faktörü (BF₁₀) hesaplayabilirsiniz. Sosyal bilimlerde Bayesyen yaklaşım giderek artan ilgi görmekte; doktora tezleri ve makale revizyonlarında hakemler zaman zaman Bayes faktörü talep etmektedir. JASP bu analizi en erişilebilir biçimde sunan programdır.</p>

<h2>R + RStudio: Nereden Başlamalısınız?</h2>
<p>R'a başlamak için önce r-project.org'dan R'ı, ardından posit.co/download/rstudio-desktop adresinden RStudio'yu kurun. İki kurulum birlikte yaklaşık 10–15 dakika sürer. İlk analiziniz için R konsoluna şu komutları yazın:</p>
<pre><code>install.packages("psych")  # İstatistik paketi
library(psych)
describe(veri)  # Tanımlayıcı istatistikler
t.test(puan ~ grup, data = veri)  # Bağımsız t-testi</code></pre>
<p>Ücretsiz kaynak önerisi: <em>Learning Statistics with R</em> (Navarro, 2019) — sosyal bilim öğrencileri için yazılmış, Türkçe istatistik terminolojisiyle birebir örtüşen bir kaynaktır; learningstatisticswithr.com adresinden ücretsiz erişilebilir.</p>

<h2>Üniversite SPSS Lisansına Nasıl Erişilir?</h2>
<p>Üniversitenizin IBM SPSS kurumsal lisansı olup olmadığını öğrenmek için önce bilgi işlem dairesinin web sitesini kontrol edin; çoğu üniversitede öğrenci kimliğiyle VPN üzerinden ya da kampüs bilgisayarlarından SPSS'e erişim sunulmaktadır. Lisans yoksa veya abone olunan sürüm ihtiyacınızı karşılamıyorsa IBM'in öğrencilere yönelik 30 günlük ücretsiz deneme sürümünü de değerlendirebilirsiniz. Ancak deneme süresi tez analizlerini tamamlamak için çoğunlukla yeterli değildir; bu nedenle jamovi veya JASP gibi kalıcı ücretsiz alternatifleri önden kurmak daha güvenlidir.</p>
"""

APPENDIX_35 = """
<h2>5 Ek Soru-Cevap Şablonu</h2>

<p><strong>"Güç analizi yaptınız mı, örneklem büyüklüğü nasıl belirlendi?"</strong><br>
<em>"Örneklem büyüklüğü G*Power programı ile hesaplanmıştır. [Analiz türü] için orta düzey etki büyüklüğü (f = 0.25 / d = 0.50 / η² = .06), α = .05 ve güç = .80 parametreleri kullanılmış; minimum örneklem [n] kişi olarak belirlenmiştir. Ulaşılan [N] kişilik örneklem bu eşiği karşılamaktadır."</em></p>

<p><strong>"Varsayımlardan biri karşılanmadıysa neden bu testi kullandınız?"</strong><br>
<em>"[Test adı] normallik varsayımı bakımından [küçük/orta düzeyde] ihlale karşı dayanıklıdır (robust); bu özellik alan yazınında [kaynak] tarafından belgelenmiştir. Örneklem büyüklüğünün [N] olması ve dağılımın çarpıklık değerinin (.43) kabul edilen aralıkta (±1.0) kalması nedeniyle parametrik test tercih edilmiştir."</em></p>

<p><strong>"Cronbach Alpha değeriniz neden .70'in altında?"</strong><br>
<em>"Madde silme analizinde [madde numarası] çıkarıldığında alpha değerinin .68'den .74'e yükseleceği görülmüştür; ancak bu madde teorik yapının vazgeçilmez bir bileşenidir. Bu nedenle madde korunmuş ve sınırlı kabul edilebilir güvenilirlik değeri tezde şeffaflıkla raporlanmıştır."</em></p>

<p><strong>"Neden bu post-hoc testi seçtiniz?"</strong><br>
<em>"Levene testi sonucunda grup varyanslarının homojen olduğu belirlenmiştir (p = .312). Eşit varyans ve dengeli grup büyüklükleri koşulunda Tukey HSD, Tip I hatayı en iyi kontrol eden ve alan yazınında en yaygın kabul gören post-hoc testidir (Field, 2018)."</em></p>

<p><strong>"Etki büyüklüğünüz küçük çıktı, bu bulgu anlamlı mı?"</strong><br>
<em>"İstatistiksel anlamlılık ile pratik önemi birbirinden ayırt etmek gerekir. η² = .032 küçük etki büyüklüğüne karşın p &lt; .001 olması, geniş örneklemin hassas tespit gücünü yansıtmaktadır. Alan yazınında [benzer çalışma] benzer etki büyüklükleri raporlamış; bu büyüklük [araştırma alanında] anlamlı bir pratik etki olarak kabul görmektedir."</em></p>

<h2>Savunma Öncesi 3 Günlük Hazırlık Planı</h2>
<table>
  <thead><tr><th>Gün</th><th>Yapılacak</th></tr></thead>
  <tbody>
    <tr><td>3. gün</td><td>Tüm tablolara bakın: hangi analizi neden seçtinizi tek cümleyle açıklayabildiğinizi test edin. Her varsayım kontrolünü gözden geçirin.</td></tr>
    <tr><td>2. gün</td><td>Olası soruları listeleyip cevaplarınızı sesli pratik yapın. Bir arkadaşınıza veya kendinize sunum yapın.</td></tr>
    <tr><td>1. gün</td><td>Sadece tez özetinizi, temel bulgularınızı ve kısıtlılıklarınızı gözden geçirin. Yoğun çalışma yerine dinlenmeyi tercih edin.</td></tr>
  </tbody>
</table>

<h2>Temel Referans Kitaplar</h2>
<p>Savunmada kaynak göstermeniz gerekebilecek temel kitaplar:</p>
<ul>
  <li><strong>Field, A. (2018).</strong> Discovering Statistics Using IBM SPSS Statistics (5th ed.). Sage. — Hemen her istatistiksel test kararı için standart referans.</li>
  <li><strong>Pallant, J. (2020).</strong> SPSS Survival Manual. Routledge. — Adım adım SPSS uygulamaları için.</li>
  <li><strong>Tabachnick, B. G., &amp; Fidell, L. S. (2013).</strong> Using Multivariate Statistics (6th ed.). Pearson. — Regresyon, faktör analizi ve SEM için derinlemesine kaynak.</li>
  <li><strong>APA (2020).</strong> Publication Manual of the American Psychological Association (7th ed.). — Raporlama formatı için nihai otorite.</li>
</ul>
"""


SLUGS_AND_APPENDIXES = [
    ('anova-mi-mann-whitney-mi-hangisini-secmeliyim', APPENDIX_19),
    ('vif-degeri-yuksek-cikti-cok-dogrusal-baglanti-ne-demek', APPENDIX_22),
    ('anova-sonucu-tezde-nasil-raporlanir-apa-formati', APPENDIX_26),
    ('t-testi-tablosu-teze-nasil-eklenir', APPENDIX_27),
    ('cronbach-alpha-guvenilirlik-bulgulari-nasil-yazilir', APPENDIX_28),
    ('likert-olcegine-hangi-istatistik-testi-uygulanir', APPENDIX_31),
    ('eksik-veri-missing-data-tezde-nasil-ele-alinir', APPENDIX_32),
    ('spss-mi-r-mi-tez-icin-hangisi-daha-kolay', APPENDIX_33),
    ('ucretsiz-spss-alternatifi-var-mi-tez-icin-en-iyi-secenekler', APPENDIX_34),
    ('tez-savunmasinda-istatistik-sorulari-nasil-cevaplanir', APPENDIX_35),
]


def expand_posts(apps, schema_editor):
    BlogPost = apps.get_model('forum', 'BlogPost')
    updated = 0
    for slug, appendix in SLUGS_AND_APPENDIXES:
        try:
            post = BlogPost.objects.get(slug=slug)
        except BlogPost.DoesNotExist:
            print(f'  UYARI: {slug} bulunamadı, atlanıyor.')
            continue

        content = post.content
        hr_pos = content.rfind('<hr>')
        if hr_pos != -1:
            post.content = content[:hr_pos] + appendix + content[hr_pos:]
        else:
            post.content = content + appendix
        post.save()
        wc = len(post.content.split())
        print(f'  ✓ {slug[:50]} ({wc} kelime)')
        updated += 1
    print(f'  Toplam: {updated} yazı genişletildi.')


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0129_fix_blogpost_published_at'),
    ]

    operations = [
        migrations.RunPython(expand_posts, migrations.RunPython.noop),
    ]
