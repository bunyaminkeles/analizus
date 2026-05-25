SEO_CONTENT = {

    'ttesti': {
        'intro': (
            'T-testi, iki grup ya da ölçüm seti arasındaki ortalama farkın istatistiksel olarak '
            'anlamlı olup olmadığını belirleyen parametrik bir hipotez testidir. Sosyal bilimler, '
            'tıp, eğitim ve mühendislik araştırmalarında en sık başvurulan analizlerden biridir. '
            'Üç temel türü vardır: bağımsız örneklem t-testi iki ayrı grubu karşılaştırır; '
            'bağımlı (eşleştirilmiş) t-testi aynı gruba iki farklı zamanda yapılan ölçümleri '
            'analiz eder; tek örneklem t-testi ise bir grubun ortalamasını bilinen teorik bir '
            'değerle sınar.'
        ),
        'when_to_use': (
            'Bağımsız örneklem t-testini; iki farklı ve birbirinden bağımsız grubu '
            '(deney/kontrol, erkek/kadın) sürekli bir değişken üzerinden karşılaştırmak '
            'istediğinizde kullanın. Bağımlı t-testini; öntest-sontest tasarımı veya '
            'eşleştirilmiş katılımcı çiftleri söz konusu olduğunda tercih edin. '
            'Veri normal dağılım göstermiyor ya da örneklem küçükse (n < 30) bağımsız '
            'gruplar için Mann-Whitney U, bağımlı gruplar için Wilcoxon Testi daha '
            'güvenilir sonuç verir.'
        ),
        'assumptions': (
            'Normallik: Her grup yaklaşık normal dağılıma sahip olmalıdır (Shapiro-Wilk p > 0.05 '
            'veya n ≥ 30). Varyans homojenliği (yalnızca bağımsız t-testi): Levene testi ile '
            'kontrol edilir; p < 0.05 ise Welch düzeltmesi otomatik uygulanır. Bağımsızlık: '
            'Gözlemler birbirini etkilememelidir. Sürekli ölçüm: Bağımlı değişken en az '
            'aralık ölçeğinde olmalıdır.'
        ),
        'how_to_interpret': (
            'p < 0.05: Gruplar arasındaki fark istatistiksel olarak anlamlıdır. '
            't istatistiği: Mutlak değer büyüdükçe gruplar arasındaki fark artar. '
            "Cohen's d etki büyüklüğü: 0.2 küçük, 0.5 orta, 0.8 ve üzeri büyük etki. "
            'Güven aralığı: %95 GA sıfırı kapsamıyorsa fark anlamlıdır. Yalnızca '
            'p değerine değil, etki büyüklüğüne ve güven aralığının genişliğine '
            'de dikkat edin.'
        ),
        'apa_example': (
            'Deney grubu (M = 78.4, SS = 9.2) kontrol grubuna (M = 71.6, SS = 10.1) '
            'kıyasla anlamlı düzeyde yüksek puan almıştır, t(58) = 2.84, p = .006, '
            "d = 0.71, %95 GA [1.98, 11.62]."
        ),
        'faq': [
            {
                'q': 'T-testi mi, Mann-Whitney mi seçmeliyim?',
                'a': ('Veriler normal dağılım gösteriyorsa veya n ≥ 30 ise t-testi tercih edin. '
                      'Küçük örneklemde normallik varsayımı sağlanmıyorsa Mann-Whitney U daha '
                      'güvenilir sonuç verir.'),
            },
            {
                'q': 'Levene testi p < 0.05 çıktı, ne yapmalıyım?',
                'a': ('Varyanslar homojen değil demektir. Analizus otomatik olarak Welch t-testi '
                      'uygular; ayrıca bir işlem yapmanıza gerek yoktur.'),
            },
            {
                'q': 'Tek yönlü mü, çift yönlü mü kullanmalıyım?',
                'a': ('Literatürde güçlü teorik gerekçe olmadıkça çift yönlü (two-tailed) test '
                      'kullanın. Tek yönlü test yalnızca farkın yönünü önceden kesin bildiğinizde '
                      'tercih edilir.'),
            },
            {
                'q': 'Sonuçları tezimde nasıl raporlamalıyım?',
                'a': ("APA 7 formatında t değeri, serbestlik derecesi, p değeri, Cohen's d ve "
                      '%95 güven aralığını bildirin. Analizus PDF raporu bu bilgilerin tamamını '
                      'hazır sunar.'),
            },
        ],
        'related_tools': [
            ('mann-whitney', 'Mann-Whitney U Testi'),
            ('anova', 'Tek Yönlü ANOVA'),
            ('wilcoxon', 'Wilcoxon Testi'),
            ('normallik', 'Normallik Testi'),
            ('orneklem', 'Örneklem Büyüklüğü'),
        ],
    },

    'anova': {
        'intro': (
            'Tek yönlü ANOVA (Analysis of Variance), üç veya daha fazla bağımsız grubun '
            'ortalamaları arasında istatistiksel olarak anlamlı bir fark olup olmadığını test '
            'eder. F istatistiğine dayanan bu analiz, t-testinin iki gruptan fazlasına '
            'genelleştirilmiş halidir. Anlamlı F bulunduğunda hangi grupların farklılaştığını '
            'belirlemek için Tukey HSD veya Bonferroni post-hoc testleri uygulanır.'
        ),
        'when_to_use': (
            'Üç veya daha fazla bağımsız grubu (örn. düşük/orta/yüksek gelir; A/B/C tedavisi) '
            'tek bir sürekli değişken üzerinden karşılaştırmak istediğinizde kullanın. '
            'Yalnızca iki grup söz konusuysa t-testi; bağımlı gruplar veya tekrarlı ölçümler '
            'varsa Tekrarlı Ölçümler ANOVA daha uygun seçenektir. Normallik ve varyans '
            'homojenliği sağlanmıyorsa Kruskal-Wallis testini tercih edin.'
        ),
        'assumptions': (
            'Normallik: Her grubun verileri normal dağılıma yakın olmalıdır. '
            'Varyans homojenliği: Levene testi ile kontrol edilir (p > 0.05 beklenir); '
            'ihlal durumunda Welch ANOVA kullanılır. Bağımsızlık: Gruplar birbirinden '
            'bağımsız olmalı, bir katılımcı yalnızca tek grupta yer almalıdır. '
            'Örneklem: Her grupta en az 5 gözlem önerilir.'
        ),
        'how_to_interpret': (
            'F istatistiği ve p değeri: p < 0.05 en az iki grup arasında anlamlı fark '
            'olduğunu gösterir; hangi grupların farklı olduğunu söylemez. '
            'Post-hoc testler (Tukey / Bonferroni): Grup çiftleri arasındaki farkları '
            'karşılaştırır ve hata oranını kontrol altında tutar. '
            "Eta-kare (η²): Etki büyüklüğü göstergesi — 0.01 küçük, 0.06 orta, 0.14 büyük."
        ),
        'apa_example': (
            'Gruplar arasında akademik başarı ortalamaları açısından anlamlı fark '
            'bulunmuştur, F(2, 87) = 5.43, p = .006, η² = .11. Tukey post-hoc analizi '
            'A grubu ile C grubu arasındaki farkın anlamlı olduğunu göstermiştir '
            '(p = .004).'
        ),
        'faq': [
            {
                'q': 'ANOVA anlamlı çıktı ama post-hoc çıkmadı, neden?',
                'a': ('ANOVA tüm gruplar arasında genel bir fark olduğunu gösterir. Post-hoc '
                      'çoklu karşılaştırma düzeltmesi (Bonferroni) alfa düzeyini düşürdüğünden '
                      'bazı çiftler anlamlı çıkmayabilir; bu tutarlı bir durumdur.'),
            },
            {
                'q': 'Kaç grubu karşılaştırabilirim?',
                'a': ('Teorik bir üst sınır yoktur, ancak çok sayıda grup post-hoc '
                      'karşılaştırmaları zorlaştırır ve I. tip hata riskini artırır. '
                      '3-6 grup için ANOVA idealdir.'),
            },
            {
                'q': 'Tukey mu, Bonferroni mu seçmeliyim?',
                'a': ('Tukey HSD, eşit örneklem büyüklüklerinde tercih edilir ve daha güçlüdür. '
                      'Bonferroni, az sayıda karşılaştırma ve dengesiz gruplar için uygundur.'),
            },
        ],
        'related_tools': [
            ('ttesti', 'T-Testi'),
            ('kruskal-wallis', 'Kruskal-Wallis Testi'),
            ('tekrarli-anova', 'Tekrarlı Ölçümler ANOVA'),
            ('orneklem', 'Örneklem Büyüklüğü'),
        ],
    },

    'mann_whitney': {
        'intro': (
            'Mann-Whitney U Testi, iki bağımsız grubun dağılımlarını karşılaştıran '
            'parametrik olmayan bir testtir. Bağımsız örneklem t-testinin normallik '
            'varsayımını gerektirmeyen alternatifidir. Sıra ortalamalarını karşılaştırarak '
            'çalışır; bu nedenle aykırı değerlere ve çarpık dağılımlara karşı '
            'dirençlidir. Küçük örneklemlerde ve ordinal verilerde güvenilir sonuçlar verir.'
        ),
        'when_to_use': (
            'İki bağımsız grubu karşılaştırmak istediğinizde ve veriler normal dağılım '
            'göstermiyorsa ya da örneklem küçükse (n < 30) kullanın. Ordinal ölçekli '
            'veriler (likert, sıralama) ve aykırı değer içeren veri setleri için '
            'idealdir. Bağımlı gruplar söz konusuysa Wilcoxon Testi, üç veya daha '
            'fazla grup varsa Kruskal-Wallis Testi tercih edilmelidir.'
        ),
        'assumptions': (
            'Bağımsızlık: İki grup birbirinden bağımsız olmalıdır. '
            'Süreklilik veya sıralanabilirlik: Bağımlı değişken en az ordinal ölçekte '
            'olmalıdır. Benzer şekil: Yalnızca merkezi eğilimi karşılaştırmak için '
            'grupların dağılım şekillerinin benzer olması beklenir.'
        ),
        'how_to_interpret': (
            'U istatistiği: Küçük U değeri iki grubun birbirinden ayrıştığını gösterir. '
            'p değeri: p < 0.05 gruplar arasında istatistiksel olarak anlamlı fark vardır. '
            'r (etki büyüklüğü): r = Z / √N formülüyle hesaplanır; '
            '0.1 küçük, 0.3 orta, 0.5 büyük etki. '
            'Sıra ortalamaları (Mean Rank): Hangi grubun daha yüksek değerlere sahip '
            'olduğunu gösterir.'
        ),
        'apa_example': (
            'Deney grubu (Md = 24.5) kontrol grubuna (Md = 18.0) kıyasla anlamlı '
            'düzeyde yüksek puan almıştır, U = 312, p = .018, r = .34.'
        ),
        'faq': [
            {
                'q': 'Mann-Whitney ortalamayı mı, medyanı mı karşılaştırır?',
                'a': ('Teknik olarak sıra dağılımlarını karşılaştırır. Grupların dağılım '
                      'şekilleri benzerse medyanlar arasındaki farkı test etmiş olur.'),
            },
            {
                'q': 'Örneklem büyükse t-testi mi kullanmalıyım?',
                'a': ('n ≥ 30 olduğunda merkezi limit teoremi devreye girer ve t-testi '
                      'sağlam sonuçlar üretir. Ancak aşırı çarpık dağılım veya aykırı '
                      'değer varlığında Mann-Whitney hâlâ tercih edilebilir.'),
            },
        ],
        'related_tools': [
            ('ttesti', 'T-Testi'),
            ('wilcoxon', 'Wilcoxon Testi'),
            ('kruskal-wallis', 'Kruskal-Wallis Testi'),
            ('normallik', 'Normallik Testi'),
        ],
    },

    'kruskal_wallis': {
        'intro': (
            'Kruskal-Wallis H Testi, üç veya daha fazla bağımsız grubu karşılaştıran '
            'parametrik olmayan bir testtir. Tek yönlü ANOVA\'nın normallik gerektirmeyen '
            'alternatifidir. Verileri sıralayarak H istatistiği hesaplar; bu nedenle '
            'aykırı değerlere ve çarpık dağılımlara karşı dirençlidir. Anlamlı '
            'sonuç bulunduğunda hangi grupların farklılaştığını belirlemek için '
            'Dunn post-hoc testi uygulanır.'
        ),
        'when_to_use': (
            'Üç veya daha fazla bağımsız grubu karşılaştırmak istediğinizde ve veriler '
            'normal dağılım göstermiyorsa ya da örneklem küçükse kullanın. '
            'Ordinal ölçekli ve aykırı değer içeren verilerde idealdir. '
            'İki grup için Mann-Whitney U; bağımlı gruplar için Friedman Testi '
            'daha uygun alternatiflerdir.'
        ),
        'assumptions': (
            'Bağımsızlık: Tüm gruplar birbirinden bağımsız olmalıdır. '
            'Sıralanabilirlik: Bağımlı değişken en az ordinal ölçekte olmalıdır. '
            'Benzer şekil: Yalnızca merkezi eğilimi karşılaştırmak için dağılım '
            'şekillerinin benzer olması beklenir.'
        ),
        'how_to_interpret': (
            'H istatistiği: Büyük H değeri gruplar arası farkın arttığını gösterir. '
            'p değeri: p < 0.05 en az iki grup arasında anlamlı fark var demektir. '
            'Dunn post-hoc: Hangi grup çiftlerinin birbirinden farklı olduğunu belirler. '
            'Etki büyüklüğü (η²): H / (N−1) formülüyle hesaplanır.'
        ),
        'apa_example': (
            'Üç grup arasında test puanları açısından anlamlı fark bulunmuştur, '
            'H(2) = 12.47, p = .002. Dunn post-hoc analizi A ve C grupları '
            'arasındaki farkın anlamlı olduğunu göstermiştir (p = .003).'
        ),
        'faq': [
            {
                'q': 'ANOVA yerine ne zaman Kruskal-Wallis kullanmalıyım?',
                'a': ('Normallik varsayımı karşılanmıyorsa, örneklem küçükse veya '
                      'veriler ordinal ölçekliyse Kruskal-Wallis tercih edin.'),
            },
            {
                'q': 'Kruskal-Wallis anlamlı çıktı, sonra ne yapmalıyım?',
                'a': ('Hangi grup çiftlerinin farklılaştığını bulmak için Dunn post-hoc '
                      'testini uygulayın. Analizus bunu otomatik olarak hesaplar.'),
            },
        ],
        'related_tools': [
            ('anova', 'Tek Yönlü ANOVA'),
            ('mann-whitney', 'Mann-Whitney U Testi'),
            ('friedman', 'Friedman Testi'),
            ('normallik', 'Normallik Testi'),
        ],
    },

    'ki_kare': {
        'intro': (
            'Ki-Kare Testi, kategorik değişkenler arasındaki ilişkiyi veya gözlenen '
            'frekansların beklenen frekanslardan anlamlı şekilde farklılaşıp '
            'farklılaşmadığını test eder. İki kullanım biçimi vardır: '
            'bağımsızlık testi iki kategorik değişken arasındaki ilişkiyi sınar; '
            'uyum iyiliği testi gözlenen dağılımın teorik bir dağılıma ne kadar '
            'uyduğunu değerlendirir. Küçük örneklemlerde Fisher\'s Exact Test '
            'otomatik olarak devreye girer.'
        ),
        'when_to_use': (
            'İki kategorik değişken arasında ilişki olup olmadığını araştırmak '
            'istediğinizde kullanın (örn. cinsiyet ile tercih, eğitim düzeyi ile '
            'istihdam durumu). Tüm hücrelerin beklenen frekansı 5 veya üzerinde '
            'olmalıdır; değilse Fisher\'s Exact Test tercih edilmelidir. '
            'Sürekli değişkenler için korelasyon veya regresyon daha uygun seçenektir.'
        ),
        'assumptions': (
            'Bağımsızlık: Her gözlem yalnızca bir kategoride yer almalıdır. '
            'Beklenen frekans: Hücrelerin %80\'inden fazlasında beklenen frekans ≥ 5 '
            'olmalıdır. Minimum gözlem: Toplam n ≥ 20 önerilir. '
            'Ölçek: Her iki değişken de kategorik (nominal veya ordinal) olmalıdır.'
        ),
        'how_to_interpret': (
            'χ² istatistiği: Büyük değer gözlenen ve beklenen frekanslar arasındaki '
            'farkın arttığını gösterir. '
            'p değeri: p < 0.05 değişkenler arasında anlamlı ilişki var demektir. '
            "Cramer's V (etki büyüklüğü): 0.1 küçük, 0.3 orta, 0.5 büyük ilişki. "
            'Artık analizi: Hangi hücrelerin ilişkiye en fazla katkıda bulunduğunu gösterir.'
        ),
        'apa_example': (
            'Cinsiyet ile program tercihi arasında anlamlı bir ilişki bulunmuştur, '
            "χ²(2, N = 150) = 11.34, p = .003, Cramer's V = .27."
        ),
        'faq': [
            {
                'q': 'Ki-Kare mi, Fisher\'s Exact mı kullanmalıyım?',
                'a': ('Herhangi bir hücrenin beklenen frekansı 5\'in altındaysa '
                      'Fisher\'s Exact Test tercih edilmelidir. Analizus bunu otomatik kontrol eder.'),
            },
            {
                'q': 'Ki-Kare ilişkinin gücünü gösterir mi?',
                'a': ("Hayır; χ² yalnızca anlamlılığı gösterir. İlişkinin gücü için Cramer's V "
                      "veya Phi katsayısına bakın."),
            },
        ],
        'related_tools': [
            ('korelasyon', 'Korelasyon Analizi'),
            ('lojistik-regresyon', 'Lojistik Regresyon'),
        ],
    },

    'korelasyon': {
        'intro': (
            'Korelasyon analizi, iki sürekli değişken arasındaki doğrusal ilişkinin '
            'yönünü ve gücünü ölçer. Pearson korelasyonu normal dağılımlı veriler için '
            'standart seçimdir; Spearman ve Kendall katsayıları normallik varsayımı '
            'gerektirmeyen ve aykırı değerlere karşı dirençli alternatiflerdir. '
            'Korelasyon nedensellik kanıtlamaz; yalnızca birlikte değişim örüntüsünü '
            'ortaya koyar.'
        ),
        'when_to_use': (
            'İki sürekli değişken arasında ilişki olup olmadığını ve varsa yönünü '
            'anlamak istediğinizde kullanın. Veriler normal dağılımlıysa Pearson; '
            'ordinal veriler veya normallik ihlali varsa Spearman; küçük örneklemde '
            'ya da bağların (tied ranks) fazla olduğu durumlarda Kendall tercih edin. '
            'Nedensellik iddiası için regresyon analizi gerekir.'
        ),
        'assumptions': (
            'Pearson için: Her iki değişken de sürekli ve yaklaşık normal dağılımlı '
            'olmalıdır; ilişki doğrusal olmalıdır; aykırı değerler kontrol edilmelidir. '
            'Spearman/Kendall için: Değişkenler en az ordinal ölçekte olmalıdır; '
            'normallik gerekmez.'
        ),
        'how_to_interpret': (
            'r değeri: +1 mükemmel pozitif, −1 mükemmel negatif, 0 ilişki yok. '
            '|r| < 0.3 zayıf, 0.3–0.5 orta, > 0.5 güçlü ilişki olarak yorumlanır '
            '(alan normlarına göre değişir). '
            'p değeri: p < 0.05 ilişkinin istatistiksel olarak anlamlı olduğunu gösterir. '
            'r²: Açıklanan varyans oranı — örn. r = 0.6 ise r² = 0.36, değişkenliğin '
            '%36\'sı paylaşılmaktadır.'
        ),
        'apa_example': (
            'Çalışma süresi ile sınav puanı arasında orta düzeyde pozitif bir ilişki '
            'bulunmuştur, r(98) = .54, p < .001.'
        ),
        'faq': [
            {
                'q': 'Korelasyon nedensellik kanıtlar mı?',
                'a': ('Hayır. İki değişken arasındaki ilişki bir üçüncü değişkenden '
                      'kaynaklanıyor olabilir. Nedensellik için deney tasarımı veya '
                      'yapısal eşitlik modellemesi gerekir.'),
            },
            {
                'q': 'Kaç değişken arasında korelasyon hesaplayabilirim?',
                'a': ('Analizus birden fazla değişken içeren veri setlerinde tüm çiftler '
                      'için otomatik korelasyon matrisi oluşturur.'),
            },
        ],
        'related_tools': [
            ('lineer-regresyon', 'Doğrusal Regresyon'),
            ('ttesti', 'T-Testi'),
            ('normallik', 'Normallik Testi'),
        ],
    },

    'cronbach': {
        'intro': (
            'Cronbach Alfa katsayısı, bir ölçeğin veya anketin iç tutarlılığını '
            'değerlendiren en yaygın güvenilirlik ölçütüdür. 0 ile 1 arasında değer alır; '
            'yüksek alfa, ölçek maddelerinin aynı yapıyı tutarlı biçimde ölçtüğüne '
            'işaret eder. Tez, makale ve anket çalışmalarında ölçek geçerleme '
            'sürecinin vazgeçilmez adımlarından biridir.'
        ),
        'when_to_use': (
            'Birden fazla madde (soru) ile ölçülen bir yapının (tutum, yetenek, '
            'kişilik özelliği) güvenilirliğini raporlamak istediğinizde kullanın. '
            'Her satır bir katılımcıyı, her sütun bir ölçek maddesini temsil '
            'etmelidir. Tek maddelik ölçekler veya birden fazla boyut içeren '
            'ölçekler için alt boyutları ayrı ayrı analiz edin.'
        ),
        'assumptions': (
            'Essensiyal tau-eşdeğerliği: Maddeler aynı yapıyı ölçmeli, '
            'hata varyansları birbirinden bağımsız olmalıdır. '
            'Ölçek düzeyi: Maddeler en az aralık ölçeğinde olmalıdır '
            '(Likert maddeler bu koşulu karşılar). '
            'Yönlülük: Tüm maddeler aynı yönde kodlanmış olmalıdır; '
            'ters maddeleri analizden önce dönüştürün.'
        ),
        'how_to_interpret': (
            'α < 0.60: Kabul edilemez. 0.60–0.70: Düşük / sınırda. '
            '0.70–0.80: Kabul edilebilir. 0.80–0.90: İyi. α ≥ 0.90: Mükemmel. '
            'Madde silinince alfa: Bir madde silindiğinde alfa artıyorsa o '
            'madde ölçeğe katkı sağlamıyor olabilir. '
            'Düzeltilmiş madde-toplam korelasyonu: 0.30\'ın altındaki maddeler '
            'ölçekten çıkarılmayı düşündürmelidir.'
        ),
        'apa_example': (
            'Ölçeğin iç tutarlılığı yüksek bulunmuştur (α = .87, 12 madde).'
        ),
        'faq': [
            {
                'q': 'Alfa çok yüksek çıktı (α > 0.95), sorun var mı?',
                'a': ('Çok yüksek alfa, maddelerin birbirinin tekrarı olduğuna '
                      '(madde artıklığı) işaret edebilir. Madde-toplam korelasyonlarını '
                      'inceleyin ve benzer içerikli maddeleri gözden geçirin.'),
            },
            {
                'q': 'Ters maddeler varsa ne yapmalıyım?',
                'a': ('Ters kodlu maddeleri analize girmeden önce dönüştürün '
                      '(örn. 1→5, 2→4 şeklinde). Aksi takdirde alfa hatalı hesaplanır.'),
            },
            {
                'q': 'Alt boyutlar için ayrı alfa hesaplamalı mıyım?',
                'a': ('Evet. Çok boyutlu ölçeklerde her alt boyut için ayrı güvenilirlik '
                      'analizi yapın; toplam ölçek için tek alfa yanıltıcı olabilir.'),
            },
        ],
        'related_tools': [
            ('afa', 'Açıklayıcı Faktör Analizi'),
            ('betimsel', 'Betimsel İstatistik'),
        ],
    },

    'normallik': {
        'intro': (
            'Normallik testi, bir veri setinin normal (Gaussian) dağılıma ne ölçüde '
            'uyduğunu değerlendirir. Pek çok parametrik testin (t-testi, ANOVA, '
            'Pearson korelasyonu) temel varsayımı olan normallik, Shapiro-Wilk testi '
            've çarpıklık/basıklık katsayıları ile ölçülür. Q-Q grafikleri görsel '
            'kontrol imkânı sağlar.'
        ),
        'when_to_use': (
            'Parametrik bir test uygulamadan önce varsayım kontrolü olarak kullanın. '
            'Shapiro-Wilk n ≤ 2000 için en güçlü testtir. Büyük örneklemlerde '
            '(n > 200) küçük sapmalar bile anlamlı çıkabileceğinden histogram ve '
            'Q-Q grafiğine de bakın. n ≥ 30 olduğunda merkezi limit teoremi gereği '
            'hafif sapmaları görmezden gelmek genellikle kabul edilebilir.'
        ),
        'assumptions': (
            'Bağımsızlık: Gözlemler birbirinden bağımsız olmalıdır. '
            'Süreklilik: Değişken sürekli ölçekte olmalıdır. '
            'Örneklem büyüklüğü: Shapiro-Wilk n = 3 ile n = 5000 arasında güvenilir '
            'sonuç verir.'
        ),
        'how_to_interpret': (
            'Shapiro-Wilk p > 0.05: Normal dağılımdan anlamlı sapma yoktur. '
            'p < 0.05: Normal dağılımdan anlamlı sapma vardır; parametrik olmayan '
            'testler düşünülmelidir. '
            'Çarpıklık (Skewness): |değer| < 1 genellikle hafif sapma sayılır. '
            'Basıklık (Kurtosis): |değer| < 1 genellikle kabul edilebilir. '
            'Q-Q plot: Noktalar referans çizgisine yakınsa normallik desteklenir.'
        ),
        'apa_example': (
            'Shapiro-Wilk testi verilerin normal dağılımdan anlamlı biçimde '
            'sapmadığını göstermiştir, W = .97, p = .214.'
        ),
        'faq': [
            {
                'q': 'Normallik testi anlamlı çıktı; ne yapmalıyım?',
                'a': ('Parametrik olmayan bir test kullanmayı düşünün. İki grup için '
                      'Mann-Whitney U, üç veya daha fazla grup için Kruskal-Wallis, '
                      'bağımlı gruplar için Wilcoxon uygun alternatiflerdir.'),
            },
            {
                'q': 'Büyük örneklemde Shapiro-Wilk her zaman anlamlı çıkıyor, neden?',
                'a': ('Örneklem büyüdükçe test gücü artar; küçük, pratik önemi olmayan '
                      'sapmalar bile p < 0.05 verebilir. Histogram ve Q-Q grafiğine '
                      'bakarak görsel yargı oluşturun.'),
            },
        ],
        'related_tools': [
            ('ttesti', 'T-Testi'),
            ('mann-whitney', 'Mann-Whitney U Testi'),
            ('betimsel', 'Betimsel İstatistik'),
        ],
    },

    'betimsel': {
        'intro': (
            'Betimsel istatistik analizi, veri setindeki değişkenleri özetlemenin '
            've görselleştirmenin temel yöntemidir. Ortalama, medyan, standart sapma, '
            'çeyrekler, çarpıklık ve basıklık gibi ölçütlerle veri dağılımı hakkında '
            'kapsamlı bir tablo sunar. Kategorik değişkenler için frekans ve yüzde '
            'dağılımları hesaplanır. Her akademik çalışmanın "Bulgular" bölümünde '
            'yer alması beklenen ilk adım budur.'
        ),
        'when_to_use': (
            'Herhangi bir ileri analize geçmeden önce veriyi tanımak için kullanın. '
            'Aykırı değerleri ve veri kalite sorunlarını erken aşamada fark etmenizi '
            'sağlar. Tez, makale ve raporlarda katılımcı/değişken özelliklerini '
            'sunmak için de başvurulan standarttır.'
        ),
        'assumptions': (
            'Betimsel istatistik herhangi bir dağılım varsayımı gerektirmez; '
            'ham verileri özetler. Ancak ortalama ve standart sapma aykırı '
            'değerlerden etkilenir — çarpık dağılımlarda medyan ve IQR '
            'daha temsil edici ölçütlerdir.'
        ),
        'how_to_interpret': (
            'Ortalama: Merkezi eğilimin en yaygın ölçütü; aykırı değerlere duyarlıdır. '
            'Medyan: Dağılımın ortasındaki değer; çarpık dağılımlarda ortalamadan '
            'daha temsilcidir. Standart sapma (SS): Değerlerin ortalamadan ne kadar '
            'saptığını gösterir. Çarpıklık > 0: Sağa çarpık dağılım; < 0: Sola çarpık. '
            'IQR (Çeyrekler Arası Genişlik): Aykırı değerlere karşı dirençli '
            'bir yayılım ölçütüdür.'
        ),
        'apa_example': (
            'Katılımcıların yaş ortalaması 28.4 (SS = 5.7, Çarpıklık = 0.42) '
            'olarak hesaplanmıştır.'
        ),
        'faq': [
            {
                'q': 'Ortalama mı, medyan mı raporlamalıyım?',
                'a': ('Normal dağılımlı sürekli değişkenler için ortalama ± SS; '
                      'çarpık dağılımlar ve ordinal veriler için medyan (IQR) tercih edin.'),
            },
            {
                'q': 'Frekans tablosu ile çapraz tablo arasındaki fark nedir?',
                'a': ('Frekans tablosu tek bir kategorik değişkeni özetler. '
                      'Çapraz tablo iki değişkeni birlikte gösterir ve Ki-Kare analizine '
                      'zemin hazırlar.'),
            },
        ],
        'related_tools': [
            ('normallik', 'Normallik Testi'),
            ('korelasyon', 'Korelasyon Analizi'),
            ('cronbach', 'Cronbach Alfa'),
        ],
    },

    'orneklem': {
        'intro': (
            'Örneklem büyüklüğü hesaplayıcı, bir araştırmanın istenen istatistiksel '
            'gücü elde etmek için kaç katılımcıya ihtiyaç duyduğunu belirler. '
            'Çok küçük örneklem gerçek etkileri kaçırır (düşük güç); çok büyük '
            'örneklem ise kaynakları boşa harcar ve küçük, pratik önemi olmayan '
            'farkları anlamlı gösterebilir. Doğru örneklem büyüklüğü hem etik hem '
            'metodolojik bir zorunluluktur.'
        ),
        'when_to_use': (
            'Veri toplamaya başlamadan önce araştırma tasarımı aşamasında kullanın. '
            'Tez ve makale hakemlerinin çoğu örneklem büyüklüğü gerekçesi ister. '
            'Bağımsız örneklem t-testi, ANOVA, korelasyon veya ki-kare analizleri '
            'için planlama yapabilirsiniz.'
        ),
        'assumptions': (
            'Etki büyüklüğü tahmini: Daha önce yapılmış araştırmalar veya pilot '
            'çalışmadan elde edilen etki büyüklüğünü girin. '
            'Alpha (α): Genellikle 0.05 kabul edilir (I. tip hata olasılığı). '
            'Güç (1 − β): 0.80 standart değerdir; yüksek riskli araştırmalarda '
            '0.90 veya 0.95 önerilir.'
        ),
        'how_to_interpret': (
            "Cohen's d etki büyüklüğü: 0.2 küçük, 0.5 orta, 0.8 büyük. "
            'f (ANOVA): 0.10 küçük, 0.25 orta, 0.40 büyük. '
            'r (korelasyon): 0.10 küçük, 0.30 orta, 0.50 büyük. '
            'Sonuç: Hesaplanan n, her grup başına gereken minimum katılımcı '
            'sayısıdır; kayıp ve redleri karşılamak için %10–20 eklenmesi önerilir.'
        ),
        'apa_example': (
            "Orta etki büyüklüğü (d = 0.5), α = .05 ve %80 güç için her grupta "
            'en az 64 katılımcı gerektiği hesaplanmıştır.'
        ),
        'faq': [
            {
                'q': 'Etki büyüklüğünü bilmiyorum; ne girmeliyim?',
                'a': ('Alanyazında benzer çalışmaların raporladığı etki büyüklüğünü '
                      'kullanın. Bilgi yoksa orta etki (d = 0.5, f = 0.25) kabul '
                      'görmüş muhafazakâr bir başlangıç noktasıdır.'),
            },
            {
                'q': 'Hesaplanan örneklem büyüklüğüne ulaşamıyorum, ne yapmalıyım?',
                'a': ('Daha büyük bir etki büyüklüğü hedefleyebilir veya gücü '
                      '0.70\'e düşürebilirsiniz. Kısıtlamayı yöntem bölümünde '
                      'şeffaf biçimde belirtin.'),
            },
        ],
        'related_tools': [
            ('ttesti', 'T-Testi'),
            ('anova', 'Tek Yönlü ANOVA'),
            ('korelasyon', 'Korelasyon Analizi'),
        ],
    },

    'lineer_regresyon': {
        'intro': (
            'Çoklu doğrusal regresyon (OLS), bir bağımlı sürekli değişkeni birden '
            'fazla bağımsız değişken aracılığıyla açıklar ve tahmin eder. '
            'Her bağımsız değişkenin bağımlı değişken üzerindeki bağımsız '
            'etkisini katsayılarla (β) nicelleştirir. Sosyal bilimler, ekonomi '
            've tıpta en sık kullanılan analitik çerçevelerden biridir.'
        ),
        'when_to_use': (
            'Sürekli bir bağımlı değişkeni birden fazla sürekli veya kategorik '
            '(kukla değişken olarak kodlanmış) bağımsız değişkenle açıklamak '
            'istediğinizde kullanın. Bağımlı değişken kategorik ise lojistik '
            'regresyon; veriler zaman serisi içeriyorsa uygun zaman serisi '
            'modelleri tercih edilmelidir.'
        ),
        'assumptions': (
            'Doğrusallık: Bağımlı ve bağımsız değişkenler arasında doğrusal ilişki olmalıdır. '
            'Normallik: Artıklar (residuals) normal dağılmalıdır. '
            'Sabit varyans (homoskedastisite): Artıkların varyansı tüm tahmin '
            'değerlerinde sabit olmalıdır. '
            'Çoklu doğrusallık olmamalıdır: VIF < 10 beklenir. '
            'Bağımsızlık: Artıklar birbirinden bağımsız olmalıdır.'
        ),
        'how_to_interpret': (
            'R²: Modelin bağımlı değişkendeki varyansı açıklama oranı. '
            'Düzeltilmiş R²: Değişken sayısını hesaba katar; modeller arasında '
            'karşılaştırma için tercih edilir. '
            'β katsayısı: Diğer değişkenler sabitken bir birimlik artışın '
            'bağımlı değişkende yarattığı değişim. '
            'p < 0.05: İlgili bağımsız değişken modelde anlamlı katkı sağlar.'
        ),
        'apa_example': (
            'Regresyon modeli toplam varyansın %43\'ünü açıklamıştır, '
            'R² = .43, F(3, 96) = 24.13, p < .001. Yalnızca çalışma süresi '
            'β = .52, t(96) = 5.87, p < .001 ile anlamlı bir yordayıcı olmuştur.'
        ),
        'faq': [
            {
                'q': 'Kaç değişken ekleyebilirim?',
                'a': ('Kural olarak her değişken için en az 10–20 gözlem önerilir. '
                      'Çok sayıda değişken aşırı uyum (overfitting) riskini artırır.'),
            },
            {
                'q': 'VIF yüksek çıktı, ne yapmalıyım?',
                'a': ('VIF > 10 çoklu doğrusallık sorununa işaret eder. '
                      'Korelasyonu yüksek değişkenlerden birini çıkarın veya '
                      'Ridge regresyonu gibi düzenlileştirme yöntemlerini deneyin.'),
            },
        ],
        'related_tools': [
            ('korelasyon', 'Korelasyon Analizi'),
            ('lojistik-regresyon', 'Lojistik Regresyon'),
            ('normallik', 'Normallik Testi'),
        ],
    },

    'lojistik_regresyon': {
        'intro': (
            'Lojistik regresyon, ikili (0/1) kategorik bir bağımlı değişkeni '
            'birden fazla bağımsız değişken aracılığıyla tahmin eder. '
            'Doğrudan olasılık yerine log-odds modeller; sonuçlar odds oranı '
            '(OR) olarak yorumlanır. Tıp, psikoloji ve sosyal bilimlerde yaygın '
            'kullanımı olan güçlü bir sınıflandırma aracıdır.'
        ),
        'when_to_use': (
            'Bağımlı değişkeniniz ikili kategorik olduğunda (hasta/sağlıklı, '
            'geçti/kaldı, satın aldı/almadı) kullanın. Bağımsız değişkenler '
            'sürekli, ordinal veya kategorik (kukla kodlanmış) olabilir. '
            'İkiden fazla kategori için çok sınıflı lojistik regresyon '
            'ya da yapay sinir ağları değerlendirilebilir.'
        ),
        'assumptions': (
            'İkili bağımlı değişken: Sonuç değişkeni 0 ve 1 değerlerini almalıdır. '
            'Bağımsızlık: Gözlemler birbirinden bağımsız olmalıdır. '
            'Çoklu doğrusallık olmamalıdır: VIF < 10. '
            'Yeterli örneklem: Her sonuç kategorisinde en az 10–15 olay önerilir. '
            'Doğrusallık (logit ölçeğinde): Sürekli bağımsız değişkenler log-odds '
            'ile doğrusal ilişkide olmalıdır.'
        ),
        'how_to_interpret': (
            'Odds Oranı (OR): OR > 1 bağımsız değişken arttıkça olayın gerçekleşme '
            'olasılığı artar; OR < 1 azalır. OR = 1 ilişki yoktur. '
            'p < 0.05: İlgili değişken modelde anlamlı katkı sağlar. '
            'Nagelkerke R²: Doğrusal regresyondaki R²\'ye benzer; modelin '
            'açıklama gücünü özetler.'
        ),
        'apa_example': (
            'Yaş değişkeni hastalık riskini anlamlı biçimde yordamıştır, '
            'OR = 1.08, %95 GA [1.03, 1.14], p = .002.'
        ),
        'faq': [
            {
                'q': 'Lojistik regresyonda örneklem ne kadar büyük olmalı?',
                'a': ('Her bağımsız değişken için nadir sonuç (0 veya 1) kategorisinde '
                      'en az 10 olay gerekir. Örneğin 5 değişkenle model kuruyorsanız '
                      've olumsuz sonuç oranınız %20 ise en az 250 katılımcı önerilir.'),
            },
            {
                'q': 'Sınıflandırma doğruluğu yeterli bir ölçüt mü?',
                'a': ('Dengesiz veri setlerinde doğruluk yanıltıcı olabilir. '
                      'AUC-ROC, duyarlılık (sensitivity) ve özgüllük (specificity) '
                      'birlikte değerlendirilmelidir.'),
            },
        ],
        'related_tools': [
            ('ki-kare', 'Ki-Kare Testi'),
            ('lineer-regresyon', 'Doğrusal Regresyon'),
            ('karar-agaci', 'Karar Ağacı'),
        ],
    },

    'friedman': {
        'intro': (
            'Friedman Testi, tekrarlı ölçümler içeren üç veya daha fazla ilişkili '
            'grubu karşılaştıran parametrik olmayan bir testtir. '
            'Tekrarlı Ölçümler ANOVA\'nın normallik gerektirmeyen alternatifidir. '
            'Sıra değerlerine dayanan bu test, küçük örneklemlerde ve ordinal '
            'verilerde güvenilir sonuçlar üretir.'
        ),
        'when_to_use': (
            'Aynı katılımcıların üç veya daha fazla farklı koşulda ölçüldüğü '
            've normallik varsayımının karşılanmadığı durumlarda kullanın. '
            'Örneğin üç farklı tedavi yönteminin aynı hasta grubuna sırayla '
            'uygulandığı çapraz tasarımlarda idealdir. İki bağımlı grup için '
            'Wilcoxon Testi, normallik sağlanıyorsa Tekrarlı Ölçümler ANOVA '
            'daha uygun seçenektir.'
        ),
        'assumptions': (
            'Tekrarlı ölçüm: Her birey tüm koşullarda ölçülmüş olmalıdır. '
            'Bağımsız bireyler: Katılımcılar birbirinden bağımsız olmalıdır. '
            'Sıralanabilirlik: Bağımlı değişken en az ordinal ölçekte olmalıdır.'
        ),
        'how_to_interpret': (
            'χ² istatistiği ve p değeri: p < 0.05 en az iki ölçüm koşulu '
            'arasında anlamlı fark var demektir. '
            'Post-hoc (Wilcoxon ile Bonferroni düzeltmesi): Hangi koşul çiftlerinin '
            'birbirinden farklı olduğunu belirler. '
            'Etki büyüklüğü (W — Kendall\'s W): 0 ilişki yok, 1 tam uyum.'
        ),
        'apa_example': (
            'Üç ölçüm zamanı arasında puanlar anlamlı biçimde farklılaşmıştır, '
            'χ²(2) = 14.30, p = .001, W = .48.'
        ),
        'faq': [
            {
                'q': 'Friedman mi, Tekrarlı Ölçümler ANOVA mı seçmeliyim?',
                'a': ('Normallik varsayımı sağlanıyorsa Tekrarlı Ölçümler ANOVA daha '
                      'güçlüdür. Küçük örneklem veya normallik ihlali varsa Friedman '
                      'daha güvenilir sonuç verir.'),
            },
        ],
        'related_tools': [
            ('tekrarli-anova', 'Tekrarlı Ölçümler ANOVA'),
            ('wilcoxon', 'Wilcoxon Testi'),
            ('kruskal-wallis', 'Kruskal-Wallis Testi'),
        ],
    },

    'tekrarli_anova': {
        'intro': (
            'Tekrarlı Ölçümler ANOVA, aynı bireylerin üç veya daha fazla koşul ya da '
            'zaman noktasında ölçüldüğü verileri analiz eder. Bireyler arası '
            'değişkenliği kontrol altına aldığından bağımsız örneklem ANOVA\'ya '
            'kıyasla daha yüksek istatistiksel güç sağlar. Öntest-sontest-izlem '
            'tasarımları ve çapraz geçişli denemelerde yaygın olarak kullanılır.'
        ),
        'when_to_use': (
            'Aynı katılımcı grubunun üç veya daha fazla zamanda ya da koşulda '
            'ölçüldüğü durumlarda kullanın. Normallik ve küresellik varsayımları '
            'karşılanmalıdır. Küresellik ihlali durumunda Greenhouse-Geisser '
            'düzeltmesi otomatik uygulanır. Normallik sağlanamıyorsa '
            'Friedman Testi tercih edilmelidir.'
        ),
        'assumptions': (
            'Normallik: Her ölçüm noktasındaki veriler normal dağılımlı olmalıdır. '
            'Küresellik (Sphericity): Ölçüm çiftleri arasındaki fark puanlarının '
            'varyansları eşit olmalıdır (Mauchly testi ile kontrol edilir). '
            'İhlal durumunda Greenhouse-Geisser veya Huynh-Feldt düzeltmesi kullanılır. '
            'Bağımsızlık: Katılımcılar birbirinden bağımsız olmalıdır.'
        ),
        'how_to_interpret': (
            'F istatistiği ve p değeri: p < 0.05 ölçüm zamanları arasında anlamlı '
            'fark olduğunu gösterir. '
            'Parsiyel eta-kare (ηp²): 0.01 küçük, 0.06 orta, 0.14 büyük etki. '
            'Post-hoc (eşleştirilmiş t-testi + Bonferroni): Hangi zaman noktaları '
            'arasında fark olduğunu belirler.'
        ),
        'apa_example': (
            'Ölçüm zamanı ana etkisi anlamlı bulunmuştur, F(1.74, 52.2) = 18.43, '
            'p < .001, ηp² = .38 (Greenhouse-Geisser düzeltmesi uygulanmıştır).'
        ),
        'faq': [
            {
                'q': 'Mauchly testi anlamlı çıktı, ne yapmalıyım?',
                'a': ('Küresellik ihlali var demektir. Analizus otomatik olarak '
                      'Greenhouse-Geisser düzeltmesini uygular; ayrıca bir işlem '
                      'yapmanıza gerek yoktur.'),
            },
            {
                'q': 'Bir katılımcının bir ölçümde verisi eksik, ne olur?',
                'a': ('Tekrarlı ANOVA tam veri gerektirir; eksik gözlem olan katılımcı '
                      'varsayılan olarak analizden çıkarılır. Çok sayıda eksik varsa '
                      'karma model (mixed model) yaklaşımını değerlendirin.'),
            },
        ],
        'related_tools': [
            ('friedman', 'Friedman Testi'),
            ('anova', 'Tek Yönlü ANOVA'),
            ('ttesti', 'T-Testi'),
        ],
    },

    'karar_agaci': {
        'intro': (
            'Karar ağacı, verileri hiyerarşik dal yapısı biçiminde bölerek '
            'sınıflandırma veya regresyon gerçekleştiren bir makine öğrenmesi '
            'yöntemidir. CART algoritmasına dayanan bu model, yorumlanabilirliği '
            've görsel sunumuyla öne çıkar. Gini safsızlığını minimize ederek '
            'en iyi bölme noktalarını belirler; sonuçlar kolayca görselleştirilebilir '
            've raporlanabilir.'
        ),
        'when_to_use': (
            'Kategorik bir sonuç değişkenini birden fazla özellik (feature) ile '
            'tahmin etmek ve modeli görsel olarak açıklamak istediğinizde kullanın. '
            'Doğrusal olmayan ilişkileri yakalamakta başarılıdır. '
            'Normallik varsayımı gerektirmez ve karma ölçek (sürekli + kategorik) '
            'değişkenleri işleyebilir.'
        ),
        'assumptions': (
            'Bağımlı değişken: Kategorik (sınıflandırma) veya sürekli (regresyon). '
            'Örneklem boyutu: Ağaç derinliği arttıkça daha fazla veriye ihtiyaç duyulur; '
            'çok küçük örneklemlerde aşırı uyum (overfitting) riski yüksektir. '
            'Derinlik kontrolü: max_depth parametresi ile aşırı büyüme önlenir.'
        ),
        'how_to_interpret': (
            'Doğruluk (Accuracy): Doğru sınıflandırılan örneklerin oranı. '
            'Karmaşıklık matrisi: Her sınıf için gerçek/yanlış pozitif ve negatifleri gösterir. '
            'Özellik önemi (Feature Importance): Hangi değişkenlerin bölme kararlarına '
            'daha fazla katkı sağladığını gösterir. '
            'Ağaç derinliği: Derin ağaçlar eğitim verisini ezberler; '
            'test doğruluğunu kontrol edin.'
        ),
        'apa_example': (
            'Karar ağacı modeli (max_depth = 4) test setinde %82 doğruluk, '
            'AUC = .88 elde etmiştir. En önemli yordayıcı değişken X1 '
            'olarak belirlenmiştir (önem = .41).'
        ),
        'faq': [
            {
                'q': 'Karar ağacı mı, lojistik regresyon mu seçmeliyim?',
                'a': ('Yorumlanabilirlik ve doğrusal olmayan ilişkiler önemliyse '
                      'karar ağacı; istatistiksel katsayı ve olasılık yorumlaması '
                      'gerekiyorsa lojistik regresyon tercih edin.'),
            },
            {
                'q': 'Aşırı uyumu (overfitting) nasıl önlerim?',
                'a': ('max_depth, min_samples_leaf ve min_samples_split parametrelerini '
                      'sınırlayın. Çapraz doğrulama (cross-validation) ile model '
                      'performansını test edin.'),
            },
        ],
        'related_tools': [
            ('lojistik-regresyon', 'Lojistik Regresyon'),
            ('svm', 'Destek Vektör Makinesi'),
        ],
    },

    'svm': {
        'intro': (
            'Destek Vektör Makinesi (SVM), sınıflar arasındaki marjini '
            'maksimize eden bir karar sınırı (hyperplane) bulan gözetimli '
            'öğrenme algoritmasıdır. Doğrusal olarak ayrılamayan veriler '
            'için çekirdek fonksiyonları (RBF, polinom) ile yüksek boyutlu '
            'uzaya projeksiyon yapar. Küçük ve orta ölçekli veri setlerinde '
            'yüksek doğruluk oranları elde edebilir.'
        ),
        'when_to_use': (
            'İkili veya çok sınıflı sınıflandırma problemlerinde kullanın. '
            'Özellik sayısının gözlem sayısına yakın ya da daha fazla olduğu '
            'durumlarda (metin sınıflandırma, genomik veriler) güçlü performans '
            'gösterir. Büyük veri setlerinde eğitim süresi uzayabileceğinden '
            'alternatif yöntemler değerlendirilebilir.'
        ),
        'assumptions': (
            'Normalleştirme: Özellikler benzer ölçeğe getirilmelidir; '
            'SVM büyük ölçek farklarına duyarlıdır. '
            'C parametresi (düzenlileştirme): Küçük C daha geniş marji, '
            'büyük C eğitim hatasına daha az tolerans sağlar. '
            'Çekirdek seçimi: Doğrusal ayırt edilebilir veriler için linear; '
            'karmaşık ilişkiler için RBF çekirdeği önerilir.'
        ),
        'how_to_interpret': (
            'Doğruluk, F1 skoru, AUC-ROC: Sınıflandırma başarısının temel ölçütleri. '
            'Destek vektörleri: Karar sınırını belirleyen, marjine en yakın '
            'eğitim örnekleri. '
            'Karmaşıklık matrisi: Hangi sınıfların daha sık karıştırıldığını gösterir.'
        ),
        'apa_example': (
            'RBF çekirdekli SVM modeli (C = 1.0, γ = "scale") test setinde '
            'F1 = .84, AUC = .91 değerlerine ulaşmıştır.'
        ),
        'faq': [
            {
                'q': 'SVM mi, karar ağacı mı tercih etmeliyim?',
                'a': ('SVM yüksek boyutlu verilerde ve az gözlemde güçlüdür; '
                      'ancak yorumlanması zordur. Karar ağacı daha yorumlanabilir '
                      've büyük veri setlerinde daha hızlıdır.'),
            },
            {
                'q': 'Çekirdek fonksiyonunu nasıl seçerim?',
                'a': ('Başlangıç olarak RBF çekirdeği deneyin; çoğu durumda iyi '
                      'sonuç verir. Doğrusal veri setleri için linear, '
                      'polinom ilişkiler için poly çekirdeği değerlendirilebilir.'),
            },
        ],
        'related_tools': [
            ('karar-agaci', 'Karar Ağacı'),
            ('lojistik-regresyon', 'Lojistik Regresyon'),
        ],
    },

    'afa': {
        'intro': (
            'Açıklayıcı Faktör Analizi (AFA), birbiriyle ilişkili gözlenen '
            'değişkenlerin altında yatan gizil yapıları (faktörleri) ortaya '
            'çıkaran boyut indirgeme yöntemidir. Ölçek geliştirme ve uyarlama '
            'çalışmalarında, anketin hangi alt boyutları ölçtüğünü belirlemek '
            'için yaygın biçimde kullanılır. Temel Bileşenler Analizi\'nden '
            'farklı olarak ölçüm hatalarını açıkça modele dahil eder.'
        ),
        'when_to_use': (
            'Çok sayıda değişken arasındaki gizli yapıyı keşfetmek ve '
            'boyut sayısını veri odaklı belirlemek istediğinizde kullanın. '
            'Ölçek geliştirme çalışmalarında geçerlik (yapı geçerliği) '
            'kanıtı sağlamak için zorunludur. Faktör yapısı önceden '
            'biliniyorsa Doğrulayıcı Faktör Analizi (DFA) daha uygun '
            'seçenektir.'
        ),
        'assumptions': (
            'Örneklem büyüklüğü: Değişken başına en az 5–10 gözlem önerilir; '
            'minimum 100 katılımcı gerekir. '
            'Korelasyon: Değişkenler arasında yeterli korelasyon bulunmalıdır '
            '(KMO ≥ 0.60, Bartlett p < 0.05). '
            'Süreklilik: Değişkenler en az aralık ölçeğinde olmalıdır. '
            'Çoklu doğrusallık olmamalıdır: Aşırı yüksek korelasyonlar '
            '(r > 0.90) sorun yaratır.'
        ),
        'how_to_interpret': (
            'KMO (Kaiser-Meyer-Olkin): ≥ 0.80 "iyi", ≥ 0.70 "orta", '
            '< 0.60 "yetersiz" örneklem yeterliliği. '
            'Bartlett Testi p < 0.05: Korelasyon matrisi faktör analizine uygundur. '
            'Özdeğer (Eigenvalue) > 1: Kaiser kriterine göre faktör sayısını belirler. '
            'Faktör yükü ≥ 0.40: İlgili maddenin faktöre kabul edilebilir katkısı. '
            'Açıklanan varyans: Tüm faktörlerin birlikte açıkladığı oran '
            '≥ %50 beklenir.'
        ),
        'apa_example': (
            'KMO = .84, Bartlett χ²(66) = 512.3, p < .001. Varimax döndürme '
            'sonucunda toplam varyansın %58.4\'ünü açıklayan iki faktörlü '
            'yapı elde edilmiştir.'
        ),
        'faq': [
            {
                'q': 'Kaç faktör seçmeliyim?',
                'a': ('Özdeğer > 1 (Kaiser), çizgi grafiği (scree plot) kırılma '
                      'noktası ve %50+ açıklanan varyans kriterlerini birlikte '
                      'değerlendirin. Yorum kolaylığı da önemli bir ölçüttür.'),
            },
            {
                'q': 'Döndürme yöntemi (rotation) nasıl seçilir?',
                'a': ('Faktörler birbirinden bağımsız olduğu varsayılıyorsa '
                      'Varimax (ortogonal); faktörler arasında korelasyon '
                      'bekleniyorsa Oblimin veya Promax (oblique) kullanın.'),
            },
            {
                'q': 'Bir madde birden fazla faktöre yüksek yük verdi, ne yapmalıyım?',
                'a': ('Çift yüklenen (cross-loading) maddeyi her iki faktördeki '
                      'yükü 0.40 eşiğinin üzerindeyse analiz dışında bırakmayı '
                      'değerlendirin; teorik açıdan da anlamlılığını sorgulayın.'),
            },
        ],
        'related_tools': [
            ('cronbach', 'Cronbach Alfa'),
            ('korelasyon', 'Korelasyon Analizi'),
            ('betimsel', 'Betimsel İstatistik'),
        ],
    },

    'wilcoxon': {
        'intro': (
            'Wilcoxon İşaret Testi, iki ilişkili ölçüm arasındaki farkı '
            'değerlendiren parametrik olmayan bir testtir. Bağımlı örneklem '
            't-testinin normallik gerektirmeyen alternatifidir. Fark '
            'puanlarının işaretlerini ve büyüklüklerini dikkate alır; '
            'bu nedenle yalnızca işaret sayısını kullanan işaret testinden '
            'daha güçlüdür.'
        ),
        'when_to_use': (
            'Aynı gruba ait iki ölçümü karşılaştırmak istediğinizde '
            've normallik varsayımı sağlanmıyorsa ya da örneklem '
            'küçükse kullanın. Öntest-sontest tasarımları, eşleştirilmiş '
            'çiftler ve ters denge (counterbalanced) tasarımları için idealdir. '
            'İki gruptan fazlası varsa Friedman Testi tercih edilmelidir.'
        ),
        'assumptions': (
            'Bağımlı çiftler: Her gözlem çifti aynı bireye veya eşleştirilmiş '
            'çifte ait olmalıdır. '
            'Simetri: Fark dağılımı simetrik olmalıdır (ortalama etrafında). '
            'Sıralanabilirlik: Fark puanları sıralanabilir nitelikte olmalıdır.'
        ),
        'how_to_interpret': (
            'W istatistiği: İki yönlü testte küçük W değeri anlamlılığa işaret eder. '
            'p değeri: p < 0.05 iki ölçüm arasında anlamlı fark var demektir. '
            'r (etki büyüklüğü): r = Z / √N; 0.1 küçük, 0.3 orta, 0.5 büyük.'
        ),
        'apa_example': (
            'Sontest puanları öntest puanlarından anlamlı düzeyde yüksektir, '
            'Z = −3.42, p = .001, r = .48.'
        ),
        'faq': [
            {
                'q': 'Wilcoxon mu, bağımlı t-testi mi seçmeliyim?',
                'a': ('Fark puanları normal dağılım gösteriyorsa bağımlı t-testi '
                      'daha güçlüdür. Normallik yoksa veya örneklem küçükse '
                      'Wilcoxon daha güvenilir sonuç verir.'),
            },
        ],
        'related_tools': [
            ('ttesti', 'T-Testi'),
            ('mann-whitney', 'Mann-Whitney U Testi'),
            ('friedman', 'Friedman Testi'),
            ('normallik', 'Normallik Testi'),
        ],
    },

}
