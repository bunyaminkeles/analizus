"""
Temizlenmiş veri seti dışa aktarımı (B3-1).
Analize giren (tekilleştirilmiş/zenginleştirilmiş) `records` listesini
XLSX/CSV'ye çevirir. `referenced_works`/`author_ids` dahil edilmez (iç
kullanım, çok uzun/gürültülü) — bkz. bibliometrics/services/parser.py EMPTY_RECORD.
"""
import csv
import io

from django.utils.translation import gettext

COLUMNS = [
    ('title', lambda r: r.get('title', '')),
    ('authors', lambda r: '; '.join(a for a in r.get('authors') or [] if a)),
    ('year', lambda r: r.get('year') or ''),
    ('journal', lambda r: r.get('journal', '')),
    ('keywords', lambda r: '; '.join(k for k in r.get('keywords') or [] if k)),
    ('abstract', lambda r: r.get('abstract', '')),
    ('cited_by', lambda r: r.get('cited_by') or 0),
    ('doi', lambda r: r.get('doi', '')),
    ('pub_type', lambda r: r.get('pub_type', '')),
    ('country', lambda r: r.get('country', '')),
    ('institution', lambda r: r.get('institution', '')),
    ('openalex_id', lambda r: r.get('openalex_id', '')),
]


def _headers() -> list:
    return [
        gettext('Başlık'), gettext('Yazarlar'), gettext('Yıl'), gettext('Dergi'),
        gettext('Anahtar Kelimeler'), gettext('Özet'), gettext('Atıf Sayısı'),
        gettext('DOI'), gettext('Yayın Türü'), gettext('Ülke'), gettext('Kurum'),
        gettext('OpenAlex ID'),
    ]


def _rows(records: list[dict]) -> list:
    return [[getter(r) for _, getter in COLUMNS] for r in records]


def build_clean_xlsx(records: list[dict]) -> bytes:
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Veri'
    ws.append(_headers())
    for row in _rows(records):
        ws.append(row)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def build_clean_csv(records: list[dict]) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(_headers())
    writer.writerows(_rows(records))
    # UTF-8 BOM: Excel'de Türkçe karakterler BOM olmadan bozuk görünüyor
    return b'\xef\xbb\xbf' + buf.getvalue().encode('utf-8')
