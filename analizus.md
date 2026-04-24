# Analizus.com — Proje Başvuru Rehberi

> Bu dosya her çalışma oturumunun başında okunur, sonunda güncellenir.
> Son güncelleme: 2026-04-24
>
> **Amaç**: Dosyalara erişim olmadan da projeyi anlayabilmek ve doğru öneriler sunabilmek.
> Bir AI aracı bu dosyayı okuyarak settings.py, models.py veya urls.py'ye bakmadan
> projenin mimarisini, kısıtlarını ve çalışma prensiplerini anlayabilmelidir.

---

## 1. Proje Nedir?

**Analizus.com** — Türkiye'deki akademisyen ve öğrencilere yönelik çok bileşenli araştırma platformu.

**Hedef kitle**: Tez yazan öğrenciler, makale hazırlayan akademisyenler, istatistik analizine ihtiyaç duyan araştırmacılar ve bu alanda hizmet veren uzmanlar.

### Ana Bileşenler ve URL'ler

| Bileşen | URL | App |
|---------|-----|-----|
| Forum (soru-cevap) | `/` | `forum` |
| Hizmetler Pazarı (uzman eşleştirme) | `/market/` | `forum` |
| İstatistik Araçları | `/istatistik/` | `istatistik` |
| YÖK Tez Arama | `/yoktez/` | `yoktez` |
| OpenAlex Yayın Tarama | `/openalex/` | `openalex` |
| TR Dizin (gizli, flag ile) | `/trdizin/` | `trdizin` |
| Üniversite Tez Arşivi (OAI-PMH) | `/oaipmh/` | `oaipmh` |
| Bibliometrik Analiz | `/bibliometrics/` | `bibliometrics` |
| Tez & Makale Analizi (AI) | `/tezanaliz/`, `/makaleanaliz/` | `tezanaliz`, `makaleanaliz` |
| AI Asistan | forum app içinde | `forum` |
| Hangi Test? | forum app içinde | `forum` |
| İstatistik Arena (Quiz) | forum app içinde | `forum` |
| Blog | forum app içinde | `forum` |
| Çalışma Odaları | forum app içinde | `forum` |
| Admin Paneli | `/admin/` | Django Unfold |

---

## 2. Teknik Stack

### Python ve Django
- **Python**: 3.11 (Dockerfile'da `python:3.11-slim`)
- **Django**: 4.2+ (ASGI modunda çalışıyor)
- **ASGI Sunucusu**: Daphne (`daphne -b 0.0.0.0 -p 8000 analizdestek.asgi:application`)
- **`ASGI_APPLICATION`**: `analizdestek.asgi.application`

### INSTALLED_APPS (sırayla)
```
daphne, channels,                        # gerçek zamanlı
unfold, unfold.contrib.filters,          # admin tema
django.contrib.admin/auth/...            # Django çekirdek
forum, trdizin, openalex, oaipmh,        # kendi app'lerimiz
yoktez, bibliometrics, tezanaliz,
makaleanaliz, istatistik,
crispy_forms, crispy_bootstrap5,         # form rendering
storages                                 # S3
```

### MIDDLEWARE (sırayla — önemli)
```
SecurityMiddleware
WhiteNoiseMiddleware          ← statik dosyalar burada serve edilir
SessionMiddleware
CommonMiddleware
CsrfViewMiddleware
AuthenticationMiddleware
LocaleMiddleware
MessageMiddleware
XFrameOptionsMiddleware
forum.middleware.EmailVerificationMiddleware  ← email doğrulama zorunluluğu
```

### Temel Paketler (requirements.txt)
```
Django, daphne, channels, channels-redis
dj-database-url, psycopg2-binary
whitenoise, boto3, django-storages
django-unfold, crispy-bootstrap5
Pillow, pandas, numpy, scipy
matplotlib, wordcloud, networkx, reportlab
bibtexparser, scikit-learn, nltk, zeyrek
openai, google-generativeai, groq
django-ratelimit, requests, httpx
beautifulsoup4, sickle (OAI-PMH client)
iyzipay (mevcut ama kullanılmıyor)
pytest, pytest-django, model-bakery
```

---

## 3. Sunucu Mimarisi (Hetzner)

### Genel Yapı
```
İnternet
    ↓
Nginx (80/443) — SSL termination, reverse proxy
    ↓
Docker network
    ├── web (Daphne, :8000) — Django uygulaması
    ├── db (PostgreSQL 16) — veritabanı
    ├── redis (Redis 7) — Channels channel layer
    └── nginx (Nginx Alpine) — reverse proxy
```

### docker-compose.yml Özeti

```yaml
services:
  db:
    image: postgres:16-alpine
    volumes: app_postgres_data:/var/lib/postgresql/data  # external volume

  redis:
    image: redis:7-alpine

  web:
    build: .                  # Dockerfile ile build edilir
    env_file: .env
    expose: 8000              # Dışarıya açık değil, sadece nginx'e
    volumes:
      - .:/app                # KOD volume-mount → kaynak değişince rebuild gerekmez
      - staticfiles_data:/app/staticfiles

  nginx:
    image: nginx:alpine
    ports: 80:80, 443:443
    volumes:
      - ./nginx/conf.d        # nginx yapılandırma
      - ./certbot/conf        # SSL sertifikaları (Let's Encrypt)
      - staticfiles_data:ro   # statik dosyaları doğrudan serve eder
```

**Kritik**: `web` servisi için `.:/app` volume-mount var. Yani sunucuda `git pull` yapınca Python dosyaları anında güncellenir — `docker compose build` gerekmez, sadece `docker compose restart web` yeterlidir. **Tek istisna**: `requirements.txt` değişirse rebuild gerekir.

### Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get install -y libpq-dev gcc   # psycopg2 için gerekli
COPY requirements.txt . && pip install -r requirements.txt
COPY . .
CMD ["sh", "-c", "bash deploy.sh && daphne -b 0.0.0.0 -p ${PORT:-8000} analizdestek.asgi:application"]
```

Container başlarken `deploy.sh` çalışır: `migrate`, `collectstatic`, seed data yükleme.

### Nginx Yapılandırması

```nginx
# HTTP → HTTPS yönlendirme
server { listen 80; return 301 https://...; }

# HTTPS
server {
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/analizus.com/fullchain.pem;

    # WebSocket (Django Channels)
    location /ws/ {
        proxy_pass http://web:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 3600;
    }

    # Statik dosyalar (Nginx doğrudan serve eder, Django'ya gitmez)
    location /static/ {
        alias /app/staticfiles/;
        expires 1d;
    }

    # Genel istekler → Daphne
    location / {
        proxy_pass http://web:8000;
        client_max_body_size 20M;
        proxy_read_timeout 120;
    }
}
```

### SSL
- Let's Encrypt (`certbot`) — `./certbot/conf/` dizininde
- `./certbot/www/` ACME challenge için

---

## 4. Deploy Akışı

### Otomatik (GitHub Actions)
```
git push origin main
    → .github/workflows/deploy.yml tetiklenir
    → SSH ile Hetzner'e bağlanır (secret: HETZNER_SSH_KEY)
    → cd /app && git pull origin main
    → docker compose restart web
```

### Manuel (Hetzner'de)
```bash
cd /app
git pull origin main
docker compose restart web              # kod değişikliği
docker compose exec web python manage.py migrate   # migration varsa
```

### Requirements.txt Değişince
```bash
docker compose up -d --build web        # yeniden build gerekir
```

---

## 5. Veritabanı

- **Motor**: PostgreSQL 16 (Docker, `db` servisi)
- **Bağlantı**: `DATABASE_URL=postgresql://bunyamin:SIFRE@db:5432/analizus`
  - `db` = Docker Compose servis adı (host olarak kullanılır)
- **`conn_max_age=0`** — her request yeni bağlantı açar (serverless uyumlu)
- **Lokal**: `DATABASE_URL` boş bırakılırsa SQLite kullanılır (`dj-database-url` otomatik)
- **Volume**: `app_postgres_data` — external volume (compose down yapınca silinmez)

### Migration Kuralları
- Her model değişikliği için `python manage.py makemigrations`
- Production'da: `docker compose exec web python manage.py migrate`
- Production DB'ye direkt dokunma — sadece migration üzerinden
- `select_related` / `prefetch_related` zorunlu (N+1 sorgu yaratma)

---

## 6. Ortam Değişkenleri

```bash
# Veritabanı
DATABASE_URL=postgresql://bunyamin:SIFRE@db:5432/analizus

# Redis (Django Channels)
REDIS_URL=redis://redis:6379/0         # 'redis' = Docker servis adı

# AWS S3
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_REGION_NAME=eu-north-1
AWS_STORAGE_BUCKET_NAME=analizus-files

# Email (prefix SMTP_* — settings.py'de EMAIL_* olarak map'lenir)
SMTP_HOST=mail.analizus.com
SMTP_PORT=587                          # 587=TLS, 465=SSL (otomatik algılanır)
SMTP_USER=info@analizus.com
SMTP_PASS=...
DEFAULT_FROM_EMAIL=Analizus <info@analizus.com>
ADMIN_NOTIFICATION_EMAIL=bkeles74@gmail.com

# Site
SITE_URL=https://www.analizus.com
DEBUG=False                            # prod'da False
SECRET_KEY=...

# AI
GROQ_API_KEY=...
OPENAI_API_KEY=...
GEMINI_API_KEY=...

# Diğer
CRON_SECRET_KEY=...
OPENALEX_EMAIL=info@analizus.com       # OpenAlex polite pool
POSTGRES_USER=bunyamin
POSTGRES_PASSWORD=...
POSTGRES_DB=analizus
```

> **Önemli**: Email env var'ları `SMTP_*` prefix'li. `EMAIL_HOST` gibi Django standartları değil.
> settings.py içinde: `EMAIL_HOST = os.getenv('SMTP_HOST')`

---

## 7. Ana Modeller

### Kullanıcı ve Profil (`forum/models.py`)
- `Profile` — her `User`'a OneToOne bağlı
- `account_type`: `Free`, `Premium`, `Expert`
- `rank`: `newbie → member → active → contributor → expert → master → legend → admin`
- `reputation`: Akademik puan (forum etkinliğinden otomatik)
- Uzman olmak için rank: `expert`, `master`, `legend` veya `admin`

### Forum
- `Category` — forum kategorisi
- `Topic` — konu başlığı
- `Post` — yanıt (Topic'e bağlı)

### Hizmetler Pazarı (FreelanceJob)
```python
class FreelanceJob:
    status: 'open' | 'in_progress' | 'completed' | 'cancelled'
    is_edited: bool       # 1 kez düzenleme hakkı (teklif yokken, open iken)
    budget_min, budget_max: int
    reference_number: str # örn: 2026/0013 (otomatik)
    expires_at: datetime  # son geçerlilik
    owner: User

class JobProposal:
    job: FreelanceJob
    expert: User
    status: 'pending' | 'accepted' | 'rejected'
    price: int
    duration: str
    # Kabul edilince: job.status → 'in_progress'
```

### İstatistik Araçları
- `IstatistikJob` — analiz işi
  - Dosya yükleme → `job_queue.py` ile arka planda işleme → S3'e PDF → email
  - `status`: `pending` | `processing` | `completed` | `failed`

### Diğer Önemli Modeller
- `SiteSettings` — tüm feature flag'ler (admin'den yönetilir, tek kayıt)
- `PrivateMessage` — kullanıcılar arası DM
- `BlogPost` / `BlogCategory` — blog
- `StudyRoom` — çalışma odaları
- `QuizQuestion` / `QuizScore` — İstatistik Arena
- `Badge` — rozetler
- `SuccessStory` — başarı hikayeleri
- `Skill` — uzman beceri alanları

---

## 8. İstatistik Araçları (`istatistik/`)

Mevcut servisler (`istatistik/services/`):
- `cronbach.py` — Cronbach Alpha güvenilirlik analizi
- `normallik.py` — Normallik testi (Shapiro-Wilk, Kolmogorov-Smirnov)
- `betimsel.py` — Betimleyici istatistik
- `korelasyon.py` — Korelasyon matrisi (Pearson/Spearman/Kendall)
- `ttesti.py` — t-Testi (bağımsız/bağımlı)
- `anova.py` — Tek yönlü ANOVA + post-hoc
- `orneklem.py` — Örneklem büyüklüğü hesaplama
- `data_validator.py` — Veri doğrulama (ID sütunu, Likert aralığı, boş değer)
- `job_runner.py` — Analizi job_queue'ya gönderir
- `pdf_fonts.py` — Türkçe PDF font yönetimi

Analiz akışı:
```
Kullanıcı dosya yükler (CSV/Excel)
    → data_validator kontrolü
    → job_queue.py ThreadPoolExecutor'a gönderilir
    → servis fonksiyonu çalışır (pandas, scipy, matplotlib)
    → PDF oluşturulur (reportlab)
    → S3'e yüklenir
    → Kullanıcıya email gönderilir
    → Admin'e bildirim emaili gönderilir
```

---

## 9. Bibliometrik Analiz (`bibliometrics/`)

- Formatlar: BibTeX (.bib), WoS TSV, Scopus CSV, OpenAlex TXT (otomatik algılama)
- Çoklu dosya desteği (kayıtlar birleştirilir)
- OpenAlex entegrasyonu: `/bibliometrics/from-openalex/<alex_job_id>/`
- 10 Analiz: Yayın trendi, top yazarlar, kelime bulutu, top atıf, top dergi, kurum/ülke, işbirliği ağı, yayın türleri, h-index, yıllık atıf
- İş modeli: Demo (3 grafik, ücretsiz) / Tam (10 grafik, ücretli)
- S3 paths: `bibliometrics/demo/`, `bibliometrics/full/`

---

## 10. Akademik Tarama Araçları

### OpenAlex (`openalex/`)
- 240M+ akademik kayıt, ücretsiz API
- Cursor-based pagination, max 5000 sonuç
- `OPENALEX_EMAIL` env var (polite pool için)
- S3 paths: `openalex/demo/`, `openalex/full/`, `openalex/orders/`

### YÖK Tez (`yoktez/`)
- HTTP tabanlı (`requests + BeautifulSoup`), Selenium yok
- YÖK form POST → JS block parse → tezDetay.jsp ile abstract
- Sonuç formatı: TXT

### TR Dizin (`trdizin/`)
- Feature flag ile gizli (`feature_trdizin = False` varsayılan)
- HTTP API tabanlı

### OAI-PMH (`oaipmh/`)
- 19 üniversite arşivi aktif endpoint
- `sickle` kütüphanesi (OAI-PMH client)
- Üniversiteler: ODTÜ, İTÜ, Dokuz Eylül, Akdeniz ve diğerleri

---

## 11. Gerçek Zamanlı (Django Channels)

```python
ASGI_APPLICATION = 'analizdestek.asgi.application'

# Dev (Redis yoksa):
CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

# Prod (Redis var):
CHANNEL_LAYERS = {"default": {"BACKEND": "channels_redis.core.RedisChannelLayer",
                               "CONFIG": {"hosts": [REDIS_URL]}}}
```

WebSocket path: `/ws/` (Nginx'te ayrı proxy_pass bloku)

---

## 12. Email Sistemi

- **SMTP** (Hetzner'de 587 portu açık)
- `mail.analizus.com` (hosting.com.tr promail)
- Gönderici: `info@analizus.com`
- **Async gönderim**: `forum/email_utils.py` içindeki tüm fonksiyonlar threading ile çalışır

### Admin Bildirim Fonksiyonları (`forum/email_utils.py`)
Her önemli event'te `bkeles74@gmail.com` adresine bildirim gider:
- Yeni kullanıcı, yeni konu, yeni yanıt
- Yeni ilan, yeni teklif, teklif kabul, iş tamamlandı
- Blog yayınlandı, analiz tamamlandı

### Kullanıcı Bildirimleri
- Yeni teklif gelince: ilan sahibine email (`send_proposal_notification`)
- Analiz tamamlanınca: kullanıcıya S3 linki ile email

---

## 13. DM ve AnalizBot Sistemi

- **AnalizBot**: Sistem kullanıcısı (username: `AnalizBot`)
- Otomatik DM göndermek için kullanılır
- `forum/signals.py` ve `forum/views.py`'de `User.objects.get(username='AnalizBot')` ile çağrılır
- DM URL'lerinde tam domain kullanılır (`SITE_URL` env var'ından)

### AnalizBot DM Gönderilen Durumlar
- İlan sahibi ilanı iptal edince → beklemedeki teklif verenlere DM
- İş tamamlanınca → başarı hikayesi daveti DM

---

## 14. Bildirim Sinyalleri (`forum/signals.py`)

| Event | Tetikleyici | Sonuç |
|-------|-------------|-------|
| Yeni kullanıcı | `User post_save (created)` | Admin email |
| Yeni konu | `Topic post_save (created)` | Admin email |
| Yeni yanıt | `Post post_save (created)` | Admin email |
| Yeni ilan | `FreelanceJob post_save (created)` | Admin email |
| Yeni teklif | `JobProposal post_save (created)` | İlan sahibine + Admin email |
| Teklif kabul | `JobProposal status → accepted` | Admin email |
| İş tamamlandı | `FreelanceJob status → completed` | Admin email, AnalizBot DM |
| Blog yayınlandı | `BlogPost status → published` | Admin email |
| Analiz tamamlandı | `IstatistikJob` signal | Kullanıcı + Admin email |

---

## 15. Hizmetler Pazarı İş Akışları

```
İlan Aç (status=open)
    ↓
Uzman Teklif Verir (proposal status=pending)
    → İlan sahibine email
    → Admin'e email
    ↓
İlan Sahibi Teklifi Kabul Eder
    → FreelanceJob.status = in_progress
    → Admin'e email
    ↓
İş Tamamlanır
    → FreelanceJob.status = completed
    → AnalizBot DM: başarı hikayesi daveti
    → Admin'e email
```

### İlan Düzenleme (1 Kez Hakkı)
- Koşul: `status=open` AND `proposals.exists()=False` AND `is_edited=False`
- Düzenledikten sonra: `is_edited=True` (bir daha düzenlenemez)
- Migration: `0071_add_freelancejob_is_edited`

### İlan İptal
- `close_job` view → `status=cancelled`
- Beklemedeki tüm teklif verenlere AnalizBot DM
- Teklif statüleri `rejected` yapılır

### Teklif Fiyat Gizliliği
- `feature_proposal_price_privacy=True` → fiyatlar gizli
- Sadece ilan sahibi ve teklif veren görür
- Diğerleri: "X uzman teklif verdi" (sayı)

---

## 16. Feature Flag Sistemi

`SiteSettings` modeli (tek kayıt), admin'den yönetilir.

| Flag | Varsayılan | Açıklama |
|------|-----------|----------|
| `feature_blog` | True | Blog |
| `feature_market` | True | Hizmetler Pazarı |
| `feature_proposal_price_privacy` | True | Teklif fiyat gizliliği |
| `feature_ai_assistant` | True | AI Asistan |
| `feature_trdizin` | **False** | TR Dizin (gizli) |
| `feature_openalex` | True | OpenAlex |
| `feature_oaipmh` | True | OAI-PMH Arşiv |
| `feature_quiz` | True | İstatistik Arena |
| `feature_messaging` | True | Özel Mesajlaşma |
| `feature_bibliometrics` | True | Bibliometrik Analiz |
| `feature_yoktez` | True | YÖK Tez |
| `feature_istatistik` | True | İstatistik Araçları |

Template kullanımı: `{% if features.openalex %}...{% endif %}`
Kaynak: `forum/context_processors.py` → `feature_flags()`

---

## 17. Güvenlik ve Bot Koruması

### Kayıt Formu (`forum/forms.py`)
1. **Honeypot**: `website` alanı CSS ile gizlenir (`position:absolute; left:-9999px`). Bot doldurursa reddedilir.
2. **Username doğrulama**: 4+ ardışık sessiz harf → bot pattern → reddedilir
   - Regex: `[bcçdfgğhjklmnprsştvyz]{4,}` (Türkçe ünsüzler dahil)
3. **Rate limit**: Kayıt `3/saat`, Login `10/5dk` (IP bazlı)

### Middleware
- `forum.middleware.EmailVerificationMiddleware` — email doğrulanmamışsa bazı işlemler engellenir
- CSRF: tüm formlarda zorunlu
- `XFrameOptionsMiddleware` — clickjacking önleme

---

## 18. S3 Depolama Yapısı

```
analizus-files/
├── avatars/                 # profil fotoğrafları
├── covers/                  # kapak fotoğrafları
├── istatistik/              # analiz PDF çıktıları
├── bibliometrics/
│   ├── demo/
│   └── full/
├── openalex/
│   ├── demo/
│   ├── full/
│   └── orders/
└── trdizin/
    ├── demo/
    ├── full/
    └── orders/
```

**Utils** (`forum/s3_utils.py`):
- `upload_to_s3(file_obj, s3_key)` — dosya yükle
- `upload_bytes_to_s3(content_bytes, s3_key, content_type)` — binary/PDF yükle
- `delete_from_s3(s3_key)` — sil

---

## 19. Statik Dosya Yönetimi

- **WhiteNoiseMiddleware** (MIDDLEWARE'in 2. sırası) — Django'nun kendisi serve eder
- `collectstatic` → `/app/staticfiles/` dizinine toplanır
- Nginx bu dizini doğrudan serve eder (`/static/` path'i için)
- S3'e upload **yok** — WhiteNoise yeterli

### CSS/JS Mimarisi
- `ax-` prefix'li özel CSS sınıfları kullanılır (Bootstrap'ten bağımsız)
- Bootstrap sadece grid layout için (`container`, `row`, `col-*`)
- UI elementleri (`btn`, `card`, `badge`) Bootstrap'ten değil, özel CSS'ten

---

## 20. URL Yapısı

```python
# analizdestek/urls.py
/admin/             → Django admin (Unfold)
/accounts/          → Django auth (password reset)
/login/             → özel login view (rate limited)
/logout/            → Django logout
/trdizin/           → trdizin.urls
/openalex/          → openalex.urls
/oaipmh/            → oaipmh.urls
/yoktez/            → yoktez.urls
/bibliometrics/     → bibliometrics.urls
/tezanaliz/         → tezanaliz.urls (namespace='tezanaliz')
/makaleanaliz/      → makaleanaliz.urls (namespace='makaleanaliz')
/istatistik/        → istatistik.urls (namespace='istatistik')
/                   → forum.urls (en sona — çakışma önlemi)
/sitemap.xml        → Django sitemaps
/robots.txt         → TemplateView
```

---

## 21. Oturum Yönetimi

```python
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # DB-backed (çoklu worker uyumlu)
SESSION_COOKIE_AGE = 7200  # 2 saat
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = True  # prod'da (HTTPS zorunlu)
SESSION_COOKIE_DOMAIN = '.analizus.com'  # prod'da
```

---

## 22. Admin Paneli

- Tema: **Django Unfold**
- Dashboard callback: `forum/dashboard.py` → `dashboard_callback`
- Önemli admin sınıfları (`forum/admin.py`):
  - `FreelanceJobAdmin` — ilan yönetimi
  - `JobProposalAdmin` — teklif (İlan Sahibi + Teklif Veren kolonları var)
  - `ProfileAdmin` — kullanıcı profil
  - `SiteSettingsAdmin` — feature flag yönetimi

---

## 23. Cron Sistemi

- Doğrulama: `X-Cron-Secret` header veya `?secret=` query param
- Env: `CRON_SECRET_KEY`
- **Aktif**: `/api/cron/cleanup-s3/` — trdizin + openalex S3 temizliği
- **Silinecek** (artık gereksiz, signals/views ile gerçek zamanlı çalışıyor):
  - `/api/cron/daily-quiz/`
  - `/api/cron/update-badges/`

---

## 24. Çalışma Kuralları

1. **Önce ilgili dosyayı oku** — tahmin yürütme
2. **Migration gerekiyorsa belirt** — production DB etkilenir; Hetzner'de `migrate` çalıştırılmalı
3. **UI için `ax-` CSS prefix** — Bootstrap sadece grid için
4. **Türkçe metin** — kullanıcıya görünen her şey Türkçe ve akademik dile uygun
5. **Commit mesajları Türkçe**: `feat:`, `fix:`, `refactor:` prefix
6. **Async email** — threading ile, blocking değil
7. **Büyük değişiklik öncesi onay al**
8. **`.env` değerlerini koda yazma**
9. **Long-running transaction'lardan kaçın** (`conn_max_age=0`)
10. **N+1 sorgu yaratma** — `select_related`/`prefetch_related` kullan

### Kod Öneri Yaparken Dikkat Edilecekler
- Email env var'ları `SMTP_*` prefix'li (`EMAIL_HOST` değil)
- `DATABASE_URL` var — `DATABASES` doğrudan ayarlanmaz
- Redis Docker servis adı: `redis` (hostname olarak)
- DB Docker servis adı: `db` (hostname olarak)
- `DEFAULT_FILE_STORAGE`: prod'da S3, local'de `FileSystemStorage`
- `SITE_URL` env var ile tam URL oluşturulur (relative path değil)
- Statik dosyalar WhiteNoise ile — `collectstatic` gerekir
- WebSocket path'leri `/ws/` altında (Nginx ayarı var)

---

## 25. Bilinen TODO'lar

- `/api/cron/daily-quiz/` ve `/api/cron/update-badges/` silinecek
- Ödeme sistemi belirsiz (iyzico altyapısı mevcut ama pasif)
- `feature_trdizin = False` (gizli, özel kullanıcılara açılabilir)

---

## 26. Görev Durumu (CLAUDE.md'den)

✅ Tamamlanan (son oturum dahil):
- Korelasyon, t-Testi, ANOVA, Örneklem araçları
- Admin email bildirim sistemi (tüm eventler)
- Bot koruması (honeypot + username + rate limit)
- İlan düzenleme hakkı (1 kez, teklif yokken, open iken)
- İlan iptal → bekleyen teklif verenlere DM
- Yeni teklif → ilan sahibine email
- Navbar'a yeni araçlar eklendi

🔲 Sıradaki görevler (CLAUDE.md sırasına göre):
- Görev 8: Yeni kullanıcı onboarding akışı (Profile.segment alanı)
- Görev 9: Analiz araçlarında akıllı hata yönetimi
- Görev 10: Blog içerik altyapısı iyileştirmeleri
- Görev 11: Admin analytics dashboard
- Görev 12: Gamification genişletmesi
