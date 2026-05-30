TARAMA_SEO_CONTENT = {

    'yoktez': {
        'intro': (
            'YÖK Ulusal Tez Merkezi, Türkiye\'deki üniversitelerde kabul edilmiş yüz binlerce '
            'lisansüstü tezi barındıran resmi akademik veritabanıdır. Yüksek lisans, doktora ve '
            'tıpta uzmanlık tezlerini konu, üniversite, yıl ve tez türüne göre filtreleyerek '
            'saniyeler içinde tarayabilirsiniz. Analizus YÖK Tez aracı, bu veritabanına filtrelenmiş '
            'erişim sağlar; arama sonuçlarını Excel veya TXT olarak indirmenize, e-posta ile '
            'almanıza ya da bibliometrik analize aktarmanıza olanak tanır.'
        ),
        'when_to_use': (
            'Tez konusu belirleme aşamasında benzer çalışmaları keşfetmek ve araştırma '
            'boşluklarını tespit etmek için kullanın. Belirli bir üniversite ya da danışmanın '
            'denetimindeki tezleri taramak, tez metodolojilerini karşılaştırmak ve Türkiye '
            'merkezli akademik yazını sistematik biçimde taramak istediğinizde en uygun araçtır. '
            'Yabancı kaynaklı literatür için OpenAlex; Türk hakemli dergi makaleleri için '
            'TR Dizin tarama araçlarını tercih edin.'
        ),
        'assumptions': (
            'Arama sonuçları YÖK\'ün anlık veritabanı görüntüsünü yansıtır; kısıtlanmamış '
            'tezlerin tam metnine YÖK Tez Merkezi üzerinden doğrudan ulaşılabilir. Demo kota '
            'kapsamında en yeni 5 sonuç gösterilir; tüm sonuç setine ihtiyaç duyulursa yöneticiyle '
            'iletişime geçilebilir. "Yıl" filtresi tezin kabul yılını; "Özet/Metin" alanı ise '
            'tezin özet bölümünü kapsar. Türkçe karaktere duyarlı arama için hem Türkçe (ş, ç, ğ) '
            'hem de ASCII karşılıkları denenmelidir.'
        ),
        'how_to_interpret': (
            'Toplam sonuç sayısı, seçilen kriterlere uyan tez sayısını gösterir ve alandaki '
            'çalışılmışlık düzeyini ortaya koyar. Çok yüksek sonuç, arama teriminin geniş '
            'tutulduğuna; çok düşük sonuç ise konunun az incelendiğine ya da farklı bir '
            'terminoloji kullanıldığına işaret edebilir. Aynı danışmanın birden fazla tezi '
            'yönetmiş olması o alana hakimiyetini gösterir. Tez türü dağılımını inceleyerek '
            'hangi akademik düzeyde (yüksek lisans/doktora) daha fazla çalışma yapıldığını '
            'belirleyebilirsiniz.'
        ),
        'apa_example': (
            'Yazar, A. A. (2022). Tez başlığı: Alt başlık [Doktora tezi, Gazi Üniversitesi]. '
            'YÖK Ulusal Tez Merkezi. https://tez.yok.gov.tr/'
        ),
        'faq': [
            {
                'q': 'Tam metin teze nasıl ulaşabilirim?',
                'a': (
                    'Analizus yalnızca künye bilgilerini (başlık, yazar, yıl, özet, danışman) '
                    'gösterir. Tam metin erişim için YÖK Tez Merkezi\'ni ziyaret edin; '
                    'araştırmacı tarafından kısıtlanmamış tezlerde PDF indirme bağlantısı mevcuttur.'
                ),
            },
            {
                'q': 'Neden yalnızca en yeni 5 tez gösteriliyor?',
                'a': (
                    'Analizus demo veri politikası kapsamında en yeni 5 sonucu ücretsiz sunar. '
                    'Tüm sonuç setine ihtiyaç duyuyorsanız info@analizus.com adresinden '
                    'toplu veri talebi oluşturabilirsiniz.'
                ),
            },
            {
                'q': 'Doktora ile yüksek lisans tezlerini ayrı tarayabilir miyim?',
                'a': (
                    'Evet. "Tez Türü" filtresinden Doktora, Yüksek Lisans veya Tıpta Uzmanlık '
                    'seçeneklerini kullanarak yalnızca ilgili tür için arama yapabilirsiniz.'
                ),
            },
            {
                'q': 'Aramanın sonucu çok az çıktı, ne yapabilirim?',
                'a': (
                    'Arama terimini genişletin (kelime sayısını azaltın), eş anlamlı terimlerle '
                    'tekrar deneyin ve Türkçe karakter farklılıklarını göz önünde bulundurun. '
                    'Yıl aralığı filtresini de genişletmek sonuç sayısını artırabilir.'
                ),
            },
        ],
        'related_tools': [
            ('/openalex/', 'OpenAlex Tarama'),
            ('/trdizin/', 'TR Dizin Tarama'),
            ('/oaipmh/', 'Üniversite Tez Arşivi'),
        ],
    },

    'openalex': {
        'intro': (
            'OpenAlex, 240 milyondan fazla akademik yayını ücretsiz erişime açan, Microsoft '
            'Academic ve Semantic Scholar\'ın devamı niteliğindeki açık kaynaklı bir bilimsel '
            'veritabanıdır. Makaleler, kitaplar, tezler ve konferans bildirileri dahil kapsamlı '
            'bir yayın yelpazesini içerir. Analizus OpenAlex Tarama aracı; başlık, özet, yazar, '
            'dergi, ülke ve yıl filtresiyle AND/OR Boolean sorguları oluşturmanızı, demo sonuçları '
            'Excel veya TXT olarak indirmenizi ve bibliometrik analize aktarmanızı sağlar.'
        ),
        'when_to_use': (
            'Sistematik literatür taraması için uluslararası kaynaklara erişmek, atıf verisi ve '
            'araştırma eğilimlerini analiz etmek, belirli bir dergi veya kurumun yayın üretimini '
            'incelemek istediğinizde kullanın. Yüksek lisans ve doktora tez yazımında yabancı '
            'kaynak taramasında güçlü bir başlangıç noktasıdır. Türk hakemli dergi makaleleri '
            'için TR Dizin; Türkiye\'deki lisansüstü tezler için YÖK Tez aracını tercih edin. '
            '100+ sonuçlu aramalarda Bibliometrik Analiz aracıyla PDF rapor alabilirsiniz.'
        ),
        'assumptions': (
            'OpenAlex, Web of Science veya Scopus\'tan farklı olarak yayıncı veya abonelik '
            'kısıtlaması içermez; ancak bazı yayınların özeti veya tam metni veri kaynağında '
            'eksik olabilir. Sonuçlar OpenAlex\'in indekslediği kaynaklarla sınırlıdır; bölgesel '
            'ya da küçük dergilerde kapsam daha dar olabilir. Demo kota kapsamında ilk 5 sonuç '
            'gösterilir; tüm veri setine ihtiyaç için tam veri talebi oluşturulabilir.'
        ),
        'how_to_interpret': (
            'Toplam sonuç sayısı, sorgunuza uyan yayın sayısını gösterir. Çok yüksek sayılar '
            'aramanın geniş tutulduğuna işaret eder; kurum, yıl veya dergi filtresi ekleyerek '
            'daraltabilirsiniz. Atıf sayısı (cited_by_count) yayının akademik etkisini '
            'gösterir; h-indeks ve ortalama atıf gibi ileri metriklere Bibliometrik Analiz '
            'aracıyla ulaşabilirsiniz. Açık erişim rozeti (Open Access), tam metne '
            'ücretsiz ulaşılabileceğini belirtir.'
        ),
        'apa_example': (
            'Yazar, A. A., & Yazar, B. B. (2023). Makale başlığı. '
            'Dergi Adı, cilt(sayı), başlangıç-bitiş sayfaları. https://doi.org/...'
        ),
        'faq': [
            {
                'q': 'OpenAlex ile Google Scholar arasındaki fark nedir?',
                'a': (
                    'Google Scholar tam metin web taraması yapar ve sonuçlara erişimde API kısıtlaması '
                    'bulunur. OpenAlex yapılandırılmış üst veri (metadata) sağlar ve API ile '
                    'programatik erişime olanak tanır. Analizus bu API\'yi soyutlayarak kodlama '
                    'bilgisi gerektirmeden veri çekmenizi sağlar.'
                ),
            },
            {
                'q': 'Arama sonuçlarını Bibliometrik Analiz\'e nasıl aktarırım?',
                'a': (
                    '100 veya daha fazla sonuç döndüren aramalarda sonuç alanında '
                    '"Bibliometrik Analiz İstiyorum" butonu belirir. Bu butona tıkladığınızda '
                    'demo rapor (3 grafik PDF) e-posta adresinize gönderilir.'
                ),
            },
            {
                'q': 'Yalnızca belirli bir dergideki yayınları arayabilir miyim?',
                'a': (
                    'Evet, sorgu oluşturucuda "Kaynak / Dergi" alanını seçip dergi adını girerek '
                    'yalnızca o dergideki yayınları listeleyebilirsiniz. '
                    'Birden fazla dergi için OR operatörüyle birleştirin.'
                ),
            },
            {
                'q': 'Neden bazı makalelerin özeti görünmüyor?',
                'a': (
                    'Özet bilgisi OpenAlex\'in veri kaynağından gelmektedir; bazı yayıncılar özet '
                    'verisini paylaşmadığı için bu alan boş görünebilir. Tam metne erişmek için '
                    'DOI bağlantısını kullanın.'
                ),
            },
        ],
        'related_tools': [
            ('/trdizin/', 'TR Dizin Tarama'),
            ('/yoktez/', 'YÖK Tez Tarama'),
            ('/bibliometrics/', 'Bibliometrik Analiz'),
        ],
    },

    'trdizin': {
        'intro': (
            'TR Dizin, TÜBİTAK ULAKBİM tarafından yönetilen Türkiye\'nin ulusal akademik atıf '
            've dizin veritabanıdır. Türkçe ve İngilizce yayın yapan hakemli Türk dergilerini '
            've bu dergilerde yer alan makaleleri kapsar. Analizus TR Dizin Tarama aracı, '
            'Boolean operatörleriyle (AND, OR) çok alanlı sorgular oluşturmanıza; başlık, '
            'özet ve anahtar kelime alanlarında gelişmiş arama yapmanıza, demo sonuçları '
            'Excel veya TXT olarak indirmenize olanak tanır.'
        ),
        'when_to_use': (
            'Tezinizin "Yerli Kaynaklar" bölümü için Türk akademik dergilerde yayımlanmış '
            'makaleleri sistematik biçimde taramak istediğinizde kullanın. TR Dizin kapsamındaki '
            'dergiler ULAKBİM kriterlerini karşıladığından akademik değerlendirmelerde '
            'güvenilir kaynak kabul edilir. Uluslararası literatür için OpenAlex; '
            'lisansüstü tezler için YÖK Tez aracını tercih edin.'
        ),
        'assumptions': (
            'Yalnızca TR Dizin endeksinde yer alan hakemli Türk dergiler taranır; '
            'uluslararası dergilerdeki Türk yazarlı makaleler bu kapsamın dışındadır. '
            'Boolean aramalarda boşlukla ayrılmış birden fazla kelime her birini AND ile '
            'birleştirerek arar. Demo kota kapsamında en yeni 5 makale gösterilir; '
            'tüm veri setine ihtiyaç için tam veri talebi oluşturulabilir.'
        ),
        'how_to_interpret': (
            'Toplam sonuç sayısı TR Dizin\'deki eşleşen makale sayısını gösterir. '
            'Sonuç bulunamazsa söz konusu konunun Türk dergilerinde az işlendiğine ya da '
            'farklı terim kullanıldığına işaret edebilir; eş anlamlılarla tekrar deneyin. '
            'DOI bağlantısı mevcut makalelere doğrudan tam metin erişim sağlanabilir. '
            'Aynı yazarın birden fazla makalesi o alandaki uzman araştırmacıları gösterir.'
        ),
        'apa_example': (
            'Yazar, A. A., & Yazar, B. B. (2021). Makale başlığı. '
            'Dergi Adı, cilt(sayı), başlangıç-bitiş. https://doi.org/...'
        ),
        'faq': [
            {
                'q': 'TR Dizin ile YÖK Tez arasındaki fark nedir?',
                'a': (
                    'TR Dizin hakemli dergi makalelerini kapsar; YÖK Tez ise yüksek lisans ve '
                    'doktora tezlerini içerir. İkisi birbirini tamamlar; kapsamlı bir literatür '
                    'taramasında her ikisinin de kullanılması önerilir.'
                ),
            },
            {
                'q': 'Boolean arama nasıl kullanılır?',
                'a': (
                    'Sorgu oluşturucuya birden fazla kriter ekleyin. AND operatörü her iki '
                    'terimin aynı anda bulunmasını; OR operatörü ise en az birinin bulunmasını '
                    'şart koşar. Örneğin "psikoloji AND kaygı" ile başlıkta her iki kelimeyi '
                    'birden içeren makaleler listelenir.'
                ),
            },
            {
                'q': 'Arama Türkçe mi İngilizce mi yapmalıyım?',
                'a': (
                    'TR Dizin her iki dili de destekler. Türkçe makale başlıkları için Türkçe, '
                    'İngilizce başlıklar veya anahtar kelimeler içeren makaleler için İngilizce '
                    'arama yapın. Her iki dilde de ayrı ayrı denemek en kapsamlı sonucu verir.'
                ),
            },
            {
                'q': 'Makale tam metnine nasıl erişebilirim?',
                'a': (
                    'Analizus yalnızca künye ve özet bilgisini gösterir. Tam metin için '
                    'DOI bağlantısını kullanın ya da TR Dizin resmi sitesinden '
                    'dergi linkini takip edin.'
                ),
            },
        ],
        'related_tools': [
            ('/yoktez/', 'YÖK Tez Tarama'),
            ('/openalex/', 'OpenAlex Tarama'),
        ],
    },

    'oaipmh': {
        'intro': (
            'Üniversite Tez Arşivi, ODTÜ, İTÜ, Sabancı, Akdeniz ve Dokuz Eylül dahil 19 Türk '
            'üniversitesinin açık erişim depolarına tek noktadan bağlanan bir tarama aracıdır. '
            'OAI-PMH (Open Archives Initiative Protocol for Metadata Harvesting) protokolü '
            'sayesinde tez başlığı, özet, yazar ve yıl bilgilerine doğrudan üniversite '
            'sunucularından ulaşırsınız. Hem anahtar kelimeyle hedefli arama hem de seçilen '
            'üniversitenin tüm arşivini toplu tarama seçenekleri mevcuttur.'
        ),
        'when_to_use': (
            'Belirli bir üniversitenin tez arşivini bütüncül olarak incelemek ya da '
            'YÖK Tez Merkezi\'nde tam metin erişimi olmayan tezlere ulaşmak istediğinizde '
            'kullanın. Üniversitelerin kendi arşivlerinde yer alan tezler zaman zaman '
            'YÖK veritabanından daha güncel bilgi içerebilir. Ulusal kapsam için '
            'YÖK Tez Tarama; uluslararası akademik literatür için OpenAlex aracını '
            'tercih edin.'
        ),
        'assumptions': (
            'Yalnızca OAI-PMH protokolünü destekleyen 19 Türk üniversitesinin arşivi '
            'taranabilir; tüm Türk üniversitelerini kapsayan ulusal bir dizin değildir. '
            'Üniversitelerin arşiv altyapısına bağlı olarak özetler ya da metadata '
            'eksik olabilir. Toplu tarama (browse) modunda büyük arşivlerde işlem birkaç '
            'dakika sürebilir. Demo kota kapsamında ilk 5 sonuç gösterilir; tüm arşiv '
            'için toplu veri talebi oluşturulabilir.'
        ),
        'how_to_interpret': (
            'Toplam sonuç sayısı, seçilen üniversite arşivindeki eşleşen tez sayısını '
            'gösterir. Sonuç bulunamazsa üniversitenin arşiv altyapısı geçici olarak '
            'erişilemez durumda ya da o konuda yayımlanmış tez bulunmuyor olabilir; '
            'farklı terimlerle veya başka bir üniversite seçerek tekrar deneyin. '
            'Özet bilgisi eksikse tezin tam başlığı ve yazarıyla ilgili üniversitenin '
            'kütüphane sisteminden detaya ulaşabilirsiniz.'
        ),
        'apa_example': (
            'Yazar, A. A. (2021). Tez başlığı [Yüksek lisans tezi, Orta Doğu Teknik Üniversitesi]. '
            'ODTÜ Açık Arşiv. http://etd.lib.metu.edu.tr/...'
        ),
        'faq': [
            {
                'q': 'Hangi üniversiteler kapsama dahil?',
                'a': (
                    'Afyon Kocatepe, Akdeniz, Çukurova, Dokuz Eylül, Ege, Gazi, Hacettepe, '
                    'İnönü, İstanbul Teknik, İstanbul, Karadeniz Teknik, Kocaeli, Marmara, '
                    'Mersin, ODTÜ, Pamukkale, Sabancı, Selçuk ve Uludağ üniversiteleri '
                    'desteklenmektedir.'
                ),
            },
            {
                'q': 'YÖK Tez Merkezi ile bu araç arasındaki fark nedir?',
                'a': (
                    'YÖK Tez Merkezi tüm Türk üniversitelerinin lisansüstü tezlerini merkezi '
                    'olarak toplar. Üniversite Tez Arşivi ise üniversitelerin kendi OAI-PMH '
                    'sunucularına doğrudan bağlanır; bazı üniversite arşivlerinde YÖK\'te '
                    'bulunmayan ek metadata veya lisans tezleri yer alabilir.'
                ),
            },
            {
                'q': '"Tüm tezleri getir" seçeneği ne kadar sürer?',
                'a': (
                    'Büyük arşivlerde (örn. ODTÜ, İTÜ) toplu tarama birkaç dakika sürebilir. '
                    'Arama devam ederken sayfadan ayrılsanız da job tamamlandığında '
                    'geri döndüğünüzde sonuçlar otomatik gösterilir.'
                ),
            },
            {
                'q': 'Bazı tezlerin özeti neden görünmüyor?',
                'a': (
                    'Özet bilgisi üniversitenin OAI-PMH kaydından alınmaktadır. Arşivleme '
                    'sırasında özet girilmemiş ya da metadata eksik kaydedilmiş tezlerde '
                    'bu alan boş görünebilir. Tez başlığı üzerinden üniversitenin '
                    'kütüphane sisteminden tam künyeye ulaşabilirsiniz.'
                ),
            },
        ],
        'related_tools': [
            ('/yoktez/', 'YÖK Tez Tarama'),
            ('/openalex/', 'OpenAlex Tarama'),
            ('/trdizin/', 'TR Dizin Tarama'),
        ],
    },

    'bibliometrics': {
        'intro': (
            'Bibliometrik analiz, akademik yayınları istatistiksel yöntemlerle inceleyen ve bir '
            'araştırma alanının yapısını, eğilimlerini ve etkisini sayısal olarak ortaya koyan '
            'bir yöntemdir. Yayın sayısı, atıf örüntüleri, yazar üretkenliği, dergi dağılımı ve '
            'kurumsal işbirliği gibi göstergeler aracılığıyla alana ilişkin bütünsel bir tablo '
            'çizilir. Analizus Bibliometrik Analiz aracı, Web of Science, Scopus veya BibTeX '
            'formatında dışa aktarılan veri dosyalarından otomatik olarak 10 farklı analiz üretir '
            've sonuçları tek bir PDF raporda sunar.'
        ),
        'when_to_use': (
            'Sistematik derleme veya meta-analiz çalışmalarında araştırma alanını haritalandırmak '
            'için kullanın. Tez veya makale literatür bölümünde alandaki yayın trendlerini, '
            'öncü araştırmacıları ve kilit dergileri sayısal olarak göstermek istediğinizde '
            'idealdir. Proje önerisinde araştırma boşluğunu kanıtlamak, belirli bir zaman '
            'aralığındaki entelektüel birikimi görselleştirmek ve işbirliği ağlarını analiz '
            'etmek için de tercih edilir. Ham veri kaynağı olarak WoS veya Scopus\'tan '
            'dışa aktarılmış bir CSV/BibTeX dosyası gerekir.'
        ),
        'assumptions': (
            'Analiz sonuçlarının kalitesi doğrudan girdi dosyasının kalitesine bağlıdır. '
            'Eksik veya tutarsız yazar adları, dergi kısaltmaları veya kayıp atıf bilgileri '
            'sonuçları etkileyebilir. WoS ve Scopus kayıtları farklı alan adları kullandığından '
            'platform uyumluluğunu kontrol edin. Lotka kanunu analizi en az 30 farklı yazar '
            'gerektirir; daha küçük veri setlerinde yorum yaparken dikkatli olunmalıdır. '
            'Kelime bulutu ve anahtar kelime analizi; başlık, anahtar kelime ve özet '
            'alanlarının dolu olduğu kayıtlar için daha doğru sonuç verir.'
        ),
        'how_to_interpret': (
            'Yayın trendi grafiği alanın büyüme hızını gösterir; ani artışlar yeni araştırma '
            'ilgi odaklarına işaret edebilir. H-index, en az h atıf almış h yayına sahip olmayı '
            'ifade eder; bireysel yazarlar için etkiyi ölçer. Bradford kanunu dağılımında çekirdek '
            'dergilere odaklanmak literatür takibini kolaylaştırır. Ortak yazarlık ağında merkezi '
            'konumdaki yazarlar alandaki köprü araştırmacıları temsil eder. Ülke/kurum '
            'dağılımı araştırmanın coğrafi yoğunlaşmasını gösterir.'
        ),
        'apa_example': (
            'Araştırmacı, A. A., & Ortak, B. B. (2023). Eğitim bilimleri alanında '
            'bibliometrik analiz: 2010–2023 dönemine ilişkin bir değerlendirme. '
            'Eğitim ve Bilim, 48(215), 1–25. https://doi.org/10.15390/EB.2023.XXXXX'
        ),
        'faq': [
            {
                'q': 'Hangi dosya formatları destekleniyor?',
                'a': (
                    'Web of Science\'dan "Tab-delimited (Win, UTF-8)" formatında; '
                    'Scopus\'tan CSV formatında dışa aktarılan dosyalar ve BibTeX (.bib) '
                    'dosyaları desteklenmektedir. OpenAlex tarama aracından indirilen '
                    'Excel dosyaları da doğrudan yüklenebilir.'
                ),
            },
            {
                'q': 'Kaç kayıtla analiz yapabilirim?',
                'a': (
                    'Demo modda ilk 3 grafiği ücretsiz alırsınız; tam rapor (10 grafik) '
                    'için sipariş oluşturabilirsiniz. Veri seti büyüklüğü konusunda bir '
                    'üst sınır yoktur; ancak çok büyük dosyalar (10.000+ kayıt) işlem '
                    'süresini uzatabilir.'
                ),
            },
            {
                'q': 'Sistematik derleme için yeterli mi?',
                'a': (
                    'Bibliometrik analiz sistematik derlemenin nicel bölümünü destekler; '
                    'araştırma alanını haritalandırmak ve anahtar kaynakları belirlemek '
                    'için güçlü bir araçtır. Ancak tam sistematik derleme; PRISMA akış '
                    'şeması, dahil etme/dışlama kriterleri ve kalite değerlendirmesi gibi '
                    'ek adımlar gerektirir.'
                ),
            },
            {
                'q': 'Hangi analizler raporlara dahil?',
                'a': (
                    'Yayın trendi, en üretken yazarlar, en çok yayın yapan dergiler, '
                    'ülke/kurum dağılımı, anahtar kelime bulutu, ortak yazarlık ağı, '
                    'Lotka kanunu, Bradford kanunu, h-index dağılımı ve yıllık atıf '
                    'trendi olmak üzere 10 farklı analiz tek PDF\'de sunulur.'
                ),
            },
        ],
        'related_tools': [
            ('/openalex/', 'OpenAlex Yayın Tarama'),
            ('/trdizin/', 'TR Dizin Tarama'),
            ('/yoktez/', 'YÖK Tez Tarama'),
        ],
    },

    'semanticscholar': {
        'intro': (
            'Semantic Scholar, Allen Institute for AI tarafından geliştirilen ücretsiz ve açık '
            'akademik arama motorudur. 200 milyondan fazla yayını kapsayan veritabanı; Web of '
            'Science, Scopus, PubMed, arXiv ve IEEE Xplore dahil tüm büyük akademik '
            'platformlardaki çalışmalara erişim sağlar. Analizus Semantic Scholar Kazıma aracı, '
            'kurumsal abonelik gerektirmeksizin anahtar kelime, yazar adı, araştırma alanı ve '
            'yıl aralığı ile gelişmiş arama yapmanızı; sonuçları Excel veya TXT olarak '
            'indirmenizi sağlar. DOI\'si olan kayıtlar CrossRef ile otomatik zenginleştirilir.'
        ),
        'when_to_use': (
            'Web of Science veya Scopus kurumsal aboneliğiniz olmadığında kapsamlı literatür '
            'taraması yapmak için idealdir. Tez veya makale literatür bölümünde uluslararası '
            'yayınları sistematik olarak derlemek, belirli bir araştırma alanındaki güncel '
            'çalışmaları atıf sayısına göre sıralamak ve bibliometrik analiz için ham veri '
            'toplamak amacıyla kullanabilirsiniz. Açık erişimli yayınlar için PDF bağlantısı '
            'da sunulduğundan tam metne ücretsiz ulaşmak mümkündür.'
        ),
        'assumptions': (
            'Semantic Scholar veritabanı her yayını kapsamamaktadır; özellikle yerel dergiler '
            've Türkçe yayınlar sınırlı olabilir. Bunun için TR Dizin veya OAI-PMH araçlarını '
            'tercih edin. Arama sonuçları alaka düzeyine göre sıralanır; yıl filtresi lokal '
            'olarak uygulandığından toplam sonuç sayısı daha az görünebilir. Tek sorguda en '
            'fazla 1.000 kayıt alınabilir (API sınırı); daha fazlası için birden fazla '
            'sorgu kullanın.'
        ),
        'how_to_interpret': (
            'Atıf sayısı (cited by) yayının alanda ne kadar yankı uyandırdığını gösterir; '
            'ancak yeni yayınların atıf sayısı düşük olabilir. Araştırma alanı (fields of '
            'study) Semantic Scholar\'ın yapay zeka tabanlı sınıflandırmasıdır, yazar '
            'tarafından girilmez. OA PDF bağlantısı varsa yayın açık erişimlidir ve '
            'ücretsiz tam metne ulaşılabilir. CrossRef ile zenginleştirilmiş kayıtlarda '
            'kurum ve yayıncı bilgisi de yer alır.'
        ),
        'apa_example': (
            'Smith, J. A., & Johnson, B. (2023). Machine learning applications in '
            'bibliometric analysis: A systematic review. Scientometrics, 128(5), '
            '2891–2915. https://doi.org/10.1007/s11192-023-04567-8'
        ),
        'faq': [
            {
                'q': 'Web of Science\'a alternatif mi?',
                'a': (
                    'Semantic Scholar 200M+ yayınla WoS\'un kapsadığı yayınların büyük bölümünü '
                    'içerir ve ücretsizdir. Ancak WoS\'un atıf analizi, dergi etki faktörü ve '
                    'belirli alan indekslerine göre filtreleme gibi özelleşmiş araçlarına sahip '
                    'değildir. Genel literatür taraması ve veri toplama için güçlü bir alternatiftir.'
                ),
            },
            {
                'q': 'Türkçe yayınları buluyor mu?',
                'a': (
                    'Uluslararası indeksli Türkçe dergiler (SCI, SSCI, ESCI kapsamındakiler) '
                    'Semantic Scholar\'da yer alır. Yalnızca TR Dizin kapsamındaki yerel hakemli '
                    'dergiler için TR Dizin Kazıma aracını kullanmanız önerilir.'
                ),
            },
            {
                'q': 'CrossRef zenginleştirme ne demek?',
                'a': (
                    'DOI\'si olan her kayıt için CrossRef API\'ye sorgu atılır ve kurum, '
                    'yayıncı, konu sınıflandırması gibi ek bilgiler otomatik olarak eklenir. '
                    'Bu işlem demo sonuçlarında (ilk 5 kayıt) uygulanır.'
                ),
            },
            {
                'q': 'Neden bazı sorgularda az sonuç geliyor?',
                'a': (
                    'Yıl filtresi API düzeyinde değil, indirilen veriye lokal olarak uygulanır. '
                    'API en fazla 1.000 kayıt döndürdüğünden geniş bir tarih aralığında çok '
                    'sayıda yayın varsa filtre sonrası kayıt azalabilir. Aramayı daha spesifik '
                    'anahtar kelimelerle daraltmayı deneyin.'
                ),
            },
        ],
        'related_tools': [
            ('/openalex/', 'OpenAlex Yayın Tarama'),
            ('/trdizin/', 'TR Dizin Tarama'),
            ('/bibliometrics/', 'Bibliometrik Analiz'),
        ],
    },

    'tableau': {
        'intro': (
            'Tableau, akademik araştırmalarda veri görselleştirme, tez bulgularını sunma ve '
            'interaktif rapor hazırlama amacıyla kullanılan profesyonel bir iş zekâsı (BI) '
            'aracıdır. Sürükle-bırak arayüzüyle karmaşık veri setlerinden grafik, harita ve '
            'dashboard oluşturmak mümkündür; programlama bilgisi gerekmez. Bu sayfadaki '
            'dashboard\'lar TR Dizin, TÜİK ve örnek satış verisi üzerinde hazırlanmış '
            'interaktif çalışmalardır; filtreleyebilir, yakınlaştırabilir ve tam ekranda '
            'inceleyebilirsiniz.'
        ),
        'when_to_use': (
            'Tez bulgularınızı görsel olarak sunmak, büyük veri setlerindeki örüntüleri '
            'keşfetmek ya da akademik bir raporu etkileşimli hâle getirmek istediğinizde '
            'Tableau\'dan yararlanabilirsiniz. Bibliyometrik analizlerde yayın trendleri, '
            'ülke ve kurum dağılımları; sağlık araştırmalarında hasta veya vaka dağılımları; '
            'sosyal bilimlerde demografik karşılaştırmalar için özellikle güçlüdür. '
            'Kendi veri setiniz için özel bir dashboard hazırlatmak isterseniz '
            'uzman analistlerimizle iletişime geçebilirsiniz.'
        ),
        'assumptions': (
            'Bu sayfadaki dashboard\'lar Tableau Public üzerinde barındırılmakta olup '
            'yüklenmeleri internet bağlantısına bağlıdır. Görselleştirmeler anlık veri '
            'çekmez; derleme tarihindeki veri kesitini yansıtır. Bazı tarayıcılarda '
            'JavaScript desteği gereklidir; engelleme durumunda "Tam Ekran" bağlantısı '
            'üzerinden Tableau Public\'e doğrudan ulaşılabilir. Dashboard\'lardaki '
            'veriler yalnızca gösterim amaçlıdır; akademik atıf için orijinal veri '
            'kaynağına (TÜİK, TR Dizin) başvurunuz.'
        ),
        'how_to_interpret': (
            'Filtreleri kullanarak belirli yıl, kategori veya bölgeye odaklanın; tüm grafikler '
            'anlık olarak güncellenir. Çubuk veya pasta grafikte bir dilime tıklayarak '
            'diğer panelleri çapraz filtreleyin. Harita dashboard\'larında ilgisini çeken '
            'bölgenin üzerine gelerek detay kartını görüntüleyin. Renk skalasında koyu '
            'tonlar yüksek değerleri, açık tonlar düşük değerleri temsil eder. '
            'Akademik raporlamada dashboard\'dan bir görsel kullanıyorsanız veri kaynağını '
            'dipnotta belirtmeyi unutmayın.'
        ),
        'apa_example': (
            'Analizus. (2024). TR Dizin Sağlık Araştırmaları İnteraktif Dashboard [Tableau '
            'görselleştirmesi]. https://www.analizus.com/tableau-analiz/'
        ),
        'faq': [
            {
                'q': 'Tableau öğrenmek ne kadar sürer?',
                'a': (
                    'Temel sürükle-bırak işlemleri ve basit grafik oluşturmayı birkaç saatte '
                    'öğrenebilirsiniz. Hesaplanan alanlar, LOD ifadeleri ve ileri düzey '
                    'dashboard tasarımı birkaç haftalık pratik gerektirir. Akademik '
                    'araştırmanız için özelleştirilmiş bir dashboard\'u kendiniz '
                    'oluşturmak yerine hazırlattırmak zaman açısından daha verimli olabilir.'
                ),
            },
            {
                'q': 'Tableau ücretsiz mi?',
                'a': (
                    'Tableau Public tamamen ücretsizdir; hazırladığınız görselleştirmeleri '
                    'herkese açık biçimde yayımlamanıza olanak tanır. Tableau Desktop '
                    '(ücretli) ise veriyi gizli tutarak çalışmanızı sağlar. Öğrenciler '
                    'edu e-posta adresiyle Tableau for Students lisansına başvurabilir.'
                ),
            },
            {
                'q': 'Kendi veri setimle dashboard yaptırabilir miyim?',
                'a': (
                    'Evet. Excel, CSV, Scopus, WoS veya TÜİK formatındaki veri dosyanızı '
                    'paylaşmanız yeterlidir. Uzman analistlerimiz araştırmanızın odağına '
                    'uygun interaktif dashboard tasarlar ve Tableau Public veya '
                    'Desktop çıktısı olarak teslim eder. İletişim formundan talebinizi iletebilirsiniz.'
                ),
            },
            {
                'q': 'Dashboard\'lar yüklenmiyorsa ne yapmalıyım?',
                'a': (
                    'Tableau Public\'in sunucularına bağlantı kesildiğinde embed yüklenmeyebilir. '
                    'Sayfayı yenileyin veya her dashboard\'un yanındaki "Tam Ekran" bağlantısına '
                    'tıklayarak Tableau Public\'e doğrudan gidin. Sorun devam ederse '
                    'tarayıcınızın reklam engelleyicisini geçici olarak devre dışı bırakmayı deneyin.'
                ),
            },
        ],
        'related_tools': [
            ('/bibliometrics/', 'Bibliometrik Analiz'),
            ('/trdizin/', 'TR Dizin Tarama'),
            ('/openalex/', 'OpenAlex Tarama'),
        ],
    },
}
