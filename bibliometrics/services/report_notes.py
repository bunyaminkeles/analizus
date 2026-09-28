"""
Tam raporun "Veri, Yöntem ve Kısıtlar" bölümünün içeriği.
PDF'ten bağımsızdır: yalnız metin/sayı üretir, çizimi pdf_builder yapar.

build_report_notes() girdileri:
  records : analize giren (temizlenmiş) kayıtlar
  stats   : parser'ın doldurduğu sayılar ({'no_title', 'duplicate'})
  skipped : run_all_analyses'in üretemediği analizler [(başlık, neden)]
  source  : {'kind': 'file', 'format': 'Scopus CSV', 'files': 1}
            {'kind': 'openalex', 'found': 12000, 'fetched': 5000, 'max_records': 5000}
"""
import inspect
from django.utils.translation import gettext

from bibliometrics.services import analyzer

# Alan doluluğu bu oranın altındaysa ilgili analizler için ayrıca kısıt yazılır
LOW_COVERAGE_PCT = 50


def _default(fn, name):
    """Analiz fonksiyonunun parametre varsayılanı — metindeki eşik kodla aynı kalsın."""
    return inspect.signature(fn).parameters[name].default


def _has_year(r, last_year):
    y = r.get('year')
    return bool(y) and 1900 < y <= last_year + 1


def _field_coverage(records, last_year):
    """[(alan adı, dolu kayıt sayısı, yüzde, eksikliği kısıt mı)] — analizlerin kullandığı alanlar.
    Atıf 0 eksik veri değil gerçek değerdir; DOI yalnız tekrar tespitinde kullanılır — ikisi kısıt sayılmaz."""
    checks = [
        (gettext('Yayın yılı'),        lambda r: _has_year(r, last_year)),
        (gettext('Yazar'),             lambda r: any(a.strip() for a in r.get('authors') or [])),
        (gettext('Anahtar kelime'),    lambda r: any(k.strip() for k in r.get('keywords') or [])),
        (gettext('Özet'),              lambda r: bool((r.get('abstract') or '').strip())),
        (gettext('Atıf (en az 1)'),    lambda r: (r.get('cited_by') or 0) > 0, False),
        (gettext('Dergi / kaynak'),    lambda r: bool((r.get('journal') or '').strip())),
        (gettext('Ülke'),              lambda r: bool((r.get('country') or '').strip())),
        (gettext('Kurum'),             lambda r: bool((r.get('institution') or '').strip())),
        (gettext('Yayın türü'),        lambda r: bool((r.get('pub_type') or '').strip())),
        (gettext('DOI'),               lambda r: bool((r.get('doi') or '').strip()), False),
    ]
    total = len(records) or 1
    rows = []
    for label, has, *flag in checks:
        n = sum(1 for r in records if has(r))
        rows.append((label, n, round(100 * n / total, 1), flag[0] if flag else True))
    return rows


def _data_flow(records, stats, source):
    """[(adım, kayıt sayısı)] — kaynaktan analize kadar kayıt sayıları."""
    stats = stats or {}
    no_title = stats.get('no_title', 0)
    duplicate = stats.get('duplicate', 0)
    rows = []
    if source.get('kind') == 'openalex':
        rows.append((gettext('OpenAlex\'te bulunan kayıt'), source.get('found', 0)))
        rows.append((gettext('Çekilen kayıt'), source.get('fetched', 0)))
    else:
        rows.append((gettext('Dosyadan okunan kayıt'), len(records) + no_title + duplicate))
    rows.append((gettext('Başlığı olmadığı için çıkarılan'), no_title))
    rows.append((gettext('Tekrar olduğu için çıkarılan'), duplicate))
    rows.append((gettext('Analize giren kayıt'), len(records)))
    return rows


def _source_warnings(records, source):
    """
    OpenAlex çekim sınırı uyarıları. Çekim yayın yılına göre yeniden eskiye sıralı
    olduğundan sınır aşılınca kesilen kısım hep en eski yıllardır.
    Döner: (uyarı metinleri, kapsamı kısmi olan en eski yıl veya None)
    """
    if source.get('kind') != 'openalex':
        return [], None
    found = source.get('found', 0)
    fetched = source.get('fetched', 0)
    max_records = source.get('max_records') or 0
    warnings = []
    years = [r['year'] for r in records if r.get('year') and r['year'] > 1900]
    oldest_year = min(years) if years else None
    partial_year = None

    if found > fetched and max_records and fetched >= max_records:
        partial_year = oldest_year
        if partial_year:
            warnings.append(gettext(
                'OpenAlex\'te {found} kayıt bulundu; çekim sınırı nedeniyle yalnız en yeni {fetched} kayıt '
                'alındı. {year} yılı kısmen, daha eski yıllar hiç kapsanmadı. Bu nedenle yayın trendi, '
                'büyüme oranı, anahtar kelime trendi ve Araştırma Boşluğu Haritası eski dönemi eksik gösterir; '
                'yıllar arası artış olduğundan yüksek görünebilir.'
            ).format(found=found, fetched=fetched, year=partial_year))
        else:
            warnings.append(gettext(
                'OpenAlex\'te {found} kayıt bulundu; çekim sınırı nedeniyle yalnız en yeni {fetched} kayıt alındı.'
            ).format(found=found, fetched=fetched))
    elif fetched < min(found, max_records or found):
        partial_year = oldest_year
        warnings.append(gettext(
            'OpenAlex\'ten veri çekimi tamamlanamadı: {found} kaydın yalnız {fetched} tanesi alınabildi. '
            'Eksik kısım en eski yıllara aittir; zaman içindeki değişimi gösteren analizler bu nedenle '
            'eksik olabilir.'
        ).format(found=found, fetched=fetched))
    return warnings, partial_year


def _rules(source, last_year):
    """Uygulanan kurallar ve eşikler (kısa, tam cümleler)."""
    rules = [
        gettext('Başlığı olmayan kayıtlar çıkarıldı. Tekrar eden kayıtlar DOI\'ye göre, DOI yoksa başlığın '
                'ilk 80 karakterine göre (büyük/küçük harf ayrımı yapılmadan) çıkarıldı.'),
        gettext('Zaman serileri (yayın trendi, büyüme oranı, anahtar kelime trendi, yıllık atıf trendi, '
                'Araştırma Boşluğu Haritası) yalnız tamamlanmış yılları ({year} ve öncesi) kullanır; '
                'içinde bulunulan yıl eksik olduğundan dahil edilmedi. Yayın olmayan yıllar 0 sayıldı.'
                ).format(year=last_year),
        gettext('Anahtar kelimeler küçük harfe çevrildi ve anlamsız sözcükler çıkarıldı; tek sözcüklü '
                'Türkçe kelimeler kök biçimine indirildi, çok sözcüklü ifadeler olduğu gibi kullanıldı. '
                'Kelime bulutunda özetlerdeki en az 4 harfli sözcükler de kullanıldı.'),
    ]
    if source.get('kind') == 'openalex':
        rules.append(gettext('Anahtar kelimesi olmayan OpenAlex kayıtlarında OpenAlex\'in geniş konu '
                             'etiketleri (concepts) anahtar kelime yerine kullanıldı.'))
    rules += [
        gettext('Ülke sayımında bir yayın, yazarlarının bulunduğu her ülke için bir kez sayıldı. '
                'Kurum grafiği yalnız ülke bilgisi hiç yoksa üretilir ve her yayının ilk kurumunu sayar.'),
        gettext('Ağ grafiklerinde en az {n} kez birlikte geçen bağlantılar gösterildi (böyle bağlantı '
                'yoksa en sık bağlantılar). Gösterilen en fazla düğüm: yazar {a}, anahtar kelime {k}, '
                'ülke {c}.').format(
            n=_default(analyzer.author_collaboration, 'min_collab'),
            a=_default(analyzer.author_collaboration, 'max_authors'),
            k=_default(analyzer.keyword_cooccurrence, 'max_kw'),
            c=_default(analyzer.country_collaboration, 'max_countries')),
        gettext('Araştırma Boşluğu Haritası en az 3 yayında geçen en sık {n} anahtar kelimeyi kullanır. '
                'Trend, son {y} tamamlanmış yıldaki yayınlarla önceki yayınların farkının toplam yayına '
                'oranıdır; atıf etkisi, kelimenin geçtiği yayınların ortalama atıfıdır.').format(
            n=_default(analyzer.research_gap, 'top_n'),
            y=_default(analyzer.research_gap, 'recent_years')),
    ]
    return rules


def _limitations(coverage, current_year_count, last_year):
    limitations = [
        gettext('Sonuçlar yalnız bu veri kaynağındaki kayıtları yansıtır; kaynağın taramadığı dergi, '
                'dil ve yayın türleri kapsam dışıdır.'),
        gettext('Yazar, kurum ve dergi adları otomatik olarak birleştirilmedi: aynı yazar farklı '
                'yazımlarla ayrı kişi, aynı adlı farklı yazarlar tek kişi olarak sayılmış olabilir.'),
        gettext('Atıf sayıları verinin alındığı andaki değerlerdir ve kaynaktan kaynağa değişir; yeni '
                'yayınlar atıf toplamak için daha az zaman bulduğundan dezavantajlıdır.'),
    ]
    if current_year_count:
        limitations.append(gettext(
            '{n} kayıt içinde bulunulan yıla ({year}) ait; bu kayıtlar zaman serilerinde yer almaz, '
            'diğer analizlere dahildir.').format(n=current_year_count, year=last_year + 1))
    for label, n, pct, is_limitation in coverage:
        if not is_limitation:
            continue
        if n == 0:
            limitations.append(gettext(
                '"{field}" bilgisi hiçbir kayıtta yok; bu bilgi analizlerde kullanılamadı.'
            ).format(field=label))
        elif pct < LOW_COVERAGE_PCT:
            limitations.append(gettext(
                '"{field}" bilgisi kayıtların yalnız %{pct} kadarında ({n} kayıt) var; bu bilgiye dayanan '
                'analizler yalnız bu kayıtları yansıtır.').format(field=label, pct=round(pct), n=n))
    return limitations


def build_report_notes(records, stats=None, skipped=None, source=None) -> dict:
    source = source or {}
    last_year = analyzer._last_complete_year()
    coverage = _field_coverage(records, last_year)
    current_year_count = sum(1 for r in records if r.get('year') == last_year + 1)
    warnings, partial_year = _source_warnings(records, source)
    return {
        'flow': _data_flow(records, stats, source),
        'coverage': coverage,
        'rules': _rules(source, last_year),
        'skipped': list(skipped or []),
        'limitations': _limitations(coverage, current_year_count, last_year),
        'source_warnings': warnings,
        'partial_year': partial_year,
    }
