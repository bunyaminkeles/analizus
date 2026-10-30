"""
Web of Science "Plain Text" (ISI tagged) uyumlu dışa aktarım (B3-2b) —
bibliometrix'in `convert2df(file, dbsource = "wos", format = "plaintext")`
ile okuyabileceği formatta. R/bibliometrix burada kurulu olmadığı için gerçek
yazılımla uçtan uca test edilemedi; format, bibliometrix'in kendi ayrıştırıcı
kaynak kodundan (github.com/massimoaria/bibliometrix, R/isi2df.R) ve resmi
örnek dosyasından (bibliometrix.org/datasets/wos_plaintext.txt) doğrulandı:

- Her kayıt `PT <J|B>` ile başlar, `ER` ile biter; kayıtlar arası boş satır.
- Çok değerli alanlar (AU/AF/CR) her değer kendi satırında; ilk satır
  `TAG değer`, sonraki satırlar tam 3 boşluk + değer (isi2df.R'nin önceki
  etiketi devralma kuralı bu girintiye dayanıyor).
- `FN`/`VR` başlık satırları ve dosya sonundaki `EF` isteğe bağlı (isi2df.R
  varsa siler, yoksa sorun çıkarmaz) — biz yine de gerçek bir WoS indirmesiyle
  tutarlı olsun diye ekliyoruz.
- Zorunlu DEĞİL ama bibliometrix'in beklediği alanlar (AU, DE, C1, RP, CR,
  PY, SO, TI, TC) — RP (düzeltme/yazışma yazarı adresi) elimizde güvenilir
  şekilde yok (hangi yazarın "corresponding author" olduğunu bilmiyoruz),
  yanlış bilgi vermemek için kasıtlı olarak YAZILMIYOR; bibliometrix bunu
  yalnızca bir konsol uyarısıyla belirtir, içe aktarma yine de çalışır.
- CR (atıf listesi) yalnızca BU veri setindeki başka bir kayda işaret eden
  (openalex_id ile eşleşen) referanslar için üretilir — dış dünyaya yapılan
  atıflar için yazar/dergi/cilt/sayfa bilgimiz yok, uydurmuyoruz. Bu da
  Biblioshiny'deki ortak-atıf/tarihsel ağ analizlerinin yalnızca veri seti
  İÇİ atıfları göreceği anlamına gelir (bibliographic_coupling/
  local_citation_counts'taki kısıtla aynı).
"""


def _clean(s) -> str:
    """Bir etiket satırı tek fiziksel satır olmalı — gömülü satır sonlarını temizle."""
    if not s:
        return ''
    return str(s).replace('\r', ' ').replace('\n', ' ').strip()


_DT_LABELS = {
    'article': 'Article', 'journal-article': 'Article',
    'review': 'Review', 'short survey': 'Review',
    'inproceedings': 'Proceedings Paper', 'conference paper': 'Proceedings Paper',
    'conference-paper': 'Proceedings Paper', 'proceedings-article': 'Proceedings Paper',
    'book chapter': 'Book Chapter', 'book-chapter': 'Book Chapter',
    'book': 'Book',
    'editorial': 'Editorial Material',
    'letter': 'Letter',
    'note': 'Note',
    'erratum': 'Correction',
    'preprint': 'Preprint',
    'dataset': 'Data Paper',
}
_BOOK_TYPES = {'book', 'book chapter', 'book-chapter'}


def _pt_code(pub_type: str) -> str:
    return 'B' if (pub_type or '').strip().lower() in _BOOK_TYPES else 'J'


def _dt_label(pub_type: str) -> str:
    t = (pub_type or '').strip().lower()
    if not t:
        return ''
    return _DT_LABELS.get(t, t.title())


def _author_surname(name: str) -> str:
    name = name.strip()
    if ',' in name:
        return name.split(',')[0].strip()
    parts = name.split()
    return parts[-1] if parts else name


def _multiline(tag: str, items: list[str]) -> list[str]:
    out = [f'{tag} {items[0]}']
    out.extend(f'   {item}' for item in items[1:])
    return out


def _cr_line(ref_record: dict) -> str:
    """Bu veri setindeki bir kayda işaret eden atıf için minimal (yazar, yıl[, dergi])
    WoS CR satırı. Cilt/sayfa/DOI bilgimiz olmadığı için eklenmiyor (uydurma yok)."""
    authors = ref_record.get('authors') or []
    year = ref_record.get('year')
    if not authors or not year:
        return ''
    surname = _clean(_author_surname(authors[0])).upper()
    if not surname:
        return ''
    parts = [surname, str(year)]
    journal = _clean(ref_record.get('journal', ''))
    if journal:
        parts.append(journal.upper())
    return ', '.join(parts)


def _record_lines(r: dict, by_oid: dict) -> list[str]:
    lines = [f'PT {_pt_code(r.get("pub_type", ""))}']

    authors = [_clean(a) for a in (r.get('authors') or []) if _clean(a)]
    if authors:
        lines.extend(_multiline('AU', authors))
        lines.extend(_multiline('AF', authors))

    title = _clean(r.get('title', ''))
    if title:
        lines.append(f'TI {title}')

    journal = _clean(r.get('journal', ''))
    if journal:
        lines.append(f'SO {journal}')

    dt = _dt_label(r.get('pub_type', ''))
    if dt:
        lines.append(f'DT {dt}')

    keywords = [_clean(k) for k in (r.get('keywords') or []) if _clean(k)]
    if keywords:
        lines.append('DE ' + '; '.join(keywords))

    abstract = _clean(r.get('abstract', ''))
    if abstract:
        lines.append(f'AB {abstract}')

    c1 = ', '.join(filter(None, [_clean(r.get('institution', '')), _clean(r.get('country', ''))]))
    if c1:
        lines.append(f'C1 {c1}.')

    cr_lines = []
    for ref_oid in (r.get('referenced_works') or []):
        ref = by_oid.get(ref_oid)
        if ref is None or ref is r:
            continue
        cr = _cr_line(ref)
        if cr:
            cr_lines.append(cr)
    if cr_lines:
        lines.extend(_multiline('CR', cr_lines))
        lines.append(f'NR {len(cr_lines)}')

    lines.append(f'TC {r.get("cited_by") or 0}')

    if r.get('year'):
        lines.append(f'PY {r["year"]}')

    doi = _clean(r.get('doi', ''))
    if doi:
        lines.append(f'DI {doi}')

    openalex_id = _clean(r.get('openalex_id', ''))
    if openalex_id:
        lines.append(f'UT OPENALEX:{openalex_id}')

    lines.append('ER')
    lines.append('')
    return lines


def build_wos_plaintext_export(records: list[dict]) -> bytes | None:
    """`records` listesini WoS plaintext (.txt) formatında dışa aktarır.
    Boş listeyle None döner."""
    if not records:
        return None

    by_oid = {r['openalex_id']: r for r in records if r.get('openalex_id')}

    lines = ['FN Clarivate Analytics Web of Science', 'VR 1.0']
    for r in records:
        lines.extend(_record_lines(r, by_oid))
    lines.append('EF')

    return ('\n'.join(lines) + '\n').encode('utf-8')
