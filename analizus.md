# ANALIZUS.COM — TAM SİSTEM DOKÜMANTASYONU

> Bu dosyayı okuyan bir AI, projeye sıfırdan başlayabilmeli, doğru kod yazabilmeli ve hata yapmamalıdır.
> Tüm kural ve kısıtlara bu belgede yer verilmiştir.

---

## 1. PROJE AMAÇ VE VİZYON

**Alan adı:** `analizus.com`
**Hedef kitle:** Tez yazan öğrenciler, makale hazırlayan akademisyenler, istatistik analizine ihtiyaç duyan araştırmacılar ve bu alanda hizmet veren uzmanlar.
**Temel değer önerisi:** Tezin için doğru istatistik testini seç, verinle anında hesapla, gerektiğinde uzman bul — Türkçe, güvenilir, akademik düzeyde.
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
| Ödeme | iyzico altyapısı mevcut ama **pasif** — sonraya bırakıldı |
| i18n | Türkçe (`tr`), `locale/` klasöründe çeviri dosyaları |
| Rate Limit | `django-ratelimit` — kayıt: 3/saat, login: 10/5dk, istatistik POST: 30/saat |
| Analytics | Veri toplama yok (henüz) |

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
```bash
git pull origin main
docker compose up -d --build web
```

### Migration Varsa
```bash
git pull origin main
docker compose up -d --build web
docker compose exec web python manage.py migrate
```

### requirements.txt Değişince (Yeni Paket)
Image'i yeniden build etmek yeterlidir — `--build` bayrağı her zaman requirements'ı günceller:
```bash
git pull origin main
docker compose up -d --build web
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
nano /app/.env          # veya compose dosyasının bulunduğu dizindeki .env
docker compose up -d web
```

---

## 4. ORTAM DEĞİŞKENLERİ

> **Kritik:** E-posta env var'ları `SMTP_*` prefix'li — Django standart `EMAIL_*` değil. `settings.py` içinde map'lenir.

```bash
# Veritabanı
DATABASE_URL=postgresql://bunyamin:SIFRE@db:5432/analizus

# Redis (Channels)
REDIS_URL=redis://localhost:6379/0

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

# Ödeme (henüz pasif)
IYZICO_API_KEY=...
IYZICO_SECRET_KEY=...

# OpenAlex polite pool
OPENALEX_EMAIL=info@analizus.com
```

---

## 5. DEPLOY AKIŞI

### Branch Stratejisi
- `main` → production (Hetzner buradan deploy eder)
- `dev` → geliştirme (main → dev merge yapılır)
- Geliştirme `main`'de yapılır; `dev` ikincil

### Standart Deploy Akışı
```bash
# 1. Lokalde geliştir + commit + push
git push origin main

# 2. main → dev merge
git checkout dev
git merge main -m "Merge main → dev: açıklama"
git push origin dev
git checkout main

# 3. Hetzner'de uygula
ssh root@89.167.5.224
git pull origin main && docker compose up -d --build web
```

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
├── middleware.py           # EmailVerificationMiddleware
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
oaipmh/                     # 19 üniversite arşivi OAI-PMH
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
/openalex/          → openalex.urls
/oaipmh/            → oaipmh.urls
/yoktez/            → yoktez.urls
/bibliometrics/     → bibliometrics.urls
/tezanaliz/         → tezanaliz.urls  (namespace='tezanaliz')
/makaleanaliz/      → makaleanaliz.urls  (namespace='makaleanaliz')
/istatistik/        → istatistik.urls  (namespace='istatistik')
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
# Her araç için: /istatistik/<araç>/status/<uuid:job_id>/
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
class FreelanceJob:
    owner: FK → User
    title: str
    description: TextField
    budget_min: Decimal (null=True, blank=True)  # Formda gösterilmez — geriye dönük uyumluluk
    budget_max: Decimal                           # Kullanıcının girdiği tek bütçe alanı
    category: FK → Category
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

### İlan Kuralları (Hizmetler Pazarı)
- **Düzenleme:** `status=open` AND `proposals.exists()=False` AND `is_edited=False` → 1 kez düzenlenebilir
- **İptal:** `close_job` view → `status=cancelled` → bekleyen teklif verenlere AnalizBot DM
- **Teklif fiyat gizliliği:** `feature_proposal_price_privacy=True` → fiyatlar gizli, sadece taraflar görür

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

### Diğer Önemli Modeller
```python
class SiteSettings:      # Singleton (tek kayıt) — feature flag'ler admin'den yönetilir
class PrivateMessage:    # Kullanıcılar arası DM (attachment: FileField → S3)
class BlogPost / BlogCategory
class StudyRoom:         # Çalışma odaları
class StudyRoomPost:     # Oda mesajları (file: FileField → S3)
class QuizQuestion / QuizScore:  # İstatistik Arena
class Badge:             # Rozetler
class SuccessStory:      # Başarı hikayeleri
class DonationTier:      # Destek paketi (name, min_amount, premium_days, is_active)
class Donation:          # Bağış kaydı
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
| `feature_openalex` | True | OpenAlex |
| `feature_oaipmh` | True | OAI-PMH Üniversite Arşivi |
| `feature_quiz` | True | İstatistik Arena |
| `feature_messaging` | True | Özel Mesajlaşma |
| `feature_bibliometrics` | True | Bibliometrik Analiz |
| `feature_yoktez` | True | YÖK Tez |
| `feature_istatistik` | True | İstatistik Araçları |

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

### `ax-` Prefix CSS Sınıfları (Örnekler)
```
.ax-card                → Temel kart (surface arka plan, ax-border)
.ax-btn                 → Temel buton
.ax-btn--primary        → Primary buton (indigo)
.ax-badge               → Rozet
.ax-job-budget          → İlan bütçe alanı
.ax-profile-*           → Profil sayfası bileşenleri
.ax-market-*            → Market/ilan bileşenleri
```

### Geliştirici Kuralı
Yeni bileşen yazarken:
1. HTML: Bootstrap grid (`row`, `col`) ile iskelet kur
2. UI: İçeriği `ax-` sınıflarıyla tasarla
3. JS: `data-bs-toggle` yerine vanilla event listener kullan
4. Asla hardcode renk/pixel yazma — `var(--ax-primary)` kullan

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

### Navigasyon Menüsü Kategorileri (`base.html`)
```
Analizler →
  Ön Analizler:         Normallik, Betimsel İstatistik, Örneklem
  Geçerlik & Güvenirlik: Cronbach Alpha
  İlişki Analizleri:    Korelasyon
  Fark Analizleri:      t-Testi, ANOVA, Mann-Whitney U, Kruskal-Wallis, Ki-Kare
  Regresyon Analizleri: Çoklu Doğrusal Regresyon, Lojistik Regresyon
```

---

## 13. BİBLİOMETRİK ANALİZ

- Desteklenen formatlar: BibTeX (.bib), WoS TSV, Scopus CSV, OpenAlex TXT (otomatik algılama)
- Çoklu dosya birleştirme
- 10 Analiz türü: Yayın trendi, top yazarlar, kelime bulutu, top atıf, top dergi, kurum/ülke, işbirliği ağı, yayın türleri, h-index, yıllık atıf
- İş modeli: Demo (3 grafik, ücretsiz) / Tam (10 grafik, ücretli)
- S3 paths: `bibliometrics/demo/`, `bibliometrics/full/`

---

## 14. AKADEMİK TARAMA ARAÇLARI

### OpenAlex (`openalex/`)
- 240M+ akademik kayıt, ücretsiz API
- Cursor-based pagination, max 5000 sonuç
- `OPENALEX_EMAIL` env var (polite pool)
- S3 paths: `openalex/demo/`, `openalex/full/`, `openalex/orders/`

### YÖK Tez (`yoktez/`)
- HTTP tabanlı (requests + BeautifulSoup) — Selenium yok
- YÖK form POST → JS block parse → tezDetay.jsp ile abstract
- Sonuç formatı: TXT

### TR Dizin (`trdizin/`)
- `feature_trdizin = False` — varsayılan gizli
- HTTP API tabanlı

### OAI-PMH (`oaipmh/`)
- 19 üniversite arşivi aktif endpoint (ODTÜ, İTÜ, Dokuz Eylül, Akdeniz vb.)
- `sickle` kütüphanesi (OAI-PMH client)

---

## 15. E-POSTA SİSTEMİ

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

---

## 16. ANALİZBOT VE BİLDİRİM SİSTEMİ

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

---

## 17. S3 DEPOLAMA YAPISI

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
│   └── lojistik_regresyon/
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
```

**Utils (`forum/s3_utils.py`):**
- `upload_to_s3(file_obj, s3_key)`
- `upload_bytes_to_s3(content_bytes, s3_key, content_type)`
- `delete_from_s3(s3_key)`

---

## 18. GÜVENLİK VE BOT KORUMASI

### Kayıt Formu (`forum/forms.py`)
1. **Honeypot:** `website` alanı CSS ile gizlenir (`position:absolute; left:-9999px`). Bot doldurursa reddedilir.
2. **Username doğrulama:** 4+ ardışık sessiz harf → bot pattern → reddedilir
   - Regex: `[bcçdfgğhjklmnprsştvyz]{4,}` (Türkçe ünsüzler dahil)
3. **Rate limit:** Kayıt `3/saat`, Login `10/5dk`, İstatistik POST `30/saat` (IP bazlı, `django-ratelimit`)

### Middleware
- `forum.middleware.EmailVerificationMiddleware` — email doğrulanmamışsa bazı işlemler engellenir
- CSRF: Tüm formlarda zorunlu
- `XFrameOptionsMiddleware` — clickjacking önleme

---

## 19. ADMIN PANELİ

- **Tema:** Django Unfold (indigo/koyu tema)
- **URL:** `/admin/`
- **Dashboard:** `forum/dashboard.py` → `dashboard_callback`

### Önemli Admin Sınıfları (`forum/admin.py`)
- `FreelanceJobAdmin` — ilan yönetimi
- `JobProposalAdmin` — teklif (İlan Sahibi + Teklif Veren kolonları)
- `ProfileAdmin` — kullanıcı profil
- `SiteSettingsAdmin` — feature flag yönetimi

---

## 20. HIZMETLER PAZARI İŞ AKIŞLARI

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

## 21. OTURUM YÖNETİMİ

```python
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 7200          # 2 saat
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = True       # Prod'da (HTTPS zorunlu)
SESSION_COOKIE_DOMAIN = '.analizus.com'  # Prod'da
```

---

## 22. CRON SİSTEMİ

- Doğrulama: `X-Cron-Secret` header veya `?secret=` query param
- Env: `CRON_SECRET_KEY`
- **Aktif:** `/api/cron/cleanup-s3/` — trdizin + openalex S3 temizliği
- **Aktif:** `/api/cron/cleanup-attachments/` — 90 günden eski DM + oda mesajı dosyaları S3'ten silinir, mesaj/post kaydı korunur (haftalık çalıştırılması önerilir)
- **Kaldırılacak** (artık gereksiz): `/api/cron/daily-quiz/`, `/api/cron/update-badges/`

---

## 23. GELİŞTİRME ORTAMI

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

# Ratelimit cache'ini temizle (geliştirme sırasında limit dolunca)
python manage.py shell -c "
from django.db import connection
with connection.cursor() as c:
    c.execute(\"DELETE FROM django_cache_table WHERE cache_key LIKE '%rl:%'\")
    print(c.rowcount, 'kayıt silindi')
"
```

---

## 24. DEĞİŞMEZ KURALLAR (NON-NEGOTIABLES)

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

## 25. SIKÇA YAPILAN HATALAR VE ÇÖZÜMLERİ

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
| Ödeme işlemi | iyzico altyapısı kodda var ama pasif — ödeme sistemi henüz aktif değil |
| `No module named 'statsmodels'` | `pip install statsmodels` (regresyon analizleri için zorunlu) |
| İstatistik polling 404 dönüyor | `STATUS_TEMPLATE.replace()` pattern'i kullan, `STATUS_BASE + jobId + '/'` değil (double slash üretir) |
| İstatistik "Sunucu hatası." (preview) | Ratelimit dolmuş (30/h) — cache temizle: `DELETE FROM django_cache_table WHERE cache_key LIKE '%rl:%'` |
| `conf_int().iloc` AttributeError | statsmodels `conf_int()` bazen ndarray döner — `np.array(model.conf_int())` kullan |
| Job spinner'da takılı, hata yok | `result_data` içinde `inf`/`nan` var, JSON save patlıyor — serviste `np.isinf()` kontrolü ekle |

---

## 26. GÖREV LİSTESİ (Mevcut Durum)

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

### Sıradaki Görevler
- Yeni kullanıcı onboarding akışı (Profile.segment alanı)
- Analiz araçlarında akıllı hata yönetimi
- Blog içerik altyapısı iyileştirmeleri
- Admin analytics dashboard
- Gamification genişletmesi
- Fiyatlandırma sayfası (iş kararı — en son)

---

*Son güncelleme: Mayıs 2026 — §3 Hetzner Docker Compose (web/db/redis, /app, 89.167.5.224); §4 DATABASE_URL host=db; §8 DonationTier/Donation/StudyRoomPost modelleri; §12 regresyon + korelasyon sütun seçimi; §15 destekçi e-postası; §22 cleanup-attachments cron; §26 dosya paylaşımı + destekçi sistemi + korelasyon sütun seçimi + SEO iyileştirmeleri (IndexNow, sitemap, meta description, www redirect) tamamlandı*
