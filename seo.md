# Analizus.com SEO Görev Listesi

Analiz tarihi: Mayıs 2026. Öncelik sırasıyla uygulanacak.

---

## ADIM 1 — Canonical + Sitemap + blog_list noindex (Mekanik, hemen uygulanabilir)

### 1a. 18 araç template'ine canonical block ekle
Her `istatistik/templates/istatistik/<araç>.html` dosyasına:
```django
{% block canonical %}/analiz/<slug>/{% endblock %}
```
Araçlar ve slug'ları:
| Template | Canonical slug |
|---|---|
| ttesti.html | ttesti |
| anova.html | anova |
| mann_whitney.html | mann-whitney |
| kruskal_wallis.html | kruskal-wallis |
| ki_kare.html | ki-kare |
| korelasyon.html | korelasyon |
| cronbach.html | cronbach |
| normallik.html | normallik |
| betimsel.html | betimsel |
| orneklem.html | orneklem |
| lineer_regresyon.html | lineer-regresyon |
| lojistik_regresyon.html | lojistik-regresyon |
| friedman.html | friedman |
| tekrarli_anova.html | tekrarli-anova |
| karar_agaci.html | karar-agaci |
| svm.html | svm |
| afa.html | afa |
| wilcoxon.html | wilcoxon |

### 1b. sitemaps.py — IstatistikSitemap'i /analiz/ URL'lerine güncelle
`forum/sitemaps.py` → `IstatistikSitemap.items()` içindeki URL'leri
`istatistik:cronbach` → `analiz:analiz_console` + slug formatına çevir.
(Dikkat: `urls_analiz.py`'deki slug'lar tire kullanıyor: `ki-kare`, `mann-whitney` vb.)

### 1c. blog_list.html noindex kaldır
`forum/templates/forum/blog/blog_list.html` satır 11:
```html
<!-- SİL: <meta name="robots" content="noindex, follow"> -->
```
Blog liste sayfası indekslenebilir olmalı.

---

## ADIM 2 — JSON-LD Altyapısı

### 2a. base.html'e structured_data block ekle
`templates/base.html` → `</head>` öncesine:
```django
{% block structured_data %}{% endblock %}
```

### 2b. analiz_console_base.html'e SoftwareApplication JSON-LD ekle
`istatistik/templates/istatistik/analiz_console_base.html` içinde,
`{% block structured_data %}` override ile dinamik JSON-LD:
```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "{{ tool_title }} — Analizus",
  "description": "{{ tool_description }}",
  "applicationCategory": "EducationalApplication",
  "operatingSystem": "Web",
  "offers": { "@type": "Offer", "price": "0", "priceCurrency": "TRY" },
  "url": "https://www.analizus.com/analiz/{{ active_tool }}/"
}
```

### 2c. Organization JSON-LD — home.html'de zaten mevcut, base.html'e taşı
Tüm sayfaların Organization bilgisine sahip olması için base.html'e statik blok olarak ekle.

---

## ADIM 3 — Teknik SEO Kontrolleri

### 3a. Araç sayfalarında h1 eksik
Araç template'lerinde `<h2>` var, `<h1>` yok. Her araç template'ine:
```html
<h1 class="visually-hidden">{{ tool_title }} — Ücretsiz Online Hesaplama</h1>
```
ya da görünür bir `<h1>` ile araç başlığı.

### 3b. robots.txt — /api/ bloğu ekle
`templates/robots.txt`:
```
Disallow: /api/
```
Crawl budget tasarrufu için.

### 3c. blog_list sitemap'e ekle
`forum/sitemaps.py` → `StaticViewSitemap.items()`'a `'blog_list'` ekle.

---

## ADIM 4 — Rehber İçerik (Önce t-testi örneği, onay sonrası tümüne)

### Yaklaşım: `istatistik/seo_content.py` Python dict
Migration gerektirmez, düzenlemesi kolay. Yapı:
```python
SEO_CONTENT = {
    'ttesti': {
        'h1': 'Bağımsız Örneklem t-Testi — Ücretsiz Online Hesaplama',
        'intro': '...',          # ~200 kelime
        'when_to_use': '...',    # ~150 kelime
        'assumptions': '...',   # ~100 kelime
        'how_to_interpret': '...', # ~150 kelime
        'apa_example': '...',    # ~100 kelime
        'faq': [
            {'q': '...', 'a': '...'},
            # 3-5 soru
        ],
        'related_tools': [       # İç link için
            ('mann_whitney', 'Mann-Whitney U Testi'),
            ('anova', 'Tek Yönlü ANOVA'),
        ],
    },
    # ... diğer 17 araç
}
```

**İlk önce t-testi taslağı göster, onaydan sonra tümünü yaz.**

`analiz_console_base.html`'de `{% block tool_guide %}{% endblock %}` tanımla.
Her araç template'inde bu block'u doldur (sunucu tarafı render — AJAX değil).
`ax-tool-guide` CSS sınıfı ile stillendir.

---

## ADIM 5 — Hangi Test? Sayfası İçerik Hub'ı

`forum/templates/forum/hangi_test.html`:
- FAQPage JSON-LD ekle (karar ağacındaki soru-cevaplardan beslen)
- Meta description güçlendir: "Tezin için hangi istatistik testini kullanmalısın? Adım adım karar rehberi — t-testi, ANOVA, Ki-Kare ve daha fazlası."
- Karar ağacının yanına her testin kısa tanımı + araç sayfasına iç link

---

## ADIM 6 — Blog Altyapısı Kontrolü

- `blog_detail.html` → Article JSON-LD zaten mevcut ✓
- `blog_list.html` → canonical block mevcut ✓, noindex kaldırılacak (Adım 1c)
- Blog slug'larının anahtar kelime içerdiğini doğrula
- Blog yazılarından ilgili araç sayfalarına link kontrolü

---

## Notlar

- `base.html`'de canonical: `{% block canonical %}{{ request.path }}{% endblock %}` — araç template'leri override etmeli
- `analiz_console` view'ı `/analiz/<slug>/` ve `/istatistik/<slug>/` için AYNI view'ı çağırıyor — canonical template'de çözülmeli
- Blog list'te `noindex` var (satır 11) — yanlışlıkla eklenmiş, kaldırılmalı
- Sitemap şu an `/istatistik/` URL'leri kullanıyor, `/analiz/` olmalı
