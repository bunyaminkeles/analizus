# Email Bildirimleri Kurulumu (SMTP)

## 1. SMTP Bilgilerini Hazırlama

Email göndermek için bir SMTP sunucusuna ihtiyacınız var. Bu bilgileri email sağlayıcınızdan (örn: Hosting.com.tr, Yandex.Mail, Google Workspace) alabilirsiniz.

Gerekli bilgiler:
- **SMTP Host**: `mail.alanadiniz.com` gibi sunucu adresi
- **SMTP Port**: Genellikle `465` (SSL için) veya `587` (TLS için)
- **SMTP User**: `info@alanadiniz.com` gibi tam e-posta adresi
- **SMTP Pass**: E-posta şifreniz
- **Güvenlik Türü**: SSL veya TLS

**Örnek (hosting.com.tr):**
- **Host**: `mail.analizus.com`
- **Port**: `465`
- **User**: `info@analizus.com`
- **Pass**: `-%Yakup1992;-)**`
- **Güvenlik**: SSL

## 2. Render Environment Variables

Render Dashboard → Your Service → Environment sekmesine gidin ve aşağıdaki değişkenleri ekleyin:

```
SMTP_HOST=mail.sunucunuz.com
SMTP_PORT=465
SMTP_USER=info@alanadiniz.com
SMTP_PASS=sifreniz
DEFAULT_FROM_EMAIL="Analizus <info@analizus.com>"
```

**Önemli Ayarlar (`analizdestek/settings.py`):**

- `EMAIL_USE_SSL = True` (Eğer port 465 ise)
- `EMAIL_USE_TLS = False` (Eğer port 465 ise)

- `EMAIL_USE_SSL = False` (Eğer port 587 ise)
- `EMAIL_USE_TLS = True` (Eğer port 587 ise)

Bu ayarlar `settings.py` içinde `SMTP_PORT` değerine göre otomatik ayarlanır, ancak sunucu yapılandırmanız farklıysa kontrol etmeniz gerekebilir.

## 3. Lokal Test (Opsiyonel)

Lokalde test etmek için `.env` dosyası oluşturun:

```bash
cp .env.example .env
nano .env
```

`.env` içeriği:
```
SMTP_HOST=mail.sunucunuz.com
SMTP_PORT=465
SMTP_USER=info@alanadiniz.com
SMTP_PASS=sifreniz
DEFAULT_FROM_EMAIL="Analizus <info@analizus.com>"
```

## 4. Test

1. Render'da deploy edin
2. İki farklı kullanıcıyla test edin:
   - Kullanıcı A: Yeni bir konu açsın
   - Kullanıcı B: Konuya cevap yazsın
   - Kullanıcı A'nın e-posta adresine bildirim gitmeli

3. Özel mesaj testi:
   - Kullanıcı A: Kullanıcı B'ye özel mesaj göndersin
   - Kullanıcı B'nin e-posta adresine bildirim gitmeli

## Sorun Giderme

### Email gitmiyor:

1. **Render loglarını kontrol edin:**
   Loglarda `✅ E-posta başarıyla gönderildi:` mesajını arayın.

2. **Hata mesajları:**
   - `[Errno 101] Network is unreachable`: Render, ücretsiz planlarda bazı SMTP portlarını engelleyebilir. Sağlayıcınızın alternatif portları (örn: 2525) destekleyip desteklemediğini kontrol edin veya ücretli bir plana geçmeyi düşünün.
   - `(535, b'5.7.8 Username and Password not accepted.')`: `SMTP_USER` veya `SMTP_PASS` yanlış.
   - `[SSL: CERTIFICATE_VERIFY_FAILED]`: Sunucunun SSL sertifikasıyla ilgili bir sorun olabilir.

3. **SMTP Sağlayıcınızın Paneli:**
   - E-posta sağlayıcınızın kontrol panelinde gönderim loglarını veya hata kayıtlarını kontrol edin.
   - Güvenlik ayarlarının dışarıdan bağlantılara izin verdiğinden emin olun. Bazı sağlayıcılar, daha az güvenli uygulamalar için özel "uygulama şifreleri" oluşturmanızı gerektirebilir.

