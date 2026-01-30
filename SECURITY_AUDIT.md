# Analizus Güvenlik Denetim Raporu

**Tarih:** 2026-01-30
**Test Edilen:** Django Web Uygulaması
**Metodoloji:** OWASP Top 10 (2021)

---

## ÖZET

| Kategori | Durum | Risk |
|----------|-------|------|
| SQL Injection | ✅ Güvenli | Düşük |
| XSS (Cross-Site Scripting) | ⚠️ Dikkat | Orta |
| CSRF | ✅ Güvenli | Düşük |
| Broken Authentication | ✅ Güvenli | Düşük |
| Sensitive Data Exposure | ⚠️ Dikkat | Orta |
| Security Misconfiguration | ⚠️ Eksik | Orta |
| File Upload | ✅ Güvenli | Düşük |
| Rate Limiting | ❌ Yok | Yüksek |

---

## 1. SQL INJECTION - ✅ GÜVENLİ

**Bulgu:** Django ORM kullanılıyor, raw SQL yok.

```python
# Örnek güvenli sorgu (views.py)
topics = category.topics.prefetch_related('tags').annotate(...)
```

**Durum:** Django ORM otomatik parametre escape yapıyor. Risk düşük.

---

## 2. XSS (Cross-Site Scripting) - ⚠️ DİKKAT

**Bulgular:**

### 2.1 `|safe` Filtresi Kullanımları
```
forum/templates/forum/admin_dashboard.html:451 → {{ chart_labels|safe }}
forum/templates/forum/admin_dashboard.html:455 → {{ user_trend|safe }}
```
**Risk:** Admin dashboard'da. Sadece staff erişebilir, düşük risk.

### 2.2 `mark_safe` Kullanımları
```python
# forum/templatetags/forum_extras.py
return mark_safe(f'<span class="badge" style="background-color: {color};">{icon} {name}</span>')
```
**Risk:** `color` ve `name` değerleri veritabanından geliyor. Manipüle edilirse XSS mümkün.

**Öneri:**
```python
from django.utils.html import escape

return mark_safe(f'<span class="badge" style="background-color: {escape(color)};">{escape(icon)} {escape(name)}</span>')
```

---

## 3. CSRF - ✅ GÜVENLİ

**Bulgular:**
- `CsrfViewMiddleware` aktif ✅
- `{% csrf_token %}` form'larda kullanılıyor ✅
- `CSRF_TRUSTED_ORIGINS` tanımlı ✅
- `CSRF_COOKIE_SECURE = True` (production) ✅

---

## 4. AUTHENTICATION & SESSION - ✅ GÜVENLİ

**Pozitif Bulgular:**
```python
# settings.py
SESSION_COOKIE_HTTPONLY = True      ✅ JavaScript erişimi engelli
SESSION_COOKIE_SECURE = not DEBUG   ✅ HTTPS zorunlu
SESSION_COOKIE_SAMESITE = 'Lax'     ✅ CSRF koruması
SESSION_COOKIE_AGE = 86400          ✅ 1 gün timeout
```

**View Koruması:**
- 25+ endpoint `@login_required` ile korunuyor ✅
- Admin endpoint'ler `@staff_member_required` ile korunuyor ✅

---

## 5. SENSITIVE DATA EXPOSURE - ⚠️ DİKKAT

### 5.1 API Anahtarları
```python
# settings.py - Doğru yöntem kullanılıyor
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
IYZICO_API_KEY = os.getenv('IYZICO_API_KEY')
```
✅ Environment variable kullanımı doğru.

### 5.2 DEBUG Modu
```python
DEBUG = 'RENDER' not in os.environ
```
⚠️ Local'de DEBUG=True. Stack trace sızabilir.

### 5.3 Secret Key
```python
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-varsayilan-anahtar')
```
⚠️ Fallback değer güvensiz. Production'da mutlaka env'den gelmeli.

---

## 6. SECURITY MISCONFIGURATION - ⚠️ EKSİK

### 6.1 Eksik: HSTS Header
```python
# EKLENMELİ - settings.py
SECURE_HSTS_SECONDS = 31536000  # 1 yıl
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### 6.2 Mevcut Headerlar ✅
```python
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### 6.3 Eksik: Content Security Policy (CSP)
```python
# Öneri - django-csp paketi ile
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net")
```

---

## 7. FILE UPLOAD - ✅ GÜVENLİ

**Bulgular:**
```python
# settings.py
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB limit ✅
ALLOWED_ATTACHMENT_TYPES = [
    'image/jpeg', 'image/png', 'image/gif', 'image/webp',
    'application/pdf', ...
]  # Whitelist ✅

# views.py:802-808
if attachment.size > settings.MAX_UPLOAD_SIZE:
    messages.error(request, 'Dosya boyutu 5 MB\'ı geçemez.')
if attachment.content_type not in settings.ALLOWED_ATTACHMENT_TYPES:
    messages.error(request, 'Bu dosya türü desteklenmiyor.')
```

**Durum:** Boyut ve MIME type kontrolü var. ✅

**Öneri:** Magic byte kontrolü eklenebilir (python-magic ile).

---

## 8. RATE LIMITING - ❌ YOK (KRİTİK)

**Eksik:** Brute force koruması yok.

**Risk Senaryoları:**
- Login brute force
- API endpoint abuse
- Form spam
- DoS saldırıları

**Çözüm - django-ratelimit:**
```bash
pip install django-ratelimit
```

```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def login_view(request):
    ...

@ratelimit(key='user', rate='10/h', method='POST', block=True)
@login_required
def new_topic(request, slug):
    ...
```

---

## 9. EK GÜVENLİK ÖNERİLERİ

### 9.1 Django Security Checklist
```bash
python manage.py check --deploy
```

### 9.2 Dependency Güvenliği
```bash
pip install safety
safety check
```

### 9.3 Password Politikası
```python
# settings.py - AUTH_PASSWORD_VALIDATORS kontrol et
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 10}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

---

## ACİL YAPILMASI GEREKENLER

| # | Görev | Öncelik |
|---|-------|---------|
| 1 | Rate limiting ekle (django-ratelimit) | 🔴 Yüksek |
| 2 | HSTS header'ları ekle | 🟡 Orta |
| 3 | mark_safe kullanımlarını escape et | 🟡 Orta |
| 4 | CSP header ekle | 🟡 Orta |
| 5 | `python manage.py check --deploy` çalıştır | 🟢 Düşük |

---

## TEST KOMUTLARI

```bash
# Django güvenlik kontrolü
python manage.py check --deploy

# Bağımlılık güvenliği
pip install safety && safety check

# OWASP ZAP ile otomatik tarama (opsiyonel)
# docker run -t owasp/zap2docker-stable zap-baseline.py -t https://analizus.com
```

---

*Rapor: Claude Code Security Audit*
