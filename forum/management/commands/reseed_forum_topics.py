"""
Faz 12 — Editoryal forum içeriği: gerçek hesaplardan 12 yeni konu + doğrulanmış
uzman cevabı. Kademeli yayın içindir — tüm liste burada hazır durur, her
çalıştırmada sadece --count kadar YENİ (henüz oluşturulmamış) konu eklenir.

Kaynak: analizus_forum_seed_konular.md (proje kökü)

Kullanım:
    python manage.py reseed_forum_topics --count 3
    docker compose exec web python manage.py reseed_forum_topics --count 3
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from forum.models import Section, Category, Topic, Post


NEW_CATEGORIES = [
    {"slug": "akademik-surec", "title": "Akademik Süreç & Etik"},
    {"slug": "veri-analizi-bi", "title": "Veri Analizi & BI"},
    {"slug": "ai-ml-agentic", "title": "AI / ML / Agentic"},
]


TOPICS = [
    {
        "category_slug": "akademik-surec",
        "subject": "Hakem 2 tüm analizimi SEM ile tekrarlamamı istiyor — zorunda mıyım?",
        "starter": "Arastirmaci_B",
        "first_post": (
            "Q1 bir dergiye gönderdiğim makalede hiyerarşik regresyon kullandım. Hakem 2 "
            "'ilişkiler yapısal eşitlik modeliyle (SEM) test edilmeli' diyor, Hakem 1'in itirazı yok. "
            "Örneklemim 214 kişi — SEM için sınırda. Revizyon mektubunda direnmek mi, yöntemi "
            "SEM'e dönüştürmek mi daha akıllıca? Direneceksem nasıl gerekçelendiririm?"
        ),
        "expert": "TezDanismani_Prof",
        "answer": (
            "Öncelikle: SEM için 'n=200' sık anılan bir eşiktir ama katı bir kural değil — model "
            "karmaşıklığına (gizil değişken sayısına) bağlıdır. 214 kişilik örneklem, az sayıda gizil "
            "değişkenli bir ölçüm modeliyle çalışan bir SEM için genelde yeterli sayılır. Revizyon "
            "mektubunda iki yol var: (1) Hakem 2'nin talebini karşılayıp aynı hipotezleri SEM'de de "
            "test edip iki yöntemin sonuçlarının tutarlı olduğunu göstermek — bu hem hakemi tatmin "
            "eder hem bulgularınızı güçlendirir. (2) Direnmek istiyorsanız, hiyerarşik regresyonun "
            "araştırma sorunuza (özellikle dolaylı/aracı etki iddianız yoksa) neden yeterli olduğunu, "
            "SEM'in ek varsayımlarının (çoklu normallik, örneklem-parametre oranı) neden riskli "
            "olacağını literatür referanslarıyla gerekçelendirin. Editöre yanıt mektubunuzda 'Hakem "
            "2'nin önerisini dikkate aldık, ancak...' diye başlayıp somut istatistiksel gerekçe sunmak, "
            "sessizce reddetmekten çok daha güçlü bir pozisyon."
        ),
    },
    {
        "category_slug": "akademik-surec",
        "subject": "Etik kurul, retrospektif kurum verisi için de bireysel onam istedi — süreç böyle mi işliyor?",
        "starter": "SaglikIst",
        "first_post": (
            "Tezimde hastane kayıtlarından anonimleştirilmiş 2019-2023 dönemine ait retrospektif veri "
            "kullanacağım. Etik kurul her hastadan bireysel onam alınmasını istedi ama beş yıllık kayıtta "
            "hastaların büyük kısmına ulaşmak fiilen imkânsız. Benzer çalışmalarda 'onam muafiyeti' "
            "(waiver) uygulandığını görüyorum — muafiyet başvurusu nasıl yazılır, hangi gerekçeler kabul görüyor?"
        ),
        "expert": "AkademikEtik",
        "answer": (
            "Retrospektif, anonimleştirilmiş kurum verisi için onam muafiyeti yaygın ve genelde kabul "
            "gören bir yol — ama başvuruda üç unsuru açıkça göstermeniz gerekiyor. Birincisi, verinin "
            "gerçekten geri döndürülemez biçimde anonimleştirildiği (kimlik bilgisi, dosya no gibi "
            "doğrudan/dolaylı tanımlayıcıların tamamen kaldırıldığı) teknik olarak tarif edilmeli. "
            "İkincisi, onam almanın 'fiilen imkânsız veya orantısız güçlük' teşkil ettiği "
            "somutlaştırılmalı — sizin durumunuzda '5 yıllık, hastaların büyük kısmına iletişim "
            "bilgisiyle ulaşılamıyor' cümlesi tam bunu karşılıyor, sayısal olarak da destekleyin. "
            "Üçüncüsü, araştırmanın hastalara asgari risk taşıdığı (retrospektif, müdahale içermiyor) "
            "vurgulanmalı. Başvuru dilekçenizde kurumunuzun kendi etik kurul yönergesindeki 'arşiv "
            "verisi' maddesine atıf yapmanız işi kolaylaştırır. Bazı kurullar muafiyet yerine 'genel "
            "bilgilendirme duyurusu' ister — kurulunuzun daha önce onayladığı benzer bir retrospektif "
            "çalışmanın etik onay metnini örnek isteyin, en hızlı yol bu."
        ),
    },
    {
        "category_slug": "akademik-surec",
        "subject": "YÖK Tez yüklemesinde benzerlik raporu %18 çıktı — yöntem bölümü şişiriyor, ne yapmalıyım?",
        "starter": "TezMagduru_A",
        "first_post": (
            "Turnitin/iThenticate raporumda benzerliğin büyük kısmı yöntem bölümünden geliyor — ölçek "
            "maddeleri, standart prosedür cümleleri, istatistik testi tanımları gibi herkesin benzer "
            "yazdığı yerler. Üniversitemin üst sınırı %20 ama danışmanım %15 altını istiyor. Yöntem "
            "bölümünde herkesin neredeyse aynı şeyi yazdığı kısımlar nasıl düşürülür — alıntılama mı "
            "yeterli, yeniden yazım mı gerekiyor?"
        ),
        "expert": "TezDanismani_Prof",
        "answer": (
            "Yöntem bölümü kaynaklı benzerlik yaygın bir durum ama danışmanınızın %15 istemesi haklı — "
            "çünkü raporun kendisi değil, tekil kaynak eşleşmesi kritik olur. Önce raporda hangi tek "
            "kaynaktan kaç puan geldiğine bakın; ölçek maddelerinin birebir alıntısı kaçınılmazdır ve "
            "tırnak içinde referansla verilirse çoğu üniversitede sorun teşkil etmez — ama 'standart "
            "prosedür cümleleri' (örn. normallik testi tanımı gibi) gerçekten yeniden yazılabilir: "
            "cümle yapısını değiştirin, aynı bilgiyi farklı sırada verin, herkesin bildiği genel-geçer "
            "tanımları uzun uzun anlatmak yerine doğrudan sonuca geçin — en sık yapılan hata bu. Ölçek "
            "maddelerinin tam listesini ek (appendix) bölümüne taşımak da ana metindeki benzerliği "
            "düşürür, çünkü bazı üniversiteler ekleri ayrı değerlendirir. %18'den %15'e inmek genelde "
            "2-3 paragrafın yeniden yazımıyla mümkün, kaynak/atıf sorunuysa parafraz + doğru künye yeterli."
        ),
    },
    {
        "category_slug": "akademik-surec",
        "subject": "Danışmanım SPSS istiyor ama verim panel veri — R'da yapıp SPSS diliyle raporlamak sorun olur mu?",
        "starter": "Can_Veri",
        "first_post": (
            "Verim 5 yıllık panel (86 firma × 5 yıl, dengesiz panel). SPSS'te panel veri regresyonu "
            "(sabit/rassal etkiler modeli) fiilen desteklenmiyor, ben de R'da plm paketiyle kurdum. "
            "Danışmanım SPSS dışında yazılım bilmiyor ve çıktıları SPSS formatında görmek istiyor. Jüride "
            "'neden R kullandın' sorusu gelirse nasıl savunurum, yoksa analizi SPSS'in yapabildiği bir "
            "modele mi indirgemeliyim?"
        ),
        "expert": "Ekonometrist",
        "answer": (
            "Analizi SPSS'in yapabildiği bir modele indirgemeyin — panel veri için sabit/rassal etkiler "
            "modelini SPSS'te doğru kuramazsınız, bu bilimsel olarak geri adım olur. Jüri savunmasında "
            "'neden R' sorusuna hazırlıklı olun ama bu aslında güçlü bir cevap: 'Panel veri "
            "ekonometrisinin standart araçlarından R'ı, açık kaynak olması ve Hausman testi/robust "
            "standart hata hesaplamalarını native desteklemesi nedeniyle tercih ettim' demeniz yeterli. "
            "Danışmanınızla ilgili pratik çözüm: SPSS formatında görmek istemesi aslında çıktının "
            "biçimiyle ilgili, yöntemle değil — R çıktılarını (katsayı, standart hata, p değeri, "
            "Hausman/Breusch-Pagan test sonuçları) SPSS'in alışık olduğu APA formatında bir regresyon "
            "tablosuna dönüştürüp sunabilirsiniz; `stargazer` paketiyle bu neredeyse otomatik. Böylece "
            "danışmanınız tanıdık bir tablo görür, siz yöntemsel doğruluktan ödün vermezsiniz."
        ),
    },
    {
        "category_slug": "akademik-surec",
        "subject": "Tez önerimde G*Power ile 128 kişi hesapladım, jüri 300 istedi — nasıl savunurum?",
        "starter": "Psikoloji_Tez",
        "first_post": (
            "Öneri savunmamda güç analizimi (etki büyüklüğü f²=.15, güç=.95, α=.05) sundum, 128 kişi "
            "çıktı. Jüri üyelerinden biri 'sosyal bilimlerde 300 altı örneklem olmaz' dedi. Hocanın "
            "söylediği mi geçerli, hesabın çıktısı mı? Revize önerimde güç analizini nasıl sunmalıyım ki "
            "hem bilimsel hem ikna edici olsun?"
        ),
        "expert": "Dr_Mehmet_Stats",
        "answer": (
            "Hesap yanlış değil — doğru parametrelerle 128 rakamı bir yönteme dayanıyor. Jüri üyesinin "
            "'300 altı olmaz' ifadesi bir kural değil, tecrübeye dayalı genel bir kanı — ama savunmada "
            "bunu göz ardı etmek yerine kullanmanız daha akıllıca. Revize öneride üç şeyi birlikte "
            "sunun: (1) G*Power çıktınızı parametreleriyle (hangi test, hangi etki büyüklüğü, neden bu "
            "etki büyüklüğü — ideal olarak benzer bir önceki çalışmadan referans alınmış) net gösterin. "
            "(2) Beklenen veri kaybı/eksik veri payını (genelde %15-20) ekleyip örneklemi 128'den "
            "~150-160'a çıkarın — bu, jüriye 'sadece minimum hesaba değil pratik gerçekliğe de baktım' "
            "mesajı verir. (3) Alanınızdaki 2-3 emsal makalenin örneklem büyüklüklerini kısaca kıyaslayın. "
            "300'e çıkmak istatistiksel olarak zorunlu değil ama jüriyle çatışmaktansa 'güç analizim + "
            "literatür + veri kaybı payı' üçlüsüyle 150-160 civarı bir orta yol sunmak, hem bilimsel hem "
            "diplomatik en güçlü pozisyon."
        ),
    },
    {
        "category_slug": "akademik-surec",
        "subject": "ChatGPT'ye yazdırdığım analiz yorumlarını jüri fark eder mi — doğrulatmak istiyorum",
        "starter": "Ayse_K",
        "first_post": (
            "İtiraf: bulgular bölümümdeki tablo yorumlarının büyük kısmını ChatGPT yazdı. Savunma "
            "yaklaşıyor ve iki korkum var — yorumlarda fark etmediğim bir istatistik hatası olması ve "
            "jürinin metinden şüphelenmesi. Birine kontrol ettirmek istiyorum, neye baktırmalıyım: "
            "sadece dil mi, sayıların tutarlılığı mı?"
        ),
        "expert": "bunyamin",
        "answer": (
            "İkisi de kontrol edilmeli ama öncelik sırası önemli. Önce sayısal tutarlılık: ChatGPT'nin "
            "en sık yaptığı hata, tablodaki gerçek p değeri/istatistiği yorumlarken yanlış yöne "
            "yorumluyor olması (örn. p=.06'yı 'anlamlı' diye yazması, ya da r=-.42'yi 'güçlü pozitif "
            "ilişki' diye betimlemesi) — bunlar jürinin fark edeceği, savunmayı gerçekten zora sokacak "
            "hatalar. Her yorum cümlesini tablodaki sayıyla tek tek eşleştirip kontrol etmek şart, bu "
            "adımı atlamayın. İkinci olarak dil/üslup: akademik metinde AI'a özgü kalıp ifadeler tekrar "
            "tekrar kullanılmışsa fark edilebilir oluyor — cümleleri kendi analiz sürecinizi yansıtacak "
            "şekilde yeniden ifade etmek hem özgünlük hem sahiplenme açısından iyi olur. Analizus'ta tam "
            "bu ihtiyaç için bir doğrulama hizmeti var — tablodaki sayılarla yorum metnini karşılaştırıp "
            "hem istatistiksel tutarlılık hem dil taraması yapıyoruz, savunmadan önce ikinci bir göz "
            "olarak düşünebilirsiniz."
        ),
    },
    {
        "category_slug": "veri-analizi-bi",
        "subject": "Excel 80 bin satırda yavaşladı — Power Query yeter mi, Power BI'a mı geçmeliyim?",
        "starter": "Planlama_Y",
        "first_post": (
            "Aylık satış raporunu 6 şubeden gelen CSV'leri elle birleştirerek hazırlıyorum, dosya 80 bin "
            "satırı geçti ve her ay yaklaşık 2 günümü alıyor. VLOOKUP'lar çöküyor, dosya donuyor. Power "
            "Query ile mevcut Excel'de mi kalmalıyım, yoksa bu iş artık Power BI işi mi? Geçiş maliyeti "
            "(öğrenme eğrisi + lisans) küçük bir ekip için mantıklı mı?"
        ),
        "expert": "VeriGorselci",
        "answer": (
            "80 bin satır ve aylık tekrarlayan bir birleştirme süreci — bu tam olarak Power Query'nin "
            "çözdüğü problem, Power BI'a geçmeden önce mutlaka deneyin. VLOOKUP'un çökme sebebi her "
            "hücre için tüm tabloyu taraması; Power Query bunun yerine 6 CSV'yi bir sorgu olarak "
            "tanımlayıp otomatik birleştirir (Append Queries), siz sadece 'Yenile' dersiniz, 2 günlük iş "
            "birkaç dakikaya iner — ve bu mevcut Excel lisansınızda zaten var, ek maliyet yok. Power "
            "BI'a geçiş asıl şu durumlarda mantıklı olur: raporu canlı/paylaşılan bir dashboard olarak "
            "sunmanız gerekiyorsa, veri Excel'in pratik sınırlarına (100-200 bin satır üstü yavaşlama) "
            "yaklaşıyorsa, ya da birden fazla kişi aynı veriye interaktif filtreyle bakacaksa. Sizin "
            "durumunuzda önce Power Query ile birleştirmeyi otomatikleştirin, hâlâ yavaşlık yaşarsanız "
            "Power BI Desktop ücretsizdir — asıl maliyet öğrenme eğrisi, o da sürükle-bırak arayüzle "
            "1-2 haftada aşılır."
        ),
    },
    {
        "category_slug": "veri-analizi-bi",
        "subject": "Tableau dashboard'um var ama yönetim hâlâ haftalık Excel istiyor — otomatik besleme kurulur mu?",
        "starter": "SirketSahibi_C",
        "first_post": (
            "Satış verisini Tableau'da gayet iyi görselleştirdim ama genel müdür 'bana Excel gönder' "
            "diyor. Her hafta dashboard'dan elle export alıp mail atıyorum. Tableau'dan zamanlanmış "
            "Excel/PDF çıktısı almanın ya da bu döngüyü tamamen otomatikleştirmenin bir yolu var mı? "
            "Tableau Server yok, sadece Desktop lisansım var."
        ),
        "expert": "StratejiAnalisti",
        "answer": (
            "Tableau Desktop'ta (Server/Cloud olmadan) yerleşik bir zamanlanmış-gönderim özelliği yok — "
            "bu Tableau'nun bilerek Server/Cloud'a bıraktığı bir yetenek. Ama elle export döngüsünü "
            "otomatikleştirmenin pratik bir yolu var: verinin kaynağına bir zamanlanmış görev (Windows "
            "Task Scheduler + Tableau'nun `tabcmd export` komut satırı özelliği, Desktop lisansıyla da "
            "çalışır) kurup PDF/görsel çıktıyı otomatik üretip mail eklentisi olarak göndermek — bunun "
            "için basit bir script yazmanız yeterli, Server lisansı almanıza gerek kalmaz. Daha kalıcı "
            "çözüm ise genel müdürünüze 'Excel gönder' yerine dashboard'un web linkini kullanmayı "
            "önermek — şirket içi bir paylaşım alanına yayınlayıp linki gönderirseniz, o da güncel "
            "veriyi her açtığında görür, siz hiç export almazsınız. Kısa vadede pratik çözüm script "
            "otomasyonu, orta vadede asıl hedef Excel alışkanlığından dashboard alışkanlığına geçiş "
            "olmalı — bu genelde yönetimin ilk dashboard deneyiminin ne kadar kolay olduğuna bağlı."
        ),
    },
    {
        "category_slug": "spss",
        "subject": "Anket verimde ters kodlu maddeleri işlemeden ölçek puanı hesaplamışım — analizleri baştan mı alacağım?",
        "starter": "MetodologiUzmani",
        "first_post": (
            "40 maddelik ölçekte 8 tanesinin ters kodlu (reverse-coded) olduğunu fark etmeden ham "
            "haliyle toplam puan almışım, güvenirlik ve korelasyon analizlerini de bu puanla "
            "raporlamışım. Cronbach alfa .58 çıkmıştı, şimdi sebebini anladım. Hangi sonuçlar "
            "kurtarılabilir, hangileri kesin yeniden hesaplanmalı? Benzer hata yapıp fark eden oldu mu?"
        ),
        "expert": "figen",
        "answer": (
            "Bu, ölçek çalışmalarında en sık rastlanan hatalardan biri — yalnız değilsiniz, ama "
            "maalesef kısmi kurtarma mümkün değil, baştan almanız gerekiyor. Sebebi şu: ters kodlu "
            "maddeler düzeltilmeden toplam puana dahil edilince, o maddeler ölçeğin geri kalanıyla "
            "negatif korelasyon veriyor — bu da doğrudan Cronbach alfa'yı düşürüyor (sizin .58'iniz "
            "bunun klasik belirtisi) ve toplam puanın kendisini anlamsızlaştırıyor. SPSS'te Transform > "
            "Recode into Different Variables ile 8 maddeyi (5'li Likert'te yeni değer = 6-eski değer "
            "formülüyle) düzeltip yeni değişkenler oluşturun, sonra toplam puanı bu düzeltilmiş "
            "maddelerle yeniden hesaplayın. Kurtarılamayan analizler: Cronbach alfa, madde-toplam "
            "korelasyonları, toplam puana dayalı tüm korelasyon/regresyon/t-testi/ANOVA sonuçları — "
            "bunların hepsi yeniden çalıştırılmalı. Kurtarılabilecek tek şey: ters kodlamadan "
            "etkilenmeyen demografik betimsel istatistikleriniz. İyi haber: veri toplama tekrarlamanıza "
            "gerek yok, sadece recode + yeniden çalıştırma — genelde 1 gün sürer."
        ),
    },
    {
        "category_slug": "ai-ml-agentic",
        "subject": "12 bin Türkçe müşteri yorumum var — duygu analizi için hazır model mi, fine-tune mu?",
        "starter": "PythonDev_X",
        "first_post": (
            "E-ticaret sitemizin yaklaşık 12 bin ürün yorumunu olumlu/olumsuz/nötr olarak sınıflamak "
            "istiyorum. Türkçe hazır modeller (BERTurk tabanlı) yeterli olur mu, yoksa kendi verimle "
            "fine-tune mu etmeliyim? Etiketli verim yok — etiketleme maliyetine girmeden başlamanın bir "
            "yolu var mı? Bütçe sınırlı, GPU yok."
        ),
        "expert": "PythonGurusu",
        "answer": (
            "12 bin yorum ve etiketli veri yokken doğru sıra şu: önce hazır bir Türkçe duygu analizi "
            "modeliyle (Hugging Face'te hazır BERTurk-tabanlı modeller) tüm veriyi sınıflandırın, GPU "
            "gerekmez — CPU'da 12 bin satır birkaç saat içinde biter, Google Colab'ın ücretsiz "
            "GPU'suyla dakikalar sürer. Sonuçları elle rastgele 200-300 örneklem üzerinde kontrol edip "
            "doğruluk oranını ölçün — e-ticaret yorumları gibi genel dilde hazır modeller genelde "
            "%80-85 civarı isabet veriyor, çoğu iş ihtiyacı için yeterli. Doğruluk yetersiz çıkarsa "
            "(sektörünüze özgü jargon çoksa) fine-tune'a geçin ama tam veriyi etiketletmeden: hazır "
            "modelin en çok kararsız kaldığı (olasılık skoru %50'ye yakın) 500-1000 örneği elle "
            "etiketleyip sadece onlarla fine-tune yapmak (active learning mantığı) maliyeti ciddi "
            "düşürür. Özetle: sıfırdan etiketleme + fine-tune bütçenizde şu an gereksiz bir yatırım — "
            "önce hazır modelle başlayın, gerçek ihtiyaç ortaya çıkarsa hedefli fine-tune'a geçin."
        ),
    },
    {
        "category_slug": "ai-ml-agentic",
        "subject": "Üretim hattı sensör verisinden arıza tahmini — 3 yılda sadece 41 arıza kaydım var, ML mümkün mü?",
        "starter": "Muhendislik_R",
        "first_post": (
            "Fabrikada 12 sensörden dakikalık veri topluyoruz (3 yıl birikti) ama toplam arıza sayısı "
            "41. Bu kadar dengesiz bir sınıfla arıza tahmin modeli kurulabilir mi, yoksa anomali "
            "tespiti gibi başka bir çerçeveye mi geçmeliyim? Yönetime 'AI yapalım' demeden önce neyin "
            "gerçekçi olduğunu bilmek istiyorum."
        ),
        "expert": "ModelEgitmeni",
        "answer": (
            "41 arıza / milyonlarca dakikalık normal veri — bu oran klasik sınıflandırma için gerçekten "
            "çok dengesiz, doğrudan bir Random Forest/XGBoost'a atarsanız model 'hep arıza yok' "
            "diyerek yüksek accuracy ama sıfır fayda üretir. Daha gerçekçi yol: anomali tespiti "
            "(unsupervised) — modele 'arıza nedir' öğretmek yerine 'normal çalışma nasıl görünür'ü "
            "öğretip (Isolation Forest, Autoencoder) normalden sapan durumları işaretlemek; 41 etiketli "
            "örneğinizi model eğitmek için değil, eşik/performans doğrulamak için kullanırsınız. Bu, "
            "dengesiz veri sorununu bypass ettiği için sizin durumunuza daha uygun. Eğer arızadan önceki "
            "saatlerde/günlerde belirgin bir sinyal kalıbı varsa (kademeli sıcaklık/titreşim artışı), "
            "'kalan yararlı ömür' tahmini gibi regresyon çerçevesine geçmek de değerlendirilebilir ama "
            "bu daha veri-yoğun bir yaklaşım. Yönetime sunumda 'arıza tahmin modeli' yerine 'anormal "
            "durum erken uyarı sistemi' çerçevesini önermenizi tavsiye ederim — hem teknik olarak daha "
            "savunulabilir hem beklenti yönetimi açısından daha doğru. İlk adım olarak 12 sensörün "
            "normal aralık dağılımlarını çıkarıp basit eşik-tabanlı bir pilot bile başlı başına değer "
            "üretir, ML şart değil."
        ),
    },
    {
        "category_slug": "ai-ml-agentic",
        "subject": "Muhasebede her ay tekrarlayan mutabakat işleri — agentic AI ile otomasyona nereden başlanır?",
        "starter": "MuhasebeUzmani",
        "first_post": (
            "KOBİ'de ön muhasebe tarafında her ay aynı döngü tekrar ediyor: banka ekstrelerini indir, "
            "cari hesaplarla eşleştir, uyuşmayanları listele, ilgili kişilere mail at. 'AI agent'larla "
            "otomatikleşir' deniyor ama nereden başlanacağını bilmiyorum. Bu süreç agentic otomasyon "
            "için uygun bir ilk aday mı, yoksa klasik RPA/script işi mi? Riskleri neler?"
        ),
        "expert": "joseph",
        "answer": (
            "Tarif ettiğiniz süreç agentic otomasyon için ideal bir ilk aday — çünkü adımlar net "
            "kurallara bağlı ama girdi formatı (banka ekstresi düzeni, cari hesap isimlendirmesi) "
            "değişken olabiliyor, tam bu değişkenliği yönetmek klasik RPA'nın zayıf olduğu, LLM tabanlı "
            "agent'ların güçlü olduğu nokta. Başlangıç için önerim: tüm süreci tek seferde "
            "otomatikleştirmeye çalışmayın, en çok zaman alan tek adımdan başlayın — genelde bu, "
            "ekstre-cari eşleştirmesi oluyor. Bir agent bu adımı yapıp 'eşleşmeyenler' listesini insana "
            "sunsun, onay/düzeltme insanda kalsın — tam otomasyon değil, 'insan onaylı otomasyon' ile "
            "başlamak hem güven inşa eder hem hataların maliyetini sınırlar. Riskler: banka verisi "
            "hassas, agent'ın hangi verilere eriştiği ve nereye gönderildiği net kontrol edilmeli "
            "(yerel/kurumsal LLM mi, dış API mi tercih edileceği önemli bir karar); yanlış eşleştirme "
            "sessizce geçerse muhasebe hatası büyür, bu yüzden ilk aylarda agent çıktısının tamamının "
            "insan tarafından çift kontrol edilmesi şart, güven oturdukça örneklem kontrolüne "
            "geçilebilir. Pilot için 1 ay, tek adım, düşük risk — böyle başlamak en gerçekçi yol."
        ),
    },
]


class Command(BaseCommand):
    help = "Faz 12 seed forum konularını kademeli olarak ekler (--count kadar yeni konu)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count", type=int, default=3,
            help="Bu çalıştırmada eklenecek en fazla yeni konu sayısı (varsayılan 3).",
        )

    def handle(self, *args, **options):
        limit = options["count"]

        section = Section.objects.first()
        if not section:
            self.stderr.write(self.style.ERROR("Hiç Section yok, önce forum kurulumu yapılmalı."))
            return

        category_cache = {}
        for c in NEW_CATEGORIES:
            category, created = Category.objects.get_or_create(
                slug=c["slug"],
                defaults={"title": c["title"], "section": section},
            )
            category_cache[c["slug"]] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f"  + Yeni kategori: {c['title']}"))

        user_cache = {}

        def get_user(username):
            if username not in user_cache:
                try:
                    user_cache[username] = User.objects.get(username=username)
                except User.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"  Kullanıcı bulunamadı: {username}, atlanıyor."))
                    return None
            return user_cache[username]

        existing_subjects = set(
            Topic.objects.filter(subject__in=[t["subject"] for t in TOPICS]).values_list("subject", flat=True)
        )

        created_count = 0

        for t in TOPICS:
            if created_count >= limit:
                break

            if t["subject"] in existing_subjects:
                continue

            category = category_cache.get(t["category_slug"])
            if category is None:
                try:
                    category = Category.objects.get(slug=t["category_slug"])
                except Category.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"  Kategori bulunamadı: {t['category_slug']}, atlanıyor."))
                    continue

            starter = get_user(t["starter"])
            expert = get_user(t["expert"])
            if not starter or not expert:
                continue

            topic = Topic.objects.create(category=category, subject=t["subject"], starter=starter)
            Post.objects.create(topic=topic, created_by=starter, message=t["first_post"])
            Post.objects.create(topic=topic, created_by=expert, message=t["answer"], is_best_answer=True)

            created_count += 1
            existing_subjects.add(t["subject"])
            self.stdout.write(self.style.SUCCESS(f"  ✓ {t['subject'][:70]}"))

        self.stdout.write(self.style.SUCCESS(f"\nTamamlandı: {created_count} yeni konu eklendi."))
        remaining = sum(1 for t in TOPICS if t["subject"] not in existing_subjects)
        if remaining:
            self.stdout.write(f"Yayınlanmayı bekleyen: {remaining} konu.")
