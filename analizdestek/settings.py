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
DEBUG = 'RENDER' not in os.environ

# Sunucu adresini kabul et
ALLOWED_HOSTS = [
    'analizus.com',
    'www.analizus.com',
    'analizdestek-ai.onrender.com',
    'analizus-dev.onrender.com',  # Geliştirme ortamı
    '*.koyeb.app',  # Koyeb için eklendi
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
    'jazzmin',          # Admin paneli teması
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',  # SEO Sitemap
    # Kendi Uygulamalarımız
    'forum',
    'yoktez',
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

# Rate Limiting
RATELIMIT_VIEW = 'forum.views.ratelimit_error'


LANGUAGES = [
    ('tr', _('Turkish')),
    ('en', _('English')),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale/',
]

# --- ADMIN PANELİ AYARLARI (JAZZMIN) ---
JAZZMIN_SETTINGS = {
    "site_title": "Analizus 2050 Core",
    "site_header": "NEURAL LINK v1.0",
    "site_brand": "Analizus AI",
    "site_logo_classes": "",
    "welcome_sign": "Sistem Çevrimiçi. Hoş Geldiniz, Komutan.",
    "copyright": "Analizus Ltd.",
    "search_model": ["auth.User", "forum.Topic"],
    "site_url": "/",

    "topmenu_links": [
        {"name": "Ana Siteye Dön", "url": "home", "permissions": ["auth.view_user"]},
        {"model": "auth.User"},
    ],

    "usermenu_links": [
        {"name": "Profilim", "url": "home", "new_window": False}, 
        {"model": "auth.user"}
    ],

    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "forum.Topic": "fas fa-comments",
        "forum.Category": "fas fa-layer-group",
        "forum.Post": "fas fa-comment-dots",
    },
    "show_ui_builder": True,
    "custom_css": "css/admin_theme_v2.css",
    "custom_js": "js/admin_custom_v2.js",
}

JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",
    "dark_mode_theme": "darkly",
    "navbar": "navbar-dark",
    "sidebar": "sidebar-dark-primary",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

# --- E-POSTA AYARLARI (SendGrid HTTP API) ---
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'info@analizus.com')
EMAIL_BACKEND = 'forum.backends.SendGridBackend'

# --- IYZICO ÖDEME AYARLARI ---
IYZICO_API_KEY = os.getenv('IYZICO_API_KEY', '').strip()
IYZICO_SECRET_KEY = os.getenv('IYZICO_SECRET_KEY', '').strip()
IYZICO_BASE_URL = os.getenv('IYZICO_BASE_URL', 'sandbox-api.iyzipay.com').strip()  # Production: api.iyzipay.com

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
if not DEBUG and AWS_ACCESS_KEY_ID:
    # Production: S3 kullan
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
else:
    # Lokal geliştirme: dosya sistemi kullan
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')