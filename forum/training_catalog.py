"""Eğitim hizmetleri kataloğu — DB'siz Python sabiti.

Not: URL adı değil, yalnızca slug tutulur; template `{% url 'egitim_detay' item.slug %}`
ile çözer (URL isimlerini grep'ten kaçıran Python sabitleri hatasını tekrarlama, bkz. analizus.md §26).

Her item'daki `related_tool_url` yalnızca platformda gerçekten karşılığı olan bir
araç/sayfa varsa doldurulur; uydurma/kırık link üretmemek için karşılığı olmayanlarda
alan hiç yazılmaz (get() ile None döner).
"""

TRAINING_CATEGORIES = [
    {
        "slug": "ofis-veri",
        "title": "Ofis & Veri",
        "icon": "bi-file-earmark-spreadsheet",
        "items": [
            {
                "slug": "excel-veri-analizi", "title": "Excel ile Veri Analizi",
                "level": "beginner", "hours": "12", "audience": ["bireysel", "kurumsal"],
                "summary": "Ham veriyi Excel'de düzenleme, pivot tablo ve temel formüllerle özetleme, basit grafiklerle raporlama.",
                "outcomes": [
                    "Pivot tablo ile veri özetleme",
                    "VLOOKUP / INDEX-MATCH ile veri eşleştirme",
                    "Temel grafik ve dashboard hazırlama",
                    "Veri temizleme (kopya/hata giderme)",
                ],
                "prerequisites": ["Yok"],
                "tools": ["Microsoft Excel"],
                "syllabus": [
                    {"week": 1, "title": "Veri Düzenleme ve Temizleme", "topics": ["Hücre biçimlendirme", "Kopya/hatalı veri temizleme", "Metin-sayı dönüşümleri"]},
                    {"week": 2, "title": "Formüller ve Fonksiyonlar", "topics": ["VLOOKUP / INDEX-MATCH", "Koşullu fonksiyonlar (SUMIF, COUNTIF)"]},
                    {"week": 3, "title": "Pivot Tablo ve Özetleme", "topics": ["Pivot tablo kurulumu", "Gruplama ve filtreleme"]},
                    {"week": 4, "title": "Görselleştirme ve Raporlama", "topics": ["Grafik türleri", "Basit dashboard tasarımı"]},
                ],
                "faq": [
                    {"q": "Excel'in hangi sürümüyle çalışılıyor?", "a": "Microsoft 365 güncel sürüm önerilir; 2016 ve sonrası sürümlerle de uyumludur."},
                    {"q": "Kendi Excel dosyamla çalışabilir miyim?", "a": "Evet, tercih edilen yöntem budur."},
                ],
            },
            {
                "slug": "excel-ileri", "title": "İleri Excel: Power Query, Power Pivot, DAX",
                "level": "intermediate", "hours": "16", "audience": ["kurumsal"],
                "summary": "Büyük ve dağınık veri kaynaklarını Power Query ile otomatik temizleme, Power Pivot ve DAX ile ileri veri modelleme.",
                "outcomes": [
                    "Power Query ile otomatik veri temizleme akışı kurma",
                    "Power Pivot ile çoklu tablo veri modeli oluşturma",
                    "DAX ile hesaplanan alan ve ölçü yazma",
                    "Periyodik güncellenen rapor şablonu hazırlama",
                ],
                "prerequisites": ["Excel ile Veri Analizi eğitimi veya dengi deneyim"],
                "tools": ["Microsoft Excel (Power Query, Power Pivot, DAX)"],
                "syllabus": [
                    {"week": 1, "title": "Power Query ile Veri Hazırlama", "topics": ["Çoklu kaynaktan veri çekme", "Dönüşüm adımlarını otomatikleştirme"]},
                    {"week": 2, "title": "Veri Modelleme", "topics": ["İlişkisel tablo modeli", "Power Pivot'a giriş"]},
                    {"week": 3, "title": "DAX Formülleri", "topics": ["Hesaplanan sütun ve ölçüler", "Zaman zekâsı fonksiyonları"]},
                    {"week": 4, "title": "Otomatik Raporlama", "topics": ["Yenilenebilir rapor şablonları", "Performans optimizasyonu"]},
                ],
                "faq": [
                    {"q": "Power BI ile farkı nedir?", "a": "Aynı Power Query/DAX motorunu kullanır; bu eğitim Excel içinde kalarak aynı yetkinliği kazandırır."},
                ],
            },
        ],
    },
    {
        "slug": "programlama",
        "title": "Programlama",
        "icon": "bi-code-slash",
        "items": [
            {
                "slug": "python-temel", "title": "Sıfırdan Python",
                "level": "beginner", "hours": "20",
                "summary": "Programlamaya hiç girmemiş katılımcılar için Python'a sıfırdan, veri analizine hazırlık odaklı giriş.",
                "outcomes": [
                    "Python temel sözdizimi ve veri tipleri",
                    "Döngü ve koşul yapılarıyla script yazma",
                    "Fonksiyon tanımlama",
                    "pandas'a geçişe hazır bir temel",
                ],
                "prerequisites": ["Yok"],
                "tools": ["Python", "Jupyter Notebook"],
                "syllabus": [
                    {"week": 1, "title": "Python'a Giriş", "topics": ["Kurulum (Anaconda/Jupyter)", "Değişkenler ve veri tipleri"]},
                    {"week": 2, "title": "Kontrol Yapıları", "topics": ["Koşullar (if/elif/else)", "Döngüler (for/while)"]},
                    {"week": 3, "title": "Fonksiyonlar ve Veri Yapıları", "topics": ["Fonksiyon tanımlama", "Liste, sözlük, demet"]},
                    {"week": 4, "title": "Dosya İşlemleri ve Hazırlık", "topics": ["CSV okuma/yazma", "pandas'a giriş önizlemesi"]},
                ],
                "faq": [
                    {"q": "Hiç kod yazmadım, zor olur mu?", "a": "Hayır; eğitim tam olarak sıfır deneyim varsayımıyla kurulur."},
                ],
            },
            {
                "slug": "python-veri-analizi", "title": "Python ile Veri Analizi (pandas, numpy, matplotlib)",
                "level": "intermediate", "hours": "24",
                "summary": "Gerçek veri setiyle pandas ile veri temizleme, numpy ile sayısal işlemler, matplotlib ile görselleştirme.",
                "outcomes": [
                    "pandas DataFrame ile veri manipülasyonu",
                    "Eksik/aykırı veri temizleme",
                    "numpy ile vektörel hesaplama",
                    "matplotlib/seaborn ile grafik üretme",
                ],
                "prerequisites": ["Temel Python bilgisi (Sıfırdan Python eğitimi veya dengi)"],
                "tools": ["Python (pandas, numpy, matplotlib)", "Jupyter Notebook"],
                "syllabus": [
                    {"week": 1, "title": "pandas Temelleri", "topics": ["DataFrame ve Series", "Veri okuma (CSV/Excel)"]},
                    {"week": 2, "title": "Veri Temizleme", "topics": ["Eksik veri yönetimi", "Aykırı değer tespiti"]},
                    {"week": 3, "title": "Gruplama ve Birleştirme", "topics": ["groupby/agg", "merge/join"]},
                    {"week": 4, "title": "Görselleştirme", "topics": ["matplotlib temelleri", "seaborn ile istatistiksel grafikler"]},
                ],
                "faq": [
                    {"q": "R yerine neden Python?", "a": "İkisi de öğretilebilir; Python'un genel amaçlı kullanımı ve geniş kütüphane ekosistemi nedeniyle çoğu katılımcı bunu tercih ediyor, talebe göre R'a da uyarlanabilir."},
                ],
            },
        ],
    },
    {
        "slug": "istatistik",
        "title": "İstatistik & Ölçme",
        "icon": "bi-bar-chart-line",
        "items": [
            {
                "slug": "spss-uygulamali", "title": "SPSS ile Uygulamalı İstatistik",
                "level": "beginner", "hours": "18",
                "summary": "SPSS arayüzünde veri girişinden hipotez testine, tablo okumadan APA raporlamaya kadar uygulamalı istatistik.",
                "outcomes": [
                    "SPSS'te veri girişi ve değişken tanımlama",
                    "Betimsel istatistik ve frekans tabloları",
                    "t-testi, ANOVA, ki-kare gibi temel testleri uygulama",
                    "SPSS çıktısını APA formatında raporlama",
                ],
                "prerequisites": ["Yok"],
                "tools": ["IBM SPSS Statistics"],
                "syllabus": [
                    {"week": 1, "title": "SPSS Arayüzü ve Veri Girişi", "topics": ["Değişken görünümü", "Veri girişi ve kodlama"]},
                    {"week": 2, "title": "Betimsel İstatistik", "topics": ["Frekans ve merkezi eğilim", "Normallik testleri"]},
                    {"week": 3, "title": "Karşılaştırma Testleri", "topics": ["t-testi", "Tek yönlü ANOVA"]},
                    {"week": 4, "title": "Raporlama", "topics": ["APA tablo formatı", "Sonuç yazımı"]},
                ],
                "related_tool_url": "/analiz/ttesti/",
                "faq": [
                    {"q": "Hangi SPSS sürümü kullanılıyor?", "a": "Güncel IBM SPSS Statistics sürümleriyle uyumludur; kurumunuzdaki lisanslı sürümle de çalışılabilir."},
                ],
            },
            {
                "slug": "istatistik-test-secimi", "title": "Doğru Testi Seçme ve APA ile Raporlama",
                "level": "beginner", "hours": "10",
                "summary": "Değişken türü ve araştırma sorusuna göre doğru istatistiksel testi seçme, sonucu APA 7 standardında yazma.",
                "outcomes": [
                    "Parametrik / parametrik olmayan test ayrımı",
                    "Değişken türüne göre test seçim ağacı kullanma",
                    "Varsayım kontrollerini (normallik, homojenlik) yorumlama",
                    "APA 7 formatında sonuç raporlama",
                ],
                "prerequisites": ["Yok"],
                "tools": ["SPSS veya Python (isteğe göre)"],
                "syllabus": [
                    {"week": 1, "title": "Test Seçim Mantığı", "topics": ["Değişken türleri", "Bağımsız/bağımlı örneklem ayrımı"]},
                    {"week": 2, "title": "Varsayım Kontrolleri", "topics": ["Normallik testleri", "Varyans homojenliği"]},
                    {"week": 3, "title": "APA Raporlama", "topics": ["Tablo ve metin formatı", "Etki büyüklüğü raporlama"]},
                ],
                "related_tool_url": "/hangi-test/",
                "faq": [
                    {"q": "Bu eğitim hangi platform aracıyla ilişkili?", "a": "/hangi-test/ sayfasındaki karar ağacı bu eğitimin temelini oluşturur; ders sırasında birlikte kullanılır."},
                ],
            },
            {
                "slug": "olcek-gelistirme", "title": "Ölçek Geliştirme, Geçerlik ve Güvenirlik",
                "level": "advanced", "hours": "14",
                "summary": "Yeni bir ölçme aracı geliştirme sürecinde madde yazımından açımlayıcı faktör analizine, güvenirlik hesaplamasına kadar tüm adımlar.",
                "outcomes": [
                    "Madde havuzu oluşturma ve uzman görüşü süreci",
                    "Açımlayıcı faktör analizi (AFA) uygulama",
                    "Cronbach Alfa ile güvenirlik hesaplama",
                    "Geçerlik-güvenirlik raporlama",
                ],
                "prerequisites": ["Temel istatistik bilgisi (SPSS ile Uygulamalı İstatistik önerilir)"],
                "tools": ["SPSS", "AMOS (isteğe bağlı)"],
                "syllabus": [
                    {"week": 1, "title": "Ölçek Geliştirme Süreci", "topics": ["Madde yazımı", "Uzman görüşü ve kapsam geçerliği"]},
                    {"week": 2, "title": "Faktör Analizi", "topics": ["AFA varsayımları (KMO, Bartlett)", "Faktör çıkarma ve döndürme"]},
                    {"week": 3, "title": "Güvenirlik", "topics": ["Cronbach Alfa", "Madde-toplam korelasyonu"]},
                    {"week": 4, "title": "Raporlama", "topics": ["Geçerlik-güvenirlik tablosu", "Tez/makale metin yazımı"]},
                ],
                "related_tool_url": "/istatistik/cronbach/",
                "faq": [
                    {"q": "Doğrulayıcı faktör analizi (DFA) de kapsanıyor mu?", "a": "Bu eğitim AFA odaklıdır; DFA/SEM ihtiyacı varsa Yapısal Eşitlik Modellemesi eğitimiyle devam edilir."},
                ],
            },
            {
                "slug": "yem-sem", "title": "Yapısal Eşitlik Modellemesi (AMOS / SmartPLS)",
                "level": "advanced", "hours": "16",
                "summary": "Ölçüm modeli ve yapısal modelin birlikte test edildiği yapısal eşitlik modellemesine (YEM/SEM) AMOS veya SmartPLS ile uygulamalı giriş.",
                "outcomes": [
                    "Ölçüm modeli kurma ve DFA",
                    "Yapısal model ve yol katsayılarını yorumlama",
                    "Model uyum indekslerini (CFI, RMSEA vb.) değerlendirme",
                    "YEM sonuçlarını tez/makalede raporlama",
                ],
                "prerequisites": ["Ölçek Geliştirme eğitimi veya temel faktör analizi bilgisi"],
                "tools": ["AMOS", "SmartPLS"],
                "syllabus": [
                    {"week": 1, "title": "YEM'e Giriş", "topics": ["Ölçüm modeli vs yapısal model", "Örneklem büyüklüğü gereksinimleri"]},
                    {"week": 2, "title": "Doğrulayıcı Faktör Analizi", "topics": ["DFA kurulumu", "Uyum indeksleri"]},
                    {"week": 3, "title": "Yapısal Model", "topics": ["Yol analizi", "Aracı/düzenleyici değişkenler"]},
                    {"week": 4, "title": "Raporlama", "topics": ["Model diyagramı", "Sonuç yazımı"]},
                ],
                "faq": [
                    {"q": "AMOS mu SmartPLS mi kullanmalıyım?", "a": "Kovaryans tabanlı SEM için AMOS, varyans tabanlı (PLS-SEM) için SmartPLS önerilir; ön görüşmede veriniz ve modelinize göre netleştirilir."},
                ],
            },
        ],
    },
    {
        "slug": "yapay-zeka",
        "title": "Yapay Zekâ & Modelleme",
        "icon": "bi-cpu",
        "items": [
            {
                "slug": "makine-ogrenmesi", "title": "Makine Öğrenmesi (scikit-learn)",
                "level": "intermediate", "hours": "24",
                "summary": "scikit-learn ile sınıflandırma, regresyon ve model değerlendirme; kendi verinizle uçtan uca bir ML projesi kurma.",
                "outcomes": [
                    "Sınıflandırma ve regresyon modelleri kurma",
                    "Eğitim/test ayrımı ve çapraz doğrulama",
                    "Model performans metriklerini yorumlama",
                    "Hiperparametre optimizasyonu",
                ],
                "prerequisites": ["Python ile Veri Analizi eğitimi veya dengi deneyim"],
                "tools": ["Python (scikit-learn, pandas)"],
                "syllabus": [
                    {"week": 1, "title": "ML'e Giriş", "topics": ["Denetimli/denetimsiz öğrenme", "Eğitim-test ayrımı"]},
                    {"week": 2, "title": "Sınıflandırma", "topics": ["Karar ağaçları, SVM, lojistik regresyon"]},
                    {"week": 3, "title": "Regresyon ve Değerlendirme", "topics": ["Regresyon modelleri", "Çapraz doğrulama, metrikler"]},
                    {"week": 4, "title": "Model Optimizasyonu", "topics": ["Hiperparametre arama", "Aşırı öğrenmeyi önleme"]},
                ],
                "related_tool_url": "/istatistik/karar-agaci/",
                "faq": [
                    {"q": "Derin öğrenmeyi de bu eğitimde görecek miyim?", "a": "Hayır; bu eğitim klasik ML'e odaklanır. Derin öğrenme ayrı bir eğitimdir."},
                ],
            },
            {
                "slug": "derin-ogrenme", "title": "Derin Öğrenme (TensorFlow / Keras)",
                "level": "advanced", "hours": "24",
                "summary": "Sinir ağı temellerinden görüntü/metin verisiyle çalışan derin öğrenme modellerine TensorFlow/Keras ile uygulamalı giriş.",
                "outcomes": [
                    "Yapay sinir ağı mimarisi kurma",
                    "CNN ile görüntü sınıflandırma",
                    "RNN/Transformer temellerine giriş",
                    "Model eğitimi ve aşırı öğrenmeyi önleme",
                ],
                "prerequisites": ["Makine Öğrenmesi eğitimi veya dengi deneyim"],
                "tools": ["Python (TensorFlow, Keras)", "Google Colab"],
                "syllabus": [
                    {"week": 1, "title": "Sinir Ağı Temelleri", "topics": ["Perceptron", "İleri/geri yayılım"]},
                    {"week": 2, "title": "Keras ile Model Kurma", "topics": ["Katman tasarımı", "Kayıp fonksiyonu ve optimizasyon"]},
                    {"week": 3, "title": "CNN", "topics": ["Evrişimli katmanlar", "Görüntü sınıflandırma"]},
                    {"week": 4, "title": "İleri Konular", "topics": ["RNN/Transformer'a giriş", "Transfer öğrenme"]},
                ],
                "faq": [
                    {"q": "GPU'suz bilgisayarımla takip edebilir miyim?", "a": "Evet; eğitimde ücretsiz Google Colab GPU'su kullanılır, kendi donanımınız yeterli değilse sorun olmaz."},
                ],
            },
            {
                "slug": "nlp-metin-madenciligi", "title": "NLP ve Türkçe Metin Madenciliği",
                "level": "intermediate", "hours": "18",
                "summary": "Türkçe metin verisiyle ön işleme, duygu analizi ve temel NLP modellerini kurma.",
                "outcomes": [
                    "Türkçe metin ön işleme (temizleme, kök bulma)",
                    "TF-IDF ve kelime gömme temelleri",
                    "Duygu analizi modeli kurma",
                    "Hazır Türkçe dil modellerini (BERTurk vb.) kullanma",
                ],
                "prerequisites": ["Python ile Veri Analizi eğitimi veya dengi deneyim"],
                "tools": ["Python (NLTK/Zemberek, scikit-learn, Hugging Face)"],
                "syllabus": [
                    {"week": 1, "title": "Metin Ön İşleme", "topics": ["Türkçe'ye özgü zorluklar", "Temizleme ve normalizasyon"]},
                    {"week": 2, "title": "Klasik NLP", "topics": ["TF-IDF", "Bag-of-words ile sınıflandırma"]},
                    {"week": 3, "title": "Modern NLP", "topics": ["Kelime gömme (embedding)", "Hazır Türkçe BERT modelleri"]},
                ],
                "faq": [
                    {"q": "Sosyal medya verisiyle çalışabilir miyiz?", "a": "Evet, kendi topladığınız veya paylaştığınız veri setiyle çalışmak tercih edilen yöntemdir."},
                ],
            },
            {
                "slug": "agentic-ai", "title": "Agentic AI: Yapay Zekâ Ajanları ve İş Otomasyonu",
                "level": "intermediate", "hours": "12", "audience": ["kurumsal"],
                "summary": "Tekrarlayan veri toplama, analiz ve raporlama süreçlerini yapay zekâ ajanlarıyla otomatikleştirme mantığı ve kurulumu.",
                "outcomes": [
                    "Ajan tabanlı otomasyon mimarisini tasarlama",
                    "Veri toplama/analiz/raporlama hattı kurma",
                    "Uzman doğrulama katmanı ekleme",
                    "Kurum içi süreçlere uygulanabilir bir prototip çıkarma",
                ],
                "prerequisites": ["Temel Python bilgisi önerilir (zorunlu değil)"],
                "tools": ["Python", "LLM API'leri"],
                "syllabus": [
                    {"week": 1, "title": "Agentic AI Temelleri", "topics": ["Ajan mimarisi", "Kural tabanlı vs. LLM tabanlı otomasyon"]},
                    {"week": 2, "title": "Veri Hattı Tasarımı", "topics": ["Veri toplama ve işleme", "Rapor üretimi"]},
                    {"week": 3, "title": "Doğrulama ve Devreye Alma", "topics": ["Uzman doğrulama katmanı", "İzleme ve bildirim"]},
                ],
                "related_tool_url": "/ai-cozumler/",
                "faq": [
                    {"q": "AI Çözümler (agentic) hizmetinden farkı ne?", "a": "Bu eğitimde ekibiniz sistemi kendisi kurmayı öğrenir; /ai-cozumler/ sayfasındaki hizmette ise sistemi ekibimiz sizin için kurar."},
                ],
            },
        ],
    },
    {
        "slug": "akademik",
        "title": "Akademik Süreç",
        "icon": "bi-mortarboard",
        "items": [
            {
                "slug": "akademik-danismanlik", "title": "Tez ve Makale Süreci Danışmanlığı",
                "level": "all", "hours": "esnek",
                "summary": "Araştırma sorusundan yöntem seçimine, veri analizinden tez/makale yazımına kadar akademik süreç boyunca danışmanlık.",
                "outcomes": [
                    "Araştırma sorusu ve hipotez kurma",
                    "Uygun yöntem ve analiz planı belirleme",
                    "Bulguları APA formatında yazma",
                    "Jüri/hakem sürecine hazırlık",
                ],
                "prerequisites": ["Yok"],
                "tools": ["İhtiyaca göre SPSS/Python/R"],
                "syllabus": [
                    {"week": 1, "title": "Araştırma Tasarımı", "topics": ["Araştırma sorusu", "Yöntem seçimi"]},
                    {"week": 2, "title": "Analiz Planı", "topics": ["Uygun testlerin belirlenmesi", "Veri toplama stratejisi"]},
                    {"week": 3, "title": "Yazım ve Raporlama", "topics": ["Bulgular bölümü", "Tartışma ve sonuç"]},
                ],
                "faq": [
                    {"q": "Analizi de sizin yapmanızı istersem?", "a": "Bu eğitim danışmanlık ve öğretim odaklıdır; analizi doğrudan yaptırmak isterseniz Proje Talebi sayfasına yönlendirilirsiniz."},
                ],
            },
            {
                "slug": "bibliyometrik-analiz", "title": "Bibliyometrik Analiz (VOSviewer, Bibliometrix)",
                "level": "intermediate", "hours": "12",
                "summary": "Yayın, atıf ve işbirliği ağlarını VOSviewer ve Bibliometrix ile görselleştirerek bibliyometrik analiz yapma.",
                "outcomes": [
                    "Bibliyometrik veri indirme (Scopus/WoS/OpenAlex)",
                    "VOSviewer ile atıf/işbirliği haritası oluşturma",
                    "Bibliometrix (R) ile tematik analiz",
                    "Bulguları makalede raporlama",
                ],
                "prerequisites": ["Yok"],
                "tools": ["VOSviewer", "R (Bibliometrix)"],
                "syllabus": [
                    {"week": 1, "title": "Veri Toplama", "topics": ["Scopus/WoS/OpenAlex'ten veri indirme", "Veri formatlama"]},
                    {"week": 2, "title": "VOSviewer", "topics": ["Atıf ve işbirliği ağları", "Kümeleme ve görselleştirme"]},
                    {"week": 3, "title": "Bibliometrix", "topics": ["Tematik harita", "Performans analizi"]},
                ],
                "related_tool_url": "/bibliometrics/",
                "faq": [
                    {"q": "Kendi alanımdaki yayınlarla mı çalışacağız?", "a": "Evet; kendi araştırma alanınızdaki veri setiyle uygulama yapılır."},
                ],
            },
            {
                "slug": "kaynakca-programlari", "title": "Kaynakça Yönetimi: EndNote, Mendeley, Zotero",
                "level": "beginner", "hours": "6",
                "summary": "Akademik kaynakları düzenleme, atıf ekleme ve otomatik kaynakça oluşturma için EndNote, Mendeley veya Zotero kullanımı.",
                "outcomes": [
                    "Kaynak kütüphanesi oluşturma ve organize etme",
                    "Word/Google Docs'a otomatik atıf ekleme",
                    "Atıf stili değiştirme (APA, Vancouver vb.)",
                    "PDF içinden otomatik künye çıkarma",
                ],
                "prerequisites": ["Yok"],
                "tools": ["EndNote", "Mendeley", "Zotero"],
                "syllabus": [
                    {"week": 1, "title": "Kurulum ve Kütüphane", "topics": ["Program seçimi", "Kaynak ekleme yöntemleri"]},
                    {"week": 2, "title": "Atıf ve Kaynakça", "topics": ["Word eklentisiyle atıf", "Stil değiştirme"]},
                ],
                "faq": [
                    {"q": "Hangi programı seçmeliyim?", "a": "Üçü de öğretilir; ön görüşmede kurumunuzun/danışmanınızın tercihine göre birine odaklanılır."},
                ],
            },
            {
                "slug": "literatur-tarama", "title": "Sistematik Literatür Tarama ve Veri Kazıma",
                "level": "beginner", "hours": "10",
                "summary": "PRISMA yaklaşımıyla sistematik literatür taraması yapma ve akademik veritabanlarından veri kazıma.",
                "outcomes": [
                    "Arama stratejisi ve anahtar kelime kurma",
                    "PRISMA akış şemasıyla tarama sürecini belgeleme",
                    "OpenAlex/YÖK Tez gibi kaynaklardan veri kazıma",
                    "Tarama sonuçlarını sentezleme",
                ],
                "prerequisites": ["Yok"],
                "tools": ["OpenAlex, YÖK Tez, TR Dizin (platform tarama araçları)"],
                "syllabus": [
                    {"week": 1, "title": "Tarama Stratejisi", "topics": ["Anahtar kelime ve arama dizeleri", "Dahil etme/dışlama kriterleri"]},
                    {"week": 2, "title": "PRISMA ve Veri Kazıma", "topics": ["PRISMA akış şeması", "Otomatik veri indirme"]},
                    {"week": 3, "title": "Sentez", "topics": ["Bulguları tablolaştırma", "Tarama bölümü yazımı"]},
                ],
                "related_tool_url": "/tarama/",
                "faq": [
                    {"q": "Platformdaki tarama araçlarını kullanacak mıyız?", "a": "Evet; /tarama/ altındaki YÖK Tez, OpenAlex ve TR Dizin araçları ders sırasında birlikte kullanılır."},
                ],
            },
        ],
    },
    {
        "slug": "dijital-analitik",
        "title": "Dijital Analitik",
        "icon": "bi-graph-up-arrow",
        "items": [
            {
                "slug": "search-console-seo", "title": "Google Search Console ve SEO Veri Analizi",
                "level": "beginner", "hours": "8",
                "summary": "Google Search Console verisiyle bir web sitesinin arama performansını analiz etme ve SEO fırsatlarını tespit etme.",
                "outcomes": [
                    "Search Console kurulumu ve doğrulama",
                    "Tıklama/gösterim/CTR verisini yorumlama",
                    "Anahtar kelime fırsatlarını tespit etme",
                    "Temel teknik SEO kontrol listesi uygulama",
                ],
                "prerequisites": ["Yok"],
                "tools": ["Google Search Console", "Excel/Google Sheets"],
                "syllabus": [
                    {"week": 1, "title": "Kurulum ve Temel Metrikler", "topics": ["Site doğrulama", "Performans raporu okuma"]},
                    {"week": 2, "title": "Analiz ve Fırsatlar", "topics": ["Anahtar kelime analizi", "Sayfa bazlı performans"]},
                ],
                "faq": [
                    {"q": "Kendi web sitem yoksa katılabilir miyim?", "a": "Katılabilirsiniz; örnek veri setiyle çalışılır, ancak kendi siteniz varsa gerçek veriyle ilerlemek önerilir."},
                ],
            },
            {
                "slug": "ga4-looker", "title": "Google Analytics 4 + Looker Studio",
                "level": "intermediate", "hours": "10",
                "summary": "GA4 ile web/uygulama verisini analiz etme, Looker Studio ile otomatik güncellenen dashboard hazırlama.",
                "outcomes": [
                    "GA4 olay ve dönüşüm yapılandırması",
                    "Kullanıcı davranışı raporlarını yorumlama",
                    "Looker Studio'da dashboard tasarlama",
                    "GA4 verisini Looker Studio'ya bağlama",
                ],
                "prerequisites": ["Temel dijital analitik bilgisi önerilir"],
                "tools": ["Google Analytics 4", "Looker Studio"],
                "syllabus": [
                    {"week": 1, "title": "GA4 Temelleri", "topics": ["Olay tabanlı veri modeli", "Dönüşüm takibi"]},
                    {"week": 2, "title": "Raporlama", "topics": ["Standart ve özel raporlar", "Kullanıcı segmentleri"]},
                    {"week": 3, "title": "Looker Studio Dashboard", "topics": ["Veri kaynağı bağlama", "Görselleştirme ve paylaşım"]},
                ],
                "faq": [
                    {"q": "Evrensel Analytics (UA) yerine neden GA4?", "a": "UA kullanımdan kaldırıldığı için tüm eğitim GA4 üzerinden verilir."},
                ],
            },
        ],
    },
]


def get_all_items():
    """Katalogdaki tüm eğitim item'larını (kategori bilgisiyle) düz liste olarak döner."""
    items = []
    for category in TRAINING_CATEGORIES:
        for item in category["items"]:
            items.append({**item, "category_slug": category["slug"], "category_title": category["title"]})
    return items


def get_item_by_slug(slug):
    """Slug'a göre tek bir eğitim item'ı döner, yoksa None."""
    for item in get_all_items():
        if item["slug"] == slug:
            return item
    return None


LEVEL_LABELS = {
    "beginner": "Başlangıç",
    "intermediate": "Orta",
    "advanced": "İleri",
    "all": "Tüm Seviyeler",
}
