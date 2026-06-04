# ANALIZUS.COM — TAM SİSTEM DOKÜMANTASYONU

> Bu dosyayı okuyan bir AI, projeye sıfırdan başlayabilmeli, doğru kod yazabilmeli ve hata yapmamalıdır.
> Tüm kural ve kısıtlara bu belgede yer verilmiştir.

---

## 1. PROJE AMAÇ VE VİZYON

**Platform tanımı:** Analizus; bütün veri analizi, istatistiki analizler ve yapay zeka modellemeleri için uzmanların ve talep sahiplerinin buluştuğu, akademik desteklerin sıfırdan uzmanlık düzeyine kadar verildiği, kabiliyetlerin hizmete dönüştürüldüğü, kodsuz veri kazıma ile veri erişiminin sağlanabildiği bir forum ve analiz platformudur.

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

# Ödeme (henüz pasif)
IYZICO_API_KEY=...
IYZICO_SECRET_KEY=...

# OpenAlex polite pool
OPENALEX_EMAIL=info@analizus.com

# Semantic Scholar API (saniyede 1 istek; key'siz çalışır ama rate limit yüksek)
SEMANTIC_SCHOLAR_API_KEY=...
```

---

## 5. DEPLOY AKIŞI

### Branch Stratejisi
- `main` → production (Hetzner buradan deploy eder)
- `dev` → geliştirme — tüm geliştirmeler burada yapılır
- Onay sonrası `dev → main` merge ve deploy

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
/istatistik/        → istatistik.urls  (namespace='istatistik')
/analiz/            → istatistik.urls_analiz (unified konsol — /analiz/<slug>/)
                      /analiz/ → analiz_hub view (tüm araçları kategorili listeler; guest + login)
/tarama/            → tarama_hub view (yoktez, openalex, trdizin, oaipmh kartları; guest + login)
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

### Quiz Puan Sistemi
- Her doğru cevap: **10 puan** (`QuizScore.total_points += 10`)
- Teklif verme eşiği: 1000+ toplam puan (forum `reputation` + quiz `total_points`)
- `quiz-efsanesi` rozeti: 1000 doğru cevap → teklif hakkı (alternatif yol)

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
- 19 üniversite arşivi aktif endpoint (ODTÜ, İTÜ, Dokuz Eylül, Akdeniz vb.)
- `sickle` kütüphanesi (OAI-PMH client)
- **Job kuyruğu:** `job_queue.enqueue('oaipmh', job_id)` kullanır — eski raw `threading.Thread` kaldırıldı
- Stale job cutoff: 60 dakika (scraping 19 üniversiteyi tarayabilir, kısa timeout uygun değil)

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
- `FreelanceJobAdmin` — ilan yönetimi
- `JobProposalAdmin` — teklif (İlan Sahibi + Teklif Veren kolonları)
- `ProfileAdmin` — kullanıcı profil
- `SiteSettingsAdmin` — feature flag yönetimi
- `JobPaymentAdmin` — vitrin ödemeleri; `status` readonly; **"Seçili ilanları vitrine ekle"** action ile onaylanır
- `BibliometricOrderProxyAdmin` (`tezanaliz/admin.py`) — `status` readonly; **"Onayla ve Tam Rapor Emailini Gönder"** action ile onaylanır; e-posta + `status=completed` otomatik set edilir
- `AlexOrderAdmin` (`openalex/admin.py`) — OpenAlex siparişleri; `status` readonly; aynı action akışı

### Gelir Kaynakları ve Ödeme Akışları
| Gelir | Model | Admin Onay Yolu |
|---|---|---|
| Bağış (Premium) | `Donation` | Dashboard "BAĞIŞ" → detail → action yok, `dashboard_approve_donation` view |
| İlan Vitrini | `JobPayment` | Job Payments list → "Seçili ilanları vitrine ekle" action |
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
| Ödeme işlemi | iyzico altyapısı kodda var ama pasif — ödeme sistemi henüz aktif değil |
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
- **SEO — GSC index hataları düzeltmesi** (haziran 2026) — `robots.txt`'e `Disallow: /istatistik/` ve `Disallow: /jobs/` eklendi; `/istatistik/<araç>/` URL'leri canonical olarak `/analiz/<araç>/`'a işaret ediyor ama Google her iki prefix'i de tarıyordu (33 "Alternative page with canonical" hatası); `blog_list.html` canonical'den `?category=` parametresi kaldırıldı — filtreli blog sayfaları artık `/blog/`'a canonical işaret ediyor
- **Ödeme/sipariş admin düzeltmeleri** (haziran 2026) — `JobPayment.status` readonly yapıldı; `approve_feature` action `status='success'` ama `feature_status='pending'` olan kayıtları da işler; gerçek işlenen sayı mesajı düzeltildi; `Donation` modeline `pending_confirmation` status eklendi (migration 0122); `send_support_email` artık DB kaydı oluşturuyor; `mark_donation_transferred` view + URL eklendi; e-posta şablonuna "Havaleyi Yaptım" butonu eklendi; `AlexOrderProxy` + `AlexOrderAdmin` eklendi (`openalex/admin.py`) — dashboard linki düzeltildi (404 veriyordu); `BibliometricOrder.status` readonly yapıldı; Gelir Özeti'ne vitrin + biblio + openalex aylık/toplam gelir eklendi; bağış filtresi `'approved'`→`'completed'` düzeltildi; Vitrine Taşı butonu zaten vitrindekilerde gizleniyor

### Sıradaki Görevler
- **ML Araçları** — Rastgele Orman, KNN (Karar Ağacı + SVM tamamlandı)
- Sosyal kanıt iyileştirmeleri (ana sayfa — çok kolay)
- Yeni kullanıcı onboarding akışı — altyapı hazır (migration `0067_profile_onboarding`; `segment`, `onboarding_completed`, `onboarding_interests`, `onboarding_tools` alanları + `/onboarding/` view mevcut); toplanan veri henüz kullanıcı deneyimine yansıtılmıyor; **pasif bekliyor**
- Analiz araçlarında akıllı hata yönetimi — `data_validator.py` mevcut ama yalnızca Cronbach'ta aktif; araç bazlı ön kontrol + Türkçe hata mesajları eksik; **pasif bekliyor**
- Blog içerik altyapısı iyileştirmeleri
- Admin analytics dashboard (kullanıcı navigasyon takibi tamamlandı — haziran 2026)
- **Semantic Scholar → Bibliometrik Analiz entegrasyonu** — Semantic Scholar'dan BibTeX export ekle; sonuçları doğrudan `/bibliometrics/` aracına aktar; iki taraf değişiklik gerektirir (`semanticscholar/` export + `bibliometrics/` parser)
- Gamification genişletmesi
- Fiyatlandırma sayfası (iş kararı — en son)

---

*Son güncelleme: Haziran 2026 — Ödeme/sipariş admin düzeltmeleri: status readonly, bağış akışı DB kaydı + havale bildirimi, AlexOrder admin, Gelir Özeti 4 kanal. Önceki: SEO GSC hataları; Çalışma odası mesaj düzenleme/silme + @mention e-posta; migration çakışması düzeltmesi; Semantic Scholar; WoS parser; DM okundu göstergesi; Karar Ağacı + SVM.*
