# [ÖNCELİKLİ] Local Docker Ortamı — nginx crash-loop + yanlış DB fallback

**Durum:** TAMAMLANDI (23 Temmuz 2026) — nginx crash-loop çözüldü, DB fallback
çözüldü. Aşağıdaki "Önerilen düzeltme" bölümü artık geçmiş kayıt.

## Bulgular

**1. nginx sürekli restart oluyor (`docker compose ps` → `Restarting (1)`)**
Log (`docker compose logs nginx`): her ~60 saniyede bir
`cannot load certificate "/etc/letsencrypt/live/analizus.com/fullchain.pem"`
hatasıyla çöküyor. Kök neden: `docker-compose.yml:41` production nginx config'ini
(`./nginx/conf.d` — Let's Encrypt sertifika yolu bekliyor) mount ediyor, ama bu
sertifika yerel makinede yok (yalnızca Hetzner'de var).

Zaten 13 Temmuz'da (10 gün önce) bunun için bir local override hazırlanmış ama
hiç bağlanmamış: `nginx/conf.d.local/local.conf` (untracked dosya, git'e hiç
eklenmemiş) self-signed sertifika (`/etc/nginx/local-ssl/selfsigned.crt`)
kullanacak şekilde yazılmış — ama:
  - `docker-compose.yml` hâlâ `./nginx/conf.d`'yi mount ediyor, `conf.d.local`'ı değil
  - Self-signed sertifika dosyaları (`selfsigned.crt`/`.key`) henüz üretilmemiş,
    docker-compose.yml'de mount edilecek bir volume de tanımlı değil

**2. Web container Postgres yerine SQLite'a düşüyor**
`.env:9` içinde `DATABASE_URL` satırı yorumlu (`# DATABASE_URL=postgres://...`).
`analizdestek/settings.py:124-129`'daki `dj_database_url.config(default='sqlite:///...')`
bu yüzden sessizce `db.sqlite3`'e fallback yapıyor — halbuki `analizdestek-db-1`
(Postgres) container'ı zaten ayakta ve çalışıyor, web ona hiç bağlanmıyor.
Bu yüzden shell'den sorgulanan sayılar (ör. `FreelanceJob` tamamlanan iş sayısı)
yanlış/boş çıktı verdi — gerçek veri kaybı DEĞİL, yanlış DB'ye bağlanma sorunu.

## Önerilen düzeltme — TÜMÜ TAMAMLANDI (bkz. aşağıdaki "nginx düzeltmesi +
KRİTİK git-güvenlik düzeltmesi" ve "Madde 3 sonucu" bölümleri için uygulama
detayları). Bu blok artık geçmiş kayıt.

## nginx düzeltmesi + KRİTİK git-güvenlik düzeltmesi (23 Temmuz 2026, TAMAMLANDI)

Self-signed sertifika üretildi (`openssl req -x509 ...` → `nginx/local-ssl/
selfsigned.crt`+`.key`, 825 gün geçerli, `.gitignore`'a eklendi — makineye
özel, commit edilmeyecek).

**⚠️ ÖNEMLİ BULGU — `docker-compose.yml` Hetzner ile PAYLAŞILAN tek dosya:**
`analizus.md` §3 doğruladı: Hetzner production da `git pull origin main` ile
aynı `docker-compose.yml`'i çekip `docker compose` ile çalıştırıyor (container
adları `app-web-1`/`app-db-1`/`app-nginx-1`, aynı `web`/`db`/`nginx` servis
isimleri). İlk denemede nginx volume mount'unu VE `web` servisine bir
`environment: DATABASE_URL: ...` override'ını doğrudan bu paylaşılan dosyaya
yazmıştım — bu, Hetzner'in `main`'e merge sonrası `git pull` yapmasıyla
**production nginx'ini (Let's Encrypt yerine self-signed/local config) ve
olası DB bağlantısını kırma riski** taşıyordu (Docker Compose'da `environment:`
her zaman `env_file`'dan önceliklidir — Hetzner'in gerçek `.env`'indeki
`DATABASE_URL`'i sessizce ezebilirdi).

**Düzeltme:** `docker-compose.yml` **main ile birebir aynı** hale geri
döndürüldü (`diff <(git show main:docker-compose.yml) docker-compose.yml` →
fark yok, doğrulandı). Tüm local-only override'lar (`web.environment.
DATABASE_URL`, `nginx.volumes` → `conf.d.local`+`local-ssl`) yeni bir
**`docker-compose.override.yml`** dosyasına taşındı — Docker Compose bunu
`docker compose up`'ta otomatik yükler (ekstra `-f` bayrağı gerekmez) ama
dosya `.gitignore`'a eklendiği için **hiçbir zaman commit'lenmez, Hetzner'e
asla ulaşmaz**. Doğrulama: `docker compose config` ile birleşmiş ayarlar
kontrol edildi (DATABASE_URL doğru, nginx conf.d.local+local-ssl doğru),
`docker compose up -d` sonrası hem Postgres bağlantısı (`ENGINE: postgresql`)
hem nginx (`https://localhost/` → 200, restart döngüsü yok) çalışır durumda.

**Ders (gelecek oturumlar için kritik):** `docker-compose.yml` Hetzner
production'da da kullanılan paylaşılan bir dosya — local-only ayarlar asla
doğrudan bu dosyaya yazılmamalı, her zaman gitignore'lu bir
`docker-compose.override.yml`'e (veya benzeri) izole edilmeli. `nginx/conf.d.
local/local.conf` (sertifika/secret içermiyor) git'e eklenip commit'lendi —
gelecekte tekrar kurulum gerekmesin diye.

**Sonuç:** `docker compose ps` → 4 container da stabil (`db` healthy, `redis`/
`web`/`nginx` Up, hiçbiri restart döngüsünde değil).

## Madde 3 sonucu — TAMAMLANDI (23 Temmuz 2026)
"Tamamlanan pazar talebi istatistikleri" (FreelanceJob completed count)
sorunu çözüldü, 3 katmanlı kök neden bulundu ve düzeltildi:

1. `.env`'de `DATABASE_URL=postgres://bunyamin:analizus@db:5432/analizus`
   eklendi (satır yorumdan çıkarıldı) — web artık SQLite'a değil Postgres'e
   bağlanıyor.
2. **Yeni bulgu:** Bağlantı denenince şifre hatası çıktı — `app_postgres_data`
   volume'ü daha önce farklı bir şifreyle init edilmiş olduğundan `bunyamin`
   rolünün gerçek şifresi `.env`'deki değerle uyuşmuyordu. Yerel unix socket
   üzerinden (`docker exec -u postgres analizdestek-db-1 psql -U bunyamin -d
   analizus`) bağlanılıp `ALTER ROLE bunyamin WITH PASSWORD 'analizus';` ile
   düzeltildi.
3. **Yeni bulgu:** Şifre düzelince DB'nin 107 migration geride olduğu ortaya
   çıktı (forum uygulaması `0068`'de kalmıştı — `seed_initial_users`,
   `freelancejob` alan eklemeleri gibi kritik migration'lar uygulanmamıştı).
   Local/dev DB olduğu için (production etkilenmiyor)
   `docker compose exec web python manage.py migrate` çalıştırıldı, hepsi
   başarıyla uygulandı (`showmigrations` artık 0 bekleyen gösteriyor).

**Yan etki — istenmeyen e-posta patlaması (23 Temmuz 2026, aynı gün çözüldü):**
`docker compose restart web` iki kez çalıştırıldı (madde 1 ve madde 3 sonrası
doğrulama için). `Dockerfile` CMD'si her başlangıçta `deploy.sh`'i çalıştırıyor;
`deploy.sh` "DB boşsa seed yükle" idempotency kontrolü (`Topic.objects.count()`)
kullanıyor. İkinci restart'ta Postgres'e ilk kez gerçekten bağlanıldığı ve forum
tabloları taze/boş olduğu için bu kontrol "boş" algıladı, `load_seed_content`
gerçek `User.objects.create_user()` ile ~78 sahte kullanıcı oluşturdu →
`forum/signals.py:578` `post_save` sinyali → `notify_admin_new_user` →
**gerçek SMTP** (`.env`'deki `mail.analizus.com`) üzerinden admin'in gerçek
Gmail'ine (`ADMIN_NOTIFICATION_EMAIL`) ~78 ayrı e-posta gitti (her biri ayrı
async thread, birkaç dakikaya yayılarak ulaştı). Kaynak süreç kendi kendine
bitti, kalıcı bir hata değildi — bir daha aynı restart'ta tekrar tetiklenmez
çünkü DB artık boş değil (idempotency guard tutar).

**Kök neden düzeltmesi — host/Docker DB ayrışması (23 Temmuz 2026, TAMAMLANDI):**
Yukarıdaki 1. maddede `.env`'e yazılan `DATABASE_URL=postgres://...@db:...`
host'ta (`.venv`/conda ile) normal `python manage.py runserver` çalıştıran
günlük local iş akışını kırdı — `db` hostname'i yalnızca docker-compose
network'ünde çözülüyor (`could not translate host name "db"`).
`analizus.md` §24 ("DATABASE_URL boş bırak, SQLite kullanılır" — host için
dokümante edilmiş varsayılan) ile §26 ("host Docker servis adı olmalı" — bu
kural Docker/prod bağlamı için) referans alınarak iki ortam ayrıştırıldı:
- `.env`'deki `DATABASE_URL` tekrar yorum satırına döndürüldü (host →
  SQLite, eski/dokümante davranış).
- `docker-compose.yml`'de `web` servisine `environment: DATABASE_URL:
  postgres://${POSTGRES_USER:-bunyamin}:${POSTGRES_PASSWORD:-analizus}@db:
  5432/${POSTGRES_DB:-analizus}` override'ı eklendi (yalnızca container için
  Postgres, `env_file`'daki boş değeri ezer).
Doğrulandı: `docker compose up -d web` sonrası container hâlâ Postgres'e
bağlı (`ENGINE: postgresql`, `NAME: analizus`); bu recreate'te `deploy.sh`
seed adımı tekrar denedi ama kaynak `.md` dosyaları bulunamadığından
(`AnalizDestek_Forum_Seed_Content.md` yok) hiç yeni kullanıcı oluşturmadı,
kullanıcı sayısı 97'de sabit kaldı — **yeni e-posta gitmedi**.

**/market/ istatistik bandının local'de görünmemesi — bug DEĞİL, kasıtlı
sıfır kuralı (23 Temmuz 2026, doğrulandı):** Kullanıcı local'de `/market/`
sayfasındaki "Tamamlanan İş / Aktif Uzman / Son 90 Gün" üçlü sayaç bandının
hiç görünmediğini bildirdi. İnceleme: `forum/views.py:450-456`'daki
`market_stats` (`total_completed`, `recent_completed`, `total_experts`) ve
`forum/templates/forum/market/job_list.html:65` `{% if market_stats.
total_completed or market_stats.total_experts or market_stats.
recent_completed %}` — template yorumu bunu zaten "sıfır kuralı: üçü de 0
ise şerit gizli" diye adlandırıyor. Local Postgres DB'de `FreelanceJob` ve
`JobProposal` tabloları tamamen boş (0 kayıt, yukarıdaki DB fallback
sorunundan bağımsız — local ortamda hiç gerçek pazar verisi girilmemiş)
olduğu için üçü de 0 çıkıyor, şerit kasıtlı olarak gizleniyor. Kod tarafında
hata/cache bayatlığı/isim uyuşmazlığı yok. Ana sayfadaki `showcase_jobs`
(views.py:284-299) de aynı sebeple boş. **İş gerekmiyor** — local'de gerçek
iş ilanı/teklif verisi oluşturulursa bant otomatik görünür.

**Sonuç:** `FreelanceJob.objects.count()` artık hatasız çalışıyor, sonuç **0**.
Repo kökündeki `yedek_2026-07-13.sql` yedeği de kontrol edildi — orada da
yalnızca 1 kullanıcı (admin) ve 0 iş var. Yani local ortamda hiçbir zaman
gerçek pazar verisi olmamış; "0 tamamlanan iş" artık **doğru** sonuç,
önceki yanlış/boş çıktı tamamen yanlış DB bağlantısından kaynaklanıyordu.

## Sıradaki adım
Yok — sertifika üretimi de (bkz. yukarı "nginx düzeltmesi" bölümü, 23 Temmuz
2026) dahil tüm maddeler tamamlandı, doğrulandı: 31 Temmuz 2026 itibarıyla
`docker compose ps` 4 container da stabil, nginx restart döngüsünde değil.

---

# Bootstrap Kaldırma — Kademeli Migration Planı

**Durum:** Envanter çıkarıldı, uygulama henüz başlamadı. (Temmuz 2026)

## Neden gerekli
CLAUDE.md kuralı "Bootstrap yalnızca grid için" diyor ama gerçek kod bunu ihlal
ediyor — Lighthouse'un "kullanılmayan CSS 111 KiB / kullanılmayan JS 164 KiB"
bulgusunun kaynağı bu. Ayrıca Google Fonts/Bootstrap CDN cache-control süresi
bizim kontrolümüzde değil (Lighthouse "verimli önbellek" bulgusu, 177 KiB).

## Envanter (temmuz 2026 taraması)
- **102 template dosyası** Bootstrap component class kullanıyor (`btn`, `card`,
  `badge`, `alert`, `modal`, `dropdown`, `form-control`, `form-select`)
- **13 dosya** `data-bs-toggle`/`data-bs-target`/`data-bs-dismiss` kullanıyor
  (Bootstrap JS bundle'a bağımlı — modal/dropdown açma-kapama)
- **96 dosya** grid class'ı (`container`/`row`/`col-*`) kullanıyor
- **3 dosya** JS'te doğrudan `new bootstrap.Modal(...)` / `bootstrap.Dropdown`
  API'sini çağırıyor: `forum/templates/forum/success_stories.html`,
  `static/js/notifications.js`, `templates/base.html`
- En ağır kullanan dosyalar: `hangi_test.html` (144), `base.html` (127),
  `studyroom_detail.html` (117), `tezanaliz/landing.html` (97),
  `istatistik/korelasyon.html` (93), `market/job_detail.html` (93)

## Mevcut ax- sistem durumu (static/css/)
Var olan: `.ax-btn` (base.css), `.ax-card` (cards.css), `.ax-badge` (8 tanım,
cards.css/profiles.css/home_sections.css'e dağılmış)

Eksik — inşa edilmesi gereken: `.ax-alert`, `.ax-modal`, `.ax-dropdown`,
`.ax-form-control`/`.ax-form-select`/`.ax-form-check`, `.ax-tooltip`,
`.ax-toast`, `.ax-collapse`/`.ax-tab`

## Fazlar

### Faz 1 — Eksik ax- CSS bileşenlerini inşa et (sıfır görsel etki) — TAMAMLANDI
`static/css/base.css`'e 4 yeni bölüm eklendi (7. Alert, 8. Modal, 9. Dropdown,
10. Form Controls — dosya sonu Responsive Utilities artık 11), mevcut
numaralandırma/token/isimlendirme deseni takip edildi. Hiçbir template
değiştirilmedi.
- `.ax-alert` (+ success/danger/warning/info varyantları)
- `.ax-modal` (backdrop + dialog + header/body/footer, `.is-open` toggle)
- `.ax-dropdown` (site-nav'daki `.site-nav__dropdown*` ile aynı görsel dil,
  genel kullanım için ayrı isimlendirildi — `.ax-dropdown-wrap`/`.ax-dropdown`)
- `.ax-form-control` / `.ax-form-select` / `.ax-form-check` (+ `.ax-form-group`,
  `.ax-form-label`, `.ax-form-hint`)

**Not — "sıfır görsel etki" tam sağlanamadı, bilinçli olarak kabul edildi:**
Uygulamadan önce tarama yapıldı, 2 sayfa zaten bu class isimlerini
kullanıyor ama hiçbir CSS tanımı yoktu (çıplak/stilsiz kullanım):
- `yoktez/templates/yoktez/results.html` (54, 192. satır) —
  `ax-alert ax-alert--danger` artık gerçekten stillenecek
- `istatistik/templates/istatistik/anova.html` (61, 66. satır) —
  `ax-form-control` artık gerçekten stillenecek

Kullanıcı onayıyla bug-fix niteliğinde kabul edildi. **TODO: bu 2 sayfa
tarayıcıda görsel doğrulanmalı** (deploy sonrası).

Çakışma olmayan (kontrol edildi, dokunulmadı): `ttesti.html`/`hangi_test.html`
kendi `.ax-form-control` tanımına sahip (body içindeki `<style>` bloğu,
cascade'de kazanıyor); `normallik.html` vb. istatistik sayfaları tek tireli
`ax-alert-danger`/`ax-alert-info` kullanıyor (farklı isim, çakışmıyor);
`hangi_test.html`'in `.ax-modal-overlay/-dialog` yapısı tamamen ayrı
isimlendirme.

### Faz 2 — Vanilla JS modal/dropdown controller — TAMAMLANDI (modal+dropdown)
**Kapsam kullanıcı onayıyla daraltıldı:** `notifications.js`'teki
`bootstrap.Toast` kapsam dışı bırakıldı — gerçekte Modal/Dropdown değil Toast
kullanıyordu, `.ax-toast` CSS'i Faz 1'de yok, ayrı görev olarak aşağıda not
edildi.

**Yapılanlar:**
- `static/js/ax-modal.js` (yeni) — `data-ax-toggle="modal"` / `data-ax-target`
  / `data-ax-dismiss="modal"` deseni + backdrop tıklama + Escape ile kapatma +
  `.ax-no-scroll` scroll kilidi + `window.AxModal.open/close` programatik API.
- `static/js/ax-dropdown.js` (yeni) — `.ax-dropdown-wrap`/`[data-ax-dropdown]`
  için genel controller, `navbar.js`'e dokunmadan ayrı çalışır. **Henüz hiçbir
  template kullanmıyor** — Faz 3 migration'larında kullanılacak, şimdilik no-op.
- `templates/base.html` — 4 modal (`searchModal`, `quizModal`, `profileModal`,
  `storyModal`) markup'ı `.ax-modal-backdrop`/`.ax-modal`/`.ax-modal__*`'e
  taşındı; 3 `new bootstrap.Modal()` çağrısı `AxModal.open(el)` ile değiştirildi;
  arama tetikleyicisi `data-ax-toggle`'a geçti. Modal içeriği (quiz butonları,
  badge'ler, spinner-border) kasıtlı olarak Bootstrap class'larıyla bırakıldı
  — o Faz 3'ün kapsamı (component migration), Bootstrap CSS/JS Faz 4'e kadar
  zaten yüklü kalacak.
- `forum/templates/forum/success_stories.html` — `shareStoryModal` aynı şekilde
  taşındı, `bootstrap.Modal(...).show()` → `AxModal.open(...)`.

**Bilinçli küçük görsel sapmalar (doğrulama listesine eklendi):**
- `profileModal`/`storyModal`'ın özel inline arka plan renkleri
  (`rgba(15,23,42,.95)`, gradient) kaldırıldı, `.ax-modal`'ın standart koyu
  arka planı kullanılıyor — görsel olarak çok yakın ama birebir aynı değil.
- `base.html`:511'deki mesaj `alert`/`data-bs-dismiss="alert"` kasıtlı
  dokunulmadı — bu Bootstrap'ın Alert bileşeni (Modal/Dropdown değil),
  kapsam dışı.

**Görsel doğrulama — TAMAMLANDI.** İlk testte modallar gizlenmedi, sayfa
akışının içinde çıplak görünüyorlardı — sebep `base.css`'in cache-busting
versiyonunun (`?v=0100`) Faz 1/2 içerik değişikliklerine rağmen artırılmamış
olmasıydı (bkz. `tasks/lessons.md`). `templates/base.html`'de `?v=0101`'e
yükseltilip tarayıcı yenilendikten sonra kullanıcı doğruladı: sorun düzeldi.

### Faz 3 — Template migration (dosya dosya, düşük riskliden başla) — BAŞLADI
Öncelik sırası: az Bootstrap class'ı olan → çok olan. Her dosya değişikliği
ayrı görev olarak onaya sunulmalı (CLAUDE.md kırmızı çizgi). Her dosyadan
sonra tarayıcıda görsel doğrulama yapılmalı.
- Grid-only sayfalar önce (sadece container/row/col — risk düşük)
- Sonra btn/card/badge kullanan sayfalar (ax- karşılığı zaten var)
- En son modal/dropdown/form kullanan ağır sayfalar (job_detail.html,
  hangi_test.html, studyroom_detail.html, istatistik araçları)

**ÖNEMLİ BULGU (kullanıcı onayıyla kapsam dışı bırakıldı, ayrıca not):**
`profile_private.html` incelenirken görüldü — "grid-only" kategorisinde
gerçek proje dosyası yok (tek eşleşme `aws/dist/awscli/...` idi, 3. parti
kütüphane, proje template'i değil). Ayrıca component class'ı (btn/card/badge)
migrate edilmiş dosyalarda bile Bootstrap **utility** class'ları (`d-flex`,
`text-white`/`text-muted`, `fw-bold`, `mb-*`/`py-*`/`px-*`, `gap-*`,
`rounded-*`, `shadow-*`, `bg-*`, `border-*`) hâlâ yaygın — bunlar CLAUDE.md'nin
"Bootstrap yalnızca grid için" kuralına göre onaylı değil ve **Faz 4'te
CDN kaldırılınca bunlar da kırılır**, sadece modal/dropdown/form değil.
Karar: Faz 3 şimdilik dar tutuldu (sadece component class migration).
Utility class migration'ı **Faz 4'ten önce ayrı bir alt görev olarak**
ele alınmalı — envanteri henüz çıkarılmadı.

**AYRI BULGU — float buton z-index/konum çakışması (Bootstrap kaldırma
kapsamı dışı):** Kullanıcı bildirdi — sayfa dar ekranda (yarım pencere)
görüntülenince sağ alttaki float butonlar (Destekçi/donate, "AI Asistan",
WhatsApp "Proje hakkında konuşalım") üst üste biniyor, biri diğerini
kapatıyor. Mobil öncelikli ([[feedback_mobile_first]] memory) gözden
geçirilmeli — muhtemelen aynı `position: fixed; bottom/right` offset'i
paylaşıyorlar, responsive stacking/offset eksik. Henüz araştırılmadı,
kök neden dosyası bulunmadı. Ayrı bir görev olarak ele alınacak.

**İlk migrate edilen component-density sıralaması (en düşükten):**
`story_modal_content.html` (1, ama 2 farklı kopyası var — `templates/` ve
`templates/forum/partials/`, senkron değiller), `account_delete.html` (2),
`donation_success.html` (3), `job_list.html` (3), `profile_detail.html` (3).

**Dosya bazlı ilerleme:**
- [x] `forum/templates/forum/account_delete.html` — tek değişiklik:
  `btn btn-danger` → `ax-btn ax-btn--danger` (40. satır). Yeni CSS gerekmedi,
  `.ax-btn--danger` zaten vardı. **Görsel doğrulama TAMAMLANDI** —
  `/account/delete/` sayfasında kullanıcı ekran görüntüsüyle onayladı.
- [x] `forum/templates/forum/donation_success.html` — 3 değişiklik:
  `card`→`ax-card` (9. satır), `card-body` kaldırıldı (10. satır, `p-5`
  zaten padding sağlıyordu), `btn`→`ax-btn` (60. satır, inline gradient
  stili korundu). Utility class'lara dokunulmadı. **Görsel doğrulama
  TAMAMLANDI** — `/donation/success/` sayfasında kullanıcı ekran
  görüntüsüyle onayladı, kart/padding/buton hiç bozulmamış.
- [ ] Sıradaki aday: `job_list.html` (3 component)

**Not (temmuz 2026) — yeni sayfalar envanteri büyütmedi:** Bu oturumda
oluşturulan `forum/templates/forum/contact.html` (İletişim landing page) ve
`forum/templates/forum/gizlilik_politikasi.html` (KVKK sayfası) sıfırdan
`ax-*` sistemiyle yazıldı — migrasyon kapsamına eklenecek yeni Bootstrap
component borcu yok. Tek istisna: KVKK sayfasındaki tablo ilk halde
`table table-dark table-borderless` ile yazılmıştı, aynı oturumda fark edilip
(`table-dark`'ın `--bs-table-bg`/`--bs-table-color` değişkenleri inline
satır renkleriyle çakışıp okunaksız görünüyordu) `.ax-kvkk-table`'a
taşındı — yani net etki: envantere yeni satır eklenmedi.

**Not (temmuz 2026) — cache-busting dersi tekrar uygulandı:** Navbar logosuna
eklenen "Analizus" yazısının puntosu `navbar.css`'te iki kez büyütüldü, ama
`templates/base.html:93`'teki `?v=0103` versiyon string'i ilk seferinde
artırılmayı unutuldu — kullanıcı production'da değişikliği göremeyince fark
edildi, `?v=0104`'e çekilip düzeltildi. Bu, §26'daki "CSS değişikliği
production'da görünmüyor" hatasının canlı bir tekrarı; her `static/css/*.css`
değişikliğinde ilgili `<link>` versiyon string'inin de artırılması gerektiği
bir kez daha teyit edildi.

### Faz 4 — Bootstrap CDN'i kaldır
`base.html`'den `bootstrap.min.css` + `bootstrap.bundle.min.js` linklerini
sil. Tüm sayfalarda regresyon taraması (özellikle modal/dropdown/form
davranışları).

### Faz 5 — Temizlik
Kullanılmayan geçiş dönemi shim'leri varsa kaldır.

## Riskler
- Modal/dropdown JS davranışı görsel olarak sessiz kırılabilir (constructor
  hatası fırlatmaz, sadece tıklama işe yaramaz) — her migration adımından
  sonra manuel tıklama testi şart
- Form control stilleri (`form-control`, `form-select`) hem stat hem
  survey/analiz formlarında yoğun kullanılıyor — ax- karşılığı görsel olarak
  input/select native davranışını (autofill, focus ring, disabled state)
  bozmamalı
- 100+ dosyalık migration tek PR'da değil, birden fazla oturuma yayılmalı

## Sıradaki adım
Faz 1'i başlatmak için onay bekleniyor — hiçbir mevcut template değişmeyeceği
için düşük riskli, istenildiğinde başlanabilir.

**Deploy notu:** Bu migration'ın tüm adımları yalnızca `dev` branch'ine push
edilecek. `main`'e (Hetzner/prod) kullanıcı açıkça "merge et" demeden
geçilmeyecek — bkz. genel proje kuralı (memory: `git_workflow`, `dev_first`).

---

# Homepage'e 3. Hero Seçeneği: "Bir Projem Var" (fikir aşaması)

**Durum:** Sadece fikir — henüz uygulanmadı, kullanıcı "todo'ya yaz ve bırak"
dedi. (Temmuz 2026)

## Fikir
Homepage'deki iki taraflı pazar yeri yönlendirmesine ("Analiz Yaptırmak
İstiyorum" / "Uzman Olarak Katılmak İstiyorum") üçüncü bir seçenek eklemek:
"Bir Projem Var..." → mevcut `/proje-talebi/` sayfasına (kurumsal danışmanlık
talep formu) yönlendiren bir kart/şerit.

## Teknik bulgular
- İki mevcut kart `forum/templates/forum/home.html:257-341` içinde, `row g-4`
  içinde iki `col-lg-6` — her biri özel SVG illüstrasyon, özellik listesi,
  kategori etiketleri, çoklu CTA içeriyor (zengin/karmaşık içerik).
- Kart shell'i `static/css/home_sections.css:71` — `.ax-market-card` (ortak
  gövde) + `.ax-market-card--demand`/`--supply` (üst renkli çizgi varyantları,
  indigo/amber). Üçüncü `.ax-market-card--project` varyantı (`--ax-accent-secondary`
  yeşili ile) düşük riskli, küçük bir CSS eklemesi olur.
- `/proje-talebi/` zaten var (`forum/views.py: proje_talebi`, "Projenizi
  Anlatın, Size Uygun Uzmanı Bulalım" başlığı) — kurumsal/şirket odaklı.
  **Dikkat:** "Analiz Yaptırmak İstiyorum" kartıyla hedef kitle örtüşmesi
  olabilir (ikisi de "biri benim için analiz yapsın" diyor) — uygulamaya
  geçilirken bu ayrım netleştirilmeli (örn. proje_talebi = kurumsal/resmi
  teklif süreci, mevcut kart = bireysel/hızlı eşleşme).

## Önerilen yaklaşım (kullanıcıya sunuldu, karar bekliyor)
İki mevcut kart hiç değişmeden kalsın (zaten dönüşüm sağlıyorlar, riske
atılmamalı). Altına tam genişlikte, sade/yatay bir üçüncü şerit eklensin —
büyük SVG yok, kısa açıklama + tek CTA (`/proje-talebi/`), yeşil
(`--ax-accent-secondary`) vurgusuyla diğer ikisinden ayrışır. **Reddedilen
alternatif:** 3 eşit kolon (`col-lg-4`) — mevcut zengin kartların
küçültülmesini gerektirir, çalışan/dönüşüm sağlayan elemanlara dokunma
riski taşır.

## Sıradaki adım
Kullanıcı ne zaman uygulamaya geçmek isterse haber verecek; o zaman hedef
kitle ayrımı netleştirilip yukarıdaki yaklaşımla (veya kullanıcının o an
tercih edeceği alternatifle) uygulanacak.

---

# Claude API ile Akademik Tarama Entegrasyonu (fikir aşaması)

**Durum:** Sadece fikir/araştırma notu — henüz plan/onay yok. (Temmuz 2026)

## Kaynak
LinkedIn'de görülen "Claude Science" paylaşımı aslında Claude'un agentic
tool use ile yaptığı bir sistematik literatür taraması: PubMed E-utilities'den
veri çekme, LLM+kural tabanlı hibrit tarama, kod yürütme ile PRISMA diyagramı/
bibliyometrik grafik üretimi, Crossref'ten DOI doğrulama.

## Fikir
Bu yeteneği platformun mevcut "akademik tarama" ve "bibliyometri"
modüllerine (analizus.md §13-15) eklemek.

## Önerilen mimari (taslak)
- **Managed Agents değil, Claude API + tool use** — mevcut Django job/polling
  altyapısına (Celery, S3, `result_data` JSON kaydı) entegre olması ve tam
  backend kontrolü için
- Custom tool: `pubmed_search` (E-utilities çağrısı), `crossref_verify_doi`
- Server-side `code_execution` tool: PRISMA diyagramı + bibliyometrik
  grafikler (matplotlib, mevcut istatistik pipeline'ıyla aynı mantık)
- Hibrit tarama: önce ucuz kural tabanlı filtre, belirsiz kalanlar Claude'a
  (maliyet kontrolü)
- Sonuç: CSV + figür + referans listesi, mevcut polling/job desenine (§12)
  uyacak şekilde

## Tradeoff notu
Managed Agents kullanılırsa ajan döngüsü/konteyner Anthropic tarafında
barınır (daha az backend kodu) ama mevcut Celery/polling mimarisiyle
entegrasyonu daha zor ve ekstra maliyet/karmaşıklık getirir.

## Sıradaki adım
Hangi modüle ekleneceği netleşmedi (mevcut akademik tarama mı, yeni özellik
mi). Karar verilmeden somut plana (dosyalar, endpoint, migration gerekip
gerekmediği) geçilmeyecek.

---

# Site Geneli "Sıfır Kuralı" (Zero-State Sigortası)

**Durum:** TAMAMLANDI (12 Temmuz 2026, commit `b39307c`). Kaynak prompt
`~/Desktop/analizus_sifir_kurali_prompt.md`. Faz 1 envanteri çıkarıldı+onaylandı,
Faz 2 uygulandı (ana sayfa 5 sayaç + `has_any_stats` grup kontrolü, uzman kartı
"0 tamamlanan proje" satırı, "Akademik Haberler" placeholder kaldırıldı,
Gündemdeki Tartışmalar+Akademik Haberler layout bütünlüğü, /hakkimizda/ "Ekip ve
Güven" bölümü), Faz 3'te 9 smoke test eklendi (`forum/tests.py`). /market/ ve
/proje-talebi/ zaten kurala uygun çıktı (yeni iş gerekmedi). Aşağıdaki eski not
artık geçmiş kayıt olarak kalıyor:

## Amaç
Değeri 0 olan hiçbir güven metriği ("0 tamamlanan analiz", "0 aktif uzman" vb.)
ve içi boş hiçbir vitrin bölümü ziyaretçiye gösterilmeyecek. Gerekçe: dev DB
boşluğu değil, canlının doğal dalgalanması (gece 03:00 çevrimiçi uzman
gerçekten 0 olabilir) — "boş dükkân" izlenimini önlemek.

## Protokol (kullanıcının vurguladığı 3 kritik nokta)
1. **Kuralı tanımla, yerleri saydırma.** Talimat sabit bir liste değil: Faz 1
   `grep` ile TÜM template'leri tarayıp tam bir envanter tablosu çıkarır
   (Template · Bölüm · Metrik/Koleksiyon · Mevcut davranış · Önerilen işlem ·
   Kategori), onay alınmadan tek satır değiştirilmez. Bilinen 8-9 aday
   (ana sayfa `ax-stats-section`, uzman vitrini kart içi satırlar, "Akademik
   haberler yakında" şeridi, /proje-talebi/ stats bar, /market/ sayaç üçlüsü,
   /hakkimizda/ "Henüz uzman kadro eklenmedi.") başlangıç noktası, liste
   bunlarla SINIRLI değil — asıl risk modelin kapsamı kendiliğinden
   genişletmesi; envanter+onay kapısı bunu keser.
2. **İstisnayı ilkeyle tanımla, örnekle sabitle — "davet vs itiraf" ayrımı.**
   Davet (bilinçli tasarlanmış CTA içeren boş-durum metni, ör. market'teki
   "İlk analiz işini sen tamamla…") KORUNUR; itiraf ("Henüz uzman kadro
   eklenmedi." gibi) GİZLENİR. Gri kalan her örnek envanterde "karar gerekli"
   işaretlenip kullanıcıya sorulacak.
3. **Yan etkileri kurala bağla.** Bir öğe gizlenince grid/flex kırılmamalı
   (7 sayaçtan 3'ü gizlenince kalan 4'ün doğal dağılması); bir sayaç
   grubundaki TÜMÜ 0 ise kapsayıcı (şerit/başlık dahil) da gizlenir; yeni DB
   sorgusu YASAK — "hepsi sıfır mı" kontrolü mevcut cache'li değerlerden
   türetilen tek bir boolean ile yapılır; parantezli `{% if %}` yasağı
   (analizus.md §26) geçerli.

## Fazlar (kaynak promptta tanımlı)
- Faz 1 — Envanter (uygulama yok, sadece rapor + onay)
- Faz 2 — Uygulama (template `{% if %}`, gerekirse tek boolean context değişkeni)
- Faz 3 — Test + Teslim (0/>0 smoke testleri, migration beklenmiyor)

## Sıradaki adım
Kullanıcı başlamamı istediğinde `analizus_sifir_kurali_prompt.md` içeriğiyle
Faz 1'i (envanter) çalıştırıp tabloyu onaya sunacağım.

---

# Merge Öncesi Son Süpürme (analizus_son_supurme_prompt.md)

**Durum:** TAMAMLANDI — Madde 1-11'in tümü bitti (13 Temmuz 2026). `dev`→`main`
merge de yapıldı (31 Temmuz 2026 itibarıyla iki branch aynı commit'te,
`9b6f58d`). Merge sonrası hatırlatmalardan `feature_agentic_landing` flag'inin
prod'da elle açılıp açılmadığı DOĞRULANMADI — sıradaki oturumda kontrol
edilmeli (bkz. Madde 10 deploy notu).
Kaynak: `~/Desktop/analizus_son_supurme_prompt.md`. Yeni oturumda önce bu dosya
+ bu bölüm okunmalı; `analizus_son_supurme_prompt.md`'nin ORİJİNAL Madde 1
metni artık güncel değil (aşağıdaki kararlarla değişti), bu yüzden bu bölüm
esas alınmalı.

## Tamamlananlar (commit sırasıyla)

- **Madde 1 (huni parametreleri)** — `cd84461`. Tableau CTA metni "Proje Talebi
  Oluştur"a çevrildi; bibliometrik ön-seçim için `ANALYSIS_CHOICES`'a
  `('bibliometric', 'Bibliyometrik Analiz')` eklendi (migration `0147`, no-op
  AlterField). `proje_talebi` view artık `?type=` GET param'ını da okuyor.
  **Karar (kullanıcı onaylı):** bibliometri istatistiksel analiz sayılmadı,
  `statistics` seçeneği yeniden kullanılmadı — ayrı seçenek açıldı.
- **Madde 2 (Sıfır Kuralı)** — `b39307c`. Yukarıdaki bölüme taşındı.
- **Madde 3 (footer tutarsızlığı)** — iş YOK, zaten çözülmüştü (footer tek
  partial, `{% url 'analiz_home' %}` kullanıyor, hardcode `/istatistik/` yok).
- **Madde 4 (forum boş-durum sızıntısı)** — iş YOK, zaten çözülmüştü (`#noResults`
  zaten `d-none` ile başlıyor, JS mantığı zaten doğruydu).
- **Madde 5 (OG override + meta)** — `d73ab72`. 8 hedef sayfaya
  og_title/og_description/twitter_title/twitter_description eklendi.
  **Önemli bulgu:** `/bibliometrics/` misafir kullanıcı için `landing.html`
  değil, PAYLAŞILAN `templates/service_promo.html` render ediyor (6+ istatistik
  araç sayfası da aynı şablonu kullanıyor). Asıl düzeltme oraya, `promo_description`
  context değişkeninden yapıldı — bonus: diğer araç sayfaları da özgün
  og:description kazandı.
- **Madde 6 (dev noindex middleware)** — iş YOK, zaten vardı
  (`forum/middleware.py::NoIndexMiddleware` + `settings.IS_PRODUCTION`).
- **Madde 7a (bibliometri örnek çıktılar + OpenAlex köprüsü)** — `2029ce9`.
  Galeri ve OpenAlex ters köprüsü zaten
  vardı; eklenen tek şey hero altı "OpenAlex'te tarama mı yaptın?" bandı
  (`promo_openalex_bridge` context bayrağı, yalnızca bibliometride true).
  **Karar (kullanıcı onaylı):** galeri kartları spec'in istediği 5 başlıkla
  (Anahtar Kelime Eş-Oluşum Ağı, Anahtar Kelime Zaman Trendi vb.) DEĞİL,
  `static/img/`'de gerçekten var olan 6 görselin gerçek içeriğine uygun
  başlıklarla kuruldu (Yayın Trendi, Anahtar Kelime Bulutu, Yazar İşbirliği
  Ağı, Atıf Analizi & H-index, Araştırma Boşluğu Haritası, Lotka Kanunu) —
  bu zaten `bibliometrics/views.py`'de mevcuttu, değiştirilmedi.
- **Madde 7b (Tableau facade)** — `4ebaa7e`. Poster+buton facade UI önceki
  turda zaten kuruluydu, ama `tableau.embedding.3.latest.min.js` script'i
  `extra_js` block'unda koşulsuz (sayfa yüklenir yüklenmez) çekiliyordu —
  bu da "ilk yüklemede public.tableau.com'a sıfır istek" kabul kriterini
  fiilen bozuyordu. Script artık yalnızca "İnteraktif Dashboard'u Yükle"
  tıklamasında dinamik `<script>` enjeksiyonuyla yükleniyor. Playwright ile
  doğrulandı: yüklemede 0 istek, tıklamada gerçek dashboard (5 istek) açılıyor.
- **Madde 7c (Blog OG/kapak/pagination)** — `8b82242`. og:type=article ve
  pagination linkleri önceki turda zaten doğruydu. Eksik olan tek parça —
  kapaksız yazılarda kategoriye göre varsayılan görsel — `BlogPost.
  cover_image_url` property'siyle eklendi (35/35 yayındaki yazının hiçbirinde
  kapak yoktu, bu yüzden kartlar ve og:image/JSON-LD boş görünüyordu).
  Migration gerekmedi. Playwright ile liste+detay sayfası görsel doğrulandı.
- **Madde 8 (Hero sadeleştirme)** — `c338a7b`. `ax-hero__actions` bloğu
  ("Ücretsiz Başla"/"Analiz Yap" / "Uzman Bul" / "Foruma Katıl", giriş
  yapmış/yapmamış iki varyantıyla) tamamen kaldırıldı. Dropzone, "uzmana
  bırak" linki, veri kazıma bandı, alt CTA kartları değişmedi — Playwright
  ile masaüstü+mobil görsel doğrulandı, orphan spacing/CSS sorunu yok.
- **Madde 10 (Testler + Deploy Notu)** — bu tur. `forum/tests.py`'e 8 yeni smoke
  test eklendi: Madde 1'in 4 ön-seçimi (`?source=verification/agentic/tableau/
  bibliometrics` → `proje_talebi` formunda doğru `<option selected>`), Madde 4
  (forum arama sonucu boş-durumu varsayılan görünümde `d-none` ile gizli),
  Madde 6 (`NoIndexMiddleware` — `IS_PRODUCTION=False`'da header var,
  `True`'da yok, 2 test), Madde 7b (tableau `<tableau-viz>` yalnızca
  `<template>` içinde, ilk yüklemede canlı DOM'da yok). Madde 2 ve 9'un
  testleri zaten mevcuttu (bkz. yukarı Sıfır Kuralı bölümü ve
  `test_register_get_returns_200`/`test_login_get_returns_200`).
  **Sonuç:** 31 test, 30 geçti; tek hata `test_yoktez_job_daily_limit_normal_user`
  — bu turla ilgisiz, önceden bilinen, dokunulmadı (bkz. "Genel notlar").

  **DEPLOY NOTU (main'e merge öncesi — dev, main'den 28 commit ileride):**
  - **Migration:** main→dev arası tam 4 migration — `0144_projectrequest_
    source_choices`, `0145_sitesettings_feature_agentic_landing_and_more`,
    `0146_projectrequest_source_tableau_bibliometrics`,
    `0147_projectrequest_analysis_bibliometric`. Hepsi `AlterField` (choices
    genişletme) + tek `AddField` (boolean flag) — veri kaybı riski yok,
    `--fake` gerekmiyor.
  - **collectstatic:** GEREKLİ. Yeni statik dosyalar: 6 yeni CSS
    (`agentic_landing.css`, `bibliometrics.css`, `brand_visuals.css`,
    `expert_card.css`, `market.css`, `trend_topics.css`) + görseller
    (`agentic-hero(-mobile).webp`, `auth-login(-mobile)/auth-register
    (-mobile).webp`, `biblio-ornek-*.webp` ×6, `tableau-poster-*.webp` ×4).
  - **`?v=` denetimi:** main'de zaten var olup dev'de içeriği değişen yalnızca
    2 CSS dosyası var — ikisi de doğru bump edilmiş: `hero.css` 0103→0105,
    `home_sections.css` 0106→0112. Diğer 6 CSS dosyası main'de hiç yok
    (prod'da eski cache'lenmiş kopya yok), versiyon numaraları (v=0001/0002)
    bu yüzden önemsiz.
  - **Hetzner sırası:** `git pull` (main) → `docker compose exec web python
    manage.py migrate` → `docker compose exec web python manage.py
    collectstatic --noinput` → `docker compose restart web` → `docker compose
    restart nginx` (IP cache sorunu, CLAUDE.md kuralı).
  - **Merge sonrası hatırlatmalar:**
    1. **Feature flag açılmalı:** `feature_agentic_landing` migration'da
       `default=False` geliyor — admin'den `SiteSettings`'te AÇILMAZSA
       `/ai-cozumler/` ne navbar'da (`context_processors.py:75`) ne sitemap'te
       (`sitemaps.py:14`) görünür. Bu adım atlanırsa Madde 1b/7a'nın tüm
       huni işi görünmez kalır.
    2. `robots.txt` içeriği değişti (`Disallow: /istatistik/` satırı
       kaldırıldı, artık 301 üzerinden /analiz/'e akıyor) — GSC "robots.txt
       Test Aracı"ndan yeniden okutulmalı.
    3. Sitemap resubmit (GSC → Sitemaps).
    4. `/ai-cozumler/` + Madde 7'deki araç sayfaları (bibliometrics,
       tableau-analiz vb.) için GSC URL denetimi → elle dizine ekleme iste.
    5. `/istatistik/` → `/analiz/` 301'i GSC URL denetim aracıyla doğrula
       (robots.txt artık bunu engellemiyor, redirect aktif görünmeli).
    6. **Premium fiyat kaynağı kontrol edildi — DÜZELTME GEREKMEDİ.** Kaynak
       tamamen DB: `DonationTier.min_amount` (migration'ları 0031/0032/0045/
       0076, zaten prod'da uygulanmış, bu merge'e dahil değil).
       `footer.html:154-167` yalnızca `{{ tier.min_amount }}` render ediyor,
       hardcode TL değeri yok — prod (250/500/750/1000) ve dev (50/100/250/
       500) farkı tamamen DB seed farkı, template/kod fark yaratmıyor.

- **Madde 9 (Auth panelleri)** — `7837700`. `login.html`/`register.html`
  base.css yüklemiyor (tamamen izole, hardcode renkli sayfalar) — bu yüzden
  `var(--ax-bg)` yerine dosyanın kendi `#0a1628` rengiyle iç vinyet
  (`box-shadow: inset 0 0 90px 70px #0a1628`) eklendi, kullanıcı onaylı.
  Turuncu dikey ayraç çizgisi (`::after`+`@keyframes fall`) kaldırıldı.
  Form `<label>` etiketleri nötr griye (#94a3b8) döndü — sadece etiketler,
  form-subtitle rengi DEĞİŞMEDİ (kullanıcı onaylı kapsam). register.html
  alt başlığı "Ücretsiz hesap — 30 saniye sürer."a çevrildi. <991px
  gizleme davranışı değişmedi, Playwright ile masaüstü+mobil doğrulandı.

## Genel notlar (yeni oturum için önemli)

- **Deploy notu — migration sayısı:** Bu tur `0147`'ye kadar geldi (0144-0147,
  toplam 4 migration). Madde 10'daki deploy notunda bu sayı kullanılmalı.
- **Pre-existing test hatası (bu turla ilgisi yok, dokunma):**
  `forum/tests.py::test_yoktez_job_daily_limit_normal_user` son commit'te de
  başarısız (`assert 3 == 1`) — bu turun DIŞINDA bir konu, `python -m pytest`
  çalıştırınca "1 failed" görürsen şaşırma.
- **service_promo.html gotcha:** Bibliometri, cronbach, normallik, betimsel,
  korelasyon, t-testi, anova, mann-whitney, kruskal-wallis, ki-kare, lineer/
  lojistik regresyon guest (misafir) görünümlerinin HEPSİ bu tek şablonu
  paylaşıyor. Bu sayfalardan birine özel bir düzenleme istenirse, view'daki
  context dict'e yeni bir bayrak eklenip template'te `{% if %}` ile o bayrağa
  göre gösterilmesi gerekir — aksi halde değişiklik ya hiçbir sayfada
  görünmez ya da yanlışlıkla hepsinde birden görünür.

- **Madde 11 (Ana sayfa "AI çağında iki yol" sağ kartı)** — TAMAMLANDI.
  `forum/templates/forum/home.html` FAZ 4 bölümündeki `.ax-agentic-band-card`
  (836-853. satır) sol karttaki (`.ax-brand-visual`) desenle birebir aynı
  yapıya geçti: `<picture>` (agentic-hero.webp masaüstü / agentic-hero-
  mobile.webp mobil, `source media="(min-width:768px)"`) + `.ax-agentic-
  band-card__overlay` gradient + mevcut başlık/metin/CTA içeriği değişmeden
  overlay içine taşındı. `static/css/home_sections.css`'te eski flat-renk
  flex kutusu CSS'i (`.ax-agentic-band-card { display:flex; background:...}`)
  kaldırılıp `__img`/`__overlay` kuralları eklendi (brand_visuals.css'teki
  `.ax-brand-visual__img`/`__overlay` ile aynı desen); `?v=0112`→`0113`.
  **Kritik gözlem:** agentic-hero görselleri sol karttaki ai-dogrulama
  görselleriyle piksel-piksel AYNI boyutta (1600×893 masaüstü, 800×446
  mobil) — bu yüzden iki kart hiçbir grid-stretch hilesine gerek kalmadan
  doğal olarak eşit yükseklikte oluştu, eski `@media(min-width:768px)
  { .ax-agentic-band-card{height:100%} }` kuralı gereksiz hale gelip
  kaldırıldı. `object-fit:cover;object-position:center` yine de güvenlik
  amaçlı bırakıldı (boyutlar eşit olduğu için normal akışta devreye
  girmiyor). Render'a push edilip (`analizus-dev.onrender.com`) Playwright
  ile doğrulandı: masaüstünde iki kart TAM eşit yükseklik (306.7px),
  380px mobilde neredeyse eşit (189.5 vs 190.4px, <1px fark), yatay taşma
  yok, görsel/overlay/metin doğru render ediyor.

## Kalan işler

Yok — "Merge Öncesi Son Süpürme" turunun 11 maddesi tamamlandı ve `dev`→`main`
merge'i de yapıldı (31 Temmuz 2026). Tek açık nokta: `feature_agentic_landing`
flag'inin prod'da elle açıldığı doğrulanmadı (bkz. Madde 10 deploy notu,
"Merge sonrası hatırlatmalar" #1) — sıradaki oturumda admin panelinden
kontrol edilmeli.

## Yeni oturumda nasıl devam edilir

1. Bu dosyayı (`tasks/todo.md`) ve `CLAUDE.md`'yi oku (CLAUDE.md zaten proje
   kökünde, otomatik yükleniyor).
2. Bu tur tamamlandı — yeni oturumda kullanıcı ya merge onayı verecek ya da
   yeni bir görev başlatacak (`/market/` pazaryeri zenginleştirme veya
   aşağıdaki fikir-aşaması maddelerinden biri gibi).

---

# /market/ Pazaryeri Zenginleştirme

**Durum:** Bekliyor — henüz başlanmadı. Kaynak prompt kullanıcı tarafından
hazırlandı (`analizus_pazaryeri_prompt.md`, bu konuşmada paylaşıldı, repo'da
dosya olarak yok). (Temmuz 2026)

## Amaç
`/market/` işlevsel ama çıplak (stats + ilan listesi + 3 adım) — hedef, sayfayı
gerçek bir pazaryeri vitrinine çevirmek: iki tarafı da (ilan açan / uzman)
karşılayan çift kapı, güven işaretleri, gezilebilir kategoriler, akan sosyal
kanıt.

## Protokol (kullanıcının vurguladığı 3 kritik nokta — sıfır kuralıyla aynı disiplin)
1. **Kuralı tanımla, yerleri saydırma.** İlk iş envanter: `/market/` view +
   template, ana sayfa uzman vitrini sorgusu (`home()`), trust bandı, skill
   chip yapısı incelenip YENİDEN KULLANILACAKLAR belirlenir; plan onaya
   sunulmadan uygulamaya geçilmez.
2. **İstisnayı ilkeyle tanımla, örnekle sabitle.** Bu görev "sıfır kuralı"
   görevinin somut uygulama alanlarından biri: market'teki "İlk analiz işini
   sen tamamla…" boş-durum metni bilinçli bir DAVETTİR, korunur — /hakkimizda/
   "Henüz uzman kadro eklenmedi." gibi bir İTİRAF değildir. Faz 4'teki sayaç
   üçlüsü (Tamamlanan İş / Aktif Uzman / Son 90 Günde) sıfır kuralına bağlanır:
   0 olan sayaç gizlenir, üçü de 0 ise şerit tamamen gizlenir.
3. **Yan etkileri kurala bağla.** Fiyat gizliliği kesin (uzman kartlarında
   fiyat/teklif bilgisi ASLA gösterilmez); sayaç/uzman sorguları ana
   sayfadaki `home_stats`/`home_experts` cache pattern'i yeniden kullanılır,
   çift hesaplama yapılmaz; kategori chip'leri ilan modelinde gerçek bir
   skill/kategori alanı yoksa "görsel chip + hepsi aynı listeye" şeklinde
   sessizce degrade EDİLMEZ — durum kullanıcıya bildirilip birlikte karar
   verilir; OG meta override mekanizması `base.html`'e dokunuyorsa ayrı onaya
   sunulur.

## Fazlar (kaynak promptta tanımlı)
- Faz 1 — Hero Bandı + Çift Kapı (İlan Aç / Uzman Olarak Katıl, market-hero
  görseli yoksa CSS-only placeholder)
- Faz 2 — Kategori Gezinmesi (`?skill=` GET filtresi — ilan modelinde kategori
  alanı yoksa DUR ve sor)
- Faz 3 — Sosyal Kanıt Katmanı (uzman vitrini şeridi, başarı hikayeleri varsa,
  oyunlaştırma/puan bandı)
- Faz 4 — Sıfır Temizliği + SEO (sayaç üçlüsü sıfır kuralı, OG override, SEO
  paragrafı)
- Faz 5 — Deploy Notu

## Sıradaki adım
Kullanıcı başlamamı istediğinde `analizus_pazaryeri_prompt.md` içeriğiyle
Faz 1'i çalıştırıp planı onaya sunacağım. Not: /market/ görevi, sıfır kuralı
görevinden ÖNCE veya SONRA yapılabilir — market'in Faz 4'ü sıfır kuralına
bağlı olduğundan, sıfır kuralı önce bitmişse market Faz 4 onun sonucunu
doğrudan kullanabilir (tekrar iş çıkarmaz), ama bu bir ön koşul değil.

---

# Çalışma Odaları Dönüşümü — Ertelenmiş İşler

**Kaynak:** `analizus_odalar_prompt.md` (repoda dosya olarak yok — yalnızca
sohbet eki olarak verildi, karakter kodlaması bozuk geldiği için repoya
olduğu gibi yazılmadı). Faz 1/2/3/4/5/6 tamamlandı (temmuz 2026, `dev`
branch'inde commit'lendi: faz-1, faz-1 ek, faz-2, faz-4, faz-3, faz-5+6).

## Ertelenen: Faz 3 milestone (proje odası ilerleme çekliste)
Proje tipi (`room_type='project'`) odalar için kurucunun işaretleyebildiği
3–7 maddelik ilerleme kontrol listesi özelliği **şimdilik eklenmedi**.
Karar: yalnızca `room_type` etiketi + görsel ayrım yeterli kabul edildi;
milestone checklist'i (JSONField `milestones = models.JSONField(default=list)`
+ kurucunun inline ekleyip işaretlediği küçük bir POST endpoint'i, üyeler
tam listeyi görür, misafir yalnızca "%40 tamamlandı" bar'ını görür) ayrı
bir görev olarak ele alınacak.

**Ne zaman gündeme gelir:** Kullanıcı proje odaları için ilerleme takibi
isteğini tekrar gündeme getirdiğinde, veya `room_type='project'` kullanımı
yaygınlaştığında.

## Henüz yapılmayan fazlar
- **Faz 7 — Görsel yükseltme:** `static/img/odalar-hero.webp` ve
  `odalar-hero-mobile.webp` artık mevcut (kullanıcı sağladı, henüz repoya
  commit'lenmedi/kullanılmadı). Hero + kart dilini market/agentic sayfalarıyla
  hizala.
- **Faz 8 — SEO + teknik temizlik:** Slug Türkçe karakter düzeltmesi
  (mevcut oda slug'larına dokunma), JSON-LD Event schema, sitemap,
  test hesap temizliği (kullanıcı kararı gerekiyor).

---

# Ana Sayfa & Navbar İyileştirme Turu — Faz 12 + Faz 13 (bekleyen)

**Kaynak:** `analizus_anasayfa_prompt.md` (proje kökünde dosya olarak mevcut).
Faz 0,1,2,3,4,5,6,7,8,9,10,11 tamamlandı ve
`main`'e merge edildi (bkz. memory `project_anasayfa_iyilestirme`). Faz 12 ve
13 o turdan kalan, henüz başlanmamış iki faz.

## Faz 12 — Forum vitrini dönüşümü — TAMAMLANDI (kısmi yayın), Temmuz 2026, dev branch
Ana sayfadaki "Gündemdeki Tartışmalar" 6 jenerik AI konusu (Fine-tuning vs RAG,
Prompt Engineering, Açık kaynak LLM'ler, LLM Halüsinasyonu, GPU olmadan Deep
Learning, LLM etik sınırları — hepsi `seed_forum.py`'den sabit views=3456-5678
ile) `forum/management/commands/remove_generic_seed_topics.py` ile silindi.
Konuyla alakalı ama sahte-seed 4 konuya (SPSS normallik, anket örneklem,
Google Forms, Türkçe NLP model) kullanıcı kararıyla dokunulmadı.

`forum/management/commands/reseed_forum_topics.py` (yeni, idempotent,
`--count N` ile kademeli yayın) 12 yeni konu+uzman cevabını (SEO'ya dikkat
edilerek yazıldı) ve 3 yeni Category'yi (`akademik-surec`, `veri-analizi-bi`,
`ai-ml-agentic`) içeriyor — kaynak: `analizus_forum_seed_konular.md`. Bu turda
`--count 3` ile yalnızca ilk 3 konu (Hakem 2/SEM, Etik kurul onam muafiyeti,
YÖK Tez benzerlik) canlıya alındı; kalan 9 konu dosyada hazır, sonraki
haftalarda `docker compose exec web python manage.py reseed_forum_topics
--count N` ile devreye alınır (kademeli yayın kuralı — hepsi bir günde
açılmaz).

`forum/views.py` — yeni `_trending_topics()` yardımcı fonksiyonu (`home()` ve
`forum_index()` ortak kullanıyor, N+1 yok): sıralama artık `-views` değil,
`Exists()` ile uzman (`account_type='Expert'`) cevaplı konular önce, dolmazsa
son aktif konular. `views` alanı DEĞİŞMEDİ (gerçek sayaç, `topic_detail()`'da
artıyor), sadece sıralama kriteri değişti.

`_gundem_tartismalar.html` — "Uzman cevapladı" rozeti (`ax-badge
ax-badge--primary`) + cevap sayısı eklendi. `trend_topics.css`'te forum
varyantı meta satırına `flex-wrap`/`max-width` eklendi (rozet mobilde
taşmasın diye), `?v=0001`→`0002` bump edildi (forum_index.html + home.html×2).

Doğrulama: `python -m pytest forum/tests.py` → 52/53 geçti (tek hata
`test_yoktez_job_daily_limit_normal_user`, bu turla ilgisiz, önceden bilinen).
Django shell üzerinden `/` ve `/forum/` render edildi, "Uzman cevapladı" 5
kez görünüyor, "Fine-tuning" metni artık hiç yok. Playwright ile görsel
(mobil taşma) doğrulaması henüz yapılmadı — sıradaki oturumda önerilir.

**Kalan iş:** 9 konunun kademeli yayını (haftada 2-3, `--count` artırılarak)
+ her yayından sonra ilgili uzman hesabın cevabının gerçekten "vitrin
kalitesinde" durduğunu gözden geçirmek.

## Faz 13 — Dropzone akışı: vaat + triyaj şeridi
Hero dropzone'a dosya bırakan kullanıcı `/analiz/?from=hero` araç listesine
düşüyor ama analiz bilmeyen kullanıcı 18 araç arasında yol göstericisiz
kalıyor — H1 "yapamıyorsan yapan burada" vaadiyle çelişki.

- **Keşif (metinden önce zorunlu):** dosya hero'da sunucuya mı yükleniyor,
  tarayıcıda mı tutuluyor; misafir kullanabiliyor mu; `/analiz/`de dosya
  durumu nasıl taşınıyor.
- **Triyaj şeridi:** `/analiz/`de yalnızca `from=hero` + dosya seçili durumda,
  rozetin altına üç link: Hangi Test? sihirbazı · AI Asistan'a sor
  (`axOpenAiWidget`) · Bu işi uzmana bırak (`?source=analiz_triyaj`). Yeni
  motor yok, mevcut hedefler kullanılır.
- **Hero mikrometni (keşif sonrası):** vaat gerçeğe göre yazılır, yalnızca
  teknik olarak doğrulanan ifadeler kullanılır; uygulamadan önce kullanıcıya
  sunulur.
- ERTELENEN (bu fazın kapsamı dışı): kolon-tipine dayalı gerçek öneri motoru.

## Sıradaki adım
Kullanıcı başlamamı istediğinde önce Faz 12 için karar noktasını (komut mu
elle mi) sorup uygulayacağım; Faz 13 keşif adımıyla başlayacak. İkisi
birbirinden bağımsız, istenen sırada yapılabilir.

## Faz 13 — DURUM: mikrometin + triyaj şeridi tamamlandı (temmuz 2026)
Keşif + uygulama bitti: hero dropzone altına "Kayıt gerekmez — hemen dene"
mikrometni (`forum/templates/forum/home.html` + `static/css/hero.css`,
`.ax-hero-dropzone__trust`, `?v=0107`), `/analiz/` sayfasına `from_hero`
rozetinin altına triyaj şeridi (Hangi Test? · AI Asistan'a sor · Bu işi
uzmana bırak `?source=analiz_triyaj`) eklendi
(`istatistik/templates/istatistik/analiz_hub.html`).

**Doğrulanan mimari bulgular (Faz 13 keşfinden):**
- Hero'dan yüklenen dosya gerçekten sunucuya gidiyor, session'da RAM'de
  tutuluyor (`istatistik/services/job_runner.py` — `_session_datasets`,
  `_pending_file_contents`); disk/DB'ye yazılmıyor.
- Login zorunlu değil — misafir hem yükleyip hem analiz çalıştırabiliyor
  (`is_demo=not request.user.is_authenticated` deseni).
- Production tek process/tek container (Hetzner: `docker-compose.yml` tek
  `web` servisi, `Dockerfile` CMD'si tek `daphne` process, nginx tek
  `web:8000` upstream'ine proxy; Render/`Procfile` de aynı). **Modül seviyesi
  dict için multi-worker veri kaybı riski şu an gerçek değil** — yalnızca
  ileride yatay ölçeklendirilirse (birden fazla container/process) mimari
  kırılır, dikkat edilecek kısıt olarak not düşülüyor.
- Dosya boyutu limiti zaten var: `MAX_UPLOAD_SIZE = 5MB`
  (`analizdestek/settings.py:529`), `hero_upload` kontrol ediyor — ek iş yok.

## `_session_datasets` TTL temizliği — KOD TAMAMLANDI, crontab satırı eksik (31 Temmuz 2026)
Faz 13 keşfinde bulunan bellek sızıntısı riski (terkedilmiş veri setleri
süresiz RAM'de birikiyor) çözüldü:
- `istatistik/services/job_runner.py` — `_session_datasets` artık
  `(content, filename, saved_at)` tutuyor, `SESSION_DATASET_TTL_SECONDS = 2 saat`
  (kullanıcı kararı — `SESSION_COOKIE_AGE` ile hizalı, 24 saat önerisi session
  zaten 2 saatte geçersiz olduğu için gereksiz bulundu), yeni
  `cleanup_expired_session_datasets()` fonksiyonu eklendi.
- `forum/api_views.py` + `forum/urls.py` — mevcut `/api/cron/*` desenine uygun
  yeni `cron_cleanup_session_datasets` endpoint'i (`X-Cron-Secret` doğrulamalı).
  DB değil RAM temizlediği için (ayrı process bu dict'e erişemez) yalnızca bu
  HTTP-tetiklemeli desen çalışır — management command seçeneği mimari olarak
  elenmiş oldu.

**Kalan iş:** Hetzner crontab'ına satır eklenmesi (ben production crontab'ı
doğrudan değiştiremiyorum, kullanıcı kendi terminalinden eklemeli):
`0 * * * * curl -s "https://www.analizus.com/api/cron/cleanup-session-datasets/?secret=..." >> /var/log/cron_cleanup_session_datasets.log 2>&1`
(saatlik — 2 saatlik TTL'e göre makul sıklık). Deploy notu: migration yok,
`dev`'e push edilip test edildikten sonra `main`'e merge + Hetzner'de
`git pull` + `restart web` yeterli.

## PageSpeed Insights — Kalan Optimizasyon Fırsatları (ertelendi, temmuz 2026)

MathJax/Prism/Font Awesome kaldırma, footer kontrast (WCAG AA) ve
bootstrap-icons preload (CLS 0.102→0.009) düzeltmeleri uygulandı ve
`main`'e merge edildi (masaüstü 86→96, mobil 70→80, erişilebilirlik
96→100). Kullanıcı kararıyla burada duruldu — kalanlar ayrı, daha büyük
işler:

- [ ] **Kullanılmayan CSS (Bootstrap, 43 KiB)** — ayrı görev olarak zaten
  planlı, bkz. bu dosyanın başındaki "Bootstrap Kaldırma — Kademeli
  Migration Planı"
- [ ] **Render-blocking `bundle.css`** (188-190ms) + **Ağ bağımlılık ağacı**
  (kritik yol ~588ms) — aynı kök neden: `bundle.css` above-the-fold
  navbar/layout stilini içeriyor, deferred yapmak FOUC riski taşır; kritik
  CSS ayıklama (inline critical CSS + async geri kalan) gerektirir
- [ ] **Yandex Metrica** — verimli önbellek (71 KiB) + kullanılmayan JS
  (43 KiB) + olası uzun görevler; üçüncü parti, init'i `requestIdleCallback`
  ile ertelemek TBT'yi düşürür ama webvisor/bounce-tracking doğruluğunu
  etkileyebilir — iş kararı, kullanıcıya sorulmadan yapılmayacak
- [ ] **Zorunlu yeniden düzenleme** (~103ms ilişkilendirilmemiş) — kesin
  kaynağı Chrome DevTools Performance profiliyle tespit edilmeli, first-party
  JS'te (navbar.js/ax-dropdown.js/widget_collapse.js/main.js) layout-thrashing
  deseni yok (grep ile doğrulandı)
- [ ] **28 birleştirilmemiş (uncomposited) animasyon** — `border-color`/
  `background-color`/`box-shadow` geçişleri ax- tasarım sisteminde ~20 CSS
  dosyasına yaygın, düzeltmek geniş kapsamlı bir tasarım sistemi revizyonu
  gerektirir
- [x] **Görsel boyutu** (`ai-dogrulama.webp`/`agentic-hero.webp`) —
  1600×893 → 1100×614 küçültüldü, kullanıcı kararıyla burada bırakıldı
  (retina netliği öncelikli, 30 KiB'lik kalan Lighthouse uyarısı kabul edildi)
