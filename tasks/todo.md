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

**Durum:** Devam ediyor — Madde 1-9 tamamlandı. Kalan: 10, 11.
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

## Kalan işler (sırasıyla)

1. **Madde 10 — Testler + Deploy Notu:** tüm turun kapanışı, smoke testler,
   migration listesi (4 adet), `?v=` listesi, Hetzner deploy sırası, merge
   sonrası hatırlatmalar (robots GSC, sitemap resubmit, premium fiyat kaynağı
   kontrolü — prod 250/500/750/1000 TL, dev 50/100/250/500 TL).
2. **Madde 11 (YENİ, bu oturumda eklendi) — Ana sayfa "AI çağında iki yol" sağ
   kartı:** `agentic-hero.webp`/`agentic-hero-mobile.webp` zaten
   `static/img/`'de hazır (kontrol edildi). Sol karttaki (`ax-brand-visual`,
   `forum/templates/forum/home.html` FAZ 4 bölümü) AYNI kalıp: `<picture>`
   mobil-önce + overlay gradient + başlık/metin/CTA. Dikkat noktası: agentic
   görseli 16:9 yatay, anlam merkezi ortadaki monitör —
   `object-fit: cover; object-position: center` ile kadraj korunmalı. İki
   kart yüksekliği eşit kalmalı, 380px mobilde alt alta ve taşmasız. Madde 7
   ile aynı oturumda geçilebilir (kullanıcı notu).

## Yeni oturumda nasıl devam edilir

1. Bu dosyayı (`tasks/todo.md`) ve `CLAUDE.md`'yi oku (CLAUDE.md zaten proje
   kökünde, otomatik yükleniyor).
2. `~/Desktop/analizus_son_supurme_prompt.md`'yi oku — ama yukarıdaki
   "Tamamlananlar" ve "Genel notlar" bölümlerini esas al, orijinal metindeki
   Madde 1 artık güncel değil.
3. "Madde 10 — Testler + Deploy Notu" ile başla, sonra "Kalan işler" sırasını
   takip et — her madde için: envanter/plan → onay → uygulama → doğrulama →
   commit → dur.

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
