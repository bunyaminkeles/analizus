import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv
from django.utils.translation import gettext_lazy as _

# .env dosyasını yükle
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Site URL (e-posta doğrulama linkleri için ve ortamı ayırt etmek için)
SITE_URL = os.getenv('SITE_URL', 'https://www.analizus.com')

# --- GÜVENLİK AYARLARI ---
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-varsayilan-anahtar')

# Canlıda Debug KAPALI olmalı.
# .env dosyasında DEBUG=False ile kapatılır (Hetzner, Render vb.)
DEBUG = os.getenv('DEBUG', 'True').lower() not in ('false', '0', 'no')

# Sunucu adresini kabul et
ALLOWED_HOSTS = [
    'analizus.com',
    'www.analizus.com',
    'analizdestek-ai.onrender.com',
    'analizus-dev.onrender.com',  # Geliştirme ortamı
    '*.koyeb.app',  # Koyeb için eklendi
    '89.167.5.224',  # Hetzner
    '127.0.0.1',
    'localhost',
]

# CSRF Güvenliği
CSRF_TRUSTED_ORIGINS = [
    'https://analizus.com',
    'https://www.analizus.com',
    'https://analizdestek-ai.onrender.com',
    'https://analizus-dev.onrender.com', # Geliştirme ortamı
    'https://analizus.onrender.com',
]

# --- UYGULAMA TANIMLARI ---
INSTALLED_APPS = [
    'daphne',           # Channels için ASGI sunucusu
    'channels',         # Gerçek zamanlı özellikler için
    'unfold',                     # Django Unfold admin teması
    'unfold.contrib.filters',     # Gelişmiş filtreler
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',  # SEO Sitemap
    # Kendi Uygulamalarımız
    'forum',
    'trdizin',
    'openalex',
    'oaipmh',
    'yoktez',
    'bibliometrics',
    'tezanaliz',
    'makaleanaliz',
    'istatistik',
    'crispy_forms',
    'crispy_bootstrap5',
    'storages',  # AWS S3 için
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'forum.middleware.HoneypotMiddleware',            # Bot honeypot kontrolü
    'forum.middleware.EmailVerificationMiddleware',  # E-posta doğrulama kontrolü
]

ROOT_URLCONF = 'analizdestek.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'forum.context_processors.profile_context',  # Profil, bildirimler vb. için
                'forum.context_processors.google_analytics',  # Google Analytics
                'forum.context_processors.feature_flags',  # Feature Flags
                'forum.context_processors.donation_context',  # Bağış paketleri (footer modal)
            ],
        },
    },
]

# WSGI_APPLICATION = 'analizdestek.wsgi.application'
ASGI_APPLICATION = 'analizdestek.asgi.application'

# --- VERİTABANI ---
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3'),
        conn_max_age=0,  # Serverless için: her istekte yeni bağlantı
        conn_health_checks=True,  # Bağlantı sağlığını kontrol et
    )
}

# --- STATİK DOSYALAR ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Canlı Ortam Güvenlik Ayarları
if not DEBUG:
    # Nginx/Render proxy arkasında SSL header'dan anla
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Sadece ana site (analizus.com) için cookie domain ayarlarını yap
    if 'analizus.com' in SITE_URL and 'onrender.com' not in SITE_URL:
        # www ve non-www arası session paylaşımı için
        SESSION_COOKIE_DOMAIN = '.analizus.com'
        CSRF_COOKIE_DOMAIN = '.analizus.com'

    # HSTS - HTTP Strict Transport Security
    SECURE_HSTS_SECONDS = 31536000  # 1 yıl
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# --- DİĞER AYARLAR ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Yönlendirmeler
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'login'

# API Anahtarları
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Scraper (Selenium)
CHROME_BINARY_PATH = os.getenv('CHROME_BINARY_PATH', None)


# Güvenlik Headerları
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Rate Limiting
RATELIMIT_VIEW = 'forum.views.ratelimit_error'


LANGUAGES = [
    ('tr', _('Turkish')),
    ('en', _('English')),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale/',
]

# --- ADMIN PANELİ AYARLARI (UNFOLD) ---
from django.urls import reverse_lazy

UNFOLD = {
    "SITE_TITLE": "Analizus | Komuta Merkezi",
    "SITE_HEADER": "Analizus Admin",
    "SITE_URL": "/",
    "SITE_ICON": None,
    "SITE_SYMBOL": "analytics",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_BACK_BUTTON": True,
    "DASHBOARD_CALLBACK": "forum.dashboard.dashboard_callback",
    "COLORS": {
        "font": {
            "subtle-light": "107 114 128",   # gray-500
            "subtle-dark": "156 163 175",    # gray-400
            "default-light": "17 24 39",     # gray-900
            "default-dark": "243 244 246",   # gray-100
            "important-light": "3 7 18",     # gray-950
            "important-dark": "249 250 251", # gray-50
        },
        "primary": {
            "50":  "238 242 255",
            "100": "224 231 255",
            "200": "199 210 254",
            "300": "165 180 252",
            "400": "129 140 248",
            "500": "99 102 241",
            "600": "79 70 229",
            "700": "67 56 202",
            "800": "55 48 163",
            "900": "49 46 129",
            "950": "30 27 75",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
        # ─── 0. HIZLI ERİŞİM ────────────────────────────────────────
        {
            "title": "Hızlı Erişim",
            "separator": False,
            "collapsible": False,
            "items": [
                {
                    "title": "Dashboard",
                    "icon": "dashboard",
                    "link": reverse_lazy("admin:index"),
                },
                {
                    "title": "Siteye Git",
                    "icon": "open_in_new",
                    "link": "/",
                },
            ],
        },
        # ─── 1. EKOSİSTEM ───────────────────────────────────────────
        {
            "title": "Ekosistem",
            "separator": True,
            "collapsible": False,
            "items": [
                {
                    "title": "Kullanıcılar",
                    "icon": "person",
                    "link": reverse_lazy("admin:auth_user_changelist"),
                },
                {
                    "title": "Profiller",
                    "icon": "badge",
                    "link": reverse_lazy("admin:forum_profile_changelist"),
                },
                {
                    "title": "Bağışlar",
                    "icon": "volunteer_activism",
                    "link": reverse_lazy("admin:forum_donation_changelist"),
                },
                {
                    "title": "Bağış Katmanları",
                    "icon": "layers",
                    "link": reverse_lazy("admin:forum_donationtier_changelist"),
                },
                {
                    "title": "İş Ödemeleri",
                    "icon": "payments",
                    "link": reverse_lazy("admin:forum_jobpayment_changelist"),
                },
            ],
        },
        # ─── 2. FORUM & İÇERİK ──────────────────────────────────────
        {
            "title": "Forum & İçerik",
            "separator": True,
            "collapsible": True,
            "items": [
                {
                    "title": "Bölümler",
                    "icon": "grid_view",
                    "link": reverse_lazy("admin:forum_section_changelist"),
                },
                {
                    "title": "Konular",
                    "icon": "forum",
                    "link": reverse_lazy("admin:forum_topic_changelist"),
                },
                {
                    "title": "Gönderiler",
                    "icon": "chat_bubble",
                    "link": reverse_lazy("admin:forum_post_changelist"),
                },
                {
                    "title": "Blog Yazıları",
                    "icon": "article",
                    "link": reverse_lazy("admin:forum_blogpost_changelist"),
                },
                {
                    "title": "Blog Kategorileri",
                    "icon": "folder",
                    "link": reverse_lazy("admin:forum_blogcategory_changelist"),
                },
                {
                    "title": "Başarı Hikayeleri",
                    "icon": "emoji_events",
                    "link": reverse_lazy("admin:forum_successstory_changelist"),
                },
                {
                    "title": "Çalışma Odaları",
                    "icon": "meeting_room",
                    "link": reverse_lazy("admin:forum_studyroom_changelist"),
                },
                {
                    "title": "Freelance İşler",
                    "icon": "work",
                    "link": reverse_lazy("admin:forum_freelancejob_changelist"),
                },
                {
                    "title": "İş Teklifleri",
                    "icon": "handshake",
                    "link": reverse_lazy("admin:forum_jobproposal_changelist"),
                },
                {
                    "title": "İş Yorumları",
                    "icon": "star_rate",
                    "link": reverse_lazy("admin:forum_jobreview_changelist"),
                },
                {
                    "title": "Günlük İpuçları",
                    "icon": "lightbulb",
                    "link": reverse_lazy("admin:forum_dailytip_changelist"),
                },
                {
                    "title": "Quiz Soruları",
                    "icon": "quiz",
                    "link": reverse_lazy("admin:forum_quizquestion_changelist"),
                },
                {
                    "title": "Rozetler",
                    "icon": "military_tech",
                    "link": reverse_lazy("admin:forum_badge_changelist"),
                },
                {
                    "title": "Yetenekler",
                    "icon": "psychology",
                    "link": reverse_lazy("admin:forum_skill_changelist"),
                },
                {
                    "title": "Konu Etiketleri",
                    "icon": "label",
                    "link": reverse_lazy("admin:forum_topictag_changelist"),
                },
                {
                    "title": "Ekip Üyeleri",
                    "icon": "groups",
                    "link": reverse_lazy("admin:forum_teammember_changelist"),
                },
            ],
        },
        # ─── 3. ARAMA & ANALİZ SERVİSLERİ ──────────────────────────
        {
            "title": "Arama & Analiz",
            "separator": True,
            "collapsible": True,
            "items": [
                {
                    "title": "OpenAlex İşleri",
                    "icon": "travel_explore",
                    "link": reverse_lazy("admin:oaipmh_alexsearchjobproxy_changelist"),
                },
                {
                    "title": "TR Dizin İşleri",
                    "icon": "search",
                    "link": reverse_lazy("admin:oaipmh_dizinsearchjobproxy_changelist"),
                },
                {
                    "title": "YÖK Tez İşleri",
                    "icon": "school",
                    "link": reverse_lazy("admin:oaipmh_yoktezsearchjobproxy_changelist"),
                },
                {
                    "title": "OAI-PMH İşleri",
                    "icon": "hub",
                    "link": reverse_lazy("admin:oaipmh_oaipmhsearchjob_changelist"),
                },
                {
                    "title": "Üniversiteler",
                    "icon": "account_balance",
                    "link": reverse_lazy("admin:oaipmh_university_changelist"),
                },
                {
                    "title": "Tez Analizleri",
                    "icon": "biotech",
                    "link": reverse_lazy("admin:tezanaliz_tezanaliz_changelist"),
                },
                {
                    "title": "Makale Analizleri",
                    "icon": "description",
                    "link": reverse_lazy("admin:tezanaliz_makaleanalizproxy_changelist"),
                },
                {
                    "title": "Bibliometrik İşler",
                    "icon": "bar_chart",
                    "link": reverse_lazy("admin:tezanaliz_bibliometricjobproxy_changelist"),
                },
                {
                    "title": "Bibliometrik Siparişler",
                    "icon": "receipt_long",
                    "link": reverse_lazy("admin:tezanaliz_bibliometricorderproxy_changelist"),
                },
            ],
        },
        # ─── 4. SİSTEM ───────────────────────────────────────────────
        {
            "title": "Sistem",
            "separator": True,
            "collapsible": True,
            "items": [
                {
                    "title": "Site Ayarları",
                    "icon": "settings",
                    "link": reverse_lazy("admin:forum_sitesettings_changelist"),
                },
                {
                    "title": "İletişim Mesajları",
                    "icon": "mail",
                    "link": reverse_lazy("admin:forum_contactmessage_changelist"),
                },
                {
                    "title": "Özel Mesajlar",
                    "icon": "lock",
                    "link": reverse_lazy("admin:forum_privatemessage_changelist"),
                },
                {
                    "title": "Gruplar",
                    "icon": "group",
                    "link": reverse_lazy("admin:auth_group_changelist"),
                },
            ],
        },
        ],  # /navigation
    },  # /SIDEBAR
}

# --- E-POSTA AYARLARI ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('SMTP_HOST')
EMAIL_PORT = int(os.getenv('SMTP_PORT', 465))
EMAIL_HOST_USER = os.getenv('SMTP_USER')
EMAIL_HOST_PASSWORD = os.getenv('SMTP_PASS')
if EMAIL_PORT == 587:
    EMAIL_USE_TLS = True
    EMAIL_USE_SSL = False
else:
    EMAIL_USE_TLS = False
    EMAIL_USE_SSL = True

DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'info@analizus.com')
# Admin bildirim e-postası — .env'de ADMIN_NOTIFICATION_EMAIL=bkeles74@gmail.com gibi ayarla
ADMIN_NOTIFICATION_EMAIL = os.getenv('ADMIN_NOTIFICATION_EMAIL', DEFAULT_FROM_EMAIL)


# --- İŞ KUYRUĞU AYARLARI ---
# Paralel iş kuyruğu — Hetzner kapasitesine göre ayarla (default: 5)
JOB_MAX_WORKERS = int(os.environ.get('JOB_MAX_WORKERS', 5))

# --- DOSYA YÜKLEME AYARLARI ---
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_ATTACHMENT_TYPES = [
    'image/jpeg', 'image/png', 'image/gif', 'image/webp',
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/csv',
    'text/plain',
]

# --- SESSION AYARLARI ---
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Database-backed sessions (çoklu worker için)
SESSION_COOKIE_AGE = 60 * 60 * 2  # 2 saat
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = not DEBUG  # Production'da HTTPS zorunlu
SESSION_SAVE_EVERY_REQUEST = True  # Her istekte session süresini yeniler
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Tarayıcı kapanınca session silinmesin

# --- CSRF AYARLARI ---
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = False  # JavaScript'in token'a erişebilmesi için
CSRF_USE_SESSIONS = False  # Cookie-based CSRF (mobile uyumlu)

# --- GOOGLE ANALYTICS ---
# GA4 Measurement ID (örn: G-XXXXXXXXXX)
GOOGLE_ANALYTICS_ID = os.getenv('GOOGLE_ANALYTICS_ID', '')

# --- SEO / SITE VERIFICATION ---
GOOGLE_SITE_VERIFICATION = os.getenv('GOOGLE_SITE_VERIFICATION', '')
BING_SITE_VERIFICATION = os.getenv('BING_SITE_VERIFICATION', '')
YANDEX_SITE_VERIFICATION = os.getenv('YANDEX_SITE_VERIFICATION', '')

# --- CACHE (django-ratelimit için worker'lar arası paylaşımlı) ---
# Redis yalnızca Channels için — cache her zaman DB (REDIS_URL yoksa çöker)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache_table",
    }
}

# --- CHANNEL (GERÇEK-ZAMANLI) AYARLARI ---
REDIS_URL = os.environ.get('REDIS_URL')

if DEBUG or not REDIS_URL:
    # Geliştirme ortamında veya Redis URL yoksa InMemory kullan
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer"
        }
    }
else:
    # Üretim ortamında, ölçeklenebilir Redis katmanını kullan
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [REDIS_URL],
            },
        },
    }

# --- AWS S3 MEDYA DOSYALARI ---
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = 'analizus-files'
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'eu-north-1')
AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN', f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com')

# S3 Güvenlik ve Performans Ayarları
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',  # 1 gün cache
}
AWS_DEFAULT_ACL = None  # Bucket policy'e bırak
AWS_S3_FILE_OVERWRITE = False  # Aynı isimli dosyaları ezme
AWS_QUERYSTRING_AUTH = False  # URL'lerde auth parametresi olmasın (public okuma için)

# Dosya boyutu limiti (5MB)
AWS_S3_MAX_MEMORY_SIZE = 5 * 1024 * 1024

# Production'da S3, lokalde dosya sistemi
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'yoktez': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'oaipmh': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

if not DEBUG and AWS_ACCESS_KEY_ID:
    # Production: S3 kullan
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
else:
    # Lokal geliştirme: dosya sistemi kullan
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')