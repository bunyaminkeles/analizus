from django.db import migrations

# ID 6: chatgpt teze yazdirmak (382 → 800+)
APPENDIX_6 = """
<h2>Yapay Zeka Dedektörleri: Ne Kadar Güvenilir?</h2>
<p>Turnitin, GPTZero ve Copyleaks gibi AI içerik tespit araçları son iki yılda hızla yaygınlaştı. Ancak bu araçların hata oranları hâlâ tartışmalıdır; sahte pozitif (gerçekte insan tarafından yazılmış metinleri AI ürünü olarak işaretleme) vakaları belgelenmiştir. Bu araçların sonuçlarını tek başına "suç kanıtı" olarak kullanmak akademik adalet açısından sorunludur. Bu nedenle Yükseköğretim Kurulu ve birçok uluslararası üniversite, AI tespit araçlarını kararın kendisi olarak değil, ek bir kontrol katmanı olarak konumlandırmaktadır.</p>

<h2>Türk Üniversitelerinin Mevcut Tutumu</h2>
<p>2023–2024 akademik yılı itibarıyla Türkiye'deki üniversitelerin büyük çoğunluğu, tez ve ödev süreçlerinde yapay zeka kullanımına dair net bir yönetmelik yayınlamamıştır. Bu hukuki boşluk öğrenciler için hem bir muğlaklık hem de bir sorumluluk alanı yaratmaktadır. Etik kurulların çoğu hâlâ mevcut intihal politikalarını temel alarak değerlendirme yapmaktadır. Yönetmelik çıkmamış olması, AI kullanımının "serbest" olduğu anlamına gelmez; aksine, araştırma etiğinin genel ilkeleri geçerliliğini korur.</p>

<h2>Kabul Edilebilir ve Kabul Edilemez Kullanım Senaryoları</h2>
<table>
  <thead><tr><th>Kullanım</th><th>Durum</th><th>Gerekçe</th></tr></thead>
  <tbody>
    <tr><td>Dilbilgisi ve yazım hatalarını düzeltmek</td><td>Genellikle kabul edilebilir</td><td>Araştırmacının katkısını azaltmaz</td></tr>
    <tr><td>Literatür taraması için anahtar kavramlar bulmak</td><td>Sınırlı kabul edilebilir</td><td>Kaynakların bizzat okunması şarttır</td></tr>
    <tr><td>Analiz bölümünü AI'a yazdırmak</td><td>Kabul edilemez</td><td>Araştırmacının yorumunu yok eder</td></tr>
    <tr><td>Var olmayan kaynak üretmek (halüsinasyon)</td><td>Kesinlikle kabul edilemez</td><td>Akademik sahtekârlık sayılır</td></tr>
  </tbody>
</table>

<h2>Yapay Zeka Kullanımını Şeffaf Biçimde Beyan Etmek</h2>
<p>Nature, Science ve Elsevier başta olmak üzere büyük yayıncılar, makalenin Yöntem veya Teşekkür bölümünde yapay zeka kullanımının nasıl ve ne amaçla gerçekleştiğinin açıklanmasını zorunlu hale getirmiştir. Tez düzeyinde de bu şeffaflık giderek beklenmektedir. Örnek beyan: <em>"Bu tezin yazım sürecinde dil bilgisi denetimi amacıyla ChatGPT-4 (OpenAI, 2024) kullanılmış; tüm içerik, yorum ve analiz kararları araştırmacı tarafından üretilmiştir."</em></p>
<p>Yapay zekanın akademik ekosistemdeki yerini etik bir çerçevede belirlemek, hem bireysel araştırmacıların hem de kurumların ortak sorumluluğudur. Teknolojiyi reddetmek değil, onu dürüstçe ve sorumlu biçimde kullanmak sürdürülebilir akademik pratiğin temelidir.</p>
"""

# ID 8: yayinla ya da yok ol (384 → 800+)
APPENDIX_8 = """
<h2>DORA Bildirgesi: Yeni Bir Değerlendirme Anlayışı</h2>
<p>San Francisco Araştırma Değerlendirmesi Bildirisi (DORA), 2012 yılında yayımlanmış ve bugün 20.000'den fazla kurum ve araştırmacı tarafından imzalanmıştır. DORA'nın temel talebi, akademisyen değerlendirmesinde Dergi Etki Faktörü'nün (Journal Impact Factor) tek ölçüt olarak kullanılmamasıdır. Bunun yerine bireysel makalelerin içerik kalitesi, toplumsal etki, veri paylaşımı, açık erişim katkıları ve disiplinler arası işbirliği gibi çok boyutlu kriterler önerilmektedir. Türkiye'deki üniversitelerin büyük çoğunluğu henüz DORA'yı imzalamamış olsa da uluslararası akademik çevrelerde bu dönüşüm ivme kazanmaktadır.</p>

<h2>Türkiye Akademisinde Doçentlik Baskısının Yapısal Boyutu</h2>
<p>Türkiye'de doçentlik şartlarında belirli sayıda ve puanlı yayın zorunluluğunun bulunması, araştırmacıları nitelikten çok niceliğe yönelten sistemik bir baskı yaratmaktadır. Bu baskı altında genç akademisyenler kısa sürede çok sayıda yayın üretmeye çalışırken, yıllarca emek gerektiren uzun soluklu araştırmaların değersizleşmesi riski ortaya çıkmaktadır. Ayrıca sınırlı hakem havuzunda hakem bulma krizi ve hakem yorgunluğu (reviewer fatigue) sistemi içten kemirmektedir.</p>

<h2>Sürdürülebilir Akademik Kariyer İçin Pratik Öneriler</h2>
<ol>
  <li><strong>Nitelikli az yayın:</strong> Az sayıda yüksek etkili dergide yayın, uzun vadede h-indeksinizi çok sayıda düşük etkili yayından daha güçlü kılacaktır.</li>
  <li><strong>Açık erişimi benimseyin:</strong> Makalelerinizin preprint versiyonunu arXiv, OSF veya Zenodo gibi platformlarda paylaşmak görünürlüğü artırır ve atıf alma olasılığını yükseltir.</li>
  <li><strong>Uluslararası işbirliği kurun:</strong> Ortak yazarlık hem atıf ağınızı genişletir hem de farklı metodolojik yaklaşımlarla araştırma kalitenizi artırır.</li>
  <li><strong>Hakem olun:</strong> Kaliteli dergilerde hakem olarak yer almak hem alanı öğretir hem de akademik itibar biriktirir.</li>
</ol>

<h2>Atıf Karteli Tespiti ve Bireysel Korunma</h2>
<p>Web of Science ve Scopus gibi veritabanları, anormal atıf örüntülerini tespit eden algoritmalar geliştirmiştir. Coercive citation (zorla atıf) talepleri hakem sürecinde karşılaşıldığında derginin editörüne ya da COPE'a şikayette bulunulabilir. Bu tür baskılara boyun eğmek kısa vadede kolaylık sağlasa da uzun vadede araştırmacının akademik özerkliğini ve itibarını zedeler. Bilimsel dürüstlüğü korumak bireysel bir karardır; ancak akademinin kolektif sağlığı bu bireysel kararların toplamından oluşur.</p>
"""

# ID 9: Türkiye akademik üretimi (373 → 800+)
APPENDIX_9 = """
<h2>OpenAlex'te Türkiye Verisine Nasıl Erişilir?</h2>
<p>OpenAlex, 250 milyondan fazla akademik çalışmayı ücretsiz sunan açık bir bibliyografik veritabanıdır. Türkiye'ye ait yayın istatistiklerine openalex.org adresinden "Turkey" filtresiyle veya API üzerinden erişilebilir. Yıllık yayın sayısı, alan dağılımı, atıf ortalaması ve uluslararası işbirliği oranı gibi metrikleri görselleştiren hazır paneller mevcuttur. Araştırmacılar ve tez öğrencileri OpenAlex API'yi Python'da <code>requests</code> kütüphanesiyle kolayca sorgulayabilir; bu sayede özgün bibliyometrik analizler yürütmek mümkündür.</p>

<h2>Uluslararası İşbirliği: Türkiye'nin Zayıf Halkası</h2>
<p>Benzer ekonomik büyüklükteki ülkelerle (Polonya, Romanya, Arjantin) karşılaştırıldığında Türkiye'nin uluslararası ortak yazarlık oranı görece düşük kalmaktadır. Uluslararası işbirliğiyle üretilen makaleler hem daha yüksek atıf ortalamasına sahiptir hem de Q1–Q2 dergilerde yayımlanma olasılıkları daha yüksektir. TÜBİTAK'ın 2547 çerçevesinde yürüttüğü çift taraflı işbirliği programları ve Avrupa Araştırma Konseyi (ERC) projelerine katılım, bu açığı kapatmak için kritik araçlar arasında yer almaktadır.</p>

<h2>Alan Bazlı Güçlü ve Zayıf Yönler</h2>
<table>
  <thead><tr><th>Alan</th><th>Güçlü Yön</th><th>Zayıf Yön</th></tr></thead>
  <tbody>
    <tr><td>Mühendislik</td><td>Yüksek yayın hacmi</td><td>Patent dönüşümü düşük</td></tr>
    <tr><td>Sağlık Bilimleri</td><td>Klinik çalışma sayısı artıyor</td><td>Açık veri paylaşımı yetersiz</td></tr>
    <tr><td>Sosyal Bilimler</td><td>TR Dizin kapsamı genişliyor</td><td>Uluslararası atıf almak zor</td></tr>
    <tr><td>Temel Bilimler</td><td>Q1 dergilerde artan varlık</td><td>Araştırmacı başına bütçe kısıtlı</td></tr>
  </tbody>
</table>

<h2>Araştırmacı ve Öğrenci için Somut Öneriler</h2>
<p>Türkiye'nin bibliometrik zayıflıklarını bireysel düzeyde aşmak için şu adımlar önerilebilir: Makalelerinizi açık erişim platformlarına (arXiv, PubMed Central, ResearchGate) yükleyerek görünürlüğü artırın; ORCID kimliğinizi tüm yayınlarınıza bağlayın; uluslararası ağlar kurmak için konferans sunumlarını ve ResearchGate gibi platformları aktif kullanın. Tez düzeyindeki çalışmalar için OpenAlex ve TR Dizin'i araştırmanızın özgün bibliyometrik bağlamını kurmak amacıyla kullanmak, danışmanların takdirini kazanan özgün bir yöntem olarak öne çıkmaktadır.</p>
"""

# ID 11: KVKK Google Drive (339 → 800+)
APPENDIX_11 = """
<h2>Hangi Veriler "Özel Nitelikli" Sayılır?</h2>
<p>KVKK, kişisel verileri iki kategoride ele alır. <em>Genel nitelikli kişisel veri</em>: isim, soyisim, e-posta, telefon, fotoğraf. <em>Özel nitelikli kişisel veri</em> (KVKK Madde 6): ırk, etnik köken, siyasi görüş, dini inanç, sağlık bilgisi, cinsel yönelim, biyometrik veri, ceza mahkûmiyeti. Akademik araştırmalarda sağlık anketleri, psikolojik ölçekler ve demografik bilgi formları çoğunlukla bu kategorilerden birine girer. Özel nitelikli veriyi işlemek için Veri Koruma Kurulu'nun belirlediği şartların sağlanması zorunludur.</p>

<h2>Üniversite Sunucuları Gerçekten Güvenli mi?</h2>
<p>Üniversite e-posta ve bulut sistemleri (örn. Office 365, Google Workspace for Education) kampüs lisansı kapsamında olsa da sunucular çoğunlukla yurt dışındadır. Bu nedenle "üniversite e-posta adresiyle erişiyorum, güvenliyim" varsayımı KVKK açısından doğru değildir. Kişisel veri içeren araştırma dosyalarının üniversitenin kendi veri merkezindeki sunucularında (on-premise) veya KVKK uyumlu yerel bulut çözümlerinde saklanması hukuken daha sağlam bir zemin oluşturur. Bilgi işlem dairenizdeki teknik ekiple görüşmek en doğru ilk adımdır.</p>

<h2>Etik Kurul Başvurusunda Veri Güvenliği</h2>
<p>Etik kurul başvuru formları genellikle şu soruları içerir: "Veriler nerede saklanacak?", "Saklama süresi ne kadardır?", "Veri imha prosedürü nedir?" Bu soruları "kişisel bilgisayarımda" veya "Google Drive'da" olarak yanıtlamak, etik kurul tarafından eksik veya riskli bulunabilir. Önerilen yanıt formatı: <em>"Toplanan veriler araştırmacının yerel bilgisayarında AES-256 şifreleme ile korunmuş bir klasörde saklanacak; proje tamamlandıktan sonra kişisel bilgiler anonimleştirilerek ham veri güvenli şekilde silinecektir."</em></p>

<h2>KVKK İhlali Cezaları</h2>
<p>2016 tarihli KVKK kapsamında veri güvenliği ihlallerinde idari para cezaları 2024 yılında yeniden düzenlenmiş olup ihlal türüne göre değişmektedir. Kişisel Verileri Koruma Kurumu (KVKK), ihlal tespiti durumunda hem kuruma (üniversiteye) hem de veri işleyen sıfatıyla araştırmacıya ceza uygulayabilir. Hukuki yaptırımın ötesinde veri ihlali, araştırma katılımcılarının güvenini zedeler ve akademik kurumun itibarını olumsuz etkiler.</p>

<h2>Araştırma Verisi Paylaşımı: Açık Veri ile Gizlilik Dengesi</h2>
<p>Açık bilim (open science) hareketi araştırma verilerinin paylaşılmasını teşvik ederken KVKK ve GDPR gizliliği zorunlu kılar. Bu gerilimi çözmenin yolu: kişisel tanımlayıcıları tamamen çıkarmış <em>anonimleştirilmiş</em> veri setini paylaşmak, ham veriyi ise üniversitenin güvenli deposunda tutmaktır. OSF (Open Science Framework), Harvard Dataverse ve Zenodo gibi platformlar bu yaklaşımı destekleyen altyapı sunar. Tezinizde "Araştırma verilerinin anonimleştirilmiş sürümü [platform adı]'nda erişime açılmıştır" ifadesi hem şeffaflığı hem de gizliliği karşılar.</p>
"""

# ID 12: anonimleştirme yanılgısı (346 → 800+)
APPENDIX_12 = """
<h2>Sentetik Veri: Gizliliğin Matematiksel Çözümü</h2>
<p>Klasik anonimleştirme yöntemlerinin sınırlarına karşı günümüzde <strong>sentetik veri üretimi</strong> ön plana çıkmaktadır. Sentetik veri, gerçek verilerden istatistiksel özellikleri öğrenerek (örneğin üretici çekişmeli ağlar — GAN — ya da Bayesyen modeller kullanarak) tamamen yapay ama istatistiksel açıdan orijinal veriyle aynı davranışı gösteren bir veri kümesi oluşturur. Böylece hiçbir gerçek birey hakkında bilgi içermediğinden re-identification mümkün değildir. Google, Microsoft ve birçok sağlık kurumu araştırma için sentetik veri üretimini aktif olarak kullanmaktadır.</p>

<h2>Tez Araştırmasında Anonimleştirme Nasıl Yapılır?</h2>
<p>Anket veya mülakat verisi toplayan tez araştırmacıları için pratik anonimleştirme adımları:</p>
<ol>
  <li><strong>Doğrudan tanımlayıcıları kaldırın:</strong> İsim, TC kimlik numarası, e-posta, telefon, adres — bunların tamamını veri setinden silin.</li>
  <li><strong>Dolaylı tanımlayıcıları genelleştirin:</strong> Yaşı "32" yerine "30–39" aralığına çevirin; mesleği "Doktor" yerine "Sağlık çalışanı" olarak kodlayın.</li>
  <li><strong>k=5 kuralını uygulayın:</strong> Veri setinizdeki herhangi bir kombinasyonun en az 5 kişiyi içerip içermediğini kontrol edin. 5'ten az kişide görülen kombinasyonlar tanımlama riskidir.</li>
  <li><strong>Takma ad (pseudonymisation) kullanın:</strong> Katılımcı adlarını "Katılımcı 1, Katılımcı 2…" şeklinde kodlayın; eşleştirme tablosunu şifreli ve ayrı bir dosyada saklayın.</li>
</ol>

<h2>Tez Çalışmalarında KVKK Uyumu</h2>
<p>Anonimleştirme işleminin tamamlanmasından sonra verinin KVKK kapsamından çıkıp çıkmadığı kritik bir sorudur. KVKK'ya göre gerçek anlamda anonimleştirilmiş veri (yani hiçbir şekilde kimliği belirlenebilir olmayan veri) kişisel veri sayılmaz ve kanun kapsamı dışına çıkar. Bu eşiğe ulaştığınızda veriyi araştırma topluluğuyla paylaşmanız hem etik hem de hukuken sorunsuz hâle gelir.</p>

<h2>Güvenli Veri Paylaşım Platformları</h2>
<p>Etik ve hukuki gereksinimler karşılandıktan sonra anonimleştirilmiş araştırma verilerini paylaşmak için kullanılabilecek güvenilir platformlar: <strong>OSF (Open Science Framework)</strong> akademik çevrede en yaygın tercih; <strong>Harvard Dataverse</strong> sosyal bilimler için kapsamlı altyapı sunar; <strong>Zenodo</strong> CERN bünyesinde geliştirilmiş, her türlü araştırma çıktısına uygun açık erişim deposu. Bu platformlarda veriye DOI (Dijital Nesne Tanımlayıcı) atanması tezinizin alıntılanabilirliğini artırır ve açık bilim uygulamasını somutlaştırır.</p>
"""

# ID 13: sağlıkta veri krizi (348 → 800+)
APPENDIX_13 = """
<h2>Uluslararası Başarı Örnekleri: Açık Sağlık Verisi</h2>
<p>İngiltere'nin <strong>UK Biobank</strong> projesi 500.000 gönüllünün genetik, biyometrik ve sağlık verilerini denetimli bir başvuru sistemiyle araştırmacılara açmaktadır; bugüne kadar 30.000'den fazla araştırmacı bu veriye erişmiştir. İskandinav ülkeleri (İsveç, Finlandiya, Danimarka), doğumdan ölüme kadar bireysel sağlık kayıtlarını benzersiz ulusal kimlik numarasıyla bağlayan <em>kayıt bağlama (record linkage)</em> altyapısına sahiptir. Bu ülkelerdeki araştırmacılar, Türkiye'deki mevcut bürokratik sürecin bir kısmını tek bir veri talebi başvurusuyla çözebilmektedir.</p>

<h2>Türkiye'nin Fırsatları: Yapılabilecekler</h2>
<p>e-Nabız sistemi, teorik olarak Türkiye'ye dünya genelinde sayılı ülkelerde bulunan bir araştırma varlığı kazandırmaktadır. Bu potansiyeli gerçeğe dönüştürmek için üç somut adım gereklidir:</p>
<ol>
  <li><strong>Araştırmacı başvuru portalı:</strong> Sağlık Bakanlığı bünyesinde standart, şeffaf ve dijital bir veri erişim başvuru sistemi kurulması. Başvuru sürecinin 30 günü geçmemesi hedeflenmelidir.</li>
  <li><strong>Veri güvenli oda (safe data room):</strong> Araştırmacıların bakanlık ortamında denetimli biçimde mikroveriye erişebildiği, verilerin kurumu terk etmediği fiziksel veya sanal çalışma ortamları.</li>
  <li><strong>Etik-idari tek pencere:</strong> Etik kurul onayı ve kurum izni süreçlerinin tek bir başvuruda birleştirilmesi, bürokratik yükü azaltır ve araştırma sürecini hızlandırır.</li>
</ol>

<h2>Araştırmacılar İçin Mevcut Alternatifler</h2>
<p>Sağlık Bakanlığı verilerine erişim beklenirken araştırmacılar şu alternatif kaynaklara yönelebilir: <strong>Global Burden of Disease (GBD)</strong> çalışması Türkiye için ülke düzeyinde hastalık yükü verisi sunar (healthdata.org); <strong>WHO Global Health Observatory</strong> Türkiye'ye ait temel sağlık göstergelerini içerir; <strong>OECD Health Statistics</strong> karşılaştırmalı analiz için kullanışlıdır. Klinik araştırmacılar için ClinicalTrials.gov'daki tamamlanmış çalışmaların ham verileri, çalışma ekiplerinden kişisel başvuru yoluyla istenebilir.</p>

<h2>Veri Talebi Sürecinde Pratik Adımlar</h2>
<p>Mevcut sistem içinde veri erişimi için şu yolu izleyin: önce kurumunuzun etik kurulundan onay alın; ardından ilgili ilin Sağlık Müdürlüğü'ne resmi yazıyla müracaat edin; başvuruya etik kurul kararı, araştırma protokolü ve anonimleştirme planını ekleyin. Retrospektif dosya taraması için hastane başhekimliğine ayrıca başvurmak gerektiğini unutmayın. Sürecin uzamasına karşı çalışma takvimini 3–6 ay veri erişim bekleme süresi hesaplayarak planlayın; etik kurul kararı henüz alınmadan veri talebine girişmek zaman kaybettirir.</p>
"""

# ID 14: survival analizi (391 → 800+)
APPENDIX_14 = """
<h2>SPSS'te Kaplan-Meier Analizi: Adım Adım</h2>
<p>SPSS'te Kaplan-Meier analizi şu yolu izleyerek yapılır: Analyze → Survival → Kaplan-Meier. <em>Time</em> kutusuna süre değişkeninizi, <em>Status</em> kutusuna olay (örneğin ölüm = 1, sansürlü = 0) değişkeninizi girin. <em>Define Event</em>'te olay kodunu (1) belirleyin. Gruplar arasında karşılaştırma yapmak istiyorsanız <em>Factor</em> kutusuna grup değişkeninizi ekleyin ve <em>Compare Factor</em> kısmında Log-rank, Breslow veya Tarone-Ware testlerinden birini seçin. Sosyal bilimler ve klinik araştırmalarda Log-rank en yaygın kullanılan testtir.</p>

<h2>Cox Regresyonu Varsayımları</h2>
<p>Cox modelinin en temel varsayımı <strong>Orantılı Riskler (Proportional Hazards)</strong> varsayımıdır: her bağımsız değişkenin risk üzerindeki etkisinin zaman içinde sabit kalması gerekir. Bu varsayımı test etmek için Schoenfeld artıklarını zaman üzerine çizin; süre ile anlamlı korelasyon olmaması varsayımın karşılandığını gösterir. SPSS'te bu testi doğrudan üretmek mümkün değildir; R'ın <em>survival</em> paketindeki <code>cox.zph()</code> fonksiyonu bu iş için standarttır. Varsayım ihlal edildiğinde zaman-bağımlı kovariyatlar (time-dependent covariates) veya tabakalama (stratification) ile model düzeltilir.</p>

<h2>Hazard Ratio'yu Tezde Raporlamak</h2>
<p>Cox regresyon çıktısında Exp(B) sütunu Hazard Ratio (HR), 95% CI sütunu güven aralığını verir. APA formatında raporlama örneği: <em>"İleri yaş, ölüm riskini anlamlı biçimde artırmaktadır (HR = 1.08, %95 CI [1.04, 1.12], p &lt; .001). Bu bulgu, her bir yıllık yaş artışının ölüm riskini %8 oranında yükselttiğini göstermektedir."</em> HR &lt; 1 olan değişkenler için "<em>risk %X azaltmaktadır</em>" ifadesi kullanılır.</p>

<h2>Survival Analizinde Sık Yapılan Hatalar</h2>
<ol>
  <li><strong>Sansürlü veriyi silmek:</strong> Gözlem süresince olayın gerçekleşmediği katılımcıları analiz dışı bırakmak, veri kaybına ve taraflı sonuçlara yol açar. Sansürlü veriler mutlaka modele dahil edilmelidir.</li>
  <li><strong>Zaman sıfır noktasını yanlış tanımlamak:</strong> Süreyi "tedavi başlangıcı", "teşhis tarihi" veya "araştırmaya giriş" olarak tanımlamak arasındaki seçim sonuçları kökten değiştirebilir. Zaman sıfırı net ve gerekçeli biçimde tanımlanmalıdır.</li>
  <li><strong>Küçük örneklemde Cox modeli:</strong> Cox regresyonunda değişken başına en az 10 olay gözlemi önerilir; "10 events per variable" kuralı çok değişkenli modellerde özellikle önemlidir.</li>
</ol>
"""

# ID 15: enflasyon verileri (381 → 800+)
APPENDIX_15 = """
<h2>Mevsimsel Düzeltme ve Zincirleme Metodolojisi</h2>
<p>Enflasyon ölçümündeki teknik tartışmaların önemli bir boyutunu <strong>mevsimsel düzeltme</strong> oluşturmaktadır. Gıda fiyatlarının yaz aylarında düşmesi, akaryakıt fiyatlarının kış aylarında artması gibi dönemsel etkileri arındırmak için X-13ARIMA-SEATS gibi mevsimsel düzeltme algoritmaları uygulanır. TÜİK bu yöntemi kullanmakta, ancak mevsim dışı faktörlerin (örneğin kuraklık, döviz kuru şoku) yakalanmasında metodoloji tartışmalıdır. Zincirleme (chain-linking) yöntemi ise sepet ağırlıklarının yıllık güncellenmesi yerine sürekli güncellenmesini sağlayarak "ağırlıklandırma gecikmesi" (substitution bias) etkisini azaltır.</p>

<h2>Enflasyon Beklentilerinin Ölçümü</h2>
<p>Gerçekleşen enflasyonun yanı sıra <em>beklenti enflasyonu</em>, merkez bankacılığının ve ekonometrik modellemenin kritik bir girdisidir. Türkiye Cumhuriyet Merkez Bankası (TCMB), her ay tüketici ve firma beklenti anketleri yayımlamaktadır. Bu anketlerdeki beklentiler ile gerçekleşen enflasyon arasındaki sapma (forecast error), para politikasının güvenilirliğini ölçen önemli bir göstergedir. Akademik araştırmalar için TCMB'nin web sitesindeki Beklenti Anketi veri setleri açık erişimle indirilebilmektedir.</p>

<h2>ILO Uluslararası Standartlarıyla Karşılaştırma</h2>
<p>Uluslararası Çalışma Örgütü (ILO), Tüketici Fiyat Endeksi hesaplamalarına ilişkin 2003 tarihli bir rehber yayımlamış ve bu rehber çoğu ulusal istatistik kurumu tarafından referans alınmaktadır. Temel standartlar şunlardır: fiyatların temsili ve çeşitli satış noktalarından derlenmesi, sepet ağırlıklarının güncel tüketim verilerine dayanması, hesaplama yönteminin kamuoyuyla paylaşılması. Türkiye'nin TÜİK metodolojisi ILO standartlarıyla büyük ölçüde uyumludur; ancak şeffaflık ve bağımsız doğrulama mekanizmaları hâlâ güçlendirilmesi gereken alanlar olarak öne çıkmaktadır.</p>

<h2>Veriye Eleştirel Yaklaşmak: Araştırmacının Sorumluluğu</h2>
<p>Bir ekonometristın veya sosyal bilimcinin enflasyon verisi kullanırken dikkat etmesi gereken temel prensipler şunlardır: Veriyi üreten kurumun metodoloji dokümanını okuyun; farklı endeksleri (TÜFE, ÜFE, çekirdek enflasyon) birbirinin yerine kullanmaktan kaçının; göreli fiyat değişimleri ile genel fiyat düzeyi değişimlerini birbirinden ayırt edin. İstatistiksel bir analizde "resmi enflasyon verisi" kullanıyorsanız TÜİK'in hangi yıl baz alındığını, hangi endeks serisi kullanıldığını ve mevsimsel düzeltme uygulanıp uygulanmadığını tezinizde açıkça belirtmeniz, sonuçların tekrar üretilebilirliği açısından zorunludur.</p>
"""

# ID 17: normallik sağlanmazsa (321 → 800+)
APPENDIX_17 = """
<h2>Wilcoxon İşaretli Sıralar Testi: Bağımlı T-Testinin Alternatifi</h2>
<p>Wilcoxon İşaretli Sıralar Testi, bağımlı örneklem t-testinin non-parametrik karşılığıdır. Aynı katılımcıdan alınan iki ölçüm (örneğin ön-test ve son-test) arasındaki farkları sıralama değerlerine dönüştürerek analiz eder. Fark puanlarının normal dağılıma uymaması veya örneklem sayısının küçük olması durumunda (N &lt; 30) t-testine tercih edilmelidir.</p>
<p>SPSS'te uygulama için: Analyze → Nonparametric Tests → Legacy Dialogs → 2 Related Samples → her iki ölçüm değişkenini çift olarak girin → Wilcoxon kutucuğunu işaretleyin → OK.</p>
<p>APA raporlama: <em>"Müdahale öncesi ve sonrası puanlar arasındaki fark Wilcoxon İşaretli Sıralar Testi ile incelenmiş; son-test puanlarının ön-test puanlarından anlamlı biçimde yüksek olduğu belirlenmiştir (z = −3.42, p = .001, r = .48)."</em></p>

<h2>Kruskal-Wallis H Testi: ANOVA'nın Non-Parametrik Karşılığı</h2>
<p>Üç veya daha fazla bağımsız grup karşılaştırmasında normallik sağlanmadığında Kruskal-Wallis H testi kullanılır. ANOVA'nın non-parametrik karşılığı olan bu test, gözlemleri sıralama değerlerine çevirerek grupların ortanca sıralamalarını karşılaştırır.</p>
<p>SPSS'te uygulama: Analyze → Nonparametric Tests → Legacy Dialogs → K Independent Samples → test değişkenini <em>Test Variable List</em>'e, gruplandırma değişkenini <em>Grouping Variable</em>'a girin → Kruskal-Wallis H işaretleyin → Define Range ile minimum ve maksimum grup numarasını girin → OK.</p>
<p>Kruskal-Wallis anlamlı çıktığında hangi gruplar arasında fark olduğunu bulmak için ikili karşılaştırma gerekir; bu aşamada <strong>Dunn testi</strong> (Bonferroni düzeltmeli) veya SPSS'in pairwise comparison seçeneği kullanılır.</p>

<h2>Spearman Rho: Pearson'ın Non-Parametrik Karşılığı</h2>
<p>İki değişken arasındaki ilişki normal dağılıma uymadığında Pearson yerine Spearman Rho kullanılır. Spearman, ham değerler yerine sıralama değerlerini kullanır; bu sayede aykırı değerlere karşı dayanıklıdır. SPSS'te: Analyze → Correlate → Bivariate → Spearman kutucuğunu işaretleyin. Raporlama: <em>"İki değişken arasında pozitif yönde orta düzeyde anlamlı bir ilişki bulunmuştur (rₛ = .43, p = .002)."</em></p>

<h2>Sık Yapılan Hatalar</h2>
<ol>
  <li><strong>Normallik p &lt; .05 çıkar çıkmaz non-parametriğe geçmek:</strong> Büyük örneklemlerde (N &gt; 100) normallik testleri aşırı duyarlıdır. Skewness ve kurtosis değerlerini de inceleyin.</li>
  <li><strong>3+ grup için Mann-Whitney U uygulamak:</strong> Üç veya daha fazla grup karşılaştırmasında Mann-Whitney U değil, Kruskal-Wallis H testi yapılmalıdır.</li>
  <li><strong>Etki büyüklüğünü raporlamamak:</strong> Kruskal-Wallis için η²H, Mann-Whitney için r (rank-biserial) ve Wilcoxon için r = z/√N etki büyüklükleri APA raporlamasında zorunludur.</li>
</ol>
"""

# ID 18: bağımsız mı bağımlı mı (335 → 800+)
APPENDIX_18 = """
<h2>SPSS'te Bağımsız t-Testi Adım Adım</h2>
<p>Analyze → Compare Means → Independent-Samples T Test yolunu izleyin. Bağımlı değişkeninizi (test edilecek puan) <em>Test Variable(s)</em> kutusuna, grup değişkeninizi (örn. cinsiyet: 1=Kadın, 2=Erkek) <em>Grouping Variable</em> kutusuna girin. <em>Define Groups</em>'ta grup kodlarını (1 ve 2) belirleyin → OK. Çıktıda önce Levene testini kontrol edin; p &gt; .05 ise "Equal variances assumed" satırını kullanın, p ≤ .05 ise "Equal variances not assumed" (Welch düzeltmesi) satırını kullanın.</p>

<h2>SPSS'te Bağımlı t-Testi Adım Adım</h2>
<p>Analyze → Compare Means → Paired-Samples T Test yolunu izleyin. İki ölçümü (örn. ön-test ve son-test değişkenlerini) yan yana seçerek <em>Paired Variables</em> listesine ekleyin → OK. Çıktıda Paired Differences bölümündeki Mean (fark ortalaması), Std. Deviation, t, df ve Sig.(2-tailed) değerlerini raporlayın.</p>

<h2>Etki Büyüklükleri: İki Test Karşılaştırması</h2>
<table>
  <thead><tr><th>Test Türü</th><th>Etki Büyüklüğü</th><th>Hesaplama</th></tr></thead>
  <tbody>
    <tr><td>Bağımsız t-Testi</td><td>Cohen's d</td><td>(M₁ − M₂) / SD_havuzlu</td></tr>
    <tr><td>Bağımlı t-Testi</td><td>Cohen's d (fark puanı)</td><td>M_fark / SD_fark</td></tr>
  </tbody>
</table>
<p>Bağımlı t-testinde Cohen's d genellikle bağımsız t-testindeki d değerinden büyük çıkar; çünkü bireyler arası varyans kontrol altına alınır. Bu nedenle iki tür d değerini doğrudan karşılaştırmak yanıltıcıdır.</p>

<h2>Araştırma Tasarımını Doğru Eşleştirmek</h2>
<p>Yanlış t-testi seçimi yalnızca p değerini değil, yorumun bütününü etkiler. Kontrol-deney grubu karşılaştırmasında katılımcılar rastgele iki gruba atanmış ve ölçümler eş zamanlı yapılmışsa bağımsız t-testi doğru seçimdir. Aynı kişi üzerinde iki farklı koşul veya iki farklı zaman noktasında ölçüm varsa bağımlı t-testi tek geçerli seçenektir. Karışık tasarımlarda (mixed design) bazı faktörler bağımsız, bazıları bağımlı olabilir; bu durumda karışık ANOVA tercih edilir.</p>

<h2>Non-Parametrik Alternatifler</h2>
<p>Normallik varsayımı karşılanmadığında iki teste de non-parametrik alternatif mevcuttur:</p>
<ul>
  <li>Bağımsız t-Testi → <strong>Mann-Whitney U Testi</strong></li>
  <li>Bağımlı t-Testi → <strong>Wilcoxon İşaretli Sıralar Testi</strong></li>
</ul>
<p>SPSS'te bu alternatiflere Analyze → Nonparametric Tests → Legacy Dialogs yolundan ulaşılır.</p>
"""

# ID 20: ki-kare mi lojistik regresyon (329 → 800+)
APPENDIX_20 = """
<h2>Ki-Kare İçin Beklenen Hücre Sayısı Varsayımı</h2>
<p>Ki-kare testini uygulamadan önce bir varsayımı kontrol etmeniz zorunludur: çapraz tablodaki beklenen hücre sayılarının (expected counts) %80'i veya daha fazlası ≥ 5 olmalıdır. SPSS çıktısında <em>"a cells have expected count less than 5"</em> uyarısı görünüyorsa ki-kare sonuçları güvenilmez olabilir.</p>
<p>Bu durumda yapılabilecekler: (1) Kategorileri birleştirerek hücre sayılarını artırın. (2) 2×2 tablolarda <strong>Fisher'ın Kesin Testi (Fisher's Exact Test)</strong>'ne geçin — SPSS ki-kare çıktısında bu testi otomatik gösterir. (3) Monte Carlo simülasyonu ile olasılık hesaplaması yapın (SPSS'te Exact sekmesinden).</p>

<h2>Fisher'ın Kesin Testi Ne Zaman Kullanılır?</h2>
<p>Fisher's Exact Test, hücre sayılarının küçük olduğu 2×2 tablolarda ki-kare yerine tercih edilir. Ki-karenin asimptotik yaklaşımı küçük örneklemlerde güvenilmezken Fisher testi tam olasılık hesabı yapar. SPSS çıktısında otomatik görünür; raporlama: <em>"Küçük hücre frekansları nedeniyle ki-kare testi yerine Fisher'ın Kesin Testi uygulanmış ve iki değişken arasında anlamlı ilişki bulunmuştur (p = .032)."</em></p>

<h2>Lojistik Regresyon SPSS'te Adım Adım</h2>
<p>Analyze → Regression → Binary Logistic yolunu izleyin. İkili bağımlı değişkeninizi (0/1) <em>Dependent</em> kutusuna, bağımsız değişkenleri <em>Covariates</em> kutusuna girin. Method olarak <em>Enter</em> (zorunlu giriş) veya <em>Forward: LR</em> (adımsal) seçin. Options kısmında <em>Classification plots</em>, <em>Hosmer-Lemeshow goodness-of-fit</em> ve <em>CI for exp(B)</em> seçeneklerini işaretleyin.</p>

<h2>Etki Büyüklükleri: Ki-Kare ve Lojistik Regresyon</h2>
<table>
  <thead><tr><th>Analiz</th><th>Etki Büyüklüğü</th><th>Küçük</th><th>Orta</th><th>Büyük</th></tr></thead>
  <tbody>
    <tr><td>Ki-Kare</td><td>Cramer's V</td><td>.10</td><td>.30</td><td>.50</td></tr>
    <tr><td>Lojistik Regresyon</td><td>Nagelkerke R²</td><td>.10</td><td>.30</td><td>.50</td></tr>
  </tbody>
</table>
<p>SPSS ki-kare çıktısında Cramer's V ve Phi değerleri <em>Symmetric Measures</em> tablosunda görünür. Nagelkerke R² ise lojistik regresyon çıktısındaki <em>Model Summary</em> tablosunda yer alır.</p>

<h2>Sık Yapılan Hatalar</h2>
<ol>
  <li><strong>Ki-kare ile nedensellik kurmak:</strong> Ki-kare yalnızca ilişkiyi (association) gösterir; nedenselliği (causation) kanıtlamaz. "A değişkeni B'ye yol açar" ifadesi yerine "A ile B arasında anlamlı ilişki bulunmuştur" ifadesini kullanın.</li>
  <li><strong>Çoklu lojistik regresyonu ihmal etmek:</strong> Birden fazla bağımsız değişken varsa basit ki-kare yerine lojistik regresyon, her değişkenin bağımsız katkısını kontrol ederek analiz eder.</li>
  <li><strong>Odds Ratio'yu Risk Ratio gibi yorumlamak:</strong> OR ve RR farklı kavramlardır; düşük prevalanslı olaylarda yakın sonuç verse de, yüksek prevalanslı olaylarda büyük fark yaratır.</li>
</ol>
"""

# ID 21: p > 0.05 çıkınca (352 → 800+)
APPENDIX_21 = """
<h2>Tip II Hata ve İstatistiksel Güç</h2>
<p>p &gt; 0.05 çıkmasının iki olası açıklaması vardır: (1) Gerçekte etki yoktur. (2) Etki vardır ama örneklem bunu tespit edecek kadar büyük değildir — bu durum Tip II Hata (β) olarak adlandırılır. İstatistiksel güç (1 − β), araştırmanın gerçek bir etkiyi doğru biçimde tespit etme olasılığıdır. Davranış bilimlerinde standart güç hedefi .80'dir; bu, gerçek bir etki varsa %80 ihtimalle anlamlı sonuç elde edileceği anlamına gelir.</p>
<p>Güç &lt; .50 olan bir çalışmada p &gt; .05 bulgusu, testin başarısızlığı değil; araştırmanın yetersiz güçte tasarlandığının göstergesidir. Bu yorumu tezinizin Kısıtlılıklar bölümünde şeffaflıkla belirtin.</p>

<h2>Geriye Dönük Güç Analizi (Post-Hoc Power)</h2>
<p>Veri toplanıp analiz yapıldıktan sonra "Peki gücüm neydi?" sorusunu yanıtlamak için geriye dönük güç analizi yapılabilir. G*Power yazılımında:</p>
<ol>
  <li>Test türünüzü seçin (t-test, ANOVA vb.).</li>
  <li>"Post-hoc: Compute achieved power" seçeneğini işaretleyin.</li>
  <li>Elde ettiğiniz etki büyüklüğünü, α = .05'i ve N'inizi girin.</li>
  <li>Hesaplanan güç değerini raporlayın.</li>
</ol>
<p>Önemli uyarı: post-hoc güç analizi tartışmalı bir uygulamadır; bazı metodologlar gözlenen etkiyi kullanarak güç hesaplamanın döngüsel bir mantık içerdiğini belirtir. Bu hesabı yorumlarken bu sınırlılığı belirtmek akademik dürüstlük gerektirir.</p>

<h2>Eşdeğerlik Testi: "Fark Yok" Demek İçin</h2>
<p>p &gt; .05 bulmak, "iki grup arasında fark yoktur" anlamına <em>gelmez</em>; yalnızca bu veriyle fark kanıtlanamadığını gösterir. "Fark yoktur" iddiasını bilimsel olarak savunmak için Eşdeğerlik Testi (Equivalence Testing / TOST prosedürü) yapılmalıdır. Bu test, iki grubun ortalamaları arasındaki farkın önceden belirlenen "önemsiz fark" sınırları (equivalence bounds) içinde kaldığını istatistiksel olarak sınar. Bu yaklaşım, psikoloji, farmakoloji ve biyoeşdeğerlilik çalışmalarında giderek yaygınlaşmaktadır.</p>

<h2>Null Bulguların Yayın Değeri</h2>
<p>Yayın yanlılığı (publication bias) nedeniyle anlamsız bulgular, anlamlı bulgulara göre çok daha düşük oranda yayınlanmaktadır. Bu durum akademik yazın birikimini çarpıtmakta ve meta-analizlerin güvenilirliğini zedelemektedir. Son yıllarda "Registered Reports" formatı giderek yaygınlaşmaktadır: araştırmacılar veri toplamadan önce çalışmayı dergiye sunar; metodoloji kabul edilirse, sonuç ne olursa olsun (anlamlı ya da anlamsız) makale yayınlanır. Bu format özellikle null bulgular için önemli bir yayın kanalı açmaktadır.</p>
"""

# ID 23: R² düşük çıkınca (312 → 800+)
APPENDIX_23 = """
<h2>Düzeltilmiş R² (Adjusted R²): Neden Önemli?</h2>
<p>SPSS Model Summary tablosunda hem R² hem de Adjusted R² değeri görünür. R², modele her yeni değişken eklendiğinde —o değişken anlamsız bile olsa— artış gösterir. Adjusted R² ise değişken sayısını ve örneklem büyüklüğünü hesaba katarak bu yapay artışı düzeltir. Birden fazla bağımsız değişken içeren regresyon modellerinde Adjusted R² değerini raporlamak standart uygulamadır. Tek değişkenli (basit) regresyonda iki değer birbirine çok yakın olduğundan fark önemsizdir.</p>
<p>Tezde raporlama: <em>"Model, bağımsız değişkeni varyansın %12.6'sını açıklamış; düzeltilmiş R² ise %9.9 olarak hesaplanmıştır (R² = .126, adj. R² = .099)."</em></p>

<h2>Model Genellenebilirliği: Shrinkage (Küçülme) Sorunu</h2>
<p>Regresyon modeli, eğitildiği veri setine aşırı uyum (overfitting) gösterme eğilimindedir. R²'nin yeni bir örneklemde ne kadar küçüleceği "shrinkage" (küçülme) olarak bilinir. Büyük örneklemlerde bu sorun minimumdur; küçük örneklemlerde ise R² değeri gerçek açıklama gücünü abartıyor olabilir. Bu nedenle R² ile adj. R² arasındaki fark büyükse (örneğin .126 vs .050 gibi) modelin aşırı öğrenme olasılığı yüksektir. Cross-validation veya bölme-örneklem (split-sample) yaklaşımıyla modelin dış geçerliğini test etmek önerilir.</p>

<h2>Model Karşılaştırmasında AIC ve BIC</h2>
<p>Birden fazla regresyon modeli karşılaştırıldığında (örneğin 3 değişkenli model ile 5 değişkenli model) yalnızca R² kullanmak yanıltıcıdır; çünkü R² değişken eklendikçe artmaya devam eder. Bu durumda karmaşıklık cezası uygulayan <strong>Akaike Bilgi Kriteri (AIC)</strong> ve <strong>Bayes Bilgi Kriteri (BIC)</strong> kullanılır. Daha düşük AIC/BIC değeri daha iyi modeldir. SPSS'te standart olarak görünmez; R'ın <code>AIC()</code> ve <code>BIC()</code> fonksiyonları veya lm() çıktısı üzerinden hesaplanır.</p>

<h2>F Testi ile R² İlişkisi</h2>
<p>Model F testi anlamlı (p &lt; .05) olmasına rağmen R² düşük çıkabilir — bu birbiriyle çelişen bir durum değildir. F testi, modelin bir bütün olarak sıfır hipotezini (tüm katsayılar = 0) reddetme gücünü gösterirken R², bu modelin bağımlı değişkendeki gerçek değişimi ne ölçüde yakaladığını yansıtır. Büyük örneklemlerde küçük etki boyutları dahi anlamlı F değeri verebilir; bu nedenle F ve R² birlikte yorumlanmalıdır.</p>

<h2>Sık Yapılan Hatalar</h2>
<ol>
  <li><strong>"R² = 1.00 olmalı" beklentisi:</strong> Sosyal bilim araştırmalarında bu değer ulaşılabilir değildir. Beklenti alanına göre kalibre edilmelidir.</li>
  <li><strong>Adj. R² yerine R² raporlamak:</strong> Çok değişkenli modelde yalnızca R² raporlamak metodolojik eksiklik sayılır.</li>
  <li><strong>Negatif adj. R² görünce paniklemek:</strong> Bağımsız değişken gerçekten anlamsızsa adj. R² negatif çıkabilir; bu modelin hiç işe yaramadığının göstergesidir ve bağımsız değişken seçiminin gözden geçirilmesi gerekir.</li>
</ol>
"""

# ID 25: korelasyon yüksek ama anlamsız (341 → 800+)
APPENDIX_25 = """
<h2>Korelasyon İçin Güven Aralığı Raporlaması</h2>
<p>APA 7. baskı, korelasyon katsayısının yanında %95 güven aralığının da raporlanmasını önermektedir. SPSS korelasyon çıktısı doğrudan güven aralığı vermez; ancak şu yollarla hesaplanabilir: (1) Fisher'ın z-dönüşümü formülü ile manuel hesaplama. (2) R'ın <em>psych</em> paketindeki <code>corr.test()</code> fonksiyonu. (3) SPSS'te Bootstrap seçeneği aktif edilerek önyükleme güven aralıkları elde edilebilir (Analyze → Correlate → Bivariate → Bootstrap → Perform bootstrapping).</p>
<p>Raporlama: <em>"İki değişken arasında pozitif yönde orta düzeyde ilişki gözlemlenmiştir (r = .38, %95 CI [.12, .60], p = .012)."</em></p>

<h2>Kısmi Korelasyon: Üçüncü Değişkenin Etkisini Kontrol Etmek</h2>
<p>İki değişken arasındaki ilişki, her ikisinin de ortak bir üçüncü değişkenle ilgili olmasından kaynaklanıyor olabilir (confounding). Örneğin "dondurma satışları" ile "boğulma vakaları" arasında yüksek korelasyon gözlemlenebilir; çünkü ikisi de sıcak hava ile ilgilidir. Kısmi korelasyon (partial correlation), bir veya birden fazla değişkenin etkisi kontrol edilerek hesaplanan korelasyondur.</p>
<p>SPSS'te: Analyze → Correlate → Partial → iki değişkeni listele, kontrol değişkenini <em>Controlling for</em> kutusuna gir. Kısmi r değeri orijinal r'den belirgin biçimde düşüyorsa ilişki büyük ölçüde o üçüncü değişkenden kaynaklanıyordur.</p>

<h2>Spearman Rho Ne Zaman Pearson Yerine Kullanılır?</h2>
<p>Şu koşullarda Pearson yerine Spearman Rho tercih edilmelidir: (1) Değişkenlerden biri veya ikisi normal dağılıma uymuyor. (2) Veriler ordinal ölçekte (Likert ölçeği, sıralama). (3) Aykırı değer (outlier) sayısı fazla. (4) İlişki doğrusal değil, monotonik. Spearman, Pearson'a göre daha az güçlüdür (daha yüksek örneklem gerektirir); ancak dağılım varsayımlarını karşılamayan verilerde daha doğru bir tahmin sunar.</p>

<h2>Örneklem Büyüklüğü Planlaması: Ne Kadar Gerekiyor?</h2>
<p>Belirli bir korelasyonu tespit etmek için gereken minimum örneklem büyüklüğü G*Power ile hesaplanabilir: Tests → Correlation: Bivariate Normal → hesaplamak istediğiniz r, α = .05, güç = .80 parametrelerini girin. Örneğin r = .30'u tespit etmek için yaklaşık N = 84 kişi; r = .20 için yaklaşık N = 191 kişi gerekir. Bu hesabı veri toplamadan önce yapmak ve gerekli örnekleme ulaşmak metodolojik güvenilirliği önemli ölçüde artırır.</p>
"""

# ID 30: kaç anket doldurulmalı (324 → 800+)
APPENDIX_30 = """
<h2>G*Power ile Güç Analizi Nasıl Yapılır?</h2>
<p>G*Power, ücretsiz ve yaygın kabul gören bir güç analizi yazılımıdır (stats.uni-duesseldorf.de/statistic). Kullanım adımları:</p>
<ol>
  <li>Uygulamanızı indirip açın.</li>
  <li><em>Statistical test</em> menüsünden analiz türünüzü seçin (t-test, ANOVA, correlation vb.).</li>
  <li><em>Type of power analysis</em> olarak <strong>"A priori: Compute required sample size"</strong> seçin.</li>
  <li>Effect size (etki büyüklüğü), α (anlamlılık düzeyi, genellikle .05) ve Power (1 − β, genellikle .80) değerlerini girin.</li>
  <li><em>Calculate</em> tuşuna basın — gereken minimum örneklem büyüklüğü hesaplanır.</li>
</ol>
<p>Tezde raporlama: <em>"Araştırmanın örneklem büyüklüğü G*Power 3.1 yazılımıyla hesaplanmıştır. Orta etki büyüklüğü (d = 0.50), α = .05 ve güç = .80 parametreleri kullanılarak iki gruplu karşılaştırma için minimum 102 kişi (grup başına 51) belirlenmiştir."</em></p>

<h2>Analiz Türüne Göre G*Power Parametreleri</h2>
<table>
  <thead><tr><th>Analiz</th><th>Effect Size Göstergesi</th><th>Orta Etki Değeri</th><th>Yaklaşık N (.80 güç)</th></tr></thead>
  <tbody>
    <tr><td>Bağımsız t-Testi</td><td>Cohen's d</td><td>d = .50</td><td>128 (2 grup)</td></tr>
    <tr><td>ANOVA (3 grup)</td><td>Cohen's f</td><td>f = .25</td><td>159</td></tr>
    <tr><td>Korelasyon</td><td>r</td><td>r = .30</td><td>84</td></tr>
    <tr><td>Çoklu Regresyon (3 pred.)</td><td>f²</td><td>f² = .15</td><td>77</td></tr>
  </tbody>
</table>

<h2>Kayıp Katılımcı İçin Tampon Oran</h2>
<p>G*Power analizi minimum gerekli örneklemi verir; ancak gerçek veri toplamada eksik yanıt ve veri kalitesi sorunları yaşanabilir. Bu nedenle hesaplanan minimuma %10–20 tampon eklemek önerilir: 128 kişi gerekirken 145–155 kişiyle çalışmak planlanmalıdır. Özellikle çevrimiçi anketlerde %30–50 oranında "anket başlayıp bitirmeme" (drop-out) gözlemlenebileceği hesaba katılmalıdır. Tezde: <em>"Tahmini kayıp oranı (%15) göz önüne alınarak 150 kişiyle çalışılmış; 138'inden eksiksiz veri elde edilmiştir."</em></p>

<h2>Sonlu Evren Düzeltmesi</h2>
<p>Cochran formülü büyük evrenler için tasarlanmıştır (N &gt; 10.000). Eğer araştırmanızın evreni küçükse (örneğin belirli bir okulun 300 öğrencisi), hesaplanan n₀'ı sonlu evren düzeltme faktörüyle küçültebilirsiniz:</p>
<p><em>n = n₀ / (1 + (n₀ − 1) / N)</em></p>
<p>Örnek: n₀ = 384, N = 300 ise n = 384 / (1 + 383/300) = 384 / 2.28 ≈ 169 kişi. Bu düzeltme küçük evrenlerden gereksiz yere büyük örneklem almayı önler ve araştırma kaynaklarının verimli kullanımını sağlar.</p>
"""

SLUGS = [
    ('chatgpty-e-tezini-yazdirmak-bilim-midir-yoksa-akademinin-olum-sertifikasi-mi', APPENDIX_6),
    ('yayinla-ya-da-yok-ol-caginda-akademisyenin-sessiz-intihari-predatory-dergiler', APPENDIX_8),
    ('turkiyenin-akademik-uretimi-nereye-gidiyor-openalex-ve-tr-dizin-verileriyle', APPENDIX_9),
    ('tez-verilerini-google-driveda-tutmak-suc-mu-kvkk-gdpr', APPENDIX_11),
    ('anonimlestirme-yanilgisi-isimsiz-veri-setlerinden-kimlik-yeniden-nasil-insa-ediliyor', APPENDIX_12),
    ('saglikta-veri-krizi-turkiyede-klinik-arastirmalarin-verisi-neden-hep-kayip', APPENDIX_13),
    ('survival-analizi-101-kaplan-meier-cox-regresyon-ve-tedavi-etkili-mi', APPENDIX_14),
    ('enflasyon-verilerine-guveniyor-muyuz-tuik-enag-resmi-veri-tartismasi', APPENDIX_15),
    ('normallik-testi-saglanmazsa-hangi-test-kullanilir', APPENDIX_17),
    ('bagimsiz-mi-bagimli-mi-t-testi-fark-ne-zaman-onemli', APPENDIX_18),
    ('ki-kare-mi-lojistik-regresyon-mu-ikisinin-farki-ne', APPENDIX_20),
    ('p-degeri-0-05-ten-buyuk-cikti-tezime-ne-yazarim', APPENDIX_21),
    ('r-kare-dusuk-cikinca-regresyon-modeli-gecersiz-mi', APPENDIX_23),
    ('korelasyon-yuksek-ama-anlamsiz-bu-nasil-olur', APPENDIX_25),
    ('tez-icin-kac-anket-doldurulmali-orneklem-buyuklugu-nasil-hesaplanir', APPENDIX_30),
]


def expand_batch2(apps, schema_editor):
    import re
    BlogPost = apps.get_model('forum', 'BlogPost')
    ok = fail = 0
    for slug, appendix in SLUGS:
        try:
            post = BlogPost.objects.get(slug=slug)
        except BlogPost.DoesNotExist:
            print(f'  UYARI: {slug[:50]} bulunamadı')
            continue
        content = post.content
        hr_pos = content.rfind('<hr>')
        post.content = (content[:hr_pos] + appendix + content[hr_pos:]) if hr_pos != -1 else content + appendix
        post.save()
        text = re.sub(r'<[^>]+>', ' ', post.content)
        wc = len(text.split())
        status = '✓' if wc >= 800 else '✗'
        if wc >= 800:
            ok += 1
        else:
            fail += 1
        print(f'  {status} {wc:4d} kelime | {slug[:50]}')
    print(f'\n  Başarılı: {ok} | Eksik: {fail}')


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0133_finalize_spss_alt_post'),
    ]

    operations = [
        migrations.RunPython(expand_batch2, migrations.RunPython.noop),
    ]
