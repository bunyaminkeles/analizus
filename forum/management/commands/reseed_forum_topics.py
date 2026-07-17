"""
Faz 12 — Editoryal forum içeriği: gerçek hesaplardan 12 yeni konu + doğrulanmış
uzman cevabı. Kademeli yayın içindir — tüm liste burada hazır durur, her
çalıştırmada sadece --count kadar YENİ (henüz oluşturulmamış) konu eklenir.

Kaynak: analizus_forum_seed_konular.md (proje kökü)

Kullanım:
    python manage.py reseed_forum_topics --count 3
    docker compose exec web python manage.py reseed_forum_topics --count 3
"""
import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from forum.models import Section, Category, Topic, Post, Profile


# Bu kullanıcılar tek bir merkezi seed komutundan gelmiyor (proje geçmişinde
# farklı oturumlarda organik biriktiler) — ortamlar arası taşınabilirlik için
# (lokal/Render/Hetzner) get_user() burada yoksa bu meta ile OLUŞTURUR.
PERSONA_META = {
    "Sahada_Arastirma": ("Saha Araştırmacısı", "Standard"),
    "Yonetim_Aras": ("İşletme Araştırmacısı", "Premium"),
    "Zeynep_Nitel": ("Sosyoloji Araştırmacısı", "Standard"),
    "opendata": ("", "Premium"),
    "Ekonometri_S": ("Ekonometri Uzmanı", "Premium"),
    "Iletisimci": ("İletişim Uzmanı", "Standard"),
    "tegmen": ("", "Free"),
    "Prof_Deneyimli": ("", "Free"),
    "GorselAnaliz": ("Etnograf", "Premium"),
    "AI_Junior": ("AI Meraklısı", "Standard"),
    "Arastirmaci_B": ("Doktora Öğrencisi", "Free"),
    "SaglikIst": ("Sağlık İstatistikçisi", "Standard"),
    "TezMagduru_A": ("Yüksek Lisans Öğrencisi", "Free"),
    "Can_Veri": ("Ekonometri Doktora", "Premium"),
    "Psikoloji_Tez": ("Doktora Öğrencisi", "Standard"),
    "Ayse_K": ("Eğitim Bilimleri YL", "Standard"),
    "Planlama_Y": ("İş Planlama Uzmanı", "Standard"),
    "SirketSahibi_C": ("Proje Yöneticisi", "Free"),
    "MetodologiUzmani": ("Araştırma Görevlisi", "Premium"),
    "PythonDev_X": ("Python Geliştirici", "Free"),
    "Muhendislik_R": ("Makine Mühendisi", "Premium"),
    "MuhasebeUzmani": ("Finans Analisti", "Premium"),
    "SEM_Uzmani": ("", "Free"),
    "VeriBilimci_A": ("Data Scientist", "Premium"),
    "Otomasyoncu": ("VBA & Makro Uzmanı", "Premium"),
    "Sosyal_Veri": ("Sosyal Bilimci", "Standard"),
    "AnalizUzmani_1": ("İstatistikçi", "Free"),
    "EditorProf": ("", "Free"),
    "AI_Ogrenci": ("YL Öğrencisi", "Standard"),
    "Donanim_Meraklisi": ("Deep Learning Dev", "Premium"),
    "Dr_Mehmet_Stats": ("Doktor - İstatistik Uzmanı", "Expert"),
    "figen": ("Dr. İstatistik Uzmanı", "Expert"),
    "bunyamin": ("Kurucu & Veri Bilimci", "Expert"),
    "PythonGurusu": ("Veri Bilimci", "Expert"),
    "ModelEgitmeni": ("ML Engineer", "Expert"),
    "joseph": ("ML Engineer & Ekonometrist", "Expert"),
    "R_Uzmani": ("Araştırmacı - Ekonometri", "Expert"),
    "Ekonometrist": ("Doç. Dr. Ekonometri", "Expert"),
    "TezDanismani_Prof": ("Profesör - Psikoloji", "Expert"),
    "Sosyolog_N": ("Dr. Nitel Araştırmacı", "Expert"),
    "AkademikEtik": ("Araştırma Metodolojisti", "Expert"),
    "Klinik_Aras": ("Dr. Klinik Araştırmacı", "Expert"),
    "VeriGorselci": ("Data Visualization Uzmanı", "Expert"),
    "StratejiAnalisti": ("Business Intelligence", "Expert"),
    "Literatur_Tarama": ("Bibliyometri Uzmanı", "Expert"),
}


# Bu 7 kategori slug'ı (yeni oluşturulan 3 kategorinin aksine) ortamdan
# ortama farklı — ör. lokal DB'de 'spss', production'da 'spss-amos'.
# Tam slug eşleşmezse listedeki anahtar kelimeler sırayla title+description
# alanında aranır (ilk eşleşen kazanır); hiçbiri bulunamazsa konu atlanır
# (yeni kategori icat edilmez — mevcut taksonomiye uymayan bir konu yanlış
# kovaya zorlanmaz).
CATEGORY_KEYWORD_FALLBACK = {
    "spss": ["SPSS"],
    "regresyon": ["Regresyon"],
    "metodoloji": ["Metodoloji", "Nitel"],
    "python": ["Python"],
    "r-programlama": ["R Studio"],
    "icerik": ["İçerik", "Nitel"],
    "danismanlik": ["Danışman"],
}


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
    # --- Gemini ile üretilen 3. dalga (8 konu, kalan starter havuzu) ---
    {
        "category_slug": "spss",
        "subject": "AMOS'ta doğrulayıcı faktör analizinde CFI 0,88 çıktı, modifikasyon indekslerini kullanmak doğru mu?",
        "starter": "SEM_Uzmani",
        "first_post": (
            "Doktora tezimde 4 faktörlü, 22 maddelik bir ölçeğin doğrulayıcı faktör analizini "
            "AMOS 28'de yaptım, örneklemim 410 kişi. Uyum indekslerim CFI 0,88, TLI 0,86, "
            "RMSEA 0,081 çıktı. Modifikasyon indeksleri bazı hata terimleri arasında kovaryans "
            "önerince birkaçını ekledim ve CFI 0,93'e yükseldi. Ancak bir makalede bunun veri "
            "avcılığı sayılabileceğini okudum. Bu düzeltmeleri raporlamak jüride veya hakemde "
            "sorun yaratır mı?"
        ),
        "expert": "bunyamin",
        "answer": (
            "Endişeniz haklı çünkü modifikasyon indeksleri en çok kötüye kullanılan YEM "
            "aracıdır. Kural şu: her düzeltme istatistiksel değil kuramsal gerekçeyle "
            "yapılmalıdır. Aynı faktöre yüklenen iki maddenin hata terimleri arasında "
            "kovaryans tanımlamak, maddeler benzer ifade kalıbı veya ortak yöntem kaynağı "
            "paylaşıyorsa savunulabilir; farklı faktörlerin maddeleri arasında hata "
            "kovaryansı eklemekse modelin ayırt edici geçerliğini örtbas eder ve hakemden "
            "döner. İkinci kural sıralıdır: modifikasyonları tek tek ekleyin, her eklemeden "
            "sonra modeli yeniden tahmin edin, çünkü indeksler birbirine bağımlıdır ve ilk "
            "düzeltme sonrakilerin değerini değiştirir. Üçüncüsü şeffaflık: hem düzeltme "
            "öncesi hem sonrası uyum değerlerini tablo halinde raporlayın ve her kovaryansın "
            "gerekçesini bir cümleyle yazın; gizlenen düzeltme veri avcılığıdır, "
            "gerekçelendirilip raporlanan düzeltme model geliştirmedir. Mevcut değerlerinize "
            "gelince, CFI için 0,90 kabul edilebilir ve 0,95 iyi uyum eşiği yaygın kabul "
            "görür, RMSEA 0,08 sınırdadır; yani başlangıç modeliniz reddedilecek kadar kötü "
            "değil. Düzeltmeye başlamadan önce standartlaştırılmış faktör yükleri 0,50'nin "
            "altında kalan maddeleri incelemenizi öneririm; sorun çoğu zaman hata "
            "kovaryansında değil zayıf bir-iki maddededir ve madde atmak, kovaryans "
            "örmekten daha temiz bir çözümdür."
        ),
    },
    {
        "category_slug": "regresyon",
        "subject": "Lojistik regresyonda Exp(B) değerim 0,42 çıktı, bunu yüzde olarak nasıl yorumlamalıyım?",
        "starter": "VeriBilimci_A",
        "first_post": (
            "Banka müşterilerinin krediyi zamanında ödeyip ödemediğini yordayan bir lojistik "
            "regresyon kurdum, 1.850 gözlemim var. Sürekli değişkenlerden biri olan mevcut "
            "borç oranı için Exp(B) 0,42 ve p değeri 0,003 çıktı. Katsayının anlamlı "
            "olduğunu görüyorum ama 0,42'yi rapora nasıl çevireceğimi bilmiyorum. Yüzde 42 "
            "azaltıyor mu demeliyim, yoksa hesap farklı mı? Olasılık ile odds kavramları da "
            "kafamı karıştırıyor."
        ),
        "expert": "Ekonometrist",
        "answer": (
            "En sık yapılan hata tam da sorduğunuz yerde: Exp(B) 0,42 yüzde 42 azalış demek "
            "değildir. Doğru okuma şudur: yordayıcıdaki bir birimlik artış, sonucun "
            "gerçekleşme oddsunu 0,42 katına düşürür; azalış oranı 1 eksi 0,42, yani yüzde "
            "58'dir. Rapora şöyle yazarsınız: borç oranındaki bir birimlik artış, krediyi "
            "zamanında ödeme oddsunu yüzde 58 azaltmaktadır. İkinci kritik nokta odds ile "
            "olasılık ayrımı: odds, olayın gerçekleşme olasılığının gerçekleşmeme "
            "olasılığına oranıdır; yüzde 58'lik düşüş oddsa aittir, ödeme olasılığındaki "
            "değişim başlangıç olasılığına göre değişir ve doğrusal değildir. Bu yüzden "
            "cümlede olasılık kelimesini kullanmaktan kaçının, hakemler bunu hemen yakalar. "
            "Üçüncüsü, bir birimlik artışın anlamlı olup olmadığını düşünün: borç oranı 0-1 "
            "aralığında bir orandaysa bir birimlik artış tüm ölçeği kat etmek demektir; "
            "değişkeni yüzde puanı olarak ölçeklendirmek veya 10 puanlık artış başına "
            "yorumlamak çok daha okunur sonuç verir. Son olarak Exp(B) yanında yüzde 95 "
            "güven aralığını mutlaka raporlayın; aralık 1'i içermiyorsa bulgunuz sağlamdır "
            "ve 0,003'lük p değerinizle tutarlı olacaktır. Nagelkerke R kare ve "
            "sınıflandırma tablosunu da eklemeyi unutmayın."
        ),
    },
    {
        "category_slug": "python",
        "subject": "Her hafta 30 şubeden gelen Excel dosyalarını Python ile otomatik nasıl birleştiririm?",
        "starter": "Otomasyoncu",
        "first_post": (
            "Şirketimizde her pazartesi 30 şubeden aynı şablonda birer Excel dosyası geliyor "
            "ve ben bunları elle kopyala-yapıştır ile tek dosyada birleştirip özet tablo "
            "çıkarıyorum, yaklaşık 3 saatimi alıyor. Python bilgim başlangıç seviyesinde, "
            "pandas ile tek dosya okuyabiliyorum. Klasördeki tüm dosyaları otomatik okuyup "
            "birleştiren, hangi satırın hangi şubeden geldiğini de kaydeden bir betik nasıl "
            "kurarım? Bazı şubeler dosyayı geç veya hatalı gönderiyor, bunu da yakalamak "
            "isterim."
        ),
        "expert": "PythonGurusu",
        "answer": (
            "Bu, otomasyonun en hızlı geri ödeyen türü; iskelet üç adımdan oluşur. Birinci "
            "adım dosyaları toplamak: pathlib modülünden Path ile klasörü gösterip glob "
            "deseniyle tüm xlsx dosyalarını listeleyin, örneğin Path(klasor).glob('*.xlsx'). "
            "İkinci adım döngüyle okumak: her dosyayı pd.read_excel ile açın ve "
            "birleştirmeden önce df'ye şube kimliğini ekleyin; dosya adları şube kodunu "
            "içeriyorsa df['sube'] = dosya.stem satırı kaynağı kalıcı olarak damgalar, "
            "sonradan hangi satır nereden geldi sorusu hiç doğmaz. Üçüncü adım pd.concat "
            "ile tek çerçevede birleştirip pivot_table veya groupby ile özetinizi almak. "
            "Hata yakalama kısmı asıl değeri üretir: okuma satırını try-except bloğuna "
            "alın, bozuk dosyalarda except dalı dosya adını bir hata listesine yazsın ve "
            "betik çökmeden devam etsin. Şablon tutarlılığı için birleştirmeden önce her "
            "df'nin sütun listesini beklenen listeyle karşılaştırın; eksik veya fazla sütun "
            "varsa o şubeyi rapora not düşün. Geç gönderenleri yakalamak için beklenen 30 "
            "şube kodunun kümesinden gelen dosyaların kümesini çıkarın, fark size eksikleri "
            "verir. Betiği Windows Görev Zamanlayıcı veya cron ile pazartesi sabahına "
            "kurduğunuzda 3 saatlik iş birkaç dakikaya iner; çıktıyı to_excel yerine "
            "Parquet olarak da saklarsanız arşiv sorguları çok hızlanır."
        ),
    },
    {
        "category_slug": "icerik",
        "subject": "VOSviewer'da tezim için oluşturduğum anahtar kelime haritasındaki 5 kümeyi nasıl yorumlamalıyım?",
        "starter": "Sosyal_Veri",
        "first_post": (
            "Tezimin literatür bölümünü bibliyometrik analizle desteklemek istiyorum. Web of "
            "Science'tan çektiğim 1.240 makaleyi VOSviewer'a yükledim ve anahtar kelime "
            "eş-oluşum haritası ürettim, program 5 renkli küme çıkardı. Görsel etkileyici "
            "duruyor ama tezde bu kümeleri nasıl anlatacağımı bilmiyorum. Renkler neye göre "
            "ayrılıyor, düğüm boyutları ne anlama geliyor? Bir de bazı kelimeler eş anlamlı "
            "olmasına rağmen ayrı düğüm olmuş, bu sorun mu?"
        ),
        "expert": "Literatur_Tarama",
        "answer": (
            "Haritayı yorumlamadan önce eş anlamlı sorununu çözmelisiniz, çünkü bu küme "
            "yapısını doğrudan bozar. VOSviewer'da thesaurus dosyası denen iki sütunlu basit "
            "bir metin dosyasıyla varyantları birleştirirsiniz; tekil-çoğul yazımlar, "
            "kısaltma-açılım çiftleri ve İngilizce yazım farkları tek etikete toplanınca hem "
            "düğüm sayısı sadeleşir hem eş-oluşum sayıları gerçek değerine kavuşur. Ayrıca "
            "minimum eş-oluşum eşiğini (genellikle 5 civarı) bilinçli seçip metin bölümünde "
            "raporlayın; eşik, haritanın kaç kelimeyle kurulduğunu belirler. Yorum katmanına "
            "gelince: her renk, birlikte anılma sıklığı yüksek kelimelerin modülerlik "
            "temelli algoritmayla ayrıştırılmış bir tematik kümesidir; kümeyi yorumlamak, "
            "içindeki en yüksek frekanslı 5-10 kelimeye bakıp alana hakimiyetinizle o "
            "araştırma damarına bir ad vermektir, adı program değil siz koyarsınız. Düğüm "
            "boyutu kelimenin toplam görülme sıklığını, bağlantı kalınlığı iki kelimenin "
            "birlikte anılma gücünü gösterir; kümeler arası köprü konumundaki kelimeler "
            "disiplinlerarası temas noktalarıdır ve tezde ayrıca vurgulanmaya değer. Son bir "
            "katman daha ekleyin: overlay görünümünde düğümler ortalama yayın yılına göre "
            "renklenir, böylece hangi temanın olgunlaştığını hangisinin yükselen araştırma "
            "cephesi olduğunu gösterebilirsiniz. Bu üçlü okuma, haritayı süsten analize "
            "dönüştürür."
        ),
    },
    {
        "category_slug": "danismanlik",
        "subject": "Analiz danışmanlığında müşteri sürekli ek analiz istiyor, revizyon sınırını nasıl belirlemeliyim?",
        "starter": "AnalizUzmani_1",
        "first_post": (
            "Yaklaşık bir yıldır serbest istatistik danışmanlığı yapıyorum. Son işimde tez "
            "verisi için t-testi ve ANOVA üzerine anlaştık, teslimden sonra müşteri önce "
            "regresyon, sonra aracılık analizi istedi ve bunları revizyon hakkı sayıyor. İş, "
            "anlaştığımız ücretin iki katı emeğe ulaştı. Müşteriyi kaybetmeden nazikçe sınır "
            "çizmek istiyorum ama nasıl formüle edeceğimi bilemiyorum. Baştan sözleşmeye ne "
            "yazmalıydım, şimdi ne demeliyim?"
        ),
        "expert": "StratejiAnalisti",
        "answer": (
            "Yaşadığınız şeyin adı kapsam kayması ve çözümü nezaket değil tanım netliğidir. "
            "Revizyon ile yeni talep ayrımını yazılı kurala bağlamalısınız: revizyon, "
            "anlaşılan analizlerin düzeltilmesi veya yeniden raporlanmasıdır; anlaşma "
            "metninde adı geçmeyen her yeni analiz türü yeni bir iş kalemidir. Bundan "
            "sonraki tekliflerinizde üç unsuru madde madde belirtin: yapılacak analizlerin "
            "adları tek tek (t-testi, tek yönlü ANOVA gibi — 'gerekli analizler' gibi açık "
            "uçlu ifade kullanmadan), dahil olan revizyon tur sayısı (sektör pratiği 2 "
            "turdur) ve kapsam dışı taleplerin ayrıca fiyatlanacağı cümlesi. Mevcut "
            "müşteriye dönüşünüz de aynı çerçeveyle kurulur: önce teslim edilen işin "
            "anlaşılan kapsamı karşıladığını nazikçe hatırlatın, ardından aracılık "
            "analizini yapmaktan memnuniyet duyacağınızı ancak bunun yeni bir kalem "
            "olduğunu belirtip küçük bir ek teklif sunun. Çoğu müşteri sınırı sizin kadar "
            "bilmez; net teklif gördüğünde ya kabul eder ya vazgeçer, ilişki nadiren "
            "bozulur. Ödeme tarafında da işi aşamalandırın: veri temizliği ve ana "
            "analizler tesliminde ara ödeme almak, sonu gelmeyen taleplerle çalışılmış "
            "emeğin karşılıksız kalmasını önler. Analizus pazaryerindeki teklif formunun "
            "fiyatla birlikte teslim süresini de zorunlu alan olarak istemesi de kapsamı "
            "baştan netleştirmeye yardımcı olur."
        ),
    },
    {
        "category_slug": "akademik-surec",
        "subject": "Editörlüğünü yaptığım dergiye AI ile yazılmış makaleler geliyor, nasıl bir politika uygulamalıyım?",
        "starter": "EditorProf",
        "first_post": (
            "Ulusal hakemli bir derginin editörlüğünü yürütüyorum. Son 6 ayda gelen "
            "gönderilerin belirgin kısmında aynı kalıp cümleler, aşırı pürüzsüz ama "
            "içeriksiz paragraflar ve doğrulanamayan kaynaklar görüyorum. İki makalede "
            "kaynakçadaki DOI'lerin bir kısmı gerçek çıkmadı. AI tespit araçlarından birini "
            "denedim ama sonuçlarına ne kadar güveneceğimi bilmiyorum. Dergi olarak yazılı "
            "bir politika oluşturmak istiyoruz, neleri kapsamalı?"
        ),
        "expert": "AkademikEtik",
        "answer": (
            "İki konuyu ayırarak başlayın, çünkü çözümleri farklı: AI kullanımı ile uydurma "
            "kaynak aynı şey değildir. Uydurma kaynak, nasıl üretilmiş olursa olsun doğrudan "
            "bilimsel sahtecilik kapsamındadır ve mevcut etik mevzuatınız zaten yeterlidir; "
            "kaynakça doğrulamasını sürece gömün, editoryal ön kontrolde rastgele seçilmiş "
            "5-10 kaynağın DOI ve künyesini kontrol etmek düşük maliyetli ve etkili bir "
            "filtredir, tarif ettiğiniz iki vaka masa reddi gerekçesidir. AI politikasına "
            "gelince, COPE ve büyük yayınevlerinin yerleşen ortak çerçevesi üç ilkeye "
            "dayanır: yapay zeka araçları yazar olamaz çünkü sorumluluk üstlenemez; "
            "yazarlar kullandıkları aracı ve kullanım amacını yöntem veya teşekkür "
            "bölümünde beyan etmekle yükümlüdür; metnin doğruluğunun tüm sorumluluğu "
            "beyandan bağımsız olarak yazarlara aittir. Tespit araçları konusunda temkinli "
            "olmanız isabetli: bu araçların yanlış pozitif oranları yüksektir ve ana dili "
            "İngilizce olmayan yazarların özgün metinlerini de sıklıkla AI diye "
            "işaretledikleri gösterilmiştir; tek başına bir tespit skoru asla ret gerekçesi "
            "yapılmamalı, olsa olsa insan incelemesini tetikleyen bir sinyal sayılmalıdır. "
            "Politikanızı dergi web sitesinde açıkça yayımlayın ve gönderi sistemine "
            "zorunlu bir beyan kutusu ekleyin; caydırıcılığın çoğu, denetimden değil beyan "
            "zorunluluğunun kendisinden gelir."
        ),
    },
    {
        "category_slug": "ai-ml-agentic",
        "subject": "Türkçe duygu analizinde 3.200 yorumluk verimle hazır model mi kullanmalıyım, kendim mi eğitmeliyim?",
        "starter": "AI_Ogrenci",
        "first_post": (
            "Bitirme projemde bir e-ticaret sitesinden topladığım 3.200 müşteri yorumunu "
            "olumlu, olumsuz ve nötr olarak sınıflandıracağım. Yorumların hepsini elle "
            "etiketledim. Hugging Face'te hazır Türkçe duygu analizi modelleri gördüm ama "
            "hocam kendi modelini eğitirsen daha çok öğrenirsin diyor. 3.200 örnek bir model "
            "eğitmek için yeterli mi, yoksa hazır modeli mi kullanmalıyım? Ekran kartım yok, "
            "sadece ücretsiz Colab kullanabiliyorum."
        ),
        "expert": "joseph",
        "answer": (
            "İkisini birden yapın, çünkü proje raporunuzun en güçlü bölümü tam da bu "
            "karşılaştırma olur. Doğru sıralama üç basamaklıdır. Önce basit bir taban "
            "çizgisi kurun: TF-IDF öznitelikleriyle lojistik regresyon, scikit-learn'de "
            "yarım saatte kurulur ve Türkçe yorumlarda şaşırtıcı derecede iyi sonuç verir; "
            "sonraki her modelin bu çıtayı geçmesi gerekir, geçemiyorsa karmaşıklık kendini "
            "ödemiyordur. İkinci basamakta Hugging Face'teki BERTurk tabanlı hazır duygu "
            "modellerinden birini kendi test kümenizde sıfır eğitimle deneyin; hazır "
            "modeller genel alan verisiyle eğitildiğinden sizin e-ticaret alanınızda etiket "
            "dağılımı kayabilir, bu farkı ölçmek başlı başına bir bulgudur. Üçüncü basamak "
            "ince ayar: 3.200 etiketli örnek, sıfırdan model eğitmek için az ama önceden "
            "eğitilmiş bir Türkçe BERT'i ince ayarlamak için gayet yeterlidir; veriyi "
            "tabakalı olarak yüzde 80-10-10 eğitim, doğrulama ve test kümelerine bölün, "
            "ücretsiz Colab'ın GPU'su bu boyuttaki ince ayarı birkaç epoch için rahatça "
            "kaldırır. Değerlendirmede doğruluk yerine makro F1 raporlayın; nötr sınıf "
            "neredeyse her zaman azınlıktadır ve doğruluk metriği bu dengesizliği gizler. "
            "Sınıf dağılımınızı raporun başında verin, üç yaklaşımın makro F1 karşılaştırma "
            "tablosuyla bitirin; hocanızın istediği öğrenme çıktısı da bu tabloda "
            "somutlaşır."
        ),
    },
    {
        "category_slug": "veri-analizi-bi",
        "subject": "Şirket verimizi buluta göndermeden kendi sunucumuzda Metabase ile dashboard kurabilir miyiz?",
        "starter": "Donanim_Meraklisi",
        "first_post": (
            "KOBİ ölçeğinde bir üretim firmasıyız, satış ve stok verimiz yerel bir "
            "PostgreSQL veritabanında duruyor. Yönetim dashboard istiyor ama veri gizliliği "
            "politikamız gereği bulut tabanlı BI araçlarına veri gönderemiyoruz. Elimde 16 "
            "GB RAM'li, Docker kurulu bir Ubuntu sunucu var. Metabase veya Superset gibi "
            "açık kaynak araçlarla tamamen kendi sunucumuzda bir çözüm kurmak gerçekçi mi, "
            "hangisini seçmeliyim ve nelere dikkat etmeliyim?"
        ),
        "expert": "VeriGorselci",
        "answer": (
            "Gerçekçi olmanın ötesinde, tarif ettiğiniz senaryo bu araçların tam hedef "
            "kitlesi. İki aday arasındaki seçim ekip profiline bağlıdır: Metabase, Docker'da "
            "tek konteynerle dakikalar içinde ayağa kalkar, SQL bilmeyen yöneticilerin bile "
            "soru sorabildiği görsel bir sorgu arayüzü sunar ve bakım yükü çok düşüktür; "
            "Superset daha geniş grafik yelpazesi ve ayrıntılı yetkilendirme sunar ama "
            "kurulumu, yükseltmesi ve yönetimi belirgin biçimde daha fazla teknik emek "
            "ister. KOBİ ölçeğinde ilk kurulum için Metabase ile başlamak, ihtiyaç aşarsa "
            "Superset'e geçmek en az riskli yoldur; ikisi de PostgreSQL'e doğrudan bağlanır "
            "ve veri sunucunuzdan dışarı çıkmaz. Donanımınız fazlasıyla yeterli, çünkü bu "
            "araçlar veriyi kendine kopyalamaz, sorguyu veritabanınıza gönderip sonucu "
            "gösterir; asıl performans, PostgreSQL tarafında satış tablolarınızın tarih ve "
            "şube sütunlarına indeks atılmasına bağlıdır. Dikkat edilecek üç nokta var: "
            "Metabase'in kendi uygulama veritabanını varsayılan H2 yerine ayrı bir "
            "PostgreSQL şemasında tutun, yoksa yükseltmelerde ayar kaybı yaşarsınız; "
            "dashboard kullanıcılarına salt okunur bir veritabanı kullanıcısıyla bağlantı "
            "verin; ve uygulamayı doğrudan internete açmayıp en azından ters proxy "
            "arkasında, şirket ağıyla sınırlı tutun. Haftalık yedek ve sürüm güncellemesi "
            "için aylık bir saatlik bakım penceresi ayırmanız yeterli olur."
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
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={"email": f"{username.lower()}@example.com"},
                )
                if created:
                    user.set_unusable_password()
                    user.save()
                    title, account_type = PERSONA_META.get(username, ("", "Standard"))
                    Profile.objects.get_or_create(
                        user=user, defaults={"title": title, "account_type": account_type}
                    )
                    self.stdout.write(self.style.SUCCESS(f"  + Yeni kullanıcı: {username} ({account_type})"))
                user_cache[username] = user
            return user_cache[username]

        existing_subjects = set(
            Topic.objects.filter(subject__in=[t["subject"] for t in TOPICS]).values_list("subject", flat=True)
        )

        created_count = 0
        # created_at auto_now_add olduğu için .create() sırasında yazılamaz —
        # aşağıda .update() ile geriye dönük ezilir. Amaç: aynı çalıştırmada
        # oluşan konular tek bir zaman damgasında kümelenip hem forum
        # akışında hem Google'a "toplu içerik dökümü" gibi görünmesin; her
        # konu bir öncekinden 1-3 gün geriye kayar, cevabı sorudan birkaç
        # saat sonrasına damgalanır.
        cursor_dt = timezone.now() - timedelta(days=1)

        for t in TOPICS:
            if created_count >= limit:
                break

            if t["subject"] in existing_subjects:
                continue

            category = category_cache.get(t["category_slug"])
            if category is None:
                slug = t["category_slug"]
                try:
                    category = Category.objects.get(slug=slug)
                except Category.DoesNotExist:
                    category = None
                    matched_keyword = None
                    for keyword in CATEGORY_KEYWORD_FALLBACK.get(slug, []):
                        category = Category.objects.filter(
                            Q(title__icontains=keyword) | Q(description__icontains=keyword)
                        ).first()
                        if category is not None:
                            matched_keyword = keyword
                            break
                    if category is None:
                        self.stdout.write(self.style.WARNING(f"  Kategori bulunamadı: {slug} (yedek anahtar kelimeler de eşleşmedi), atlanıyor."))
                        continue
                    self.stdout.write(f"  ~ '{slug}' slug'ı bulunamadı, '{category.title}' kategorisine (anahtar kelime: {matched_keyword}) düşüldü.")
                category_cache[slug] = category

            starter = get_user(t["starter"])
            expert = get_user(t["expert"])
            if not starter or not expert:
                continue

            topic_dt = cursor_dt
            reply_dt = topic_dt + timedelta(hours=random.randint(2, 20))

            topic = Topic.objects.create(category=category, subject=t["subject"], starter=starter)
            first_post = Post.objects.create(topic=topic, created_by=starter, message=t["first_post"])
            reply = Post.objects.create(topic=topic, created_by=expert, message=t["answer"], is_best_answer=True)

            Topic.objects.filter(pk=topic.pk).update(created_at=topic_dt)
            Post.objects.filter(pk=first_post.pk).update(created_at=topic_dt)
            Post.objects.filter(pk=reply.pk).update(created_at=reply_dt)

            cursor_dt = topic_dt - timedelta(days=random.randint(1, 3), hours=random.randint(0, 6))

            created_count += 1
            existing_subjects.add(t["subject"])
            self.stdout.write(self.style.SUCCESS(f"  ✓ {t['subject'][:70]} ({topic_dt.date()})"))

        self.stdout.write(self.style.SUCCESS(f"\nTamamlandı: {created_count} yeni konu eklendi."))
        remaining = sum(1 for t in TOPICS if t["subject"] not in existing_subjects)
        if remaining:
            self.stdout.write(f"Yayınlanmayı bekleyen: {remaining} konu.")
