# EN/DE Ana Sayfa — Danışmanlık Dönüşümü (Claude Code görev dosyası)

> Hazırlanma: 16 Ekim 2026. Kaynak: canlı `/de/` ve `/en/` HTML'i (oturumsuz `curl -sL`, 16 Ekim 13:13),
> admin oturumlu DE ekran görüntüsü, `analizus.md` §10/§27/§28, `tasks/todo.md`.
> **Bu dosya bir iş listesidir, onay listesi değildir.** Her adım ayrı görevdir; adım bitince DUR, özet ver, onay bekle.

---

## 0. Önce oku (zorunlu)

- `CLAUDE.md` → KIRMIZI ÇİZGİ bölümü (kapsam, çoklu dosyada önce liste+onay, tek seferde tek görev).
- `analizus.md` §28 (özellikle §28.3 çeviri kuralları, §28.5 iş akışı, §28.7 EN/DE ürün kararları), §10 (token'lar,
  bundle.css tuzağı), §26 (CSS/Frontend, Çeviri alt başlıkları).
- `tasks/lessons.md`.

**Bu görevin değişmez kuralları:**
- TR ana sayfa görünümü **değişmeyecek** (Adım 3 ve 4'teki açıkça belirtilen ortak düzeltmeler hariç). Her adımda TR'yi
  önce/sonra karşılaştır.
- msgid = Türkçe kaynak. Yalnız EN/DE'yi değiştirmek için mevcut msgid'in **msgstr**'ını değiştir; TR'yi de değiştiren
  bir msgid düzenlemesi yapma.
- Yeni metin → `{% trans %}` tek satır / `{% blocktrans trimmed %}`; parça birleştirme yok.
- Renk/spacing yalnız `var(--ax-*)`. Yeni inline sabit hex YAZMA. `--ax-color-primary` gibi tanımsız token kullanma.
- `base.css`/`navbar.css`/`footer.css`/`style.css`/`sidebar_widgets.css` değişirse `bundle.css` elle üretilir (§10).
  Ana sayfa CSS'i (`hero.css`, `home_sections.css` vb.) bundle dışı ayrı dosyalardır.
- `main`'e push = otomatik production deploy. Push/merge yalnız kullanıcı "merge et / push et" deyince. Migration
  içeren adımda push öncesi kullanıcıdan `scripts/yedek_indir.sh --simdi` (KENDİ bilgisayarında) iste.
- Şablon değişikliğini doğrulamadan önce `docker compose restart web`.

---

## 1. Canlıda tespit edilen durum (16 Ekim 2026, kanıtlı)

### 1.1 §28.7'ye AYKIRI sızıntılar (EN ve DE'de aynı)
| # | Bölüm (şablon yorumu) | Canlı kanıt |
|---|---|---|
| S1 | `FAZ 3: UZMAN VİTRİNİ` — "Projekte, die einen Experten suchen / Projects looking for an expert" | `/de/market/` "Alle anzeigen →" + `/de/market/job/190/` "Agentic ai … bis zu ₺7500" |
| S2 | `GÜNDEMDEKİ TARTIŞMALAR` | Başlık Türkçe ("Gündemdeki Tartışmalar", "Tümünü Gör →"), `/forum/` + 5 `/topic/<id>/` |
| S3 | Sayaçlar (`.ax-stat-item[data-target]`) | Aktif üye 131, Akademik konu 124, Forum mesajı 247, Tamamlanan proje 31, Analiz 88 — HTML'de `0`, JS ile sayıyor → JS'siz/Google `0` görür; forum/konu sayıları EN/DE'de anlamsız |
| S4 | "So arbeiten wir / How We Work" | Adımlar pazaryeri akışı: "Auftrag einstellen", "Angebote erhalten — Verifizierte Analysten unterbreiten … Preisangebote" |
| S5 | Güven kutuları | "Sichere Zahlung", "Expertenverifizierung", "Transparente Bewertungen (5-Sterne)" — bu mekanizmalar yok (`feature_verified_experts`=False, ödeme kararı blokajda) |
| S6 | SSS | Cevaplar pazaryeri modeli: uzman kendi teklifini verir, gelir = vitrin paketleri + bağış |
| S7 | Premium modalı + footer "Unterstützen Sie uns" | TL fiyatlar (500–5000 TL), IBAN, "Angebote auf Aufträge abgeben" |

**Muhtemel kök neden (doğrula):** S1/S2 bölümleri veri yokken render edilmiyor (Sıfır Kuralı). 16 Ekim turundaki
"EN/DE: 0 `/market/` link" kontrolü açık ilanı olmayan lokal DB'de yapıldığı için geçmiş olabilir.
**Ders:** EN/DE sızıntı kontrolü canlı HTML ile ya da veri dolu DB ile yapılır.

### 1.2 Doğrulanamayan vaatler / dil
- DE: "in Minuten" ×1, "100 % Vertraulichkeit" ×1, "verifizierte Experten/Analysten" ×7, "Expert/innen" ×1,
  "24 Stunden" ×3 (AI doğrulama bandı ×1, Premium ×2). EN: "in minutes", "verified experts/analysts", "24 hours" ×3.
- H1 DE "du" (Analysiere selbst… findest du…), geri kalan "Sie" → karışık hitap.
- DE'de "AI Assistent" ve "KI-Assistent" birlikte.

### 1.3 Renk / erişilebilirlik (WCAG AA küçük metin 4.5:1)
| Öğe | Oran | Durum |
|---|---|---|
| Beyaz / `--ax-accent-primary` #6366f1 (dolu buton) | 4.47 | sınırda kalır |
| `--ax-accent-primary` link / zemin #0b0f19 · kart #111827 ("Alle 18 Tools →", kart içi çipler) | 4.29 · 3.97 | kalır |
| `--ax-text-muted` #64748b / zemin · kart ("oder analysieren Sie selbst:", "oder machen Sie es selbst →") | 4.02 · 3.73 | kalır (ayrıca ~10–11px) |
| `--ax-text-secondary` #94a3b8 | 7.47 · 6.92 | geçer |
| #818cf8 (indigo-400) link | 6.42 · 5.95 | geçer — `--ax-accent-primary-light` değeri bu mu, `base.css`'ten doğrula |

- `home.html` inline kritik CSS: `.ax-hero__personal-badge{…color:var(--ax-color-primary)}` ve
  `.ax-hero__personal-link:hover{color:var(--ax-color-primary)}` → **tanımsız token** (canlıda doğrulandı).
- Bölüm başlıklarında inline sabit hex: `#fbbf24` (pazar başlığı), `#f97316` (forum başlığı), `#a855f7`, `#818cf8` ×3.
- Dekoratif kart görseli (`.ax-market-visual`) ~1240px'te sağ kenarda kırpılıyor (ekran görüntüsü).

### 1.4 SEO
- `<title>` DE: "Analizus — Kostenlose Plattform für Statistik- und Datenanalyse"; EN: "… Free Statistical Analysis and
  Data Analysis Platform" → danışmanlık değil ücretsiz araç sinyali.
- Meta description "Laden Sie Ihre Datei hoch…" / "Upload your file…" ile başlıyor.
- SSS'deki 5 soru **H2** → başlık hiyerarşisi bozuk (H3 olmalı).
- hreflang + canonical doğru (tr/en/de/x-default).
- Proje talebi CTA'ları ve `?source=` ayrımı doğru: nav ×2, hero, home_market, home_corporate, home_steps,
  verification, home_faq, footer.

---

## 2. Adımlar (sırayla; her biri ayrı görev)

### ADIM 1 — Sızıntıları kapat (S1, S2, S3'ün forum/konu kalemleri) — HATA, karar zaten var
**Kapsam:** yalnız §28.7'nin zaten verdiği kararı uygulamak.
1. `forum/templates/forum/home.html`'i oku. S1 ve S2 bölümlerinin mevcut koşullarını, S3 sayaçlarının hangi
   değişkenlerden beslendiğini raporla.
2. S1 (Uzman Vitrini) ve S2 (Gündemdeki Tartışmalar) bölümlerini `{% if LANGUAGE_CODE == 'tr' %}` ile sar.
3. S3: EN/DE'de "Akademische Themen" ve "Forenbeiträge" kalemlerini gizle. "Aktive Mitglieder" kalemini de gizle
   (topluluk metriği). "Abgeschlossene Projekte" ve "Abgeschlossene Analysen" kalsın mı → **kullanıcıya sor**, varsayma.
4. Sızıntı tarama: `home.html` ve dahil ettiği partial'larda `job_list`, `market`, `forum`, `topic`, `blog`,
   `uzman_dizini`, `yoktez`, `trdizin`, `oaipmh`, `arena` geçen tüm link/bölümleri listele; her biri için EN/DE
   koşulu var mı göster. Yeni bulunan varsa **değiştirmeden** raporla.
5. Değişecek dosyaları listele → onay al → uygula.

**Doğrulama (veri dolu DB şart):**
- Test Client render'ı `transaction.atomic()` içinde yap: açık bir `FreelanceJob` (status='open', `approved_at` dolu —
  boşsa `save()` yeniden yayınlar) ve forumda en az bir konu oluştur, `/`, `/en/`, `/de/` render et, rollback.
  S3'e dokunan hiçbir kod çalıştırma (lokal ve prod aynı bucket).
- Beklenen: EN/DE'de `/market/` 0, `/forum/` 0, `/topic/` 0, "Gündemdeki" 0. TR'de sayılar önceki ile aynı.
- Deploy sonrası (kullanıcı çalıştırır):
  ```bash
  for l in de en; do echo "== $l"; curl -sL https://www.analizus.com/$l/ | grep -oE 'href="[^"]*(market|forum|/topic/)[^"]*"' | sort | uniq -c; done
  ```
  Önceki canlı değer: her dilde `/market/` 2, `/forum/` 1, `/topic/` 5 → hedef 0.

**Deploy etkisi:** migration yok, collectstatic gerekmez, `--build` yok.
**analizus.md:** §27'ye tur notu; §28.7 "Gizli" E maddesine Uzman Vitrini + Gündemdeki Tartışmalar + sayaç kalemleri;
§26 (Genel Süreç) dersine "EN/DE sızıntı kontrolü veri dolu DB/canlı HTML ile".

---

### ADIM 2 — Vaatler ve hitap: geçici düzeltme (yalnız EN/DE msgstr) — onay gerekli
**Amaç:** Adım 6 (yeni EN/DE ana sayfa) canlıya çıkana kadar yanlış vaatleri kaldırmak. TR etkilenmez.
**Yöntem:** yalnız `locale/{de,en}/LC_MESSAGES/django.po` msgstr düzenlemesi. msgid'e dokunma.

| Kaynak (DE canlı) | Öneri DE msgstr | Öneri EN msgstr |
|---|---|---|
| Analysiere selbst. / Wenn nicht, findest du hier jemanden, der es tut. | Analysieren Sie selbst. / Oder lassen Sie es von Fachleuten erledigen. | (mevcut kalabilir) |
| Lassen Sie Ihre Analyse von Expert/innen erstellen | Analyse von Fachleuten erstellen lassen | (mevcut) |
| … werden Sie in Minuten mit einem verifizierten Experten Ihres Fachgebiets zusammengebracht. 100 % Vertraulichkeit, keine versteckten Kosten. | … wir finden die passende Fachperson für Ihr Projekt. Vertraulicher Umgang mit Ihren Daten, kostenlose Erstbewertung. | … we find the right specialist for your project. Confidential handling of your data, free initial assessment. |
| In ihrem Fachgebiet verifizierte Experten | Fachleute mit Erfahrung in Ihrem Gebiet | Specialists experienced in your field |
| Transparente Preisgestaltung ohne Überraschungen | Unverbindliches Angebot vor Arbeitsbeginn | Non-binding quote before work starts |
| … innerhalb von 24 Stunden prüfen … (AI doğrulama bandı) | „24 Stunden" çıkar → „… prüfen und einen Verifizierungsbericht erstellen" | "within 24 hours" çıkar |
| AI Assistent | KI-Assistent | — |
| "verifizierte Experten" (alt başlık, footer) | „Fachleute" | "specialists" |

> Not: Bu msgstr'lar TR kaynağın birebir çevirisi olmaktan bilerek sapar (geçici). Her birinin msgid'ini po'da bul ve
> tabloyu gerçek msgid'lerle kullanıcıya göster; aynı msgid başka sayfada (ör. `proje_talebi.html`, `ai_cozumler`)
> kullanılıyorsa etkisini raporla. Premium "24 Stunden" Adım 5'e bağlı, burada dokunma.

**İş akışı (§28.5):** po sonuna/yerinde düz metin düzenleme (polib `save()` tüm dosyayı sarar — kullanma veya
`git diff --stat`'ı kontrol et), `compilemessages -l en -l de` → çıktıda `error` ara; container'da msgfmt yoksa host'ta
`msgfmt -c -o …/django.mo …/django.po`; `docker compose restart web`.
**Doğrulama:**
```bash
curl -sL https://www.analizus.com/de/ | grep -oiE "in Minuten|100 ?% Vertraulichkeit|verifizierte[a-z]* [A-Za-z]+|Expert/innen|findest du|24 Stunden|AI Assistent" | sort | uniq -c
curl -sL https://www.analizus.com/en/ | grep -oiE "in minutes|verified [a-z]+|24 hours" | sort | uniq -c
```
Hedef: Premium kaynaklı "24 Stunden/hours" ×2 dışında 0. TR çıktısı değişmemiş olmalı.
**Deploy:** migration yok.

---

### ADIM 3 — Renk ve kontrast (ana sayfa) — TR'yi de etkiler, onay gerekli
1. `base.css`'te `--ax-accent-primary-light` ve `--ax-accent-primary-hover` gerçek değerlerini oku, raporla.
2. `home.html:~371,374` `--ax-color-primary` → `--ax-accent-primary-light` (koyu zeminde okunurluk; değer #818cf8 ise
   6.42:1). Kullanıcıya hangi token'ı seçtiğini gerekçesiyle söyle.
3. Koyu zemindeki küçük metin linkleri ("Alle 18 Tools →", kart içi çipler, `.ax-hero-dropzone__examples a` vb.):
   `--ax-accent-primary` → `--ax-accent-primary-light`.
4. "oder analysieren Sie selbst:", "oder machen Sie es selbst →" ve benzeri `--ax-text-muted` küçük metinler →
   `--ax-text-secondary`. Kural `home.html` inline kritik CSS + `hero.css`'te iki kopya olabilir (12 Ekim notu) →
   ikisini birlikte değiştir.
5. Bölüm başlıklarındaki inline sabit hex'ler (`#fbbf24`, `#f97316`, `#a855f7`, `#818cf8`): yalnız **listele** ve
   token karşılığını öner (sarı → `--ax-accent-warning`). Uygulama ayrı onay.
6. `.ax-market-visual` kırpılması: 1024/1280/1440px'te Playwright ekran görüntüsü al, kırpılıyorsa öner, uygulama ayrı onay.
7. **Kapsam dışı (ayrı görev olarak yalnız not düş):** global `.ax-btn--primary` zemini (beyaz metin 4.47) — bundle.css
   ve tüm siteyi etkiler.

**Doğrulama:** Playwright TR/EN/DE × 360/768/1280px; hesaplanan kontrastları rapora yaz.
**Deploy:** migration yok; ana sayfa CSS dosyaları değişirse hash'li ad collectstatic ile (deploy.sh) gelir. bundle.css
kaynaklarına dokunulmadıysa bundle üretimi gerekmez.

---

### ADIM 4 — SEO başlık/açıklama ve SSS başlık seviyesi — onay gerekli
1. Ana sayfa `<title>` ve meta description'ın nereden geldiğini bul (view context / şablon bloğu / msgid).
2. Yalnız EN/DE msgstr öneri (TR değişmez):
   - DE title: `Statistikberatung & Datenanalyse für Forschung und Unternehmen | Analizus`
   - DE description: `Statistische Beratung und Auswertung für Promovierende, Forschende und Unternehmen – methodisch sauber, mit APA-Bericht. Kostenlose Erstbewertung, dazu 18 kostenlose Statistik-Tools.`
   - EN title: `Statistical Consulting & Data Analysis for Research and Business | Analizus`
   - EN description: `Statistical consulting and analysis for PhD candidates, researchers and companies — methodologically sound, with an APA-style report. Free initial assessment, plus 18 free statistics tools.`
   - Uzunlukları ölç (title ≤ ~60–65, description ≤ ~155–160 karakter); aşıyorsa kısalt ve göster.
3. SSS soruları H2 → H3 (accordion yapısını bozmadan). Bu TR'yi de etkiler; FAQPage JSON-LD varsa etkilenmediğini doğrula.

**Doğrulama:** `curl -sL …/de/ | grep -o '<title>.*</title>'`; H1/H2/H3 sırası listesi TR/EN/DE.
**Sonra (kullanıcı):** GSC'de `/en/` ve `/de/` URL denetimi + dizine ekleme isteği; Bing IndexNow.

---

### ADIM 5 — Premium/bağış bloğu EN/DE — KARAR BEKLİYOR
Soru (kullanıcıya): Premium modalı + footer "Unterstützen Sie uns" EN/DE'de gizlensin mi?
Gerekçe: Premium'un ana faydası (ilanlara teklif verme, haftalık ilan hakkı) EN/DE'de pazaryeri kapalı olduğu için
anlamsız; fiyatlar TL; "24 Stunden" vaadi burada.
Karar "gizle" ise: modal ve footer bloğunun hangi şablonda (muhtemelen `templates/base.html`,
`templates/partials/footer.html`) olduğunu bul, tüm açılış noktalarını (buton, link, JS tetikleyici) listele, onay al,
`LANGUAGE_CODE == 'tr'` ile sar. §28.7'ye yeni madde.

---

### ADIM 6 — Danışmanlık odaklı EN/DE ana sayfası (`home_intl.html` + flag) — KARARLAR + MIGRATION
**Önkoşul kararlar (bölüm 3'teki K1, K4, K5, K7).**
**Mimari öneri:**
- Yeni flag `SiteSettings.feature_intl_consulting_home` (default False) — **üç yerde**: model + `feature_flags()`
  context processor + `SiteSettingsAdmin.fieldsets`. Migration (no-data).
- Ana sayfa view'ı: flag açık ve dil `tr` değilse `forum/home_intl.html`, aksi halde mevcut `home.html`. TR yolu
  bit-bit aynı kalmalı.
- Yeni şablon TR ana sayfadaki bileşen sınıflarını (`ax-hero`, `ax-section-card`, `ax-btn` …) yeniden kullanır; yeni CSS
  gerekirse `home_sections.css`'e (bundle dışı) eklenir.
- Gerekirse view'da yalnız EN/DE bölümlerinin ihtiyaç duyduğu sorgular çalışsın (forum/ilan sorguları atlanır → N+1 ve
  gereksiz sorgu yok).

**Bölüm sırası:**
1. Hero — tek birincil CTA (`?source=hero`), ikincil küçük link "Selbst rechnen → 18 Tools". Dropzone: K7'ye göre.
2. Güven şeridi — yalnız doğrulanmış gerçekler (K1, K5). Sayaç yoksa bölüm yok (Sıfır Kuralı).
3. İki iş kolu kartı — Akademik / Kurumsal (kurumsal kart `ai_cozumler`'e de link, `?source=home_corporate`).
4. Teslimatlar listesi.
5. Süreç (4 adım, `?source=home_steps`).
6. Sınırlarımız (ghostwriting yok).
7. AI analiz doğrulama bandı (mevcut, `?source=verification`, "24 saat" olmadan).
8. Ücretsiz araçlar (kompakt) + Hangi Test? + Akademik Tarama (yalnız `intl` araçlar).
9. SSS (danışmanlık modeli, H3 sorular, FAQPage JSON-LD) + kapanış CTA (`?source=home_faq`).
**Yeni `source` değerleri gerekirse** `ProjectRequest.SOURCE_CHOICES`'a ekle (no-op AlterField migration) — önce mevcut
listeyi kontrol et.

**Metin taslakları** (msgid = TR kaynak; EN/DE msgstr). Claude Code TR msgid'leri bu anlamla yazar, kullanıcıya gösterir:

*Hero*
- TR: `İstatistik danışmanlığı ve veri analizi — yöntemsel olarak sağlam, izlenebilir biçimde raporlanmış.`
  DE: `Statistische Beratung und Datenanalyse – methodisch sauber, nachvollziehbar dokumentiert.`
  EN: `Statistical consulting you can defend.`
- TR: `Doktora öğrencileri, araştırmacılar ve kurumlar için: analizinizi planlıyor, yürütüyor ve açıklıyoruz — APA raporu ve yeniden üretilebilir kodla.`
  DE: `Für Promovierende, Forschende und Unternehmen: Wir planen, rechnen und erklären Ihre Analyse – mit APA-konformem Bericht und reproduzierbarem Code.`
  EN: `For PhD candidates, researchers and companies: we plan, run and explain your analysis — with an APA-style report and reproducible code.`
- CTA — DE: `Kostenlose Erstberatung anfragen` · EN: `Request a free consultation`
- İkincil — DE: `Lieber selbst rechnen? 18 kostenlose Statistik-Tools →` · EN: `Prefer to run it yourself? 18 free statistics tools →`
- Konumlandırma satırı — DE: `KI ist schnell. Wir sorgen dafür, dass es stimmt.` · EN: `AI is fast. We make sure it's right.`

*Süreç (4 adım)*
1. DE `Anfrage` — `Beschreiben Sie Ihr Projekt und Ihre Daten. Kostenlos und unverbindlich.` · EN `Request` — `Describe your project and data. Free and non-binding.`
2. DE `Erstgespräch & Angebot` — `Wir klären Fragestellung, Methode und Umfang und senden Ihnen ein Festpreisangebot.` · EN `Scoping & quote` — `We clarify your question, method and scope, then send a fixed-price quote.` **(Festpreis/fixed-price yalnız K3 "teklif" ise; değilse "Angebot/quote")**
3. DE `Analyse` — `Wir führen die Analyse durch und dokumentieren jeden Schritt.` · EN `Analysis` — `We run the analysis and document every step.`
4. DE `Bericht & Rückfragen` — `Sie erhalten Bericht, Tabellen und Code. Rückfragen von Betreuung oder Gutachtern beantworten wir im vereinbarten Umfang.` · EN `Report & follow-up` — `You get the report, tables and code. We address supervisor or reviewer feedback within the agreed scope.`

*Teslimatlar* — DE/EN: Analyseplan / analysis plan · Ergebnistabellen im APA-Format / APA-style results tables ·
Methoden- und Ergebnisteil (Entwurf) / methods & results section (draft) · SPSS-, R- oder Python-Code / SPSS, R or Python
code · eine Überarbeitungsrunde / one revision round **(sayısı K3 ile teyit)**.

*Sınırlarımız* — DE: `Wir schreiben keine Abschlussarbeiten. Wir beraten zur Methodik und führen Analysen nachvollziehbar durch – die wissenschaftliche Arbeit bleibt Ihre.`
EN: `We don't write theses. We advise on methodology and carry out analyses transparently — the scholarly work remains yours.`

*SSS konuları* (cevaplarda yalnız K kararlarına dayanan bilgi): Wie läuft die Zusammenarbeit ab? · Was kostet eine
Analyse? (K3) · Wie schnell bekomme ich Ergebnisse? (K4 — süre yazılmayacaksa "nach Umfang, im Angebot festgelegt") ·
Wie gehen Sie mit meinen Daten um? (K5) · In welcher Sprache arbeiten Sie? (K1) · Schreiben Sie meine Arbeit? (hayır →
Sınırlarımız).

**Doğrulama:** Test Client TR/EN/DE (flag açık/kapalı × 3 dil = 6 render); TR çıktısı flag açıkken de değişmemiş
(HTML diff, CSRF token hariç); Playwright 360/768/1280; kontrast; `/market/`,`/forum/`,`/topic/` = 0; JSON-LD
`json.loads`; inline JS `node --check`; pytest.
**Deploy:** migration VAR → push öncesi kullanıcıdan yedek. Flag canlıda kapalı gelir; kullanıcı admin'den açar.

---

### ADIM 7 — EN/DE navigasyon — Adım 6'dan sonra, onay gerekli
Öneri: `Leistungen/Services ▾` (hizmet sayfaları yoksa geçici olarak ana sayfa bölüm çapaları) · `Ablauf/Process` ·
`Kostenlose Tools/Free tools ▾` (Statistik-Tools, Welcher Test?, KI-Assistent, Bibliometrie) · `Akademische
Recherche` · `Über uns` · sağda çerçeveli CTA `Erstberatung/Free consultation` (`?source=nav`).
"Schulung/Training": K6'ya göre. Masaüstü + mobil drawer + footer birlikte; 360px ve 1280px genişlik bütçesini Playwright
ile ölç (§10 Mobil Navbar Genişlik Bütçesi).

### ADIM 8 — Impressum (DE) — K2 bekliyor
`/de/impressum/` (+ EN `legal notice`), footer'da her sayfada link. İçerik kullanıcı/avukattan; Claude içerik uydurmaz,
yalnız sayfa iskeleti + link. Footer'daki Ankara adresiyle tutarlılık.

### ADIM 9 — EN/DE hizmet sayfaları — YALNIZ TASARIM DOKÜMANI (kod yok)
`ServicePage` şu an yalnız TR. Tasarım önerisi: `language` alanı + dil karşılıklarını bağlayan grup anahtarı; URL öneki
`gettext_lazy` ile (`/de/leistungen/<slug>/`, `/en/services/<slug>/`); **risk:** dile göre slug farklı → mevcut
`hreflang_alternates` (aynı yol varsayımı) ve `set_language` sarmalayıcısı özel eşleme ister. Önerilen ilk sayfalar:
Statistikberatung für Promotion / Methodik & Gutachterantwort / Datenanalyse & Dashboards für Unternehmen / KI &
Automatisierung (mevcut `ai_cozumler`). Çıktı: `tasks/todo.md`'ye plan; kullanıcı onayı olmadan kod yok.

### ADIM 10 — Proje talebi → ön görüşme formu — Adım 6'dan sonra, MIGRATION
Önce `/de/proje-talebi/` canlı HTML'ini ve `proje_talebi.html`'i oku. Öneri alanlar: aşama (planlama / veri toplandı /
analiz bitti-rapor lazım / hakem yanıtı), bütçe aralığı, teslim tarihi, isteğe bağlı görüşme randevu linki
(`SiteSettings`'ten — sabit yazma). EN/DE'de pazaryerine geri link olmadığını doğrula (TR'de var, 12 Ekim U2).

### ADIM 11 — Ölçüm
Kullanıcıya verilecek salt okunur komut (Hetzner):
```bash
docker compose exec web python manage.py shell -c "from forum.models import ProjectRequest as P; from django.db.models import Count; print(list(P.objects.values('language','source').annotate(n=Count('id')).order_by('language','-n')))"
```
Başlangıç değerini `analizus.md` §28.7'ye yaz; Adım 6 canlıya çıktıktan 4 hafta sonra tekrar.

---

## 3. Kullanıcı kararları (adımlar bunlara bağlı)
| # | Soru | Etkilediği adım |
|---|---|---|
| K1 | EN/DE danışmanlığı kim, hangi dillerde (DE/EN/TR) teslim edecek? | 6, 7 |
| K2 | Impressum için şirket/kişi bilgileri (avukat kontrolü) | 8 |
| K3 | Fiyat modeli: paket ("ab X €", `SiteSettings`) mi, yalnız teklif mi? Revizyon turu sayısı? | 6 |
| K4 | Taahhüt edilebilecek ilk yanıt süresi var mı? Yoksa süre yazılmaz. | 2, 6 |
| K5 | Veri işleme: sunucu + S3 bölgesi, NDA / AVV sunulacak mı? (doğrulanmadan "Daten in Deutschland" yazılmaz) | 6 |
| K6 | Eğitimler EN/DE'de veriliyor mu? | 7 |
| K7 | Dropzone EN/DE hero'dan tamamen kalksın mı? | 6 |
| K8 | Premium/bağış EN/DE'de gizlensin mi? | 5 |
| K9 | EN/DE sayaçlardan "Tamamlanan proje / analiz" kalsın mı? | 1 |

## 4. Kapsam dışı (ayrı görev olarak not düş, uygulama)
- Global `.ax-btn--primary` kontrastı (bundle.css, tüm site).
- TR ana sayfadaki benzer vaatler ("dakikalar içinde", "%100 gizlilik", "doğrulanmış uzman") — TR pazaryeri açık olduğu
  için ayrı değerlendirme.
- Ana sayfanın 12 ayrı CSS dosyası (HTML'de her biri iki kez geçiyor — preload+noscript mi, doğrula).
- Uzman profillerinin anonime açılması (ertelenmiş karar).

## 5. Her adım sonunda rapor formatı
1. Değişen dosyalar + satırlar (diff özeti)
2. Doğrulama çıktıları (komut + sonuç)
3. Deploy etkisi (migration? collectstatic? `--build`? bundle?)
4. `analizus.md` / `tasks/todo.md` / `tasks/lessons.md` için eklenecek kısa not
5. Sıradaki adım için gereken karar/onay
