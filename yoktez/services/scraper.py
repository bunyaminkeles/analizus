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
DETAIL_URL = f'{BASE_URL}/tezDetay.jsp'

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

        # Yöntem 1: JS doc bloğunda doğrudan 'id' ve 'no' alanları
        id_m = re.search(r'(?<![a-zA-Z])id\s*:\s*"((?:[^"\\]|\\.)*)"', block)
        no_m = re.search(r'(?<![a-zA-Z])no\s*:\s*"((?:[^"\\]|\\.)*)"', block)
        detail_id = id_m.group(1) if id_m else ''
        detail_no = no_m.group(1) if no_m else ''

        # Yöntem 2: userId HTML'indeki onclick=tezDetay('id','no')
        if not detail_id:
            user_id_unescaped = user_id_html.replace("\\'", "'").replace('\\"', '"')
            detail_m = re.search(r"""tezDetay\(['"]([\w\-+/=]+)['"]\s*,\s*['"]([\w\-+/=]+)['"]\)""", user_id_unescaped)
            detail_id = detail_m.group(1) if detail_m else ''
            detail_no = detail_m.group(2) if detail_m else ''

        if detail_id:
            logger.info(f'tezDetay bulundu: id={detail_id[:12]}… tez_no={tez_no}')
        else:
            # Hangi alanlar var? Tanımlama için ilk blok içeriğini logla
            field_names = re.findall(r'(\w+)\s*:', block[:500])
            logger.warning(f'tezDetay parametreler YOK, tez_no={tez_no}, alanlar={field_names}, userId={user_id_html[:120]}')

        title_html = _extract_field(block, 'weight')
        # İlk <br> öncesi kısım başlık (İngilizce), sonrası Türkçe
        title_parts = re.split(r'<br\s*/?>', title_html, maxsplit=1)
        title = _strip_html(title_parts[0])
        title_tr = _strip_html(title_parts[1]) if len(title_parts) > 1 else ''

        records.append({
            'tez_no': tez_no,
            'detail_id': detail_id,
            'detail_no': detail_no,
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


def _fetch_detail(session, detail_id: str, detail_no: str) -> dict:
    """Tek bir tezin detay sayfasından özet ve ek bilgileri çek."""
    if not detail_id or not detail_no:
        return {}
    try:
        url = f'{DETAIL_URL}?id={detail_id}&no={detail_no}'
        resp = session.get(url, timeout=15, headers={'Referer': SEARCH_URL})
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        tds = soup.find_all('td')
        logger.info(f'tezDetay id={detail_id[:8]}… status={resp.status_code} tds={len(tds)}')

        result = {}

        # td[6]: başlık + Yazar, Danışman, Yer Bilgisi, Konu, Dizin
        if len(tds) > 6:
            lines = tds[6].get_text(separator='\n').split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('Danışman:'):
                    result['danisman'] = line[len('Danışman:'):].strip()
                elif line.startswith('Konu:'):
                    result['konu'] = line[len('Konu:'):].strip()
                elif line.startswith('Dizin:'):
                    result['dizin'] = line[len('Dizin:'):].strip()

        # td[9]: Türkçe özet
        if len(tds) > 9:
            ozet_tr = tds[9].get_text(separator=' ').strip()
            if ozet_tr:
                result['abstract_tr'] = ozet_tr

        # td[11]: İngilizce özet
        if len(tds) > 11:
            ozet_en = tds[11].get_text(separator=' ').strip()
            if ozet_en:
                result['abstract_en'] = ozet_en

        return result
    except Exception as e:
        logger.warning(f'tezDetay fetch hatası ({detail_id}): {e}')
        return {}


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

    # Demo kayıtları için detay (özet) çek
    for rec in demo:
        detail = _fetch_detail(session, rec.get('detail_id', ''), rec.get('detail_no', ''))
        rec.update(detail)

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
        if r.get('danisman'):
            lines.append(f'   Danışman: {r["danisman"]}')
        if r.get('abstract_tr'):
            lines.append(f'   Özet: {r["abstract_tr"]}')
        if r.get('abstract_en'):
            lines.append(f'   Abstract: {r["abstract_en"]}')
        lines.append('')
    return '\n'.join(lines)
