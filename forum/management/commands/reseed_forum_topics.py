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
    # --- Gemini ile üretilen 2. dalga (10 konu, her kategoriden 1) ---
    {
        "category_slug": "spss",
        "subject": "SPSS'te faktör analizi yaparken KMO değerim 0,58 çıktı, örneklemi artırmalı mıyım?",
        "starter": "Sahada_Arastirma",
        "first_post": (
            "Yüksek lisans tezim için 28 maddelik bir tutum ölçeği geliştiriyorum. 142 kişilik "
            "örneklemle SPSS 29'da açımlayıcı faktör analizi denedim ama KMO değeri 0,58 çıktı, "
            "Bartlett testi anlamlı. Danışmanım KMO'nun en az 0,60 olması gerektiğini söyledi. "
            "Veri toplamaya devam mı etmeliyim yoksa bazı maddeleri çıkararak bu veriyle "
            "ilerleyebilir miyim? Savunmaya 3 ay var, yeni veri toplamak zaman alacak."
        ),
        "expert": "figen",
        "answer": (
            "KMO 0,58 sınırda bir değer; Kaiser'in sınıflamasında 0,50 altı kabul edilemez, "
            "0,60-0,70 arası vasat sayılır. İki yönlü ilerleyebilirsiniz ve ikisini birlikte yapmak "
            "en sağlıklısı. Önce SPSS çıktısındaki Anti-Image Correlation matrisinin köşegenine "
            "bakın: her maddenin kendi örneklem yeterliliği (MSA) değeri orada yazar. MSA değeri "
            "0,50'nin altında kalan maddeleri tek tek (hepsini aynı anda değil) analizden çıkarıp "
            "KMO'yu yeniden hesaplayın; çoğu zaman 2-3 sorunlu madde genel KMO'yu belirgin "
            "yükseltir. İkincisi örneklem-madde oranı: 28 madde için 142 kişi 5:1 oranının hemen "
            "üzerinde, ideal kabul edilen 10:1 için 280 civarı gözlem gerekir. Madde eleme sonrası "
            "KMO 0,60'ı geçiyorsa ve her faktör en az 3 maddeyle, 0,40 üzeri yüklerle temsil "
            "ediliyorsa mevcut veriyle savunulabilir bir açımlayıcı faktör analizi "
            "raporlayabilirsiniz. Yine 0,60 altında kalıyorsa veri toplamaya devam etmek tek "
            "gerçek çözümdür; ölçek geliştirme çalışmasında zayıf örneklem yeterliliği jüride "
            "mutlaka sorulur. Bartlett küresellik testinin anlamlı olması iyi haber, korelasyon "
            "matrisi faktörleşmeye uygun demektir."
        ),
    },
    {
        "category_slug": "regresyon",
        "subject": "Çoklu regresyonda iki değişkenin VIF değeri 8'in üzerinde, birini modelden çıkarmalı mıyım?",
        "starter": "Yonetim_Aras",
        "first_post": (
            "Örgütsel bağlılığı yordayan bir model kuruyorum. 5 bağımsız değişkenli çoklu doğrusal "
            "regresyonda iş doyumu ve örgütsel güven değişkenlerinin VIF değerleri 8,4 ve 8,9 "
            "çıktı, diğerleri 2'nin altında. İki değişken arasındaki korelasyon 0,87. Örneklemim "
            "315 kişi, veriyi SPSS'te analiz ediyorum. Kuramsal olarak ikisi de modelde önemli ama "
            "çoklu bağlantı sorunu makale hakemlerinden döner mi diye endişeliyim."
        ),
        "expert": "Dr_Mehmet_Stats",
        "answer": (
            "VIF 8 civarı değerler gri bölgededir: bazı kaynaklar eşiği 10, daha muhafazakar "
            "olanlar 5 kabul eder, dolayısıyla hakemin itiraz etme ihtimali gerçektir. Ancak asıl "
            "sorun VIF sayısı değil, 0,87'lik korelasyonun işaret ettiği şey: iş doyumu ve "
            "örgütsel güven ölçekleriniz büyük olasılıkla aynı örtük yapıyı ölçüyor. Bu durumda "
            "çoklu bağlantı, katsayıların standart hatalarını şişirir; iki değişkenin beta "
            "işaretleri tutarsızlaşabilir veya ikisi de anlamsız görünürken model R karesi yüksek "
            "kalır. Çıktınızda bu belirtiler varsa müdahale şart. Seçenekleriniz şunlar: birini "
            "kuramsal gerekçeyle modelden çıkarmak; ikisini standartlaştırıp tek bir bileşik "
            "endekse dönüştürmek; ya da iki ayrı model kurup sonuçları karşılaştırmalı "
            "raporlamak. Değişken silmek istemiyorsanız hiyerarşik regresyonda ayrı bloklarda "
            "girerek her birinin tekil katkısını da gösterebilirsiniz. Ridge regresyon teknik bir "
            "alternatif olsa da sosyal bilim dergilerinde yorumlaması zor bulunur. Hangi yolu "
            "seçerseniz seçin, makalede tolerans ve VIF değerlerini tablo halinde raporlayıp "
            "verdiğiniz kararı gerekçelendirin; hakemler sorunu görmezden gelmenize değil, "
            "yönetmemenize itiraz eder."
        ),
    },
    {
        "category_slug": "metodoloji",
        "subject": "Nitel tez görüşmelerinde 12 katılımcıya ulaştım, veri doyumuna ulaştığımı nasıl anlarım?",
        "starter": "Zeynep_Nitel",
        "first_post": (
            "Doktora tezimde göçmen kadınların çalışma deneyimlerini fenomenolojik desenle "
            "inceliyorum. Şu ana kadar 12 yarı yapılandırılmış görüşme yaptım, her biri 45-70 "
            "dakika sürdü. Son iki görüşmede önceki kodlara çok benzer ifadeler duymaya "
            "başladım ama emin olamıyorum. Danışmanım en az 15 görüşme bekliyor. Doyuma "
            "ulaştığımı jüriye nasıl kanıtlarım, sadece sayı yeterli mi yoksa somut bir gösterim "
            "mi gerekiyor?"
        ),
        "expert": "TezDanismani_Prof",
        "answer": (
            "Doyum bir sayı değil, gözlemlenebilir bir durumdur ve jüriye tam da bunu göstermeniz "
            "gerekir. Literatürde Guest ve arkadaşlarının sık atıf alan çalışması, görece homojen "
            "gruplarda temel temaların ilk 12 görüşmede büyük ölçüde ortaya çıktığını bulmuştur; "
            "yani sayınız savunulabilir bir aralıkta. Ancak sayıya yaslanmak yerine bir doyum "
            "tablosu hazırlayın: satırlarda kodlarınız, sütunlarda görüşme sırası olsun ve her "
            "kodun ilk hangi görüşmede ortaya çıktığını işaretleyin. Son üç-dört görüşmede yeni "
            "kod üretilmediğini bu tabloyla görselleştirdiğinizde doyum iddianız ampirik bir "
            "dayanak kazanır; MAXQDA veya NVivo bu matrisi kolayca üretir. İkinci olarak kod "
            "doyumu ile anlam doyumunu ayırın: yeni kod çıkmıyor olabilir ama mevcut temaların "
            "içeriği hâlâ zenginleşiyorsa birkaç görüşme daha değerlidir. Fenomenolojik desende "
            "örneklemin homojenliği de gerekçenizin parçası olmalı; katılımcı profillerinizin "
            "ortak deneyim ölçütünü nasıl karşıladığını yöntem bölümünde açıkça yazın. "
            "Danışmanınızın 15 görüşme beklentisiyle çatışmak yerine doyum tablosunu 12 "
            "görüşmeyle hazırlayıp gösterin; tablo iki-üç görüşme daha gerektiğini söylüyorsa bu, "
            "keyfi bir sayıdan çok daha ikna edici bir gerekçedir."
        ),
    },
    {
        "category_slug": "python",
        "subject": "Pandas 2 milyon satırlık CSV dosyamı okurken bellek hatası veriyor, ne yapabilirim?",
        "starter": "opendata",
        "first_post": (
            "Açık veri portalından indirdiğim 2,1 milyon satır ve 34 sütunluk bir CSV ile "
            "çalışıyorum, dosya boyutu yaklaşık 1,8 GB. 8 GB RAM'li dizüstümde pd.read_csv ile "
            "okumaya çalışınca MemoryError alıyorum, bazen de bilgisayar tamamen donuyor. Python "
            "3.12 ve pandas 2.2 kullanıyorum. Amacım birkaç sütunda gruplama ve özet istatistik "
            "çıkarmak. Donanım yükseltmeden bu veriyi işleyebilmemin bir yolu var mı?"
        ),
        "expert": "PythonGurusu",
        "answer": (
            "Var, hem de birkaç katmanlı. İlk ve en etkili adım usecols parametresi: 34 sütunun "
            "tamamına ihtiyacınız yoksa read_csv çağrısında yalnızca gruplama ve özet için "
            "gereken sütunları isteyin; bellek kullanımı doğrudan sütun sayısıyla orantılı "
            "düşer. İkinci adım dtype optimizasyonu: pandas varsayılan olarak metin sütunlarını "
            "object, sayıları int64/float64 tutar. Tekrarlayan kategorik metinleri dtype olarak "
            "category, küçük tam sayıları int32 veya int16 belirterek okursanız bellek çoğu "
            "zaman dörtte bire iner. Üçüncü seçenek chunksize ile parçalı okuma: read_csv'ye "
            "chunksize=200000 verip her parçada ara toplamları biriktirir, sonda "
            "birleştirirsiniz; groupby-agg işlemleri bu desene çok uygundur. Pandas 2.2 "
            "kullandığınız için engine='pyarrow' ve dtype_backend='pyarrow' da deneyin; Arrow "
            "tabanlı string tipi klasik object'ten çok daha ekonomiktir. Bunların ötesine geçmek "
            "isterseniz Polars kütüphanesinin lazy API'si veya DuckDB, 1,8 GB'lık CSV'yi 8 GB "
            "RAM'de sorgu mantığıyla rahatça işler; DuckDB'de tek satır SQL ile gruplama yapıp "
            "sonucu küçük bir pandas DataFrame olarak alabilirsiniz. Dosyayı bir kez Parquet "
            "formatına çevirmek de sonraki okumaları hem hızlandırır hem küçültür."
        ),
    },
    {
        "category_slug": "r-programlama",
        "subject": "R'da plm paketiyle panel regresyonda sabit etkiler mi rassal etkiler mi seçmeliyim?",
        "starter": "Ekonometri_S",
        "first_post": (
            "Tezimde 2010-2023 dönemi için 26 OECD ülkesinin verileriyle dengeli panel kurdum, R "
            "4.4 ve plm paketi kullanıyorum. Bağımlı değişkenim işsizlik oranı, 4 makro bağımsız "
            "değişkenim var. Hem within hem random tahmincisiyle model çalıştırdım, katsayılar "
            "birbirine yakın ama tam aynı değil. Hangi modeli raporlayacağıma karar veremiyorum, "
            "seçimi hangi testle ve hangi sırayla yapmalıyım?"
        ),
        "expert": "R_Uzmani",
        "answer": (
            "Standart karar zinciri üç testten oluşur ve plm hepsini içerir. Önce havuzlanmış "
            "EKK'ya karşı sabit etkileri sınayın: pFtest(fe_model, pooled_model) anlamlıysa "
            "birim etkileri vardır, havuzlama uygun değildir. Ardından rassal etkilerin "
            "havuzlamaya karşı geçerliliği için Breusch-Pagan LM testi: plmtest(pooled_model, "
            "type = \"bp\"). İki test de birim etkisine işaret ediyorsa asıl karar Hausman "
            "testiyle verilir: phtest(fe_model, re_model). Sıfır hipotez, birim etkilerinin "
            "açıklayıcılarla ilişkisiz olduğudur; p değeri 0,05'in altındaysa rassal etkiler "
            "tahmincisi tutarsızdır, sabit etkileri raporlarsınız. P değeri yüksekse rassal "
            "etkiler hem tutarlı hem daha etkindir. 26 ülkelik makro panelde ülkeye özgü "
            "gözlenmeyen özelliklerin (kurumsal yapı, işgücü piyasası rejimi) açıklayıcılarınızla "
            "ilişkili olması kuvvetle muhtemel olduğundan Hausman genellikle sabit etkileri "
            "işaret eder. Hangi model seçilirse seçilsin standart hataları vcovHC ile, ülke "
            "bazında kümelenmiş (arellano yöntemi) olarak düzeltin; makro panellerde değişen "
            "varyans ve otokorelasyon neredeyse kuraldır. Zaman etkilerini de effect = "
            "\"twoways\" ile sınayıp anlamlıysa modele katmayı unutmayın."
        ),
    },
    {
        "category_slug": "icerik",
        "subject": "İçerik analizinde Krippendorff alfa 0,62 çıktı, kodlayıcılar arası güvenirliği nasıl yükseltirim?",
        "starter": "Iletisimci",
        "first_post": (
            "Yüksek lisans tezimde 480 gazete haberini 9 kategorili bir kod şemasıyla analiz "
            "ediyorum. İkinci kodlayıcıyla örneklemin yüzde 15'ini bağımsız kodladık ve "
            "Krippendorff alfa 0,62 çıktı. Okuduğum kaynaklar 0,80 eşiğinden söz ediyor. "
            "Kodlayıcım da ben de şemayı anladığımızı düşünüyorduk ama bazı kategorilerde "
            "sürekli ayrışıyoruz. Tüm kodlamayı baştan mı yapmalıyım yoksa şemayı düzeltip "
            "devam edebilir miyim?"
        ),
        "expert": "Sosyolog_N",
        "answer": (
            "Baştan kodlamadan önce ayrışmanın nerede olduğunu teşhis edin; 0,62'lik genel alfa "
            "çoğu zaman iki-üç sorunlu kategorinin eseridir. Krippendorff'un kendi önerisi 0,80 "
            "üzerinin güvenilir, 0,667-0,80 arasının ancak ihtiyatlı çıkarımlar için kabul "
            "edilebilir olduğu yönündedir; 0,62 bu eşiğin de altında, dolayısıyla mevcut "
            "kodlamayla sonuç raporlayamazsınız. Yapılacak iş sırasıyla şu: uyuşmazlık matrisini "
            "çıkarıp hangi kategori çiftlerinin karıştığına bakın. Genellikle sorun, kavramsal "
            "olarak örtüşen kategorilerdedir; iki kategori sürekli birbirine karışıyorsa ya "
            "birleştirilmeli ya da kod kitabındaki tanımlara ayırt edici karar kuralları ve "
            "sınır örnekleri eklenmelidir. Kod kitabını revize ettikten sonra kodlayıcınızla "
            "uyuşmazlık örneklerini tek tek tartışın, ancak nihai kararları müzakereyle değil "
            "kurala bağlayın; müzakere edilmiş mutabakat güvenirlik katsayısını yapay şişirir. "
            "Sonra daha önce kullanılmamış yeni bir alt örneklemde (yine yüzde 10-15) pilot "
            "kodlamayı tekrarlayın ve alfayı yeniden hesaplayın. Eşik aşıldığında ana kodlamaya "
            "geçersiniz; revizyon öncesi kodlanan haberler yeni şemayla yeniden kodlanmalıdır. "
            "Tezde her kategori için ayrı alfa raporlamak, genel katsayının maskeleyebileceği "
            "zayıflıkları şeffaflaştırdığı için jüride güven yaratır."
        ),
    },
    {
        "category_slug": "danismanlik",
        "subject": "Anket verimi analiz için danışmana gönderirken KVKK açısından nasıl anonimleştirmeliyim?",
        "starter": "tegmen",
        "first_post": (
            "Kurumumda 240 personelle yürüttüğüm bir iş doyumu anketinin analizini dışarıdan bir "
            "istatistik danışmanına yaptırmak istiyorum. Veri setinde ad soyad yok ama sicil "
            "numarası, doğum tarihi, birim adı ve rütbe bilgisi var. Excel dosyasını olduğu gibi "
            "göndermekten çekiniyorum çünkü kurum içinde bazı birimlerde 3-4 kişi çalışıyor, kim "
            "olduğu tahmin edilebilir. Hangi alanları nasıl dönüştürmeliyim, hukuken de "
            "sorumluluğum var mı?"
        ),
        "expert": "Klinik_Aras",
        "answer": (
            "Endişeniz yerinde; ad soyad olmaması veriyi anonim yapmaz, KVKK dolaylı yoldan "
            "kimliği belirlenebilir kişileri de kapsar. Sizin tarif ettiğiniz durum tam olarak "
            "yarı-tanımlayıcı (quasi-identifier) sorunudur: doğum tarihi, birim ve rütbe "
            "kombinasyonu 3-4 kişilik birimlerde kişiyi tekil olarak işaret eder. Yapmanız "
            "gerekenler sırasıyla şunlar: sicil numarasını tamamen silin veya analiz sırasında "
            "eşleştirme gerekiyorsa yalnızca sizde kalan ayrı bir anahtar dosyayla rastgele "
            "katılımcı kodlarına (K001, K002) dönüştürün; danışmana anahtar dosya asla "
            "gitmesin. Doğum tarihini yaş grubuna çevirin (25-34, 35-44 gibi). Birim ve rütbeyi, "
            "her hücrede en az 5 kişi kalacak şekilde üst kategorilerde birleştirin; buna "
            "k-anonimlik ilkesi denir ve k=5 makul bir başlangıçtır. Analiz açısından da "
            "kaybınız az olur çünkü grup karşılaştırmaları zaten kategorik düzeyde yapılır. "
            "Hukuki tarafta veri sorumlusu kurumunuz, danışman veri işleyen konumundadır; "
            "aranızda gizlilik ve veri işleme taahhüdü içeren yazılı bir sözleşme olmalı, "
            "aktarım şifreli kanaldan yapılmalı ve iş bitiminde verinin silineceği yazıya "
            "bağlanmalıdır. Analizus üzerinden açılan proje taleplerinde bu gizlilik çerçevesi "
            "zaten sürecin parçasıdır."
        ),
    },
    {
        "category_slug": "akademik-surec",
        "subject": "SSCI dergisine gönderdiğim makale 5 aydır hakemde görünüyor, editöre hatırlatma yazmak uygun mu?",
        "starter": "Prof_Deneyimli",
        "first_post": (
            "Şubat ayında bir SSCI Q2 dergisine makale gönderdim. İlk iki hafta with editor "
            "göründü, sonra under review statüsüne geçti ve 5 aydır orada duruyor. Derginin "
            "sitesinde ortalama ilk karar süresi 90 gün yazıyor. Doçentlik dosyam için bu yayın "
            "önemli ve süre daralıyor. Editöre yazmak süreci olumsuz etkiler mi, yazacaksam "
            "nasıl bir üslup kullanmalıyım, yoksa geri çekip başka dergiye mi göndermeliyim?"
        ),
        "expert": "AkademikEtik",
        "answer": (
            "Beyan edilen ortalama süreyi yüzde 50'den fazla aştığınız için nazik bir durum "
            "sorgusu tamamen meşrudur ve süreci olumsuz etkilemez; editörler bu tür mesajlara "
            "alışkındır, hatta bazen unutulmuş bir hakem davetini fark etmelerini sağlar. Under "
            "review statüsünde 5 ay geçmesi çoğunlukla hakem bulma güçlüğüne veya geciken tek "
            "bir hakeme işaret eder. Mesajınız kısa olsun: makale numarası, başlık, gönderim "
            "tarihi ve derginin ilan ettiği ortalama süreye kibar bir atıfla sürecin hangi "
            "aşamada olduğunu sormanız yeterli; aciliyet gerekçenizi (doçentlik takvimi) "
            "yazmanıza gerek yok, bu editörün karar hızını değiştirmez ve profesyonel durmaz. "
            "Yanıt gelmezse 3-4 hafta sonra bir kez daha yazabilirsiniz. Geri çekme kararını "
            "aceleye getirmeyin: makaleyi çekip yeni dergiye göndermek süreci sıfırlar ve yeni "
            "dergide de 3-6 ay ilk karar beklersiniz; toplamda muhtemelen daha çok zaman "
            "kaybedersiniz. Geri çekme ancak editörden iki sorguya rağmen hiç yanıt alamazsanız "
            "veya süre 8-9 ayı bulursa rasyonel hale gelir. Bu arada makaleyi eş zamanlı başka "
            "dergiye göndermeyin; çoklu gönderim yayın etiği ihlalidir ve tespit edildiğinde her "
            "iki dergiden de ret getirir."
        ),
    },
    {
        "category_slug": "veri-analizi-bi",
        "subject": "50 şubenin aylık satış verisini Tableau dashboard'ına çevirirken hangi grafikleri kullanmalıyım?",
        "starter": "GorselAnaliz",
        "first_post": (
            "Perakende firmamızda 50 şubenin 24 aylık satış verisini Excel'de tutuyoruz, "
            "yönetim artık aylık toplantılarda tek ekranlık bir Tableau dashboard'ı görmek "
            "istiyor. Denedim ama 50 şubeyi tek çizgi grafiğe koyunca okunmaz bir spagetti "
            "çıktı, pasta grafik de öneriliyor ama içime sinmedi. Hem genel trendi hem sorunlu "
            "şubeleri aynı ekranda gösterecek bir düzen için hangi grafik türlerini ve "
            "filtreleri kurgulamalıyım?"
        ),
        "expert": "VeriGorselci",
        "answer": (
            "İçgüdünüz doğru; 50 kategorili pasta grafik de 50 çizgili trend de okunmaz. Doğru "
            "kurgu, dashboard'ı genelden özele üç katmanda düşünmektir. En üste toplam ciro, "
            "önceki aya ve geçen yılın aynı ayına göre değişim yüzdesi gibi 3-4 KPI kartı koyun; "
            "yönetim ekrana baktığı ilk saniyede genel durumu görsün. Orta katmanda tek bir "
            "toplam satış çizgi grafiği (24 aylık trend) ve yanına şube karşılaştırması için "
            "yatay çubuk grafik yerleştirin; çubuğu son ay cirosuna göre sıralayıp Top N "
            "parametresiyle ilk ve son 10 şubeyi gösterilebilir yapın, böylece hem yıldızlar "
            "hem sorunlu şubeler tek bakışta seçilir. Sorunlu şubeleri vurgulamak için çubuk "
            "rengini hedefe ulaşma oranına bağlayın; kırmızı-gri ikili renk, gökkuşağı "
            "paletinden çok daha net okunur. Üçüncü katman etkileşimdir: çubuktaki bir şubeye "
            "tıklandığında dashboard action ile trend grafiği o şubeye filtrelensin, spagetti "
            "sorununu böyle çözersiniz. Bölge bilgisi varsa harita yerine bölge bazlı küçük "
            "çoklu grafikler (small multiples) de değerlendirilebilir. Tarihi ay düzeyinde "
            "DATETRUNC ile toplayıp extract kullanırsanız 50 şube 24 ay boyutundaki veri "
            "performans sorunu çıkarmaz."
        ),
    },
    {
        "category_slug": "ai-ml-agentic",
        "subject": "ChatGPT'ye yaptırdığım regresyon analizinin sonuçlarına güvenebilir miyim, nasıl doğrularım?",
        "starter": "AI_Junior",
        "first_post": (
            "Bitirme projem için 380 kişilik anket verimin özetini ChatGPT'ye verdim ve çoklu "
            "regresyon yorumu istedim. Bana R kare, F ve p değerleriyle dolu, gayet ikna edici "
            "bir sonuç tablosu yazdı. Sonra aynı veriyi arkadaşımın SPSS'inde denedik, "
            "katsayılar tutmuyor. Hangisine güveneceğim, yapay zekanın verdiği istatistik "
            "sonuçları ne kadar gerçek? Teslim tarihine 2 hafta var ve kafam çok karışık."
        ),
        "expert": "ModelEgitmeni",
        "answer": (
            "SPSS çıktısına güvenin; yaşadığınız durum bilinen bir olgudur. Bir dil modeline "
            "verinin kendisini değil özetini verdiğinizde model gerçek bir hesaplama yapmaz, "
            "eğitim verisinde gördüğü regresyon tablolarına biçimsel olarak benzeyen, akla "
            "yatkın görünen sayılar üretir. Buna halüsinasyon denir ve R kare, F, p değerleri "
            "gibi kesinlik hissi veren rakamlarda özellikle tehlikelidir çünkü çıktı formatı "
            "gerçek bir SPSS tablosundan ayırt edilemez. Doğrulamanın yolu basit bir ilkeye "
            "dayanır: yapay zekadan sonuç değil, çalıştırılabilir kod isteyin. Modele veri "
            "yapınızı tarif edip Python (statsmodels) veya R kodu yazdırın, kodu kendi "
            "verinizle kendiniz çalıştırın; hesaplamayı yazılım yapar, model yalnızca kod "
            "iskeletini kurar. Çıktıyı kontrol ederken üç şeye bakın: gözlem sayısı ve "
            "serbestlik dereceleri sizin verinizle tutarlı mı, katsayı işaretleri korelasyon "
            "matrisiyle uyumlu mu, varsayım kontrolleri (artıkların normalliği, çoklu bağlantı "
            "için VIF) yapılmış mı. Yapay zekanın yazdığı yorum paragrafını da mutlaka gerçek "
            "çıktıdaki sayılarla satır satır karşılaştırın; model bazen doğru tabloya yanlış "
            "yorum ekler. Analizus'un AI analiz doğrulama hizmeti de tam bu ihtiyaç için var; "
            "teslimden önce sonuçlarınızı bağımsız olarak kontrol ettirebilirsiniz."
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
