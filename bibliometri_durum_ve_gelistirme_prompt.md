# Bibliometri — Durum, Hatalar ve Geliştirme Yol Haritası (Claude Code promptu)

> Hazırlanma: 28 Ekim 2026. Kaynak: canlı PageView + BibliometricJob kayıtları, S3 demo PDF'i,
> sunucuda grep çıktıları. Tek doğru kaynak `analizus.md` (§14 Bibliometri, §25 kurallar, §26 bilinen
> hatalar, §28 çok dil). Bu belge ile kod çelişirse bana söyle, varsayım yapma.

## 0. Çalışma kuralları

- `CLAUDE.md` ve `analizus.md` §25/§26'yı oku. **Tek seferde tek görev**, her görevden sonra dur, onay bekle.
- Birden fazla dosya değişecekse önce dosya listesi + gerekçe, onaydan sonra kod.
- `main`'e push ETME (otomatik prod deploy). Commit mesajını ve deploy etkisini (migration? collectstatic?
  `--build`?) bana bırak. Migration içeren işten önce yedek hatırlat: `scripts/yedek_indir.sh --simdi`.
- **S3'e yazan/silen hiçbir şeyi çalıştırma** (lokal ve prod aynı bucket). Testlerde S3 ve e-postayı mock'la.
- Prod DB'ye erişimin yok; gerekirse bana salt-okunur `docker compose exec web python manage.py shell -c` komutu ver.
- Fiyat/limit/eşik sabit yazılmaz → `SiteSettings`. Yeni flag = model + context processor + admin fieldsets.
- Kullanıcıya görünen her yeni metin `gettext` ile; EN/DE `.po` güncellenir; EN/DE'de TR-only sayfaya link yok.
- Vanilla JS, `ax-` sınıfları, `var(--ax-*)`, önce mobil, N+1 yok. Sıfır Kuralı geçerli.
- **İstatistikte doğruluk hızdan önce gelir.** Her yeni analiz için bağımsız hesapla karşılaştıran pytest yaz.
- Her görev sonunda `analizus.md` için kısa güncelleme notu ver.

## 1. Gerçek vaka (neden bu belge var)

d4yu (user id 777, Endonezya, `stu.untar.ac.id`, 28 Ekim 2026) — PageView sırası (UTC):

| Saat | Olay |
|---|---|
| — | `/en/bibliometrics` sayfasından "Register" (`?next=/en/bibliometrics`) |
| 13:09 | `/en/verification-pending/` |
| 13:10:21 | `/en/onboarding/` |
| 13:10:47 | `/en/` — **bibliometriye geri dönmedi (next kayboldu)** |
| 13:10:56 | hero dropzone'a dosya bıraktı → `/analiz/?from=hero` — **Türkçeye düştü** |
| 13:12:52 | `/analiz/` → `/bibliometrics/` (TR) |
| 13:13:13 | `OpenAlex Data.csv` yükledi (521 kayıt, `file_format=csv_auto`, `source=upload`), 38 sn'de tamamlandı |

Sonuç: EN sayfası kullanıcı kazandırdı, ama kullanıcı **Türkçe arayüzde, Türkçe demo rapor** aldı.
Sipariş/proje talebi yok. OpenAlex arama aracımızı kullanmadı; veriyi openalex.org'dan indirmiş.

## 2. Doğrulanmış bulgular

| # | Bulgu | Kanıt | Önem |
|---|---|---|---|
| F1 | `forum/templates/forum/home_intl.html:551` → `window.location.href = '/analiz/?from=hero'` sabit, dil öneki yok | grep + PageView referrer | **Kritik** (tüm EN/DE kullanıcılar) |
| F2 | Kayıt → doğrulama → onboarding zincirinde `?next=` kayboluyor | PageView: onboarding sonrası `/en/` | Yüksek (huni) |
| F3 | Demo rapor Türkçe üretildi (iş, isteğin dilinde çalışıyor) | S3 demo PDF | Yüksek |
| F4 | "Yıllık Yayın Büyüme Oranı" grafiğinde x ekseni ondalıklı yıl (2023.75, 2024.25…) | demo PDF s.3 | Orta (vitrin) |
| F5 | 3 yıllık veride büyüme/CAGR (%302,5) uyarısız sunuluyor — küçük taban etkisi | demo PDF; hesaplar doğru (264%, 345%, CAGR 302,5%) | Orta (doğruluk algısı) |
| F6 | OpenAlex **web CSV** dışa aktarımı resmi format değil, `csv_auto`'ya düşüyor; yıl doğru okundu, yazar/kurum/ülke/anahtar kelime/atıf okunması **doğrulanmadı** | job kaydı | Yüksek (bu kitle oradan geliyor) |
| F7 | Demo dipnotu "Tam rapor için sipariş oluşturunuz" — EN/DE'de sipariş yok, hedef proje talebi | demo PDF kapak | Orta |
| F8 | Demo daima `figures[:3]` = Trend + Büyüme + Yazarlar; büyüme trendin tekrarı, satış gücü düşük | `job_runner.py` | Ürün kararı |
| F9 | `egitim.html:199,230` sabit `/analiz/`, `/tarama/` (sayfa i18n'de) | grep | Düşük |
| F10 | `analiz_console_base.html:17` JSON-LD `url` EN/DE'de de TR adresi | grep | Düşük (SEO) |
| F11 | EN `<title>` "Bibliometric Analysis - Analizus" — anahtar kelime zayıf (Scopus/WoS/VOSviewer/report yok) | curl | Orta (SEO) |
| ✓ | AI Asistan `_localize_paths` önekleri doğru ekliyor — suçsuz | `ai_service.py:102-117` | — |
| ✓ | EN bibliometri sayfası görünür metninde çeviri açığı yok; TR-only link yok | curl + perl | — |

## 3. GÖREV GRUBU A — Hatalar (bu sırayla)

**A1. Hero yönlendirmesi (F1).** Önce URL adını doğrula:
`reverse('analiz_home')` mı `reverse('istatistik:analiz_home')` mı, `translation.override` ile tr/en/de çıktısı.
Sonra `home_intl.html:551` → `'{% url "<doğru_ad>" %}?from=hero'`. `home.html`'e (TR) dokunma.
Deploy: yalnız şablon. Kabul: giriş yapmış kullanıcı `/en/`'de dosya bırakınca `/en/analiz/?from=hero`.

**A2. Dil öneki taraması — yalnız RAPOR (F9, F10 dahil).** i18n'deki tüm şablon/JS/Python'da öneksiz sabit
yollar: `href="/`, `location.href`, `location.assign`, `fetch('/`, `redirect('/`, `HttpResponseRedirect('/`,
e-posta şablonlarındaki mutlak `analizus.com/...`. Dosya:satır + önem sırası. Düzeltme ayrı onayla.

**A3. `next` kaybı (F2).** Önce analiz: register → verification-pending → e-posta doğrulama → onboarding →
son yönlendirme; `next` nerede düşüyor? Öneri: session'da sakla, onboarding sonunda
`url_has_allowed_host_and_scheme` ile doğrulayıp oraya yönlendir. Dosya listesi + onay, sonra kod.
Test: `?next=/en/bibliometrics/` ile kayıt → onboarding sonrası `/en/bibliometrics/`; dış domain `next` reddedilir.

**A4. Rapor dili (F3).** Mevcut: iş, yükleme isteğinin dilinde. Öneri (karar bekliyor, uygulamadan önce sor):
yükleme formuna "Rapor dili" seçimi (TR/EN/DE), varsayılan = arayüz dili. `BibliometricJob`'a alan → **migration**.
Alternatif (migration'sız): yalnız arayüz dilini kullan, A1+A3 düzelince sorun büyük ölçüde kapanır.

**A5. Tam sayı yıl ekseni (F4).** Tüm zaman serisi grafiklerinde (trend, büyüme, kelime trendi, yıllık atıf,
Research Gap) yıl eksenini tam sayıya zorla (`MaxNLocator(integer=True)` veya tick = yıl listesi).
Kabul: 3 yıllık ve 20 yıllık sentetik veriyle PNG'lerde ondalık etiket yok.

**A6. Kısa dönem uyarısı (F5).** Zaman serisi < N tam yıl ise (öneri N=5, `SiteSettings`'e değil analyzer
varsayılanına; `report_notes` eşikleri `inspect` ile okuyor) büyüme/CAGR grafiğine ve "Veri, Yöntem ve Kısıtlar"
bölümüne not: "Veri N yıldan kısa dönemi kapsıyor; büyüme oranları küçük taban etkisine açıktır."
Ayrıca CAGR'ın hangi yıllar arasında hesaplandığı zaten yazıyor — koru. Yeni msgid'ler EN/DE.

**A7. OpenAlex web CSV (F6).** Ben openalex.org'dan ~150 kayıtlık örnek CSV vereceğim (kullanıcı dosyası
KULLANILMAZ). Lokal, S3'süz: parser çıktısında yazar ayrımı, kurum, ülke, anahtar kelime/concept, atıf, DOI,
dergi alanlarını raporla. Eksikse `detect_format`'a `openalex_csv` + sütun eşlemesi öner (`|` ayracı vb.).
Desteklenen formatlar listesi + sayfa metinleri + EN/DE güncellenir. Migration yok (beklenen).

**A8. Demo CTA (F7).** Demo PDF kapak/dipnotunda EN/DE için "Request the full report / expert analysis →
`/en/proje-talebi/?source=bibliometrics&type=bibliometric`", TR'de mevcut sipariş metni.

**A9. EN/DE başlık ve meta (F11).** `bibliometrics/views.py` promo context: EN/DE `promo_title` önerisi
"Bibliometric Analysis from Scopus, WoS & OpenAlex Data – Automated Report | Analizus" (DE karşılığı).
Oturumsuz curl ile doğrula (Google `service_promo.html` görür).

## 4. GÖREV GRUBU B — "Çok iyi bibliometri" yol haritası

> Hedef: bibliometrix/Biblioshiny ve VOSviewer ile **eşit kalite** + onların vermediği şeyler
> (temiz veri, hazır yöntem metni, çok dil, uzman doğrulaması). Konumlandırma: "AI hızlı, biz doğru."
> Sunucu 4 GB RAM: torch/transformers tabanlı paketler (BERTopic vb.) YOK. `networkx`, `scikit-learn`,
> `numpy/pandas`, `matplotlib` ile kal; mevcut requirements'ı kontrol et, yeni paket = `--build`.
> Her faz başında: veri gereksinimi (hangi formatta hangi alan), atlanma koşulu (`skipped` + neden),
> bağımsız hesaplı pytest, PDF'te TR/EN/DE başlık + yorum cümlesi.

### Faz B1 — Veri kalitesi (her şeyin temeli)
1. **DOI ile zenginleştirme (OpenAlex API).** Yüklenen kayıtlarda DOI varsa OpenAlex'ten atıf, yazar ID,
   kurum (ROR), ülke, `referenced_works`, concepts/topics çek. Kazanç: PubMed'de eksik atıf ve ülke tahmini,
   eksik BibTeX/CSV alanları dolar. Toplu `filter=doi:a|b|...` ile istek sayısı düşük tutulur.
   **Önce** günlük OpenAlex bütçe/limitini güncel dokümandan doğrula; kayıt üst sınırı `SiteSettings`'e.
   Raporun Kısıtlar bölümüne: "N kaydın M'si OpenAlex ile zenginleştirildi."
2. **Tekilleştirme:** çoklu dosya birleştirmede DOI → normalize başlık+yıl sırası; kaç kaydın elendiği raporlanır.
3. **Yazar adı birleştirme:** OpenAlex author ID varsa onu kullan; yoksa "Soyad + baş harf" normalizasyonu
   (aksan/büyük-küçük harf). Kurum: ROR varsa ROR, yoksa ham ad (bugünkü davranış, kısıtlarda belirt).
4. **Anahtar kelime normalizasyonu:** küçük harf, tekil/çoğul (basit kural), tire/boşluk; ileride kullanıcı
   eş anlamlı sözlüğü (CSV) yükleyebilir.

### Faz B2 — Bilim haritalama (bibliometrix eşitliği)
1. **Bradford kanunu:** çekirdek dergi bölgeleri (3 eşit bölge), tablo + grafik. Dergi alanı zaten var.
2. **Anahtar kelime eş-oluşum ağı + kümeler:** `networkx` + Louvain (`networkx.community.louvain_communities`,
   seed sabit), min. frekans eşiği, küme renkleri, küme başına ilk kelimeler tablosu.
3. **Tematik harita (Callon merkeziyet × yoğunluk):** motor / niş / gelişen-azalan / temel temalar dört kadranı.
   Tez öğrencilerinin en çok kullandığı görsellerden biri.
4. **Tematik evrim:** 2–3 dönem (kullanıcı kesim yılı ya da otomatik), dönemler arası tema akışı (Sankey benzeri,
   matplotlib ile).
5. **Üç alan grafiği:** Yazar ↔ Anahtar kelime ↔ Dergi/Ülke (ilk N), Sankey.
6. **Ülke işbirliği:** SCP/MCP (tek/çok ülkeli yayın) yığılmış çubuk + ülke işbirliği ağı; dünya haritası
   (geopandas'sız: hafif GeoJSON + matplotlib poligon) opsiyonel.
7. **Atıf ağları (veri varsa):** `referenced_works` / WoS `CR` alanından **ortak atıf** (co-citation) ve
   **bibliyografik eşleşme** (bibliographic coupling) ağları, en çok yerel atıf alan çalışmalar
   (local vs global citations). Referans alanı yoksa `skipped` + neden.
8. **Konu modelleme (özet varsa):** OpenAlex abstract (inverted index → metin) ile scikit-learn NMF/LDA,
   konu başına kelimeler + yıllara göre konu payı. Research Gap'i bununla destekle.

### Faz B3 — Çıktılar (rakiplerin vermediği)
1. **Temizlenmiş veri seti indirme:** XLSX/CSV (tekilleştirilmiş, normalize edilmiş, zenginleştirilmiş).
2. **VOSviewer uyumlu dışa aktarım:** map + network dosyaları (eş-oluşum, ortak yazarlık, ortak atıf) —
   "verini bizde temizle, VOSviewer'da çiz". Biblioshiny için bibliometrix'in okuyabildiği formatta dışa aktarım.
   Format şartnamelerini resmi dokümandan doğrula.
3. **Hazır "Yöntem" metni (TR/EN/DE):** veri kaynağı, sorgu (biliniyorsa), tarih, kayıt akışı, tekilleştirme,
   kullanılan analizler ve yazılım; tezine/makalesine yapıştırılabilir paragraf + önerilen kaynakça.
   PRISMA tarzı kayıt akış diyagramı (bulunan → elenen → analiz edilen).
4. **Grafik başına otomatik yorum cümlesi** (kural tabanlı, sayılardan üretilir — LLM değil; doğruluk garanti).
   LLM'li "bulgular taslağı" yalnız uzman doğrulama paketiyle (B4) ve "taslaktır" etiketiyle.
5. **İnteraktif HTML rapor (sonra):** ağları yakınlaştırılabilir; Tableau/dashboard portföyüne köprü.

### Faz B4 — Ürün ve huni
1. **Demo seçimi (F8, karar):** Trend + en etkileyici 2 görsel (örn. eş-oluşum ağı + tematik harita) —
   `figures[:3]` yerine sabit öncelik listesi.
2. **Paketler:** Demo (ücretsiz) → Tam otomatik rapor → **Uzman paketi** (doğrulama, yöntem/bulgular yazımı,
   revizyon) = proje talebi. Fiyatlar `SiteSettings`'ten.
3. **Rapor dili seçimi** (A4 kararına bağlı) — EN/ID kitlesi için kritik.
4. **EN örnek tam rapor** (anonim, gerçek veri) sayfada indirilebilir; galeri EN/DE başlıklı.
5. **SEO:** EN/DE SSS çevirisi (`tarama_seo_content.py` gettext'siz — ayrı iş), "how to export from Scopus/WoS/
   OpenAlex" rehberleri (cannibalization kontrolü önce).

## 5. Karar bekleyen sorular (Bünyamin)

1. A4: rapor dili seçimi (migration) mı, yalnız arayüz dili mi?
2. A6: kısa dönem eşiği 5 yıl uygun mu?
3. B1-1: OpenAlex zenginleştirme için kayıt üst sınırı (öneri: demo 300, tam 2000 — `SiteSettings`).
4. B4-1: demo hangi 3 grafiği göstersin?
5. B4-2: uluslararası ödeme (EUR/USD) — şimdilik yalnız proje talebi mi?

## 6. Önerilen yürütme sırası

A1 → A2 (rapor) → A3 → A5 + A6 → A7 → A8 + A9 → [karar: A4] → B1 (1→4) → B2 (1→3, sonra 4–8) → B3 (1→3) → B4.
Her adım: plan → onay → kod → test (pytest + gerçek/sentetik veriyle 3 dil × demo/tam PDF) → deploy notu →
`analizus.md` güncelleme notu.
