"""
Tam raporun "Veri, Yöntem ve Kısıtlar" bölümünün içeriği.
PDF'ten bağımsızdır: yalnız metin/sayı üretir, çizimi pdf_builder yapar.

build_report_notes() girdileri:
  records : analize giren (temizlenmiş) kayıtlar
  stats   : parser'ın doldurduğu sayılar ({'no_title', 'duplicate'})
  skipped : run_all_analyses'in üretemediği analizler [(başlık, neden)]
  source  : {'kind': 'file', 'format': 'Scopus CSV', 'files': 1}
            {'kind': 'openalex', 'found': 12000, 'fetched': 5000, 'max_records': 5000}
            {'kind': 'pubmed', ...} — openalex ile aynı anahtarlar
"""
import inspect
from django.utils.formats import number_format
from django.utils.translation import gettext

from bibliometrics.services import analyzer

def _num(n):
    """Metin içindeki sayı — tablolardaki gibi dile göre binlik ayırıcılı (25.000 / 25,000)."""
    return number_format(n, force_grouping=True)


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
    elif source.get('kind') == 'pubmed':
        rows.append((gettext('PubMed\'de bulunan kayıt'), source.get('found', 0)))
        rows.append((gettext('Çekilen kayıt'), source.get('fetched', 0)))
    else:
        rows.append((gettext('Dosyadan okunan kayıt'), len(records) + no_title + duplicate))
    rows.append((gettext('Başlığı olmadığı için çıkarılan'), no_title))
    rows.append((gettext('Tekrar olduğu için çıkarılan'), duplicate))
    rows.append((gettext('Analize giren kayıt'), len(records)))
    return rows


def _source_warnings(records, source):
    """
    OpenAlex/PubMed çekim sınırı uyarıları. Çekim yayın yılına göre yeniden eskiye sıralı
    olduğundan sınır aşılınca kesilen kısım hep en eski yıllardır.
    Döner: (uyarı metinleri, kapsamı kısmi olan en eski yıl veya None)
    """
    kind = source.get('kind')
    if kind not in ('openalex', 'pubmed'):
        return [], None
    # Kaynak adı ekle birlikte değiştiği için ("OpenAlex'te" / "PubMed'de") her kaynağa tam cümle msgid
    if kind == 'openalex':
        msg_cut_year = gettext(
            'OpenAlex\'te {found} kayıt bulundu; çekim sınırı nedeniyle yalnız en yeni {fetched} kayıt '
            'alındı. {year} yılı kısmen, daha eski yıllar hiç kapsanmadı. Bu nedenle yayın trendi, '
            'büyüme oranı, anahtar kelime trendi ve Araştırma Boşluğu Haritası eski dönemi eksik gösterir; '
            'yıllar arası artış olduğundan yüksek görünebilir.')
        msg_cut = gettext(
            'OpenAlex\'te {found} kayıt bulundu; çekim sınırı nedeniyle yalnız en yeni {fetched} kayıt alındı.')
        msg_incomplete = gettext(
            'OpenAlex\'ten veri çekimi tamamlanamadı: {found} kaydın yalnız {fetched} tanesi alınabildi. '
            'Eksik kısım en eski yıllara aittir; zaman içindeki değişimi gösteren analizler bu nedenle '
            'eksik olabilir.')
    else:
        msg_cut_year = gettext(
            'PubMed\'de {found} kayıt bulundu; çekim sınırı nedeniyle yalnız en yeni {fetched} kayıt '
            'alındı. {year} yılı kısmen, daha eski yıllar hiç kapsanmadı. Bu nedenle yayın trendi, '
            'büyüme oranı ve anahtar kelime trendi eski dönemi eksik gösterir; yıllar arası artış '
            'olduğundan yüksek görünebilir.')
        msg_cut = gettext(
            'PubMed\'de {found} kayıt bulundu; çekim sınırı nedeniyle yalnız en yeni {fetched} kayıt alındı.')
        msg_incomplete = gettext(
            'PubMed\'den veri çekimi tamamlanamadı: {found} kaydın yalnız {fetched} tanesi alınabildi. '
            'Eksik kısım en eski yıllara aittir; zaman içindeki değişimi gösteren analizler bu nedenle '
            'eksik olabilir.')
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
            warnings.append(msg_cut_year.format(found=_num(found), fetched=_num(fetched), year=partial_year))
        else:
            warnings.append(msg_cut.format(found=_num(found), fetched=_num(fetched)))
    elif fetched < min(found, max_records or found):
        partial_year = oldest_year
        warnings.append(msg_incomplete.format(found=_num(found), fetched=_num(fetched)))
    return warnings, partial_year


def _rules(source, last_year, stats=None):
    """Uygulanan kurallar ve eşikler (kısa, tam cümleler)."""
    stats = stats or {}
    rules = [
        gettext('Başlığı olmayan kayıtlar çıkarıldı. Tekrar eden kayıtlar DOI\'ye göre, DOI yoksa noktalama '
                'yok sayılarak normalize edilmiş başlık ve yayın yılına göre (ikisi de bilinen kayıtlarda) '
                'çıkarıldı.'),
        gettext('Zaman serileri (yayın trendi, büyüme oranı, anahtar kelime trendi, yıllık atıf trendi, '
                'Araştırma Boşluğu Haritası) yalnız tamamlanmış yılları ({year} ve öncesi) kullanır; '
                'içinde bulunulan yıl eksik olduğundan dahil edilmedi. Yayın olmayan yıllar 0 sayıldı.'
                ).format(year=last_year),
        gettext('Anahtar kelimeler küçük harfe çevrildi, tire ile boşluk aynı sayıldı (ör. "COVID-19" ve '
                '"COVID 19" aynı anahtar kelime) ve anlamsız sözcükler çıkarıldı; tek sözcüklü Türkçe '
                'kelimeler kök biçimine indirildi, kök bulunamayan tek sözcükler basit bir çoğul→tekil '
                'kuralıyla (ör. "cats"→"cat") sadeleştirildi, çok sözcüklü ifadeler olduğu gibi kullanıldı. '
                'Kelime bulutunda özetlerdeki en az 4 harfli sözcükler de kullanıldı.'),
    ]
    if source.get('kind') == 'openalex':
        rules.append(gettext('Anahtar kelimesi olmayan OpenAlex kayıtlarında OpenAlex\'in geniş konu '
                             'etiketleri (concepts) anahtar kelime yerine kullanıldı.'))
    elif source.get('kind') == 'pubmed':
        rules.append(gettext('Yazar anahtar kelimesi olmayan PubMed kayıtlarında MeSH terimleri anahtar '
                             'kelime yerine kullanıldı.'))
    if stats.get('zenginlestirme_enriched'):
        rules.append(gettext(
            'DOI\'si olan kayıtlardan {n} tanesi OpenAlex ile zenginleştirildi: eksik atıf sayısı, '
            'ülke, kurum ve/veya anahtar kelime bilgisi tamamlandı.'
        ).format(n=_num(stats['zenginlestirme_enriched'])))
    rules += [
        gettext('Ülke ve kurum sayımında bir yayın, yazarlarının bulunduğu her ülke ve kurum için bir kez '
                'sayıldı. Kurum grafiği yalnız ülke bilgisi hiç yoksa üretilir.'),
        gettext('Ağ grafiklerinde en az {n} kez birlikte geçen bağlantılar gösterildi (böyle bağlantı '
                'yoksa en sık bağlantılar). Gösterilen en fazla düğüm: yazar {a}, anahtar kelime {k}, '
                'ülke {c}.').format(
            n=_default(analyzer.author_collaboration, 'min_collab'),
            a=_default(analyzer.author_collaboration, 'max_authors'),
            k=_default(analyzer.keyword_cooccurrence, 'max_kw'),
            c=_default(analyzer.country_collaboration, 'max_countries')),
        gettext('Anahtar kelime kümeleri (Küme 1, 2…) Louvain algoritmasıyla belirlendi (sabit başlangıç '
                'değeriyle — aynı veri her çalıştırmada aynı kümeleri verir), en büyükten küçüğe '
                'numaralandırıldı.'),
        gettext('Araştırma Boşluğu Haritası en az 3 yayında geçen en sık {n} anahtar kelimeyi kullanır. '
                'Trend, son {y} tamamlanmış yıldaki yayınlarla önceki yayınların farkının toplam yayına '
                'oranıdır; atıf etkisi, kelimenin geçtiği yayınların ortalama atıfıdır.').format(
            n=_default(analyzer.research_gap, 'top_n'),
            y=_default(analyzer.research_gap, 'recent_years')),
        gettext('Bradford Kanunu\'nda dergiler yayın sayısına göre sıralanıp, toplam yayının üçte birini '
                'üreten art arda gelen dergi grupları 3 bölgeye ayrıldı (Bölge 1 = çekirdek).'),
        gettext('Tematik Harita\'da her tema (anahtar kelime kümesi) merkeziyet (diğer temalarla bağlantı '
                'gücü) ve yoğunluğuna (tema içi bağlantı gücü) göre konumlandırıldı; kadran sınırları tüm '
                'temaların ortalama merkeziyet ve yoğunluğudur.'),
    ]
    return rules


def _short_series_span(records, last_year):
    """Tamamlanmış yıllardaki takvim yılı aralığı (publication_growth_rate ile aynı tanım) — A6."""
    years = [r['year'] for r in records if r.get('year') and 1900 < r['year'] <= last_year]
    if not years:
        return 0
    return max(years) - min(years) + 1


def _limitations(coverage, current_year_count, last_year, source=None, records=None):
    is_pubmed = (source or {}).get('kind') == 'pubmed'
    limitations = [
        gettext('Sonuçlar yalnız bu veri kaynağındaki kayıtları yansıtır; kaynağın taramadığı dergi, '
                'dil ve yayın türleri kapsam dışıdır.'),
        gettext('Yazar adları soyad ve ilk adın baş harfine göre birleştirildi (ör. "Smith, J." ve '
                '"John Smith" aynı kişi sayılır); bu basit bir yaklaşımdır, aynı adlı farklı yazarlar '
                'yanlışlıkla birleştirilmiş veya aynı yazarın farklı yazımları ayrı sayılmış olabilir. '
                'Kurum ve dergi adları otomatik olarak birleştirilmedi.'),
    ]
    span = _short_series_span(records or [], last_year)
    if 3 <= span < analyzer.SHORT_SERIES_YEARS:
        limitations.append(gettext(
            'Veri {n} yıldan kısa bir dönemi kapsıyor; büyüme oranları küçük taban etkisine açıktır.'
        ).format(n=analyzer.SHORT_SERIES_YEARS))
    if is_pubmed:
        limitations += [
            gettext('PubMed atıf sayısı sağlamadığından atıfa dayanan analizler (en çok atıf alan yayınlar, '
                    'H-index, yıllık atıf trendi, Araştırma Boşluğu Haritası) üretilmedi.'),
            gettext('Ülke ve kurum bilgisi tahminidir: PubMed bu bilgileri ayrı alan olarak vermez; yazar '
                    'adres metninden otomatik çıkarıldı. Adresinde ülke adı geçmeyen yazarlar ülke '
                    'sayımına, kurum adı tanınamayan adresler kurum sayımına girmedi.'),
        ]
    else:
        limitations.append(gettext(
            'Atıf sayıları verinin alındığı andaki değerlerdir ve kaynaktan kaynağa değişir; yeni '
            'yayınlar atıf toplamak için daha az zaman bulduğundan dezavantajlıdır.'))
    if current_year_count:
        limitations.append(gettext(
            '{n} kayıt içinde bulunulan yıla ({year}) ait; bu kayıtlar zaman serilerinde yer almaz, '
            'diğer analizlere dahildir.').format(n=_num(current_year_count), year=last_year + 1))
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
                'analizler yalnız bu kayıtları yansıtır.').format(field=label, pct=round(pct), n=_num(n)))
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
        'rules': _rules(source, last_year, stats),
        'skipped': list(skipped or []),
        'limitations': _limitations(coverage, current_year_count, last_year, source, records),
        'source_warnings': warnings,
        'partial_year': partial_year,
    }
