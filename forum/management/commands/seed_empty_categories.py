import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from forum.models import Category, Topic, Post, Profile


SEED_USERS = [
    ('Ekonometrist', 'Expert', 'Doç. Dr. Ekonometri'),
    ('Psikoloji_Tez', 'Free', 'Doktora Öğrencisi'),
    ('Sosyal_Veri', 'Free', 'Sosyal Bilimci'),
    ('Yonetim_Aras', 'Premium', 'İşletme Araştırmacısı'),
    ('SaglikIst', 'Free', 'Sağlık İstatistikçisi'),
    ('Klinik_Aras', 'Expert', 'Dr. Klinik Araştırmacı'),
    ('VeriBilimci_A', 'Premium', 'Data Scientist'),
    ('Arastirmaci_X', 'Premium', 'Akademisyen'),
    ('AkademikKariyer', 'Free', 'Doktora Adayı'),
    ('AnalizBot', 'Expert', 'AI Asistan'),
    ('Muhendislik_R', 'Premium', 'Makine Mühendisi'),
    ('AI_Ogrenci', 'Free', 'YL Öğrencisi'),
    ('Literatur_Tarama', 'Expert', 'Bibliyometri Uzmanı'),
    ('VeriGorselci', 'Expert', 'Data Visualization Uzmanı'),
]

CONTENT_BY_SLUG = {
    'ekonometrik-araclar': [
        {
            'subject': "EViews ile VAR modeli kurma adımları",
            'starter': 'Ekonometrist',
            'message': "Makroekonomik değişkenler arasındaki ilişkiyi modellemek için VAR kurmak istiyorum. Hangi adımları izlemeliyim?",
            'answer': "Önce durağanlık testlerini (ADF/PP) yap. Tüm değişkenler I(1) ise VAR yerine VECM düşün. Uygun gecikme uzunluğunu AIC/SC kriteriyle seç, sonra Granger nedenselliği ve etki-tepki fonksiyonlarını yorumla.",
        },
        {
            'subject': "Stata'da GMM tahmini ne zaman kullanılır?",
            'starter': 'Yonetim_Aras',
            'message': "Dinamik panel veri modelimde endojenlik sorunu var. GMM mi, IV mi tercih etmeliyim?",
            'answer': "Arellano-Bond GMM (xtabond2), T küçük N büyükse idealdir. IV tek dışsal araç varken çalışır; GMM ise birden fazla aracı etkin kullanır. Sargan/Hansen testi ile araçların geçerliliğini mutlaka kontrol et.",
        },
        {
            'subject': "Eş-bütünleşme testi yorumlaması",
            'starter': 'Ekonometrist',
            'message': "Johansen testi sonucunda 'r=1' çıktı. Bu ne anlama geliyor?",
            'answer': "r=1, değişkenler arasında bir adet uzun dönem denge ilişkisi olduğunu gösterir. VECM kurarak kısa ve uzun dönem dinamiklerini ayrı ayrı tahmin edebilirsin.",
        },
    ],
    'makale-destegi': [
        {
            'subject': "Q1 dergiye gönderilecek makalede metodoloji bölümü nasıl yazılır?",
            'starter': 'AkademikKariyer',
            'message': "Metodoloji kısımda hangi bilgilerin mutlaka yer alması gerekiyor?",
            'answer': "Örneklem seçim yöntemi, örneklem büyüklüğü gerekçesi, veri toplama aracı (geçerlilik/güvenilirlik kanıtlarıyla), analiz yazılımı ve sürümü ile etik kurul onay bilgisi mutlaka yer almalı.",
        },
        {
            'subject': "Hakem yorumlarına nasıl yanıt verilir?",
            'starter': 'Arastirmaci_X',
            'message': "3 hakemin her birinden farklı eleştiri geldi. Revision sürecini nasıl yönetmeliyim?",
            'answer': "Her eleştiriyi ayrı bir satır/madde olarak sırala, yanıt mektubunda 'Hakem 1, Yorum 3' formatını kullan. Katılmadığın yorumlara da gerekçeli ve nazikçe yanıt ver; hakemlere saygısız görünmekten kaçın.",
        },
        {
            'subject': "Benzerlik raporu (intihal) yüzdesini düşürme yöntemleri",
            'starter': 'Psikoloji_Tez',
            'message': "Tez benzerlik oranım %22 çıktı. Hangi kısımları düzeltmeliyim?",
            'answer': "Referans listesi ve alıntılar genellikle hariç tutulabilir. Yüksek benzerlik gösteren paragrafları parafraze et. Kaynakça bölümünü 'hariç tut' listesine ekle. Asıl sorun metodoloji veya teori kısmındaki kelimesi kelimesine çevirilerden kaynaklanıyor olabilir.",
        },
    ],
    'hipotez-testleri': [
        {
            'subject': "Tek örneklem t-testi mi, bağımsız örneklem t-testi mi?",
            'starter': 'SaglikIst',
            'message': "İki farklı grubun ortalamasını karşılaştırıyorum. Hangisini seçmeliyim?",
            'answer': "İki ayrı grubun ortalamasını karşılaştırıyorsan Bağımsız Örneklem t-testi kullan. Aynı kişilerin iki farklı zamandaki ölçümlerini karşılaştıracaksan Bağımlı Örneklem (Eşleştirilmiş) t-testi gerekir.",
        },
        {
            'subject': "Ki-kare testi için beklenen frekans şartı nedir?",
            'starter': 'Klinik_Aras',
            'message': "SPSS'de 'expected count less than 5' uyarısı alıyorum. Ne yapmalıyım?",
            'answer': "Ki-kare için beklenen hücre frekanslarının en az %80'i 5'in üzerinde olmalı, hiçbiri 1'den küçük olmamalı. Bu şart sağlanmıyorsa Fisher's Exact Test kullan veya kategorileri birleştir.",
        },
        {
            'subject': "Normallik varsayımı sağlanmıyorsa ne yapılır?",
            'starter': 'Sosyal_Veri',
            'message': "Shapiro-Wilk p<0.05 çıktı. Parametrik test yapamaz mıyım?",
            'answer': "n>30 ise Merkezi Limit Teoremi'ne dayanarak parametrik testleri kullanabilirsin. n küçükse Mann-Whitney U (bağımsız) veya Wilcoxon (bağımlı) gibi parametrik olmayan alternatiflere geç.",
        },
    ],
    'olcek-gelistirme': [
        {
            'subject': "Likert ölçeği mi, Likert tipi ölçek mi?",
            'starter': 'Psikoloji_Tez',
            'message': "Tezimde geliştirdiğim ölçeği nasıl adlandırmalıyım?",
            'answer': "Gerçek Likert ölçeği toplam puan alınabilen, maddelerin akümülatif özellik taşıdığı bir yapıdır. Çoğu araştırmada kullanılan 5'li cevap formatı aslında 'Likert tipi' ya da 'Likert formatında' diye anılmalıdır.",
        },
        {
            'subject': "EFA'dan sonra CFA yapmak şart mı?",
            'starter': 'Yonetim_Aras',
            'message': "Sadece EFA ile ölçek geçerliliği sağlanmış sayılır mı?",
            'answer': "EFA yapıyı keşfeder, CFA onu doğrular. Güçlü bir geçerlilik kanıtı için her ikisi de gereklidir. Aynı örneklem üzerinde yapma; örneği ikiye böl veya farklı bir örneklem kullan.",
        },
        {
            'subject': "Kapsam geçerliliği (content validity) için kaç uzman yeterli?",
            'starter': 'AkademikKariyer',
            'message': "CVR hesaplaması için uzman paneli oluştururken kaç kişiyle çalışmalıyım?",
            'answer': "Lawshe'nin tablosuna göre %95 güven için en az 10 uzman önerilir. 5-7 uzmanla da çalışılabilir ama eşik CVR değeri yükselir. Uzmanların alan yazarına uygunluğu sayıdan önemlidir.",
        },
    ],
    'panel-veri-analizi': [
        {
            'subject': "Dengeli (balanced) ve dengesiz (unbalanced) panel farkı",
            'starter': 'Ekonometrist',
            'message': "Bazı gözlemlerim eksik. Dengeli panel şartı şart mı?",
            'answer': "Çoğu panel veri tahmincisi (FE, RE, GMM) dengesiz panelle de çalışır. Ancak dengesiz olmanın 'rastgele' mı yoksa 'seçim yanlılığı' nedeniyle mi olduğunu kontrol et; ikincisi tahminleri sapkınlaştırır.",
        },
        {
            'subject': "Hausman testi sonucu anlamsız çıkıyor",
            'starter': 'Yonetim_Aras',
            'message': "p=0.43 çıktı. Testin sonuçsuz kalması normal mi?",
            'answer': "p>0.05 ise RE etkin ve tutarlıdır; FE zorunlu değil. Ancak teorik gerekçen FE'yi işaret ediyorsa robust Hausman veya Mundlak yaklaşımını tercih edebilirsin.",
        },
        {
            'subject': "Panel veride otokorelasyon testi nasıl yapılır?",
            'starter': 'Ekonometrist',
            'message': "Wooldridge testi mi, Breusch-Godfrey mi kullanmalıyım?",
            'answer': "Panel veri için Wooldridge (2002) testi önerilir; Stata'da xtserial komutuyla çalışır. H0: Birinci dereceden otokorelasyon yok. p<0.05 çıkarsa clustered standart hatalar veya AR(1) disturbance'lı model kullan.",
        },
    ],
    'zaman-serisi-analizi': [
        {
            'subject': "ADF testi durağanlık için yeterli mi?",
            'starter': 'Ekonometrist',
            'message': "Tek bir test mi, yoksa birden fazla test mi kullanmalıyım?",
            'answer': "ADF tek başına yeterli değil. PP (Phillips-Perron), KPSS ve yapısal kırılmalı testlerle (Zivot-Andrews) teyit et. Testler çelişirse farklar hakkında yorumlayıcı bilgi ver.",
        },
        {
            'subject': "ARIMA model seçiminde ACF/PACF nasıl yorumlanır?",
            'starter': 'VeriBilimci_A',
            'message': "Grafiğe bakınca hangi p ve q değerlerini seçmeliyim?",
            'answer': "ACF geometrik düşüyorsa AR, PACF geometrik düşüyorsa MA süreci işareti. PACF'de k gecikmede sert kesinti varsa AR(k), ACF'de q gecikmede sert kesinti varsa MA(q) modeli dene. Sonuçta AIC/BIC ile en iyi modeli seç.",
        },
        {
            'subject': "Mevsimselliği modellemek için SARIMA mı, X-13 mi?",
            'starter': 'Ekonometrist',
            'message': "Aylık satış verisinde belirgin mevsimsel örüntü var.",
            'answer': "Akademik çalışma için SARIMA(p,d,q)(P,D,Q)s yeterlidir. Resmi istatistik kurumları (TÜİK gibi) X-13 ARIMA-SEATS kullanır. İkisi de R veya Python ile uygulanabilir.",
        },
    ],
    'veri-gorsellestirme': [
        {
            'subject': "Akademik makale için renk paleti seçimi",
            'starter': 'VeriGorselci',
            'message': "Siyah-beyaz baskıda da okunabilir grafik nasıl yapılır?",
            'answer': "ColorBrewer paletlerini kullan; özellikle 'print-friendly' seçeneğini işaretle. Renk körü okuyucular için RColorBrewer'da 'colorblind-safe' paleti tercih et. Çizgi grafiklerinde farklı kesik türleri ekle.",
        },
        {
            'subject': "Kutu grafik (boxplot) mi, keman grafik (violin plot) mi?",
            'starter': 'VeriBilimci_A',
            'message': "Dağılımı göstermek için hangisi daha bilgilendirici?",
            'answer': "Violin plot dağılımın tamamını gösterir; unimodal/bimodal yapıyı görünür kılar. Boxplot medyan ve aykırı değerleri daha net öne çıkarır. Mümkünse her ikisini birleştiren 'raincloud plot' tercih edilebilir.",
        },
        {
            'subject': "Power BI vs Tableau: akademik sunum için hangisi?",
            'starter': 'VeriGorselci',
            'message': "Tez savunmasında interaktif grafik sunmak istiyorum.",
            'answer': "Tableau Public ücretsiz ve web'de paylaşılabilir; tez için iyi seçenek. Power BI'ın ücretsiz masaüstü sürümü de yeterlidir ama yayımlamak için Microsoft hesabı gerekir. Her iki araç da .pbix/.twbx formatında portföy oluşturmana imkân tanır.",
        },
    ],
    'g-power-analizi': [
        {
            'subject': "G*Power ile örneklem büyüklüğü nasıl hesaplanır?",
            'starter': 'SaglikIst',
            'message': "Bağımsız örneklem t-testi için örneklem büyüklüğü hesaplamak istiyorum.",
            'answer': "G*Power'da: Test family = t tests, Statistical test = Means: Difference between two independent means. Effect size d için literatür ortalaması 0.5 (orta), α = 0.05, Power = 0.80 gir. Çıkan n her grup için ayrı ayrı uygulanmalı.",
        },
        {
            'subject': "Etki büyüklüğü (effect size) nasıl yorumlanır?",
            'starter': 'Klinik_Aras',
            'message': "Cohen's d = 0.35 çıktı. Bu küçük mü, orta mı?",
            'answer': "Cohen (1988) kuralına göre: d<0.2 ihmal edilebilir, 0.2≤d<0.5 küçük, 0.5≤d<0.8 orta, d≥0.8 büyük etki. d=0.35 küçük-orta arası sayılır; klinik önem ayrıca değerlendirilmeli.",
        },
        {
            'subject': "Yapısal eşitlik modeli için örneklem büyüklüğü ne olmalı?",
            'starter': 'Psikoloji_Tez',
            'message': "SEM için minimum örneklem konusunda çelişkili bilgiler var.",
            'answer': "Kline (2016): gözlenen değişken başına 10-20 katılımcı önerir. MacCallum'un kuralı: basit modelde 200, karmaşıkta 400+. G*Power yerine WebPower veya pwrSEM paketi daha uygun SEM güç analizi yapar.",
        },
    ],
    'tez-onerisi-destegi': [
        {
            'subject': "Tez önerisi savunmasında sıkça sorulan sorular",
            'starter': 'AkademikKariyer',
            'message': "Jüri hangi konulara özellikle takılıyor?",
            'answer': "En sık sorulanlar: 'Neden bu yöntemi seçtiniz?', 'Örnekleminiz temsil edici mi?', 'Bu çalışmanın özgün katkısı nedir?', 'Literatür boşluğu gerçekten var mı?' Bu soruları 2-3 cümleyle yanıtlayabilmek için hazırlık yap.",
        },
        {
            'subject': "Araştırma sorusu ile hipotez arasındaki fark",
            'starter': 'Psikoloji_Tez',
            'message': "Nitel çalışmamda hipotez yazmam gerekiyor mu?",
            'answer': "Nicel araştırmalarda hipotez (H1, H0) beklenir. Nitel araştırmalarda 'araştırma sorusu' kullanılır; hipotez genellikle uygun değildir çünkü nitel çalışma keşifsel nitelik taşır.",
        },
        {
            'subject': "Pilot çalışma zorunlu mu, nasıl rapor edilir?",
            'starter': 'Yonetim_Aras',
            'message': "30 kişiyle pilot yaptım. Teze nasıl dahil edeyim?",
            'answer': "Pilot çalışmayı Metodoloji bölümünde kısa bir alt başlık olarak sun. Ölçek güvenilirliği (Cronbach α), öngörülemeyen sorunlar ve yapılan düzeltmeleri açıkla. Ayrı bir bölüm açman gerekmez.",
        },
    ],
    'etik-kurul-basvurusu': [
        {
            'subject': "Hangi araştırmalar etik kurul gerektirmez?",
            'starter': 'AkademikKariyer',
            'message': "Kamuya açık veri kullanıyorum. Yine de başvuru yapmam gerekiyor mu?",
            'answer': "Tamamen kamuya açık, anonimleştirilmiş ikincil veriler genellikle muafiyet kapsamındadır. Ancak üniversitenin etik yönergesini kontrol et; bazı kurumlar ikincil veri için bile onay formu istiyor.",
        },
        {
            'subject': "Etik kurul başvuru formu nasıl doldurulur?",
            'starter': 'SaglikIst',
            'message': "İlk kez başvuruyorum, en çok dikkat edilmesi gereken bölümler hangileri?",
            'answer': "'Araştırmanın amacı', 'katılımcılara yönelik riskler', 'gizlilik ve anonimlik tedbirleri' ile 'aydınlatılmış onam süreci' en kritik bölümlerdir. Onam formunu ek olarak sisteme yüklemeyi unutma.",
        },
        {
            'subject': "Etik kurul onayı alındıktan sonra değişiklik yapılabilir mi?",
            'starter': 'Klinik_Aras',
            'message': "Örneklem büyüklüğümü artırmam gerekti. Revizyon mu başvurusunu mu açmalıyım?",
            'answer': "Evet, onaylı protokolde yapılan değişiklikler için revizyon (amendment) başvurusu açılmalı. Örneklem büyüklüğündeki artış, yeni risk doğursa da doğurmazsa da bildirilmesi etik zorunluluktur.",
        },
    ],
    'yayin-sureci-destegi': [
        {
            'subject': "Dergi seçiminde hangi kriterlere bakılmalı?",
            'starter': 'Arastirmaci_X',
            'message': "WoS/Scopus listesinde yüzlerce dergi var. Nasıl eleme yapayım?",
            'answer': "Önce Q değerini (SJR/JCR) ve etki faktörünü kontrol et. Sonra derginin kapsam alanının çalışmanla örtüşüp örtüşmediğini son sayıdaki makalelere bakarak doğrula. Son olarak ortalama değerlendirme süresine bak; bazı dergiler 18-24 ay alıyor.",
        },
        {
            'subject': "Cover letter (kapak mektubu) nasıl yazılır?",
            'starter': 'AkademikKariyer',
            'message': "Editöre yazacağım mektup ne kadar uzun olmalı, ne içermeli?",
            'answer': "Üç paragraf yeterlidir: (1) Çalışmanın başlığı ve temel bulgusu, (2) Bu dergiye neden uygun olduğu, (3) Çıkar çatışması/etik onay bildirimi. Yarım sayfayı geçmemeli; editörü etkilemek için abartma.",
        },
        {
            'subject': "Open Access yayın ücretleri (APC) nasıl karşılanır?",
            'starter': 'YayinHedefi',
            'message': "Q1 derginin APC'si 3000 EUR. Destek kaynağı var mı?",
            'answer': "TÜBİTAK 2218 ve 2219 programları yayın desteği sunuyor. Üniversitenin araştırma fonu ve kütüphane OA anlaşmalarını kontrol et. DEAL, Springer Compact gibi transformatif anlaşmalar üzerinden ücretsiz OA mümkün olabilir.",
        },
    ],
    'referans-programi': [
        {
            'subject': "Zotero mi, Mendeley mi kullanmalıyım?",
            'starter': 'AkademikKariyer',
            'message': "İkisi arasındaki temel farklar neler?",
            'answer': "Zotero açık kaynaklı, daha özgür ve tarayıcı entegrasyonu güçlü. Mendeley Elsevier'e ait, PDF okuyucusu daha gelişmiş. Uzun vadeli bağımsızlık isteyenler Zotero, PDF annotasyon ağırlıklı çalışanlar Mendeley tercih ediyor.",
        },
        {
            'subject': "Word içinde referans otomatik numaralandırma bozuluyor",
            'starter': 'Psikoloji_Tez',
            'message': "Zotero eklentisi bazen kayıyor ya da numara atlıyor. Çözüm nedir?",
            'answer': "Word'de Zotero sekmesinden 'Refresh' düğmesine bas. Sorun devam ederse 'Document Preferences > Store Citations' ayarını 'Bookmarks' yerine 'Fields' olarak değiştir. Gerekirse tüm alanları (Fields) yenile.",
        },
        {
            'subject': "Farklı stillerle atıf yapma: APA 7 vs Vancouver",
            'starter': 'SaglikIst',
            'message': "Tıp dergisi Vancouver istiyor ama benim tezim APA kullanıyor. İkisini aynı anda tutmak mümkün mü?",
            'answer': "Zotero/Mendeley'de her belge için ayrı stil seçebilirsin. Tez için APA 7, makale için Vancouver stilini ayrı projeler altında yönet. Kaynakları aynı kütüphaneden kullanırsın, stil otomatik değişir.",
        },
    ],
    'akademik-lounge': [
        {
            'subject': "Akademik kariyer mi, sektör mü? Doktora sonrası karar",
            'starter': 'AkademikKariyer',
            'message': "Doktoram bitmek üzere. Akademide kalmak mı, sektöre geçmek mi daha mantıklı?",
            'answer': "İkisi de geçerli. Akademi: özgür araştırma, öğretme, ama uzun ve belirsiz kariyer yolu. Sektör: daha yüksek başlangıç maaşı, hız, ama araştırma özgürlüğü kısıtlı. 3-5 yıllık bir sektör deneyimi sonrası akademiye dönüş de mümkün.",
        },
        {
            'subject': "Araştırma verimi artırmak için kullandığınız teknikler",
            'starter': 'Literatur_Tarama',
            'message': "Literatür taramasında kayboluyorum. Odaklanmayı nasıl sağlıyorsunuz?",
            'answer': "PRISMA akış diyagramı çizerek başla; dahil/dışlama kriterlerini önceden belirle. Sistematik tarama için PICO veya SPIDER çerçevesini kullan. Zotero koleksiyonu + etiket sistemiyle yönet.",
        },
        {
            'subject': "Uluslararası konferanslara katılım nasıl finanse edilir?",
            'starter': 'AI_Ogrenci',
            'message': "Yurt dışında sunum yapma fırsatım var ama bütçem yok.",
            'answer': "TÜBİTAK 2224-A yurt dışı kongre desteği başvuru sürecini kontrol et. Üniversitenin BAP birimi ve ilgili anabilim dalı da kaynak sağlayabilir. Konferansın 'travel grant' programını da incele; çoğu büyük konferansta mevcuttur.",
        },
    ],
    'betimsel-kesifsel': [
        {
            'subject': "Tanımlayıcı istatistiklerde hangi değerleri raporlamak zorunlu?",
            'starter': 'SaglikIst',
            'message': "Makale için standart bir tablo formatı var mı?",
            'answer': "Sürekli değişkenler için: n, ortalama ± SS veya medyan (Q1–Q3). Kategorik için: n (%). Normal dağılım yoksa medyan/IQR tercih et. APA 7'de tabloların başlığı üstte, notlar altta yer almalı.",
        },
        {
            'subject': "Keşifsel veri analizinde (EDA) nelere bakılır?",
            'starter': 'VeriBilimci_A',
            'message': "Modellemeye geçmeden önce hangi grafiklere mutlaka bakmalıyım?",
            'answer': "Histogram (dağılım şekli), boxplot (aykırı değerler), korelasyon ısı haritası (çoklu doğrusal bağlantı riski), scatter plot matrisi (doğrusallık). Eksik veri için missingno kütüphanesini kullan.",
        },
        {
            'subject': "Standart sapma mı, standart hata mı raporlanmalı?",
            'starter': 'Klinik_Aras',
            'message': "Bazı makalelerde SS, bazılarında SH kullanılıyor. Farkı nedir?",
            'answer': "SS örneklemdeki değişkenliği, SH ise örneklem ortalamasının güvenilirliğini gösterir. Betimsel istatistiklerde SS, ortalama tahminin kesinliğini göstermek istediğinde SH kullanılır. Grafiklerde hata çubukları neyi temsil ettiğini mutlaka belirt.",
        },
    ],
    'karsilastirma-testleri': [
        {
            'subject': "ANOVA sonrası post-hoc testi hangisi?",
            'starter': 'SaglikIst',
            'message': "3 grup arasında fark çıktı. Hangi çiftler farklı, nasıl bulurum?",
            'answer': "Varyanslar eşitse Tukey HSD tercih edilir. Eşit değilse Games-Howell kullan. Kontrol grubu varsa ve sadece onunla karşılaştırma yapılacaksa Dunnett testi uygun.",
        },
        {
            'subject': "Kruskal-Wallis ne zaman ANOVA'ya alternatif olur?",
            'starter': 'Psikoloji_Tez',
            'message': "Normallik varsayımı sağlanmıyor. Otomatik olarak Kruskal-Wallis'e mi geçeyim?",
            'answer': "Örneklem büyükse (n>30 her grupta) ANOVA sağlamlıdır. Küçük örneklemde veya sıralı (ordinal) veri varsa Kruskal-Wallis uygundur. Post-hoc olarak Dunn testi kullan; Bonferroni düzeltmesiyle.",
        },
        {
            'subject': "Tekrarlı ölçümler ANOVA'da sferlik varsayımı",
            'starter': 'Yonetim_Aras',
            'message': "Mauchly testi p<0.05 çıktı. Ne yapmalıyım?",
            'answer': "Sferlik ihlali varsa Greenhouse-Geisser veya Huynh-Feldt düzeltmesiyle F testini raporla. Hangi ε değerini seçeceğini ikisi arasında ε < 0.75 ise Greenhouse-Geisser, büyükse Huynh-Feldt önerilir.",
        },
    ],
    'boyut-indirgeme': [
        {
            'subject': "Kaç faktör çıkarmalıyım? Kaiser kriterine güvenebilir miyim?",
            'starter': 'Psikoloji_Tez',
            'message': "EFA'da özdeğer (eigenvalue) > 1 olan 5 faktör çıktı ama scree plot 3'te kırılıyor.",
            'answer': "Kaiser kriteri aşırı faktör çıkarma eğilimindedir. Scree plot daha tutarlı ama öznel. Paralel analiz (Horn, 1965) en güvenilir yöntemdir; SPSS'de syntax veya R'da psych paketi ile yapılabilir.",
        },
        {
            'subject': "PCA ile EFA arasındaki fark nedir?",
            'starter': 'VeriBilimci_A',
            'message': "İkisi de boyut indirgiyor ama ne zaman hangisini kullanayım?",
            'answer': "PCA matematiksel olarak varyansı maksimize eden bileşenler arar; teorik yapı varsaymaz. EFA gizli (latent) faktörlerin gözlenen değişkenleri açıkladığını varsayar. Ölçek geliştirmede EFA, veri özetlemede PCA kullanılır.",
        },
        {
            'subject': "t-SNE vs UMAP: hangisi daha iyi görselleştirme sağlar?",
            'starter': 'VeriBilimci_A',
            'message': "Yüksek boyutlu metin verisini 2 boyuta indirgemek istiyorum.",
            'answer': "t-SNE küme yapısını iyi görselleştirir ama büyük veride yavaş. UMAP daha hızlı, küresel yapıyı daha iyi korur. Makale için ikisini de sun ve parametrelerin değiştikçe sonuçların nasıl değiştiğini göster.",
        },
    ],
    'yapisal-esitlik': [
        {
            'subject': "AMOS'ta Confirmatory Factor Analysis adımları",
            'starter': 'Psikology_Tez',
            'message': "İlk kez CFA yapıyorum, hangi uyum indekslerine bakmalıyım?",
            'answer': "Minimum raporlanması gerekenler: χ²/df (<3), CFI (>0.90, ideal >0.95), RMSEA (<0.08, ideal <0.05), SRMR (<0.08). Modifikasyon indislerine bakarak MI>10 olan kovaryansları dikkatli ekle; teorik gerekçe olmalı.",
        },
        {
            'subject': "Yakınsak ve ayrışık geçerlilik nasıl test edilir?",
            'starter': 'Yonetim_Aras',
            'message': "AVE ve CR değerleri ne olmalı?",
            'answer': "Yakınsak geçerlilik için AVE > 0.50 ve CR > 0.70 beklenir. Ayrışık geçerlilik için √AVE her faktörde, o faktörün diğerleriyle korelasyonundan büyük olmalı (Fornell-Larcker kriteri).",
        },
        {
            'subject': "SmartPLS ile AMOS arasında nasıl seçim yapılır?",
            'starter': 'AkademikKariyer',
            'message': "Danışmanım ikisi hakkında da konuşuyor. Farkları nelerdir?",
            'answer': "AMOS/LISREL (CB-SEM): normallik varsayımı gerektirir, reflektif modeller için idealdir. SmartPLS (PB-SEM): dağılımdan bağımsız, küçük örneklemde çalışır, formative ve reflective karışımına izin verir. Keşifsel çalışmalarda SmartPLS, doğrulayıcı/teorik çalışmalarda CB-SEM önerilir.",
        },
    ],
    'yapay-zeka-modellemeleri': [
        {
            'subject': "Sosyal bilimler tezinde makine öğrenmesi modeli kullanmak",
            'starter': 'AI_Ogrenci',
            'message': "İşletme tezimde Random Forest ile sınıflandırma yapacağım. Hakem bunu nasıl karşılar?",
            'answer': "ML yöntemleri sosyal bilimlerde giderek kabul görüyor. Ancak model yorumlanabilirliği (explainability) çok önemli. SHAP değerleri veya özellik önem grafikleriyle 'kara kutu' eleştirisine yanıt ver.",
        },
        {
            'subject': "Akademik metin sınıflandırmada BERT vs BoW",
            'starter': 'Arastirmaci_X',
            'message': "Dergi makalelerini alana göre sınıflandırmak istiyorum. Hangisi daha iyi?",
            'answer': "BERT bağlam anlayışıyla çok daha güçlü ama hesaplama maliyeti yüksek. Eğer verin sınırlıysa BERTurk veya mBERT ile transfer learning dene. Küçük veri setinde (< 1000 örnek) klasik TF-IDF + SVM hâlâ rekabetçi.",
        },
        {
            'subject': "Yapay zeka çıktısını akademik çalışmada kullanmak etik mi?",
            'starter': 'AkademikKariyer',
            'message': "GPT ile oluşturduğum metin tezde kullanılabilir mi?",
            'answer': "Çoğu üniversite ve dergi AI kullanımının şeffaf biçimde beyan edilmesini istiyor. Veri analizi veya kod yazımında araç olarak kullanmak genellikle kabul görüyor, ancak ham metin üretimi için sorumluluk yazarındır. Üniversitenin AI politikasını kontrol et.",
        },
    ],
    'smartpls': [
        {
            'subject': "SmartPLS'de outer loading ve outer weight farkı",
            'starter': 'Yonetim_Aras',
            'message': "Reflective modelde hangisini raporlamalıyım?",
            'answer': "Reflective (yansıtıcı) modellerde outer loading raporlanır; 0.70 ve üzeri kabul edilir. Formative (biçimlendirici) modellerde outer weight kullanılır ve negatif değerler de anlamlı olabilir.",
        },
        {
            'subject': "Bootstrapping kaç tekrarla yapılmalı?",
            'starter': 'Psikoloji_Tez',
            'message': "Varsayılan 500 tekrar yeterli mi?",
            'answer': "Hair vd. (2017) minimum 5000 bootstrapping tekrarı önermektedir. SmartPLS 4'te varsayılan zaten 5000'dir. Bias-corrected and accelerated (BCa) bootstrap tercih edilmeli.",
        },
        {
            'subject': "Common Method Bias (CMB) SmartPLS'de nasıl test edilir?",
            'starter': 'Yonetim_Aras',
            'message': "Tüm verim anket yoluyla toplandı. Ortak yöntem yanlılığı sorun yaratır mı?",
            'answer': "Harman's single factor test yaparak açıklanan varyansın %50'nin altında olup olmadığını kontrol et. Daha güçlü yöntem: HTMT oranı < 0.90 ve marker değişkeni kullanımı. Structural model sonuçlarına CMB düzeltmesi ekle.",
        },
    ],
}


class Command(BaseCommand):
    help = 'Boş kalan forum kategorilerine seed içerik ekler (mevcut verilere dokunmaz)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Boş kategorilere seed içerik ekleniyor...'))

        # Kullanıcıları oluştur/al
        users = {}
        for username, acc_type, title in SEED_USERS:
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password('pass1234')
                user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.account_type = acc_type
            profile.title = title
            profile.save()
            users[username] = user

        analizbot = users.get('AnalizBot')
        added_topics = 0
        added_posts = 0

        for category in Category.objects.all():
            if category.topics.count() > 0:
                continue

            topics_data = CONTENT_BY_SLUG.get(category.slug)
            if not topics_data:
                self.stdout.write(self.style.WARNING(f'  ⚠ İçerik tanımsız: {category.title} ({category.slug})'))
                continue

            self.stdout.write(f'  → {category.title} kategorisine içerik ekleniyor...')
            for topic_data in topics_data:
                starter = users.get(topic_data['starter'], analizbot)
                topic = Topic.objects.create(
                    category=category,
                    subject=topic_data['subject'],
                    starter=starter,
                    views=random.randint(200, 1500),
                )
                added_topics += 1

                Post.objects.create(
                    topic=topic,
                    created_by=starter,
                    message=f"Merhaba,\n\n{topic_data['message']}\n\nTeşekkürler.",
                )
                added_posts += 1

                Post.objects.create(
                    topic=topic,
                    created_by=analizbot,
                    message=f"Merhaba,\n\n{topic_data['answer']}\n\nBaşarılar dilerim!",
                    is_best_answer=True,
                )
                added_posts += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Tamamlandı: {added_topics} konu, {added_posts} gönderi eklendi.\n'
            f'   Toplam konu: {Topic.objects.count()} | Toplam gönderi: {Post.objects.count()}'
        ))
