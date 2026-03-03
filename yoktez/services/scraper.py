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


def _extract_field(block: str, key: str) -> str:
    """JS doc objesinden bir alanı çıkar: key: "value" """
    m = re.search(key + r'\s*:\s*"((?:[^"\\]|\\.)*)"', block)
    return m.group(1) if m else ''


def _strip_html(text: str) -> str:
    """HTML tag'lerini temizle."""
    return re.sub(r'<[^>]+>', '', text).replace('\\"', '"').replace("\\'", "'").strip()


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

    # YÖK Tez formatı: var rows = []; ... var doc = { userId:..., name:..., ... }; rows.push(doc);
    # Her kayıt ayrı bir `var doc = {...};` bloğu olarak gelir.
    doc_blocks = re.findall(r'var\s+doc\s*=\s*\{(.*?)\};', html, re.DOTALL)

    for block in doc_blocks:
        user_id_html = _extract_field(block, 'userId')
        tez_no_m = re.search(r'>(\d+)<', user_id_html)
        tez_no = tez_no_m.group(1) if tez_no_m else ''

        title_html = _extract_field(block, 'weight')
        # İlk <br> öncesi kısım başlık (İngilizce), sonrası Türkçe
        title_parts = re.split(r'<br\s*/?>', title_html, maxsplit=1)
        title = _strip_html(title_parts[0])
        title_tr = _strip_html(title_parts[1]) if len(title_parts) > 1 else ''

        records.append({
            'tez_no': tez_no,
            'author': _extract_field(block, 'name').strip(),
            'title': title,
            'title_tr': title_tr,
            'year': _extract_field(block, 'age').strip(),
            'university': _extract_field(block, 'uni').strip(),
            'thesis_type': _extract_field(block, 'important').strip(),
            'language': _extract_field(block, 'height').strip(),
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
        if r.get('title_tr'):
            lines.append(f'   TR: {r["title_tr"]}')
        lines.append(f'   Yazar: {r.get("author", "-")}')
        lines.append(f'   Yıl: {r.get("year", "-")} | Tür: {r.get("thesis_type", "-")} | Dil: {r.get("language", "-")}')
        lines.append(f'   Üniversite: {r.get("university", "-")}')
        lines.append(f'   Tez No: {r.get("tez_no", "-")}')
        lines.append('')
    return '\n'.join(lines)
