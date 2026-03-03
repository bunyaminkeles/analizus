"""
YÖK Ulusal Tez Merkezi HTTP scraper.
Selenium kullanmaz — requests + BeautifulSoup ile doğrudan form POST.

Referans: saidsurucu/yoktez-mcp
"""
import re
import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = 'https://tez.yok.gov.tr/UlusalTezMerkezi'
SEARCH_URL = f'{BASE_URL}/SearchTez'
INIT_URL = f'{BASE_URL}/tarama.jsp'

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}


def _make_session():
    session = requests.Session()
    session.headers.update(HEADERS)
    session.verify = False  # YÖK SSL sertifikası sorunlu
    return session


def _build_form(tez_ad='', yazar='', danisman='', universite='',
                tur='0', yil1='0', yil2='0', metin=''):
    return {
        'TezNo': '',
        'TezAd': tez_ad,
        'AdSoyad': yazar.upper() if yazar else '',
        'DanismanAdSoyad': danisman.upper() if danisman else '',
        'Universite': '0',
        'Enstitu': '0',
        'ABD': '0',
        'BilimDali': '0',
        'uniad': universite.upper() if universite else '',
        'ensad': '',
        'abdad': '',
        'bilim': '',
        'Tur': tur or '0',
        'Dil': '0',
        'izin': '0',
        'Durum': '3',
        'EnstituGrubu': '',
        'yil1': str(yil1) if yil1 else '0',
        'yil2': str(yil2) if yil2 else '0',
        'Dizin': '',
        'Metin': metin,
        'Konu': '',
        'islem': '2',
        'Bolum': '0',
    }


def _parse_results(html: str) -> tuple[int, list[dict]]:
    """HTML'den tez kayıtlarını parse et. (total_count, records) döner."""
    soup = BeautifulSoup(html, 'html.parser')

    # Toplam kayıt sayısını bul
    total = 0
    uyari = soup.find(id='divuyari')
    if uyari:
        m = re.search(r'(\d+)\s*kayıt', uyari.get_text())
        if m:
            total = int(m.group(1))

    records = []

    # WATable JS verisi: var rows = [[...], [...], ...]
    script_content = ''
    for script in soup.find_all('script'):
        if script.string and 'var rows' in script.string:
            script_content = script.string
            break

    if script_content:
        # rows array'ini bul
        m = re.search(r'var\s+rows\s*=\s*(\[[\s\S]*?\]);', script_content)
        if m:
            import json
            try:
                rows_raw = m.group(1)
                rows = json.loads(rows_raw)
                for row in rows:
                    if len(row) >= 6:
                        records.append({
                            'tez_no': str(row[0]).strip() if row[0] else '',
                            'author': str(row[1]).strip() if row[1] else '',
                            'title': str(row[2]).strip() if row[2] else '',
                            'year': str(row[3]).strip() if row[3] else '',
                            'university': str(row[4]).strip() if row[4] else '',
                            'thesis_type': str(row[5]).strip() if row[5] else '',
                        })
            except (json.JSONDecodeError, IndexError, TypeError) as e:
                logger.warning(f'YÖK Tez JSON parse hatası: {e}')

    # WATable tablosundan fallback parse (JS yoksa)
    if not records:
        table = soup.find('table', id='watable')
        if not table:
            table = soup.find('table', class_=re.compile('watable|table'))
        if table:
            rows = table.find_all('tr')
            for row in rows[1:]:  # Header satırını atla
                cells = row.find_all('td')
                if len(cells) >= 5:
                    records.append({
                        'tez_no': cells[0].get_text(strip=True),
                        'author': cells[1].get_text(strip=True),
                        'title': cells[2].get_text(strip=True),
                        'year': cells[3].get_text(strip=True),
                        'university': cells[4].get_text(strip=True),
                        'thesis_type': cells[5].get_text(strip=True) if len(cells) > 5 else '',
                    })

    if not total and records:
        total = len(records)

    return total, records


def search(tez_ad='', yazar='', danisman='', universite='',
           tur='0', yil_baslangic=None, yil_bitis=None, metin='',
           demo_limit=5) -> tuple[int, list[dict]]:
    """
    YÖK Tez araması yapar.
    Returns: (total_count, demo_records)
    """
    session = _make_session()

    # 1. Session aç
    try:
        session.get(INIT_URL, timeout=15)
    except Exception as e:
        logger.warning(f'YÖK Tez session init hatası (devam ediliyor): {e}')

    # 2. Arama yap
    form_data = _build_form(
        tez_ad=tez_ad,
        yazar=yazar,
        danisman=danisman,
        universite=universite,
        tur=tur,
        yil1=yil_baslangic,
        yil2=yil_bitis,
        metin=metin,
    )

    response = session.post(SEARCH_URL, data=form_data, timeout=30, allow_redirects=False)

    # HTTP → HTTPS redirect
    if response.status_code in (301, 302, 303, 307, 308):
        redirect_url = response.headers.get('location', '')
        if redirect_url.startswith('http://'):
            redirect_url = redirect_url.replace('http://', 'https://', 1)
        if redirect_url:
            response = session.get(redirect_url, timeout=30)

    response.encoding = 'utf-8'
    total, records = _parse_results(response.text)

    demo = records[:demo_limit]
    return total, demo


def generate_results_txt(records: list[dict], job) -> str:
    """Sonuçları indirilebilir TXT formatına dönüştür."""
    lines = [
        'YÖK Ulusal Tez Merkezi - Arama Sonuçları',
        f'Sorgu: {job.get_query_summary()}',
        f'Toplam: {job.total_results} tez',
        '=' * 60,
        '',
    ]
    for i, r in enumerate(records, 1):
        lines.append(f'{i}. {r.get("title", "(Başlık yok)")}')
        lines.append(f'   Yazar: {r.get("author", "-")}')
        lines.append(f'   Yıl: {r.get("year", "-")} | Tür: {r.get("thesis_type", "-")}')
        lines.append(f'   Üniversite: {r.get("university", "-")}')
        lines.append(f'   Tez No: {r.get("tez_no", "-")}')
        lines.append('')
    return '\n'.join(lines)
