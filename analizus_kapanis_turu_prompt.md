# GÖREV: Analizus.com — Merge Öncesi Kapanış Turu (Dev Branch Denetim Bulguları)

## GÜNCELLEME NOTU (temmuz 2026 — kod denetimiyle revize edildi)

Bu prompt yazıldıktan SONRA "AI Çözümler (Agentic) landing page" turu (`cd82201`) ve
"/market/ Pazaryeri zenginleştirme" turu (`2de0635`..`d374131`) tamamlandı. Kod denetimi
şunu gösterdi: aşağıdaki fazların bir kısmı bu turlar sırasında zaten kapatıldı, bir
maddenin varsayımı da gerçek kodla çelişiyor. Fazlar buna göre işaretlendi:

- **FAZ A madde 1-2 (`&type=verification`/`&type=agentic` ekleme) — İPTAL.**
  `proje_talebi` view'ı (`forum/views.py:2021`) yalnızca `source = request.GET.get('source', 'direct')`
  okuyor, `type`/`analysis_type` GET param'ı hiç işlenmiyor; `proje_talebi.html:166-167`
  zaten `source=='verification'|'agentic'` ile doğru ön-seçimi yapıyor. AI Çözümler
  turu bunu zaten tespit edip "`?type=` kullanılmadı" diye belgeledi (§27). Bu iki
  madde artık uygulanMAYACAK.
- **FAZ A madde 5 (bibliometri `?source=tool`→`?source=bibliometrics`) — ÇATIŞMA,
  karar gerekiyor.** `?source=tool` bibliometrics'e özgü değil; paylaşılan
  `templates/service_promo.html:144` ve `istatistik/templates/istatistik/analiz_console_base.html:206`'dan
  geliyor — bibliometrics dahil ~10+ araç sayfası (openalex, trdizin, oaipmh, yoktez,
  semanticscholar, 18 analiz konsolu) aynı include'u paylaşıyor. Bibliometrics'i tek
  başına ayırmak için ya bibliometrics'e özel bir context/override eklenmeli ya da bu
  madde tamamen iptal edilmeli. **Uygulamadan önce kullanıcıya sorulacak.**
- **FAZ B madde 1-5 (iki kartlı "AI çağında iki yol" bölümü + 🏢 pill metni) — ZATEN
  YAPILMIŞ.** AI Çözümler turunun Faz 4'ü bunu birebir uyguladı (`home.html`,
  `.ax-verify-band` → `ax-ai-era-grid`, flag `feature_agentic_landing`). Bu maddeler
  artık uygulanMAYACAK, yalnızca doğrulama amaçlı kalsın.
- **FAZ B madde 6 (hero eski üçlü buton satırı kaldırma) — HÂLÂ GEÇERLİ.** Denetimde
  eski satır (`home.html:195-215` — `Ücretsiz Başla`/`Analiz Yap` / `Uzman Bul` /
  `Foruma Katıl`) dropzone'la birlikte hâlâ duruyor bulundu. Onay şartı (kaldırmadan
  önce tam HTML göster) geçerliliğini koruyor.
- **FAZ B madde 7 (akademik haberler şeridi) — doğrulanmadı**, olduğu gibi kalsın.
- **FAZ C (AI Asistan yönlendirmesi) — TAMAMEN ZATEN YAPILMIŞ.** `forum/services/ai_service.py`'de
  `_ALLOWED_PATHS` (satır 32) ve `SYSTEM_PROMPT` (satır 109) zaten `/ai-cozumler/`
  içeriyor. Bu faz artık atlanacak.
- **FAZ D madde 1 (OG override mekanizması) — KISMEN ZATEN VAR.** `templates/base.html:35-50`'de
  tek `{% block og %}` yok ama alan-bazlı bloklar zaten mevcut: `og_type`, `og_title`,
  `og_description`, `og_image`, `twitter_title`, `twitter_description`,
  `twitter_image`, `meta_description`, `canonical`, `robots_content`. Yeni blok
  eklemeye gerek yok — asıl iş, 8 hedef sayfanın (ana sayfa, /ai-cozumler/, /market/,
  /proje-talebi/, /bibliometrics/, /tableau-analiz/, /analiz/, /tarama/) bu blokları
  gerçekten doldurup doldurmadığını denetlemek ve eksik/eski olanları güncellemek.
  (/market/ zaten Faz 4 pazaryeri turunda og_title/og_description aldı — diğer 7 sayfa
  doğrulanmalı.)
- **FAZ D madde 2-3 — geçerliliğini koruyor**, 8 sayfa denetimi kapsamında ele alınacak.
- **FAZ E madde 1 (robots.txt `/istatistik/` engeli) — YENİDEN AÇILDI, gerçek sorun
  bulundu.** İlk denetimde "yanlış alarm" denmişti ama ikinci bir tur (kullanıcı
  talebiyle) şunu ortaya çıkardı: `/istatistik/<slug>/` ile `/analiz/<slug>/` arasında
  GERÇEK bir 301 yok — `istatistik/urls_analiz.py`'deki `analiz_console(request,
  tool_slug)` view'ı, `_SLUG_MAP` üzerinden `/istatistik/<slug>/`'i işleyen AYNI view
  fonksiyonunu (örn. `cronbach_landing`) çağırıyor; iki prefix birebir aynı içeriği
  bağımsız render ediyor, ikisi de 200 dönüyor. Canonical etiketi yalnızca GİRİŞ
  YAPMIŞ kullanıcı şablonlarında doğru (`istatistik/cronbach.html` vb. —
  `{% block canonical %}/analiz/cronbach/{% endblock %}`); ANONİM ziyaretçi/Googlebot
  `service_promo.html` alıyor ve o şablonda canonical override YOK — kendi kendine
  (`/istatistik/...`) referans veriyor. Bu, GSC'nin orijinal "Alternative page with
  canonical" uyarısının kök nedeni; robots.txt Disallow'u kalıcı çözüm değil, geçici
  bant-aid'di. Aşağıdaki revize FAZ E madde 1 bunu gerçek 301 + robots.txt açma ile
  çözüyor. **Ek bulgular:** `forum/templates/forum/liderboard.html:88`'deki
  `/istatistik/` (bare) linki zaten ŞU AN 404 veriyor (istatistik/urls.py'de boş path
  yok) — düzeltme kapsamına dahil edilmeli. `istatistik/views.py:862`'deki
  `analiz_redirect` fonksiyonu hiçbir URL'e bağlı değil (dead code) — kapsam dışı,
  yalnızca not.
- **FAZ E madde 2 (dev noindex middleware) — HÂLÂ GEÇERLİ.** Kodda hiçbir noindex
  middleware'i yok, `MIDDLEWARE` listesinde (`analizdestek/settings.py:74-89`) böyle
  bir şey yok.
- **FAZ E madde 3 (sitemap `/ai-cozumler/`) — HÂLÂ GEÇERLİ.** `forum/sitemaps.py`'deki
  `ToolsSitemap` flag kontrolü hiç yapmıyor, `/ai-cozumler/` listede yok — bu zaten
  §27'de bilinen bir tutarsızlık olarak not edilmiş.
- **FAZ E madde 4 (footer "Analiz Araçları" linki) — HÂLÂ GEÇERLİ.** `templates/partials/footer.html:47`
  hâlâ `{% url 'istatistik:cronbach' %}` (`/istatistik/cronbach/`) veriyor — hem eski
  path hem de robots.txt'te disallow'lu bir path'e site içi link veriyor, gerçek bir
  hata.
- **FAZ E madde 5 (ana sayfa cache) — doğrulanmadı**, olduğu gibi kalsın.

Aşağıdaki orijinal metin referans için olduğu gibi bırakıldı; **yürütme sırasında
yukarıdaki güncelleme notu esas alınır — iptal edilen maddeler uygulanmaz.**

---

## GÖREV: Analizus.com — Merge Öncesi Kapanış Turu (Dev Branch Denetim Bulguları)

## BAĞLAM

Dev branch canlı denetimden geçti. AI Çözümler sayfası, ana sayfa v2 dönüşümü ve görsel
entegrasyonları büyük ölçüde doğru uygulanmış durumda. Bu görev, denetimde saptanan
kalan hataları ve eksikleri TEK turda kapatır. Yeni özellik YOK — yalnızca düzeltme,
tamamlama ve sigorta işleri.

**İlk iş:** `analizus.md` ve `CLAUDE.md`'yi oku. Her fazdan önce ilgili dosyaları oku,
plan + dosya listesi sun, ONAY AL, uygula, dur.

## DEĞİŞMEZ KURALLAR

1. Kapsam disiplini: yalnızca aşağıdaki fazlar. Başka sorun görürsen rapora not düş.
2. CSS: `ax-` sınıfları, `var(--ax-*)` token'ları, Bootstrap sadece grid.
3. **bundle.css tuzağı:** base/navbar/footer/style/sidebar_widgets.css yüklenmiyor —
   site-geneli CSS gerekirse 5'li birleştir+minify+`bundle.css` (+`base.html:92` `?v=`);
   sayfa-özel CSS kendi dosyasına.
4. Cache busting: dokunulan her CSS/JS'in `?v=` sürümü artar.
5. Önce mobil: yeni CSS taban mobil, masaüstü `@media (min-width: 768px)`; 380px kontrol.
6. Model değişiklikleri (varsa) TEK migration'da. Parantezli `{% if %}` yasak.
7. Git: `dev` branch, faz başına tek commit (`fix:` veya `feat:`).

---

## FAZ A — Huni Parametre Düzeltmeleri (fix)

~~1. **Ana sayfa Doğrulama bandı CTA:** `/proje-talebi/?source=verification` →
   `/proje-talebi/?source=verification&type=verification`~~ **İPTAL — bkz. güncelleme notu.**
~~2. **AI Çözümler sayfası — HER İKİ CTA** (hero + kapanış bandı):
   `/proje-talebi/?source=agentic` → `/proje-talebi/?source=agentic&type=agentic`~~ **İPTAL.**
~~3. Bu ikisini düzeltmeden önce `proje_talebi` view'ındaki `?type=` ön-seçim mantığının
   `verification` ve `agentic` değerlerini gerçekten işlediğini DOĞRULA...~~ **Doğrulandı: işlemiyor,
   ihtiyaç da yok — `source` tek başına yeterli.**
4. **Tableau sayfası CTA'ları:** her iki "İletişime Geç" →
   `/proje-talebi/?source=tableau` olarak değiştir (yapılandırılmış huniye yönlendir).
   `SOURCE_CHOICES`'ta `tableau` yoksa ekle. `ANALYSIS_CHOICES`'ta görselleştirme/
   dashboard'a karşılık gelen bir tür VARSA `&type=` ile ön-seç; yoksa tür EKLEME,
   sadece source ile bırak ve not düş. **(Hâlâ geçerli — CTA'lar şu an hiçbir yere
   linklemiyor, düz metin.)**
5. **Bibliometri alt CTA:** `?source=tool` → `?source=bibliometrics`
   (`SOURCE_CHOICES`'a ekle). Diğer araç sayfalarındaki `?source=tool` kullanımına
   DOKUNMA — yalnızca bu sayfa; genel araç-bazlı ayrıştırma ayrı görev.
   **(⚠️ ÇATIŞMA — bkz. güncelleme notu: `?source=tool` paylaşımlı bir template'ten
   geliyor, "yalnızca bu sayfa" teknik olarak mümkün değil şu anki yapıda. Uygulamadan
   önce sor.)**
6. Tüm SOURCE/ANALYSIS eklemeleri TEK migration'da.

**Kabul:** Tableau CTA'sı doğru parametreyle gidiyor, form doğru ön-seçimle açılıyor;
bibliometri kararı netleşti; admin'de yeni source'lar filtrelenebiliyor.

---

## FAZ B — Ana Sayfa "AI Çağı" Bölümü (Doğrulama + Agentic iki kart)

~~Mevcut tek kartlı AI Doğrulama bandını iki kartlı bölüme genişlet: [madde 1-5]~~
**Madde 1-5 ZATEN YAPILMIŞ (AI Çözümler turu Faz 4) — bkz. güncelleme notu. Yalnızca
doğrulama amaçlı kontrol edilsin, yeniden uygulanMAYACAK.**

6. **Hero sadeleştirme (ONAYLI YIKIM):** hero'daki eski üçlü buton satırı
   (`Ücretsiz Başla` / `Uzman Bul` / `Foruma Katıl`) KALDIRILIR — dropzone, "uzmana
   bırak" linki, kodsuz veri kazıma satırı ve kitle bandı kalır. Kaldırmadan önce
   satırın tam HTML'ini bana göster, onayımı al. **(Hâlâ geçerli — `home.html:195-215`,
   dropzone'la birlikte hâlâ duruyor.)**
7. **"Akademik haberler yakında burada" şeridi:** içerik gelene kadar render edilmez
   (sıfır kuralı prompt'unda ele alındıysa atla; alınmadıysa burada gizle).
   **(Doğrulanmadı.)**

**Kabul:** Hero eski üçlü olmadan dengeli; akademik haberler şeridi kuralı netleşti;
Lighthouse gerilemedi.

---

## FAZ C — AI Asistan Yönlendirmesi

**TAMAMEN ZATEN YAPILMIŞ — bkz. güncelleme notu. `ai_service.py`'de `_ALLOWED_PATHS`
ve `SYSTEM_PROMPT` zaten `/ai-cozumler/` içeriyor. Bu faz ATLANACAK.**

~~1. `_ALLOWED_PATHS` frozenset'ine `/ai-cozumler/` ekle.~~
~~2. `SYSTEM_PROMPT` içindeki platform haritasına AI Çözümler sayfasını ekle.~~

---

## FAZ D — OG Override Mekanizması + Sayfa Bazlı OG'ler

1. ~~`base.html`'deki og:title / og:description / twitter:title / twitter:description
   bloğunu `{% block og %}` ile override edilebilir yap.~~ **KISMEN ZATEN VAR — bkz.
   güncelleme notu: `base.html:35-50`'de alan-bazlı bloklar zaten mevcut. Yeni blok
   eklemeye gerek yok.**
2. Önce mevcut 8 hedef sayfanın (ana sayfa, /ai-cozumler/, /market/, /proje-talebi/,
   /bibliometrics/, /tableau-analiz/, /analiz/, /tarama/) bu blokları DOLDURUP
   DOLDURMADIĞINI denetle — `/market/` zaten dolduruyor (Faz 4 pazaryeri turu), diğer
   7 sayfa kontrol edilmeli. Eksik veya eski olan sayfalara özgün OG yaz (kısa,
   sayfanın `<title>`/description'ıyla uyumlu): ana sayfa (yeni hero mesajı: "Analizini
   yap. Yapamıyorsan, yapan burada."), vb.
3. /bibliometrics/ meta-description'ındaki "Türkiye'nin en büyük veri bilimi
   topluluğu" iddiasını ölçülü ifadeyle değiştir (ör. "Türkçe bibliometrik analiz
   aracı ve akademik topluluk").

**Kabul:** Blok override edilmeyen sayfalarda OG çıktısı öncekiyle AYNI; 8 hedef
sayfanın OG durumu netleşti (dolu/eksik); eksik olanlara özgün OG eklendi; sosyal kart
validator'da (manuel) doğru görünüm.

---

## FAZ E — İndeksleme ve SEO Güvenliği

1. **/istatistik/ → /analiz/ geçiş temizliği (SEO-kritik):**
   a) urls.py'de doğrula: araç sayfaları /analiz/<slug>/ altında mı
      yaşıyor ve /istatistik/<slug>/ oraya 301 atıyor mu? Atmıyorsa
      önce kalıcı 301'leri kur (urls.py seviyesinde, tool listesi
      üzerinden döngüyle — tek tek elle yazma).
      **(Doğrulandı: atmıyor — `analiz_console` `_SLUG_MAP` üzerinden
      `/istatistik/`'i işleyen aynı view'ı çağırıyor, gerçek 301 yok. 18 araçlık
      liste `istatistik/urls.py` + `_SLUG_MAP` + `IstatistikSitemap.items()`'ta
      tutarlı — döngü buradan kurulabilir.)**
   b) TÜM iç linkleri yeni adreslere güncelle: ana sayfa "kendin yap"
      linkleri, footer "Analiz Araçları", analiz hub, blog içi linkler,
      service_promo/ilgili-araçlar partial'ları. Tarama komutu:
      grep -rn "istatistik/" templates/ --include="*.html"
      (yalnızca URL referansları; metin içindeki "istatistik" kelimesine
      DOKUNMA).
      **(Genişletilmiş taramada gerçek 6+1 hit bulundu — `templates/` dışında
      app-özel template dizinlerine de bakmak gerekiyor:
      `templates/partials/footer.html:47`, `forum/templates/forum/home.html:232,234,358,359,360`,
      ve bonus bir 404 bug: `forum/templates/forum/liderboard.html:88`'deki bare
      `/istatistik/` linki şu an zaten kırık. `templates/admin/index.html:173`
      Django admin URL'i — DOKUNMA.)**
   c) robots.txt'ten "Disallow: /istatistik/" satırını KALDIR —
      301'lerin Google tarafından görülüp değerin /analiz/'e
      aktarılabilmesi için eski prefix taranabilir olmalı. Eski URL'ler
      sitemap'te zaten yok, öyle kalsın.
      **(Doğrulandı: `IstatistikSitemap.location()` zaten yalnızca `/analiz/{item}/`
      döndürüyor — sitemap tarafında değişiklik gerekmiyor.)**
   d) Doğrulama: /istatistik/cronbach/ → 301 → /analiz/cronbach/ → 200
      zinciri için smoke test; iç linklerde /istatistik/ kalmadığının
      grep kanıtı.
   **(Kapsam dışı not: `istatistik/views.py:862`'deki `analiz_redirect` fonksiyonu
   hiçbir URL'e bağlı değil, dead code — bu görevde dokunulmuyor.)**
2. **Dev ortamı noindex:** ortam bazlı çözüm — production dışı ortamlarda tüm
   yanıtlara `X-Robots-Tag: noindex, nofollow` header'ı ekleyen minimal bir
   middleware. Production davranışı DEĞİŞMEZ. **(Hâlâ geçerli — kodda hiç yok.)**
3. **Sitemap:** `/ai-cozumler/` sitemap'e eklenir (flag'li sayfa pattern'i neyse o;
   pattern yoksa flag açıkken listelenecek şekilde koşullu ekle). **(Hâlâ geçerli —
   `ToolsSitemap` flag kontrolü hiç yapmıyor, `/ai-cozumler/` listede yok.)**
4. ~~**Footer düzeltmesi:** "Analiz Araçları" linki...~~ **madde 1(b)'ye taşındı —
   ayrı yapılmayacak, iç link temizliğinin bir parçası olarak orada ele alınıyor.**
5. Ana sayfada template/full-page cache olup olmadığını kontrol et (denetimde ana
   sayfa navbar'ı diğer sayfalardan farklı/eski görünüyordu) — cache varsa
   invalidasyon stratejisini not düş; YOKSA "fark fetch cache'inden" diye rapora yaz.
   **(Doğrulanmadı.)**

**Kabul:** /istatistik/<slug>/ → 301 → /analiz/<slug>/ tüm 18 araçta çalışıyor;
iç linklerde /istatistik/ kalmadı (liderboard.html'deki kırık link dahil); robots.txt
`Disallow: /istatistik/` kaldırıldı; dev yanıtlarında noindex header var,
production'da yok; sitemap'te /ai-cozumler/ var.

---

## FAZ F — Test + Deploy Notu

1. Smoke testler: FAZ A'nın Tableau CTA'sı için ön-seçim testi; FAZ B madde 6 için
   hero render testi; FAZ E madde 1 için 18 araçlık 301 zinciri testi; FAZ E madde 2
   middleware'i için dev/prod header testi.
2. `python manage.py test` yeşil.
3. DEPLOY NOTU: değişen dosyalar; migration (varsa — FAZ A); `collectstatic`
   (CSS değiştiyse); `--build` YOK; `?v=` listesi; Hetzner komut sırası.
4. **Merge sonrası hatırlatma:** Google Search Console'da `/analiz/` araç
   sayfalarının indekslenme durumu kontrol edilsin — 301'ler devreye girdikten
   sonra Google'ın eski `/istatistik/` URL'lerini nasıl işlediğini (redirect
   olarak mı, hâlâ ayrı sayfa olarak mı) birkaç hafta içinde doğrulamak gerekir.

## KAPSAM DIŞI (bilinçli — başka görevlerde)

- Sıfır kuralı (ayrı prompt'ta ele alındı; uygulanmadıysa önce onu çalıştır)
- Pazaryeri zenginleştirme (tamamlandı — `analizus_pazaryeri_prompt.md`)
- Hakkımızda testimonial kararı (ürün sahibi kararı bekliyor)
- Anonim araç denemesi / hero vaadi hizalaması (stratejik karar bekliyor)
- Araç sayfalarında `?source=tool` → araç-bazlı ayrıştırma (bibliometrics hariç)
