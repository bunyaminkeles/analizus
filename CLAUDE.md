# Analizus.com Geliştirme Görevi — Claude Code Prompt

## 🎯 Proje Bağlamı

Sen, **Analizus.com** platformunun geliştirilmesinde bana yardımcı olacaksın. Platform hakkında bilmen gerekenler:

**Analizus nedir?**
Türkiye'de akademik araştırmacılara yönelik bir platform. Şu bileşenlerden oluşuyor:
- **Forum**: Akademik soru-cevap topluluğu (`forum/` app, `/` URL'i)
- **Hizmetler Pazarı**: Araştırmacı-uzman eşleştirme (FreelanceJob, JobProposal modelleri)
- **Online Analiz Araçları**: Cronbach Alpha, Normallik Testi, Betimleyici İstatistik (`istatistik/` app, `/istatistik/`)
- **Akademik Tarama Araçları**: YÖK Tez (`yoktez/`), OpenAlex (`openalex/`), TR Dizin (`trdizin/`), OAI-PMH üniversite tezleri (`oaipmh/`)
- **Bibliometrik Analiz**: BibTeX/WoS/Scopus/OpenAlex format desteği (`bibliometrics/`)
- **Tez & Makale Analizi**: AI destekli (`tezanaliz/`, `makaleanaliz/`)
- **AI Asistan**: İstatistik danışmanlığı (forum app içinde)
- **Hangi Test?**: Uygun istatistik testi seçme aracı (forum app içinde)
- **Çalışma Odaları**: Topluluk çalışma alanları (StudyRoom modeli)
- **İstatistik Arena**: Quiz tabanlı puan kazanma sistemi (QuizQuestion, QuizScore modelleri)
- **Blog**: Akademik içerik (BlogPost, BlogCategory modelleri)

**Hedef kitle**: Tez yazan öğrenciler, makale hazırlayan akademisyenler, istatistik analizine ihtiyaç duyan araştırmacılar, bu alanda hizmet veren uzmanlar.

---

## 🏗️ Teknik Stack (Kesinleşmiş)

### Backend
- **Framework**: Django 4.2+ (ASGI — Daphne ile çalışıyor)
- **Python**: 3.10.12
- **Gerçek zamanlı**: Django Channels + InMemoryChannelLayer (dev) / Redis (`REDIS_URL` env var ile prod)
- **Job kuyruğu**: `analizdestek/job_queue.py` (custom ThreadPoolExecutor), `JOB_MAX_WORKERS=5`

### Veritabanı
- **Üretim**: **Neon PostgreSQL** (serverless, havuzlu bağlantı)
  - `conn_max_age=0` — her istek yeni bağlantı açar (serverless zorunluluğu)
  - Env var: `DATABASE_URL=postgresql://...@...neon.tech/neondb?sslmode=require`
- **Lokal geliştirme**: SQLite (DATABASE_URL boşsa otomatik)

### Sunucu / Hosting
- **VPS**: Hetzner (IP: 89.167.5.224)
- **Web sunucusu**: Nginx (reverse proxy) + Gunicorn `>=22.0,<24.0`
- **Statik dosyalar**: WhiteNoise (Django içinden serve edilir)

### Depolama
- **Dosya yükleme**: AWS S3 bucket `analizus-files` (bölge: `eu-north-1`)
  - Production'da `DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'`
  - Lokalde `media/` klasörü kullanılır
  - Env vars: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_REGION_NAME`
  - S3 utils: `forum/s3_utils.py`

### E-posta
- **Backend**: Django SMTP (`django.core.mail.backends.smtp.EmailBackend`)
- **Sunucu**: `mail.analizus.com` (hosting.com.tr promail)
- **Port**: 587 (TLS) veya 465 (SSL) — settings.py otomatik algılar
- **Env vars** (settings.py `SMTP_*` prefix kullanıyor!):
  - `SMTP_HOST` → `EMAIL_HOST`
  - `SMTP_PORT` → `EMAIL_PORT`
  - `SMTP_USER` → `EMAIL_HOST_USER`
  - `SMTP_PASS` → `EMAIL_HOST_PASSWORD`
- **Gönderici**: `DEFAULT_FROM_EMAIL=Analizus <info@analizus.com>`

### Ödeme
- iyzico altyapısı kodda mevcut ama **kullanılmayacak**
- Ödeme sistemi henüz belirsiz — sonradan karar verilecek

### AI / LLM
- **Groq** (aktif, `GROQ_API_KEY` var): hızlı inference, Llama modelleri
- **OpenAI** (`OPENAI_API_KEY`): GPT modelleri (key girilmemiş olabilir)
- **Gemini** (`GEMINI_API_KEY`): Google modelleri (key girilmemiş olabilir)

### Admin Paneli
- **Django Unfold** tema, özel sidebar navigasyonu
- Dashboard: `forum/dashboard.py` → `dashboard_callback`
- URL: `/admin/`

### Diğer
- **Feature flags**: `SiteSettings` modeli (forum/models.py:1077) → `forum.context_processors.feature_flags`
- **Rate limiting**: `django-ratelimit`, hata view: `forum.views.ratelimit_error`
- **Session**: Database-backed, 2 saat ömür
- **i18n**: Türkçe (`tr`) varsayılan, `locale/` klasöründe çeviri dosyaları

### Önemli Dosya Yolları
```
analizdestek/settings.py   — Ana konfigürasyon
analizdestek/urls.py       — Ana URL routing
analizdestek/job_queue.py  — Paralel iş kuyruğu
forum/models.py            — Büyük model dosyası (Profile, Blog, Forum, Freelance, Quiz...)
forum/context_processors.py — Profil, feature flags, GA
forum/s3_utils.py          — S3 upload/delete yardımcıları
istatistik/services/       — cronbach.py, normallik.py, betimsel.py, job_runner.py
bibliometrics/services/    — parser.py, analyzer.py, pdf_builder.py, job_runner.py
```

---

## 📋 Çalışma Prensipleri

### 1. Önce Anla, Sonra Kodla
- Her yeni göreve başlamadan önce ilgili dosyaları oku ve mevcut yapıyı anla
- **Tahmin yürütme; dosyaya bak.** "Muhtemelen şöyledir" deme, kodu oku.
- Veritabanı değişikliklerinde Neon bağlantısını göz önünde bulundur: `conn_max_age=0`

### 2. Küçük Adımlarla İlerle
- Büyük değişiklikleri parçalara böl
- Her değişiklik sonrası durup onayımı bekle
- Bir seferde tek bir todo maddesi üzerinde çalış, birden fazla iş birleştirme

### 3. Mevcut Kod Tarzına Sadık Kal
- Dosyalarda kullanılan naming convention, import stili, indentation'ı koru
- Mevcut renk paleti: Unfold primary = indigo (#6366f1 ailesi), dark theme tercihleri var
- Yeni kütüphane öneriyorsan önce neden gerekli olduğunu açıkla, onay al

### 4. Türkçe Dil Tutarlılığı
- Kullanıcıya görünen tüm metinler Türkçe ve akademik dile uygun
- Hata mesajları kullanıcı dostu: "500 Internal Server Error" değil, açıklayıcı Türkçe

### 5. Güvenlik
- Kullanıcı dosya yüklemelerinde boyut sınırı (`MAX_UPLOAD_SIZE = 5MB`), format kontrolü
- SQL injection, XSS, CSRF korumalarını göz ardı etme
- `.env` içindeki secret'ları kod içine hardcode etme
- iyzico entegrasyonunda sandbox/production ayrımını koru

### 6. Veritabanı
- Migration dosyaları üzerinden git, production DB'ye direkt dokunma
- Neon serverless nedeniyle `conn_max_age=0` — long-running transaction'lardan kaçın
- `select_related` / `prefetch_related` kullan, N+1 sorgu yaratma

### 7. Dokümantasyon
- Karmaşık algoritmalara (istatistik hesaplamaları) kısa satır içi açıklama ekle
- Her yeni analiz fonksiyonuna bir satır docstring yeterli

---

## ✅ GÖREV LİSTESİ — Kolaydan Zora (Öncelik Sırası)

Görevler kolaylık derecesine göre sıralanmıştır. Fiyatlandırma/para modeli işleri en sona alınmıştır. **Sırayı takip et**, "şu göreve geç" demedikçe atlama.

---

### 🟢 KOLAY (Şablon / İçerik Değişikliği)

#### Görev 1: Sosyal Kanıt İyileştirmeleri
**Zorluk**: Çok kolay — sadece template değişikliği
- Küçük kullanıcı/işlem rakamlarını gizle veya "Beta" etiketi kullan
- Başarı hikayeleri (SuccessStory modeli var) öne çıkar
- Ana sayfada "Bu hafta Analizus'ta" haftalık özet kutusu ekle
- Kullanıcı testimonial'leri için alan aç

---

#### Görev 2: Hero Alanında Net Değer Önerisi
**Zorluk**: Kolay — template + CSS
- Ana sayfa hero bölümünde tek cümlelik güçlü değer önerisi
- Örnek: *"Tezin için doğru istatistik testini seç, verinle anında hesapla, gerektiğinde uzman bul."*
- Hero altına 3 hızlı eylem butonu + 1 satır açıklama (Analiz Yap / Uzman Bul / Foruma Katıl)
- Mobil responsive kontrolü

**Başarı kriteri**: İlk giren biri 5 saniyede "burada analiz yapabilirim, uzman bulabilirim" anlıyor.

---

#### Görev 3: Analiz Araçlarına Akademik Referans
**Zorluk**: Kolay — template eklentisi, statik içerik
- `istatistik/templates/` altındaki analiz sonuç şablonlarına "Metodoloji" bölümü ekle
- Cronbach → Cronbach (1951), Shapiro-Wilk → Shapiro & Wilk (1965) referansları
- Her aracın varsayımlarını ve formülünü kısaca açıkla
- "Bu aracı nasıl raporlamalıyım?" başlığı altında APA örnek cümle

---

#### Görev 4: APA Formatında Otomatik Rapor Şablonu
**Zorluk**: Kolay-Orta — JavaScript + template
- Her analiz sonucuna "Tezinde Nasıl Yazarsın?" kutusu ekle
- Sonuç değerlerini kullanarak APA cümlesi otomatik üret (JS ile)
- Örnek: *"α = .873 ... yüksek düzeyde güvenilir (Nunnally, 1978)"*
- Kopyala butonu (clipboard API)
- Yorumlama eşikleri: α < .50 kabul edilmez → > .90 çok yüksek

---

#### Görev 5: "Hangi Test?" → Analiz Araçları Entegrasyonu
**Zorluk**: Kolay — view + template tweak
- "Hangi Test?" sonuç sayfasında önerilen test için direkt aksiyon butonu
- Platformda olan testler: "→ Buradan Yap" butonu
- Olmayan testler: "Yakında Geliyor" etiketi
- İlgili blog/forum konuları da öner

---

#### Görev 6: "Neden Biz?" Sayfası
**Zorluk**: Kolay — yeni statik sayfa
- `/neden-biz/` URL'inde yeni sayfa
- Rakip karşılaştırma tablosu (SPSS, SmartPLS vb.)
- Analizus'un benzersiz özellikleri listesi
- Kullanıcı hikayeleri

---

### 🟡 ORTA (Yeni View + Model Değişikliği)

#### Görev 7: Teklif Fiyat Gizliliği
**Zorluk**: Orta — permission kontrolü
- İlan detay sayfasında teklif tutarını sadece ilan sahibi ve teklif veren görsün
- Diğerlerine: "X uzman teklif verdi" (sadece sayı)
- JobProposal modelinde ve view'da permission kontrolü
- Admin paneline "Teklif gizliliği" SiteSettings alanı

---

#### Görev 8: Yeni Kullanıcı Onboarding Akışı
**Zorluk**: Orta — yeni model alanı + form
- Profile modeline `segment` alanı ekle (migration gerekli)
- Kayıt sonrası 3 adımlı anket:
  - Adım 1: "Seni en iyi hangisi tanımlıyor?" (Öğrenci/Akademisyen/Uzman/Meraklı)
  - Adım 2: "Burada ne yapacaksın?" (çoklu seçim)
  - Adım 3: "Hangi araçları kullanıyorsun?" (SPSS, R, Python vb.)
- Cevaplara göre kişiselleştirilmiş dashboard
- "Atla" butonu zorunlu

---

#### Görev 9: Analiz Araçlarında Akıllı Hata Yönetimi
**Zorluk**: Orta — yeni utils modülü
- `istatistik/services/data_validator.py` yaz
- ID sütunlarını otomatik tespit (isim + monoton artış kontrolü)
- Sayısal olmayan sütunları uyar, boş değerleri say
- Likert aralığı dışı değerleri uyar (Cronbach için)
- UI'da renkli uyarı kutuları (sarı/kırmızı/mavi)
- "Yine de devam et" seçeneği

**Başarı kriteri**: Katılimci_No sütunu dahil edilince uyarı verilmesi.

---

#### Görev 10: Blog İçerik Altyapısı İyileştirmeleri
**Zorluk**: Orta — mevcut BlogPost modeli var
- Editörde kod bloğu, formül, tablo desteği
- SEO meta tag yönetimi (BlogPost modeline meta_description, og_image)
- İlgili içerik önerileri (aynı kategori)
- Yeni kategoriler: "İstatistik 101", "SPSS Rehberleri", "R ile Analiz", "Python ile Veri Bilimi", "Tez Süreci"
- İlk 10 yazı başlıkları için içerik üret (admin panelden eklenebilir hale getir)

---

#### Görev 11: Admin Analytics Dashboard
**Zorluk**: Orta — mevcut Unfold dashboard genişletme
- `forum/dashboard.py` içine metrik kartları ekle (mevcut dashboard_callback var)
- DAU/WAU/MAU, yeni kayıt trendi, analiz araçları kullanım istatistikleri
- Pazar yeri: açılan ilan, tamamlanan iş, ortalama teklif
- Forum: yeni konu, gönderi, aktif kullanıcı
- Kullanıcı segmentasyonu (onboarding sonrası)
- CSV indirme seçeneği

---

#### Görev 12: Gamification Genişletmesi
**Zorluk**: Orta — mevcut Badge/QuizScore sistemi var
- Günlük giriş streak sistemi (Profile modeline alan)
- Analiz yapınca puan kazanma (istatistik job tamamlanınca signal)
- Haftalık liderboard
- Yeni rozetler: "İlk Analiz", "10 Analiz Tamamlayan", "Forum Kahramanı"

---

#### Görev 13: Uzman Profil Sayfaları
**Zorluk**: Orta — mevcut Profile var, genişletme
- Uzmanlık alanları ve sertifikalar (zaten Skill modeli var)
- Tamamlanan proje portföyü (anonim, örnek çıktı)
- Puan dağılımı detayları
- "Uzmanla İletişime Geç" butonu (PrivateMessage sistemi var)

---

#### Görev 14: Mobil Optimizasyon
**Zorluk**: Orta — CSS/template tarama
- Sidebar panelleri mobilde collapse
- Dosya yükleme akışı mobilde test
- Touch-friendly buton boyutları (min 44px)
- Analiz sonuç sayfası mobil scroll iyileştirme

---

### 🔴 ZOR (Yeni Servis / Karmaşık Feature)

#### Görev 15: API Dokümantasyonu
**Zorluk**: Zor — Swagger/drf-spectacular entegrasyonu
- `/api/docs/` URL'inde OpenAPI dokümanı
- Her endpoint için request/response örneği, auth, rate limit bilgisi
- Public API'leri iç API'lerden ayır

---

#### Görev 16: Korelasyon Matrisi Aracı
**Zorluk**: Zor — yeni analiz servisi
- `istatistik/services/korelasyon.py` yaz
- Pearson/Spearman/Kendall seçeneği
- P-değerleri ile tablo + heatmap görselleştirme
- PDF rapor (mevcut pdf sistemiyle entegre)
- `istatistik/urls.py`'ye ekle, job_queue ile çalıştır

---

#### Görev 17: Örneklem Büyüklüğü Hesaplayıcı
**Zorluk**: Zor — istatistik hesaplama + UI
- Etki büyüklüğü, alfa, güç parametreleri
- Test tipine göre hesaplama (t-test, ANOVA, korelasyon)
- scipy.stats kullanılabilir
- G*Power alternatifi olarak konumlandır

---

#### Görev 18: t-Testi ve ANOVA Aracı
**Zorluk**: Zor — yeni analiz servisi
- `istatistik/services/ttesti.py`, `anova.py` yaz
- Bağımsız/bağımlı örneklem t-testi
- Tek yönlü ANOVA + Tukey/Bonferroni post-hoc
- Dosya yükle → grup belirle → sonuç al akışı (mevcut Cronbach akışına benzer)

---

#### Görev 19: İstatistik Arena İyileştirmesi
**Zorluk**: Zor — quiz sistemi revizyonu
- Mevcut QuizQuestion modelini genişlet
- Genel programlama soruları yerine analiz senaryolu sorular
- "Bu çıktıda α değeri nedir?" tipi sorular
- Görsel destekli sorular (grafik okuma)

---

#### Görev 20: Çalışma Odaları + Analiz Entegrasyonu
**Zorluk**: Çok zor — WebSocket + gerçek zamanlı işbirliği
- StudyRoom içinde ortak veri seti yükleme
- Gerçek zamanlı işbirliği (Django Channels WebSocket, Redis gerekli)
- Sohbet + not paylaşımı + analiz sonuçları paylaşımı
- Prod ortamında `REDIS_URL` env var gerekli

---

#### Görev 21: Açık Kaynak Politikası
**Zorluk**: Zor — organizasyonel + teknik
- GitHub organizasyonu kur
- Analiz motorlarını açık kaynak yap
- Kullanılan kütüphaneler transparan liste

---

### ⚪ EN SON (Fiyatlandırma / Para Modeli)

#### Görev 22: Para Modeli Sayfası ve Görünürlüğü
**Zorluk**: Orta teknik, ancak iş kararı gerektiriyor — en son yapılacak
**Not**: Premium üyelik fiyatı, komisyon oranları, plan sınırları benim onayımla belirlenecek.

- `/fiyatlandirma/` sayfası oluştur
- Ücretsiz / Premium / Uzman planları (fiyatlar TBD)
- Hizmetler Pazarı komisyonu (oran TBD)
- Header menüsüne "Fiyatlandırma" ekle
- iyzico ile ödeme entegrasyonu (altyapı zaten var: `IYZICO_API_KEY`)
- Premium özellikleri belirle: sınırsız analiz, öncelikli destek, özel rozet, detaylı PDF rapor

---

## 🤝 Benimle Çalışma Şeklin

1. **Her görev için önce plan sun**: "Görev X'i şu dosyalarda şu değişikliklerle yapacağım. Onaylıyor musun?"
2. **Migration gerekiyorsa mutlaka söyle**: Neon prod DB etkilenir
3. **Belirsizlik olunca sor**: Fiyat, oran, limit gibi iş kararlarını varsayma
4. **Bozulan bir şey varsa anında söyle**: Commit'ten önce haber ver
5. **Tamamlanan görevi özet geç**: Ne yaptın, ne test edilmeli

---

## 📌 Önemli Notlar

- Commit mesajları Türkçe: "feat: Hero alanına değer önerisi eklendi"
- Yeni branch için bana sor (mevcut: `dev` branch)
- Production veritabanına (Neon) direkt dokunma, migration dosyaları üzerinden git
- `.env` değişkenlerini kod içine hardcode etme
- Email env varları `SMTP_*` prefix ile (settings.py bunu bekliyor)
- Büyük değişiklikler öncesi `git status` kontrol et
- Şüpheye düşersen dur ve sor

**Her zaman hatırla: Analizus'u kullanan akademisyenler ve öğrenciler araçlarımızın sonucuna güvenmek zorunda. Hızlı değil, doğru.**
