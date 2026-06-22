# Analizus.com — Claude Çalışma Kuralları

Tam sistem dokümantasyonu: `analizus.md` (proje kökünde, ~1240 satır). Tamamını okuma — ihtiyaca göre offset ile ilgili bölümü oku:

| Bölüm | offset | Konu |
|---|---|---|
| §1–2 | 8 | Proje amacı, tech stack, paketler |
| §3–5 | 68 | Sunucu mimarisi, deploy, env vars |
| §6–7 | 223 | Dizin yapısı, URL mimarisi |
| §8–9 | 359 | Veri modelleri, feature flag'ler |
| §10–11 | 512 | CSS/tasarım sistemi, WebSocket |
| §12 | 582 | İstatistik araçları (akış, PDF, polling) |
| §13–15 | 722 | DM/oda mesajlaşma, bibliometri, akademik tarama |
| §16–19 | 848 | E-posta, AnalizBot, S3, güvenlik |
| §20–23 | 964 | Admin, pazar iş akışı, session, cron |
| §24–25 | 1045 | Geliştirme ortamı, değişmez kurallar |
| §26 | 1124 | Sık yapılan hatalar ve çözümleri |
| §27 | 1158 | Görev listesi (tamamlanan / sıradaki) |

---

## KIRMIZI ÇİZGİ — DEĞİŞİKLİK KISITLARI

1. **Kapsam dışına çıkma.** İstenen dosya/satır dışında hiçbir şeye dokunma. "İyileştirme" fırsatı görsen bile yapma — ayrı görev olarak sor.
2. **Birden fazla dosya değişecekse önce listele, onay al, sonra uygula.**
3. **Değişiklik yapmadan önce ilgili dosyayı oku.** Tahmin yürütme.
4. **Bir şeyi düzeltirken başka şeyi bozma.** Şüpheliysen sor.
5. **Her değişiklik sonrası dur ve onay bekle.** Tek seferde tek görev.

> Bu kuralları ihlal etmek, doğru çözümden daha büyük zarar verir.

---

## CSS / Tasarım (ax- sistemi)
- Bootstrap yalnızca grid: `container`, `row`, `col-*`
- UI elementleri (`btn`, `card`, `badge`, `alert`) → `ax-` prefix'li özel sınıflar, Bootstrap bileşenleri kullanma
- Renk/spacing → `var(--ax-primary)` CSS değişkeni, asla hardcode renk/pixel yazma
- JS → `data-bs-toggle` yerine vanilla event listener

## Çalışma Prensipleri
- Tahmin yürütme — ilgili dosyayı oku, sonra yaz
- Her değişiklik sonrası dur ve onay bekle; tek seferde tek görev
- Migration gerekiyorsa mutlaka söyle (production DB etkilenir)
- Belirsizlik olunca sor — fiyat, oran, limit gibi iş kararlarını varsayma
- N+1 sorgu yasak — `select_related` / `prefetch_related` zorunlu
- `conn_max_age=0` — long-running transaction'dan kaçın
- Kullanıcıya görünen tüm metinler Türkçe ve akademik dile uygun

## Kritik Non-obvious Kurallar
- E-posta env var: `SMTP_*` prefix — `EMAIL_HOST` değil (`settings.py` içinde map'leniyor)
- `conf_int()` sonucunu `np.array()` ile sar — statsmodels versiyona göre DataFrame veya ndarray döner
- `result_data` kaydetmeden önce `inf`/`nan` temizle → JSON save patlar
- Polling URL: `STATUS_TEMPLATE.replace(sentinel, jobId)` — `STATUS_BASE + jobId + '/'` double slash üretir
- Docker'da migration: `docker compose exec web python manage.py migrate` — host'ta `db` hostname çözülmez
- `docker compose restart web` sonrası nginx da restart edilmeli (IP cache sorunu)
- `docker-compose` değil `docker compose` (Hetzner'de plugin kurulu, eski binary yok)

## Git & Deploy
- Tüm geliştirme `dev` branch'inde — `main`'e kullanıcı "merge et" demeden dokunma
- `dev` → **Render** (push'ta otomatik deploy — staging/preview)
- `main` → **Hetzner** (manuel deploy — production)
- Commit mesajları: `feat:`, `fix:`, `refactor:` prefix (Türkçe veya İngilizce)
- `.env` değerlerini commit'e dahil etme

**Her zaman hatırla: Kullanıcılar analiz sonuçlarına güvenmek zorunda — hızlı değil, doğru.**

---

## Workflow Orchestration

### 1. Plan Mode Default

- Önemsiz olmayan HER görev için plan moduna gir (3+ adım veya mimari kararlar)
- Bir şeyler ters giderse DUR ve hemen yeniden planla — ısrarla devam etme
- Plan modunu yalnızca üretim için değil, doğrulama adımları için de kullan
- Belirsizliği azaltmak için önceden detaylı spec yaz

### 2. Subagent Stratejisi

- Ana context penceresini temiz tutmak için subagent'leri bolca kullan
- Araştırma, keşif ve paralel analizleri subagent'lere devret
- Karmaşık problemlerde subagent'ler aracılığıyla daha fazla hesaplama gücü kullan
- Odaklı çalışma için her subagent'e tek görev ver

### 3. Öz-İyileştirme Döngüsü

- Kullanıcıdan HERHANGİ bir düzeltme geldikten sonra: `tasks/lessons.md` dosyasını kalıpla güncelle
- Aynı hatayı önleyen kurallar yaz
- Hata oranı düşene kadar bu dersleri amansızca gözden geçir
- İlgili proje için oturum başında dersleri incele

### 4. Tamamlamadan Önce Doğrulama

- Çalıştığını kanıtlamadan görevi asla tamamlanmış sayma
- Gerektiğinde main ile değişikliklerindeki davranış farkını karşılaştır
- Kendine sor: "Bir senior engineer bunu onaylar mıydı?"
- Test çalıştır, log kontrol et, doğruluğu göster

### 5. Zarafet Talebi (Dengeli)

- Önemsiz olmayan değişiklikler için dur ve "daha zarif bir yol var mı?" diye sor
- Bir düzeltme hack gibi hissettiriyorsa: "Şu an bildiklerimin hepsiyle zarif çözümü uygula"
- Basit ve açık düzeltmelerde bunu atlat — aşırı mühendislik yapma
- Sunmadan önce kendi çalışmanı sorgula

### 6. Otonom Hata Düzeltme

- Bir hata raporu geldiğinde: sadece düzelt. El tutma isteme
- Log'lara, hatalara, başarısız testlere bak — sonra çöz
- Kullanıcı tarafında sıfır bağlam geçişi gereksin
- Nasıl yapılacağı söylenmeden başarısız CI testlerini düzelt

---

## Görev Yönetimi

1. **Önce Planla**: Planı işaretlenebilir maddelerle `tasks/todo.md`'ye yaz
2. **Planı Doğrula**: Uygulamaya başlamadan önce kontrol et
3. **İlerlemeyi Takip Et**: Tamamlandıkça maddeleri işaretle
4. **Değişiklikleri Açıkla**: Her adımda üst düzey özet ver
5. **Sonuçları Belgele**: `tasks/todo.md`'ye inceleme bölümü ekle
6. **Dersleri Yakala**: Düzeltmelerden sonra `tasks/lessons.md`'yi güncelle

---

## Temel Prensipler

- **Önce Sadelik**: Her değişikliği olabildiğince basit yap. Minimal kod etkisi.
- **Tembellik Yok**: Kök nedeni bul. Geçici düzeltme yok. Senior developer standartları.
- **Minimal Etki**: Değişiklikler yalnızca gerekliye dokunsun. Hata sokmaktan kaçın.
