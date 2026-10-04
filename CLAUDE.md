# Analizus.com — Claude Çalışma Kuralları

Tam sistem dokümantasyonu: `analizus.md` (proje kökünde, ~2300 satır; offset'ler 2 Ekim 2026). Tamamını okuma — ihtiyaca göre offset ile ilgili bölümü oku:

| Bölüm | offset | Konu |
|---|---|---|
| §1–2 | 8 | Proje amacı, tech stack, paketler |
| §3–5 | 68 | Sunucu mimarisi + bakım (log sınırı, disk, yedek → yerel, **deploy öncesi `yedek_indir.sh --simdi`**), deploy (deploy.sh açılışta migrate+collectstatic), env vars (NCBI_API_KEY dahil) |
| §6–7 | 284 | Dizin yapısı, URL mimarisi (i18n_patterns; `/section/` 301, `/uzmanlar/?cat=` kuralı) |
| §8–9 | 464 | Veri modelleri (`JobCategory.intro`, `Category.INDEX_MIN_TOPICS`, BlogPost SEO alanları, **pazar: ilan onayı / haftalık hak / form sınırları, profil "Hakkında", bağış `premium_days_promised`** ~552), feature flag'ler |
| §10–11 | 748 | CSS/tasarım sistemi, WebSocket (route'lar) |
| §12 | 873 | İstatistik araçları (akış, PDF, polling, **konsol düzeni**: Nedir kartı → SSS → CTA, `tool_title`) |
| §13–15 | 1033 | DM/oda mesajlaşma, bibliometri, akademik tarama (**Google'ın gördüğü başlık = view `promo_title`**) |
| §16–19 | 1263 | E-posta (500 hata e-postası), AnalizBot/AI Asistan, S3, güvenlik (çerez onayı, cron anahtarı) |
| §20–23 | 1482 | Admin (sipariş akışı, Fiyatlandırma, **Limitler, İlan onayı/ret aksiyonları + panel "İlan Onayı", bağış onayı aksiyonu**, İş Kategorisi tanıtım metni, blog SEO), pazar akışı (pending → open), session, cron |
| §24–25 | 1607 | Geliştirme ortamı (pytest 82 test + test notları, çeviri komutları), değişmez kurallar |
| §26 | 1694 | Sık yapılan hatalar ve çözümleri |
| §27 | 1797 | Görev listesi (tamamlanan / sıradaki; **en son: "2 Ekim 2026" pazar/bağış/profil turu**) |
| §28 | 2209 | Çok dilli yapı (TR/EN/DE) ve gizlilik — mimari, çeviri kuralları, iş akışı, EN/DE ürün kararları (§28.7) |

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
- Testler **pytest** ile: `docker compose exec web python -m pytest forum/tests.py` (`manage.py test` 0 test bulur)
- Container açılışında `deploy.sh` `migrate` + `collectstatic` çalıştırır — migration'lı deploy öncesi DB yedeği al: kullanıcının bilgisayarında `scripts/yedek_indir.sh --simdi` (yerele akar; sunucuda `pg_dump > /root/…` artık yapma — birikiyordu)
- Yeni app'te `makemigrations`'ı container'da çalıştırırsan `migrations/` klasörü root sahipli olur → git dal değiştiremez; klasörü host'ta aç ya da `chown -R 1000:1000` (§26)
- Fiyat/ücret **ve limit** kodda sabit YAZILMAZ — `SiteSettings` alanı + admin (tarama siparişi, vitrin, bibliometri; haftalık ilan hakkı, ilan başlık/açıklama sınırı → Limitler; §20)
- Pazar: herkese açık listeler yalnız `status='open'`; pk ile erişen view pending/rejected ilanı yalnız sahibi + staff'a gösterir. Açık ilan `approved_at` boşken kaydedilirse `FreelanceJob.save()` yeniden yayınlar (süre + hediye) — seed/test'te `approved_at` ver (§8)
- Ödül/e-posta tetikleyen durum geçişleri sinyalde (ilan pending→open/rejected, bağış →completed) — admin aksiyonunda `queryset.update` değil kayıt kayıt `save()`; söz verilen değeri (gün, fiyat) talep anında kayda yaz (§26)
- Profil formu alanları doğrulamasız kaydedilir — şablonda kullanıcı URL'si yalnız `Profile.public_links()` üzerinden (http(s) + regex)
- Dış kaynaktan (API/kazıma) gelen veri JS'te `innerHTML`'e kaçışsız yazılmaz — `_esc()`; link yalnız http(s) (§15)
- Şablon değişikliğini doğrulamadan önce `docker compose restart web` (cached loader) — yoksa eski sürüm test edilir
- API anahtarı URL'de giden istemcilerde `requests` hata metni anahtarı taşır → kullanıcıya sabit mesaj, istisnayı `api_key=***` ile yeniden fırlat (§26)
- `.env` değişikliği `restart` ile okunmaz → `docker compose up -d web`; env adını koddakiyle birebir kontrol et (`NCBI_API_KEY`)
- Hetzner `docker-compose.yml`'de commit'lenmemiş `rlprehber` var — compose'u git'te değiştirme; host ayarı `daemon.json` (§3)
- Sunucuda yalnız kullanıcı isteyince işlem; Hetzner deploy kullanıcıda. Push/merge yalnız kullanıcı açıkça isteyince ("push et", "merge et") — 2 Ekim 2026'da çalıştı; yalnız doküman/betik commit'ini push etmek gereksiz (kullanıcı)

## SEO Kritik Kurallar — ayrıntı analizus.md §12, §15, §26, `tasks/todo.md` "BÜYÜK SEO DÖNÜŞÜMÜ"
- Google (anonim) araç/tarama sayfalarında `service_promo.html` görür → başlık/açıklama/H1 view'daki `promo_title`/`promo_description`; `landing.html` blokları yalnız giriş yapmışa. Doğrulama **oturumsuz** `curl` ile
- Blog SEO: `BlogPost.meta_title`/`meta_description` (admin → yazı → en alttaki SEO); sayfadaki H1/slug'a dokunma (sıralama kaybı)
- İçerik/SEO veri migration'ı korumalı: alan doluysa yazma, içerik yalnız beklenen eski metin varsa değişir; canlı içerik yerelden farklı olabilir → canlı HTML'den oku
- İçerikte abartılı vaat yok (kullanıcı kararı): ücretsiz kısım = toplam sonuç + en yeni 5; resmî kurum izlenimi/ilişki iddiası yok; "tez yazdırma" niyeti hedeflenmez
- Ortak şablon (analiz/tarama konsolu) değişince 18 aracın hepsini Playwright ile aynı ölçütle kontrol et (sıra, boşluk, hiza, boş `tool_title`, mobil taşma) — kullanıcı tek tek bakmamalı
- Django `{# #}` tek satır; çok satır için `{% comment %}`

## Çok Dilli (i18n) Kritik Kurallar — ayrıntı analizus.md §28
- Yeni kullanıcıya görünen metin **her zaman** çeviriye işaretlenir (msgid = Türkçe); EN/DE `locale/` + `.mo` git'te
- Python+JS ortak cümlede `{ad}` süslü yer tutucu (`.format()` / JS `fmt`) — şablon `trans` `%`'yi `%%` yapar
- Parça birleştirme yok: anlamlı/anlamsız, artış/azalış ayrı **tam cümle** msgid
- Çevrilen görünen metinle `==`/`!==` karşılaştırma yapma (bayrak kullan: ör. `is_const`)
- Arka plan işi (job_queue thread) dili bilmez — `translation.override` ile taşı; e-posta: `recipient_language(user)`
- Çeviri sonrası `compilemessages` çıktısında `error` ara; polib'de `previous_*` alanlarının üçünü temizle. Container'da msgfmt yoksa (imaj build sonrası) host'ta `msgfmt -c -o …mo …po`
- API'sine doğrudan bağlı paketlere `requirements.txt`'te sürüm sabitle (sürümsüz `bibtexparser` 2.x gelip BibTeX'i kırdı)
- Türkçe metin taraması yalnız ç/ğ/ş… harflerine bakamaz ("Yorum", "Hesapla" kaçar) — tüm sabitleri listele
- Eksik çeviri taramasında `.py` dosyalarını `ast` ile oku — regex çok satırlı (bitişik) string'lerin yalnız ilk parçasını yakalar

## Git & Deploy
- Tüm geliştirme `dev` branch'inde — `main`'e kullanıcı "merge et" demeden dokunma
- `dev` → **Render** (push'ta otomatik deploy — staging/preview)
- `main` → **Hetzner** (manuel deploy — production); merge: `git merge --no-ff dev` ("Merge branch 'dev': …"), sonra `dev`'e dön
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
