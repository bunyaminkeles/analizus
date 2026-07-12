# ANALIZUS.COM — TAM SİSTEM DOKÜMANTASYONU

> Bu dosyayı okuyan bir AI, projeye sıfırdan başlayabilmeli, doğru kod yazabilmeli ve hata yapmamalıdır.
> Tüm kural ve kısıtlara bu belgede yer verilmiştir.

---

## 1. PROJE AMAÇ VE VİZYON

**Platform tanımı:** Analizus; veri analizi, istatistiksel analizler ve yapay zeka modellemeleri için uzmanların ve talep sahiplerinin buluştuğu bir analiz platformudur. Hem akademik çevreye (tez/makale desteği) hem de kurumsal müşterilere (şirket verisi → insight, görselleştirme, ML) hizmet verir.

**Alan adı:** `analizus.com`
**Hedef kitle (iki segment):**
- **Akademik:** Tez yazan öğrenciler, makale hazırlayan akademisyenler, istatistik analizine ihtiyaç duyan araştırmacılar
- **Kurumsal:** Verilerinden insight elde etmek, görselleştirme/ML yaptırmak isteyen şirketler ve kurumlar
**Temel değer önerisi:** Doğru istatistik testini seç, verinle anında hesapla, gerektiğinde uzman bul — Türkçe, güvenilir, akademik ve kurumsal düzeyde.
**Tasarım felsefesi:** `ax-` prefix'li özel CSS sınıfları; Bootstrap sadece grid (`container`, `row`, `col-*`) için kullanılır. UI elementleri (`btn`, `card`, `badge`) tamamen özel CSS'ten gelir.
**Güven prensibi:** Kullanıcılar analiz sonuçlarına güvenmek zorunda — hızlı değil, doğru.

---

## 2. TEKNİK YIĞIN (TECH STACK)

| Katman | Teknoloji |
|---|---|
| Backend | Django 4.2+ (ASGI — Daphne) |
| Python | 3.11 (Dockerfile: `python:3.11-slim`) |
| Gerçek Zamanlı | Django Channels + Redis (prod) / InMemoryChannelLayer (dev) |
| Veritabanı | PostgreSQL 16 (prod) / SQLite (local) |
| ORM | Django ORM — `select_related`, `prefetch_related` zorunlu |
| Job Kuyruğu | `analizdestek/job_queue.py` (custom ThreadPoolExecutor, `JOB_MAX_WORKERS=5`) |
| Frontend CSS | Bootstrap 5 (sadece grid) + `ax-` prefix özel CSS sınıfları |
| Frontend JS | Vanilla JS — React/Vue/jQuery YASAK |
| İkonlar | Bootstrap Icons (CDN) veya inline SVG |
| Admin Paneli | `django-unfold` (indigo/koyu tema, özel navigasyon) |
| Kimlik Doğrulama | Django auth (özel login view, rate limited) |
| Formlar | `django-crispy-forms` + `crispy-bootstrap5` |
| E-posta | SMTP (`mail.analizus.com`, 587 TLS / 465 SSL) |
| Statik Dosyalar | WhiteNoise (CompressedStaticFilesStorage) — S3'e upload yok |
| Dosya Yükleme | AWS S3 `eu-north-1`, bucket: `analizus-files` |
| Hosting | Hetzner VPS (`89.167.5.224`) — Docker Compose (web, db, redis) + Nginx |
| SSL | Let's Encrypt (certbot) |
| AI/LLM | Groq (aktif), OpenAI, Gemini (env var ile) |
| Ödeme | iyzico **kullanım izni yok** — entegrasyon yapılmayacak; ödeme sistemi belirsiz |
| i18n | Türkçe (`tr`), `locale/` klasöründe çeviri dosyaları |
| Rate Limit | `django-ratelimit` — kayıt: 3/saat, login: 10/5dk, istatistik POST: 30/saat |
| Analytics | `analytics/` Django app — login'li kullanıcı sayfa ziyaretleri (PageView + PageViewSummary), admin grafik (Chart.js, in-place user filtresi), 5 günlük otomatik temizlik |

### Temel Paketler (requirements.txt)
```
Django, daphne, channels, channels-redis
dj-database-url, psycopg2-binary
whitenoise, boto3, django-storages
django-unfold, crispy-bootstrap5
Pillow, pandas, numpy, scipy, statsmodels
matplotlib, wordcloud, networkx, reportlab
bibtexparser, scikit-learn, nltk, zeyrek
openai, google-generativeai, groq
django-ratelimit, requests, httpx
beautifulsoup4, sickle
pytest, pytest-django, model-bakery
```

> **Not:** `statsmodels` regresyon analizleri için zorunludur. Yeni ortamda `pip install statsmodels` çalıştırılmalıdır.

---

## 3. SUNUCU MİMARİSİ (HETZNER — DOCKER)

```
İnternet
    ↓
Nginx (80/443) — SSL termination, reverse proxy
    ↓
Docker Container — Django / Gunicorn (/app)
    ↓
PostgreSQL (host) + Redis (host)
```

**VPS IP:** `89.167.5.224`
**Uygulama dizini (container içi):** `/app`
**Servis yönetimi:** `docker compose`
**Container adları:** `app-web-1`, `app-db-1`, `app-redis-1`
**Compose servis adları:** `web`, `db`, `redis`

> Not: `DATABASE_URL` içinde servis adı kullanılır (`db`) — `localhost` container içinden host'a ulaşamaz.

### Bağlantı
```bash
ssh root@89.167.5.224
```

> ⚠️ **KRİTİK:** Hetzner'de `docker-compose` komutu **YOKTUR**. Her zaman `docker compose` (boşluklu, plugin) kullan.
> Migration'ları **asla** host'ta çalıştırma — `db` hostname container dışında çözümlenmez.
> Doğru: `docker compose exec web python manage.py migrate`

### Uygulama Yönetimi
```bash
# Container durumu
docker compose ps

# Logları izle
docker compose logs -f web

# Site yanıt veriyor mu?
curl -o /dev/null -w '%{http_code}' http://localhost/
```

### Manuel Deploy (Kod Değişikliği Sonrası)
> Kod volume-mount ile container'a bağlı — `--build` GEREKMEZ, sadece restart yeterli.
```bash
git pull origin main
docker compose restart web && docker compose restart nginx
```

### Migration + Statik Dosya Varsa
```bash
git pull origin main
docker compose restart web && docker compose restart nginx
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
```

### requirements.txt Değişince (Yeni Paket)
> Tek `--build` gereken durum budur — yeni paket image'e eklenmeli.
```bash
git pull origin main
docker compose up -d --build web && docker compose restart nginx
```

### Servis Yönetimi
```bash
docker compose restart web

# Tüm servisler
docker compose ps
docker compose down && docker compose up -d
```

### .env Güncelleme
```bash
nano /app/.env
docker compose up -d web
```

---

## 4. ORTAM DEĞİŞKENLERİ

> **Kritik:** E-posta env var'ları `SMTP_*` prefix'li — Django standart `EMAIL_*` değil. `settings.py` içinde map'lenir.

```bash
# Veritabanı
DATABASE_URL=postgresql://bunyamin:SIFRE@db:5432/analizus

# Redis (Channels) — Docker servis adı kullanılmalı, localhost değil
REDIS_URL=redis://redis:6379

# Site
SITE_URL=https://www.analizus.com
DEBUG=False
SECRET_KEY=...
ALLOWED_HOSTS=analizus.com,www.analizus.com

# AWS S3
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_REGION_NAME=eu-north-1
AWS_STORAGE_BUCKET_NAME=analizus-files

# E-posta (SMTP_* prefix zorunlu!)
SMTP_HOST=mail.analizus.com
SMTP_PORT=587                            # 587=TLS, 465=SSL (otomatik algılanır)
SMTP_USER=info@analizus.com
SMTP_PASS=...
DEFAULT_FROM_EMAIL=Analizus <info@analizus.com>
ADMIN_NOTIFICATION_EMAIL=bkeles74@gmail.com

# AI / LLM
GROQ_API_KEY=...
OPENAI_API_KEY=...
GEMINI_API_KEY=...

# Cron güvenlik
CRON_SECRET_KEY=...

# WhatsApp float butonu (boşsa buton çıkmaz)
WHATSAPP_NUMBER=905XXXXXXXXX    # Uluslararası format, başında + yok

# OpenAlex polite pool
OPENALEX_EMAIL=info@analizus.com

# Semantic Scholar API (saniyede 1 istek; key'siz çalışır ama rate limit yüksek)
SEMANTIC_SCHOLAR_API_KEY=...
```

---

## 5. DEPLOY AKIŞI

### Branch Stratejisi
- `dev` → **Render** (push'ta otomatik deploy — staging/preview)
- `main` → **Hetzner** (manuel deploy — production)
- Tüm geliştirmeler `dev`'de yapılır; onay sonrası `dev → main` merge + Hetzner deploy

### Standart Deploy Akışı
```bash
# 1. Lokalde geliştir + commit (dev branch)
# 2. dev → main merge + push
git checkout main && git merge dev && git push origin main && git checkout dev

# 3. Hetzner'de uygula
ssh root@89.167.5.224
git pull && docker compose restart web && docker compose restart nginx
```

> ⚠️ **KRİTİK:** `docker compose restart web` sonrası **mutlaka** `docker compose restart nginx` da çalıştır.
> Nginx, web container'ın IP'sini başlangıçta çözümler. Container restart'ta yeni IP'yi almak için nginx de yeniden başlatılmalıdır.
> Aktif scraping/analiz job'u varken restart yapma — önce `docker compose exec web python manage.py shell -c "from yoktez.models import YokTezSearchJob; print(YokTezSearchJob.objects.filter(status='running').count())"` ile kontrol et.

---

## 6. PROJE DİZİN YAPISI

```
analizdestek/               # Django proje konfigürasyonu
├── settings.py             # Ana ayar dosyası
├── urls.py                 # Ana URL router
├── asgi.py                 # ASGI entry (Channels)
├── job_queue.py            # Paralel iş kuyruğu (ThreadPoolExecutor)
├── wsgi.py
forum/                      # Ana app — Forum, Market, Blog, Quiz, DM, AI...
├── models.py               # Büyük model dosyası (Profile, Topic, Post, FreelanceJob...)
├── views.py
├── admin.py
├── signals.py              # Bildirim sinyalleri (yeni topic/blog → IndexNow ping dahil)
├── email_utils.py          # Async admin+kullanıcı e-posta bildirimleri
├── indexnow.py             # Bing IndexNow ping (arka plan thread, key: 534e22a9f9e4d375119c5bc6d006aad0)
├── context_processors.py   # Profil, feature flags, GA
├── s3_utils.py             # S3 upload/delete yardımcıları
├── middleware.py           # HoneypotMiddleware, LastSeenMiddleware, EmailVerificationMiddleware
├── dashboard.py            # Unfold admin dashboard callback
├── forms.py                # Kayıt formu (honeypot + bot koruması)
├── consumers.py            # WebSocket consumer (Channels)
├── serializers.py          # DRF serializer'lar
├── ai_service.py           # AI asistan servisi
├── tasks.py                # Asenkron görevler
├── services/               # Özel servis modülleri
├── templates/forum/        # Tüm forum ve market şablonları
│   ├── market/             # job_list, job_detail, post_job, edit_job
│   ├── home.html, forum_*.html, profile_*.html, blog_*.html ...
istatistik/                 # İstatistik analiz araçları
├── models.py               # IstatistikJob modeli (tool choices, mark_completed vb.)
├── views.py                # Landing view'ları + job_status AJAX endpoint
├── urls.py                 # URL pattern'leri
├── migrations/
├── services/
│   ├── cronbach.py         # Cronbach Alpha (güvenirlik)
│   ├── normallik.py        # Normallik (Shapiro-Wilk, KS, Skewness/Kurtosis)
│   ├── betimsel.py         # Betimsel istatistik (min, max, mean, std, quartile...)
│   ├── korelasyon.py       # Korelasyon matrisi (Pearson/Spearman/Kendall)
│   ├── ttesti.py           # t-Testi (bağımsız/bağımlı/tek örneklem)
│   ├── anova.py            # Tek yönlü ANOVA + Tukey/Bonferroni post-hoc
│   ├── mann_whitney.py     # Mann-Whitney U testi (parametrik olmayan)
│   ├── kruskal_wallis.py   # Kruskal-Wallis H testi (parametrik olmayan)
│   ├── ki_kare.py          # Ki-Kare + Fisher's Exact Test
│   ├── lineer_regresyon.py # Çoklu Doğrusal Regresyon (OLS, statsmodels)
│   ├── lojistik_regresyon.py # Lojistik Regresyon (Logit, statsmodels)
│   ├── orneklem.py         # Örneklem büyüklüğü hesaplama
│   ├── data_validator.py   # Veri doğrulama
│   ├── karar_agaci.py      # Karar Ağacı (sklearn DecisionTreeClassifier, feature_importances_)
│   ├── svm.py              # Destek Vektör Makinesi (SVC + StandardScaler, permutation_importance)
│   ├── job_runner.py       # _execute_job, _parse_file, _upload_pdf
│   └── pdf_fonts.py        # DejaVuSans Türkçe font kaydı (reportlab)
├── templates/istatistik/   # Her araç için ayrı HTML şablonu
bibliometrics/
├── services/
│   ├── parser.py           # BibTeX/WoS/Scopus/OpenAlex format ayrıştırıcı
│   ├── analyzer.py         # 10 analiz türü
│   ├── pdf_builder.py
│   └── job_runner.py
tezanaliz/, makaleanaliz/   # AI destekli tez/makale analizi
openalex/                   # OpenAlex akademik yayın tarama
yoktez/                     # YÖK tez arama (HTTP tabanlı)
trdizin/                    # TR Dizin (feature flag ile gizli)
semanticscholar/            # Semantic Scholar + CrossRef yayın kazıma
oaipmh/                     # 19 üniversite arşivi OAI-PMH
transcript/                 # YouTube transcript indirici — `feature_transcript` (varsayılan KAPALI, bkz. §26 cloud IP kısıtı)
templates/                  # Genel şablonlar (base.html, auth...)
static/
├── css/
│   ├── base.css            # :root değişkenleri + ax- component'ler
│   └── ...                 # Modül bazlı CSS dosyaları
├── 534e22a9f9e4d375119c5bc6d006aad0.txt  # IndexNow key dosyası (Bing)
staticfiles/                # collectstatic çıktısı
media/                      # Yerel geliştirme dosya yükleme alanı
nginx/                      # Nginx konfigürasyonu
certbot/                    # Let's Encrypt SSL sertifikaları
locale/                     # Türkçe çeviriler
manage.py
requirements.txt
analizus.md                 # Bu dosya — tam sistem dokümantasyonu
CLAUDE.md                   # AI geliştirme kuralları ve görev listesi
```

---

## 7. URL MİMARİSİ

```python
/admin/             → Django admin (Unfold)
/accounts/          → Django auth (password reset)
/login/             → Özel login view (rate limited)
/logout/            → Django logout
/trdizin/           → trdizin.urls  (feature flag: feature_trdizin)
/semantic-scholar/  → semanticscholar.urls  (feature flag: feature_semanticscholar)
/openalex/          → openalex.urls
/oaipmh/            → oaipmh.urls
/yoktez/            → yoktez.urls
/bibliometrics/     → bibliometrics.urls
/tezanaliz/         → tezanaliz.urls  (namespace='tezanaliz')
/makaleanaliz/      → makaleanaliz.urls  (namespace='makaleanaliz')
/istatistik/        → istatistik.urls  (namespace='istatistik') — 18 aracın hepsinde GET → 301 kalıcı
                      /analiz/<slug>/'e yönlendirir (temmuz 2026); POST (analiz gönderimi/TOOL_URL
                      hedefi) değişmeden aynı view'a ulaşır — bkz. §26 "istatistik double-duty" dersi.
                      /istatistik/<slug>/status/<job_id>/ polling endpoint'leri KASITLI dokunulmadı,
                      tek çalışan implementasyon burada yaşıyor.
/analiz/            → istatistik.urls_analiz (unified konsol — /analiz/<slug>/)
                      /analiz/ → analiz_hub view (tüm araçları kategorili listeler; guest + login)
                      /analiz/hero-upload/ → hero_upload view (POST) — ana sayfa hero dropzone dosyasını
                      session veri setine kaydeder (save_session_dataset), araç sayfasına geçince otomatik yüklü gelir
/tarama/            → tarama_hub view (yoktez, openalex, trdizin, oaipmh kartları; guest + login)
/proje-talebi/      → proje_talebi view (kurumsal talep formu — ProjectRequest modeli, FAQPage schema)
/ai-cozumler/       → ai_cozumler view (AI ajan/otomasyon landing page — feature flag: feature_agentic_landing, default False)
/sitemap.xml        → Django sitemaps (StaticView, Topic, Category, Job, BlogPost, Istatistik, Tools)
/robots.txt         → TemplateView
/534e22a9f9e4d375119c5bc6d006aad0.txt → IndexNow key (Bing doğrulama)
/                   → forum.urls  (en sona — çakışma önlemi)

# istatistik.urls içindeki URL'ler:
/istatistik/cronbach/
/istatistik/normallik/
/istatistik/betimsel/
/istatistik/korelasyon/
/istatistik/orneklem/
/istatistik/ttesti/
/istatistik/anova/
/istatistik/mann-whitney/
/istatistik/kruskal-wallis/
/istatistik/ki-kare/
/istatistik/lineer-regresyon/
/istatistik/lojistik-regresyon/
/istatistik/karar-agaci/
/istatistik/svm/
# Her araç için: /istatistik/<araç>/status/<uuid:job_id>/

# forum.urls içindeki mesajlaşma API'leri:
/api/message/<int:message_id>/edit/              → api_edit_message (POST)
/api/message/<int:message_id>/delete/            → api_delete_message (POST, soft delete)
/api/chat/<str:username>/delete-conversation/    → api_delete_conversation (POST, hard delete)
/api/room-post/<int:post_id>/edit/               → api_edit_room_post (POST)
/api/room-post/<int:post_id>/delete/             → api_delete_room_post (POST, hard delete — S3 signal)
```

---

## 8. VERİ MODELLERİ (`forum/models.py`)

### Kullanıcı ve Profil
```python
class Profile:   # User ile OneToOne
    account_type: 'Free' | 'Premium' | 'Expert'
    rank: 'newbie' | 'member' | 'active' | 'contributor' | 'expert' | 'master' | 'legend' | 'admin'
    reputation: int          # Akademik puan (forum etkinliğinden otomatik)
    skills: M2M → Skill
    # Uzman olmak için rank: expert/master/legend/admin VEYA account_type: Expert

class Skill:     # Uzmanlık alanları
    name, slug
```

### Forum
```python
class Category:  # Forum kategorisi
    title, slug, description, order

class Topic:     # Konu başlığı
    category, author, title, body
    is_pinned, is_closed
    created_at, updated_at

class Post:      # Yanıt (Topic'e bağlı)
    topic, author, body
    is_best_answer   # "En Faydalı Cevap"
    created_at
```

### Hizmetler Pazarı (FreelanceJob)
```python
class JobCategory:   # Forum Category'den BAĞIMSIZ — yalnızca iş ilanı kategorileri
    title: str
    order: int
    is_active: bool
    # Admin → Forum & İçerik → İş Kategorileri

class FreelanceJob:
    owner: FK → User
    title: str
    description: TextField
    budget_min: Decimal (null=True, blank=True)  # Formda gösterilmez — geriye dönük uyumluluk
    budget_max: Decimal                           # Kullanıcının girdiği tek bütçe alanı
    category: FK → JobCategory (null=True, blank=True)
    status: 'open' | 'in_progress' | 'completed' | 'cancelled'
    is_edited: bool        # 1 kez düzenleme hakkı (teklif yokken, open iken)
    reference_number: str  # Örn: 2026/0013 (otomatik)
    expires_at: datetime   # Son geçerlilik
    is_featured: bool
    views: int
    likes: M2M → User
    saved_by: M2M → User

class JobProposal:
    job: FK → FreelanceJob
    expert: FK → User
    status: 'pending' | 'accepted' | 'rejected'
    price: Decimal
    duration: str          # "3 gün", "1 hafta" vb.
    message: TextField
    # Kabul edilince: job.status → 'in_progress'
```

### Quiz Puan Sistemi
- Her doğru cevap: **10 puan** (`QuizScore.total_points += 10`)
- Teklif verme eşiği: 1000+ toplam puan (forum `reputation` + quiz `total_points`)
- `quiz-efsanesi` rozeti: 1000 doğru cevap → teklif hakkı (alternatif yol)

### İlan Kuralları (Hizmetler Pazarı)
- **Düzenleme:** `status=open` AND `proposals.exists()=False` AND `is_edited=False` → 1 kez düzenlenebilir
- **İptal:** `close_job` view → `status=cancelled` → bekleyen teklif verenlere AnalizBot DM
- **Teklif fiyat gizliliği:** `feature_proposal_price_privacy=True` → fiyatlar gizli, sadece taraflar görür
- **İlan süresi:** `Profile.get_job_duration_days()` puana göre: &lt;500p → 10 gün, 500–1000p → 20 gün, 1000+p → 30 gün; yayınlama ekranında kullanıcıya gösterilir; "İlanlarım" sayfasında kalan gün + bitiş tarihi görünür
- **Haftalık ilan limiti:** Free=1, Premium=3; her 5 geçerli referans için +1 bonus (maks +2) — `get_weekly_job_limit()` DB'den referral sayısını çeker

### Referral (Davet) Sistemi
```python
class ReferralCode:          # Her kullanıcıya OneToOne, benzersiz 8-karakter kod
    user: OneToOne → User
    code: str                # secrets.token_urlsafe(6)[:8].upper()

class ReferralUse:           # Davet bağlantısıyla kayıt olan her kullanıcı
    referrer: FK → User      # Davet eden
    referred: OneToOne → User  # Davet edilen (unique — 1 referrer)
    ip_address: str          # Abuse tespiti
    email_verified_at: datetime (null)
    qualified_at: datetime (null)
    rewarded: bool
    flagged: bool            # IP abuse şüphesi
    premium_days_awarded: int
    reputation_awarded: int
```
**URL'ler:** `/davet/` (dashboard) · `/davet/<code>/` (landing → session'a kod yaz → register'a yönlendir)
**Geçerlilik koşulları (hepsi zorunlu):** e-posta doğrulama + 48 saat bekleme + 1 quiz sorusu çözme
**Abuse önleme:** aynı IP'den max 2 ödül; referrer 7 günlük hesap + email_verified; self-referral yasak
**Ödül (azalan getiri):** 1–5. davet → 20 gün premium, 6–10. → 10 gün, 11+ → 5 gün; her davette +50 rep
**Rozet kademeleri:** 1. davet → "Davetçi", 5. → "Topluluk Elçisi", 10. → "Büyükelçi"
**Tetikleyici:** `user_logged_in` signal + `verify_email` view → `check_and_award_referral()` (forum/services/referral_service.py)
**Admin:** Ekosistem → Davet Kodları / Davet Kullanımları; `rewarded` + `flagged` filtreleri

### İstatistik İşi
```python
class IstatistikJob:
    user: FK → User (null=True — anonim demo)
    tool: str   # TOOL_CHOICES — tüm araç listesi
    status: 'pending' | 'running' | 'completed' | 'failed'
    original_filename: str
    options: JSONField      # dep_col, indep_cols, group_col, columns vb.
    result_data: JSONField  # Analiz sonuçları (template'te JS ile render edilir)
    pdf_url: str            # S3 public URL
    error_message: str
    is_demo: bool
    created_at, completed_at
    # Dosya içeriği in-memory dict'te tutulur (_pending_file_contents)
    # — DB'ye yazılmaz, worker thread'e aktarılır
```

### Kurumsal Talep (ProjectRequest)
```python
class ProjectRequest:
    name: str                  # Ad Soyad
    email: EmailField
    company: str (blank)       # Kişi / Şirket / Kurum
    analysis_type: choice      # visualization | ml | statistics | cleaning | timeseries | nlp | literature | verification | agentic | bibliometric | other
    description: TextField
    data_size: choice          # small | medium | large | unknown
    timeline: choice           # urgent | short | flexible
    status: choice             # new | in_review | contacted | closed  (admin'den yönetilir)
    source: choice              # direct | yoktez | trdizin | tool | hero | home_corporate | verification | agentic | tableau | bibliometrics (default: direct)
    admin_notes: TextField
    # Gönderimde: admine ADMIN_NOTIFICATION_EMAIL'e + kullanıcıya onay e-postası gider
    # Admin paneli: renk kodlu durum, list_editable status, fieldset
    # source ön-seçim pattern'i: proje_talebi.html'de {% if source == '...' %} ile analysis_type
    # select'inde ilgili <option> otomatik seçilir (ör. source=verification → "AI Analiz Doğrulama").
    # `?type=` GET param'ı da okunur (view'da `qs_type`) — ama YALNIZCA bibliometric için: source
    # değeri 'bibliometrics' iken ANALYSIS_CHOICES'ta doğrudan aynı ada denk gelmediğinden
    # (source='bibliometrics' ama analysis_type='bibliometric'), select şu ikisinden HERHANGİ
    # biri sağlanırsa 'bibliometric'i seçili yapar: source=='bibliometrics' OR qs_type=='bibliometric'
    # (temmuz 2026, "son süpürme" turu — önceki iki turda "?type= hiç işlenmiyor, eklemeye gerek yok"
    # notu düşülmüştü, bibliometric case'inde gerçekten gerekti). Diğer tüm kaynaklar (verification,
    # agentic, tableau→visualization, yoktez/trdizin→literature) hâlâ salt `source` ile eşleşiyor.
    # `?source=tool` paylaşımlı `templates/service_promo.html`/`analiz_console_base.html`'den geliyor —
    # ~10+ araç sayfası aynı include'u paylaşıyor. Sayfaya özel source değeri gerekiyorsa (ör.
    # bibliometrics → `?source=bibliometrics&type=bibliometric`) `service_promo.html`'e opsiyonel
    # `promo_cta_source` context değişkeni eklenmiş; view context'ine `'promo_cta_source': 'X'`
    # geçirilmezse `tool` varsayılanına düşer (`bibliometrics/views.py`, ayrıca `&type=bibliometric`
    # yalnızca bu kaynak için ekleniyor). `service_promo.html` ayrıca `promo_gallery` (opsiyonel
    # örnek-çıktı galerisi) ve `promo_openalex_bridge` (opsiyonel OpenAlex köprü bandı) bayraklarını
    # destekler — ikisi de yalnızca bibliometri true geçiyor, diğer araç sayfalarını etkilemez.
```

### Diğer Önemli Modeller
```python
class SiteSettings:      # Singleton (tek kayıt) — feature flag'ler admin'den yönetilir
class PrivateMessage:    # Kullanıcılar arası DM (attachment: FileField → S3)
    # edited_at: DateTimeField (null=True) — düzenleme zamanı
    # is_deleted: BooleanField (default=False) — yumuşak silme; mesaj='' olur, kayıt kalır
class BlogPost / BlogCategory
class StudyRoom:         # Çalışma odaları
class StudyRoomPost:     # Oda mesajları (file: FileField → S3)
    # edited_at: DateTimeField(null=True) — düzenleme zamanı (migration 0120)
class QuizQuestion / QuizScore:  # İstatistik Arena — 432 soru (hedef: 1000)
class Badge:             # Rozetler
class SuccessStory:      # Başarı hikayeleri
class DonationTier:      # Destek paketi (name, min_amount, premium_days, is_active)
class Donation:          # Bağış kaydı
    # STATUS: pending → pending_confirmation → completed | failed
    # pending_confirmation: kullanıcı "Havaleyi Yaptım" butonuna bastı, admin onayı bekliyor
    # grant_premium() / grant_supporter_badge() — completed olunca çağrılır
class JobPayment:        # İlan vitrin ödemeleri
    # STATUS: pending → pending_confirmation → success | failed
    # ⚠️ status alanı admin'de readonly — değişiklik yalnızca list action ile yapılır
    # approve_feature action: status='success' VE job.feature_status='pending' olanları da işler
```

---

## 9. FEATURE FLAG SİSTEMİ

`SiteSettings` modeli (tek kayıt) — admin panelinden yönetilir.

| Flag | Varsayılan | Açıklama |
|---|---|---|
| `feature_blog` | True | Blog |
| `feature_market` | True | Hizmetler Pazarı |
| `feature_proposal_price_privacy` | True | Teklif fiyat gizliliği |
| `feature_ai_assistant` | True | AI Asistan |
| `feature_trdizin` | **False** | TR Dizin (gizli, özel kullanıcılara açılabilir) |
| `feature_semanticscholar` | True | Semantic Scholar Yayın Kazıma |
| `feature_openalex` | True | OpenAlex |
| `feature_oaipmh` | True | OAI-PMH Üniversite Arşivi |
| `feature_quiz` | True | İstatistik Arena |
| `feature_messaging` | True | Özel Mesajlaşma |
| `feature_bibliometrics` | True | Bibliometrik Analiz |
| `feature_yoktez` | True | YÖK Tez |
| `feature_istatistik` | True | İstatistik Araçları |
| `feature_transcript` | **False** | YouTube Transcript İndirici — cloud IP engeli nedeniyle Render'da doğrulanamadı, kapalı (bkz. §26) |
| `feature_agentic_landing` | **False** | AI Çözümler (Agentic) Sayfası — `/ai-cozumler/` |

Template kullanımı: `{% if features.openalex %}...{% endif %}`
Kaynak: `forum/context_processors.py` → `feature_flags()`

---

## 10. CSS / TASARIM SİSTEMİ

### Temel Kural
- **Bootstrap:** Yalnızca grid layout — `container`, `row`, `col-*`
- **UI Elementleri:** `ax-` prefix'li özel sınıflar — `btn`, `card`, `badge` Bootstrap'ten **değil**
- **CSS Değişkenleri:** Tüm renkler ve spacing `static/css/base.css` içindeki `:root`'tan

### CSS Değişkenleri (`base.css`)
```css
:root {
  --ax-primary:    #6366f1;   /* Indigo — primary aksiyonlar */
  --ax-accent:     #8b5cf6;   /* Violet — vurgu */
  --ax-bg:         #0f172a;   /* Koyu sayfa arka planı */
  --ax-surface:    #1e293b;   /* Kart/panel arka planı */
  --ax-border:     rgba(255,255,255,0.08); /* Kart kenarlığı */
  --ax-text:       #f1f5f9;   /* Ana metin */
  --ax-muted:      #94a3b8;   /* Soluk metin */
}
```

### Bootstrap'te Eksik Renk Utility Class'ları (`style.css`)
Bootstrap `text-teal` / `text-purple` / `btn-teal` / `btn-purple` sınıflarını tanımlamaz.
`istatistik/views.py`'de bazı araçlar `promo_color='teal'` veya `promo_color='purple'` kullanır;
bu sınıflar `static/css/style.css` sonunda tanımlıdır:
```css
.text-teal   { color: #20c997 }   /* Kruskal-Wallis, SVM */
.text-purple { color: #c084fc }   /* t-Testi, Ki-Kare, Karar Ağacı */
.btn-teal / .btn-purple / .btn-outline-teal / .btn-outline-purple
```
Yeni araç eklerken `teal` / `purple` dışında bir renk kullanılıyorsa önce Bootstrap class'ının var olup olmadığını kontrol et.

### `ax-` Prefix CSS Sınıfları (Örnekler)
```
.ax-card                → Temel kart (surface arka plan, ax-border)
.ax-btn                 → Temel buton
.ax-btn--primary        → Primary buton (indigo)
.ax-badge               → Rozet
.ax-job-budget          → İlan bütçe alanı
.ax-profile-*           → Profil sayfası bileşenleri
.ax-market-*            → Market/ilan bileşenleri
.ax-noise-overlay       → Site geneli subtle grain texture (base.html body hemen altında; SVG feTurbulence, opacity 0.025, position:fixed, pointer-events:none)
.ax-market-visual       → Market kartlarına dekoratif SVG arka planı (home_sections.css; parent kart position:relative + overflow:hidden gerektirir; mobile hidden)
```

### CSS Dosya Versiyonlama (Cache Busting)
`<link href="{% static 'css/foo.css' %}?v=XXXX">` — dosya içeriği değiştiğinde `v=` sayısını artır.
- **Neden:** nginx (production) `Cache-Control: max-age` ile CSS'i önbelleğe alır. `v=` değişmezse tarayıcı eski dosyayı sunar.
- **Lokal tuzak:** Django dev server nginx'ten geçmez → lokalde güncel görünür, production'da eski stil kalır.
- Bir CSS dosyasını her düzenleyişte o dosyanın `?v=` stringini güncelle.

### Geliştirici Kuralı
Yeni bileşen yazarken:
1. HTML: Bootstrap grid (`row`, `col`) ile iskelet kur
2. UI: İçeriği `ax-` sınıflarıyla tasarla
3. JS: `data-bs-toggle` yerine vanilla event listener kullan
4. Asla hardcode renk/pixel yazma — `var(--ax-primary)` kullan
5. CSS dosyası değiştiğinde `?v=XXXX` string'ini güncelle (cache busting)

---

## 11. GERÇEK ZAMANLI (DJANGO CHANNELS)

```python
ASGI_APPLICATION = 'analizdestek.asgi.application'

# Local (Redis yoksa):
CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

# Prod (Redis var):
CHANNEL_LAYERS = {"default": {
    "BACKEND": "channels_redis.core.RedisChannelLayer",
    "CONFIG": {"hosts": [REDIS_URL]}
}}
```

WebSocket path: `/ws/` — Nginx'te ayrı `proxy_pass` bloğu (proxy_http_version 1.1, Upgrade header)

---

## 12. İSTATİSTİK ARAÇLARI

### Genel Akış
```
Kullanıcı dosya yükler (CSV/Excel, max 10MB)
    → step=preview: dosya parse edilir, sütun listesi döner (AJAX)
    → step=run: değişkenler seçilir, IstatistikJob oluşturulur
    → job_queue.py (ThreadPoolExecutor) → _execute_job(job_id)
    → Servis fonksiyonu çalışır (pandas, scipy, statsmodels, sklearn)
    → PDF oluşturulur (reportlab, DejaVuSans Türkçe font)
    → S3'e yüklenir: istatistik/{tool}/{job_id}.pdf
    → mark_completed(result_data, pdf_url)
    → JS polling (2sn aralık) status=completed algılar → sonuçlar ekranda gösterilir
    → Admin'e bildirim e-postası (araç adı + public sayfa linki)
```

### Dosya İçeriği Aktarımı
- **In-memory:** `_pending_file_contents: dict[str, bytes]` (job_runner.py)
- Preview: `store_file_content('preview_' + preview_id, content)`
- Run: `content = _pending_file_contents.pop('preview_' + preview_id)` → `store_file_content(str(job.id), content)`
- Worker: `content = _pending_file_contents.pop(job_id)`
- **Önemli:** Dict aynı process içinde thread'ler arası paylaşılır. Çoklu worker process kullanılamaz.

### Mevcut Araçlar

| URL Slug | Tool Kodu | Servis | Açıklama |
|---|---|---|---|
| `cronbach/` | `cronbach` | cronbach.py | Cronbach Alpha — çoklu sütun seçimi |
| `normallik/` | `normallik` | normallik.py | Shapiro-Wilk, KS, Skewness/Kurtosis — sütun seçimi |
| `betimsel/` | `betimsel` | betimsel.py | Betimsel istatistik — sütun seçimi |
| `korelasyon/` | `korelasyon` | korelasyon.py | Pearson/Spearman/Kendall korelasyon matrisi |
| `orneklem/` | — | orneklem.py | Örneklem büyüklüğü (JS hesaplama, job yok) |
| `ttesti/` | `ttesti` | ttesti.py | t-Testi (bağımsız/bağımlı/tek örneklem) |
| `anova/` | `anova` | anova.py | Tek yönlü ANOVA + Tukey/Bonferroni post-hoc + η² |
| `mann-whitney/` | `mann_whitney` | mann_whitney.py | Mann-Whitney U (parametrik olmayan, 2 grup) |
| `kruskal-wallis/` | `kruskal_wallis` | kruskal_wallis.py | Kruskal-Wallis H (parametrik olmayan, 3+ grup) |
| `ki-kare/` | `ki_kare` | ki_kare.py | Ki-Kare + Fisher's Exact Test |
| `lineer-regresyon/` | `lineer_regresyon` | lineer_regresyon.py | Çoklu Doğrusal Regresyon (OLS) |
| `lojistik-regresyon/` | `lojistik_regresyon` | lojistik_regresyon.py | Lojistik Regresyon (Binary) |
| `friedman/` | `friedman` | friedman.py | Friedman Testi (tekrarlayan ölçüm, parametrik olmayan) |
| `tekrarli-anova/` | `tekrarli_anova` | tekrarli_anova.py | Tekrarlayan Ölçümler ANOVA + Cohen's d post-hoc |
| `karar-agaci/` | `karar_agaci` | karar_agaci.py | Karar Ağacı Sınıflandırması (DecisionTreeClassifier, feature_importances_) |
| `svm/` | `svm` | svm.py | Destek Vektör Makinesi (SVC, RBF/Linear/Poly, StandardScaler, permutation importance) |

### Araç Kategorileri (`TOOL_CATEGORIES` — `istatistik/views.py`)
```python
('Güvenirlik', ['cronbach'])
('Tanımlayıcı', ['normallik', 'betimsel', 'korelasyon', 'orneklem'])
('Karşılaştırma', ['ttesti', 'anova', 'mann_whitney', 'kruskal_wallis', 'ki_kare', 'friedman', 'tekrarli_anova'])
('Regresyon', ['lineer_regresyon', 'lojistik_regresyon'])
('Makine Öğrenmesi', ['karar_agaci', 'svm'])
```
Her kategori `analiz_console_base.html` sidebar'ında accordion olarak gösterilir.

### Makine Öğrenmesi Araçları (Detay)

**Karar Ağacı (`karar_agaci.py`)**
- `sklearn.tree.DecisionTreeClassifier`; bağımlı değişken kategorik
- `clf.feature_importances_` ile doğrudan feature önem sıralaması
- Çıktı: accuracy, precision, recall, f1, confusion_matrix, feature_importances list, max_depth, n_leaves

**Destek Vektör Makinesi (`svm.py`)**
- `sklearn.svm.SVC` + `StandardScaler` (ölçekleme zorunlu — karar ağacından farkı)
- Kernel seçeneği: RBF (varsayılan), Linear, Poly; C parametresi: 0.1–10
- Feature önemi: `sklearn.inspection.permutation_importance` (model-agnostik; `np.clip(importances, 0, None)` — negatif değer kesilir)
- Büyük dataset (>5000 satır): 5000 satıra otomatik örnekleme (stratified)
- Çıktı: accuracy, precision, recall, f1, confusion_matrix, n_support_vectors, feature_importances list, kernel, C

### Regresyon Araçları (Detay)

**Çoklu Doğrusal Regresyon (`lineer_regresyon.py`)**
- `statsmodels.api.OLS` ile model; standardize beta için `sklearn.StandardScaler`
- VIF: `statsmodels.stats.outliers_influence.variance_inflation_factor`
- Kategorik bağımsız değişkenler `pd.get_dummies(drop_first=True)` ile otomatik dummy'e dönüştürülür
- Çıktı: R², düzeltilmiş R², F istatistiği, B, β, SE, t, p, %95 GA, VIF
- PDF renk: navy blue `#1e3a5f`

**Lojistik Regresyon (`lojistik_regresyon.py`)**
- `statsmodels.Logit`; Nagelkerke R² manuel: `cox_snell / max_cox_snell`
- Wald: `tvalues[i] ** 2`; Exp(B) = `np.exp(params[i])`
- Sınıflandırma tablosu: TP, TN, FP, FN, doğruluk %
- Bağımlı değişken binary (0/1 veya iki kategorili string)
- PDF renk: teal `#065f46`

### PDF Çıktısı
- `reportlab` + DejaVuSans fontu (`pdf_fonts.py` ile register edilir)
- Her araçta `conf_int()` sonucu `np.array()` ile sarılır (DataFrame değil, numpy array döner)
- VIF `inf`/`nan` ise `'—'` olarak gösterilir (JSON serialization hatası önlenir)
- **Her analizin PDF'i "Tezinde Nasıl Raporlarsın?" bölümü içerir** — APA formatında hazır metin

### APA Raporlama Metni (Lineer Regresyon Örnek Format)
```
"[dep_col] değişkenini yordamak amacıyla kurulan model [anlamlı/değil],
F(df_model, df_resid) = x.xxx, p = x.xxx. Model, bağımlı değişkendeki
varyansın %xx.x'ini açıklamaktadır (R² = x.xxxx, düzeltilmiş R² = x.xxxx).
Anlamlı yordayıcılar: Değişken (B = x.xxx, β = x.xxx, p = x.xxx); ..."
```

### JS Polling Kritik Kuralı
```javascript
// YANLIŞ — double slash üretir (/status//uuid/):
const STATUS_BASE = '{% url "istatistik:cronbach_status" "00000000..." %}'.replace('00000000...', '');
fetch(STATUS_BASE + jobId + '/')

// DOĞRU — ki_kare ve regresyon template'lerinde kullanılan pattern:
const STATUS_TEMPLATE = '{% url "istatistik:cronbach_status" "00000000-0000-0000-0000-000000000000" %}';
fetch(STATUS_TEMPLATE.replace('00000000-0000-0000-0000-000000000000', jobId))
```

### Navigasyon Menüsü (`base.html` — Mayıs 2026)
```
Analizler ▾          → İstatistik Analiz Araçları (/analiz/)
                       Bibliometrik Analiz (/bibliometrics/)
                       Tableau Analizleri
                       ──────────────────────────
                       Hangi Test? (/hangi-test/)
                       AI Asistan (/ai-asistan/)
                       Çalışma Odaları (/odalar/)

Akademik Tarama      → /tarama/ (direkt link; aktif path ile is-active vurgusu)

Pazaryeri            → /hizmetler/ (eski adı: Hizmetler)

Kurumsal ▾           → Neden Analizus? (/neden-biz/)
                       Blog (/blog/)
                       Hakkımızda + İletişim
```
Mobil drawer: Her üst gruba accordion. Analizler altında `/analiz/` tek link (eski 16 ayrı link kaldırıldı).

### Unified Analiz Arayüzü (TAMAMLANDI — mayıs 2026)
- 18 istatistik aracı tek sidebar'lı konsol: `/analiz/<slug>/`
- `analiz_console_base.html` + `analiz_console.css` — sidebar kategorilere göre accordion, aktif araç vurgulu
- Eski `/istatistik/<slug>/` URL'leri çalışmaya devam eder (redirect yok, template değişti)
- Context: `TOOL_CATEGORIES` sabiti + `_console_ctx()` helper (`istatistik/views.py`)
- `/analiz/` URL'i `istatistik/urls_analiz.py` üzerinden dahil edildi; `analiz_hub` view tüm araçları listeler
- `analiz_console` view içindeki `_SLUG_MAP` tüm 18 aracı içerir (svm dahil — eksikti, 404 üretiyordu)
- Mobilde sidebar gizli, "Araç Seç" toggle butonu ile açılır

---

## 13. ÖZEL MESAJLAŞMA (DM) — DÜZENLEME / SİLME / SOHBET SİLME

### Model Alanları (PrivateMessage)
- `edited_at: DateTimeField(null=True, blank=True)` — mesaj düzenlenince doldurulur
- `is_deleted: BooleanField(default=False)` — yumuşak silme; silinince `message=''` olur, kayıt DB'de kalır

### API Endpoint'leri (`forum/views.py`)
| Endpoint | İzin | Açıklama |
|---|---|---|
| `POST /api/message/<id>/edit/` | Sadece gönderen | `message`, `edited_at` günceller; WS broadcast |
| `POST /api/message/<id>/delete/` | Sadece gönderen | `is_deleted=True`, `message=''`; WS broadcast |
| `POST /api/chat/<username>/delete-conversation/` | Giriş yapmış | Broadcast ÖNCE gönderilir, sonra hard delete |

### WebSocket Broadcast Yardımcıları (`forum/views.py`)
```python
def _chat_room_name(uid1, uid2):
    ids = sorted([uid1, uid2])
    return f'chat_{ids[0]}_{ids[1]}'   # ChatConsumer ile aynı format — önemli

def _broadcast_chat(uid1, uid2, event):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(_chat_room_name(uid1, uid2), event)
```

### ChatConsumer Handlers (`forum/consumers.py`)
Üç yeni handler eklendi — WS event type → handler eşleşmesi:
- `message_edit` → `message_id`, `message`, `edited_at` gönderir
- `message_delete` → `message_id` gönderir
- `conversation_delete` → payload boş; client `/inbox/` adresine yönlendirilir

### Poll API Notu
`api_chat_poll` endpoint'i `is_deleted=False` filtresi eklenmiştir — silinmiş mesajlar polling ile geri gelmez.

---

## 13b. ÇALIŞMA ODASI MESAJLARI — DÜZENLEME / SİLME

### Model Alanı (StudyRoomPost)
- `edited_at: DateTimeField(null=True, blank=True)` — mesaj düzenlenince doldurulur (migration 0120)

### API Endpoint'leri (`forum/views.py`)
| Endpoint | İzin | Açıklama |
|---|---|---|
| `POST /api/room-post/<id>/edit/` | Sadece yazar | `message`, `edited_at` günceller |
| `POST /api/room-post/<id>/delete/` | Sadece yazar | Hard delete — `post_delete` signal S3 dosyasını temizler |

### Davranış Farkı (DM'den)
- DM siler: **soft delete** (`is_deleted=True, message=''`) — kayıt DB'de kalır, WS broadcast var
- Oda siler: **hard delete** — kayıt DB'den silinir, DOM'dan kaldırılır; WS yok (polling mimarisi)
- Düzenleme yalnızca metin içindir; dosya eki düzenlenemez

### @mention E-posta Bildirimi
- Gönderilen mesajda `@username` varsa ve o kullanıcı oda üyesiyse:
  1. `Notification` kaydı oluşturulur (mevcut sistem)
  2. `email_utils.notify_room_mention()` ile async e-posta gönderilir
- Tüm üyelere değil — **yalnızca etiketlenen kişiye** gider

---

## 14. BİBLİOMETRİK ANALİZ

- Desteklenen formatlar: BibTeX (.bib), WoS TSV, Scopus CSV, OpenAlex TXT (otomatik algılama)
- Çoklu dosya birleştirme
- 10 Analiz türü: Yayın trendi, top yazarlar, kelime bulutu, top atıf, top dergi, kurum/ülke, işbirliği ağı, yayın türleri, h-index, yıllık atıf
- İş modeli: Demo (3 grafik, ücretsiz) / Tam (10 grafik, ücretli)
- S3 paths: `bibliometrics/demo/`, `bibliometrics/full/`

---

## 15. AKADEMİK TARAMA ARAÇLARI

### Scraping Ban Koruması (3 Servis)

| Koruma | YÖK Tez | TR Dizin | OpenAlex |
|---|---|---|---|
| Semaphore | `Semaphore(2)` | `Semaphore(3)` | `Semaphore(4)` |
| 429/503 backoff | 5-9s × deneme | 5-10s × deneme | Retry-After header |
| UA rotasyonu | 4 farklı UA | 4 farklı UA | — (API, UA sabit) |
| Sayfa gecikmesi | 0.8-2.0s | 0.5-1.5s | 0.3-0.6s |
| Queue pozisyonu | status endpoint'te `queue_position` alanı |

- Status `pending` iken frontend "Sırada N. sıradasınız" gösterir
- İndirilen dosya adları: `yoktez_<kelime>_<tarih>.xlsx`, `trdizin_<kelime>_<tarih>.xlsx` vb.

### OpenAlex (`openalex/`)
- 240M+ akademik kayıt, ücretsiz API
- Cursor-based pagination, max 5000 sonuç
- `OPENALEX_EMAIL` env var (polite pool, 10 req/s)
- S3 paths: `openalex/demo/`, `openalex/full/`, `openalex/orders/`

### YÖK Tez (`yoktez/` vs `tezanaliz/` — KARIŞTIRILMAMALI)
- `/yoktez/` = **Tarama**: arama formu → TXT/Excel indir (ham veri)
- `/tezanaliz/` = **Analiz**: aynı arama + 7 grafiksel analiz (LDA, TF-IDF, trend, wordcloud) + PDF
- `tezanaliz` scraper için `yoktez.services.scraper`'ı import eder — rate limiting her ikisine de uygulanır
- HTTP tabanlı (requests + BeautifulSoup) — Selenium yok

### Semantic Scholar (`semanticscholar/`)
- `feature_semanticscholar = True`
- Semantic Scholar Graph API (`api.semanticscholar.org/graph/v1/paper/search`)
- 200M+ yayın; WoS, Scopus, PubMed, arXiv dahil
- DOI'si olan kayıtlar CrossRef API ile kurum/yayıncı/konu bilgisiyle zenginleştirilir
- Arama alanları: keyword, title, author, year, field_of_study, doi
- Max 1.000 kayıt (API hard limit — offset sınırı)
- `SEMANTIC_SCHOLAR_API_KEY` env var (saniyede 1 istek; key'siz paylaşımlı limit)
- Key yeni oluşturulunca aktivasyon birkaç saat sürebilir; bu sürede key'siz çalışır (429)
- S3 paths: `semanticscholar/demo/`, `semanticscholar/full/`

### TR Dizin (`trdizin/`)
- `feature_trdizin = False` — varsayılan gizli, admin'den açılabilir
- REST JSON API tabanlı (`search.trdizin.gov.tr/api/`)

### OAI-PMH (`oaipmh/`)
- 19 üniversite kayıtlı; **17 aktif** (Akdeniz ve Fırat `is_active=False` — sunucu erişilemez/WAF)
- Çalışan 17: ODTÜ, İTÜ, Dokuz Eylül, Çukurova, Uludağ, Sakarya, Mersin, Muğla, Afyon Kocatepe, Kafkas, Giresun, Ordu, Isparta, Uşak, Düzce, BEUN, Sabancı
- `sickle` kütüphanesi (OAI-PMH client)
- **Job kuyruğu:** `job_queue.enqueue('oaipmh', job_id)` kullanır — eski raw `threading.Thread` kaldırıldı
- Stale job cutoff: 60 dakika (scraping 19 üniversiteyi tarayabilir, kısa timeout uygun değil)
- Çukurova + Uşak: HTTPS desteklemiyor → `http://` URL kullanılıyor
- Uludağ + BEUN: DSpace 7'ye geçmiş → `/server/oai/request` path (migration `0008_fix_university_urls`)

### Akademik Tarama Unified Console
- 4 tarama aracı tek sidebar'lı konsolda: `/tarama/` → `tarama_hub` view (hub sayfası; eski redirect kaldırıldı), her araç kendi URL'inde çalışır
- `templates/tarama_console_base.html` — `analiz_console.css`'i yeniden kullanır (`.ax-console-*` sınıfları)
- Sidebar aktif araç tespiti: `request.path` ile (context processor gerekmez)
- Feature flag kontrollü: `features.oaipmh`, `features.yoktez`, `features.openalex`, `features.trdizin`
- Landing template'leri `base.html` yerine `tarama_console_base.html`'i extend eder; `{% block content %}` → `{% block tool_area %}`

---

## 16. E-POSTA SİSTEMİ

**SMTP:** `mail.analizus.com` (587 TLS veya 465 SSL — settings.py otomatik algılar)
**Gönderici:** `Analizus <info@analizus.com>`
**Async:** `forum/email_utils.py` içindeki tüm fonksiyonlar threading ile çalışır — blocking değil

### Admin Bildirim Fonksiyonları (`email_utils.py`)
Her önemli event'te `bkeles74@gmail.com` adresine bildirim:
- Yeni kullanıcı, yeni konu, yeni yanıt
- Yeni ilan, yeni teklif, teklif kabul, iş tamamlandı
- Blog yayınlandı, analiz tamamlandı

### Destekçi E-postası (`support_payment_details.html`)
- Endpoint: `POST /api/send-support-email/` → `forum/views.py:send_support_email`
- Kullanıcı footer modalından tier seçer → buton e-posta gönderir
- Şablon: `forum/templates/forum/emails/support_payment_details.html` (HTML, koyu tema)
- İçerik: IBAN (TR73 0003 2000 0000 0079 1034 65), seçilen paket, premium gün, adımlar
- `donation_context` context processor → `DonationTier.objects.filter(is_active=True)` → her sayfada `donation_tiers` değişkeni

### `notify_admin_analysis_completed` Detayı
- Tüm istatistik araç kodları Türkçe isme çevrilir (`tool_names` dict)
- E-postadaki "Analiz Sayfasına Git" linki admin paneline değil **public araç sayfasına** gider: `{SITE_URL}/istatistik/{tool_path}/`

### Kullanıcı Bildirimleri
- Yeni teklif gelince → ilan sahibine e-posta
- Analiz tamamlanınca → kullanıcıya S3 linki ile e-posta
- Çalışma odası @mention → `notify_room_mention(sender, recipient, room, message)` — sadece etiketlenen oda üyesine

---

## 17. ANALİZBOT VE BİLDİRİM SİSTEMİ

**AnalizBot:** Sistem kullanıcısı (`username: AnalizBot`) — otomatik DM göndermek için kullanılır.

### Bildirim Sinyalleri (`forum/signals.py`)

| Event | Tetikleyici | Sonuç |
|---|---|---|
| Yeni kullanıcı | `User post_save (created)` | Admin email |
| Yeni konu | `Topic post_save (created)` | Admin email |
| Yeni yanıt | `Post post_save (created)` | Admin email |
| Yeni ilan | `FreelanceJob post_save (created)` | Admin email |
| Yeni teklif | `JobProposal post_save (created)` | İlan sahibine + Admin email |
| Teklif kabul | `JobProposal status → accepted` | Admin email |
| İş tamamlandı | `FreelanceJob status → completed` | Admin email + AnalizBot DM |
| Blog yayınlandı | `BlogPost status → published` | Admin email |
| Analiz tamamlandı | `IstatistikJob` signal | Admin email (public sayfa linki) |

### AnalizBot DM Gönderilen Durumlar
- İlan sahibi ilanı iptal edince → beklemedeki teklif verenlere DM
- İş tamamlanınca → başarı hikayesi daveti DM

### AI Asistan (Groq Chat Servisi)

**Dosya:** `forum/services/ai_service.py` (`GroqService` sınıfı, `SYSTEM_PROMPT`)
**Model:** `llama-3.3-70b-versatile` (Groq ücretsiz tier — ~14.400 istek/gün, 30 istek/dk)
**Feature flag:** `feature_ai_assistant` (SiteSettings) — kapalıysa her iki URL de 404 döner

#### Erişim ve Limitler
| Kullanıcı | Günlük Limit | Cache Key |
|---|---|---|
| Giriş yapmış | 30 soru/gün | `ai_usage_{user.id}_{date}` |
| Anonim | 3 soru/gün | `ai_usage_anon_{uuid}_{date}` |

`@login_required` kaldırıldı — anonim erişim **cookie bazlı** sınırlandırıldı (`ax_anon_id` UUID cookie, `max_age=86400`, `HttpOnly`, `SameSite=Lax`). IP bazlı yapılamazdı: Nginx arkasındaki tüm kullanıcılar aynı `172.x.x.x` internal IP'yi paylaşır. Her iki URL aynı cache key'i paylaşır (ortak kota).

#### URL'ler
- `GET/POST /ai-asistan/` → Tam sayfa chat arayüzü (`forum/views.py:ai_assistant`)
- `POST /api/ai/chat/` → Floating widget JSON API (`forum/views.py:api_ai_chat`) — body: `{message: str}`, cevap: `{success, response, remaining, daily_limit}`

#### System Prompt Mantığı
`SYSTEM_PROMPT` içinde platformun tüm araçları ve URL'leri kayıtlıdır. Kullanıcı ne yapmak istediğini söyleyince AI önce "**Analizus'ta bunu yapabilirsiniz: → /url/**" bloğunu verir, ardından teorik açıklamayı ekler:
- İstatistik analizi istiyorsa → `/istatistik/<araç>/` URL'i ile ilgili araca yönlendir
- Test seçimi belirsizse → soru sor (bağımlı değişken tipi, grup sayısı, normallik) → `/hangi-test/`
- Makale/tez araması → `/openalex/`, `/yoktez/`, `/semantic-scholar/`, `/bibliometrics/`
- Uzman/iş → `/uzmanlar/`, `/market/`, `/market/new/`
- Forum/topluluk → `/forum/`, `/odalar/`

#### Floating Chat Widget (`base.html`)
Tüm sayfalarda `{% if features.ai_assistant %}` bloğunda görünen WhatsApp-tarzı sohbet balonu:
- **Buton:** Sabit sağ alt, indigo gradyan; WhatsApp butonu varsa onun üstünde (`bottom: 110px`), yoksa `bottom: 48px`
- **Desktop popup:** 350×480px, sağ altta; butonun üstünde açılır
- **Mobil (≤575px):** Full-width bottom sheet, 72dvh yükseklik; `border-radius: 18px 18px 0 0`
- **Özellikler:** Typing indicator (3 nokta bounce), markdown render (`**bold**`, `` `code` ``), `→ Ad (/url/)` → `<a>` dönüşümü, Enter=gönder, Shift+Enter=yeni satır, textarea auto-grow, dışarı tıkla → kapat
- **Hak sayacı:** İlk başarılı mesajdan sonra header'da `N/30 hak` badge'i görünür
- **Anonim notu:** Giriş yapılmamışsa footer'da "3 soru/gün · Üye ol → 30 soru" satırı çıkar

#### Post-processing Filtreleri (`ai_service.py`)
Groq yanıtı `generate_response()` içinde sırayla iki filtreden geçer:
1. **`_CJK_RE.sub()`** — Llama'nın ara sıra eklediği Çince/Japonca/Korece karakterleri siler
2. **`_sanitize_paths()`** — `_ALLOWED_PATHS` frozenset dışındaki her `/path/` URL'yi yanıttan kaldırır; silinen URL'in çevresindeki `→ Ad ()` kalıplarını da temizler

`_ALLOWED_PATHS` güncellenirken `SYSTEM_PROMPT` platform haritası da eş zamanlı güncellenmelidir.

#### Önemli Non-obvious Kurallar
- `ai_assistant` view ve `api_ai_chat` view aynı cache key pattern'ini kullanır — birinden harcanan kota diğerini de etkiler
- Anonim cache key: `_anon_ai_cache_key(request)` → `ax_anon_id` cookie'den UUID okur; cookie yoksa yeni oluşturur ve tüm return path'lerde `_set_anon_cookie(response, anon_id)` ile set eder
- Groq API `max_tokens=1024`, `temperature=0.7` — uzun yanıtlar kesilebilir, bu değerler ayarlanabilir
- Widget JS'de URL'ler `target="_blank"` açılır — popup içinde sayfa değişmez
- Sistem prompt'ta URL'lerin "örnek amaçlı" veya "farklı olabilir" olduğunu söylemek kesinlikle yasak — bu kural KESİN YASAKLAR bölümünde açıkça belirtilmiştir

---

## 18. S3 DEPOLAMA YAPISI

```
analizus-files/
├── avatars/              # Profil fotoğrafları
├── covers/               # Kapak fotoğrafları
├── istatistik/
│   ├── cronbach/
│   ├── normallik/
│   ├── betimsel/
│   ├── korelasyon/
│   ├── ttesti/
│   ├── anova/
│   ├── mann_whitney/
│   ├── kruskal_wallis/
│   ├── ki_kare/
│   ├── lineer_regresyon/
│   ├── lojistik_regresyon/
│   ├── friedman/
│   ├── tekrarli_anova/
│   ├── karar_agaci/
│   └── svm/
├── bibliometrics/
│   ├── demo/
│   └── full/
├── openalex/
│   ├── demo/
│   ├── full/
│   └── orders/
├── trdizin/
│   ├── demo/
│   ├── full/
│   └── orders/
├── semanticscholar/
│   ├── demo/
│   └── full/
```

**Utils (`forum/s3_utils.py`):**
- `upload_to_s3(file_obj, s3_key)`
- `upload_bytes_to_s3(content_bytes, s3_key, content_type)`
- `delete_from_s3(s3_key)`

---

## 19. GÜVENLİK VE BOT KORUMASI

### Kayıt Formu (`forum/forms.py`)
1. **Honeypot:** `website` alanı CSS ile gizlenir (`position:absolute; left:-9999px`). Bot doldurursa reddedilir.
2. **Username doğrulama:** 4+ ardışık sessiz harf → bot pattern → reddedilir
   - Regex: `[bcçdfgğhjklmnprsştvyz]{4,}` (Türkçe ünsüzler dahil)
3. **Rate limit:** Kayıt `3/saat`, Login `10/5dk`, İstatistik POST `30/saat` (IP bazlı, `django-ratelimit`)

### Middleware
- `forum.middleware.HoneypotMiddleware` — POST'ta gizli `website` alanı dolu gelirse botu reddeder
- `forum.middleware.LastSeenMiddleware` — giriş yapmış kullanıcının `Profile.last_seen` alanını 60 saniyelik throttle ile günceller; static/media isteklerini atlar
- `forum.middleware.EmailVerificationMiddleware` — email doğrulanmamışsa bazı işlemler engellenir
- CSRF: Tüm formlarda zorunlu
- `XFrameOptionsMiddleware` — clickjacking önleme

---

## 20. ADMIN PANELİ

- **Tema:** Django Unfold (indigo/koyu tema)
- **URL:** `/admin/`
- **Dashboard:** `forum/dashboard.py` → `dashboard_callback`

### Önemli Admin Sınıfları (`forum/admin.py`)
- `JobCategoryAdmin` — iş kategorisi yönetimi (forum Category'den bağımsız)
- `FreelanceJobAdmin` — ilan yönetimi
- `JobProposalAdmin` — teklif (İlan Sahibi + Teklif Veren kolonları)
- `ProfileAdmin` — kullanıcı profil
- `SiteSettingsAdmin` — feature flag yönetimi
- `JobPaymentAdmin` — vitrin ödemeleri; `status` readonly; dashboard "VİTRİN" satırındaki **"Onayla →"** butonuyla tek tıkla onaylanır (`/admin/forum/jobpayment/<pk>/quick-approve/` — `quick_approve_view`); onay öncesi detay confirm dialogu çıkar; list view action ("Seçili ilanları vitrine ekle") da hâlâ çalışır
- `BibliometricOrderProxyAdmin` (`tezanaliz/admin.py`) — `status` readonly; **"Onayla ve Tam Rapor Emailini Gönder"** action ile onaylanır; e-posta + `status=completed` otomatik set edilir
- `AlexOrderAdmin` (`openalex/admin.py`) — OpenAlex siparişleri; `status` readonly; aynı action akışı

### Davranış Analizi (`analytics/admin.py`)
- `PageViewAdmin` — ham ziyaret logları (son 5 gün tutulur); kullanıcı adına tıklamak `/admin/analytics/pageview/grafik/` adresine yönlendirir (7 günlük bar+çizgi+kullanıcı grafikleri)
- `PageViewSummaryAdmin` — özetler (sonsuza kadar tutulur); kullanıcı adına tıklamak `/admin/analytics/pageviewsummary/grafik/` adresine yönlendirir (tüm geçmiş: stat box'ları + bar + çizgi + kullanıcı grafikleri)
- Ham loglar `cleanup_pageviews` yönetim komutu / `/api/cron/cleanup-pageviews/` endpoint'i ile özetlenir ve silinir
- Admin grafik template'leri dark mode'da Tailwind `dark:` prefix sınıfları yerine inline style kullanır (Unfold PurgeCSS uyumu)

### Gelir Kaynakları ve Ödeme Akışları
| Gelir | Model | Admin Onay Yolu |
|---|---|---|
| Bağış (Premium) | `Donation` | Dashboard "BAĞIŞ" → detail → action yok, `dashboard_approve_donation` view |
| İlan Vitrini | `JobPayment` | Dashboard "VİTRİN" → **"Onayla →"** (tek tıkla, confirm dialog) veya Job Payments list → "Seçili ilanları vitrine ekle" action |
| Bibliometrik Analiz | `BibliometricOrder` | Bibliometrik Siparişler list → "Onayla ve Tam Rapor Emailini Gönder" action |
| OpenAlex Sipariş | `AlexOrder` | OpenAlex Siparişleri list → "Onayla ve Tam Rapor Emailini Gönder" action |

> ⚠️ **KRİTİK:** Ödeme/sipariş `status` alanlarını admin detail sayfasından **elle değiştirme** — e-posta gönderilmez, job alanları güncellenmez. Her zaman **list view → action** kullan.

### Bağış Akışı (Kullanıcı tarafı)
```
Kullanıcı paket seçer → send_support_email → Donation(status=pending) oluşur + IBAN e-postası gönderilir
    ↓ E-postadaki "Havaleyi Yaptım" butonu
mark_donation_transferred view → status=pending_confirmation + admin bildirimi
    ↓ Admin dashboard "BAĞIŞ" satırı → dashboard_approve_donation
Donation.grant_premium() + grant_supporter_badge()
```

---

## 21. HIZMETLER PAZARI İŞ AKIŞLARI

```
İlan Aç (status=open)
    ↓
Uzman Teklif Verir (proposal status=pending)
    → İlan sahibine e-posta
    → Admin'e e-posta
    ↓
İlan Sahibi Teklifi Kabul Eder
    → FreelanceJob.status = in_progress
    → Admin'e e-posta
    ↓
İş Tamamlanır
    → FreelanceJob.status = completed
    → AnalizBot DM: başarı hikayesi daveti
    → Admin'e e-posta
```

---

## 22. OTURUM YÖNETİMİ

```python
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 7200          # 2 saat
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = True       # Prod'da (HTTPS zorunlu)
SESSION_COOKIE_DOMAIN = '.analizus.com'  # Prod'da
```

---

## 23. CRON SİSTEMİ

- Doğrulama: `X-Cron-Secret` header veya `?secret=` query param
- Env: `CRON_SECRET_KEY`
- **Aktif:** `/api/cron/cleanup-s3/` — trdizin + openalex S3 temizliği
- **Aktif:** `/api/cron/cleanup-attachments/` — 90 günden eski DM + oda mesajı dosyaları S3'ten silinir, mesaj/post kaydı korunur (haftalık çalıştırılması önerilir)
- **Aktif:** `/api/cron/cleanup-pageviews/` — 5 günden eski sayfa ziyaret loglarını PageViewSummary'e toplar ve siler; Hetzner crontab'ında `0 4 * * * curl -s "https://analizus.com/api/cron/cleanup-pageviews/?secret=..." >> /var/log/cron_pageviews.log 2>&1` ile çalışır. ⚠️ `www.analizus.com` kullanan eski satır `curl -L` olmadığından redirect'i takip etmez — crontab'da yalnızca `analizus.com` (www'suz) satırı kalmalıdır.
- **Aktif:** `/api/cron/process-account-deletions/` — `deletion_requested_at` üzerinden 30 gün geçmiş hesapları anonimleştirir (email/username/profil) + DM'leri siler; Hetzner crontab'ına `0 3 * * *` ile eklenmelidir
- **Kaldırılacak** (artık gereksiz): `/api/cron/daily-quiz/`, `/api/cron/update-badges/`

---

## 24. GELİŞTİRME ORTAMI

### Local Kurulum
```bash
cd analizdestek
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt   # statsmodels dahil
# .env dosyası oluştur: DATABASE_URL boş bırak (SQLite kullanılır)
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Faydalı Komutlar
```bash
python manage.py migrate           # Migration'ları uygula
python manage.py makemigrations istatistik --name="aciklama"  # Yeni migration
python manage.py collectstatic     # Statik dosyaları topla
python manage.py shell             # Django shell
python manage.py test              # Test suite (pytest-django)

# Test kullanıcıları (lokal SQLite'ta mevcut — prod'a gönderilmedi)
# testuser_a / testuser_b  →  şifre: testpass123  →  DM okundu göstergesi testi için oluşturuldu
# Kullanım: python manage.py shell → User.objects.get(username='testuser_a')

# Ratelimit cache'ini temizle (geliştirme sırasında limit dolunca)
python manage.py shell -c "
from django.db import connection
with connection.cursor() as c:
    c.execute(\"DELETE FROM django_cache_table WHERE cache_key LIKE '%rl:%'\")
    print(c.rowcount, 'kayıt silindi')
"
```

---

## 25. DEĞİŞMEZ KURALLAR (NON-NEGOTIABLES)

### KIRMIZI ÇİZGİ — Değişiklik Kısıtları (Claude için zorunlu)
1. **Kapsam dışına çıkma.** İstenen dosya/satır dışında hiçbir şeye dokunma. "İyileştirme" fırsatı görsen bile yapma — ayrı görev olarak sor.
2. **Birden fazla dosya değişecekse önce listele, onay al, sonra uygula.**
3. **Değişiklik yapmadan önce ilgili dosyayı oku.** Tahmin yürütme.
4. **Bir şeyi düzeltirken başka şeyi bozma.** Şüpheliysen sor.
5. **Her değişiklik sonrası dur ve onay bekle.** Tek seferde tek görev.

### Backend
1. ORM sorgularında `select_related()` / `prefetch_related()` kullan. N+1 sorgu yasaktır.
2. `conn_max_age=0` — long-running transaction'lardan kaçın.
3. Migration dosyaları üzerinden git — production DB'ye direkt dokunma.
4. `SECRET_KEY`, API key'leri, şifreler asla koda yazılmaz — `.env`.
5. E-posta env var'ları `SMTP_*` prefix'li — `EMAIL_HOST` gibi Django standartları değil.
6. `DATABASE_URL` env var'dan gelir — `DATABASES` doğrudan ayarlanmaz.
7. İstatistik servislerinde `conf_int()` sonucu her zaman `np.array()` ile sarılmalıdır — bazı statsmodels versiyonlarında ndarray, bazılarında DataFrame döner.
8. `result_data` JSONField'a kaydedilmeden önce `inf` / `nan` değerleri temizlenmeli (`'—'` veya `None`'a çevrilmeli) — aksi hâlde DB save patlar.

### Frontend CSS
1. Bootstrap yalnızca grid için: `container`, `row`, `col-*`.
2. UI elementleri `ax-` prefix'li özel CSS sınıflarıyla yazılır.
3. Yeni CSS yazarken `var(--ax-primary)` vb. token kullan — hardcode renk yazma.
4. Inline SVG tercih edilir (CDN ikonlar yerine, Bootstrap Icons CDN şimdilik kalıyor).

### Frontend JS
1. Vanilla JS ve Fetch API. React, Vue, Angular, jQuery yasaktır.
2. `data-bs-toggle` yerine vanilla event listener.
3. AJAX polling fetch'lerinde mutlaka `.catch()` handler eklenir — sessiz hata durumunda spinner sonsuz döner.
4. Polling URL'i `STATUS_TEMPLATE.replace(sentinel, jobId)` pattern'i ile kurulur (§12'ye bak).

### UX
1. Kullanıcıya görünen tüm metinler Türkçe ve akademik dile uygun.
2. Hata mesajları kullanıcı dostu — "500 Internal Server Error" değil, açıklayıcı Türkçe.
3. Dosya yükleme boyut sınırı: `MAX_UPLOAD_SIZE = 10MB`.

### Git
1. Commit mesajları Türkçe veya İngilizce: `feat:`, `fix:`, `refactor:` prefix kullan.
2. Her şehir/özellik bitiminde `main → dev` merge yapılır.
3. `.env` değerlerini commit'e dahil etme.

---

## 26. SIKÇA YAPILAN HATALAR VE ÇÖZÜMLERİ

| Hata | Çözüm |
|---|---|
| E-posta gönderilmiyor | `SMTP_HOST` kullan, `EMAIL_HOST` değil |
| DB bağlantı hatası (prod) | `DATABASE_URL` içindeki host Docker servis adı olmalı (`db`) — `localhost` container içinden çalışmaz; önce `docker compose up -d db` ile DB servisini başlat |
| Migration production'da çalışmadı | `docker compose exec web python manage.py migrate` |
| Statik dosyalar eksik | `python manage.py collectstatic` çalıştır |
| `budget_min` form validation hatası | `budget_min` formdan kaldırıldı (nullable) — form sadece `budget_max` bekler |
| Feature görünmüyor | `SiteSettings` admin'den ilgili flag'i `True` yap |
| AnalizBot bulunamadı | `User.objects.get(username='AnalizBot')` — sisteme bu kullanıcı eklenmeli |
| S3 yükleme başarısız | `AWS_S3_REGION_NAME=eu-north-1` (eu-central değil) |
| WebSocket bağlanmıyor | Nginx `/ws/` bloğunda `proxy_http_version 1.1` ve `Upgrade` header'ı kontrol et |
| Redis bağlantı hatası (`Connect call failed 127.0.0.1:6379`) | `.env`'de `REDIS_URL=redis://redis:6379` kullan — Docker'da `localhost`/`127.0.0.1` container dışına ulaşamaz; Render'dan kalan eski şifreli URL'i temizle |
| 502 Bad Gateway (web restart sonrası) | `docker compose restart web` sonrası **nginx da restart edilmeli**: `docker compose restart nginx`. Nginx, web container IP'sini başlangıçta cache'ler. Nginx conf'unda `resolver 127.0.0.11 valid=10s;` ve `set $backend http://web:8000;` bu sorunu kalıcı çözer. |
| Ödeme işlemi | iyzico **kullanım izni yok** — entegrasyon yapılmayacak; ödeme sistemi henüz belirsiz |
| Admin'de status elle değiştirildi, e-posta gitmedi / vitrin açılmadı | `status` alanları readonly — **list view → action** kullanılmalı. JobPayment: "Seçili ilanları vitrine ekle"; BibliometricOrder/AlexOrder: "Onayla ve Tam Rapor Emailini Gönder" |
| Donation geliri admin'de 0₺ gösteriyor | `status='completed'` filtresi — eski kod `'approved'` kullanıyordu (haziran 2026'da düzeltildi) |
| Vitrine Taşı butonu zaten vitrindekilerde görünüyor | `job.is_featured=True` veya `feature_status='pending'/'approved'` ise buton gizleniyor (haziran 2026'da düzeltildi) |
| `No module named 'statsmodels'` | `pip install statsmodels` (regresyon analizleri için zorunlu) |
| İstatistik polling 404 dönüyor | `STATUS_TEMPLATE.replace()` pattern'i kullan, `STATUS_BASE + jobId + '/'` değil (double slash üretir) |
| İstatistik "Sunucu hatası." (preview) | Ratelimit dolmuş (30/h) — cache temizle: `DELETE FROM django_cache_table WHERE cache_key LIKE '%rl:%'` |
| `conf_int().iloc` AttributeError | statsmodels `conf_int()` bazen ndarray döner — `np.array(model.conf_int())` kullan |
| Migration çakışması (`multiple leaf nodes`) | Sunucuda lokal `makemigrations --merge` ile oluşturulan dosya git'e eklenmemişse çıkar. Çözüm: sunucuda `python manage.py makemigrations --merge --no-input` → `migrate` → oluşan dosyayı lokale ekle, commit, push |
| Job spinner'da takılı, hata yok | `result_data` içinde `inf`/`nan` var, JSON save patlıyor — serviste `np.isinf()` kontrolü ekle |
| `check_array() got an unexpected keyword argument 'force_all_finite'` (AFA) | scikit-learn 1.6+ `force_all_finite` parametresini kaldırdı. **Çözüm:** `factor-analyzer==0.5.1` pin'le (`requirements.txt`); `istatistik/services/afa.py`'de `_patch_sklearn_compat()` monkey-patch shim çağrısı var — `analyze()` fonksiyonu başında çalışır. `docker compose up -d --build web` ile image yeniden build edilmeli (sadece restart yetmez). |
| OAI-PMH job sayfadan çıkınca duruyor | Eski tasarım raw `daemon=True` thread kullanıyordu — process exit/nav baskısına karşı korumasız. **Düzeltme:** `job_queue.enqueue('oaipmh', job_id)` ile merkezi ThreadPoolExecutor'a taşındı. Ek olarak stale cutoff 5 dk → 60 dk'ya çıkarıldı (19 üniversite taraması uzun sürebilir). |
| Session veri seti (lineer/lojistik regresyon) form gönderince kaybolıyor | DataTransfer API ile sentinel File inject edilir; fetch interceptor sentinel'i algılayıp `use_session=true`'ya çevirir. `analiz_console_base.html`'deki `DOMContentLoaded` handler üç JS konvansiyonunu da karşılar (`files[0]`, `._selectedFile`, `._file`). |
| `analytics/admin.py` 500 — `NameError: name 'username' is not defined` | `chart_view`'dan `?user=` filtresi kaldırılınca `if not username:` satırı düzenlenmemişti. Grafik sayfası artık tek modda çalışır (filtre yok), `top_users` + `per_user_data` her zaman hesaplanır. |
| `cleanup-pageviews` cron endpoint model uyumsuzluğu | `forum/api_views.py`'deki `cron_cleanup_pageviews` eski modele göre `unique_users` yazıyordu. `PageViewSummary`'ye `user` FK eklendikten sonra endpoint de `user_id` bazlı aggregate'e güncellendi. Her iki yer birlikte değiştirilmeli: `analytics/models.py` + `analytics/management/commands/cleanup_pageviews.py` + `forum/api_views.py`. |
| `PageViewSummary` admin'de user araması çalışmıyor | Model `user` FK içermiyordu, `search_fields = ['tab_name', 'path']` kullanıcı adını aramıyordu. Migration 0002 ile `user` FK eklendi, `search_fields`'e `user__username` eklendi. |
| AI anonim limit herkese uygulanıyor / "0/3 ama limit doldu" | Nginx arkasında tüm kullanıcılar aynı `172.x.x.x` internal IP'yi paylaşır — IP bazlı cache key tüm kullanıcıların kotasını tek sayaçta toplar. **Çözüm:** `ax_anon_id` UUID cookie (`max_age=86400`); her tarayıcının kendi sayacı olur. Session bazlı yapılmamalı: tarayıcı kapanınca sıfırlanır. |
| AI olmayan platform URL'si veriyor (`/istatistik/nitel/`, `/maxqda/` vb.) | `_sanitize_paths()` post-processing filtresi devrede ama `_ALLOWED_PATHS` listesine eklenmemiş olabilir. Kontrol: `ai_service.py`'de `_ALLOWED_PATHS` frozenset'e ilgili path'i ekle; yoksa sadece SYSTEM_PROMPT ile önlenemiyor — model kuralı bazen görmezden geliyor. |
| AI "Platform haritası örnek amaçlı / gerçek linkler farklı olabilir" diyor | Sistem prompt'un KESİN YASAKLAR bölümünde bu ifade açıkça yasaklı. Model yine de söylüyorsa `_sanitize_paths()` URL'yi sildiği için model bunu "uydurdu" sanıp özür diliyor. `_ALLOWED_PATHS`'e eksik path'i ekle — filtre URL'yi silmeyecek, model özür dilemeyecek. |
| `ProgrammingError: relation "django_cache_table" does not exist` | Render (veya yeni DB) ilk kurulumda cache tablosu oluşturulmamış. `python manage.py createcachetable` çalıştır. `deploy.sh`'e migrate'in hemen altına eklendi (haziran 2026). |
| YÖK Tez "9538 tez bulundu" ama veri nerede? | Bu sayı YÖK'ün sonuç sayacı — gerçek veri değil. S3'e yalnızca 5 demo tezin TXT özeti kaydedilir (`yoktez/demo/<job_id>.txt`). Tam veri indirme (~954 sayfa pagination, 3-6 saat) için otomatik akış henüz yok — `proje-talebi` linki ile manuel süreç işliyor. |
| `AttributeError: module 'django.utils.timezone' has no attribute 'utc'` | Django 5.2'de `django.utils.timezone.utc` kaldırıldı. `from datetime import timezone as _tz` ile Python'un kendi `_tz.utc`'sini kullan. |
| CSS değişikliği production'da görünmüyor (lokal tamam) | `static/css/*.css` içeriği değiştiğinde `<link href="...?v=XXXX">` versiyon stringi de güncellenmeli — nginx/tarayıcı `Cache-Control: max-age` ile eski dosyayı cache'den sunar. Lokalde fark edilmez: Django dev server nginx'ten geçmez. |
| `TemplateSyntaxError: Could not parse the remainder: '(request.user'` | Django template `{% if %}` parantezi desteklemiyor. `A and (B or C)` yerine iç içe `{% if A %}{% if B or C %}` kullan. |
| YouTube transcript — `TranscriptsDisabled` / bot hatası (sunucu) | Hetzner **ve Render** dahil cloud provider IP'leri YouTube tarafından engelleniyor (temmuz 2026'da Render'da da doğrulandı). Hem `youtube-transcript-api` hem `yt-dlp` başarısız olur. Çözüm: `feature_transcript` flag'ini kapalı tut (varsayılan), lokal script (`transcript_local.py`) kullan. |
| `ModuleNotFoundError` — `requirements.txt`'te olan paket bulunamıyor | Docker image, paket `requirements.txt`'e eklenmeden/güncellenmeden önce build edilmiş — `restart` image'ı değiştirmez. Çözüm: `docker compose build web` + `docker compose up -d web` (sadece `restart web` yetmez). |
| yt-dlp lokalde 403 / "n challenge solving failed" | İki şey gerekli: (1) JS runtime — `deno` kur: `curl -fsSL https://deno.land/install.sh \| sh`, PATH'e ekle; (2) solver script indir: `yt_dlp` opts'a `"remote_components": ["ejs:github"]` ekle (string değil list — string olursa karakter karakter parse eder). Ayrıca `"cookiesfrombrowser": ("firefox",)` ile tarayıcı cookie'si gerekli. |
| `ImportError: cannot import name 'list_available_languages'` | `youtube-transcript-api` v1.x'te bu fonksiyon kaldırıldı. Instance tabanlı API: `_ytt = YouTubeTranscriptApi()` → `_ytt.list(video_id)`. |
| `<label>` içine gömülü checkbox/radio'ya `click` listener bağlanınca çift tetikleme | Tarayıcı, label tıklamasını içindeki input'a yönlendirir ve bu sentetik click de label'a bubble eder — aynı tıklamada listener 2 kez çalışır, manuel `classList.toggle()` net etkiyi sıfırlar. **Çözüm:** listener'ı label'a değil input'un kendi `change` event'ine bağla, class'ı `checked` durumuna göre senkronize et (`toggle('selected', cb.checked)`). |
| `django_ratelimit` limit aşılınca özel hata sayfası gösterilmiyor | `Ratelimited` exception `PermissionDenied`'den türer; `settings.RATELIMIT_VIEW` gerçek bir Django/django-ratelimit ayarı **değildir**, hiçbir yerde okunmaz. Düzgün çalışması için `analizdestek/urls.py`'ye `handler403 = 'forum.views.ratelimit_error'` eklenmesi gerekir (DEBUG=False iken devreye girer) — şu an eklenmemiş, tüm `@ratelimit` view'ları (login, register, mesajlaşma vb.) tetiklenince Django'nun çıplak 403 sayfasını gösteriyor. **Henüz düzeltilmedi.** |
| CSS değişikliği hiçbir yerde görünmüyor (cache değil) | temmuz 2026'da `base.css`+`navbar.css`+`footer.css`+`style.css`+`sidebar_widgets.css` → tek `static/css/bundle.css`'de birleştirilip minify edildi (render-blocking istek sayısını azaltmak için); `templates/base.html:92` artık yalnızca `bundle.css`'i yüklüyor. 5 kaynak dosya diskte duruyor ama hiçbir template onlara referans vermiyor — birini düzenlemek sitede **hiçbir etki yaratmaz** (cache sorunu değil, dosya hiç okunmuyor). Yeniden üretmek için: 5 dosyayı aynı sırayla (base, navbar, footer, style, sidebar_widgets) birleştir + minify et, `bundle.css`'e yaz, `base.html:92`'deki `?v=` sürümünü artır. |
| Sayfa üzerinden `window.axOpenAiWidget()` ile açılan AI widget popup'ı anında kendi kendine kapanıyor | AI widget'ın `document`'a bağlı "dışarı tıklanınca kapat" click listener'ı, popup'ı açan chip/butonun click event'inin bubble fazında da tetikleniyor — `toggle()` açar, aynı event'in bubble'ında ikinci bir `toggle()` hemen kapatır (görsel flaş bile olmaz, tek tick içinde olur). **Çözüm:** widget'ın kendi kodunu değiştirme; `axOpenAiWidget()`'ı tetikleyen elemanın `onclick`'inde `event.stopPropagation()` çağır (ana sayfa AI soru chip'lerinde uygulanan pattern, `home.html`). |
| Ana sayfa hero dropzone'undan dosya "yüklendi" ama seçilen araç sayfasında veri gelmiyor | Dropzone dosyayı yalnızca `sessionStorage`'a (dosya adı) yazıp yönlendiriyorsa sunucuya hiç ulaşmaz — araç sayfaları anonim/session bazlı çalışır. **Doğru akış:** dosya gerçekten `POST /analiz/hero-upload/`'a `fetch` ile gönderilmeli; bu endpoint mevcut `save_session_dataset()` mekanizmasına yazar (`istatistik/services/job_runner.py`), ardından `/analiz/<slug>/` sayfaları `_console_ctx()`'teki `session_dataset_name` sayesinde dosyayı otomatik "seçili" gösterir (sentinel-File + DataTransfer JS pattern, `analiz_console_base.html`). **Not:** tüm araç sayfaları `if not request.user.is_authenticated: return service_promo.html` ile misafire kapalı — bu akış yalnızca giriş yapmış kullanıcı için gerçek anlamda çalışır. |
| Yeni `SiteSettings` feature flag admin panelinde hiç görünmüyor | `SiteSettingsAdmin.fieldsets` (`forum/admin.py`) her flag'i elle listeler — model alanı + migration eklense bile `fieldsets`'teki `'fields': (...)` tuple'ına eklenmezse admin formunda hiç render edilmez (model DB'de kayıtlı ama arayüzden değiştirilemez). Yeni flag eklerken **üç yeri birlikte** güncelle: `SiteSettings` modeli + `feature_flags()` context processor + `SiteSettingsAdmin.fieldsets`. |
| Django dev server (`runserver`, ASGI/Daphne) `curl` ile hemen bağlanmıyor (`Connection refused`) | Arka planda başlatılan `manage.py runserver` süreci ~5 saniye içinde port'a bind ediyor (system check + ASGI/Daphne başlatma gecikmesi); 1-2 saniyelik `sleep` sonrası test etmek yanlış negatif verir. Ayrıca `manage.py runserver` autoreload modunda watcher+worker olmak üzere **iki ayrı process** açar — sadece watcher PID'i `kill` etmek worker'ı öldürmez, arka planda biriken zombi süreçler yeni test portlarını meşgul edebilir. Yerel smoke test için `--noreload` kullan, tek process kalır, `pkill -f "manage.py runserver"` ile temizle. |
| `/istatistik/<slug>/` gibi "eski/legacy" görünen bir route'u toptan 301'e çevirince analiz gönderimi bozulur | Bu rotalar yalnızca eski giriş sayfası değil — 18 istatistik aracının HEPSİNDE aynı zamanda POST (analiz gönderimi) hedefi: JS'teki `TOOL_URL`/fetch her zaman `{% url "istatistik:X" %}` isimlendirmesini kullanıyor (entry `/analiz/` veya `/istatistik/` olsun fark etmez). Naif bir `RedirectView`/blanket 301 bu POST'ları da yakalar ve analiz asla çalışmaz. **Çözüm (temmuz 2026):** method-aware wrapper — yalnızca `request.method == 'GET'` ise 301 `/analiz/<slug>/`'e; POST ise view'a değişmeden devam. `/status/<job_id>/` polling endpoint'leri de aynı sebeple hiç dokunulmadı (tek çalışan implementasyon `/istatistik/` altında). Genel ders: bir route'u "sadece eski giriş noktası" sanıp yönlendirmeden önce, o route'u üreten template'teki TÜM `{% url %}`/`fetch` kullanımlarını (form submit, polling, AJAX) grep'le doğrula — GET-only landing page varsayımı yanlış olabilir. |
| `TOOL_CATEGORIES` (istatistik/views.py) gibi paylaşılan bir sidebar/nav veri yapısı sessizce en çok tıklanan linkleri üretiyor olabilir | `analiz_console_base.html` sidebar'ı (18 araç sayfasının HEPSİNDE görünür) ve `analiz_hub.html` grid'i aynı `TOOL_CATEGORIES` listesindeki 5. tuple elemanını `{% url %}` ile çözüyordu — bu eleman `istatistik:X` namespace'li isimdi, yani her tıklama `/istatistik/`'e gidiyordu (site genelinde tek en yüksek hacimli iç link kaynağı). Bir prefix'i "kaldırıyoruz" derken yalnızca doğrudan grep sonuçlarına güvenme — Python içinde tuple/dict olarak saklanan URL isimleri de tara (`grep "istatistik:"` hem `.py` hem `.html` dosyalarında). |

---

## 27. GÖREV LİSTESİ (Mevcut Durum)

### Tamamlananlar
- Tüm istatistik araçları: Cronbach Alpha, Normallik, Betimsel, Korelasyon, t-Testi, ANOVA, Örneklem
- Mann-Whitney U ve Kruskal-Wallis H testleri
- Ki-Kare + Fisher's Exact Test
- **Çoklu Doğrusal Regresyon (OLS)** — R², β, VIF, APA raporu
- **Lojistik Regresyon (Binary)** — Nagelkerke R², OR, sınıflandırma tablosu, APA raporu
- Tüm analiz PDF'lerine "Tezinde Nasıl Raporlarsın?" APA bölümü eklendi
- Analizler menüsü kategorilere ayrıldı (5 kategori)
- **Korelasyon sütun seçimi** — Cronbach ile aynı iki adımlı akış (preview → sütun seç → run)
- Admin e-posta bildirim sistemi (tüm event'ler + araç Türkçe isimleri)
- Bot koruması (honeypot + username regex + rate limit)
- İlan düzenleme hakkı (1 kez, teklif yokken)
- İlan iptal → bekleyen teklif verenlere DM
- Yeni teklif → ilan sahibine e-posta
- İş ilanı formunda minimum bütçe alanı kaldırıldı (yalnızca maksimum bütçe giriliyor)
- Başarı hikayeleri, rozet, quiz sistemi
- **Dosya paylaşımı (DM + Çalışma Odaları)** — PDF, Word, Excel, PPT, CSV, TXT, resim; max 5 MB; S3'e yüklenir; mesaj/oda silinince dosya da silinir (post_delete signal)
- **Destekçi / Bağış sistemi** — Footer widget, modal (DonationTier seçimi), IBAN e-postası; `donation_context` processor ile her sayfada tier listesi mevcut; migration `0076_seed_donation_tiers` (4 tier)
- **SEO iyileştirmeleri** — Nginx non-www→www 301 yönlendirmesi; sitemap genişletmesi (blog, 12 istatistik aracı, 5 landing page); 18 sayfaya benzersiz meta description; 6 title güncellendi; IndexNow entegrasyonu (Bing); Google Search Console `https://www.analizus.com/` property eklendi + sitemap submit edildi
- **YÖK Tez birleştirme** — `/tezanaliz/` + `/yoktez/` tek çatıda birleştirildi; tüm işlevler `/yoktez/` altında; `/tezanaliz/*` 301 redirect; navbar'da tek "YÖK Tez" girişi
- **Veri kazıma filter audit** — OAI-PMH `search_keyword` tez filtresi (`_is_thesis`, dc:type boş=dahil et); YÖK Tez `_search_legacy` yıl/üniversite/tür lokal filtreleri; TR Dizin ve OpenAlex temiz bulundu
- **OAI-PMH iyileştirmeleri** — özet (dc:description) arama alanı kaldırıldı (OAI-PMH'de boş geliyor, 0 sonuç üretiyordu); "Analiz Yap" butonu kaldırıldı (makaleanaliz'e yanlış yönlendiriyordu)
- **YÖK Tez UX** — job state kalıcılığı: arama başlayınca sayfadan ayrılıp dönünce form dolu gelir, tamamlanan job 24 saat boyunca otomatik gösterilir; scraper hız iyileştirmesi (detay gecikmesi 2-4.5s→0.8-2.0s, erken çıkış: 5 demo dolunca durur, kandidat limiti 10x→5x)
- **Nginx Docker DNS resolver** — `resolver 127.0.0.11 valid=10s;` + `set $backend http://web:8000;` eklendi; web restart sonrası 502 sorunu giderildi
- **Unified Analiz Konsolu** (mayıs 2026) — 16 istatistik aracı tek sidebar'lı konsolda; `/analiz/<slug>/`; `analiz_console_base.html` + `analiz_console.css`; navbar'da flyout menüler kaldırıldı, tek "İstatistik Analiz Araçları" linki
- **Akademik Tarama Unified Console** (mayıs 2026) — 4 tarama aracı `tarama_console_base.html` altında; `/tarama/` giriş noktası (→ `/yoktez/` redirect); sidebar feature flag koşullu
- **Navbar sadeleştirme** (mayıs 2026) — Forum linki kaldırıldı; Blog → Kurumsal dropdown'a taşındı; Hizmetler → Pazaryeri olarak yeniden adlandırıldı; Araçlar flyout menüsü → Analizler dropdown (tek `/analiz/` linki); Akademik Tarama direkt link oldu
- **OAI-PMH job_queue entegrasyonu** (mayıs 2026) — Raw `threading.Thread` → `job_queue.enqueue('oaipmh')`; stale cutoff 5 dk → 60 dk; `job_queue.py`'de `oaipmh` case eklendi
- **AFA sklearn 1.6+ uyumluluğu** (mayıs 2026) — `factor-analyzer==0.5.1` pin'lendi; `afa.py`'de `_patch_sklearn_compat()` monkey-patch shim eklendi
- **Session veri seti kalıcılığı** (mayıs 2026) — Çoklu Doğrusal Regresyon + Lojistik Regresyon: DataTransfer API + sentinel file + fetch interceptor; `analiz_console_base.html`'de tüm üç JS konvansiyonu destekleniyor
- **İstatistik Rehberi eksik linkler** — `hangi_test.html`'de `r_tekrarli_anova` ve `r_friedman` düğümlerine `tool_url` eklendi
- **YÖK Tez geçmiş analizler** — Scrollable container (`max-height:260px`) + queryset `[:8]→[:5]`; liste aşağı uzayıp gitmiyor
- **Mobil navbar** — Drawer'da eski 16 ayrı analiz linki → tek `/analiz/` linki
- **Çevrimiçi göstergesi** (mayıs 2026) — `Profile.is_online` property (son 5 dk kontrolü); `LastSeenMiddleware` her istekte `last_seen` günceller (60s throttle); profil sayfası + tüm profil kartları + sohbet + hikaye modallarında koşullu yeşil nokta; hover tooltip "Çevrimiçi"
- **Kayıt formu autocomplete** (mayıs 2026) — `autocomplete="new-password"` (parola alanları) + `username`/`email` attribute'ları eklendi; tarayıcı otomatik doldurma engellendi
- **Çift mesaj düzeltmesi** (mayıs 2026) — Gönder butonu `type=submit` → `type=button`; `trySend()` tek giriş noktası (buton click + Enter); `messageForm.submit()` fallback (upload hata → ikinci kayıt) kaldırıldı
- **Gelen Kutusu konuşma listesi** (mayıs 2026) — Sadece alınan değil, gönderilen + alınan tüm konuşmalar listeleniyor (`Q(sender=user) | Q(receiver=user)`); konuşma ortağı dinamik tespit edilir
- **Inbox "diğerlerini göster"** (mayıs 2026) — İlk 5 konuşma görünür, fazlası `d-none`; "Diğer N konuşmayı göster" butonu tıklanınca sayfa yenilemesiz açılır
- **Karar Ağacı (ML)** (mayıs 2026) — Unified konsolda "Makine Öğrenmesi" kategorisi altında; `karar_agaci.py`; sklearn DecisionTreeClassifier; feature_importances_ ile önem sıralaması; PDF çıktısı
- **Destek Vektör Makinesi (SVM)** (mayıs 2026) — `svm.py`; SVC + StandardScaler; RBF/Linear/Poly kernel; C parametresi 0.1–10; permutation_importance (model-agnostik); büyük dataset otomatik örnekleme (5000 satır); PDF çıktısı
- **Mesaj düzenleme / silme / sohbet silme** (mayıs 2026) — Inline edit (textarea), soft delete (`is_deleted=True, message=''`), conversation hard delete; `_broadcast_chat` + `_chat_room_name` view helper'ları; ChatConsumer'a `message_edit`, `message_delete`, `conversation_delete` handler'ları eklendi; WS broadcast ile karşı taraf anlık güncellenir; poll API `is_deleted=False` filtresi eklendi
- **DM okundu göstergesi** (mayıs 2026) — Gönderen kendi mesajı altında `✓` (gri, iletildi) veya `✓✓` (cyan, okundu) görür; `consumers.py`'de `connect` + `chat_message` handler'ında `mark_messages_read` / `mark_single_message_read` DB çağrısı + `messages_read` WS event broadcast; `send_message.html`'de template (mevcut mesajlar) ve `appendMessage` JS (yeni mesajlar) güncellendi; JS `messages_read` event handler `data-own="1"` mesajlarını anlık günceller. **Düzeltme:** `sendMessage` AJAX callback'inde `appendMessage` çağrısına `id: data.id` eklenmedi — balonun `data-msg-id` boş kalıyordu, `messages_read` eventi mesajı bulamıyordu; sayfa yenilemeden `✓✓` gösterilmiyordu.

- **SEO — Hub sayfaları + promo içerik** (mayıs 2026)
  - `/analiz/` → `analiz_hub`: 18 aracı kategorili listeler (guest görebilir, Google index'ler)
  - `/tarama/` → `tarama_hub`: 4 akademik tarama aracını listeler
  - `service_promo.html`: `seo_guide` varsa intro + accordion + SSS bloğu render eder
  - 17 istatistik aracı + yoktez/oaipmh/openalex/trdizin/bibliometrics promo context'lerine `seo_guide` eklendi
  - `tarama_seo_content.py`'ye `bibliometrics` ve `tableau` girişleri eklendi
  - Tableau sayfası: meta description, intro paragraf, tab açıklamaları, accordion + SSS SEO bloğu
  - `robots.txt` genişletildi: `/login/`, `/logout/`, `/accounts/`, `/register/`, `/forum/*/new|edit|delete`, `/market/new|*/edit`, `/blog/create|*/edit`, `/odalar/ac/`, `/studyroom/*/katil/`, `/analiz/clear-session/` engellendi
  - `istatistik/views.py` `_SLUG_MAP` eksik `svm` eklendi (404 düzeltmesi)

- **Semantic Scholar yayın kazıma modülü** (mayıs 2026) — `semanticscholar/` Django uygulaması; Semantic Scholar Graph API + CrossRef zenginleştirme; arama formu, job kuyruğu, Excel/TXT indirme, e-posta, sipariş akışı; feature flag, navbar, sitemap, robots.txt, tarama_hub entegrasyonu; SEO içerikleri
- **WoS Plain Text (ISI) parser** (mayıs 2026) — `bibliometrics/services/parser.py`'e `_parse_wos_txt()` eklendi; `FN/VR` başlıklı ve başlıksız format, çok satırlı alan desteği
- **Çalışma Odası mesaj düzenleme / silme** (haziran 2026) — `StudyRoomPost`'a `edited_at` alanı (migration 0120); `/api/room-post/<id>/edit|delete/`; hover ile ✏️/🗑️ ikonları, inline textarea; hard delete (S3 signal); `(düzenlendi)` etiketi
- **Çalışma Odası @mention e-postası** (haziran 2026) — `email_utils.notify_room_mention()`; etiketlenen oda üyesine async e-posta; tüm üyelere değil
- **Migration çakışması düzeltmesi** (haziran 2026) — sunucuda lokal kalan `0119_alter_sitevisit_id`, `0120_merge_20260530_2123`, `0121_merge_20260601_1555` dosyaları git'e eklendi
- **YÖK Tez / TR Dizin → Proje Talebi entegrasyonu** (haziran 2026) — email footer + landing page "info@analizus.com" → `/proje-talebi/?source=yoktez|trdizin`; `ProjectRequest` modeline `source` field (yoktez/trdizin/direct) + `SOURCE_CHOICES`; `ANALYSIS_CHOICES`'a "Tez / Makale Veri İndirme" eklendi; kaynağa göre analiz türü form'da otomatik seçili; admin'e `source` filtresi + sütunu; "Şirket/Kurum" → "Kişi/Şirket/Kurum"; migration `0126`
- **deploy.sh createcachetable** (haziran 2026) — Render'da `django_cache_table does not exist` hatası; `deploy.sh`'e `python manage.py createcachetable` eklendi (migrate'in hemen altına; idempotent — tablo varsa sessizce geçer)
- **SEO — GSC index hataları düzeltmesi** (haziran 2026) — `robots.txt`'e `Disallow: /istatistik/` ve `Disallow: /jobs/` eklendi; `/istatistik/<araç>/` URL'leri canonical olarak `/analiz/<araç>/`'a işaret ediyor ama Google her iki prefix'i de tarıyordu (33 "Alternative page with canonical" hatası); `blog_list.html` canonical'den `?category=` parametresi kaldırıldı — filtreli blog sayfaları artık `/blog/`'a canonical işaret ediyor
- **Ödeme/sipariş admin düzeltmeleri** (haziran 2026) — `JobPayment.status` readonly yapıldı; `approve_feature` action `status='success'` ama `feature_status='pending'` olan kayıtları da işler; gerçek işlenen sayı mesajı düzeltildi; `Donation` modeline `pending_confirmation` status eklendi (migration 0122); `send_support_email` artık DB kaydı oluşturuyor; `mark_donation_transferred` view + URL eklendi; e-posta şablonuna "Havaleyi Yaptım" butonu eklendi; `AlexOrderProxy` + `AlexOrderAdmin` eklendi (`openalex/admin.py`) — dashboard linki düzeltildi (404 veriyordu); `BibliometricOrder.status` readonly yapıldı; Gelir Özeti'ne vitrin + biblio + openalex aylık/toplam gelir eklendi; bağış filtresi `'approved'`→`'completed'` düzeltildi; Vitrine Taşı butonu zaten vitrindekilerde gizleniyor
- **Kullanıcı navigasyon analizi** (haziran 2026) — `analytics/` Django uygulaması; `PageView` (ham log, 5 gün TTL) + `PageViewSummary` (kalıcı özet, user FK ile); `PageViewMiddleware` login'li kullanıcıların GET 200 isteklerini loglar (`/static/`, `/admin/`, `/api/` vb. atlanır); URL → Türkçe sekme adı eşleştirmesi (`analytics/utils.py`); admin'de kullanıcı bazlı liste + `/admin/analytics/pageview/grafik/` Chart.js sayfası — "En Aktif Kullanıcılar" bar'ına tıklanınca üstteki "En Çok Ziyaret" + "Günlük Trend" grafikleri sayfa yenilemesiz in-place güncellenir, seçili kullanıcı badge ile gösterilir, tekrar tıklanınca filtre sıfırlanır; `PageViewSummary` user FK'lı (migration 0002), user bazlı arama admin'de çalışır; `cleanup_pageviews` management command + `/api/cron/cleanup-pageviews/` endpoint (her ikisi de user_id bazlı aggregate); Hetzner crontab'ında `0 4 * * *`
- **Semantic Scholar e-posta revizyonu** (haziran 2026) — demo email OpenAlex ile hizalandı; "info@analizus.com'a yaz" kaldırıldı, sipariş sayfası linki eklendi; S3 linki varsa ek gönderilmez (OpenAlex pattern)
- **İş ilanı kategorileri bağımsızlaştırıldı** (haziran 2026) — `JobCategory` modeli eklendi; `FreelanceJob.category` artık forum `Category`'ye değil `JobCategory`'ye bağlı; admin → İş Kategorileri menüsünden yönetilir; sidebar `settings.py` `UNFOLD.SIDEBAR.navigation`'dan kontrol ediliyor; migration `0124_job_category_independent`
- **SEO — GSC "Alternative page with canonical tag" 30 sayfa düzeltmesi** (haziran 2026) — `blog_list.html`: kategori-only sayfalar (`/blog/?category=xyz`) self-referencing canonical → Google index'ler; sayfalama + level filtresi + arama sayfaları → `noindex, follow`; `uzman_dizini.html`: skill sayfaları (`/uzmanlar/?skill=nvivo`) self-referencing canonical; boş skill param (`/uzmanlar/?skill=`) → view'da 301 redirect `/uzmanlar/`'e; trailing `&` URL'leri (`/blog/?category=xyz&`) → `blog_list` view'da 301 redirect ile temizleniyor.
- **AI Asistan iyileştirmeleri** (haziran 2026) — Platform-aware `SYSTEM_PROMPT`: tüm araçlar + URL'ler dahil, kullanıcıyı doğru sayfaya yönlendirir; `@login_required` kaldırıldı, anonim erişim açıldı (3 soru/gün); üye limiti 10 → 30 soru/gün; `POST /api/ai/chat/` JSON API endpoint eklendi; `base.html`'e mobil-önce floating chat widget (WhatsApp tarzı — desktop 350×480px, mobil full bottom-sheet 72dvh, typing indicator, tıklanabilir platform linkleri `→ Ad (/url/)` regex dönüşümü, Enter=gönder, textarea auto-grow); tam sayfa: cevap gelince smooth scroll + textarea clear; `/proje-talebi/` URL sistem prompt'a eklendi; `robots.txt`'e `/ai-asistan/` eklendi.
- **AI Asistan güvenlik/kalite katmanları** (haziran 2026) — Anonim rate limiting IP → `ax_anon_id` UUID cookie'ye taşındı (`max_age=86400`, HttpOnly) — Nginx arkasındaki shared IP sorununu çözdü; `_CJK_RE` post-processing: Llama'nın Çince/Japonca karakter karıştırmasını engeller; `_sanitize_paths()` post-processing: `_ALLOWED_PATHS` frozenset dışındaki her platform URL'sini yanıttan kaldırır (hallüsinasyon önlemi); sistem prompt KESİN YASAKLAR güncellendi: sahte uzman adı yasağı, iç kural sızdırma yasağı, "linkler örnek amaçlı" yasağı, CJK karakter yasağı.
- **Profil gizlilik — Verilen Teklifler** (haziran 2026) — Başkasının profilinde "Verilen Teklifler" bölümü (fiyat + red durumu) gizlendi; yerine son 5 tamamlanan proje fiyatsız listeleniyor; kendi profilinde "Verdiğim Teklifler" adıyla görünmeye devam eder; "Reddedildi" → "Kabul Edilmedi" (kırmızı renk korundu); `posted_jobs` limiti 20→5; `given_proposals` sadece `is_owner=True` iken sorgulanıyor; `is_owner` context'e eklendi
- **Profil + Pazar ilanları hata düzeltmeleri** (haziran 2026) — 3 bug: (1) "Tamamlanan Projeler" badge'i her zaman "Tamamlandı" yazıyordu → `proposal.job.status` ile doğru durum gösteriliyor; (2) `job_detail.html` "Başarı Hikayenizi Paylaşın" butonu tüm giriş yapmış kullanıcılara açıktı → iş sahibi veya `accepted_proposal.expert` ile kısıtlandı; (3) `TemplateSyntaxError` — Django template parantezi desteklemiyor, iç içe `{% if %}` ile düzeltildi; `profile_detail` İlanlar sekmesi "Tamamlanan Projeler" → "Tamamlanan ve Devam Eden Projeler"; "Reddedildi" → "Kabul Edilmedi" (`job_detail` teklif listesinde); `completed_projects` sorguya `prefetch_related('job__reviews')` eklendi (N+1 önleme); İlanlar sekmesindeki proje linkleri kaldırıldı (gizlilik — Portföy sekmesiyle çelişiyordu), alınan yıldız değerlendirmesi gösteriliyor
- **Hesap silme akışı** (haziran 2026) — KVKK uyumlu email onaylı silme: `/account/delete/` (onay sayfası) → `/account/delete/confirm/<token>/` (24 saat geçerli token, hesabı `is_active=False` yapar); 30 gün sonra `/api/cron/process-account-deletions/` cron endpoint'i anonimleştirme + DM silme yapar; Profile modeline `deletion_requested_at`, `deletion_token`, `deletion_token_expires_at` eklendi (migration `0127`); profil sayfasına "Hesabımı Sil" butonu eklendi (sadece `is_owner`)
- **Navbar yeniden düzeni** (haziran 2026) — "Proje Talebi" Kurumsal dropdown'dan çıktı → bağımsız navbar linki; "Forum" (`/forum/`) Kurumsal dropdown'a ilk sıra olarak eklendi; mobil drawer da aynı şekilde güncellendi
- **Forum @mention — yeni konu formu** (haziran 2026) — `new_topic.html`'e yanıt formundakiyle aynı @mention autocomplete eklendi (`/api/users/search/` endpoint, ok/tab/esc klavye navigasyonu, avatar dropdown)
- **Forum topic_detail DM stili** (haziran 2026) — "Cevap Yaz" büyük bölümü → compact inline input (DM'deki gibi tek satır textarea + send butonu); mesaj balonları solid renk → gradient+border stiline güncellendi; AI Yanıt Öner butonu alt satıra taşındı; `#chat-kutusu` sabit yükseklik (`calc(100vh-340px)`) kaldırıldı — mesajlar doğal yükseklikte akıyor
- **Forum index kompakt kartlar + aktivite sıralaması** (haziran 2026) — Section içinde kategoriler `last_post_at` azalan sırada (en son yazışma önce, hiç konu olmayanlar sona); kart yüksekliği ~50% azaltıldı: ikon + başlık + sinyaller tek satırda, açıklama 2. satıra küçük font; sinyal sayıları kısaltıldı (rakam+ikon, etiket yok); `django.utils.timezone.utc` → `datetime.timezone.utc` (Django 5.2 uyumluluğu)
- **SEO — GSC indexing sorunları (canonical/noindex/CTA)** (haziran 2026):
  - `uzman_dizini.html`: `?skill=` veya `?sort=` parametreli sayfalar → `noindex, follow` (canonical `/uzmanlar/`'a işaret ederken robots `index` kalıyordu — 31 "Alternative page" hatasının kaynağı)
  - `blog_list.html`: `request.GET.page` koşulu eklendi — `?page=1` de artık `noindex` (önceden `has_previous=False` olduğu için yanlışlıkla index'leniyordu)
  - `studyroom_list.html`: canonical block (`{% url 'studyroom_list' %}`) + robots_content block eklendi — `/odalar/?kategori=...` filtrelenmiş URL'ler `noindex, follow`
  - `proje_talebi` view + template: stats bar (tamamlanan analiz / üye sayısı — DB'den dinamik) + sağ kolona "Son Tamamlanan Analizler" kartı (anonimleştirilmiş, `FreelanceJob.updated_at - created_at` → gün/hafta etiketi)
  - `analiz_console_base.html`: 18 analiz aracının altına "Bu analizi uzmanına bırakmak ister misiniz?" CTA eklendi (`?source=tool` parametresi ile proje talebi iç link); `ProjectRequest.SOURCE_CHOICES`'a `('tool', 'Analiz Aracı')` eklendi; migration `0128_projectrequest_source_tool` (no-op — DB şeması değişmiyor)
- **YouTube Transcript altyapısı kuruldu, menüden kaldırıldı** (haziran 2026) — `transcript/` Django uygulaması: `TranscriptSettings` singleton (admin maks dakika), `TranscriptJob` modeli, `youtube-transcript-api` v1.x servisi (dil önceliği: tr→de→en→otomatik çeviri), download/e-posta teslim, job_queue entegrasyonu; `transcript_local.py` standalone script (yt-dlp + faster-whisper "small" modeli, CPU int8). **Sunucuda çalışmıyor:** Hetzner cloud IP YouTube tarafından engelleniyor — hem `youtube-transcript-api` hem `yt-dlp` 403/bot hatası alıyor. Menü linkleri kaldırıldı; backend kod ve migration'lar yerinde duruyor. Lokal script kendi IP'den çalışıyor.
- **SEO — 36 blog yazısı 800+ kelimeye genişletildi** (haziran 2026) — GSC "Crawled - currently not indexed" sorunu için tüm blog yazıları data migration ile genişletildi; 3 batch, 11 migration (0130–0140); her yazıya akademik Türkçe h2 bölümleri, tablolar, APA örnekleri eklendi; içerik `<hr>` referans ayracından önce insert edildi (`content.rfind('<hr>')` pattern); kelime sayımı `re.sub(r'<[^>]+>', ' ', content).split()` ile yapıldı (HTML tag'leri soyularak)
- **SEO — Landing page tarama keyword'leri** (haziran 2026) — `yoktez/landing.html`, `trdizin/landing.html`, `oaipmh/landing.html` güncellendi; title + H1 + meta_description + meta_keywords'e "tez tarama", "yök tez tarama", "yök tez arşiv", "trdizin tarama", "üniversite tez tarama" varyasyonları eklendi; her sayfanın altına görünür keyword paragrafı eklendi (Google'a on-page sinyal); hedef: "yök tez arşiv" (boşluklu) ve "tez tarama" aramalarında sıralama almak
- **Backlink / Domain Authority** (haziran 2026) — Bing Webmaster "not enough inbound links" uyarısı üzerine: (1) AlternativeTo.net başvurusu yapıldı (22 Haz, 7 gün bekleme); (2) Product Hunt lansmanı planlandı ve form dolduruldu (13 saat 48 dk'ya launch zamanlandı); gallery için 4 ekran görüntüsü (`/tmp/ph_*.png`) + 14 saniyelik demo video (`/tmp/analizus_demo.mp4`) üretildi; yatırımcı formu dolduruldu; launch tags: Productivity, Education, No-Code
- **YouTube içerik planı** (haziran 2026) — 4 video planlandı: Genel tanıtım (2-3 dk, hook+platform turu+CTA), YÖK Tez tutorial, İstatistik araçları tutorial, TR Dizin tutorial; demo video `/tmp/analizus_demo.mp4` (14 sn, ana sayfa + istatistik scroll)
- **Ana sayfa tasarım iyileştirmeleri — "Sihirli Dokunuş"** (haziran 2026)
  - **Hero mesh gradient:** `hero.css`'te `::after` 3 asimetrik radial-gradient blob (indigo %18 + violet %14 + indigo %10); eski tek blob'un yerini aldı
  - **Gradient text başlık:** `<mark>` elementleri `background: linear-gradient(135deg, #818cf8→#a78bfa→#c084fc)`; `-webkit-background-clip: text`; `hero.css`'te tanımlı — HTML içindeki inline style kaldırıldı
  - **Card hover glow:** `.ax-card:hover` → indigo border (`rgba(99,102,241,0.45)`) + glow shadow (`0 0 24px rgba(99,102,241,0.18)`) + `transform: translateY(-2px)`; `base.css`
  - **Noise overlay:** `.ax-noise-overlay` site geneli subtle grain texture (SVG feTurbulence base64 data-URI, `opacity: 0.025`, `position: fixed`); `base.html` body hemen altında tek div; `base.css`
  - **Market kartları SVG görselleri:** Sol kart (çalışma ilanı) — 3 monitör sahnesi indigo renkli; sağ kart (uzman) — kitaplar + Σ sigma + veritabanı silindirleri amber/gold renk; `home_sections.css`'te `.ax-market-visual` sınıfı; mobile (`max-width:767px`) `display:none`
  - **Market kartı metinleri güncellendi:** Sol → "Tezinizden makaleye, SPSS analizinden Python projesine — alanında doğrulanmış uzmanla dakikalar içinde eşleşin. %100 gizlilik, sürprizsiz fiyat." / Sağ → "SPSS, R, Python veya alan uzmanlığınızı gerçek akademik projelere dönüştürün. Komisyonsuz çalışın, akademik itibarınızı büyütün."
- **`analytics/middleware.py` polling URL regex genişletildi** (haziran 2026) — `r'/status/[0-9a-f\-]{36}/'` → `r'/status/([0-9a-f\-]{36}|\d+)(/api)?/'`; transcript status polling endpoint'leri de kapsıyor
- **Logo ve OG görseli yenilendi** (haziran 2026) — Navbar'daki inline SVG bar-chart logo + "Analizus" span kaldırıldı; `static/img/analizus-logo-001.png` (yuvarlak rozet stili) eklendi; `base.html` desktop + mobile logo `<img class="site-nav__logo-img">` tag'ine döndü; `navbar.css`'e `.site-nav__logo-img { height:40px; border-radius:50%; }` eklendi; favicon `favicon.svg` → `static/img/analizus-logo-001.png` (PNG); OG/Twitter image için 1200×630 koyu banner (`static/img/og-banner.png`) Pillow ile üretildi (logo sol + "Analizus / Analiz Ekosistemi / www.analizus.com" sağda); `og:image`, `twitter:image`, JSON-LD `logo` güncellendi; `navbar.css?v=0103` cache buster artırıldı. Deploy: `collectstatic` + `docker compose restart web` gerekli. LinkedIn önizlemesi için Post Inspector ile cache temizlenmeli.
- **Onboarding yeniden tasarımı + login/hesap güvenliği düzeltmeleri** (temmuz 2026)
  - Onboarding adım 2/3 (ilgi alanı/araç seçimi) checkbox'larında çift tetikleme bug'ı: label'a bağlı `click` listener + tarayıcının input'a yönlendirdiği sentetik click aynı anda 2 kez tetikleniyor, seçim görsel olarak işlemiyordu → listener `change` event'ine taşındı (bkz. §26)
  - Onboarding adım 2/3 tamamen yeniden tasarlandı: artık seçim yapılan checkbox değil, salt bilgilendirme ekranı — adım 2 platform imkanlarını (istatistik analizi, veri kazıma & toplama, danışmanlık, proje desteği, akademik destek, bibliometrik analiz, akademik tarama, forum) icon+açıklama satırları olarak listeler; adım 3 desteklenen araçları (SPSS, R, Python, Excel, SmartPLS, AMOS, Stata, NVivo, MAXQDA, AI Araçları) rozet olarak gösterir; `onboarding_interests`/`onboarding_tools` artık toplanmıyor (model alanları duruyor ama boş kalıyor, migration gerekmedi)
  - Referral (davet) sistemi keşfedilebilirliği: sistemin kendisi tamamlanmış olsa da hiçbir yerde linki/bahsi yoktu (yalnızca admin sidebar'da) — navbar profil dropdown'una (masaüstü + mobil drawer) "Arkadaşını Davet Et" linki (`referral_dashboard`) ve hoş geldin e-postasına (`welcome_email.html`) 🎁 madde eklendi
  - Login açık yönlendirme (open redirect) güvenlik açığı: `custom_login`'de `next` GET parametresi doğrulanmadan `redirect()`'e veriliyordu → `url_has_allowed_host_and_scheme()` ile doğrulanıyor, güvenli değilse `home`'a düşer
  - Hesap silme onayı (`account_delete_confirm`) 3 durumda da (geçersiz token, süresi dolmuş token, başarılı silme) `forum_index`'e yönlendiriyordu → `home`'a düzeltildi
  - `send_message`: hesabını silmiş (`is_active=False`) bir kullanıcıya artık mesaj gönderilemiyor — "Bu kullanıcı hesabını sildiği için mesaj gönderilemiyor" hatasıyla inbox'a yönlendirilir (admin dahil hiç kimse deaktif hesaba DM atamaz)
  - **Düzeltilmedi, bilinen açık:** `django_ratelimit` limit aşımı özel hata sayfası göstermiyor (bkz. §26); login honeypot alanı (`website`) sunucu tarafında kontrol edilmiyor, sadece dekoratif
- **Mobil PageSpeed performans iyileştirmesi** (temmuz 2026) — Google PageSpeed Insights: mobil Performans 58→61 (LCP 11.0sn→5.5sn), masaüstü 73→94 (LCP 2.1sn→1.2sn)
  - Google Fonts + Bootstrap CDN CSS render-blocking'den kurtarıldı: ikonlarda zaten kullanılan `media="print" onload="this.media='all'"` deseni + `noscript` fallback uygulandı (`base.html`)
  - 5 preconnect → 1'e indirildi (yalnızca `fonts.gstatic.com`), gerisi ucuz `dns-prefetch` (Lighthouse "4'ten fazla preconnect" uyarısını gideriyor)
  - Navbar logosu (`static/img/analizus-logo-001.png`) 1024×1024/1.17MB → 200×200/48KB küçültüldü — 40px'te gösterilen görsel ~26x fazla piksel taşıyordu; "image delivery" bulgusunun (1148 KiB) neredeyse tamamı bu tek dosyaydı. Navbar `<img>`'lara `width` eklendi (CLS önleme)
  - **Bilinçli ertelendi (kullanıcı kararı):** Bootstrap CDN kaldırma (grid'i custom CSS ile değiştirme — todo listede), Font Awesome/Prism self-host + cache lifetime iyileştirmesi, 3 erişilebilirlik bulgusu (aria-hidden içinde odaklanabilir öğe — `nav-drawer`/modal'lar; kontrast; başlık sırası) — skor zaten yeşil (91) olduğu için düşük öncelik
- **Mobil PageSpeed devam — Agentic browsing + cache + görsel + CSS bundling** (temmuz 2026)
  - PageSpeed'in yeni "Agentic browsing" denetimi: `#navDrawer` kapalıyken `aria-hidden="true"` idi ama içinde odaklanabilir `<a>`/`<button>` vardı (WCAG ihlali, AI ajanları da karışıyordu) → `inert` attribute eklendi (`templates/base.html:367` başlangıç durumu + `static/js/navbar.js` açma/kapama fonksiyonları toggle ediyor). Yukarıdaki "3 erişilebilirlik bulgusu" listesindeki `nav-drawer` kısmı çözüldü; modal'lar (`searchModal` vb.) hâlâ bekliyor (bkz. Sıradaki Görevler)
  - Nginx `/static/` cache: `expires 1d` → `1y; immutable` (`nginx/conf.d/default.conf:46-50`) — dosyalar zaten hash'li (`CompressedManifestStaticFilesStorage`) + CSS'lerde manuel `?v=` var, çelişki yok
  - Navbar logosu tekrar büyümüştü: 200×200/47.4 KB → 80×80/9.8 KB küçültüldü (36-40px'te gösteriliyor, retina için 2x yeterli)
  - Footer'daki 3 dış favicon (Google Scholar/DergiPark/Semantic Scholar) `loading="lazy"` aldı (`templates/partials/footer.html`)
  - `base.css`+`navbar.css`+`footer.css`+`style.css`+`sidebar_widgets.css` → tek `static/css/bundle.css` (5 istek→1, minify ile %32 küçüldü); bilerek **render-blocking bırakıldı** — bunlar 3. parti kütüphane değil sayfanın kendi navbar/layout CSS'i, deferred yapılsa FOUC (stilsiz navbar flaşı) oluşurdu. **Bakım notu:** kaynak 5 dosya artık kullanılmıyor, düzenlemenin `bundle.css`'e yansıması için elle yeniden üretilmesi gerekiyor (bkz. §26)
- **Hakkımızda / Neden Analizus birleştirme + İletişim'i bağımsız landing page yapma** (temmuz 2026) — baypass.net kontakt sayfasından esinlenildi
  - "Neden Analizus?" sayfası (`/neden-biz/`, rakip karşılaştırma tablosu + garantiler + başarı hikayeleri) kaldırıldı, içeriği tek sayfada `/hakkimizda/`'ya taşındı; `about()` view artık `neden_biz()`'in ürettiği context'i de üretiyor; `/neden-biz/` → `/hakkimizda/` 301 redirect; `analytics/utils.py`'deki artık kullanılmayan `/neden-biz` etiketi silindi
  - İletişim, Hakkımızda'nın `#iletisim` alt bölümü olmaktan çıkıp `/iletisim/` (`contact` view, isim `contact`) üzerinde bağımsız landing page oldu — GET artık redirect değil gerçek sayfa render ediyor; baypass tarzı iki kolon: solda tıklanabilir, hover animasyonlu E-posta/WhatsApp bilgi kartları (`ax-contact-info-card`, `:has()` seçiciyle ikon rengine göre blob), sağda form kartı (`ax-contact-card` — pill input/select/textarea, `--ax-radius-full`/`--ax-radius-xl` token'ları)
  - Form "Konu" serbest metni → "Konu Türü" dropdown (İstatistik Analiz Talebi / Akademik Tarama / Hizmetler Pazarı / Teknik Destek / Diğer); view değişmedi (`POST.get('subject')` aynı kalır)
  - Yeni `/gizlilik-politikasi/` sayfası — footer'daki daha önce ölü olan `{% url 'about' %}#kvkk` linki (hiç `id="kvkk"` yoktu) buraya düzeltildi; iletişim formuna zorunlu (HTML `required`, backend doğrulaması yok) KVKK onay checkbox'ı eklendi, linki bu sayfaya gidiyor
  - Navbar/footer: "Neden Analizus?" linkleri kaldırıldı, "İletişim" linkleri `/iletisim/`'e güncellendi (`templates/base.html` desktop+mobil, `templates/partials/footer.html`)
- **`/gizlilik-politikasi/` içerik ve tasarım revizyonu** (temmuz 2026)
  - İlk sürüm kendi taslağımızdı (üstte "hukuk danışmanına onaylat" uyarı kutusuyla); kullanıcı uyarı kutusunu kaldırttı, ardından daha resmi/kapsamlı bir KVKK metniyle (Veri Sorumlusu, İşlenme Amaçları ve Hukuki Sebepler tablosu, Aktarım, Saklama Süreleri, Madde 11 Hakları, Çerez Politikası) tamamen değiştirdi
  - Tablo başta Bootstrap `table table-dark table-borderless` ile yapılmıştı — `table-dark`'ın kendi `--bs-table-bg`/`--bs-table-color` CSS değişkenleri satıra verilen inline arkaplanla çakışıp donuk/okunaksız görünüyordu; kendi `.ax-kvkk-table` sınıfına (ax- token'ları, `:hover` satır aydınlatma) taşındı
  - Sayfa geneli gövde metni `text-secondary` (`#94a3b8`, soluk) yerine `text-light`/`--ax-text-primary` ile daha belirgin hale getirildi — baypass.net'in datenschutz sayfası referans alındı
  - **Veri saklama süresi tutarsızlığı bulundu ve kısmen giderildi:** sitede aynı konuda 3 farklı süre iddiası vardı — KVKK taslağı "7 gün", `home.html` FAQ'i "30 gün" (Hizmetler Pazarı teslim sonrası), `about.html` "hemen silinir" (aynı konu); kodda ise `cron_cleanup_s3_files` (`forum/api_views.py`) + `trdizin`/`openalex`/`oaipmh` `job_runner.py`'deki `cleanup_expired_*_s3_files()` fonksiyonları **3 gün** hardcode idi. Tarama araçları (YÖK Tez/OpenAlex/TR Dizin/OAI-PMH) için hepsi **7 güne** eşitlendi (kod + `openalex/management/commands/cleanup_openalex_files.py` + KVKK metni). **Hizmetler Pazarı tarafı kullanıcı kararıyla dokunulmadı** — ayrı görev (aşağıda).
  - **Bulgu, düzeltilmedi:** `analizus.md` §23'e göre yalnızca `cleanup-pageviews` cron'unun Hetzner crontab'ında gerçekten kayıtlı olduğu dokümante edilmiş; `cleanup-s3` "Aktif" işaretli ama crontab satırı doğrulanmamış — crontab repo'da tutulmadığından buradan teyit edilemedi, sunucuda `crontab -l` ile kontrol edilmeli.
- **YouTube Transcript menüye eklendi, Render testinde başarısız olunca tekrar kapatıldı** (temmuz 2026) — `feature_transcript` flag'i eklenip (`SiteSettings`, migration 0142) Analizler dropdown'ına linklendi, default `True` yapılmıştı; Docker image `youtube-transcript-api`'yi içermiyordu (`requirements.txt`'e girmiş ama image rebuild edilmemişti) → `docker compose build web` ile düzeltildi. **Render'da gerçek bir YouTube linkiyle denendiğinde çalışmadı** — §26'daki önceden bilinen cloud IP engeli teyit edildi. `feature_transcript` default `False`'a çevrildi (migration 0143, `help_text`'e not eklendi), DB'deki mevcut kayıt da kapatıldı; nav linki `{% if features.transcript %}` sayesinde koddan hiçbir şey silinmeden otomatik gizlendi.
- **Navbar logosu — "Analizus" yazısı eklendi** (temmuz 2026) — baypass.net navbar'ından esinlenildi; ikonun yanına `<span class="site-nav__logo-text">Analizus</span>` eklendi (desktop + mobil drawer), `alt` metni boşaltıldı (yazı zaten ismi taşıyor, ikon dekoratif). Punto iki kez büyütüldü: `--ax-text-2xl`→`--ax-text-3xl`→`--ax-text-4xl` (desktop), mobil drawer `--ax-text-xl`→`--ax-text-2xl` — kullanıcı production ekran görüntüsüyle "bir tık daha büyük olmalı" diyerek son artışı istedi. **Cache-busting unutulmamalı:** `navbar.css` içeriği değiştiğinde `templates/base.html:93`'teki `?v=XXXX` sorgu parametresi de artırılmalı yoksa nginx/tarayıcı önbelleği eski CSS'i sunmaya devam eder (bilinen hata, bkz. §26) — bu değişiklikte `?v=0103`→`?v=0104` yapılarak uygulandı.
- **Ana sayfa eylem-odaklı dönüşüm** (temmuz 2026) — "AI hızlı, biz doğru" konumlandırması; 6 faz, iki ayrı prompt dokümanı (ilk denetimde `home.html`'in zaten timeline/market-routing/stats bölümlerine sahip olduğu tespit edilip v2'ye revize edildi — bkz. §25 protokol notu)
  - **Faz 1 — Hero:** yeni H1 ("Analizini yap. Yapamıyorsan, yapan burada.") + alt başlık; `ax-hero-dropzone` sürükle-bırak alanı — dosya gerçekten `POST /analiz/hero-upload/`'a yüklenir (yeni `hero_upload` view, `istatistik/views.py`), mevcut `save_session_dataset()` mekanizmasına yazılır, `/analiz/<slug>/` sayfasına geçince dosya otomatik "seçili" gelir (ilk sürüm yalnızca `sessionStorage`'a dosya adı yazıyordu, gerçek veri aktarmıyordu — kullanıcı test edip düzelttirdi, bkz. §26); ikincil CTA `/proje-talebi/?source=hero`; hero altına kitle yönlendirme bandı (`/analiz/` · `/proje-talebi/?source=home_corporate`)
  - **Faz 2 — Sayaçlar:** `home()` view'ındaki 8 sayaç tek `home_stats` cache bloğuna alındı (300sn); `IstatistikJob` bazlı "Tamamlanan Analiz" ve `last_seen__gte=now-5dk` bazlı "Şu An Çevrimiçi Uzman" sayaçları eklendi (mevcut FreelanceJob bazlı sayaç "Tamamlanan Proje" olarak yeniden adlandırıldı, etiket çakışması önlendi)
  - **Faz 3 — Uzman Vitrini:** "Uzmanlarla Tanış" bölümü; sorgu ilk halinde bağımsız bir kriterle yazılmıştı, kullanıcı isteğiyle `/uzmanlar/` (`uzman_dizini`) sayfasının varsayılan "puan" sıralamasıyla birebir aynı kritere (rank contributor+ VEYA skill VEYA en iyi cevap, `-reputation,-completed_jobs`) hizalandı; `username='admin'` özel olarak hariç tutuldu (diğer superuser'lar kalabilir — kullanıcı kararı), 5 dk cache (`home_experts`); fiyat/teklif bilgisi hiç gösterilmez
  - **Faz 4 — AI Analiz Doğrulama bandı:** `ProjectRequest.ANALYSIS_CHOICES`'a `verification`, `SOURCE_CHOICES`'a `hero`/`home_corporate`/`verification` eklendi — tek migration'da birleştirildi (`0144_projectrequest_source_choices`); `proje_talebi.html`'de `source` değerine göre otomatik ön-seçim
  - **Faz 5 — AI Asistan soru chip'leri:** "Hangi testi kullanmalıyım?" bölümü; widget'ın iç koduna dokunulmadan `window.axOpenAiWidget(question)` köprüsü eklendi (`templates/base.html`); **bulunan bug:** chip'e tıklayınca widget açılıp anında kendi kendine kapanıyordu (widget'ın "dışarı tıklanınca kapat" `document` listener'ı aynı click'in bubble fazında tetikleniyordu) — chip'in `onclick`'ine `event.stopPropagation()` eklenerek düzeltildi (bkz. §26)
  - **Faz 6 — SEO:** `<title>`/meta description yeni pozisyonlamaya göre güncellendi; JSON-LD şemaları kontrol edildi, çelişki yok (görünür FAQ akordiyonu ile `FAQPage` şemasının farklı sorular içermesi **önceden var olan**, düzeltilmemiş bir tutarsızlık olarak not edildi)
- **Marka görselleri entegrasyonu** (temmuz 2026) — `static/img/`'a eklenen 6 görsel çifti (masaüstü+mobil WebP, indigo-violet/koyu lacivert marka dili) 5 sayfaya yerleştirildi; ortak `static/css/brand_visuals.css` (`.ax-brand-visual` bileşeni) yalnızca ilgili template'lerde `{% block extra_head %}` ile yüklendi (bundle.css'e girmedi)
  - `proje-talebi-hero` → `/proje-talebi/` üst bandı, `kurumsal-hero` → `/hakkimizda/` üst bandı, `studio-sonrasi` → `/hakkimizda/` orta bandı, `tarama-hero` → `/tarama/` hub üst bandı, `akademik-hero` → `/analiz/` hub üst bandı, `ai-dogrulama` → ana sayfa AI Doğrulama bandının arka planı (metin üzerine biniyor, `.ax-brand-visual__overlay` gradient ile)
  - **LCP kararı:** sayfa en üstündeki 4 bant (proje-talebi/kurumsal/tarama/akademik-hero) `loading="lazy"` almadı, `fetchpriority="high"` aldı (Google'ın LCP eleman tavsiyesi); sayfa ortasındaki 2 görsel (studio-sonrasi, ai-dogrulama) `loading="lazy"` ile kaldı — kullanıcıya sorulup onaylanan, sayfa içi konuma göre değişen bir karardı, geriye dönük olarak Faz A/B'de de düzeltildi
  - Tüm görseller dekoratif (`alt=""`); `<picture>` mobil-önce kalıp (`<source media="(min-width:768px)">` masaüstü, varsayılan `<img>` mobil) — kullanıcının ayrıca "ÖNCE MOBİL" kuralını proje prompt dosyalarına eklettiği oturumda uygulandı

- **AI Çözümler (Agentic) landing page** (temmuz 2026) — `/ai-cozumler/` kurumsal AI ajan/otomasyon tanıtım sayfası, `feature_agentic_landing` flag'i arkasında (default `False`); 4 fazda kuruldu:
  - **Faz 1 — Altyapı:** `SiteSettings.feature_agentic_landing`, `ProjectRequest.ANALYSIS_CHOICES`/`SOURCE_CHOICES`'a `agentic` girişi, `ai_cozumler` view (`feature_required` decorator), `proje_talebi.html`'de `source=agentic` ön-seçimi — tek migration (`0145`). Dokümandaki `?type=` parametresi varsayımı gerçek kodla uyuşmadığı için (yalnızca `?source=` işleniyor) **kullanılmadı**.
  - **Faz 2 — İçerik:** `static/css/agentic_landing.css` (mobil-önce, sayfaya özel, `bundle.css`'e girmiyor); hero (CSS-only mesh gradient), 3 kullanım senaryosu kartı, "Nasıl Çalışır" 4 adımlı timeline (`ax-timeline-section` class'ları `home.html`'den kopyalandı, 3. adım amber vurgulu), dürüstlük kutusu (iki sütun: "Ajanlara Uygun" / "İnsan İşi"), 5 soruluk SSS (vanilla-JS accordion, Bootstrap `data-bs-toggle` **kullanılmadı**).
  - **Faz 3 — Navbar + SEO:** Kurumsal dropdown'a (desktop + mobil) `{% if features.agentic_landing %}` koşullu link; FAQPage JSON-LD şeması; görünür SEO paragrafı. Sitemap'e **eklenmedi** — `forum/sitemaps.py`'deki `ToolsSitemap` flag kontrolü yapmıyor (mevcut, dokunulmayan bir tutarsızlık), flag açılınca elle eklenmesi gerekiyor.
  - **Faz 4 — Ana sayfa birleştirme:** Mevcut "AI Analiz Doğrulama" bandı (`home.html`, `.ax-verify-band`) "AI çağında iki yol" başlıklı iki kartlı bir bölüme yükseltildi — sol kart Doğrulama (aynen), sağ kart Agentic (`{% if features.agentic_landing %}` koşullu, flag kapalıyken sol kart `ax-ai-era-grid--single` ile tam genişlik alır); kitle bandı 🏢 pill metni "Kurumsal veri ve otomasyon projeleri" oldu; `forum/services/ai_service.py` `_ALLOWED_PATHS` + `SYSTEM_PROMPT` platform haritasına `/ai-cozumler/` eklendi.
  - **Bulunan bug'lar:** `{% load static %}` eksikliği (500 hatası) template'e eklenerek düzeltildi; `SiteSettingsAdmin.fieldsets`'e yeni flag eklenmeyi unutulmuştu (bkz. §26) — flag admin panelinde görünmüyordu, düzeltildi.

- **`/market/` Pazaryeri zenginleştirme** (temmuz 2026) — kaynak prompt `analizus_pazaryeri_prompt.md`; sayfa "stats + ilan listesi + 3 adım" çıplaklığından iki tarafı (ilan açan/uzman) karşılayan bir vitrine dönüştürüldü, 5 fazda + ayrı bir hero görsel commit'inde:
  - **Faz 1 — Hero + Çift Kapı:** mesh-gradient hero (`static/css/market.css`, sayfaya özel, `bundle.css`'e girmiyor), çift CTA (`İlan Aç (Ücretsiz)` / `Uzman Olarak Katıl`, giriş durumuna göre `?next=` ile login'e veya doğrudan hedefe yönlenir), tek satır güven şeridi (fiyat gizliliği, rozetli uzman, gerçek yorum)
  - **Faz 2 — Kategori Gezinmesi:** `?category=<id>` GET filtresi; chip'ler sabit bir taksonomi yerine açık ilanlarda fiilen kullanılan gerçek `JobCategory` değerlerinden dinamik üretiliyor — `FreelanceJob.category` gerçek bir FK ama `JobPostForm.category_input` serbest metinle dolduğundan (`get_or_create`) sabit taksonomi/anahtar-kelime eşleştirmesi yanlış-eşleşme riski taşırdı, kullanıcıya soruldu, dinamik seçildi; sort dropdown + chip linkleri birbirini ezmeden GET parametrelerini koruyor, JS yok
  - **Faz 3 — Sosyal Kanıt:** Uzman Vitrini şeridi eklendi — `home()`'daki sorgu/cache (`home_experts`) `_get_featured_experts()` yardımcı fonksiyonuna taşınarak iki view arasında tekrar hesaplama önlendi; kart HTML'i `forum/templates/forum/partials/_expert_showcase.html`'e, CSS'i (`.ax-expert-*`) `home_sections.css`'ten paylaşılan `static/css/expert_card.css`'e çıkarıldı (ana sayfa artık bu partial'ı include ediyor, görünüm/davranış değişmedi — regresyon test edildi). Başarı Hikayesi şeridi (varsa son 3 onaylı `SuccessStory`, yoksa gizli). Oyunlaştırma bandı — yalnızca giriş yapmış VE teklif verme yetkisi olmayan (`Profile.can_propose()` gerçek kuralı, metin "Teklif vermek için 1000+ puan veya özel rozet gerekli" ile tutarlı) kullanıcıya gösteriliyor, `{% url 'home' %}#istatistik-arenasi` linkli
  - **Faz 4 — Sıfır Temizliği + SEO:** İstatistik şeridi (Tamamlanan İş/Aktif Uzman/Son 90 Gün) sıfır kuralına bağlandı — 0 olan kutu gizli, üçü de 0 ise şerit tamamen gizli, kalan kutular Bootstrap'in otomatik eşit-genişlik `col-md` sınıfıyla doğal dağılıyor (yeni DB sorgusu yok); `og_title`/`og_description` blokları eklendi (`base.html`'deki mevcut override mekanizması kullanıldı, base.html'e dokunulmadı); görünür SEO paragrafı eklendi
  - **Hero görseli:** Faz 1'de CSS-only placeholder bırakılmıştı; kullanıcı iki fotoğraf (iki elin buluşması — ilan açan/uzman metaforu) sağlayınca `<picture>` ile mobil/masaüstü ayrı dosya (`market-hero-mobile.webp`/`market-hero.webp`, `min-width:768px` kırılımı, `fetchpriority="high"`, `alt=""`) eklendi, koyu gradient overlay fotoğrafın üzerine bindirildi
  - Sayfa hâlâ büyük ölçüde ham Bootstrap (`btn`/`card`/`badge`/`dropdown`, inline `style=`) üzerine kurulu — yalnızca bu görevde eklenen yeni bölümler `ax-` sistemine uygun; mevcut ilan kartları kapsam dışı bırakıldı, Bootstrap CDN kaldırma migration'ının (bkz. §27) gelecekteki bir fazına kaldı

- **Merge öncesi kapanış turu** (temmuz 2026) — kaynak prompt `analizus_kapanis_turu_prompt.md`; ilk yazıldığı hâliyle denetlendiğinde maddelerin ~1/3'ünün (FAZ B'nin çoğu, FAZ C tamamı, FAZ A'nın `&type=` adımları) AI Çözümler turunda zaten kapatıldığı, bir maddenin de (`&type=` ekleme) gerçek kodla çeliştiği (view yalnızca `source` okuyor) tespit edilip prompt buna göre revize edildikten sonra kalan gerçek işler uygulandı:
  - **FAZ A — Huni parametreleri:** Tableau sayfasındaki iki "İletişime Geç" CTA'sı (önceden `{% url 'contact' %}`'a gidiyordu, huniye hiç bağlı değildi) → `/proje-talebi/?source=tableau`; `proje_talebi.html`'de `visualization` seçeneği `source=='tableau'` ile ön-seçili. Bibliometri sayfasının `?source=tool` CTA'sı paylaşımlı `templates/service_promo.html`'den geldiği (bibliometrics dahil ~10+ araç sayfası aynı include'u paylaşıyor) için tek başına değiştirilemiyordu — `service_promo.html`'e opsiyonel `promo_cta_source` context değişkeni eklendi (`bibliometrics/views.py` `'bibliometrics'` geçiriyor, diğer 6 çağıran değişmeden `tool` varsayılanında kalıyor). `SOURCE_CHOICES`'a `tableau`/`bibliometrics` eklendi, migration `0146`.
  - **AI Çözümler hero görseli:** kullanıcının sağladığı `agentic-hero(-mobile).webp` çifti, market sayfasındaki aynı `<picture>`+koyu gradient overlay desenine göre placeholder HTML yorumunun yerine yerleştirildi (`agentic_landing.css?v=0002`).
  - **Proje-talebi sıfır kuralı düzeltmesi:** Platform Güven Sinyalleri şeridindeki "Tamamlanan Analiz" kutusu (`FreelanceJob` `completed` sayısı) 0 olduğunda gösterilmeye devam ediyordu — market sayfasındaki aynı desenle (`{% if %}` + `col-md` auto-genişlik) hizalandı, `completed_count`/`total_users` artık ayrı ayrı koşullu.
  - **`static/robots.txt` silindi** — Django `TEMPLATES.DIRS` yalnızca `templates/`'e bakıyor (`settings.py:96`), bu kopya hiçbir zaman serve edilmiyordu; canlı dosya her zaman `templates/robots.txt` idi.
  - **FAZ E — `/istatistik/` → `/analiz/` geçiş temizliği:** ilk denetimde "robots.txt disallow'u bilinçli, dokunma" denmişti; kullanıcının ikinci bir turda ısrarıyla yeniden açılınca gerçek bir SEO sorunu bulundu — `/istatistik/<slug>/` ile `/analiz/<slug>/` arasında GERÇEK 301 yoktu (`analiz_console` aynı view fonksiyonunu çağırıyordu), ve anonim ziyaretçi (`service_promo.html`) canonical override'ı YOKTU (yalnızca giriş yapmış kullanıcı şablonlarında vardı) — GSC'nin eski "Alternative page with canonical" uyarısının kök nedeni buydu. **Çözüm:** `istatistik/urls.py`'de 18 aracın hepsi için method-aware wrapper (GET → 301 `/analiz/<slug>/`, POST view'a değişmeden ulaşır — bkz. §26, naif blanket redirect analiz gönderimini kırardı). İç linkler güncellendi: en yüksek etkili düzeltme `TOOL_CATEGORIES` (`istatistik/views.py`) — `analiz_console_base.html` sidebar'ı + `analiz_hub.html` grid'i artık `istatistik:X` yerine `{% url 'analiz_console' slug %}` kullanıyor (bkz. §26); ayrıca footer "Analiz Araçları" → `analiz_home`, ana sayfa 5 kısayol linki, `liderboard.html`'deki zaten kırık (404) bare `/istatistik/` linki düzeltildi. `robots.txt`'ten `Disallow: /istatistik/` kaldırıldı. Yeni `NoIndexMiddleware` (`forum/middleware.py`) — `settings.IS_PRODUCTION` (`SITE_URL` bazlı, mevcut cookie-domain kontrolüyle aynı desen) `False` iken tüm yanıtlara `X-Robots-Tag: noindex, nofollow` ekler, production davranışı değişmez. `/ai-cozumler/` `StaticViewSitemap`'e `feature_agentic_landing` koşuluyla eklendi.
  - **Merge sonrası hatırlatma:** Google Search Console'da `/analiz/` araç sayfalarının indekslenme durumu birkaç hafta içinde kontrol edilmeli (301'lerin Google tarafından nasıl işlendiğini doğrulamak için).

- **İçerik & Topluluk Güçlendirme Turu** (temmuz 2026) — kaynak prompt `analizus_icerik_topluluk_prompt.md`; bibliometri/Tableau/blog/forum sayfalarında kanıt, performans ve akış düzeltmeleri, 4 fazda:
  - **Faz 1 — Bibliometri:** "Örnek Rapor Çıktıları" galerisi eklendi — aracın kendi gerçek çıktı grafiklerinden 6 tanesi (Yayın Trendi, Anahtar Kelime Bulutu, Yazar İşbirliği Ağı, Atıf Analizi & H-index, Araştırma Boşluğu Haritası, Lotka Kanunu), `static/css/bibliometrics.css` (yeni, `ax-` sistemi, mobil yatay kaydırma → masaüstü 3'lü grid) ile stillendi; OpenAlex ↔ Bibliometri arası köprü bandı `landing.html`'e eklendi (ters yön zaten `openalex/landing.html`'de AJAX transfer olarak mevcuttu, dokunulmadı). **Bulgu:** galeri ilk halinde yalnızca giriş yapmış kullanıcının gördüğü `landing.html`'e eklenmişti — anonim ziyaretçi `bibliometrics/views.py`'nin döndürdüğü ayrı `service_promo.html`'i görüyordu ve galeri hiç görünmüyordu; `service_promo.html`'e (7 araç sayfası paylaşıyor) `{% if promo_gallery %}` korumalı opsiyonel galeri bloğu eklenerek çözüldü — diğer 6 çağıran etkilenmedi.
  - **Faz 2 — Tableau facade:** 4 dashboard'un `<tableau-viz>` embed'i `<template>` etiketi içine taşındı (kod silinmedi), yerine poster görseli (`tableau-poster-{trdizin,obezite,nufus,satis}.webp`) + "▶ İnteraktif Dashboard'u Yükle" butonu; tek event-delegation JS (~10 satır) tıklamada `template.content.cloneNode(true)` ile gerçek embed'i DOM'a enjekte ediyor. Sonuç: ilk yüklemede `public.tableau.com`'a sıfır istek (Network sekmesiyle doğrulandı). **Bulgu/bug:** `tableau_dashboard.html`'in kullandığı `{% block extra_css %}` `base.html`'de hiç tanımlı değildi (yalnızca `extra_head` var) — bu yüzden hem eski sekme stilleri hem yeni facade/buton CSS'i hiç render edilmiyordu (buton stilsiz, sayfanın altında görünüyordu); `extra_head`'e çevrilerek düzeltildi.
  - **Faz 3 — Blog:** `blog_detail.html` kapanış turundaki `{% block og %}` mekanizmasını kullanmıyordu, kendi elle yazdığı `<meta property="og:...">` etiketleri vardı — bu, base.html'in varsayılanıyla birlikte **çift `og:title`/`og:description`** üretiyordu (render testiyle doğrulandı: 2 tag → düzeltme sonrası 1 tag). `{% block og_title/og_description/og_type/og_image %}` kullanımına geçirildi, kapak yoksa `{{ block.super }}` ile varsayılan og-banner korunuyor. `BlogPost.cover_image` alanı zaten vardı ama liste sayfasında (öne çıkan + grid kartları) render edilmiyordu — ikisine de `loading="lazy"` + `width`/`height` ile eklendi. Pagination bug'ı (iddia edilen ham `?page=2` linki) kod incelemesi + mock render testinde bulunamadı, atlandı.
  - **Faz 4 — Forum:** `?next=` desteği `register()`'a login'deki (`custom_login`) aynı `url_has_allowed_host_and_scheme` deseniyle eklendi (3 senaryo test edildi: geçerli/next-yok/kötü-niyetli). **Bulgu:** `new_topic` view'ının kendisi doğrulama şartı aramasa da site geneli `EmailVerificationMiddleware` (`forum/middleware.py`) doğrulanmamış kullanıcıları sabit bir beyaz liste dışına çıkarmıyordu, `new_topic` listede yoktu — next fiilen işe yaramıyordu; kullanıcı onayıyla `new_topic` beyaz listeye eklendi. "Gündemdeki Tartışmalar" bloğu `forum/templates/forum/partials/_gundem_tartismalar.html`'e çıkarılıp hem `home.html`'de (davranış birebir korundu, `gundem_zero_rule` yok) hem `forum_index.html`'de (sıfır kuralına uygun, `gundem_zero_rule=True`, boşsa render edilmiyor) kullanılıyor; sorgu `home()`'daki `popular_topics` ile birebir aynı (N+1 yok). Boş-durum sızıntısı ve kategori açıklaması yazım hatası iddiaları kod/DB incelemesinde doğrulanamadı (zaten doğru korunuyor / DB'de açıklamalar şu an boş), atlandı. "Popüler" rozeti gerçek metrikten geliyor (en aktif ilk 5 kategori, sabit top-5 — minimum konu sayısı eşiği yok), kullanıcıya bildirildi, karar bekliyor. "Türkiye'nin en büyük..." iddiası `forum_index.html`, `about.html` ve **site geneli varsayılan** `templates/base.html` meta description'ından temizlendi (4 istatistik sayfasındaki "büyük" eşleşmeleri matematiksel terimdi, dokunulmadı).
  - **Login/Register görsel paneli:** `registration/login.html`/`templates/forum/register.html`'deki mevcut iki-sütunlu split layout (masaüstünde görsel panel + form, `<992px`'te panel gizli/form tek başına) yeni cinematic `auth-login.webp`/`auth-register.webp` görselleriyle güncellendi (eski `login-hero.jpeg`/`register-hero.jpeg`, 878K/748K → 23K/41K WebP; JPEG'ler şifre sıfırlama sayfalarında hâlâ kullanıldığı için silinmedi). Mobil davranış kullanıcı kararıyla değiştirilmedi (panel gizli kalıyor); `auth-login-mobile.webp`/`auth-register-mobile.webp` repo'da hazır bekliyor, referanslanmıyor. 768-991px (tablet) aralığında da panel zaten gizli (`max-width:991px` kuralı tableti kapsıyor), ek işlem gerekmedi.

- **Merge öncesi son süpürme turu** (temmuz 2026, devam ediyor) — kaynak prompt `analizus_son_supurme_prompt.md` (`~/Desktop/`, repo'da dosya olarak yok); önceki turların ardından kalan maddeleri kapatmak için başlatıldı. Denetlendiğinde maddelerin önemli bir kısmının **önceki turlarda zaten kapatıldığı** görüldü (bu durum art arda üçüncü kez tekrarlandı — bkz. aşağıdaki genel ders):
  - **Madde 1 — Huni parametreleri:** Tableau'daki iki "İletişime Geç" CTA'sı "Proje Talebi Oluştur"a çevrildi. Bibliometri için gerçek bir eksik bulundu: `?source=bibliometrics`'in `ANALYSIS_CHOICES`'ta karşılığı yoktu (kullanıcı kararıyla mevcut `statistics` seçeneği yeniden kullanılmadı — "bibliyometrik analiz istatistiksel analiz değildir"). `ANALYSIS_CHOICES`'a `bibliometric` eklendi (migration `0147`, no-op AlterField); `proje_talebi` view artık `?type=` GET param'ını da okuyor — bkz. §8'deki güncellenmiş not.
  - **Madde 2 — Site geneli Sıfır Kuralı:** Kaynak `analizus_sifir_kurali_prompt.md` (`~/Desktop/`). Ana sayfa istatistik bandındaki 5 sayaç (aktif üye/akademik konu/forum gönderisi/tamamlanan proje/tamamlanan analiz) ayrı ayrı `{% if %}` ile korunuyor; hepsi + diğer 3 sayaç (açık ilan/haftalık yeni üye/çevrimiçi uzman) sıfırsa `has_any_stats` (mevcut cache'li `home_stats`'tan türetilen tek boolean, yeni sorgu yok) ile bant tamamen gizleniyor. Uzman kartı "X tamamlanan proje" satırı 0 ise gizli. "Akademik Haberler" itiraf placeholder'ı kaldırıldı; aynı satırdaki "Gündemdeki Tartışmalar" kartıyla (bkz. İçerik & Topluluk turu, `_gundem_tartismalar.html`) layout bütünlüğü kuruldu — **bulgu:** o kartın `gundem_zero_rule` bayrağı `forum_index.html`'de bağlıydı ama `home.html`'e hiç bağlanmamıştı, düzeltildi. `/hakkimizda/` "Ekip ve Güven" bölümü `team_members` boşsa (başlık dahil) tamamen gizleniyor artık. `forum/tests.py`'e 9 smoke test eklendi.
  - **Madde 3 (footer), 4 (forum arama boş-durumu), 6 (dev noindex middleware) — iş YOK:** üçü de zaten çözülmüştü, muhtemelen önceki turlarda, bu dokümana yansımamıştı.
  - **Madde 5 — OG override + meta:** 8 sayfaya (ana sayfa, /ai-cozumler/, /market/, /proje-talebi/, /bibliometrics/, /tableau-analiz/, /analiz/, /tarama/) özgün `og_title`/`og_description`/`twitter_title`/`twitter_description` eklendi (mekanizma zaten vardı, kullanılmıyordu). **Bulgu:** `/bibliometrics/` misafir kullanıcı için `landing.html` değil `service_promo.html` render ediyor (bkz. §8) — asıl düzeltme `promo_description`'dan türetilen meta bloğuyla oraya yapıldı, bu da aynı şablonu paylaşan 10+ araç sayfasına özgün og:description kazandırdı.
  - **Madde 6a — Bibliometri OpenAlex köprüsü:** "Örnek Rapor Çıktıları" galerisi ve OpenAlex ters köprüsü İçerik & Topluluk turunda zaten eklenmişti; eksik kalan tek parça — hero altı "OpenAlex'te tarama mı yaptın?" bandı — eklendi (`promo_openalex_bridge` bayrağı, yalnızca bibliometride true, bkz. §8).
  - **ÖNEMLİ BULGU — Madde 7b (Tableau facade) ve 7c'nin (Blog) büyük kısmı da zaten yapılmıştı:** İçerik & Topluluk turunun Faz 2'si (Tableau: poster+`<template>`+lazy JS enjeksiyonu, 4 dashboard) ve Faz 3'ü (Blog: `og_title`/`og_description`/`og_type=article`/kapak görseli) canlı kodda doğrulandı — süpürme promptunun 7b/7c maddeleri neredeyse tamamen örtüşüyor. Yalnızca **tek gerçek eksik** kaldı: blog yazısının `cover_image` alanı boşsa kategoriye göre bir görsel eşlemesi (İstatistik→akademik-hero, Veri Kazıma→tarama-hero, Ekonometri/Veri Politikası→kurumsal-hero, Akademi ve AI→agentic-hero, diğer→studio-sonrasi) YOK — kapak yoksa liste kartı da `og:image` da görselsiz kalıyor. Pagination linkleri zaten doğru (arama/kategori/tag/level parametrelerini koruyor).
  - **Genel ders (üçüncü kez tekrarlandı — bkz. §26'ya taşınmalı):** ardışık "kapanış/süpürme" promptları yazılırken bir öncekinin gerçekte neyi kapattığı doğrulanmadan yazılıyor, bu da her turda "zaten yapılmış" maddelerin yeniden envanterini çıkarmaya harcanan zamana yol açıyor. Yeni bir süpürme/kapanış promptu yazmadan önce ilgili dosyaların CANLI halini (`git show`, `grep`) kontrol etmek, yalnızca önceki promptun metnine güvenmemek gerekiyor.
  - **Madde 7b — gerçek bir eksik bulundu ve düzeltildi:** "zaten yapılmıştı" notu yarı doğruydu — poster+buton facade UI önceki turda kuruluydu ama `tableau.embedding.3.latest.min.js` script'i `extra_js` block'unda koşulsuz (sayfa yüklenir yüklenmez) çekiliyordu, bu da "ilk yüklemede `public.tableau.com`'a sıfır istek" kabul kriterini fiilen bozuyordu. Script artık yalnızca "İnteraktif Dashboard'u Yükle" tıklamasında dinamik `<script>` enjeksiyonuyla yükleniyor; Playwright ile doğrulandı (yüklemede 0 istek, tıklamada gerçek dashboard). **Eşzamanlı oturum notu:** bu düzeltme, aynı repo üzerinde eşzamanlı çalışan başka bir oturum tarafından da bağımsız olarak bulunup commit'lenmişti (`4ebaa7e`) — iki oturum aynı anda aynı sonuca ulaştı, çakışma olmadı.
  - **Madde 7c — tek eksik parça tamamlandı:** `BlogPost.cover_image_url` property'si eklendi (kapak yoksa kategoriye göre 5 tema görselinden birine düşer, 15 gerçek `BlogCategory` slug'ı eşlendi, migration gerekmedi). Liste/öne çıkan/detay/ilgili-yazı kartları + `og:image` + JSON-LD `image` alanı artık her zaman bir görsel gösteriyor — 35/35 yayındaki yazının hiçbirinde kapak yoktu, bu yüzden hepsi boş görünüyordu.
  - **Madde 8 — Hero sadeleştirme:** `ax-hero__actions` bloğu ("Ücretsiz Başla"/"Analiz Yap" / "Uzman Bul" / "Foruma Katıl", giriş yapmış/yapmamış iki varyantıyla) `home.html`'den tamamen kaldırıldı; dropzone, "uzmana bırak" linki, veri kazıma bandı, alt CTA kartları değişmedi.
  - **Madde 9 — Auth panelleri:** `login.html`/`register.html` `base.css` yüklemiyor (tamamen izole, hardcode renkli sayfalar) — spesifikasyondaki `var(--ax-bg)` bu sayfada tanımsız olduğundan, kullanıcı onayıyla dosyanın kendi `#0a1628` rengiyle iç vinyet eklendi (`box-shadow: inset 0 0 90px 70px #0a1628`). Turuncu dikey "yıldız kayması" ayraç çizgisi (`::after`+`@keyframes fall`) kaldırıldı. Form `<label>` etiketleri turuncudan (#ff6b4a) nötr griye (#94a3b8) döndü — yalnızca etiketler, form-subtitle rengi ve CTA butonu kullanıcı kararıyla turuncu kaldı. `register.html` alt başlığı "Veri Üssü Protokolü v3.0" → "Ücretsiz hesap — 30 saniye sürer." `<991px` gizleme davranışı değişmedi.
  - **Durum:** Madde 1-9 tamamlandı, `dev`'e push edildi. Kalan: 10 (deploy notu) ve 11 (ana sayfa "AI çağında iki yol" sağ kartına agentic-hero görseli) — kullanıcı kararıyla ertesi güne bırakıldı, ayrıntılı ilerleme ve kararlar `tasks/todo.md`'de.

### Sıradaki Görevler

#### Danışmanlık Dönüşümü (feature flag'lerle, detay: `danismanlik_roadmap.md`)
- **Ödeme sistemi kararı** — Stripe / Papara / IBAN+fatura (iyzico yasak) — **blokaj**
- **SiteSettings'e 6 flag** — `feature_consultancy_catalog`, `feature_consultancy_pricing`, `feature_client_portal`, `feature_project_pipeline`, `feature_verified_experts`, `feature_trust_stats` (hepsi `default=False`)
- **Hizmet kataloğu** — `/hizmetler/` + 5 alt sayfa (tez-analiz, literatur-tarama, kurumsal-veri, gorsellestirme, ml-yapay-zeka)
- **Müşteri portalı** — `/hesabim/talepler/` + `/<id>/` (login zorunlu, `feature_client_portal`)
- **Navbar güncellemesi** — Hizmetler dropdown + Uzmanlar linki + Taleplerim koşullu
- **Proje pipeline** — `ProjectRequest` → `Project` modeli, milestone, durum e-postaları
- **Verified uzman vitrini** — `uzman-dizini`'ne `tier=verified` filtresi + onay mekanizması
- **Referanslar sayfası** — `/referanslar/` + ana sayfa güven sayaçları (`SuccessStory` modeli mevcut)

#### Teknik Borç / Özellikler
- **Hizmetler Pazarı dosya otomatik silme mekanizması eksik** — `home.html` FAQ'i "proje teslim sonrası 30 gün saklanır, sonra silinir" diyor ama kodda bu sürece özel hiçbir cron/silme fonksiyonu yok (`grep "def cleanup"` yalnızca trdizin/openalex/oaipmh döndürüyor); dosyalar muhtemelen DM ekleri üzerinden gidiyorsa `cleanup-attachments` cronu (90 gün, genel DM/oda ekleri) devreye giriyor ama FreelanceJob'a özel değil ve süre de uyuşmuyor. Karar bekliyor: gerçek bir 30 günlük mekanizma mı eklensin, yoksa metin mi düzeltilsin.
- **`cleanup-s3` cron'unun Hetzner crontab'ında olduğu doğrulanmadı** — yalnızca `cleanup-pageviews` için crontab satırı dokümante edilmiş (§23); `crontab -l` ile sunucuda kontrol edilmeli, yoksa 7 güne çekilen kod hiç çalışmaz.
- **Admin dashboard ProjectRequest bildirimi** — `dashboard_service.py`'e `status='new'` olan talepleri ekle; `ProjectRequest` şu an bildirim panelinde görünmüyor
- **YÖK Tez filtre genişletmesi** — üniversite + anabilim_dali text alanları; dolu gelince `islem=2` (legacy form) kullan — `abdad` + `Konu` parametreleri legacy formda mevcut; 6 dosya + 1 migration
- **ML Araçları** — Rastgele Orman, KNN (Karar Ağacı + SVM tamamlandı)
- ~~Yeni kullanıcı onboarding akışı~~ → Adım 2/3 bilgilendirme ekranına çevrildi (temmuz 2026); `onboarding_interests`/`onboarding_tools` alanları artık kullanılmıyor (model'de duruyor, boş)
- Analiz araçlarında akıllı hata yönetimi — `data_validator.py` mevcut ama yalnızca Cronbach'ta aktif; araç bazlı ön kontrol + Türkçe hata mesajları eksik; **pasif bekliyor**
- Blog içerik altyapısı iyileştirmeleri
- Admin analytics dashboard — navigasyon takibi tamamlandı; gelişmiş kullanıcı segmentasyonu/funnel analizi eklenebilir
- **Semantic Scholar → Bibliometrik Analiz entegrasyonu** — Semantic Scholar'dan BibTeX export ekle; sonuçları doğrudan `/bibliometrics/` aracına aktar; iki taraf değişiklik gerektirir (`semanticscholar/` export + `bibliometrics/` parser)
- ~~Gamification genişletmesi~~ → Referral sistemi tamamlandı (temmuz 2026)
- **Bootstrap CDN kaldırma** (temmuz 2026 — devam ediyor, kademeli migration) — Lighthouse'ta "kullanılmayan CSS" (111 KiB) + "kullanılmayan JS" (164 KiB) bulgusunun kaynağı. **Faz 1** (tamamlandı): eksik `ax-` bileşenleri (`.ax-alert`, `.ax-modal`, `.ax-dropdown`, `.ax-form-control`/`select`/`check`) `base.css`'e eklendi. **Faz 2** (tamamlandı): `static/js/ax-modal.js` + `ax-dropdown.js` vanilla controller'ları eklendi; `base.html` (4 modal: search/quiz/profile/story) + `success_stories.html` (1 modal) `.ax-modal` yapısına taşındı, `bootstrap.Modal` JS çağrıları kaldırıldı. **Faz 3** (başladı, dosya dosya): `account_delete.html`, `donation_success.html` migrate edildi (btn/card class'ları). **Bulgu:** component class'lardan (btn/card/badge/modal) bağımsız olarak Bootstrap **utility** class'ları (`d-flex`, `text-*`, `fw-*`, `mb-*`/`py-*`/`px-*`, `gap-*`, `rounded-*`, `shadow-*`, `bg-*`, `border-*`) hâlâ neredeyse her template'te yaygın — bunlar CLAUDE.md'nin "yalnızca grid" kuralına da aykırı ve Faz 4'te (CDN kaldırma) ayrıca migrate edilmeleri gerekiyor, henüz envanteri çıkarılmadı. Detaylı dosya bazlı ilerleme ve bulgular: `tasks/todo.md`.
- **Erişilebilirlik bulguları** (Lighthouse skoru 91, düşük öncelik) — `nav-drawer` düzeltildi (temmuz 2026, `inert` eklendi); `aria-hidden="true"` taşıyan modal'lar (`searchModal` vb.) hâlâ kapalıyken içlerinde odaklanabilir `<a>`/`<button>` var, aynı `inert` çözümü uygulanabilir; bazı metin/arkaplan kontrast oranları yetersiz; başlık (`h1`-`h6`) sırası bazı sayfalarda azalan düzende değil; **pasif bekliyor**

---

*Son güncelleme: Temmuz 2026 — Merge öncesi son süpürme turu (devam ediyor, kaynak: `analizus_son_supurme_prompt.md`), Madde 1-9 tamamlanıp `dev`'e push edildi: huni parametreleri (Tableau CTA metni + bibliometrik `ANALYSIS_CHOICES`/`?type=` ön-seçimi, migration `0147`); site geneli Sıfır Kuralı (ana sayfa 5 sayaç + `has_any_stats`, uzman kartı satırı, Akademik Haberler + Gündemdeki Tartışmalar layout bütünlüğü, /hakkimizda/ Ekip bölümü, 9 smoke test); 8 sayfaya özgün og/twitter meta (+ `service_promo.html` üzerinden 10+ araç sayfasına bonus); bibliometri OpenAlex köprü bandı; Tableau facade'daki gerçek eager-script bug'ı düzeltildi (eşzamanlı bir oturumla aynı anda bağımsız bulunup düzeltildi); blog kapaksız yazılara kategoriye göre varsayılan görsel (`BlogPost.cover_image_url`); hero'daki eski üçlü CTA satırı kaldırıldı; login/register görsel panellerine iç vinyet + turuncu ayraç kaldırma + nötr etiket rengi. **Bulgu:** footer/forum-arama/noindex-middleware maddeleri ve Tableau facade + blog OG'nin büyük kısmı zaten önceki turlarda kapatılmıştı, dokümana yansımamıştı. Kalan: deploy notu (Madde 10), ana sayfa agentic-hero sağ kart (Madde 11) — kullanıcı kararıyla ertesi güne bırakıldı (detay: `tasks/todo.md`). Önceki: İçerik & Topluluk Güçlendirme turu tamamlandı (kaynak: `analizus_icerik_topluluk_prompt.md`): Bibliometri örnek-rapor galerisi (guest+üye, `service_promo.html` genişletmesi dahil) + OpenAlex köprü bandı; Tableau 4 dashboard facade kalıbı (sıfır ilk-yük isteği) + `extra_css` block bug fix; blog çift-OG bug fix + kapak görselleri; forum `?next=` register akışı (`EmailVerificationMiddleware` whitelist genişletmesi dahil) + paylaşılan gündem partial'ı + "en büyük" iddia temizliği; login/register split-panel yeni cinematic WebP görselleriyle güncellendi. Önceki: Merge öncesi kapanış turu (kaynak: `analizus_kapanis_turu_prompt.md`): Tableau/bibliometri proje-talebi CTA düzeltmeleri (`promo_cta_source` mekanizması, migration `0146`); AI Çözümler hero görseli yerleştirildi; proje-talebi sıfır kuralı düzeltmesi; kullanılmayan `static/robots.txt` kopyası silindi; `/istatistik/` → `/analiz/` geçiş temizliği (18 aracın hepsinde method-aware 301; `TOOL_CATEGORIES` sidebar/hub linkleri düzeltildi; `robots.txt` disallow kaldırıldı; dev/staging `NoIndexMiddleware` eklendi; `/ai-cozumler/` sitemap'e flag-koşullu eklendi). Önceki: `/market/` Hizmetler Pazarı sayfası zenginleştirildi (5 faz: hero+çift kapı, dinamik kategori chip gezinmesi, paylaşılan Uzman Vitrini partial'ı + başarı hikayesi şeridi + oyunlaştırma bandı, sıfır kuralı + OG/SEO; ardından hero görseli). Daha eski geçmiş (`/ai-cozumler/` landing, ana sayfa eylem-odaklı dönüşüm, marka görselleri, Hakkımızda/İletişim/KVKK yeniden yapılandırması, YouTube Transcript, navbar logosu, Bootstrap CDN kaldırma migration Faz 1-3, Mobil PageSpeed, onboarding/referral/güvenlik düzeltmeleri) için yukarıdaki "Tamamlananlar" listesine bakın — bu satır yalnızca en güncel 3 turu özetler.*
