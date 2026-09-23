"""Eğitim hizmetleri kataloğu — DB'siz Python sabiti.

Not: URL adı değil, yalnızca slug tutulur; template `{% url 'egitim_detay' item.slug %}`
ile çözer (URL isimlerini grep'ten kaçıran Python sabitleri hatasını tekrarlama, bkz. analizus.md §26).

Her item'daki `related_tool_url` yalnızca platformda gerçekten karşılığı olan bir
araç/sayfa varsa doldurulur; uydurma/kırık link üretmemek için karşılığı olmayanlarda
alan hiç yazılmaz (get() ile None döner).
"""

from django.utils.translation import gettext_lazy


TRAINING_CATEGORIES = [
    {
        "slug": "ofis-veri",
        "title": gettext_lazy("Ofis & Veri"),
        "icon": "bi-file-earmark-spreadsheet",
        "items": [
            {
                "slug": "excel-veri-analizi", "title": gettext_lazy("Excel ile Veri Analizi"),
                "level": "beginner", "hours": "12", "audience": ["bireysel", "kurumsal"],
                "summary": gettext_lazy("Ham veriyi Excel'de düzenleme, pivot tablo ve temel formüllerle özetleme, basit grafiklerle raporlama."),
                "outcomes": [
                    gettext_lazy("Pivot tablo ile veri özetleme"),
                    gettext_lazy("VLOOKUP / INDEX-MATCH ile veri eşleştirme"),
                    gettext_lazy("Temel grafik ve dashboard hazırlama"),
                    gettext_lazy("Veri temizleme (kopya/hata giderme)"),
                ],
                "prerequisites": [gettext_lazy("Yok")],
                "tools": [gettext_lazy("Microsoft Excel")],
                "syllabus": [
                    {"week": 1, "title": gettext_lazy("Veri Düzenleme ve Temizleme"), "topics": [gettext_lazy("Hücre biçimlendirme"), gettext_lazy("Kopya/hatalı veri temizleme"), gettext_lazy("Metin-sayı dönüşümleri")]},
                    {"week": 2, "title": gettext_lazy("Formüller ve Fonksiyonlar"), "topics": [gettext_lazy("VLOOKUP / INDEX-MATCH"), gettext_lazy("Koşullu fonksiyonlar (SUMIF, COUNTIF)")]},
                    {"week": 3, "title": gettext_lazy("Pivot Tablo ve Özetleme"), "topics": [gettext_lazy("Pivot tablo kurulumu"), gettext_lazy("Gruplama ve filtreleme")]},
                    {"week": 4, "title": gettext_lazy("Görselleştirme ve Raporlama"), "topics": [gettext_lazy("Grafik türleri"), gettext_lazy("Basit dashboard tasarımı")]},
                ],
                "faq": [
                    {"q": gettext_lazy("Excel'in hangi sürümüyle çalışılıyor?"), "a": gettext_lazy("Microsoft 365 güncel sürüm önerilir; 2016 ve sonrası sürümlerle de uyumludur.")},
                    {"q": gettext_lazy("Kendi Excel dosyamla çalışabilir miyim?"), "a": gettext_lazy("Evet, tercih edilen yöntem budur.")},
                ],
            },
            {
                "slug": "excel-ileri", "title": gettext_lazy("İleri Excel: Power Query, Power Pivot, DAX"),
                "level": "intermediate", "hours": "16", "audience": ["kurumsal"],
                "summary": gettext_lazy("Büyük ve dağınık veri kaynaklarını Power Query ile otomatik temizleme, Power Pivot ve DAX ile ileri veri modelleme."),
                "outcomes": [
                    gettext_lazy("Power Query ile otomatik veri temizleme akışı kurma"),
                    gettext_lazy("Power Pivot ile çoklu tablo veri modeli oluşturma"),
                    gettext_lazy("DAX ile hesaplanan alan ve ölçü yazma"),
                    gettext_lazy("Periyodik güncellenen rapor şablonu hazırlama"),
                ],
                "prerequisites": [gettext_lazy("Excel ile Veri Analizi eğitimi veya dengi deneyim")],
                "tools": [gettext_lazy("Microsoft Excel (Power Query, Power Pivot, DAX)")],
                "syllabus": [
                    {"week": 1, "title": gettext_lazy("Power Query ile Veri Hazırlama"), "topics": [gettext_lazy("Çoklu kaynaktan veri çekme"), gettext_lazy("Dönüşüm adımlarını otomatikleştirme")]},
                    {"week": 2, "title": gettext_lazy("Veri Modelleme"), "topics": [gettext_lazy("İlişkisel tablo modeli"), gettext_lazy("Power Pivot'a giriş")]},
                    {"week": 3, "title": gettext_lazy("DAX Formülleri"), "topics": [gettext_lazy("Hesaplanan sütun ve ölçüler"), gettext_lazy("Zaman zekâsı fonksiyonları")]},
                    {"week": 4, "title": gettext_lazy("Otomatik Raporlama"), "topics": [gettext_lazy("Yenilenebilir rapor şablonları"), gettext_lazy("Performans optimizasyonu")]},
                ],
                "faq": [
                    {"q": gettext_lazy("Power BI ile farkı nedir?"), "a": gettext_lazy("Aynı Power Query/DAX motorunu kullanır; bu eğitim Excel içinde kalarak aynı yetkinliği kazandırır.")},
                ],
            },
        ],
    },
    {
        "slug": "programlama",
        "title": gettext_lazy("Programlama"),
        "icon": "bi-code-slash",
        "items": [
            {
                "slug": "python-temel", "title": gettext_lazy("Sıfırdan Python"),
                "level": "beginner", "hours": "20",
                "summary": gettext_lazy("Programlamaya hiç girmemiş katılımcılar için Python'a sıfırdan, veri analizine hazırlık odaklı giriş."),
                "outcomes": [
                    gettext_lazy("Python temel sözdizimi ve veri tipleri"),
                    gettext_lazy("Döngü ve koşul yapılarıyla script yazma"),
                    gettext_lazy("Fonksiyon tanımlama"),
                    gettext_lazy("pandas'a geçişe hazır bir temel"),
                ],
                "prerequisites": [gettext_lazy("Yok")],
                "tools": [gettext_lazy("Python"), gettext_lazy("Jupyter Notebook")],
                "syllabus": [
                    {"week": 1, "title": gettext_lazy("Python'a Giriş"), "topics": [gettext_lazy("Kurulum (Anaconda/Jupyter)"), gettext_lazy("Değişkenler ve veri tipleri")]},
                    {"week": 2, "title": gettext_lazy("Kontrol Yapıları"), "topics": [gettext_lazy("Koşullar (if/elif/else)"), gettext_lazy("Döngüler (for/while)")]},
                    {"week": 3, "title": gettext_lazy("Fonksiyonlar ve Veri Yapıları"), "topics": [gettext_lazy("Fonksiyon tanımlama"), gettext_lazy("Liste, sözlük, demet")]},
                    {"week": 4, "title": gettext_lazy("Dosya İşlemleri ve Hazırlık"), "topics": [gettext_lazy("CSV okuma/yazma"), gettext_lazy("pandas'a giriş önizlemesi")]},
                ],
                "faq": [
                    {"q": gettext_lazy("Hiç kod yazmadım, zor olur mu?"), "a": gettext_lazy("Hayır; eğitim tam olarak sıfır deneyim varsayımıyla kurulur.")},
                ],
            },
            {
                "slug": "python-veri-analizi", "title": gettext_lazy("Python ile Veri Analizi (pandas, numpy, matplotlib)"),
                "level": "intermediate", "hours": "24",
                "summary": gettext_lazy("Gerçek veri setiyle pandas ile veri temizleme, numpy ile sayısal işlemler, matplotlib ile görselleştirme."),
                "outcomes": [
                    gettext_lazy("pandas DataFrame ile veri manipülasyonu"),
                    gettext_lazy("Eksik/aykırı veri temizleme"),
                    gettext_lazy("numpy ile vektörel hesaplama"),
                    gettext_lazy("matplotlib/seaborn ile grafik üretme"),
                ],
                "prerequisites": [gettext_lazy("Temel Python bilgisi (Sıfırdan Python eğitimi veya dengi)")],
                "tools": [gettext_lazy("Python (pandas, numpy, matplotlib)"), gettext_lazy("Jupyter Notebook")],
                "syllabus": [
                    {"week": 1, "title": gettext_lazy("pandas Temelleri"), "topics": [gettext_lazy("DataFrame ve Series"), gettext_lazy("Veri okuma (CSV/Excel)")]},
                    {"week": 2, "title": gettext_lazy("Veri Temizleme"), "topics": [gettext_lazy("Eksik veri yönetimi"), gettext_lazy("Aykırı değer tespiti")]},
                    {"week": 3, "title": gettext_lazy("Gruplama ve Birleştirme"), "topics": [gettext_lazy("groupby/agg"), gettext_lazy("merge/join")]},
                    {"week": 4, "title": gettext_lazy("Görselleştirme"), "topics": [gettext_lazy("matplotlib temelleri"), gettext_lazy("seaborn ile istatistiksel grafikler")]},
                ],
                "faq": [
                    {"q": gettext_lazy("R yerine neden Python?"), "a": gettext_lazy("İkisi de öğretilebilir; Python'un genel amaçlı kullanımı ve geniş kütüphane ekosistemi nedeniyle çoğu katılımcı bunu tercih ediyor, talebe göre R'a da uyarlanabilir.")},
                ],
            },
        ],
    },
    {
        "slug": "istatistik",
        "title": gettext_lazy("İstatistik & Ölçme"),
        "icon": "bi-bar-chart-line",
        "items": [
            {
                "slug": "spss-uygulamali", "title": gettext_lazy("SPSS ile Uygulamalı İstatistik"),
                "level": "beginner", "hours": "18",
                "summary": gettext_lazy("SPSS arayüzünde veri girişinden hipotez testine, tablo okumadan APA raporlamaya kadar uygulamalı istatistik."),
                "outcomes": [
                    gettext_lazy("SPSS'te veri girişi ve değişken tanımlama"),
                    gettext_lazy("Betimsel istatistik ve frekans tabloları"),
                    gettext_lazy("t-testi, ANOVA, ki-kare gibi temel testleri uygulama"),
                    gettext_lazy("SPSS çıktısını APA formatında raporlama"),
                ],
                "prerequisites": [gettext_lazy("Yok")],
                "tools": [gettext_lazy("IBM SPSS Statistics")],
                "syllabus": [
                    {"week": 1, "title": gettext_lazy("SPSS Arayüzü ve Veri Girişi"), "topics": [gettext_lazy("Değişken görünümü"), gettext_lazy("Veri girişi ve kodlama")]},
                    {"week": 2, "title": gettext_lazy("Betimsel İstatistik"), "topics": [gettext_lazy("Frekans ve merkezi eğilim"), gettext_lazy("Normallik testleri")]},
                    {"week": 3, "title": gettext_lazy("Karşılaştırma Testleri"), "topics": [gettext_lazy("t-testi"), gettext_lazy("Tek yönlü ANOVA")]},
                    {"week": 4, "title": gettext_lazy("Raporlama"), "topics": [gettext_lazy("APA tablo formatı"), gettext_lazy("Sonuç yazımı")]},
                ],
                "related_tool_url": "/analiz/ttesti/",
                "faq": [
                    {"q": gettext_lazy("Hangi SPSS sürümü kullanılıyor?"), "a": gettext_lazy("Güncel IBM SPSS Statistics sürümleriyle uyumludur; kurumunuzdaki lisanslı sürümle de çalışılabilir.")},
                ],
            },
            {
                "slug": "istatistik-test-secimi", "title": gettext_lazy("Doğru Testi Seçme ve APA ile Raporlama"),
                "level": "beginner", "hours": "10",
                "summary": gettext_lazy("Değişken türü ve araştırma sorusuna göre doğru istatistiksel testi seçme, sonucu APA 7 standardında yazma."),
                "outcomes": [
                    gettext_lazy("Parametrik / parametrik olmayan test ayrımı"),
                    gettext_lazy("Değişken türüne göre test seçim ağacı kullanma"),
                    gettext_lazy("Varsayım kontrollerini (normallik, homojenlik) yorumlama"),
                    gettext_lazy("APA 7 formatında sonuç raporlama"),
                ],
                "prerequisites": [gettext_lazy("Yok")],
                "tools": [gettext_lazy("SPSS veya Python (isteğe göre)")],
                "syllabus": [
                    {"week": 1, "title": gettext_lazy("Test Seçim Mantığı"), "topics": [gettext_lazy("Değişken türleri"), gettext_lazy("Bağımsız/bağımlı örneklem ayrımı")]},
                    {"week": 2, "title": gettext_lazy("Varsayım Kontrolleri"), "topics": [gettext_lazy("Normallik testleri"), gettext_lazy("Varyans homojenliği")]},
                    {"week": 3, "title": gettext_lazy("APA Raporlama"), "topics": [gettext_lazy("Tablo ve metin formatı"), gettext_lazy("Etki büyüklüğü raporlama")]},
                ],
                "related_tool_url": "/hangi-test/",
                "faq": [
                    {"q": gettext_lazy("Bu eğitim hangi platform aracıyla ilişkili?"), "a": gettext_lazy("/hangi-test/ sayfasındaki karar ağacı bu eğitimin temelini oluşturur; ders sırasında birlikte kullanılır.")},
                ],
            },
            {
                "slug": "olcek-gelistirme", "title": gettext_lazy("Ölçek Geliştirme, Geçerlik ve Güvenirlik"),
                "level": "advanced", "hours": "14",
                "summary": gettext_lazy("Yeni bir ölçme aracı geliştirme sürecinde madde yazımından açımlayıcı faktör analizine, güvenirlik hesaplamasına kadar tüm adımlar."),
                "outcomes": [
                    gettext_lazy("Madde havuzu oluşturma ve uzman görüşü süreci"),
                    gettext_lazy("Açımlayıcı faktör analizi (AFA) uygulama"),
                    gettext_lazy("Cronbach Alfa ile güvenirlik hesaplama"),
                    gettext_lazy("Geçerlik-güvenirlik raporlama"),
                ],
                "prerequisites": [gettext_lazy("Temel istatistik bilgisi (SPSS ile Uygulamalı İstatistik önerilir)")],
                "tools": [gettext_lazy("SPSS"), gettext_lazy("AMOS (isteğe bağlı)")],
                "syllabus": [
                    {"week": 1, "title": gettext_lazy("Ölçek Geliştirme Süreci"), "topics": [gettext_lazy("Madde yazımı"), gettext_lazy("Uzman görüşü ve kapsam geçerliği")]},
                    {"week": 2, "title": gettext_lazy("Faktör Analizi"), "topics": [gettext_lazy("AFA varsayımları (KMO, Bartlett)"), gettext_lazy("Faktör çıkarma ve döndürme")]},
                    {"week": 3, "title": gettext_lazy("Güvenirlik"), "topics": [gettext_lazy("Cronbach Alfa"), gettext_lazy("Madde-toplam korelasyonu")]},
                    {"week": 4, "title": gettext_lazy("Raporlama"), "topics": [gettext_lazy("Geçerlik-güvenirlik tablosu"), gettext_lazy("Tez/makale metin yazımı")]},
                ],
                "related_tool_url": "/analiz/cronbach/",
                "faq": [
                    {"q": gettext_lazy("Doğrulayıcı faktör analizi (DFA) de kapsanıyor mu?"), "a": gettext_lazy("Bu eğitim AFA odaklıdır; DFA/SEM ihtiyacı varsa Yapısal Eşitlik Modellemesi eğitimiyle devam edilir.")},
                ],
            },
            {
                "slug": "yem-sem", "title": gettext_lazy("Yapısal Eşitlik Modellemesi (AMOS / SmartPLS)"),
                "level": "advanced", "hours": "16",
                "summary": gettext_lazy("Ölçüm modeli ve yapısal modelin birlikte test edildiği yapısal eşitlik modellemesine (YEM/SEM) AMOS veya SmartPLS ile uygulamalı giriş."),
                "outcomes": [
                    gettext_lazy("Ölçüm modeli kurma ve DFA"),
                    gettext_lazy("Yapısal model ve yol katsayılarını yorumlama"),
                    gettext_lazy("Model uyum indekslerini (CFI, RMSEA vb.) değerlendirme"),
                    gettext_lazy("YEM sonuçlarını tez/makalede raporlama"),
                ],
                "prerequisites": [gettext_lazy("Ölçek Geliştirme eğitimi veya temel faktör analizi bilgisi")],
                "tools": [gettext_lazy("AMOS"), gettext_lazy("SmartPLS")],
                "syllabus": [
                    {"week": 1, "title": gettext_lazy("YEM'e Giriş"), "topics": [gettext_lazy("Ölçüm modeli vs yapısal model"), gettext_lazy("Örneklem büyüklüğü gereksinimleri")]},
                    {"week": 2, "title": gettext_lazy("Doğrulayıcı Faktör Analizi"), "topics": [gettext_lazy("DFA kurulumu"), gettext_lazy("Uyum indeksleri")]},
                    {"week": 3, "title": gettext_lazy("Yapısal Model"), "topics": [gettext_lazy("Yol analizi"), gettext_lazy("Aracı/düzenleyici değişkenler")]},
                    {"week": 4, "title": gettext_lazy("Raporlama"), "topics": [gettext_lazy("Model diyagramı"), gettext_lazy("Sonuç yazımı")]},
                ],
                "faq": [
                    {"q": gettext_lazy("AMOS mu SmartPLS mi kullanmalıyım?"), "a": gettext_lazy("Kovaryans tabanlı SEM için AMOS, varyans tabanlı (PLS-SEM) için SmartPLS önerilir; ön görüşmede veriniz ve modelinize göre netleştirilir.")},
                ],
            },
        ],
    },
    {
        "slug": "yapay-zeka",
        "title": gettext_lazy("Yapay Zekâ & Modelleme"),
        "icon": "bi-cpu",
        "items": [
            {
                "slug": "makine-ogrenmesi", "title": gettext_lazy("Makine Öğrenmesi (scikit-learn)"),
                "level": "intermediate", "hours": "24",
                "summary": gettext_lazy("scikit-learn ile sınıflandırma, regresyon ve model değerlendirme; kendi verinizle uçtan uca bir ML projesi kurma."),
                "outcomes": [
                    gettext_lazy("Sınıflandırma ve regresyon modelleri kurma"),
                    gettext_lazy("Eğitim/test ayrımı ve çapraz doğrulama"),
                    gettext_lazy("Model performans metriklerini yorumlama"),
                    gettext_lazy("Hiperparametre optimizasyonu"),
                ],
                "prerequisites": [gettext_lazy("Python ile Veri Analizi eğitimi veya dengi deneyim")],
                "tools": [gettext_lazy("Python (scikit-learn, pandas)")],
                "syllabus": [
                    {"week": 1, "title": gettext_lazy("ML'e Giriş"), "topics": [gettext_lazy("Denetimli/denetimsiz öğrenme"), gettext_lazy("Eğitim-test ayrımı")]},
                    {"week": 2, "title": gettext_lazy("Sınıflandırma"), "topics": [gettext_lazy("Karar ağaçları, SVM, lojistik regresyon")]},
                    {"week": 3, "title": gettext_lazy("Regresyon ve Değerlendirme"), "topics": [gettext_lazy("Regresyon modelleri"), gettext_lazy("Çapraz doğrulama, metrikler")]},
                    {"week": 4, "title": gettext_lazy("Model Optimizasyonu"), "topics": [gettext_lazy("Hiperparametre arama"), gettext_lazy("Aşırı öğrenmeyi önleme")]},
                ],
                "related_tool_url": "/analiz/karar-agaci/",
                "faq": [
                    {"q": gettext_lazy("Derin öğrenmeyi de bu eğitimde görecek miyim?"), "a": gettext_lazy("Hayır; bu eğitim klasik ML'e odaklanır. Derin öğrenme ayrı bir eğitimdir.")},
                ],
            },
            {
                "slug": "derin-ogrenme", "title": gettext_lazy("Derin Öğrenme (TensorFlow / Keras)"),
                "level": "advanced", "hours": "24",
                "summary": gettext_lazy("Sinir ağı temellerinden görüntü/metin verisiyle çalışan derin öğrenme modellerine TensorFlow/Keras ile uygulamalı giriş."),
                "outcomes": [
                    gettext_lazy("Yapay sinir ağı mimarisi kurma"),
                    gettext_lazy("CNN ile görüntü sınıflandırma"),
                    gettext_lazy("RNN/Transformer temellerine giriş"),
                    gettext_lazy("Model eğitimi ve aşırı öğrenmeyi önleme"),
                ],
                "prerequisites": [gettext_lazy("Makine Öğrenmesi eğitimi veya dengi deneyim")],
                "tools": [gettext_lazy("Python (TensorFlow, Keras)"), gettext_lazy("Google Colab")],
                "syllabus": [
                    {"week": 1, "title": gettext_lazy("Sinir Ağı Temelleri"), "topics": [gettext_lazy("Perceptron"), gettext_lazy("İleri/geri yayılım")]},
                    {"week": 2, "title": gettext_lazy("Keras ile Model Kurma"), "topics": [gettext_lazy("Katman tasarımı"), gettext_lazy("Kayıp fonksiyonu ve optimizasyon")]},
                    {"week": 3, "title": gettext_lazy("CNN"), "topics": [gettext_lazy("Evrişimli katmanlar"), gettext_lazy("Görüntü sınıflandırma")]},
                    {"week": 4, "title": gettext_lazy("İleri Konular"), "topics": [gettext_lazy("RNN/Transformer'a giriş"), gettext_lazy("Transfer öğrenme")]},
                ],
                "faq": [
                    {"q": gettext_lazy("GPU'suz bilgisayarımla takip edebilir miyim?"), "a": gettext_lazy("Evet; eğitimde ücretsiz Google Colab GPU'su kullanılır, kendi donanımınız yeterli değilse sorun olmaz.")},
                ],
            },
            {
                "slug": "nlp-metin-madenciligi", "title": gettext_lazy("NLP ve Türkçe Metin Madenciliği"),
                "level": "intermediate", "hours": "18",
                "summary": gettext_lazy("Türkçe metin verisiyle ön işleme, duygu analizi ve temel NLP modellerini kurma."),
                "outcomes": [
                    gettext_lazy("Türkçe metin ön işleme (temizleme, kök bulma)"),
                    gettext_lazy("TF-IDF ve kelime gömme temelleri"),
                    gettext_lazy("Duygu analizi modeli kurma"),
                    gettext_lazy("Hazır Türkçe dil modellerini (BERTurk vb.) kullanma"),
                ],
                "prerequisites": [gettext_lazy("Python ile Veri Analizi eğitimi veya dengi deneyim")],
                "tools": [gettext_lazy("Python (NLTK/Zemberek, scikit-learn, Hugging Face)")],
                "syllabus": [
                    {"week": 1, "title": gettext_lazy("Metin Ön İşleme"), "topics": [gettext_lazy("Türkçe'ye özgü zorluklar"), gettext_lazy("Temizleme ve normalizasyon")]},
                    {"week": 2, "title": gettext_lazy("Klasik NLP"), "topics": [gettext_lazy("TF-IDF"), gettext_lazy("Bag-of-words ile sınıflandırma")]},
                    {"week": 3, "title": gettext_lazy("Modern NLP"), "topics": [gettext_lazy("Kelime gömme (embedding)"), gettext_lazy("Hazır Türkçe BERT modelleri")]},
                ],
                "faq": [
                    {"q": gettext_lazy("Sosyal medya verisiyle çalışabilir miyiz?"), "a": gettext_lazy("Evet, kendi topladığınız veya paylaştığınız veri setiyle çalışmak tercih edilen yöntemdir.")},
                ],
            },
            {
                "slug": "agentic-ai", "title": gettext_lazy("Agentic AI: Yapay Zekâ Ajanları ve İş Otomasyonu"),
                "level": "intermediate", "hours": "12", "audience": ["kurumsal"],
                "summary": gettext_lazy("Tekrarlayan veri toplama, analiz ve raporlama süreçlerini yapay zekâ ajanlarıyla otomatikleştirme mantığı ve kurulumu."),
                "outcomes": [
                    gettext_lazy("Ajan tabanlı otomasyon mimarisini tasarlama"),
                    gettext_lazy("Veri toplama/analiz/raporlama hattı kurma"),
                    gettext_lazy("Uzman doğrulama katmanı ekleme"),
                    gettext_lazy("Kurum içi süreçlere uygulanabilir bir prototip çıkarma"),
                ],
                "prerequisites": [gettext_lazy("Temel Python bilgisi önerilir (zorunlu değil)")],
                "tools": [gettext_lazy("Python"), gettext_lazy("LLM API'leri")],
                "syllabus": [
                    {"week": 1, "title": gettext_lazy("Agentic AI Temelleri"), "topics": [gettext_lazy("Ajan mimarisi"), gettext_lazy("Kural tabanlı vs. LLM tabanlı otomasyon")]},
                    {"week": 2, "title": gettext_lazy("Veri Hattı Tasarımı"), "topics": [gettext_lazy("Veri toplama ve işleme"), gettext_lazy("Rapor üretimi")]},
                    {"week": 3, "title": gettext_lazy("Doğrulama ve Devreye Alma"), "topics": [gettext_lazy("Uzman doğrulama katmanı"), gettext_lazy("İzleme ve bildirim")]},
                ],
                "related_tool_url": "/ai-cozumler/",
                "faq": [
                    {"q": gettext_lazy("AI Çözümler (agentic) hizmetinden farkı ne?"), "a": gettext_lazy("Bu eğitimde ekibiniz sistemi kendisi kurmayı öğrenir; /ai-cozumler/ sayfasındaki hizmette ise sistemi ekibimiz sizin için kurar.")},
                ],
            },
        ],
    },
    {
        "slug": "akademik",
        "title": gettext_lazy("Akademik Süreç"),
        "icon": "bi-mortarboard",
        "items": [
            {
                "slug": "akademik-danismanlik", "title": gettext_lazy("Tez ve Makale Süreci Danışmanlığı"),
                "level": "all", "hours": "esnek",
                "summary": gettext_lazy("Araştırma sorusundan yöntem seçimine, veri analizinden tez/makale yazımına kadar akademik süreç boyunca danışmanlık."),
                "outcomes": [
                    gettext_lazy("Araştırma sorusu ve hipotez kurma"),
                    gettext_lazy("Uygun yöntem ve analiz planı belirleme"),
                    gettext_lazy("Bulguları APA formatında yazma"),
                    gettext_lazy("Jüri/hakem sürecine hazırlık"),
                ],
                "prerequisites": [gettext_lazy("Yok")],
                "tools": [gettext_lazy("İhtiyaca göre SPSS/Python/R")],
                "syllabus": [
                    {"week": 1, "title": gettext_lazy("Araştırma Tasarımı"), "topics": [gettext_lazy("Araştırma sorusu"), gettext_lazy("Yöntem seçimi")]},
                    {"week": 2, "title": gettext_lazy("Analiz Planı"), "topics": [gettext_lazy("Uygun testlerin belirlenmesi"), gettext_lazy("Veri toplama stratejisi")]},
                    {"week": 3, "title": gettext_lazy("Yazım ve Raporlama"), "topics": [gettext_lazy("Bulgular bölümü"), gettext_lazy("Tartışma ve sonuç")]},
                ],
                "faq": [
                    {"q": gettext_lazy("Analizi de sizin yapmanızı istersem?"), "a": gettext_lazy("Bu eğitim danışmanlık ve öğretim odaklıdır; analizi doğrudan yaptırmak isterseniz Proje Talebi sayfasına yönlendirilirsiniz.")},
                ],
            },
            {
                "slug": "bibliyometrik-analiz", "title": gettext_lazy("Bibliyometrik Analiz (VOSviewer, Bibliometrix)"),
                "level": "intermediate", "hours": "12",
                "summary": gettext_lazy("Yayın, atıf ve işbirliği ağlarını VOSviewer ve Bibliometrix ile görselleştirerek bibliyometrik analiz yapma."),
                "outcomes": [
                    gettext_lazy("Bibliyometrik veri indirme (Scopus/WoS/OpenAlex)"),
                    gettext_lazy("VOSviewer ile atıf/işbirliği haritası oluşturma"),
                    gettext_lazy("Bibliometrix (R) ile tematik analiz"),
                    gettext_lazy("Bulguları makalede raporlama"),
                ],
                "prerequisites": [gettext_lazy("Yok")],
                "tools": [gettext_lazy("VOSviewer"), gettext_lazy("R (Bibliometrix)")],
                "syllabus": [
                    {"week": 1, "title": gettext_lazy("Veri Toplama"), "topics": [gettext_lazy("Scopus/WoS/OpenAlex'ten veri indirme"), gettext_lazy("Veri formatlama")]},
                    {"week": 2, "title": gettext_lazy("VOSviewer"), "topics": [gettext_lazy("Atıf ve işbirliği ağları"), gettext_lazy("Kümeleme ve görselleştirme")]},
                    {"week": 3, "title": gettext_lazy("Bibliometrix"), "topics": [gettext_lazy("Tematik harita"), gettext_lazy("Performans analizi")]},
                ],
                "related_tool_url": "/bibliometrics/",
                "faq": [
                    {"q": gettext_lazy("Kendi alanımdaki yayınlarla mı çalışacağız?"), "a": gettext_lazy("Evet; kendi araştırma alanınızdaki veri setiyle uygulama yapılır.")},
                ],
            },
            {
                "slug": "kaynakca-programlari", "title": gettext_lazy("Kaynakça Yönetimi: EndNote, Mendeley, Zotero"),
                "level": "beginner", "hours": "6",
                "summary": gettext_lazy("Akademik kaynakları düzenleme, atıf ekleme ve otomatik kaynakça oluşturma için EndNote, Mendeley veya Zotero kullanımı."),
                "outcomes": [
                    gettext_lazy("Kaynak kütüphanesi oluşturma ve organize etme"),
                    gettext_lazy("Word/Google Docs'a otomatik atıf ekleme"),
                    gettext_lazy("Atıf stili değiştirme (APA, Vancouver vb.)"),
                    gettext_lazy("PDF içinden otomatik künye çıkarma"),
                ],
                "prerequisites": [gettext_lazy("Yok")],
                "tools": [gettext_lazy("EndNote"), gettext_lazy("Mendeley"), gettext_lazy("Zotero")],
                "syllabus": [
                    {"week": 1, "title": gettext_lazy("Kurulum ve Kütüphane"), "topics": [gettext_lazy("Program seçimi"), gettext_lazy("Kaynak ekleme yöntemleri")]},
                    {"week": 2, "title": gettext_lazy("Atıf ve Kaynakça"), "topics": [gettext_lazy("Word eklentisiyle atıf"), gettext_lazy("Stil değiştirme")]},
                ],
                "faq": [
                    {"q": gettext_lazy("Hangi programı seçmeliyim?"), "a": gettext_lazy("Üçü de öğretilir; ön görüşmede kurumunuzun/danışmanınızın tercihine göre birine odaklanılır.")},
                ],
            },
            {
                "slug": "literatur-tarama", "title": gettext_lazy("Sistematik Literatür Tarama ve Veri Kazıma"),
                "level": "beginner", "hours": "10",
                "summary": gettext_lazy("PRISMA yaklaşımıyla sistematik literatür taraması yapma ve akademik veritabanlarından veri kazıma."),
                "outcomes": [
                    gettext_lazy("Arama stratejisi ve anahtar kelime kurma"),
                    gettext_lazy("PRISMA akış şemasıyla tarama sürecini belgeleme"),
                    gettext_lazy("OpenAlex/YÖK Tez gibi kaynaklardan veri kazıma"),
                    gettext_lazy("Tarama sonuçlarını sentezleme"),
                ],
                "prerequisites": [gettext_lazy("Yok")],
                "tools": [gettext_lazy("OpenAlex, YÖK Tez, TR Dizin (platform tarama araçları)")],
                "syllabus": [
                    {"week": 1, "title": gettext_lazy("Tarama Stratejisi"), "topics": [gettext_lazy("Anahtar kelime ve arama dizeleri"), gettext_lazy("Dahil etme/dışlama kriterleri")]},
                    {"week": 2, "title": gettext_lazy("PRISMA ve Veri Kazıma"), "topics": [gettext_lazy("PRISMA akış şeması"), gettext_lazy("Otomatik veri indirme")]},
                    {"week": 3, "title": gettext_lazy("Sentez"), "topics": [gettext_lazy("Bulguları tablolaştırma"), gettext_lazy("Tarama bölümü yazımı")]},
                ],
                "related_tool_url": "/tarama/",
                "faq": [
                    {"q": gettext_lazy("Platformdaki tarama araçlarını kullanacak mıyız?"), "a": gettext_lazy("Evet; /tarama/ altındaki YÖK Tez, OpenAlex ve TR Dizin araçları ders sırasında birlikte kullanılır.")},
                ],
            },
        ],
    },
    {
        "slug": "dijital-analitik",
        "title": gettext_lazy("Dijital Analitik"),
        "icon": "bi-graph-up-arrow",
        "items": [
            {
                "slug": "search-console-seo", "title": gettext_lazy("Google Search Console ve SEO Veri Analizi"),
                "level": "beginner", "hours": "8",
                "summary": gettext_lazy("Google Search Console verisiyle bir web sitesinin arama performansını analiz etme ve SEO fırsatlarını tespit etme."),
                "outcomes": [
                    gettext_lazy("Search Console kurulumu ve doğrulama"),
                    gettext_lazy("Tıklama/gösterim/CTR verisini yorumlama"),
                    gettext_lazy("Anahtar kelime fırsatlarını tespit etme"),
                    gettext_lazy("Temel teknik SEO kontrol listesi uygulama"),
                ],
                "prerequisites": [gettext_lazy("Yok")],
                "tools": [gettext_lazy("Google Search Console"), gettext_lazy("Excel/Google Sheets")],
                "syllabus": [
                    {"week": 1, "title": gettext_lazy("Kurulum ve Temel Metrikler"), "topics": [gettext_lazy("Site doğrulama"), gettext_lazy("Performans raporu okuma")]},
                    {"week": 2, "title": gettext_lazy("Analiz ve Fırsatlar"), "topics": [gettext_lazy("Anahtar kelime analizi"), gettext_lazy("Sayfa bazlı performans")]},
                ],
                "faq": [
                    {"q": gettext_lazy("Kendi web sitem yoksa katılabilir miyim?"), "a": gettext_lazy("Katılabilirsiniz; örnek veri setiyle çalışılır, ancak kendi siteniz varsa gerçek veriyle ilerlemek önerilir.")},
                ],
            },
            {
                "slug": "ga4-looker", "title": gettext_lazy("Google Analytics 4 + Looker Studio"),
                "level": "intermediate", "hours": "10",
                "summary": gettext_lazy("GA4 ile web/uygulama verisini analiz etme, Looker Studio ile otomatik güncellenen dashboard hazırlama."),
                "outcomes": [
                    gettext_lazy("GA4 olay ve dönüşüm yapılandırması"),
                    gettext_lazy("Kullanıcı davranışı raporlarını yorumlama"),
                    gettext_lazy("Looker Studio'da dashboard tasarlama"),
                    gettext_lazy("GA4 verisini Looker Studio'ya bağlama"),
                ],
                "prerequisites": [gettext_lazy("Temel dijital analitik bilgisi önerilir")],
                "tools": [gettext_lazy("Google Analytics 4"), gettext_lazy("Looker Studio")],
                "syllabus": [
                    {"week": 1, "title": gettext_lazy("GA4 Temelleri"), "topics": [gettext_lazy("Olay tabanlı veri modeli"), gettext_lazy("Dönüşüm takibi")]},
                    {"week": 2, "title": gettext_lazy("Raporlama"), "topics": [gettext_lazy("Standart ve özel raporlar"), gettext_lazy("Kullanıcı segmentleri")]},
                    {"week": 3, "title": gettext_lazy("Looker Studio Dashboard"), "topics": [gettext_lazy("Veri kaynağı bağlama"), gettext_lazy("Görselleştirme ve paylaşım")]},
                ],
                "faq": [
                    {"q": gettext_lazy("Evrensel Analytics (UA) yerine neden GA4?"), "a": gettext_lazy("UA kullanımdan kaldırıldığı için tüm eğitim GA4 üzerinden verilir.")},
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
    "beginner": gettext_lazy("Başlangıç"),
    "intermediate": gettext_lazy("Orta"),
    "advanced": gettext_lazy("İleri"),
    "all": gettext_lazy("Tüm Seviyeler"),
}
