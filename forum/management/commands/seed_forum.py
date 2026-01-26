import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from forum.models import Section, Category, Topic, Post, Profile, Skill, FreelanceJob
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Veritabanını temizler ve ANALIZUS içerikleriyle doldurur.'

    def turkish_slugify(self, text):
        """Türkçe karakterleri düzgünce dönüştüren slug fonksiyonu"""
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
        self.stdout.write(self.style.WARNING('DİKKAT: Bu işlem tüm Forum verilerini (Bölümler, Kategoriler, Konular, Mesajlar) SİLECEKTİR!'))
        confirm = input('Devam etmek istiyor musunuz? (e/h): ')
        
        if confirm.lower() != 'e':
            self.stdout.write(self.style.ERROR('İşlem iptal edildi.'))
            return

        # 1. TEMİZLİK
        self.stdout.write('Veritabanı temizleniyor...')
        Post.objects.all().delete()
        Topic.objects.all().delete()
        Category.objects.all().delete()
        Section.objects.all().delete()
        Skill.objects.all().delete()
        FreelanceJob.objects.all().delete()
        self.stdout.write('Temizlik tamamlandı.')

        # 2. KULLANICILAR
        users = []
        user_data = [
            ('VeriGorselci', 'Expert', 'Data Visualization Uzmanı'),
            ('MuhasebeUzmani', 'Premium', 'Finans Analisti'),
            ('Otomasyoncu', 'Premium', 'VBA & Makro Uzmanı'),
            ('Planlama_Y', 'Standard', 'İş Planlama Uzmanı'),
            ('StratejiAnalisti', 'Expert', 'Business Intelligence'),
            ('Sosyolog_N', 'Expert', 'Dr. Nitel Araştırmacı'),
            ('GorselAnaliz', 'Premium', 'Etnograf'),
            ('Sahada_Arastirma', 'Standard', 'Saha Araştırmacısı'),
            ('AkademikEtik', 'Expert', 'Araştırma Metodolojisti'),
            ('Iletisimci', 'Standard', 'İletişim Uzmanı'),
            ('Ekonometrist', 'Expert', 'Doç. Dr. Ekonometri'),
            ('Muhendislik_R', 'Premium', 'Makine Mühendisi'),
            ('VeriBilimci_A', 'Premium', 'Data Scientist'),
            ('AI_Ogrenci', 'Standard', 'YL Öğrencisi'),
            ('SaglikIst', 'Standard', 'Sağlık İstatistikçisi'),
            ('Klinik_Aras', 'Expert', 'Dr. Klinik Araştırmacı'),
            ('Ekonometri_S', 'Premium', 'Ekonometri Uzmanı'),
            ('Psikoloji_Tez', 'Standard', 'Doktora Öğrencisi'),
            ('Yonetim_Aras', 'Premium', 'İşletme Araştırmacısı'),
            ('Sosyal_Veri', 'Standard', 'Sosyal Bilimci'),
            ('AI_Junior', 'Standard', 'AI Meraklısı'),
            ('Donanim_Meraklisi', 'Premium', 'Deep Learning Dev'),
            ('ModelEgitmeni', 'Expert', 'ML Engineer'),
            ('Dil_Islemci', 'Premium', 'NLP Uzmanı'),
            ('Etik_AI', 'Standard', 'AI Ethics Researcher'),
            ('Literatur_Tarama', 'Expert', 'Bibliyometri Uzmanı'),
            ('Arastirmaci_X', 'Premium', 'Akademisyen'),
            ('Bilim_Haritaci', 'Standard', 'Scientometrics'),
            ('AkademikKariyer', 'Standard', 'Doktora Adayı'),
            ('YayinHedefi', 'Premium', 'Araştırmacı'),
            ('AnalizBot', 'Expert', 'AI Asistan'),
            ('Akademik_Kus', 'Standard', 'Doktora Öğrencisi'),
        ]

        admin_user = User.objects.filter(is_superuser=True).first()

        for username, acc_type, title in user_data:
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password('pass1234')
                user.save()

            if not hasattr(user, 'profile'):
                Profile.objects.create(user=user, account_type=acc_type, title=title)
            else:
                user.profile.account_type = acc_type
                user.profile.title = title
                user.profile.save()

            users.append(user)

        if admin_user:
            users.append(admin_user)
            if not hasattr(admin_user, 'profile'):
                Profile.objects.create(user=admin_user, account_type='Expert', title='Sistem Yöneticisi')

        # YETENEKLERİ EKLE
        self.stdout.write('Yetenekler ekleniyor...')
        skills_list = [
            "SPSS", "R Studio", "Stata", "SAS", "Minitab", "EViews", "JASP", "Jamovi", "AMOS", "SmartPLS",
            "Python", "R", "SQL", "MATLAB", "Julia", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch",
            "Excel", "Power BI", "Tableau", "QlikView", "Google Data Studio",
            "MAXQDA", "NVivo", "Atlas.ti",
            "Akademik Yazım", "Literatür Taraması", "Anket Tasarımı", "Araştırma Yöntemleri", "Etik Kurul Başvurusu",
            "Regresyon Analizi", "Faktör Analizi", "SEM", "Zaman Serisi", "Meta-Analiz", "G*Power"
        ]
        for s in skills_list:
            Skill.objects.get_or_create(name=s)

        # 3. İÇERİK YAPISI - PART3 DAHİL TÜM İÇERİKLER

        # ===== EXCEL & İŞ ZEKASI =====
        excel_topics = [
            {
                'subject': "Excel'de otomatik güncellenen Dashboard nasıl yapılır?",
                'starter': 'VeriGorselci',
                'message': "Verilerimi her hafta güncelliyorum, grafiklerin manuel kaydırılmadan otomatik büyümesini nasıl sağlarım?",
                'answer': 'Verilerini "Tablo" (Ctrl+L) formatına sokmalısın. Grafik veri kaynağı tablo olursa, yeni veri eklediğinde grafik otomatik genişler. Pivot Table kullanıyorsan "Dilimleyici" (Slicer) eklemeyi unutma!',
                'views': 892,
            },
            {
                'subject': "10 farklı Excel dosyasını tek tabloda toplamak",
                'starter': 'MuhasebeUzmani',
                'message': "Farklı şubelerden gelen aylık raporları tek bir ana tabloda nasıl birleştiririm?",
                'answer': 'Veri sekmesinden "Verileri Al" > "Dosyadan" > "Klasörden" yolunu izle. Power Query tüm dosyaları sütun başlıklarına göre eşleştirip saniyeler içinde birleştirir.',
                'views': 1245,
            },
            {
                'subject': "Excel'de 'Makrolar devre dışı bırakıldı' hatası",
                'starter': 'Otomasyoncu',
                'message': "Yazdığım VBA kodları başka bilgisayarda çalışmıyor, neden?",
                'answer': 'Dosya > Seçenekler > Güven Merkezi > Makro Ayarları\'ndan "Tüm makroları etkinleştir" seçilmeli. Ayrıca dosyanın `.xlsx` değil, `.xlsm` formatında kaydedildiğinden emin ol.',
                'views': 756,
            },
            {
                'subject': "Hücre değerine göre tüm satırı renklendirme",
                'starter': 'Planlama_Y',
                'message': 'Sadece tek hücreyi değil, durum "Tamamlandı" ise tüm satırı yeşil yapmak istiyorum.',
                'answer': 'Koşullu Biçimlendirme > Yeni Kural > "Biçimlendirilecek hücreleri belirlemek için formül kullan" seç. Formüle `=$C2="Tamamlandı"` yaz (Dolar işareti sadece sütunda kalmalı).',
                'views': 634,
            },
            {
                'subject': "Büyük veri setleri için Excel yeterli mi?",
                'starter': 'StratejiAnalisti',
                'message': "1 milyon satırın üzerindeki verilerde Excel çok kasıyor, Power BI'a geçmeli miyim?",
                'answer': "Kesinlikle evet. Excel'in satır limiti 1.048.576'dır. Power BI ise \"Veri Modeli\" mimarisiyle milyonlarca satırı saniyeler içinde işleyebilir.",
                'views': 1567,
            },
        ]

        # ===== NİTEL ANALİZ ARAÇLARI =====
        nitel_topics = [
            {
                'subject': "Mülakat metinlerini kodlarken nelere dikkat edilmeli?",
                'starter': 'Sosyolog_N',
                'message': "MAXQDA'da çok fazla kod oluşturmak analizi zorlaştırır mı?",
                'answer': 'Başlangıçta "Açık Kodlama" yaparken cömert olabilirsin ama sonra bu kodları hiyerarşik temalar altında toplamalısın. "Kod Ağacı" çok karmaşıksa analizde kaybolabilirsin.',
                'views': 423,
            },
            {
                'subject': "NVivo ile fotoğraf ve video kodlanabilir mi?",
                'starter': 'GorselAnaliz',
                'message': "Etnografik çalışmamda fotoğrafları analiz birimi olarak kullanabilir miyim?",
                'answer': "Evet, NVivo'da resim dosyalarını içe aktarıp belirli bölgeleri (region) kare içine alarak kodlayabilirsin. Her bölgeye ayrı notlar eklemek mümkün.",
                'views': 312,
            },
            {
                'subject': "Ses kayıtlarını metne dönüştüren en iyi araç hangisi?",
                'starter': 'Sahada_Arastirma',
                'message': "Mülakatları tek tek elle yazmak çok vakit alıyor. Yapay zeka çözümü var mı?",
                'answer': 'Türkçe için "Otter.ai" zayıf kalsa da, "Whisper AI" veya yerli "Voiser" oldukça başarılı. Metne çevirdikten sonra MAXQDA\'ya `.docx` olarak aktarabilirsin.',
                'views': 867,
            },
            {
                'subject': "İki farklı kodlayıcı arasındaki uyum (Inter-coder Reliability)",
                'starter': 'AkademikEtik',
                'message': "Aynı metni iki kişi kodladık, uyum oranını nasıl raporlamalıyız?",
                'answer': 'MAXQDA içinde "Kullanıcılar Arası Uyumu Kontrol Et" aracı vardır. Cohen\'s Kappa katsayısının 0.70 üzerinde olması akademik olarak kabul edilebilirdir.',
                'views': 534,
            },
            {
                'subject': "En sık geçen kavramları görselleştirme",
                'starter': 'Iletisimci',
                'message': "Odak grup görüşmelerinde en çok kullanılan kelimeleri nasıl raporlarım?",
                'answer': '"Kelime Bulutu" (Word Cloud) aracını kullan. Ancak "ve, ama, gibi" gibi anlam taşımayan kelimeleri "Stop Word List" (Hariç Tutulanlar) listesine eklemeyi unutma.',
                'views': 445,
            },
        ]

        # ===== STATA & MATLAB =====
        stata_topics = [
            {
                'subject': "Panel veride Fixed Effects vs Random Effects?",
                'starter': 'Ekonometrist',
                'message': "Hangisini seçeceğime nasıl karar veririm?",
                'answer': "Stata'da `hausman` testini kullanmalısın. Eğer p < 0.05 ise Fixed Effects (Sabit Etkiler) modelini kullanman gerekir.",
                'views': 1123,
            },
            {
                'subject': "MATLAB plot renklerini ve kalınlıklarını ayarlama",
                'starter': 'Muhendislik_R',
                'message': "Makale için yüksek çözünürlüklü grafik çıktısı nasıl alınır?",
                'answer': "`plot(x,y,'LineWidth',2,'Color','r')` komutunu kullan. Çıktı alırken `exportgraphics` fonksiyonu ile 300 DPI çözünürlükte `.tiff` veya `.pdf` kaydet.",
                'views': 678,
            },
            {
                'subject': "Analizlerimi neden Do-File ile kaydetmeliyim?",
                'starter': 'VeriBilimci_A',
                'message': "Komut penceresinden yazmak daha hızlı değil mi?",
                'answer': 'Hayır, Do-File analizin "kara kutusu"dur. Hata yaptığında veya hakem düzeltme istediğinde tek tıkla her şeyi en baştan hatasız çalıştırabilirsin.',
                'views': 534,
            },
            {
                'subject': "MATLAB ile hazır yapay zeka modelleri kullanılabilir mi?",
                'starter': 'AI_Ogrenci',
                'message': "Resim sınıflandırma için hazır modeller var mı?",
                'answer': '"Deep Learning Toolbox" içinde AlexNet, GoogLeNet gibi önceden eğitilmiş modelleri saniyeler içinde çağırıp kendi verilerinle "Transfer Learning" yapabilirsin.',
                'views': 892,
            },
            {
                'subject': "Eksik verileri (Missing Values) toplu silme",
                'starter': 'SaglikIst',
                'message': "`drop if missing(var)` komutu güvenli mi?",
                'answer': 'Güvenlidir ancak veri kaybına yol açar. Önce `mdesc` komutuyla eksiklik oranına bak, eğer oran %5\'ten azsa silebilirsin, fazlaysa "Multiple Imputation" yöntemini düşün.',
                'views': 445,
            },
        ]

        # ===== REGRESYON & İLİŞKİ ANALİZİ =====
        regresyon_topics = [
            {
                'subject': "Odds Ratio (Olasılıklar Oranı) nedir?",
                'starter': 'Klinik_Aras',
                'message': "Lojistik regresyon sonucunda çıkan Exp(B) değerini nasıl okurum?",
                'answer': "Exp(B) > 1 ise bağımsız değişken bağımlı değişkenin gerçekleşme olasılığını artırıyor demektir. Örneğin 1.50 çıktıysa, o durumun görülme olasılığı %50 artıyor demektir.",
                'views': 1456,
            },
            {
                'subject': "VIF değerleri kaç olmalı?",
                'starter': 'Ekonometri_S',
                'message': "Bağımsız değişkenlerim birbirine çok benziyor, model bozulur mu?",
                'answer': "VIF değerlerine bak. VIF > 10 ise ciddi bir çoklu doğrusal bağlantı sorunu vardır. Akademik olarak genellikle 5'in altı istenir.",
                'views': 1234,
            },
            {
                'subject': "Baron ve Kenny yöntemi hala geçerli mi?",
                'starter': 'Psikoloji_Tez',
                'message': "Danışmanım Process Macro kullanmamı istiyor, farkı nedir?",
                'answer': "Baron-Kenny artık eskidi. Hayes'in **Process Macro**su (Bootstrap yöntemi) çok daha güçlü ve modern kabul ediliyor. Model 4 en yaygın aracılık modelidir.",
                'views': 1678,
            },
            {
                'subject': "Etkileşim terimi (Interaction Term) nasıl oluşturulur?",
                'starter': 'Yonetim_Aras',
                'message': "Cinsiyetin eğitimin maaş üzerindeki etkisini değiştirdiğini nasıl test ederim?",
                'answer': "Eğitim ve Cinsiyet değişkenlerini çarparak yeni bir değişken oluşturmalısın. Eğer bu çarpım terimi regresyonda anlamlı çıkarsa, moderasyon etkisi vardır.",
                'views': 987,
            },
            {
                'subject': "Kategorik değişkenler regresyona nasıl girer?",
                'starter': 'Sosyal_Veri',
                'message': "Eğitim durumu (Lise, Lisans, Lisansüstü) değişkenini nasıl modele eklerim?",
                'answer': 'n-1 kuralını uygula. 3 kategorin varsa 2 adet kukla değişken oluşturmalısın. Bir kategoriyi "Referans" olarak dışarıda bırakmalısın.',
                'views': 756,
            },
        ]

        # ===== YAPAY ZEKA & DERİN ÖĞRENME =====
        ai_topics = [
            {
                'subject': "Tez çalışmamda Kaggle verisi kullanabilir miyim?",
                'starter': 'AI_Junior',
                'message': "Gerçek dünya verisi yerine Kaggle kullanmak akademik değerini düşürür mü?",
                'answer': 'Hayır, ancak verinin kaynağını (metadata) iyi açıklamalı ve "Secondary Data" olarak belirtmelisin. Çok popüler veri setleri (Titanic gibi) yerine daha spesifik olanları seç.',
                'views': 1234,
            },
            {
                'subject': "Derin öğrenme için RTX 3060 yeterli mi?",
                'starter': 'Donanim_Meraklisi',
                'message': "Kendi bilgisayarımda mı yoksa Colab bulutunda mı model eğitmeliyim?",
                'answer': "3060 giriş seviyesi için harika. Ancak çok katmanlı CNN veya Transformer eğiteceksen Google Colab'ın ücretsiz T4 GPU'su bazen daha hızlı olabilir.",
                'views': 1567,
            },
            {
                'subject': "Eğitim kaybı düşüyor ama test kaybı artıyor!",
                'starter': 'ModelEgitmeni',
                'message': "Modelim eğitim verisini ezberliyor, ne yapmalıyım?",
                'answer': "Dropout katmanları ekle, öğrenme oranını (learning rate) düşür veya veri artırma (Data Augmentation) tekniklerini kullan.",
                'views': 2134,
            },
            {
                'subject': "Metin sınıflandırmada BERT neden bu kadar popüler?",
                'starter': 'Dil_Islemci',
                'message': "Word2Vec'ten farkı nedir?",
                'answer': 'BERT kelimenin "bağlamını" anlar. "Yüz" kelimesinin sayı mı yoksa çehre mi olduğunu sağındaki ve solundaki kelimelere bakarak (Bi-directional) çözer.',
                'views': 1890,
            },
            {
                'subject': "Yapay zeka modellerindeki taraflılık (Bias) sorunu",
                'starter': 'Etik_AI',
                'message': "Modelim neden hep belirli bir gruba karşı ayrımcı sonuçlar veriyor?",
                'answer': "Eğitim verin yanlı (biased) olabilir. Eğer veride temsil edilmeyen gruplar varsa model bunu öğrenir. Verini dengelemen (balancing) şart.",
                'views': 1345,
            },
        ]

        # ===== BİBLİYOMETRİK ANALİZLER =====
        biblio_topics = [
            {
                'subject': "Bibliyometrik görselleştirme için hangi araç daha iyi?",
                'starter': 'Literatur_Tarama',
                'message': "VOSviewer vs Biblioshiny - Görsel olarak hangisi makalelerde daha çok kabul görüyor?",
                'answer': "VOSviewer ağ haritaları için standarttır. Biblioshiny (R-Bibliometrix) ise daha detaylı istatistiksel tablolar sunar. İkisini birden kullanmak en iyisidir.",
                'views': 1123,
            },
            {
                'subject': "Hangi veri tabanı bibliyometride daha kapsayıcı?",
                'starter': 'Arastirmaci_X',
                'message': "Scopus mu Web of Science mı? İki veriyi birleştirebilir miyim?",
                'answer': "Scopus genellikle daha fazla dergi içerir ama WoS daha prestijli kabul edilir. İkisini birleştirmek zordur (mükerrer kayıtlar yüzünden), genellikle tek bir tanesi seçilir.",
                'views': 987,
            },
            {
                'subject': "Ortak atıf ile ortak yazarlık arasındaki fark nedir?",
                'starter': 'Bilim_Haritaci',
                'message': "Hangi analiz entelektüel yapıyı gösterir?",
                'answer': "Co-citation analizi, iki makalenin aynı anda üçüncü bir makale tarafından kaynak gösterilmesidir. Bu, o alanın teorik temellerini ortaya çıkarır.",
                'views': 756,
            },
            {
                'subject': "Bir yazarın etkisini ölçmek için sadece H-indeksi yeterli mi?",
                'starter': 'AkademikKariyer',
                'message': "i10 indeksi ne işe yarar?",
                'answer': "H-indeksi nicelik ve niteliği birleştirir ama yeni yazarlar için dezavantajlıdır. i10 indeksi ise Google Scholar'ın kullandığı, en az 10 atıf almış makale sayısını gösteren bir metriktir.",
                'views': 645,
            },
            {
                'subject': "Sadece bibliyometrik analiz ile Q1 dergide yayın yapılır mı?",
                'starter': 'YayinHedefi',
                'message': "Sadece grafik koymak yeterli mi?",
                'answer': 'Hayır. Grafiklerin ötesine geçip alanın "gelecek projeksiyonunu" yapmalı, boşlukları (research gaps) belirlemeli ve derinlemesine bir tartışma sunmalısın.',
                'views': 1234,
            },
        ]

        # ===== SPSS & AMOS =====
        spss_topics = [
            {
                'subject': "SPSS'de normallik testi nasıl yapılır?",
                'starter': 'Akademik_Kus',
                'message': "Verimin normal dağılıp dağılmadığını kontrol etmem gerekiyor.",
                'answer': "Analyze > Descriptive Statistics > Explore yolunu izle. Shapiro-Wilk (n<50) veya Kolmogorov-Smirnov (n>50) testlerini kullan. p>0.05 ise normal dağılım var demektir.",
                'views': 2345,
            },
            {
                'subject': "AMOS'ta model uyum indeksleri nasıl yorumlanır?",
                'starter': 'Psikoloji_Tez',
                'message': "CFI, GFI, RMSEA değerleri ne olmalı?",
                'answer': "CFI ve GFI > 0.90 (ideal >0.95), RMSEA < 0.08 (ideal <0.05) olmalıdır. Chi-square/df oranı da 3'ün altında olmalı.",
                'views': 1890,
            },
            {
                'subject': "Cronbach Alpha değeri düşük çıkıyor",
                'starter': 'Sosyal_Veri',
                'message': "Ölçeğimin güvenirliği 0.60 çıktı, ne yapmalıyım?",
                'answer': "Item-Total Correlation değerlerine bak. 0.30'un altındaki maddeleri çıkarmayı düşün. Ayrıca 'Alpha if Item Deleted' sütununa bakarak hangi maddenin çıkarılmasının alpha'yı artıracağını gör.",
                'views': 1567,
            },
        ]

        # ===== PYTHON & VERİ BİLİMİ =====
        python_topics = [
            {
                'subject': "Pandas ile büyük CSV dosyası nasıl okunur?",
                'starter': 'VeriBilimci_A',
                'message': "5GB'lık dosyayı açmaya çalışınca RAM dolup taşıyor.",
                'answer': "`pd.read_csv('dosya.csv', chunksize=100000)` kullanarak parça parça oku. Veya `dtype` parametresiyle veri tiplerini optimize et. Dask kütüphanesi de alternatif.",
                'views': 1678,
            },
            {
                'subject': "Scikit-learn ile Cross Validation nasıl yapılır?",
                'starter': 'ModelEgitmeni',
                'message': "Modelimin gerçek performansını nasıl ölçerim?",
                'answer': "`from sklearn.model_selection import cross_val_score` kullan. `cross_val_score(model, X, y, cv=5)` ile 5-katlı çapraz doğrulama yapabilirsin.",
                'views': 1234,
            },
            {
                'subject': "Matplotlib vs Seaborn hangisi daha iyi?",
                'starter': 'VeriGorselci',
                'message': "Akademik makale için hangi kütüphaneyi kullanmalıyım?",
                'answer': "Seaborn, Matplotlib üzerine kurulu ve daha estetik grafikler üretiyor. Ancak tam kontrol istiyorsan Matplotlib kullan. İkisini birlikte kullanmak en iyisi.",
                'views': 987,
            },
        ]

        # ===== R STUDIO =====
        r_topics = [
            {
                'subject': "R'da ggplot2 ile profesyonel grafik nasıl yapılır?",
                'starter': 'Arastirmaci_X',
                'message': "Makalem için yayın kalitesinde grafik lazım.",
                'answer': "`theme_minimal()` veya `theme_classic()` kullan. `ggsave('grafik.png', dpi=300, width=8, height=6)` ile yüksek çözünürlüklü kaydet.",
                'views': 1345,
            },
            {
                'subject': "R'da tidyverse paketi ne işe yarar?",
                'starter': 'VeriBilimci_A',
                'message': "Herkes tidyverse kullanın diyor ama neden?",
                'answer': "tidyverse; dplyr, ggplot2, tidyr gibi paketleri içeren bir koleksiyon. Veri manipülasyonu için pipe operatörü (%>%) ile okunabilir kod yazmanı sağlar.",
                'views': 1123,
            },
        ]

        # ===== 2050 VİZYONU: GELECEĞİN TEKNOLOJİLERİ =====
        future_topics = [
            {
                'subject': "Kuantum Bilgisayarlarda Veri Analizi Nasıl Değişecek?",
                'starter': 'Donanim_Meraklisi',
                'message': "Klasik bitler yerine Qubit kullanıldığında SPSS veya Python kütüphaneleri tarih mi olacak?",
                'answer': "Kuantum, olasılıksal hesaplamayı değiştirecek. Şimdiden IBM Qiskit veya Google Cirq öğrenmeye başlamak, 2050 vizyonu için kritik.",
                'views': 5050,
            },
            {
                'subject': "Neuralink ve Beyin-Bilgisayar Arayüzleri (BCI) Verisi",
                'starter': 'SaglikIst',
                'message': "İnsan beyninden doğrudan alınan verilerin analizi için hangi etik kurallar geçerli olacak?",
                'answer': "Bu, 'Nöro-Etik' alanına giriyor. Veri mahremiyeti artık sadece dijital izler değil, düşünce mahremiyetini de kapsayacak.",
                'views': 4200,
            },
        ]

        # ===== ANALİZ PAZARI & FREELANCE (KAZANÇ ODAKLI) =====
        freelance_topics = [
            {
                'subject': "[İLAN] Tıp Fakültesi Tez Analizi İçin SPSS Uzmanı Aranıyor",
                'starter': 'Klinik_Aras',
                'message': "Elimde 200 hastalık bir veri seti var. Ki-Kare ve Lojistik Regresyon analizleri yapılacak. Raporlama dahil tekliflerinizi bekliyorum. Bütçe: 5000 TL.",
                'answer': "Merhaba, Tıp istatistiği konusunda 5 yıllık deneyimim var. Veri setinizi inceleyip 3 gün içinde teslim edebilirim. Özelden referanslarımı iletiyorum.",
                'views': 2100,
            },
            {
                'subject': "[HİZMET] Power BI ile Kurumsal Dashboard Tasarımı",
                'starter': 'StratejiAnalisti',
                'message': "Satış, Stok ve Finans verileriniz için otomatik güncellenen, mobil uyumlu Power BI raporları tasarlıyorum. Örnek çalışmalarım profilimdedir.",
                'answer': "Merhaba, şirketimiz için bir demo çalışma talep edebilir miyiz? İletişime geçildi.",
                'views': 1850,
            },
            {
                'subject': "[PROJE] Python ile Web Scraping ve Duygu Analizi",
                'starter': 'Iletisimci',
                'message': "Twitter'dan belirli bir hashtag altındaki verileri çekip NLP ile duygu analizi yapacak bir script'e ihtiyacımız var.",
                'answer': "Bu proje için Selenium ve BERT modelini kullanarak %90 doğrulukla çalışan bir yapı kurabilirim. Detayları konuşalım.",
                'views': 1540,
            },
            {
                'subject': "[DANIŞMANLIK] Akademik Makale Yazım ve Düzenleme Desteği",
                'starter': 'AkademikEtik',
                'message': "Q1 ve Q2 dergiler için istatistiksel raporlama, tablo düzeni ve metodoloji yazımı konusunda danışmanlık veriyorum.",
                'answer': "Hocam merhaba, çalışmamın metodoloji kısmı için revizyon aldım. Destek olabilir misiniz?",
                'views': 3200,
            },
        ]

        # 4. KATEGORİ YAPISI OLUŞTUR
        structure = {
            "Yazılımlar": [
                ("SPSS & AMOS", "bi-bar-chart-fill", "İstatistiksel analiz ve yapısal eşitlik modellemesi.", spss_topics),
                ("Python & Veri Bilimi", "bi-filetype-py", "Pandas, NumPy, Scikit-learn ile veri analizi.", python_topics),
                ("R Studio", "bi-r-circle", "Akademik R paketleri ve ggplot2 görselleştirme.", r_topics),
                ("Excel & Power Query", "bi-file-earmark-spreadsheet", "İleri Excel, VBA ve iş zekası.", excel_topics),
                ("Stata & MATLAB", "bi-graph-up-arrow", "Ekonometri ve mühendislik analizleri.", stata_topics),
                ("NVivo & MAXQDA", "bi-chat-quote-fill", "Nitel veri kodlama ve tematik analiz.", nitel_topics),
            ],
            "Yöntemler": [
                ("Regresyon & İlişki Analizi", "bi-diagram-3", "Lojistik regresyon, moderasyon ve aracılık.", regresyon_topics),
                ("Bibliyometrik Analizler", "bi-book", "VOSviewer, Biblioshiny ve atıf analizleri.", biblio_topics),
            ],
            "Akademi": [
                ("Yapay Zeka & Deep Learning", "bi-robot", "Machine Learning, NLP ve AI etiği.", ai_topics),
            ],
            "Vizyon 2050": [
                ("Geleceğin Teknolojileri", "bi-cpu-fill", "Kuantum, BCI ve Uzay Veri Madenciliği.", future_topics),
            ],
            "Analiz Pazarı (Beta)": [
                ("Freelance Projeler", "bi-briefcase-fill", "Analiz projeleri, iş ilanları ve uzman teklifleri.", freelance_topics),
            ],
        }

        # 5. VERİLERİ OLUŞTUR
        user_dict = {u.username: u for u in users}

        for sec_title, categories in structure.items():
            section = Section.objects.create(title=sec_title)

            for cat_title, icon, desc, topics_data in categories:
                slug_val = self.turkish_slugify(cat_title)

                category = Category.objects.create(
                    section=section,
                    title=cat_title,
                    description=desc,
                    icon_class=icon,
                    slug=slug_val
                )

                for topic_data in topics_data:
                    starter_username = topic_data['starter']
                    starter = user_dict.get(starter_username, random.choice(users))

                    topic = Topic.objects.create(
                        category=category,
                        subject=topic_data['subject'],
                        starter=starter,
                        views=topic_data.get('views', random.randint(100, 500))
                    )

                    # İlk mesaj (soru)
                    Post.objects.create(
                        topic=topic,
                        created_by=starter,
                        message=f"Merhaba,\n\n{topic_data['message']}\n\nTeşekkürler."
                    )

                    # Cevap (AnalizBot veya rastgele uzman)
                    responder = user_dict.get('AnalizBot', random.choice(users))
                    Post.objects.create(
                        topic=topic,
                        created_by=responder,
                        message=f"Merhaba,\n\n{topic_data['answer']}\n\nBaşarılar dilerim!",
                        is_best_answer=True
                    )

        # 6. FREELANCE MARKET VERİLERİ (VİTRİN İLANLARI İÇİN)
        self.stdout.write('Freelance Market verileri oluşturuluyor...')
        
        # Kategorileri al
        cat_spss = Category.objects.filter(title__icontains="SPSS").first()
        cat_python = Category.objects.filter(title__icontains="Python").first()
        cat_excel = Category.objects.filter(title__icontains="Excel").first()
        
        market_jobs = [
            {
                'title': 'Tıp Fakültesi Tez Analizi İçin SPSS Uzmanı Aranıyor',
                'desc': 'Elimde 200 hastalık bir veri seti var. Ki-Kare ve Lojistik Regresyon analizleri yapılacak. Raporlama dahil tekliflerinizi bekliyorum.',
                'budget_min': 3000,
                'budget_max': 5000,
                'category': cat_spss,
                'owner': 'Klinik_Aras',
                'is_featured': True
            },
            {
                'title': 'Python ile Web Scraping ve Duygu Analizi',
                'desc': 'Twitter\'dan belirli bir hashtag altındaki verileri çekip NLP ile duygu analizi yapacak bir script\'e ihtiyacımız var.',
                'budget_min': 4000,
                'budget_max': 7000,
                'category': cat_python,
                'owner': 'Iletisimci',
                'is_featured': True
            },
            {
                'title': 'Kurumsal Power BI Dashboard Tasarımı',
                'desc': 'Satış ve stok verilerimiz için yönetim paneli tasarlanacak.',
                'budget_min': 10000,
                'budget_max': 15000,
                'category': cat_excel,
                'owner': 'StratejiAnalisti',
                'is_featured': False
            }
        ]
        
        for job_data in market_jobs:
            owner_name = job_data['owner']
            owner = user_dict.get(owner_name, users[0])
            category = job_data['category']
            
            if not category:
                category = Category.objects.first()
                
            job = FreelanceJob.objects.create(
                owner=owner,
                title=job_data['title'],
                description=job_data['desc'],
                budget_min=job_data['budget_min'],
                budget_max=job_data['budget_max'],
                category=category,
                status='open',
                is_featured=job_data['is_featured'],
                expires_at=timezone.now() + timedelta(days=30)
            )
            
            if job.is_featured:
                job.featured_until = timezone.now() + timedelta(days=7)
                job.save()

        # İstatistikleri göster
        total_topics = Topic.objects.count()
        total_posts = Post.objects.count()
        total_users = User.objects.count()
        total_jobs = FreelanceJob.objects.count()

        self.stdout.write(self.style.SUCCESS(f'''
╔══════════════════════════════════════════════╗
║     🚀 ANALIZUS VERİTABANI HAZIR! 🚀         ║
╠══════════════════════════════════════════════╣
║  📊 Toplam Konu: {total_topics:<27} ║
║  💬 Toplam Gönderi: {total_posts:<24} ║
║  👥 Toplam Üye: {total_users:<28} ║
║  💼 Toplam İlan: {total_jobs:<27} ║
╚══════════════════════════════════════════════╝
        '''))
