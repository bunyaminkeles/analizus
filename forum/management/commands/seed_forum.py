import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from forum.models import Section, Category, Topic, Post, Profile, Skill, FreelanceJob
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Analizus.com forum içeriklerini oluşturur.'

    def turkish_slugify(self, text):
        replacements = {
            'ı': 'i', 'İ': 'i', 'ğ': 'g', 'Ğ': 'g',
            'ü': 'u', 'Ü': 'u', 'ş': 's', 'Ş': 's',
            'ö': 'o', 'Ö': 'o', 'ç': 'c', 'Ç': 'c',
            '&': 've', '/': '-'
        }
        for src, dest in replacements.items():
            text = text.replace(src, dest)
        return slugify(text)

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING(
            'DİKKAT: Bu işlem tüm Forum verilerini SİLECEKTİR!'))
        confirm = input('Devam etmek istiyor musunuz? (e/h): ')

        if confirm.lower() != 'e':
            self.stdout.write(self.style.ERROR('İşlem iptal edildi.'))
            return

        # =============================================
        # 1. TEMİZLİK
        # =============================================
        self.stdout.write('Veritabanı temizleniyor...')
        Post.objects.all().delete()
        Topic.objects.all().delete()
        Category.objects.all().delete()
        Section.objects.all().delete()
        Skill.objects.all().delete()
        FreelanceJob.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Temizlik tamamlandı.'))

        # =============================================
        # 2. KULLANICILAR
        # =============================================
        users = []
        user_data = [
            ('bunyamin', 'Expert', 'Kurucu & Veri Bilimci'),
            ('admin', 'Expert', 'Platform Yöneticisi'),
            ('user', 'Standard', 'Yeni Üye'),
            ('ben', 'Premium', 'Doktora Öğrencisi'),
            ('figen', 'Expert', 'Dr. İstatistik Uzmanı'),
            ('rabia', 'Premium', 'NLP Araştırmacısı'),
            ('joseph', 'Expert', 'ML Engineer & Ekonometrist'),
            ('beyza', 'Premium', 'Akademik Editör & İçerik Analisti'),
        ]

        for username, acc_type, title in user_data:
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password('pass1234')
                user.save()

            if not hasattr(user, 'profile'):
                Profile.objects.create(
                    user=user, account_type=acc_type, title=title)
            else:
                user.profile.account_type = acc_type
                user.profile.title = title
                user.profile.save()

            users.append(user)

        user_dict = {u.username: u for u in users}

        # =============================================
        # 3. YETENEKLERİ EKLE
        # =============================================
        self.stdout.write('Yetenekler ekleniyor...')
        skills_list = [
            # İstatistik & Akademik
            "SPSS", "R Studio", "Stata", "SAS", "Minitab", "EViews",
            "JASP", "Jamovi", "AMOS", "SmartPLS", "LISREL", "G*Power",
            # Programlama & Veri Bilimi
            "Python", "R", "SQL", "MATLAB", "Julia",
            "Pandas", "NumPy", "Scikit-learn",
            # AI & Deep Learning
            "TensorFlow", "PyTorch", "Keras", "Hugging Face",
            "OpenAI API", "LangChain", "BERT", "GPT", "LLM Fine-tuning",
            # NLP
            "spaCy", "NLTK", "Transformers", "Sentiment Analysis",
            "Named Entity Recognition", "Text Mining",
            # Ekonometri
            "Zaman Serisi", "Panel Veri", "ARDL", "VAR/VECM",
            "GARCH", "Koentegrasyon",
            # Görselleştirme
            "Excel", "Power BI", "Tableau", "Matplotlib",
            "Seaborn", "Plotly", "ggplot2",
            # Nitel Araçlar
            "MAXQDA", "NVivo", "Atlas.ti",
            # Akademik & İçerik
            "Akademik Yazım", "Metin Editörlüğü", "İçerik Analizi",
            "Literatür Taraması", "Anket Tasarımı",
            "Araştırma Yöntemleri", "Etik Kurul Başvurusu",
            "Bibliyometri", "Meta-Analiz", "Sistematik Derleme",
            # Analiz Türleri
            "Regresyon Analizi", "Faktör Analizi", "SEM",
            "Kümeleme Analizi", "Diskriminant Analizi",
            "Survival Analysis", "Bayesian Statistics",
        ]
        for s in skills_list:
            slug_val = self.turkish_slugify(s)
            Skill.objects.get_or_create(
                slug=slug_val, defaults={'name': s})

        # =============================================
        # 4. İÇERİK YAPISI
        # =============================================

        # ─────────────────────────────────────────────
        # BÖLÜM 1: İSTATİSTİK & AKADEMİK ANALİZ
        # ─────────────────────────────────────────────

        spss_topics = [
            {
                'subject': "SPSS'de normallik testi: Shapiro-Wilk mi Kolmogorov-Smirnov mu?",
                'starter': 'user',
                'message': "Merhaba, 120 kişilik bir örneklemim var. Anket verilerimin normal dağılıp dağılmadığını test etmem gerekiyor. Hangisini kullanmalıyım? Ayrıca çarpıklık ve basıklık değerlerine bakmak yeterli mi?",
                'answer': "120 kişilik örneklem için Kolmogorov-Smirnov daha uygun (n>50). Ancak sadece teste güvenme: Çarpıklık (Skewness) ve Basıklık (Kurtosis) değerlerinin -1.5 ile +1.5 arasında olması, Q-Q Plot'ta noktaların çizgiye yakın olması ve histogramın çan eğrisine benzemesi birlikte değerlendirilmeli. Çoğu hakem sadece tek bir kriteri kabul etmez, üçlü kontrol yap.",
                'views': 3456,
            },
            {
                'subject': "Likert ölçekte parametrik test kullanılabilir mi?",
                'starter': 'ben',
                'message': "Danışmanım 5'li Likert ölçekle toplanan veriler için t-testi yapmamı istiyor. Ancak bazı kaynaklar Likert verilerinin ordinal olduğunu ve parametrik test yapılamayacağını söylüyor. Hangi yaklaşım doğru?",
                'answer': "Bu, istatistiğin en tartışmalı konularından biri! Teknik olarak tek bir Likert maddesi ordinaldir. ANCAK birden fazla Likert maddesinin toplamı/ortalaması (yani ölçek puanı) sürekli değişken gibi davranır. Carifio & Perla (2008) ve Norman (2010) çalışmaları parametrik testlerin Likert ölçek puanlarında güvenle kullanılabileceğini göstermiştir. Danışmanınız haklı, ama bunu metodoloji bölümünde bu referanslarla destekleyin.",
                'views': 2890,
            },
            {
                'subject': "AMOS'ta DFA yaparken model uyum indeksleri sınırda kalıyor",
                'starter': 'figen',
                'message': "Doğrulayıcı Faktör Analizi sonuçlarım: CFI=0.89, RMSEA=0.082, SRMR=0.06. CFI 0.90'ın altında, RMSEA 0.08'in üstünde. Modifikasyon indekslerine bakarak hata terimleri arasına kovaryans eklemeli miyim yoksa madde çıkarmalı mıyım?",
                'answer': "Önce teorik olarak düşün: Modifikasyon indeksi yüksek olan hata terimleri aynı alt boyutta mı? Aynı yönteme mi ait (ör: ters kodlanmış maddeler)? Eğer evetse kovaryans eklemen teorik olarak savunulabilir. Ama rastgele ekleme! Hair vd. (2019) CFI>0.90, RMSEA<0.08 sınırlarını kullanır. Senin değerlerin çok kötü değil, 1-2 düşük yüklü maddeyi çıkarmak dengeyi kurabilir. Schermelleh-Engel (2003)'e atıf yaparak savunabilirsin.",
                'views': 2134,
            },
            {
                'subject': "SmartPLS ile PLS-SEM ne zaman kullanılmalı?",
                'starter': 'rabia',
                'message': "Tezimde yapısal eşitlik modellemesi yapacağım ama örneklemim sadece 85 kişi. AMOS mu SmartPLS mi kullanmalıyım?",
                'answer': "85 kişilik örneklemle AMOS riskli çünkü kovaryans tabanlı SEM (CB-SEM) en az 200+ örneklem ister. PLS-SEM ise küçük örneklemlerle çalışabilir (Hair vd., 2017). Ayrıca modelinde formatif yapılar veya tahmin odaklı bir yaklaşım varsa PLS daha uygun. SmartPLS 4 ücretsiz ve kullanıcı dostu. R² değerlerini, f² etki büyüklüklerini ve Q² tahmin gücünü raporlamayı unutma.",
                'views': 1876,
            },
            {
                'subject': "Cronbach Alpha çok yüksek çıkması sorun mu? (0.97)",
                'starter': 'beyza',
                'message': "Ölçeğimin güvenirlik katsayısı 0.97 çıktı. Danışmanım 'Bu kadar yüksek şüpheli, maddeler birbirinin kopyası olabilir' dedi. Gerçekten sorun mu?",
                'answer': "Evet, dikkat! Alpha > 0.95 genellikle 'madde fazlalığı' (item redundancy) göstergesidir. Yani bazı maddeler neredeyse aynı şeyi ölçüyor. Inter-Item Correlation Matrix'e bak: .90'ın üzerinde korelasyon gösteren madde çiftleri varsa birini çıkarmayı düşün. Streiner (2003) 0.90 üzerini 'şişirilmiş güvenirlik' olarak tanımlar. 0.70-0.90 arası idealdir.",
                'views': 1654,
            },
        ]

        anova_topics = [
            {
                'subject': "Tek Yönlü ANOVA'da varyanslar homojen değilse ne yapılır?",
                'starter': 'user',
                'message': "Levene testi p<0.05 çıktı, yani varyanslar homojen değil. ANOVA sonuçlarıma güvenebilir miyim?",
                'answer': "Hayır, klasik ANOVA yerine Welch ANOVA kullanmalısın. SPSS'te One-Way ANOVA penceresinde 'Options' kısmında 'Welch' seçeneğini işaretle. Post-hoc için de Tukey yerine Games-Howell testini tercih et. Bu test eşit olmayan varyanslar için tasarlanmıştır.",
                'views': 2345,
            },
            {
                'subject': "Tekrarlı Ölçümler ANOVA'da Mauchly Küresellik Testi",
                'starter': 'ben',
                'message': "Ön test, son test ve izleme testi olmak üzere 3 ölçümüm var. Mauchly testi anlamlı çıktı (p<0.05). Ne yapmalıyım?",
                'answer': "Küresellik varsayımı ihlal edilmiş demektir. Bu durumda düzeltme faktörlerini kullan: Epsilon değeri >0.75 ise Huynh-Feldt, <0.75 ise Greenhouse-Geisser düzeltmesini raporla. SPSS zaten ikisini de otomatik hesaplar, sadece doğru satırı okumalısın.",
                'views': 1890,
            },
            {
                'subject': "MANOVA ne zaman kullanılır? ANOVA'dan farkı ne?",
                'starter': 'figen',
                'message': "Araştırmamda 3 bağımsız grup var ve 4 farklı bağımlı değişkeni aynı anda test etmek istiyorum. Her birini ayrı ayrı ANOVA ile mi test etmeliyim?",
                'answer': "Ayrı ayrı ANOVA yapmak Tip 1 hata oranını şişirir (çoklu karşılaştırma problemi). MANOVA, birden fazla bağımlı değişkeni aynı anda test ederek bu sorunu çözer. Pillai's Trace veya Wilks' Lambda istatistiklerini raporla. MANOVA anlamlı çıkarsa, sonrasında her değişken için ayrı ANOVA'lar yapabilirsin.",
                'views': 1567,
            },
            {
                'subject': "Etki büyüklüğü raporlamak zorunlu mu?",
                'starter': 'rabia',
                'message': "ANOVA sonucum anlamlı çıktı (p<0.05) ama danışmanım 'p değeri yetmez, etki büyüklüğü de raporla' diyor. Hangi metriği kullanmalıyım?",
                'answer': "APA 7 kılavuzu etki büyüklüğü raporlamayı zorunlu kılıyor. ANOVA için Partial Eta Squared (η²p) kullan: 0.01=küçük, 0.06=orta, 0.14=büyük etki. SPSS'te 'Options' kısmında 'Estimates of effect size' kutusunu işaretle. p değeri sadece 'fark var mı?' sorusuna cevap verir, etki büyüklüğü ise 'bu fark ne kadar anlamlı/önemli?' sorusuna.",
                'views': 2100,
            },
        ]

        regression_topics = [
            {
                'subject': "Çoklu regresyonda çoklu doğrusal bağlantı (Multicollinearity) sorunu",
                'starter': 'joseph',
                'message': "Modelimdeki VIF değerleri 8-12 arasında. Değişkenleri çıkarmak istemiyorum çünkü teorik olarak hepsi önemli. Ne yapabilirim?",
                'answer': "VIF>10 ciddi, 5-10 arası uyarı seviyesidir. Değişken çıkarmadan önce şunları dene: 1) Değişkenleri merkezleme (centering), 2) Birbirine çok benzeyen değişkenleri birleştirerek kompozit skor oluşturma, 3) Ridge Regression veya LASSO kullanma (bunlar multicollinearity'ye dayanıklıdır), 4) PCA ile boyut indirgeme. Eğer hiçbiri işe yaramazsa, en yüksek VIF'li değişkeni teorik gerekçeyle çıkarmak zorunda kalabilirsin.",
                'views': 2567,
            },
            {
                'subject': "Lojistik Regresyonda Odds Ratio yorumlama",
                'starter': 'figen',
                'message': "Sağlık araştırmamda lojistik regresyon çalıştırdım. Sigara içme değişkeninin Exp(B)=2.4 çıktı. Bunu nasıl yorumlamalıyım?",
                'answer': "Exp(B)=2.4 şu demek: 'Diğer değişkenler sabit tutulduğunda, sigara içenlerin hastalığa yakalanma olasılığı içmeyenlere göre 2.4 kat daha fazladır.' Veya '%140 daha yüksek risk' olarak ifade edebilirsin. Eğer Exp(B)=0.6 olsaydı, 'Sigara içmek riski %40 azaltıyor' anlamına gelirdi (koruyucu faktör). Güven aralığını (CI) da mutlaka raporla — eğer CI 1'i kapsıyorsa sonuç anlamsızdır.",
                'views': 3210,
            },
            {
                'subject': "Aracılık (Mediation) analizi: Baron-Kenny mi Process Macro mu?",
                'starter': 'ben',
                'message': "Psikoloji tezimde X→M→Y şeklinde bir aracılık modeli test edeceğim. Baron-Kenny yöntemi hala kabul görüyor mu?",
                'answer': "Baron-Kenny artık 'eski usul' kabul ediliyor ve birçok hakemli dergi tarafından eleştiriliyor. Andrew Hayes'in Process Macro'su (Model 4) Bootstrap yöntemiyle dolaylı etkiyi test eder ve çok daha güçlüdür. 5000 bootstrap örneklemiyle %95 güven aralığı hesapla. Eğer güven aralığı sıfırı kapsamıyorsa aracılık etkisi anlamlıdır. Process Macro'yu SPSS'e eklenti olarak yükleyebilirsin, ücretsiz.",
                'views': 2890,
            },
            {
                'subject': "Moderasyon analizi sonuçlarını grafik ile gösterme",
                'starter': 'beyza',
                'message': "Process Macro Model 1 ile moderasyon testi yaptım. Etkileşim terimi anlamlı çıktı ama bunu nasıl görselleştireceğimi bilmiyorum.",
                'answer': "Process Macro otomatik olarak düşük, orta ve yüksek moderatör düzeylerinde slope değerleri verir. Bunları Excel'de veya R'da 'interaction plot' olarak çizebilirsin. Daha kolay yol: 'interactionR' paketi veya Johnson-Neyman tekniği ile moderatörün hangi değerlerinde etkinin anlamlı olduğunu göster. Jüriler bu grafiklere bayılır!",
                'views': 1987,
            },
        ]

        survey_topics = [
            {
                'subject': "Google Forms ile toplanan anket verisi akademik olarak kabul edilir mi?",
                'starter': 'user',
                'message': "Yüksek lisans tezim için Google Forms ile veri topladım. Jüri 'Bu güvenilir değil' diyebilir mi?",
                'answer': "Google Forms bir veri toplama aracıdır ve akademik olarak kabul edilir. Önemli olan aracın kendisi değil, örneklem yöntemi ve veri kalitesidir. Metodoloji bölümünde şunları açıkla: 1) Örneklem büyüklüğü ve seçim yöntemi, 2) Veri toplama süresi, 3) Kontrol soruları (dikkat testi), 4) Eksik/tutarsız yanıtların elenmesi. Qualtrics veya SurveyMonkey daha profesyonel görünse de Forms da gayet yeterli.",
                'views': 3567,
            },
            {
                'subject': "Anket örneklem büyüklüğünü nasıl hesaplarım?",
                'starter': 'rabia',
                'message': "Tezim için kaç kişiye anket uygulamam gerektiğini bilmiyorum. G*Power mı kullanmalıyım yoksa evren büyüklüğüne göre mi hesaplamalıyım?",
                'answer': "İkisi farklı yaklaşımlar: 1) Evren büyüklüğü biliniyor ve genelleme yapmak istiyorsan Cochran veya Krejcie-Morgan tablosunu kullan. 2) Belirli bir istatistiksel testi çalıştıracaksan (örn: regresyon, ANOVA) G*Power ile güç analizi yap. Örneğin regresyon için: G*Power > F tests > Linear multiple regression > Effect size f²=0.15 (orta etki), α=0.05, Power=0.80, predictor sayısını gir. Minimum örneklem boyutunu verir.",
                'views': 4123,
            },
            {
                'subject': "Açımlayıcı Faktör Analizi (AFA) için örneklem yeterli mi?",
                'starter': 'beyza',
                'message': "28 maddelik bir ölçek geliştirdim, 150 kişiye uyguladım. AFA için yeterli mi?",
                'answer': "Genel kural: madde sayısının en az 5-10 katı örneklem. 28 madde × 5 = 140, yani sınırdasın. Ancak KMO değerine bak: KMO>0.80 ise güzel, >0.60 ise kabul edilebilir. Bartlett Küresellik Testi p<0.05 olmalı. Communalities değerleri de >0.40 olmalı. Eğer bunlar sağlanıyorsa 150 kişi yeterli. Ama 200+ olsa daha rahat savunursun.",
                'views': 2678,
            },
        ]

        # ─────────────────────────────────────────────
        # BÖLÜM 2: YAPAY ZEKA & MAKİNE ÖĞRENMESİ
        # ─────────────────────────────────────────────

        ml_topics = [
            {
                'subject': "Random Forest vs XGBoost: Hangisini ne zaman kullanmalıyım?",
                'starter': 'joseph',
                'message': "Sınıflandırma problemi için model seçimi yapıyorum. İkisi arasındaki fark nedir ve hangisi daha iyi performans verir?",
                'answer': "Random Forest bağımsız ağaçları paralel eğitir (bagging), XGBoost ise her ağacı bir öncekinin hatasını düzeltecek şekilde sıralı eğitir (boosting). Pratikte: 1) Veri seti küçük-orta ise ve yorumlanabilirlik önemliyse → Random Forest, 2) Veri seti büyük ve maksimum doğruluk istiyorsan → XGBoost, 3) Kaggle yarışmalarında XGBoost genelde kazanır ama overfitting'e dikkat et. Her zaman cross-validation ile karşılaştır.",
                'views': 3456,
            },
            {
                'subject': "Feature Engineering: Ham veriyi modele hazırlamanın en iyi yolları",
                'starter': 'bunyamin',
                'message': "ML modelimin doğruluğu %72'de takılı kaldı. Yeni özellikler (features) türetmek performansı artırır mı? Pratik önerileriniz neler?",
                'answer': "Feature engineering modelin %80'ini belirler! Öneriler: 1) Tarih sütunundan gün/ay/yıl/haftanın_günü/mevsim çıkar, 2) Kategorik değişkenlerde target encoding dene, 3) Sayısal değişkenlerde log/karekök dönüşümü uygula, 4) Değişken çaprazlamaları oluştur (örn: gelir/yaş = kişi başı gelir), 5) Domain knowledge kullan — alanı bilmek en güçlü feature'ları yaratır. sklearn.preprocessing ve featuretools kütüphanelerini incele.",
                'views': 2890,
            },
            {
                'subject': "Dengesiz Veri (Imbalanced Data) ile başa çıkma yöntemleri",
                'starter': 'figen',
                'message': "Fraud detection projesinde %98 normal, %2 sahte işlem var. Model hep 'normal' diyor ve %98 doğruluk gösteriyor ama hiç sahtecilik yakalamıyor!",
                'answer': "Klasik sorun! Accuracy yerine F1-Score, Precision-Recall AUC kullan. Çözümler: 1) SMOTE ile azınlık sınıfını sentetik olarak çoğalt, 2) class_weight='balanced' parametresini kullan, 3) Undersampling + Ensemble (EasyEnsemble), 4) Anomaly Detection yaklaşımına geç (Isolation Forest). İmbalanced-learn kütüphanesi bu iş için biçilmiş kaftan.",
                'views': 2345,
            },
            {
                'subject': "AutoML araçları gerçekten veri bilimcinin yerini alabilir mi?",
                'starter': 'ben',
                'message': "AutoML (H2O, AutoGluon, PyCaret) kullandığımda çok iyi sonuçlar alıyorum. Manuel model tuning yapmaya gerek var mı artık?",
                'answer': "AutoML harika bir başlangıç noktası ama sihirli değnek değil. Güçlü yanları: hızlı baseline, hiperparametre optimizasyonu, model karşılaştırma. Zayıf yanları: feature engineering yapmaz, domain bilgisi kullanamaz, sonuçları yorumlayamaz, veri kalitesi sorunlarını çözemez. En iyi yaklaşım: AutoML ile başla, sonra uzman olarak ince ayar yap. Veri bilimcinin gerçek değeri veriyi anlama ve iş problemini çözme becerisindedir.",
                'views': 1987,
            },
            {
                'subject': "Model performansını raporlarken hangi metrikler kullanılmalı?",
                'starter': 'rabia',
                'message': "Makalemdeki ML modelinin performansını raporlayacağım. Sadece Accuracy yeterli mi?",
                'answer': "Kesinlikle yetmez! Sınıflandırma için: Accuracy, Precision, Recall, F1-Score, AUC-ROC, Confusion Matrix. Regresyon için: MAE, MSE, RMSE, R², Adjusted R². Ayrıca: 1) Cross-validation sonuçlarını (mean ± std) raporla, 2) Baseline modelle karşılaştır, 3) Farklı modellerin karşılaştırma tablosunu koy, 4) Confusion matrix'i ısı haritası olarak görselleştir. Hakemler bunu sever!",
                'views': 2567,
            },
        ]

        dl_topics = [
            {
                'subject': "CNN mi Transfer Learning mi? Görüntü sınıflandırma için en iyi yaklaşım",
                'starter': 'joseph',
                'message': "Tıbbi görüntü sınıflandırma projemde 5000 röntgen görüntüsü var. Sıfırdan CNN mi eğitmeliyim yoksa ResNet/VGG gibi önceden eğitilmiş modelleri mi kullanmalıyım?",
                'answer': "5000 görüntü sıfırdan CNN eğitmek için azdır, kesinlikle Transfer Learning kullan. Önerilen yol: 1) ResNet50 veya EfficientNet'i yükle (imagenet ağırlıklarıyla), 2) Son katmanları dondur (freeze), 3) Kendi sınıflandırma katmanını ekle, 4) Önce sadece yeni katmanları eğit, sonra fine-tuning ile son birkaç katmanı da aç. Data Augmentation (döndürme, çevirme, zoom) ile veri setini yapay olarak büyüt. PyTorch'ta torchvision.models kullanabilirsin.",
                'views': 2678,
            },
            {
                'subject': "LSTM vs Transformer: Zaman serisi tahmini için hangisi?",
                'starter': 'bunyamin',
                'message': "Hisse senedi fiyat tahmini yapıyorum. LSTM modeli kurdum ama son zamanlarda Transformer tabanlı modeller (Temporal Fusion Transformer) çok popüler. Geçmeli miyim?",
                'answer': "LSTM hala güçlü ama Transformer tabanlı modeller uzun vadeli bağımlılıkları çok daha iyi yakalar. Önerilerim: 1) Kısa zaman serileri ve az veri → LSTM yeterli, 2) Uzun serilerde ve çok değişkenli tahminlerde → TFT (Temporal Fusion Transformer) üstün, 3) Basit baseline olarak Prophet veya ARIMA ile karşılaştır, 4) Darts kütüphanesi tüm bu modelleri tek çatı altında sunuyor, denemeye değer. Not: Finansal tahmin inherently zordur, %55 doğruluk bile başarıdır!",
                'views': 3123,
            },
            {
                'subject': "GPU olmadan Deep Learning çalışılabilir mi?",
                'starter': 'user',
                'message': "Öğrenciyim, RTX ekran kartı alacak bütçem yok. Derin öğrenme projelerimi nasıl çalıştırabilirim?",
                'answer': "Bütçe sıkıntısı DL'e engel değil! Ücretsiz seçenekler: 1) Google Colab (ücretsiz T4 GPU, günlük ~4 saat), 2) Kaggle Notebooks (haftalık 30 saat GPU), 3) Lightning.ai (ücretsiz GPU kredisi). İpuçları: Colab Pro (\$10/ay) çok daha rahat kullanım sunar. Modelini küçük veriyle test et, son eğitimi bulutta yap. Mixed precision training (fp16) ile bellek kullanımını yarıya indir. Küçük modeller (MobileNet, DistilBERT) az kaynak ister.",
                'views': 4567,
            },
            {
                'subject': "Epoch sayısını nasıl belirlerim? Overfitting nasıl önlenir?",
                'starter': 'ben',
                'message': "Modelim 50 epoch'ta eğitim loss'u düşüyor ama validation loss artmaya başlıyor. Ne yapmalıyım?",
                'answer': "Klasik overfitting! Çözümler: 1) Early Stopping kullan (patience=10, val_loss monitör et), 2) Dropout katmanları ekle (0.3-0.5), 3) Data Augmentation uygula, 4) L1/L2 Regularization ekle, 5) Model karmaşıklığını azalt (daha az katman/nöron), 6) Batch Normalization kullan. Keras'ta: `EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)` callback'ini ekle. En önemlisi: eğitim ve validasyon loss grafiklerini her zaman çiz!",
                'views': 2890,
            },
        ]

        nlp_topics = [
            {
                'subject': "Türkçe NLP için en iyi pre-trained model hangisi?",
                'starter': 'rabia',
                'message': "Türkçe metin sınıflandırma projesi yapıyorum. mBERT mi, BERTurk mü, yoksa başka bir model mi kullanmalıyım?",
                'answer': "Türkçe NLP için kesin sıralama: 1) BERTurk (dbmdz/bert-base-turkish-cased) — Türkçe'ye özel eğitilmiş, en stabil sonuçları verir. 2) Multilingual BERT (mBERT) — 104 dil destekler ama Türkçe performansı BERTurk'ün gerisinde kalır. 3) XLM-RoBERTa — Cross-lingual görevlerde güçlü. 4) Yeni nesil: Hugging Face'te 'savasy/bert-base-turkish-squad' ve 'loodos/bert-base-turkish-uncased' modellerine de bak. Fine-tuning yapacaksan BERTurk ile başla.",
                'views': 3890,
            },
            {
                'subject': "Sentiment Analysis (Duygu Analizi) için etiketli Türkçe veri seti var mı?",
                'starter': 'beyza',
                'message': "Sosyal medya paylaşımlarının duygu analizini yapacağım ama Türkçe etiketli veri bulmakta zorlanıyorum.",
                'answer': "Türkçe sentiment veri setleri: 1) Turkish Sentiment Analysis Dataset (Kaggle'da mevcut), 2) SemEval Türkçe Twitter verisi, 3) Beyazperde film yorumları dataseti, 4) E-ticaret yorum datasetleri (Hepsiburada, Trendyol scraping ile). Kendi verinizi etiketleyecekseniz: en az 3 etiketçi kullanın, Cohen's Kappa ile uyumu ölçün. Hugging Face Datasets kütüphanesinde 'turkish' filtresini deneyin. Not: ChatGPT/Claude ile de veri etiketleme yaptırılabilir ama doğrulama şart!",
                'views': 2456,
            },
            {
                'subject': "Named Entity Recognition (NER) Türkçe'de nasıl yapılır?",
                'starter': 'bunyamin',
                'message': "Türkçe haber metinlerinden kişi, kurum ve yer adlarını otomatik çıkarmak istiyorum. Hangi araçları kullanmalıyım?",
                'answer': "Türkçe NER için: 1) spaCy'nin Türkçe modeli (tr_core_news_trf) — hızlı ve kullanımı kolay, 2) Hugging Face'te 'savasy/bert-base-turkish-ner' modeli — en iyi performans, 3) Stanza (Stanford NLP) Türkçe modeli, 4) Zemberek + kural tabanlı yaklaşım. Fine-tuning yapacaksan WikiANN veya MilliyetNER datasetlerini kullan. Transformers kütüphanesiyle 3-4 satır kodla NER pipeline kurabilirsin: `pipeline('ner', model='savasy/bert-base-turkish-ner')`",
                'views': 2123,
            },
            {
                'subject': "LLM'leri akademik araştırmalarda kullanmanın etik sınırları nerede?",
                'starter': 'figen',
                'message': "ChatGPT veya Claude ile mülakat kodlaması, literatür taraması veya veri analizi yaptırmak etik mi? Jüri veya hakemler bunu nasıl karşılar?",
                'answer': "Bu konu çok tartışmalı ve kurallar hızla değişiyor. Genel kabul: 1) Veri oluşturmak/uydurmak için ASLA kullanılmamalı (fabrication), 2) Metin yazdırmak (ghostwriting) çoğu dergi tarafından yasak, 3) Kod yazımında yardımcı araç olarak kullanılabilir (ama belirtilmeli), 4) Kodlama/analiz doğrulaması için co-pilot olarak kullanılabilir. APA 7 ve Nature/Science dergileri 'AI kullanımını methods bölümünde beyan edin' diyor. KVKK: Kişisel verileri kesinlikle LLM'lere yüklemeyin!",
                'views': 4567,
            },
            {
                'subject': "Text Mining ile büyük ölçekli içerik analizi yapılabilir mi?",
                'starter': 'beyza',
                'message': "Geleneksel içerik analizinde metinleri elle kodluyoruz. 10.000 belgeyi Python ile otomatik kodlamak mümkün mü?",
                'answer': "Kesinlikle! Bu 'Automated Content Analysis' veya 'Computational Text Analysis' olarak adlandırılır. Adımlar: 1) Veri toplama (web scraping veya API), 2) Ön işleme (tokenization, stopword removal, lemmatization — Türkçe için Zemberek), 3) Topic Modeling (LDA veya BERTopic), 4) Sınıflandırma (zero-shot classification veya fine-tuned BERT). BERTopic özellikle harika: konu başlıklarını otomatik çıkarır ve görselleştirir. Ancak sonuçları mutlaka manuel doğrulamayla destekle!",
                'views': 2890,
            },
        ]

        genai_topics = [
            {
                'subject': "Fine-tuning vs RAG: Şirket verilerimle LLM'i nasıl özelleştirmeliyim?",
                'starter': 'joseph',
                'message': "Şirketimizin dahili dokümanlarını (500+ PDF) kullanarak bir chatbot yapmak istiyorum. GPT-4'ü fine-tune mı etmeliyim yoksa RAG mı kurmalıyım?",
                'answer': "Kesinlikle RAG (Retrieval-Augmented Generation) ile başla! Nedenleri: 1) Fine-tuning pahalı ve sürekli güncelleme gerektirir, 2) RAG her zaman güncel veriye erişir, 3) Halüsinasyonu azaltır çünkü kaynak belgeyi referans gösterir. Mimari: PDF → Chunk → Embedding (OpenAI/Cohere) → Vector DB (ChromaDB/Pinecone) → LLM. LangChain veya LlamaIndex ile 50 satır kodla çalışan bir RAG kurabilirsin. Fine-tuning'i sadece modelin 'tonunu' veya 'formatını' değiştirmek istiyorsan düşün.",
                'views': 5678,
            },
            {
                'subject': "Prompt Engineering: LLM'lerden en iyi sonucu alma teknikleri",
                'starter': 'bunyamin',
                'message': "ChatGPT/Claude kullanırken bazen harika, bazen çöp sonuçlar alıyorum. Prompt yazmanın bilimsel bir yöntemi var mı?",
                'answer': "Evet, Prompt Engineering başlı başına bir alan! Temel teknikler: 1) Role Prompting: 'Sen bir istatistik uzmanısın...' 2) Few-shot Learning: 2-3 örnek girdi-çıktı ver, 3) Chain-of-Thought: 'Adım adım düşün' de, 4) Structured Output: 'JSON/tablo formatında cevap ver', 5) Constraints: 'Maksimum 100 kelime, akademik ton'. İleri teknikler: Self-consistency, Tree-of-Thought, ReAct. Araştırma için: PromptBench ve OpenPrompt kütüphanelerini incele. Not: Her model farklı prompt'a farklı tepki verir, A/B test yap!",
                'views': 4321,
            },
            {
                'subject': "Açık kaynak LLM'ler (LLaMA, Mistral) ile neler yapılabilir?",
                'starter': 'rabia',
                'message': "OpenAI API maliyetleri çok yüksek. Kendi sunucumda çalıştırabileceğim açık kaynak alternatifler neler?",
                'answer': "Açık kaynak LLM dünyası patlama yaşıyor! Öneriler: 1) Mistral 7B — hafif ama güçlü, tek GPU'da çalışır, 2) LLaMA 3 — Meta'nın en yeni modeli, çok başarılı, 3) Phi-3 — Microsoft'un küçük ama etkili modeli, 4) Gemma — Google'ın açık modeli. Çalıştırma: Ollama ile yerel bilgisayarda 1 komutla çalıştır, vLLM veya text-generation-inference ile production'a al. Quantization (4-bit GPTQ/GGUF) ile 8GB RAM'li bilgisayarda bile 7B model çalışır. Türkçe için Trendyol'un açık kaynak Türkçe LLM'ini de takip edin!",
                'views': 3890,
            },
            {
                'subject': "LLM Halüsinasyonu: Yapay zekanın uydurduğu bilgileri nasıl tespit ederim?",
                'starter': 'figen',
                'message': "Akademik araştırmamda LLM kullanıyorum ama bazen olmayan makalelere referans veriyor. Bu 'halüsinasyon' sorununu nasıl çözerim?",
                'answer': "LLM halüsinasyonu ciddi bir sorundur, özellikle akademik bağlamda! Çözümler: 1) Her referansı Google Scholar'da doğrula, 2) RAG kullanarak modeli gerçek verilere bağla, 3) Temperature'ı düşür (0.1-0.3) — yaratıcılığı azaltır ama doğruluğu artırır, 4) 'Emin değilsen bilmiyorum de' promptu ekle, 5) Birden fazla LLM'in çıktısını karşılaştır (ensemble). Araştırma için: FactScore ve SelfCheckGPT kütüphaneleri halüsinasyon tespiti yapar. Altın kural: LLM çıktısına asla körü körüne güvenme!",
                'views': 3456,
            },
        ]

        # ─────────────────────────────────────────────
        # BÖLÜM 3: EKONOMETRİ & FİNANSAL MODELLEME
        # ─────────────────────────────────────────────

                # ─────────────────────────────────────────────
        # BÖLÜM 3: EKONOMETRİ & FİNANSAL MODELLEME
        # (Oda: R & Ekonometri)
        # ─────────────────────────────────────────────

        ekonometri_topics = [
            {
                'subject': "Hausman Testi: Fixed mi Random Effects mi?",
                'starter': 'joseph',
                'message': "30 ülke × 20 yıl panel verim var. Hausman testi nasıl yorumlanır?",
                'answer': (
                    "p<0.05 → Fixed Effects, p>0.05 → Random Effects. "
                    "Stata: `hausman fe re`. Ek olarak Breusch-Pagan LM "
                    "ve F testi de mutlaka yap."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "ADF Testi: Birim Kök Nasıl Yorumlanır?",
                'starter': 'fatma',
                'message': "Zaman serisi değişkenlerim durağan mı bilmem lazım. ADF yeterli mi?",
                'answer': (
                    "ADF + PP testi birlikte yap. p<0.05 ise durağan (I(0)). "
                    "Değilse birinci fark al, tekrar test et → I(1). "
                    "R: `adf.test()` (tseries paketi)."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "ARDL Bounds Test: Karışık Durağanlıkta Eşbütünleşme",
                'starter': 'mehmet',
                'message': "Değişkenlerimin bir kısmı I(0) bir kısmı I(1). Ne yapmalıyım?",
                'answer': (
                    "ARDL Bounds Test tam bu durum için. Hiçbir değişken I(2) "
                    "olmamalı. F-istatistiği üst sınırı aşarsa eşbütünleşme var. "
                    "Stata: `ardl y x1 x2, maxlags(4) aic`."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "Johansen Eşbütünleşme: Trace mi Max-Eigen mi?",
                'starter': 'joseph',
                'message': "Johansen testinde Trace ve Max-Eigenvalue farklı sonuç veriyor.",
                'answer': (
                    "Genelde Trace daha güvenilir kabul edilir. İkisi de "
                    "aynı sonucu veriyorsa sorun yok. Farklıysa Trace'e öncelik ver. "
                    "EViews: Quick → Group Statistics → Johansen."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "VAR Model: Gecikme Uzunluğu Nasıl Seçilir?",
                'starter': 'fatma',
                'message': "VAR modelimde kaç gecikme kullanmalıyım?",
                'answer': (
                    "AIC, SBC, HQ kriterlerini karşılaştır. Küçük örneklemde "
                    "SBC tercih edilir. Stata: `varsoc`. "
                    "Ayrıca AR köklerinin birim çember içinde olmasını kontrol et."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "Granger Nedensellik Testi Yorumlama",
                'starter': 'mehmet',
                'message': "Döviz kuru → enflasyon Granger nedensellik çıktı. Gerçek nedensellik mi bu?",
                'answer': (
                    "Hayır! Granger nedensellik sadece 'öngörü gücü' demek. "
                    "X, Y'yi tahmin etmede yardımcı mı onu test eder. "
                    "Gerçek nedensellik için teorik dayanağın sağlam olmalı."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "VECM: Hata Düzeltme Modeli Ne Zaman Kullanılır?",
                'starter': 'joseph',
                'message': "Eşbütünleşme bulduktan sonra VECM kurmam gerekiyor mu?",
                'answer': (
                    "Evet. Eşbütünleşme varsa VAR değil VECM kullan. "
                    "ECM katsayısı negatif ve anlamlı olmalı — uzun dönem "
                    "dengeye dönüş hızını gösterir. R: `cajorls()` (urca)."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "GARCH(1,1): Volatilite Modelinin Temeli",
                'starter': 'fatma',
                'message': "Borsa getiri serisi için GARCH(1,1) kurdum. α + β ne olmalı?",
                'answer': (
                    "α + β < 1 → durağanlık şartı. α + β ≈ 1 ise volatilite "
                    "çok kalıcı. α (ARCH) kısa dönem şoku, β (GARCH) kalıcılığı "
                    "gösterir. R: `ugarchfit()` (rugarch paketi)."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "EGARCH vs GJR-GARCH: Asimetrik Volatilite",
                'starter': 'mehmet',
                'message': "Kaldıraç etkisi var mı diye test etmem lazım. Hangi modeli seçeyim?",
                'answer': (
                    "EGARCH: logaritmik form, negatif varyans problemi olmaz. "
                    "GJR-GARCH: dummy ile asimetri yakalar. İkisini de kur, "
                    "AIC/BIC ile karşılaştır. Python: `arch` kütüphanesi."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "Yapısal Kırılma: Zivot-Andrews Testi",
                'starter': 'joseph',
                'message': "2001 krizini içeren verimde ADF birim kök veriyor ama şüpheliyim.",
                'answer': (
                    "Yapısal kırılma varken ADF yanıltıcı olur. "
                    "Zivot-Andrews tek kırılma, Bai-Perron çoklu kırılma "
                    "tespit eder. Stata: `zandrews varname`."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "Panel Birim Kök Testleri: LLC, IPS, Fisher",
                'starter': 'fatma',
                'message': "Panel verimde durağanlık testi yapacağım. Hangi testi seçmeliyim?",
                'answer': (
                    "LLC ortak birim kök varsayar, IPS bireysel birim kök. "
                    "İkisini birlikte raporla. Yatay kesit bağımlılığı varsa "
                    "CADF (Pesaran 2007) kullan. Stata: `xtunitroot`."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "Arellano-Bond GMM: Dinamik Panel",
                'starter': 'mehmet',
                'message': "Bağımlı değişkenin gecikmesi modelde. OLS sapmalı diyorlar.",
                'answer': (
                    "Doğru, Nickell bias. System GMM kullan. Hansen testi "
                    "p>0.05, AR(2) p>0.05 olmalı. Araç sayısı < grup sayısı. "
                    "Stata: `xtabond2`. R: `pgmm()` (plm paketi)."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "VaR Hesaplama: Parametrik vs Tarihi Simülasyon",
                'starter': 'joseph',
                'message': "Portföy riski için VaR hesaplayacağım. Hangi yöntem daha iyi?",
                'answer': (
                    "Parametrik: hızlı ama normal dağılım varsayar. "
                    "Tarihi simülasyon: varsayım yok ama geçmişe bağımlı. "
                    "Monte Carlo: en esnek ama yavaş. "
                    "Backtesting ile doğrulamayı unutma."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "Expected Shortfall: VaR'ın Ötesi",
                'starter': 'fatma',
                'message': "Basel III neden VaR yerine ES'ye geçti?",
                'answer': (
                    "VaR sadece eşik değer verir, kuyruk riskini görmezden "
                    "gelir. ES, eşik aşıldığında ortalama kaybı hesaplar. "
                    "R: `ES()` fonksiyonu (PerformanceAnalytics paketi)."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "Logit vs Probit: İkili Bağımlı Değişken",
                'starter': 'mehmet',
                'message': "Bağımlı değişkenim 0/1. Logit mi Probit mi?",
                'answer': (
                    "Sonuçlar çok benzer. Logit → Odds Ratio yorumu kolay. "
                    "Probit → çok değişkenli genişlemeye uygun. "
                    "Katsayıları değil marginal etkileri (AME) yorumla! "
                    "Stata: `margins, dydx(*)`."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "Ordered Logit: Likert Ölçek Analizi",
                'starter': 'joseph',
                'message': "5'li Likert ölçekli bağımlı değişkenim var. OLS kullanabilir miyim?",
                'answer': (
                    "OLS yerine Ordered Logit/Probit kullan. Parallel lines "
                    "varsayımını Brant testi ile kontrol et. İhlal varsa "
                    "Generalized Ordered Logit dene. Stata: `ologit y x1 x2`."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "Poisson Regresyon: Sayı Verisi Modelleme",
                'starter': 'fatma',
                'message': "Bağımlı değişkenim sayı (makale sayısı). OLS uygun mu?",
                'answer': (
                    "Hayır, Poisson veya Negatif Binom regresyon kullan. "
                    "Aşırı yayılım (overdispersion) varsa Negatif Binom tercih et. "
                    "R: `glm(y ~ x, family=poisson)`, test: `dispersiontest()`."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "Tobit Model: Sansürlü Bağımlı Değişken",
                'starter': 'mehmet',
                'message': "Bağımlı değişkenim 0'da yığılma gösteriyor (harcama verisi).",
                'answer': (
                    "Tobit model tam bu durum için. Alt sınır 0'da sansürlü. "
                    "Heckman iki aşamalı model de alternatif — seçim ve "
                    "miktar kararları ayrı modellenebilir. Stata: `tobit y x1 x2, ll(0)`."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "Engle-Granger vs Johansen: Hangisi Ne Zaman?",
                'starter': 'joseph',
                'message': "2 değişken arası eşbütünleşme testi. Engle-Granger yeterli mi?",
                'answer': (
                    "2 değişken → Engle-Granger yeterli. 3+ değişken veya "
                    "birden fazla eşbütünleşme vektörü olasılığı → Johansen. "
                    "Karışık I(0)/I(1) → ARDL. R: `ca.jo()` (urca paketi)."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "Mekansal Ekonometri: Moran's I ve SAR/SEM",
                'starter': 'fatma',
                'message': "81 il verisiyle çalışıyorum. Komşu iller birbirini etkiliyor mu?",
                'answer': (
                    "Moran's I ile mekansal otokorelasyonu test et. Anlamlıysa "
                    "SAR veya SEM kur. LM testleri ile seç. "
                    "R: `spdep` + `spatialreg` paketleri. GeoDa da kullanışlı."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "DCC-GARCH: Dinamik Korelasyon Modelleme",
                'starter': 'mehmet',
                'message': "İki piyasa arasındaki korelasyon zamanla değişiyor mu test etmek istiyorum.",
                'answer': (
                    "DCC-GARCH tam bunun için. Önce her seri için GARCH "
                    "tahmin et, sonra dinamik korelasyonu modellle. "
                    "R: `rmgarch` paketi, `dccfit()`. Python: `arch` ile."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "Markov-Switching: Rejim Değişim Modelleri",
                'starter': 'joseph',
                'message': "Ekonomik kriz dönemlerinde model parametreleri değişiyor gibi.",
                'answer': (
                    "MS-VAR veya MS-GARCH ile rejim değişimini modelleyebilirsin. "
                    "Genelde 2 rejim: genişleme ve daralma. Rejim olasılıklarını "
                    "grafikle göster. R: `MSwM` paketi. Stata: `mswitch`."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "Heteroskedastisite: White ve Breusch-Pagan Testleri",
                'starter': 'fatma',
                'message': "OLS modelimde varyans sabit mi test etmem lazım.",
                'answer': (
                    "Breusch-Pagan veya White testi kullan. p<0.05 → heteroskedastisite var. "
                    "Çözüm: Robust standart hatalar (HC1/HC3). "
                    "Stata: `hettest`, sonra `reg y x1 x2, robust`."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "Otokorelasyon: Durbin-Watson ve Breusch-Godfrey",
                'starter': 'mehmet',
                'message': "Zaman serisi modelimde hata terimleri bağımlı olabilir.",
                'answer': (
                    "DW sadece AR(1) test eder. Breusch-Godfrey daha genel. "
                    "Çözüm: Newey-West HAC standart hatalar veya "
                    "Cochrane-Orcutt düzeltmesi. Stata: `bgodfrey`."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "Çoklu Doğrusallık: VIF Eşik Değeri Kaç?",
                'starter': 'joseph',
                'message': "Bağımsız değişkenler arası korelasyon yüksek. VIF kaça kadar kabul?",
                'answer': (
                    "VIF > 10 kesin sorunlu. VIF > 5 şüpheli. "
                    "Çözümler: değişken çıkar, PCA uygula veya Ridge regresyon. "
                    "Stata: `estat vif`. R: `vif()` (car paketi)."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "İçsellik Sorunu ve Araç Değişken (IV) Yöntemi",
                'starter': 'fatma',
                'message': "Modelimde içsellik var diyorlar. 2SLS nasıl uygulanır?",
                'answer': (
                    "İyi bir araç değişken bul: bağımsız değişkenle korelasyonlu "
                    "ama hata terimiyle korelasyonsuz. Sargan/Hansen testi ile "
                    "geçerliliği kontrol et. Stata: `ivregress 2sls y (x=z)`."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "Difference-in-Differences (DiD) Tasarımı",
                'starter': 'mehmet',
                'message': "Politika etkisini ölçmek istiyorum. DiD nasıl kurulur?",
                'answer': (
                    "Tedavi ve kontrol grubu + öncesi/sonrası karşılaştırma. "
                    "Paralel trend varsayımını mutlaka kontrol et. "
                    "Event study grafiği çiz. Stata: `diff` veya `did_multiplegt`."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "Regresyon Süreksizliği (RDD) Tasarımı",
                'starter': 'joseph',
                'message': "Bir eşik değere göre tedavi atanıyor. RDD uygulanabilir mi?",
                'answer': (
                    "Keskin eşik varsa Sharp RDD, olasılıksal eşik varsa "
                    "Fuzzy RDD kullan. Bandwidth seçimi kritik — "
                    "Imbens-Kalyanaraman optimal bant genişliği. R: `rdrobust` paketi."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "Propensity Score Matching (PSM)",
                'starter': 'fatma',
                'message': "Rassal atama yok ama tedavi etkisi ölçmek istiyorum.",
                'answer': (
                    "Logit/Probit ile propensity score hesapla, sonra eşleştir "
                    "(nearest neighbor, caliper, kernel). Dengelemeyi kontrol et. "
                    "Stata: `psmatch2` veya `teffects psmatch`."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "Kripto Piyasalarda Volatilite: GARCH Yeterli mi?",
                'starter': 'mehmet',
                'message': "Bitcoin getiri serisinde GARCH(1,1) kurdum ama yetersiz gibi.",
                'answer': (
                    "Kripto için Student-t veya GED dağılımı kullan. "
                    "FIGARCH uzun hafıza, MS-GARCH rejim değişimi yakalar. "
                    "Saatlik veri varsa HAR-RV modeli daha üstün. Python: `arch`."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "ML vs Ekonometri: Tahmin mi Nedensellik mi?",
                'starter': 'joseph',
                'message': "Random Forest daha yüksek R² veriyor ama hakemler itiraz ediyor.",
                'answer': (
                    "ML tahmin, ekonometri nedensellik içindir. Birleştir: "
                    "Double ML ile nedensel etki tahmin et. SHAP ile ML'yi "
                    "yorumla. Python: `econml` veya `doubleml` paketi."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "Toda-Yamamoto: Durağanlık Gerektirmeyen Nedensellik",
                'starter': 'fatma',
                'message': "Değişkenlerim durağan değil ama Granger nedensellik yapmam lazım.",
                'answer': (
                    "Toda-Yamamoto yöntemi VAR'a ekstra gecikme (d_max) ekler, "
                    "durağanlık şartı aramaz. Maksimum integrasyon derecesini "
                    "belirle ve VAR(p+d_max) kur. EViews'da Wald testi ile yap."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "Panel Eşbütünleşme: Pedroni ve Kao Testleri",
                'starter': 'mehmet',
                'message': "Panel verimde değişkenler I(1). Panel eşbütünleşme nasıl test edilir?",
                'answer': (
                    "Pedroni (7 test istatistiği) ve Kao testi kullan. "
                    "Westerlund testi yatay kesit bağımlılığında daha sağlam. "
                    "Stata: `xtpedroni` ve `xtwest`."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "FMOLS ve DOLS: Uzun Dönem Katsayı Tahmini",
                'starter': 'joseph',
                'message': "Eşbütünleşme bulduktan sonra uzun dönem katsayıları nasıl tahmin ederim?",
                'answer': (
                    "OLS sapmalı olabilir. FMOLS (Fully Modified) veya "
                    "DOLS (Dynamic OLS) kullan. DOLS lead/lag ekler, "
                    "küçük örneklemde daha iyi. Stata: `cointreg`."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "Quantile Regresyon: Koşullu Dağılımın Farklı Noktaları",
                'starter': 'fatma',
                'message': "OLS ortalamayı tahmin ediyor. Medyanı veya kuyrukları modellemek istiyorum.",
                'answer': (
                    "Quantile regresyon farklı yüzdeliklerde (0.10, 0.50, 0.90) "
                    "ayrı katsayılar verir. Aykırı değerlere dayanıklı. "
                    "R: `quantreg` paketi, `rq()`. Stata: `qreg`."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "Copula Modelleri: Bağımlılık Yapısı Modelleme",
                'starter': 'mehmet',
                'message': "İki değişken arası bağımlılık doğrusal korelasyonla açıklanamıyor.",
                'answer': (
                    "Copula modelleri marjinal dağılımları ve bağımlılık yapısını "
                    "ayrı modeller. Clayton (alt kuyruk), Gumbel (üst kuyruk), "
                    "Frank (simetrik). R: `copula` paketi. Python: `copulas`."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "Bayesian VAR (BVAR): Küçük Örneklem Avantajı",
                'starter': 'joseph',
                'message': "Az gözlemle VAR tahmini yapıyorum. Parametre sayısı çok fazla.",
                'answer': (
                    "BVAR Minnesota prior ile parametre sayısı sorununu çözer. "
                    "Küçük örneklemde klasik VAR'dan daha stabil tahminler verir. "
                    "R: `bvartools` veya `BVAR` paketi. Python: `statsmodels`."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "Stochastic Frontier Analysis: Verimlilik Ölçümü",
                'starter': 'fatma',
                'message': "Firmaların teknik verimliliğini ölçmek istiyorum.",
                'answer': (
                    "SFA üretim fonksiyonu + verimsizlik terimi modeller. "
                    "DEA (non-parametrik) ile karşılaştır. Panel SFA zaman "
                    "içinde verimlilik değişimini de gösterir. Stata: `frontier`."
                ),
                'responder': 'joseph',
            },
        ]
                    # ─────────────────────────────────────────────
        # BÖLÜM 4: VERİ BİLİMİ & MÜHENDİSLİK
        # ─────────────────────────────────────────────

        veri_bilimi_topics = [
            {
                'subject': "Python ile Veri Analizine Nereden Başlamalıyım?",
                'starter': 'mehmet',
                'message': "Excel biliyorum ama Python ile veri analizi öğrenmek istiyorum. İlk adım ne olmalı?",
                'answer': (
                    "İlk olarak `pandas`, `numpy`, `matplotlib` öğren. "
                    "CSV okuma, filtreleme, groupby ve basit grafiklerle başla. "
                    "Sonra `seaborn` ve `scikit-learn`e geçebilirsin."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "Pandas'ta groupby Mantığı Nasıl Çalışır?",
                'starter': 'joseph',
                'message': "groupby kullanıyorum ama aggregation mantığını tam oturtamadım.",
                'answer': (
                    "groupby = veriyi gruplara ayır + özet istatistik uygula. "
                    "Örn: `df.groupby('şehir')['satış'].mean()` şehir bazında ortalama satış verir. "
                    "`agg()` ile birden fazla özet fonksiyon da ekleyebilirsin."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "Eksik Veri: Drop mu Fill mi?",
                'starter': 'fatma',
                'message': "Datasetimde çok sayıda missing value var. Silmeli miyim, doldurmalı mıyım?",
                'answer': (
                    "Eksik veri oranına ve mekanizmasına bağlı. "
                    "Azsa silinebilir, ama yüksekse mean/median, KNN veya MICE ile imputasyon düşün. "
                    "Önce eksikliğin rastgele olup olmadığını değerlendir."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "Aykırı Değerleri Tespit Etmenin En Pratik Yolu",
                'starter': 'mehmet',
                'message': "Outlier temizliği yapacağım. Z-score mu IQR mı daha mantıklı?",
                'answer': (
                    "Normal dağılıma yakın veride Z-score işe yarar. "
                    "Daha robust yaklaşım için IQR genelde daha güvenlidir. "
                    "Önce boxplot ile görselleştirmen iyi olur."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "Feature Engineering Neden Bu Kadar Önemli?",
                'starter': 'joseph',
                'message': "Model kurmadan önce feature engineering yapın diyorlar. Gerçekten fark yaratıyor mu?",
                'answer': (
                    "Evet, çoğu zaman modelden daha çok fark yaratır. "
                    "Tarih parçalama, etkileşim değişkeni üretme, log dönüşüm ve kategori kodlama performansı artırır. "
                    "Kaliteli özellik = daha iyi model."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "One-Hot Encoding mi Label Encoding mi?",
                'starter': 'fatma',
                'message': "Kategorik değişkenleri modele vermeden önce nasıl dönüştürmeliyim?",
                'answer': (
                    "Nominal değişkenlerde one-hot encoding tercih edilir. "
                    "Ordinal değişkenlerde label encoding mantıklı olabilir. "
                    "Ağaç tabanlı modellerde label encoding bazen sorun yaratmaz ama dikkatli olmak gerekir."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "Train-Test Split Oranı Kaç Olmalı?",
                'starter': 'mehmet',
                'message': "Veriyi %80-%20 mi böleyim, yoksa cross-validation yeterli mi?",
                'answer': (
                    "Genelde %80-%20 iyi başlangıçtır. "
                    "Ama küçük veri setlerinde cross-validation daha güvenilir sonuç verir. "
                    "Model seçimi için CV, final değerlendirme için ayrı test seti idealdir."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "Cross Validation Ne İşe Yarar?",
                'starter': 'joseph',
                'message': "Tek seferlik test yerine neden k-fold cross validation kullanılıyor?",
                'answer': (
                    "Çünkü tek bölünmede sonuç şansa bağlı olabilir. "
                    "K-fold, modeli farklı alt kümelerde tekrar tekrar test eder ve daha stabil performans ölçümü sağlar. "
                    "Özellikle küçük veri setlerinde faydalıdır."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "SQL Bilmeden Veri Bilimci Olunur mu?",
                'starter': 'fatma',
                'message': "Python öğreniyorum ama SQL zor geliyor. Şart mı gerçekten?",
                'answer': (
                    "Evet, pratikte çok önemli. Çünkü verinin büyük kısmı veritabanında tutulur. "
                    "SELECT, JOIN, GROUP BY, WHERE gibi temel SQL komutlarını mutlaka öğren."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "JOIN Türleri: INNER, LEFT, RIGHT Karışıyor",
                'starter': 'mehmet',
                'message': "SQL JOIN mantığını oturtamıyorum. En kolay nasıl düşünmeliyim?",
                'answer': (
                    "INNER JOIN = iki tabloda ortak olanlar. "
                    "LEFT JOIN = sol tablonun tamamı + sağdan eşleşenler. "
                    "Önce Venn diagram mantığıyla düşün, sonra örnek veriyle dene."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "Dashboard İçin Tableau mu Power BI mı?",
                'starter': 'joseph',
                'message': "Görselleştirme ve dashboard için hangi aracı öğrenmek daha mantıklı?",
                'answer': (
                    "Kurumsal tarafta Power BI çok yaygın, özellikle Microsoft ekosisteminde. "
                    "Tableau görselleştirme esnekliği açısından güçlü. "
                    "Hedef sektörüne göre seçmek en doğrusu."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "ETL Nedir? Veri Biliminde Neden Önemli?",
                'starter': 'fatma',
                'message': "ETL kavramını sürekli görüyorum ama tam oturtamadım.",
                'answer': (
                    "ETL = Extract, Transform, Load. "
                    "Yani veriyi kaynaktan çek, temizle/dönüştür, hedef sisteme yükle. "
                    "Analitik projelerin omurgasıdır çünkü kirli veriyle model kurulmaz."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "Big Data Gerçekten Ne Zaman Gerekli?",
                'starter': 'mehmet',
                'message': "Her veri projesinde Spark/Hadoop öğrenmek gerekiyor mu?",
                'answer': (
                    "Hayır. Veri tek makinede rahat işleniyorsa klasik Python/SQL yeterlidir. "
                    "Spark/Hadoop çok büyük, dağıtık ve hızlı işlenmesi gereken veri için anlamlıdır."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "API'den Veri Çekmek İçin En Kolay Yol",
                'starter': 'joseph',
                'message': "Bir web servisinden veri alıp analiz yapmak istiyorum. Nereden başlamalıyım?",
                'answer': (
                    "Python'da `requests` kütüphanesi ile başla. "
                    "JSON response'u `response.json()` ile alıp pandas DataFrame'e çevirebilirsin. "
                    "Önce GET isteği mantığını öğren."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "Web Scraping: BeautifulSoup mu Selenium mu?",
                'starter': 'fatma',
                'message': "Web'den veri toplayacağım. Hangi araçla başlamalıyım?",
                'answer': (
                    "Sayfa statikse BeautifulSoup yeterli ve hafiftir. "
                    "JavaScript ile yüklenen dinamik sayfalarda Selenium gerekir. "
                    "Ama robots.txt ve yasal sınırları mutlaka kontrol et."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "Veri Görselleştirmede En Sık Yapılan Hatalar",
                'starter': 'mehmet',
                'message': "Dashboard hazırlarken nelere dikkat etmeliyim?",
                'answer': (
                    "Gereksiz renk, aşırı metin ve yanlış grafik seçimi en yaygın hatalar. "
                    "Mesaja uygun grafik seç, eksenleri yanıltıcı kullanma ve sadeliği koru. "
                    "Önce 'neyi göstermek istiyorum?' sorusunu cevapla."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "A/B Testi İçin Minimum Örneklem Nasıl Hesaplanır?",
                'starter': 'joseph',
                'message': "Bir ürün özelliğini test edeceğim ama kaç kullanıcı gerektiğini bilmiyorum.",
                'answer': (
                    "Etki büyüklüğü, anlamlılık düzeyi ve test gücüne göre hesaplanır. "
                    "Power analysis yapman gerekir. "
                    "Python'da `statsmodels.stats.power` modülü iş görür."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "Veri Pipeline Nedir?",
                'starter': 'fatma',
                'message': "Data pipeline kavramını iş ilanlarında çok görüyorum.",
                'answer': (
                    "Verinin bir kaynaktan alınıp işlenerek başka bir sisteme aktarılma akışıdır. "
                    "Otomasyon, tekrar üretilebilirlik ve ölçeklenebilirlik sağlar. "
                    "ETL/ELT süreçleri pipeline'ın parçasıdır."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "Jupyter Notebook mu VS Code mu?",
                'starter': 'mehmet',
                'message': "Veri analizi için hangi ortam daha verimli?",
                'answer': (
                    "Keşifsel analiz ve hızlı prototiplemede Jupyter çok iyi. "
                    "Daha düzenli proje geliştirmede VS Code daha güçlüdür. "
                    "Çoğu kişi ikisini birlikte kullanıyor."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "Git Bilmek Veri Biliminde Gerekli mi?",
                'starter': 'joseph',
                'message': "Version control öğrenmek şart mı?",
                'answer': (
                    "Evet, özellikle ekip işlerinde çok önemli. "
                    "Git ile değişiklikleri takip eder, geri alır ve branch mantığıyla daha güvenli çalışırsın. "
                    "En azından commit, push, pull, branch öğren."
                ),
                'responder': 'mehmet',
            },
        ]


        # ─────────────────────────────────────────────
        # BÖLÜM 5: İÇERİK & EDİTÖRLÜK
        # ─────────────────────────────────────────────

        icerik_editorluk_topics = [
            {
                'subject': "Akademik Makale Editörlüğü ile Proofreading Aynı Şey mi?",
                'starter': 'fatma',
                'message': "Bir dergiye makale göndereceğim. Editörlük ile proofreading farkı nedir?",
                'answer': (
                    "Proofreading daha çok yazım, noktalama ve küçük dil hatalarını düzeltir. "
                    "Editörlük ise akış, yapı, tutarlılık ve akademik ifade kalitesini de geliştirir. "
                    "Yani editörlük daha kapsamlıdır."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "İntihal Oranı Kaç Olmalı?",
                'starter': 'mehmet',
                'message': "Turnitin sonucu %18 çıktı. Bu kabul edilebilir mi?",
                'answer': (
                    "Tek başına oran yeterli ölçüt değildir; eşleşmenin niteliği önemli. "
                    "Kaynakça, kalıp ifadeler ve metodoloji bölümleri oranı artırabilir. "
                    "Asıl önemli olan doğrudan kopya ve atıfsız kullanım olmamasıdır."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "APA 7 Kaynakça Düzeni En Sık Nerede Bozuluyor?",
                'starter': 'joseph',
                'message': "APA 7 ile yazıyorum ama sürekli kaynakça hatası alıyorum.",
                'answer': (
                    "En sık hata: italik kullanımı, yazar sırası, DOI yazımı ve metin içi atıf uyumsuzluğu. "
                    "Kaynakçadaki her eser metinde geçmeli, metindeki her atıf da kaynakçada yer almalı."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "Nitel Veri Analizinde Kodlama Nasıl Başlanır?",
                'starter': 'fatma',
                'message': "Görüşme kayıtlarım var ama tematik analize nasıl başlayacağımı bilmiyorum.",
                'answer': (
                    "Önce veriyi birkaç kez okuyup açık kodlar çıkar. "
                    "Benzer kodları temalarda birleştir. "
                    "MAXQDA veya NVivo kullanıyorsan kod ağacı oluşturarak ilerlemek işini kolaylaştırır."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "MAXQDA mı NVivo mu?",
                'starter': 'mehmet',
                'message': "Nitel analiz için hangi yazılımı öğrenmek daha mantıklı?",
                'answer': (
                    "İkisi de güçlü. MAXQDA arayüz açısından daha kullanıcı dostu bulunuyor, "
                    "NVivo ise akademide çok yaygın. "
                    "Hangisini danışmanın/ekibin kullanıyorsa ona yönelmek pratik olur."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "Tematik Analiz ile İçerik Analizi Aynı mı?",
                'starter': 'joseph',
                'message': "Bu iki yöntemi literatürde bazen aynı gibi görüyorum.",
                'answer': (
                    "Benzer yönleri var ama aynı değil. "
                    "Tematik analiz daha çok anlam örüntülerine ve temalara odaklanır; "
                    "içerik analizi ise daha sistematik kategorileştirme ve bazen sayısallaştırma içerir."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "Tez Yazımında Dil mi Daha Önemli İçerik mi?",
                'starter': 'fatma',
                'message': "İçeriğim güçlü ama dilim çok akademik değil. Bu büyük sorun olur mu?",
                'answer': (
                    "İçerik temeldir ama zayıf ifade güçlü içeriğin etkisini düşürür. "
                    "Akademik dil; netlik, tutarlılık ve ikna gücü sağlar. "
                    "İyi bir editörlük desteği bu farkı ciddi şekilde kapatabilir."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "Paragraf Akışı Nasıl Güçlendirilir?",
                'starter': 'mehmet',
                'message': "Cümlelerim doğru ama metin bütünlüklü akmıyor gibi.",
                'answer': (
                    "Her paragraf tek ana fikir taşımalı. "
                    "İlk cümlede ana fikir, ortada destek, sonda geçiş/sonuç mantığı iyi çalışır. "
                    "Bağlaçlar ve geçiş ifadeleri akışı güçlendirir."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "Akademik İngilizce için En Sık Yapılan Hatalar",
                'starter': 'joseph',
                'message': "Makale çevirisi yaparken doğal görünmeyen cümleler kuruyorum.",
                'answer': (
                    "Kelime kelime çeviri en büyük hata. "
                    "Türkçe cümle yapısını İngilizceye taşımak metni yapaylaştırır. "
                    "Kısa, doğrudan ve alan terminolojisine uygun cümle kurmaya odaklan."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "Özet (Abstract) Yazarken Nelere Dikkat Edilmeli?",
                'starter': 'fatma',
                'message': "Abstract kısmı kısa ama çok zor geliyor. İyi bir özet nasıl yazılır?",
                'answer': (
                    "Amaç, yöntem, bulgu ve sonuç net biçimde yer almalı. "
                    "Gereksiz literatür detayı verilmez. "
                    "Özet, makalenin mini versiyonu gibi düşünülmeli."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "Hakem Düzeltmelerine Nasıl Cevap Verilir?",
                'starter': 'mehmet',
                'message': "Revizyon geldi ama nasıl profesyonel cevap yazacağımı bilmiyorum.",
                'answer': (
                    "Her yoruma tek tek, nazik ve somut şekilde cevap ver. "
                    "Ne değiştirdiğini sayfa/satır belirterek yaz. "
                    "Katılmıyorsan da savunmanı akademik ve sakin tonda yap."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "Anahtar Kelime Seçimi Neden Önemli?",
                'starter': 'joseph',
                'message': "Keywords kısmını genelde rastgele seçiyorum. Etkisi var mı?",
                'answer': (
                    "Evet, görünürlük ve indeksleme açısından önemli. "
                    "Alan yazındaki yaygın terimleri seçmek gerekir. "
                    "Çok genel ya da çok belirsiz kelimelerden kaçın."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "Nitel Çalışmada Geçerlik ve Güvenirlik Nasıl Sağlanır?",
                'starter': 'fatma',
                'message': "Nicel çalışmadaki gibi alfa katsayısı yok. Ne raporlamalıyım?",
                'answer': (
                    "İnandırıcılık, aktarılabilirlik, tutarlılık ve teyit edilebilirlik çerçevesinde raporlanır. "
                    "Kodlayıcı uyumu, katılımcı doğrulaması ve ayrıntılı yöntem açıklaması önemli araçlardır."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "Metin Editörlüğü ile Danışmanlık Karıştırılıyor mu?",
                'starter': 'mehmet',
                'message': "Bazı müşteriler editörlük isterken aslında içerik üretimi bekliyor.",
                'answer': (
                    "Evet, çok sık karışıyor. "
                    "Editörlük mevcut metni iyileştirir; danışmanlık yapı ve yön verir; "
                    "ghostwriting ise baştan yazma işidir. Hizmet sınırlarını baştan netleştirmek gerekir."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "İçerik Analizinde Kod Defteri Oluşturmak Gerekli mi?",
                'starter': 'joseph',
                'message': "Kodları direkt oluştursam olmaz mı, codebook şart mı?",
                'answer': (
                    "Özellikle birden fazla kodlayıcı varsa codebook şart gibi düşünülmeli. "
                    "Kodların tanımı, örnekleri ve dışlama kriterleri tutarlılığı artırır. "
                    "Bu, analiz kalitesini ciddi biçimde yükseltir."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "Makale Giriş Bölümü Nasıl Daha Güçlü Yazılır?",
                'starter': 'fatma',
                'message': "Giriş bölümüm çok bilgi veriyor ama ikna edici değil gibi.",
                'answer': (
                    "İyi giriş; problemi tanımlar, literatürdeki boşluğu gösterir ve çalışmanın katkısını net söyler. "
                    "Sadece bilgi yığmak değil, okuyucuyu çalışmanın neden önemli olduğuna ikna etmek gerekir."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "Tezde Bulgular ve Tartışma Ayrı mı Yazılmalı?",
                'starter': 'mehmet',
                'message': "Bazı tezlerde birlikte, bazılarında ayrı görüyorum.",
                'answer': (
                    "Bu çoğu zaman enstitü kılavuzuna ve alana bağlı. "
                    "Ama mantık olarak bulgular 'ne bulundu?', tartışma ise 'bu ne anlama geliyor?' sorusuna cevap verir. "
                    "Ayrı yazmak genelde daha nettir."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "Yapay Zeka ile Yazılan Metinler Editörlükten Geçmeli mi?",
                'starter': 'joseph',
                'message': "GenAI ile taslak çıkarıyorum. Bu metinleri doğrudan kullanmak riskli mi?",
                'answer': (
                    "Evet, riskli. "
                    "Dil akıcı görünse de kaynak hatası, yüzeysellik ve akademik ton sorunu olabilir. "
                    "Mutlaka insan editör kontrolünden geçmeli."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "Nitel Görüşme Soruları Nasıl Yazılır?",
                'starter': 'fatma',
                'message': "Mülakat formu hazırlıyorum ama sorularım yönlendirici olabilir diye korkuyorum.",
                'answer': (
                    "Açık uçlu, nötr ve tek boyutlu sorular yaz. "
                    "Aynı anda iki şey sorma, cevap ima etme. "
                    "Pilot görüşme yaparak soruların çalışıp çalışmadığını test et."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "Akademik Yazıda Pasif Yapı Şart mı?",
                'starter': 'mehmet',
                'message': "Danışmanım pasif yapı kullan diyor ama bazı makalelerde aktif dil görüyorum.",
                'answer': (
                    "Eskiden pasif yapı daha baskındı ama artık birçok alanda aktif dil kabul görüyor. "
                    "Önemli olan açıklık ve tutarlılık. "
                    "Dergi kılavuzu ne istiyorsa ona öncelik ver."
                ),
                'responder': 'fatma',
            },
        ]


        # ─────────────────────────────────────────────
        # BÖLÜM 6: DANIŞMANLIK & MENTORLUK
        # ─────────────────────────────────────────────

        danismanlik_topics = [
            {
                'subject': "Tez Konusu Seçerken En Büyük Hata Nedir?",
                'starter': 'joseph',
                'message': "Tez konumu belirleyeceğim ama çok geniş düşünmekten korkuyorum.",
                'answer': (
                    "En büyük hata fazla geniş ve yönetilemez konu seçmek. "
                    "Konu; özgün, veri erişilebilir ve süre içinde tamamlanabilir olmalı. "
                    "İyi tez konusu dar ama derin olur."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "Araştırma Sorusu ile Hipotez Aynı Şey mi?",
                'starter': 'fatma',
                'message': "Tez önerisinde research question ve hypothesis kısmını karıştırıyorum.",
                'answer': (
                    "Hayır. Araştırma sorusu neyi anlamak istediğini söyler; "
                    "hipotez ise test edilebilir beklentidir. "
                    "Her nicel çalışmada hipotez olur, ama her çalışmada zorunlu olmayabilir."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "Danışman Seçimi Ne Kadar Belirleyici?",
                'starter': 'mehmet',
                'message': "Konu mu daha önemli danışman mı?",
                'answer': (
                    "İkisi de önemli ama iyi danışman süreci çok kolaylaştırır. "
                    "Alan uyumu, geri bildirim hızı ve iletişim tarzı kritik. "
                    "Sadece ünvana bakarak seçim yapmak risklidir."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "Tez Takvimi Nasıl Hazırlanmalı?",
                'starter': 'fatma',
                'message': "Son ana bırakmamak için nasıl bir plan yapmalıyım?",
                'answer': (
                    "Literatür, yöntem, veri toplama, analiz ve yazım aşamalarını ayrı takvimle. "
                    "Her aşama için küçük teslim tarihleri koy. "
                    "Revizyon süresi için mutlaka tampon zaman bırak."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "Yüksek Lisans Tezi ile Makale Aynı Anda Çıkar mı?",
                'starter': 'joseph',
                'message': "Tezimden makale üretmek istiyorum. Başta buna göre plan yapmalı mıyım?",
                'answer': (
                    "Evet, baştan planlarsan çok daha kolay olur. "
                    "Araştırma sorusunu odaklı kurmak, yöntem ve veri kalitesini makale standardına göre düşünmek avantaj sağlar. "
                    "Her tez makale olmaz ama iyi planlanmış tez olabilir."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "Akademik Kariyer İçin İlk Adım Ne Olmalı?",
                'starter': 'mehmet',
                'message': "Araştırma görevlisi veya doktora yoluna girmek istiyorum. Nereden başlamalıyım?",
                'answer': (
                    "Alanını netleştir, güçlü bir okuma listesi oluştur ve erken dönemde yazmaya başla. "
                    "Konferans, seminer ve hocalarla iletişim ağı kurmak da çok önemli. "
                    "Sadece not ortalamasına odaklanmak yetmez."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "Portföy Hazırlamak Analistler İçin Gerekli mi?",
                'starter': 'fatma',
                'message': "Freelance analiz işi almak istiyorsam portföy oluşturmam şart mı?",
                'answer': (
                    "Kesinlikle evet. "
                    "Gerçek veya anonimleştirilmiş örnek çalışmalar güven yaratır. "
                    "GitHub, Notion, PDF vaka çalışmaları veya dashboard örnekleri kullanılabilir."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "Freelance Uzman Olarak İlk Müşteri Nasıl Bulunur?",
                'starter': 'mehmet',
                'message': "Analiz biliyorum ama müşteri bulmak ayrı bir sorun.",
                'answer': (
                    "Niş bir alan seçip onun üzerinden görünür olmak en etkili yol. "
                    "Örnek işler paylaş, forumlarda faydalı cevaplar ver ve profilini net konumlandır. "
                    "İlk müşteri çoğu zaman güvenden gelir."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "Teklif Hazırlarken Nelere Dikkat Etmeli?",
                'starter': 'joseph',
                'message': "Bir analiz işi için profesyonel teklif metni nasıl hazırlanır?",
                'answer': (
                    "Sorunu anladığını göster, kapsamı netleştir, teslimleri yaz ve süre/fiyatı açık belirt. "
                    "Belirsiz teklif güvensiz görünür. "
                    "Revizyon sınırını da baştan belirtmek önemlidir."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "Müşteri Beklentisini Başta Nasıl Yönetmeli?",
                'starter': 'fatma',
                'message': "Bazı projelerde scope sürekli büyüyor. Bunu nasıl önlerim?",
                'answer': (
                    "İlk görüşmede iş kapsamını yazılı netleştir. "
                    "Teslim edilecek çıktı, süre ve revizyon hakkını açık belirt. "
                    "Sözlü değil yazılı mutabakat iş kurtarır."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "Akademik Danışmanlık ile Etik Sınır Nasıl Korunur?",
                'starter': 'mehmet',
                'message': "Danışmanlık verirken öğrencinin yerine iş yapmak etik mi?",
                'answer': (
                    "Hayır. Etik sınır; yönlendirme, öğretme ve geri bildirim vermektir. "
                    "Doğrudan öğrencinin yerine içerik üretmek veya veri uydurmak ciddi etik ihlaldir. "
                    "Bu sınır baştan net çizilmeli."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "Mentorluk ile Eğitim Arasındaki Fark Nedir?",
                'starter': 'joseph',
                'message': "Birine mentorluk verdiğimi söylüyorum ama aslında ders anlatıyor gibi oluyorum.",
                'answer': (
                    "Eğitim bilgi aktarımıdır, mentorluk ise yön verme ve karar sürecini destekleme. "
                    "Mentor her zaman 'şunu yap' demez; kişinin kendi yolunu bulmasına yardım eder."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "Araştırma Tasarımı Neden En Kritik Aşama?",
                'starter': 'fatma',
                'message': "Birçok kişi veri toplama ve analize odaklanıyor ama tasarımı atlıyor.",
                'answer': (
                    "Çünkü kötü tasarım iyi analizle kurtarılamaz. "
                    "Araştırma sorusu, örneklem, veri toplama yöntemi ve analiz planı baştan uyumlu olmalı. "
                    "En büyük zaman kaybı yanlış tasarımdan gelir."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "Zaman Yönetimi: Aynı Anda Birden Fazla Proje Yürütmek",
                'starter': 'mehmet',
                'message': "Hem tez, hem freelance iş, hem öğrenme sürecini birlikte götürmek zor oluyor.",
                'answer': (
                    "Önceliklendirme ve zaman bloklama şart. "
                    "Aynı gün içinde her şeye biraz bakmak yerine bloklar halinde çalışmak daha verimli. "
                    "Mutlaka haftalık plan yap."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "Akademik CV Nasıl Güçlendirilir?",
                'starter': 'joseph',
                'message': "Henüz çok yayınım yok. CV'mi nasıl daha güçlü gösterebilirim?",
                'answer': (
                    "Yayın yoksa araştırma projeleri, seminerler, konferans sunumları ve teknik becerileri öne çıkar. "
                    "Düzenli, sade ve kanıt odaklı CV daha etkilidir."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "Bir Uzmanın Profilinde Neler Olmalı?",
                'starter': 'fatma',
                'message': "Forum/marketplace profilimi dolduracağım. Ne yazarsam daha güven veririm?",
                'answer': (
                    "Uzmanlık alanı, kullandığın araçlar, örnek projeler, eğitim geçmişi ve net hizmet tanımı olmalı. "
                    "Genel ifadeler yerine somut uzmanlık yazmak daha etkilidir."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "Yeni Başlayan Analistler Fiyatı Nasıl Belirlemeli?",
                'starter': 'mehmet',
                'message': "Çok düşük yazınca değersiz, yüksek yazınca iş kaçıyor gibi hissediyorum.",
                'answer': (
                    "Piyasaya, işin zorluğuna ve teslim süresine göre fiyatlandır. "
                    "Başlangıçta portföy için kontrollü daha düşük fiyat olabilir ama sürdürülemez düşük fiyat zararlıdır."
                ),
                'responder': 'fatma',
            },
            {
                'subject': "Revizyon Politikası Baştan Yazılmalı mı?",
                'starter': 'joseph',
                'message': "Bazı müşteriler sınırsız revizyon bekliyor.",
                'answer': (
                    "Evet, mutlaka yazılmalı. "
                    "Kaç revizyon hakkı olduğu, hangi değişikliklerin kapsam içinde sayıldığı baştan belirtilmeli. "
                    "Bu hem uzmanı hem müşteriyi korur."
                ),
                'responder': 'mehmet',
            },
            {
                'subject': "Online Danışmanlıkta İlk Görüşme Nasıl Yapılmalı?",
                'starter': 'fatma',
                'message': "İlk toplantıda çok dağınık gidiyor. Daha iyi nasıl yönetebilirim?",
                'answer': (
                    "Önce problemi tanımla, sonra hedefi netleştir, ardından kapsam ve takvim konuş. "
                    "Toplantı sonunda kısa yazılı özet göndermek çok profesyonel görünür."
                ),
                'responder': 'joseph',
            },
            {
                'subject': "Kariyer Geçişi: Akademiden Veri Bilimine Mümkün mü?",
                'starter': 'mehmet',
                'message': "Akademik geçmişim var ama sektöre geçmek istiyorum. Geç kalmış sayılır mıyım?",
                'answer': (
                    "Hayır. Akademik araştırma deneyimi; veri okuryazarlığı, metodoloji ve analitik düşünme açısından güçlü avantajdır. "
                    "Bunu sektör diline çevirmek ve portföyle desteklemek gerekir."
                ),
                'responder': 'fatma',
            },
        ]

        # =============================================
        # 5. KATEGORİ KONTROLÜ VE İÇERİKLERİN EKLENMESİ
        # =============================================
        self.stdout.write('Konular ve gönderiler oluşturuluyor...')

        # Kategori silinmiş olma ihtimaline karşı kontrol
        if not Category.objects.exists():
            section = Section.objects.create(title="Genel Analiz Forumu", order=1)
            Category.objects.create(title="SPSS & İstatistik", slug="spss", section=section)
            Category.objects.create(title="Regresyon & İlişki", slug="regresyon", section=section)
            Category.objects.create(title="Metodoloji", slug="metodoloji", section=section)
            Category.objects.create(title="Python & Yapay Zeka", slug="python", section=section)
            Category.objects.create(title="R & Ekonometri", slug="r-programlama", section=section)
            Category.objects.create(title="İçerik & Editörlük", slug="icerik", section=section)
            Category.objects.create(title="Danışmanlık", slug="danismanlik", section=section)

        # İçerik listelerini ilgili kategori slug'ları ile eşleştiriyoruz
        content_map = {
            'spss': spss_topics + anova_topics,
            'regresyon': regression_topics,
            'metodoloji': survey_topics,
            'python': ml_topics + dl_topics + nlp_topics + genai_topics + veri_bilimi_topics,
            'r-programlama': ekonometri_topics,
            'icerik': icerik_editorluk_topics,
            'danismanlik': danismanlik_topics,
        }

        for cat_slug, topics in content_map.items():
            category = Category.objects.filter(slug=cat_slug).first()
            if not category:
                # Eğer belirtilen slug yoksa konular boşa gitmesin diye ilk kategoriye ata
                category = Category.objects.first()

            for t in topics:
                starter = user_dict.get(t.get('starter'), random.choice(users))
                topic = Topic.objects.create(
                    category=category,
                    subject=t['subject'],
                    starter=starter,
                    views=t.get('views', random.randint(100, 1000))
                )

                Post.objects.create(topic=topic, created_by=starter, message=t['message'])

                responder_username = t.get('responder', 'admin')
                responder = user_dict.get(responder_username)
                
                # Cevaplayan ve Soran aynı kişi olmasın
                if not responder or responder == starter:
                    possible_responders = [u for u in users if u != starter]
                    responder = random.choice(possible_responders) if possible_responders else starter

                Post.objects.create(topic=topic, created_by=responder, message=t['answer'], is_best_answer=True)

        self.stdout.write(self.style.SUCCESS('✨ Tüm içerikler başarıyla eklendi ve forum güncellendi!'))