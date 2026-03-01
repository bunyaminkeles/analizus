"""
Bibliometrik veri dosyası parser.
Desteklenen formatlar: BibTeX, Web of Science CSV (TSV), Scopus CSV
Çıktı: normalize edilmiş dict listesi
"""
import io
import re
import logging

logger = logging.getLogger(__name__)

# Normalize edilmiş kayıt şablonu
EMPTY_RECORD = {
    'title': '',
    'authors': [],
    'year': None,
    'journal': '',
    'keywords': [],
    'abstract': '',
    'cited_by': 0,
    'doi': '',
    'pub_type': '',
    'country': '',
    'institution': '',
}


def detect_format(content: str) -> str:
    """
    Dosya içeriğine göre formatı tahmin eder.
    Returns: 'bibtex' | 'csv_wos' | 'csv_scopus' | 'openalex_txt' | 'csv_auto'
    """
    stripped = content.strip()

    # BibTeX: @ ile başlayan kayıtlar
    if re.search(r'@\w+\s*\{', stripped):
        return 'bibtex'

    # OpenAlex TXT: "--- Yayın #" ile başlayan kayıtlar
    if '--- Yayın #' in stripped or 'Başlık       :' in stripped:
        return 'openalex_txt'

    # İlk satırı al (header)
    first_line = stripped.split('\n')[0]

    # WoS: tab-separated, PT AU TI SO TC sütunları
    if '\t' in first_line:
        cols = [c.strip() for c in first_line.split('\t')]
        if any(c in cols for c in ('PT', 'TI', 'AU', 'SO', 'TC')):
            return 'csv_wos'

    # Scopus: comma-separated, Authors Title "Source title" "Cited by" sütunları
    if ',' in first_line:
        lower = first_line.lower()
        if 'authors' in lower and 'title' in lower:
            return 'csv_scopus'

    return 'csv_auto'


def parse_file(content: str, fmt: str = None) -> tuple[list[dict], str]:
    """
    Veriyi parse eder ve geçersiz/boş kayıtları temizler.
    Returns: (records_list, detected_format)
    """
    if not fmt or fmt == 'csv_auto':
        fmt = detect_format(content)

    if fmt == 'bibtex':
        records = _parse_bibtex(content)
    elif fmt == 'csv_wos':
        records = _parse_wos_csv(content)
    elif fmt == 'csv_scopus':
        records = _parse_scopus_csv(content)
    elif fmt == 'openalex_txt':
        records = parse_openalex_txt(content)
    else:
        records = _parse_generic_csv(content)
        fmt = 'csv_auto'

    records = _deduplicate_and_filter(records)
    return records, fmt


def _deduplicate_and_filter(records: list[dict]) -> list[dict]:
    """
    Boş başlıklı satırları atar ve DOI'ye göre tekrarları kaldırır.
    WoS/Scopus dosyalarında "atıf listesi" satırları veya boş separator
    satırları olabilir; bunlar başlıksız geldiği için filtrelenir.
    """
    seen_dois = set()
    seen_titles = set()
    result = []

    for r in records:
        title = r.get('title', '').strip()
        doi   = r.get('doi', '').strip().lower()

        # Başlıksız kayıtları at (separator/atıf listesi satırları)
        if not title:
            continue

        # DOI ile tekrar tespiti
        if doi:
            if doi in seen_dois:
                continue
            seen_dois.add(doi)
        else:
            # DOI yoksa başlık ile (case-insensitive, ilk 80 karakter)
            title_key = title.lower()[:80]
            if title_key in seen_titles:
                continue
            seen_titles.add(title_key)

        result.append(r)

    removed = len(records) - len(result)
    if removed > 0:
        logger.info(f'Parser: {removed} tekrar/boş kayıt çıkarıldı, net: {len(result)}')

    return result


# ─────────────────────────── BibTeX ───────────────────────────

def _parse_bibtex(content: str) -> list[dict]:
    try:
        import bibtexparser
        from bibtexparser.bparser import BibTexParser
        from bibtexparser.customization import convert_to_unicode

        parser = BibTexParser(common_strings=True)
        parser.customization = convert_to_unicode
        bib_db = bibtexparser.loads(content, parser=parser)
        records = []
        for entry in bib_db.entries:
            rec = dict(EMPTY_RECORD)
            rec = {k: (v.copy() if isinstance(v, list) else v) for k, v in rec.items()}

            rec['title'] = _clean(entry.get('title', ''))
            rec['year'] = _safe_int(entry.get('year'))
            rec['journal'] = _clean(entry.get('journal') or entry.get('booktitle', ''))
            rec['abstract'] = _clean(entry.get('abstract', ''))
            rec['doi'] = _clean(entry.get('doi', ''))
            rec['pub_type'] = entry.get('ENTRYTYPE', '').lower()
            rec['cited_by'] = _safe_int(entry.get('cited_by') or entry.get('note', ''))

            # Yazarlar: "Last, First and Last2, First2" formatı
            author_str = entry.get('author', '')
            rec['authors'] = _split_bibtex_authors(author_str)

            # Anahtar kelimeler
            kw_raw = entry.get('keywords', '') or entry.get('keyword', '')
            rec['keywords'] = _split_keywords(kw_raw)

            # Kurum (affiliation)
            rec['institution'] = _clean(entry.get('affiliation', ''))

            records.append(rec)
        return records
    except Exception as e:
        logger.error(f'BibTeX parse hatası: {e}')
        return []


def _split_bibtex_authors(raw: str) -> list[str]:
    if not raw:
        return []
    parts = re.split(r'\s+and\s+', raw, flags=re.IGNORECASE)
    result = []
    for p in parts:
        p = p.strip()
        if ',' in p:
            last, first = p.split(',', 1)
            result.append(f'{first.strip()} {last.strip()}')
        elif p:
            result.append(p)
    return result


# ─────────────────────────── Web of Science TSV ───────────────────────────

def _parse_wos_csv(content: str) -> list[dict]:
    import csv
    records = []
    reader = csv.DictReader(io.StringIO(content), delimiter='\t')
    for row in reader:
        rec = dict(EMPTY_RECORD)
        rec = {k: (v.copy() if isinstance(v, list) else v) for k, v in rec.items()}

        rec['title'] = _clean(row.get('TI', '') or row.get('Title', ''))
        rec['year'] = _safe_int(row.get('PY', '') or row.get('Publication Year', ''))
        rec['journal'] = _clean(row.get('SO', '') or row.get('Source Title', ''))
        rec['abstract'] = _clean(row.get('AB', '') or row.get('Abstract', ''))
        rec['doi'] = _clean(row.get('DI', '') or row.get('DOI', ''))
        rec['cited_by'] = _safe_int(row.get('TC', '') or row.get('Times Cited, All Databases', ''))
        rec['pub_type'] = _clean(row.get('DT', '') or row.get('Document Type', ''))
        rec['country'] = _clean(row.get('CU', '') or row.get('Country/Region', ''))
        rec['institution'] = _clean(row.get('C1', '') or row.get('Affiliations', ''))

        # Yazarlar: noktalı virgülle ayrılmış
        au_raw = row.get('AU', '') or row.get('Authors', '')
        rec['authors'] = [a.strip() for a in re.split(r'[;,]', au_raw) if a.strip()]

        # Anahtar kelimeler (Author Keywords: DE, Plus Keywords: ID)
        kw_raw = row.get('DE', '') or row.get('Author Keywords', '')
        kw_raw2 = row.get('ID', '') or row.get('Keywords Plus', '')
        combined = '; '.join(filter(None, [kw_raw, kw_raw2]))
        rec['keywords'] = _split_keywords(combined)

        records.append(rec)
    return records


# ─────────────────────────── Scopus CSV ───────────────────────────

def _parse_scopus_csv(content: str) -> list[dict]:
    import csv
    records = []
    reader = csv.DictReader(io.StringIO(content))
    for row in reader:
        rec = dict(EMPTY_RECORD)
        rec = {k: (v.copy() if isinstance(v, list) else v) for k, v in rec.items()}

        rec['title'] = _clean(row.get('Title', ''))
        rec['year'] = _safe_int(row.get('Year', ''))
        rec['journal'] = _clean(row.get('Source title', ''))
        rec['abstract'] = _clean(row.get('Abstract', ''))
        rec['doi'] = _clean(row.get('DOI', ''))
        rec['cited_by'] = _safe_int(row.get('Cited by', ''))
        rec['pub_type'] = _clean(row.get('Document Type', ''))
        rec['country'] = _clean(row.get('Country', ''))
        rec['institution'] = _clean(row.get('Affiliations', '') or row.get('Author full names', ''))

        # Yazarlar
        au_raw = row.get('Authors', '')
        rec['authors'] = [a.strip() for a in re.split(r'[;,]', au_raw) if a.strip()]

        # Anahtar kelimeler
        kw_raw = row.get('Author Keywords', '') or row.get('Index Keywords', '')
        rec['keywords'] = _split_keywords(kw_raw)

        records.append(rec)
    return records


# ─────────────────────────── Genel CSV ───────────────────────────

def _parse_generic_csv(content: str) -> list[dict]:
    """Bilinmeyen CSV: sütun adlarını eşleştirmeye çalış."""
    import csv

    # Tab veya virgül ayırt et
    delimiter = '\t' if '\t' in content.split('\n')[0] else ','
    records = []
    reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)

    COL_MAP = {
        'title': ['title', 'başlık', 'ti'],
        'year': ['year', 'yıl', 'py', 'publication year'],
        'journal': ['journal', 'source', 'source title', 'dergi', 'so'],
        'abstract': ['abstract', 'özet', 'ab'],
        'authors': ['authors', 'yazarlar', 'au'],
        'cited_by': ['cited by', 'citation count', 'tc', 'atıf'],
        'doi': ['doi', 'di'],
        'keywords': ['author keywords', 'keywords', 'anahtar kelimeler', 'de'],
    }

    def find_col(row, keys):
        row_lower = {k.lower(): v for k, v in row.items()}
        for k in keys:
            if k in row_lower:
                return row_lower[k]
        return ''

    for row in reader:
        rec = dict(EMPTY_RECORD)
        rec = {k: (v.copy() if isinstance(v, list) else v) for k, v in rec.items()}
        rec['title'] = _clean(find_col(row, COL_MAP['title']))
        rec['year'] = _safe_int(find_col(row, COL_MAP['year']))
        rec['journal'] = _clean(find_col(row, COL_MAP['journal']))
        rec['abstract'] = _clean(find_col(row, COL_MAP['abstract']))
        rec['doi'] = _clean(find_col(row, COL_MAP['doi']))
        rec['cited_by'] = _safe_int(find_col(row, COL_MAP['cited_by']))
        au_raw = find_col(row, COL_MAP['authors'])
        rec['authors'] = [a.strip() for a in re.split(r'[;,]', au_raw) if a.strip()]
        kw_raw = find_col(row, COL_MAP['keywords'])
        rec['keywords'] = _split_keywords(kw_raw)
        records.append(rec)
    return records


# ─────────────────────────── OpenAlex JSON ───────────────────────────

def parse_openalex_json(records: list) -> list[dict]:
    """
    OpenAlex all_results JSON listesini normalize edilmiş bibliometric kayıtlara çevirir.
    AlexSearchJob.all_results alanından doğrudan beslenir.
    """
    result = []
    for pub in records:
        rec = {k: (v.copy() if isinstance(v, list) else v) for k, v in EMPTY_RECORD.items()}

        rec['title'] = _clean(pub.get('title', ''))
        year_raw = pub.get('year', '')
        rec['year'] = _safe_int(year_raw) if year_raw else None
        rec['journal'] = _clean(pub.get('journal', ''))
        rec['abstract'] = _clean(pub.get('abstract', ''))
        rec['doi'] = _clean(pub.get('doi', ''))
        rec['cited_by'] = _safe_int(pub.get('cited_by_count', 0))
        rec['pub_type'] = _clean(pub.get('type', ''))
        rec['institution'] = _clean(pub.get('institutions', ''))

        # Authors: scraper'da ', '.join() ile birleştirilmiş string
        authors_raw = pub.get('authors', '')
        if isinstance(authors_raw, list):
            rec['authors'] = [_clean(a) for a in authors_raw if a]
        elif authors_raw:
            rec['authors'] = [a.strip() for a in str(authors_raw).split(', ') if a.strip()]

        # Keywords + concepts (max 5 concept) birleştir
        keywords = pub.get('keywords', [])
        rec['keywords'] = [_clean(k) for k in (keywords if isinstance(keywords, list) else [])]
        for c in (pub.get('concepts', []) or []):
            cname = _clean(c) if isinstance(c, str) else _clean(c.get('display_name', ''))
            if cname and cname not in rec['keywords']:
                rec['keywords'].append(cname)

        result.append(rec)

    return _deduplicate_and_filter(result)


# ─────────────────────────── OpenAlex TXT ───────────────────────────

def parse_openalex_txt(content: str) -> list[dict]:
    """
    OpenAlex job_runner tarafından üretilen TXT formatını parse eder.

    Format:
        --- Yayın #N ---
        Başlık       : ...
        Yazarlar     : ...
        Dergi/Kaynak : ...
        Yıl          : ...
        DOI          : ...
        Tür          : ...
        Atıf Sayısı  : ...
        Kurumlar     : ...
        Anahtar Kel. : ...
        Özet         : ...
    """
    records = []
    current: dict | None = None

    for line in content.splitlines():
        line = line.strip()
        if line.startswith('--- Yayın #'):
            if current is not None:
                records.append(current)
            current = {k: (v.copy() if isinstance(v, list) else v) for k, v in EMPTY_RECORD.items()}
            continue

        if current is None:
            continue

        def _val(prefix):
            return line[len(prefix):].strip() if line.startswith(prefix) else None

        v = _val('Başlık       :')
        if v is not None:
            current['title'] = _clean(v)
            continue
        v = _val('Yazarlar     :')
        if v is not None:
            current['authors'] = [a.strip() for a in v.split(', ') if a.strip()]
            continue
        v = _val('Dergi/Kaynak :')
        if v is not None:
            current['journal'] = _clean(v)
            continue
        v = _val('Yıl          :')
        if v is not None:
            current['year'] = _safe_int(v) or None
            continue
        v = _val('DOI          :')
        if v is not None:
            current['doi'] = _clean(v)
            continue
        v = _val('Tür          :')
        if v is not None:
            current['pub_type'] = _clean(v)
            continue
        v = _val('Atıf Sayısı  :')
        if v is not None:
            current['cited_by'] = _safe_int(v)
            continue
        v = _val('Kurumlar     :')
        if v is not None:
            current['institution'] = _clean(v)
            continue
        v = _val('Anahtar Kel. :')
        if v is not None:
            current['keywords'] = _split_keywords(v)
            continue
        v = _val('Özet         :')
        if v is not None:
            current['abstract'] = _clean(v)
            continue

    if current is not None:
        records.append(current)

    return _deduplicate_and_filter(records)


# ─────────────────────────── Yardımcılar ───────────────────────────

def _clean(val) -> str:
    if not val:
        return ''
    return re.sub(r'\s+', ' ', str(val).strip().strip('{}'))


def _safe_int(val) -> int:
    try:
        return int(str(val).strip())
    except (ValueError, TypeError):
        # Metin içindeki ilk sayıyı al (örn. "Cited 45 times")
        m = re.search(r'\d+', str(val))
        return int(m.group()) if m else 0


def _split_keywords(raw: str) -> list[str]:
    if not raw:
        return []
    parts = re.split(r'[;|]', raw)
    result = []
    for p in parts:
        p = p.strip().strip('{}')
        if p:
            result.append(p)
    return result
