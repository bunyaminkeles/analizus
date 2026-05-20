"""
YÖK Ulusal Tez Merkezi HTTP scraper — YENİ ARAYÜZ (2025+).
Selenium kullanmaz — requests + BeautifulSoup ile GForm2 (islem=4).

Sonuç sayfası: tezSorguSonucYeni.jsp  (div.result-card elementleri)
Detay endpoint: tezBilgiDetay.jsp?kayitNo=...&tezNo=...  (JSON yanıt)
"""
import re
import time
import random
import logging
import threading
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Aynı anda en fazla 2 job YÖK'e aktif istek atabilir.
# Kalan job'lar thread'de bekler — sunucu IP'mizden eş zamanlı yük sınırlanır.
_yoktez_semaphore = threading.Semaphore(2)

# İstekler arası bekleme aralıkları (saniye) — YÖK firewall'ını tetiklemez
_DELAY_INIT_TO_SEARCH  = (1.5, 3.0)   # session init → POST arama
_DELAY_BETWEEN_DETAILS = (0.8, 2.0)   # her detail isteği arası
_DELAY_DETAIL_RETRY    = (5.0, 9.0)   # 429/503 sonrası retry bekle
_MAX_DETAIL_RETRIES    = 2            # detail endpoint için maksimum yeniden deneme

BASE_URL = 'https://tez.yok.gov.tr/UlusalTezMerkezi'
SEARCH_URL = f'{BASE_URL}/SearchTez'
INIT_URL   = f'{BASE_URL}/tarama.jsp'
DETAIL_URL = f'{BASE_URL}/tezBilgiDetay.jsp'

# Birden fazla gerçekçi User-Agent — her session rastgele birini seçer
_USER_AGENTS = [
    ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
     'AppleWebKit/537.36 (KHTML, like Gecko) '
     'Chrome/124.0.0.0 Safari/537.36'),
    ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
     'AppleWebKit/537.36 (KHTML, like Gecko) '
     'Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'),
    ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
     'AppleWebKit/537.36 (KHTML, like Gecko) '
     'Chrome/123.0.0.0 Safari/537.36'),
    ('Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) '
     'Gecko/20100101 Firefox/125.0'),
]

HEADERS = {
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'DNT': '1',
}

# nevi değerleri: arama alanı seçimi
NEVI_TEZ_ADI  = '1'
NEVI_YAZAR    = '2'   # YÖK tarafında kararsız, çalışmayabilir
NEVI_DANISMAN = '3'
NEVI_OZET     = '6'
NEVI_TUMU     = '7'

# tur kodu → thesis_type metni (lokal filtreleme için)
TUR_MAP = {
    '1': 'yüksek lisans',
    '2': 'doktora',
    '3': 'tıpta uzmanlık',
    '4': 'sanatta yeterlik',
}


def _make_session():
    session = requests.Session()
    session.headers.update(HEADERS)
    # Her session'da rastgele User-Agent — farklı tarayıcı izlenimi
    session.headers['User-Agent'] = random.choice(_USER_AGENTS)
    return session


def _human_delay(lo: float, hi: float):
    """Verilen aralıkta insan davranışını taklit eden rastgele bekleme."""
    time.sleep(random.uniform(lo, hi))


def _determine_query(tez_ad='', yazar='', danisman='', metin=''):
    """
    Dolu alan sayısına göre keyword ve nevi belirler.
    Birden fazla alan doluysa tez_ad önceliklidir.
    Returns: (keyword, nevi)
    """
    if tez_ad:
        return tez_ad, NEVI_TEZ_ADI
    if danisman:
        return danisman, NEVI_DANISMAN
    if metin:
        return metin, NEVI_OZET
    if yazar:
        return yazar, NEVI_YAZAR
    return '', NEVI_TUMU


def _build_form(keyword='', nevi=NEVI_TUMU, tip='2',
                universite='', yil_baslangic=None, yil_bitis=None, tur='0'):
    """GForm2 (islem=4) POST verisi."""
    return {
        'keyword':    keyword,
        'keyword1':   '',
        'keyword2':   '',
        'ops_field':  'and',
        'ops_field1': 'and',
        'nevi':       nevi,
        'tip':        tip,
        'islem':      '4',
        'uniad':      universite.upper() if universite else '',
        'yil1':       str(yil_baslangic) if yil_baslangic else '0',
        'yil2':       str(yil_bitis) if yil_bitis else '0',
        'Tur':        tur if tur and tur != '0' else '0',
    }


def _strip_html(text: str) -> str:
    return re.sub(r'<[^>]+>', '', text or '').strip()


def _parse_results(html: str) -> tuple[int, list[dict]]:
    """
    tezSorguSonucYeni.jsp HTML'inden kayıtları parse et.
    Returns: (total_count, records)
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Toplam kayıt sayısı — "X kayıt bulundu" veya "Toplam: X" gibi metinler
    total = 0
    for text_node in soup.find_all(string=re.compile(r'\d[\d\.\s]*kayıt', re.I)):
        nums = re.findall(r'[\d\.]+', str(text_node))
        for n in nums:
            n_clean = n.replace('.', '')
            if n_clean.isdigit() and int(n_clean) > total:
                total = int(n_clean)

    # Yedek: sayfada "15.377" gibi büyük sayıyı içeren span/div bul
    if not total:
        for tag in soup.find_all(['span', 'div', 'p', 'strong'], string=re.compile(r'^\s*[\d\.]+\s*$')):
            n_clean = tag.get_text(strip=True).replace('.', '')
            if n_clean.isdigit() and int(n_clean) > 100:
                total = int(n_clean)
                break

    cards = soup.find_all('div', class_='result-card')
    logger.info(f'YÖK Tez: {len(cards)} kart bulundu, bildirilen toplam={total}')

    records = []
    for card in cards:
        kayit_no = card.get('data-kayitno', '')
        tez_no   = card.get('data-tezno', '')

        # TR Başlık — div.card-title
        title_tag = card.find(class_='card-title')
        title_tr = title_tag.get_text(strip=True) if title_tag else ''

        # EN Başlık — div.card-info style="font-style: italic" (inline stil, <i> tag değil)
        title_en = ''
        info_divs = card.find_all(class_='card-info')
        for info in info_divs:
            style = info.get('style', '')
            if 'italic' in style:
                title_en = info.get_text(strip=True)
                break

        # Tez No — kart metninde "Tez No: 962854" yazıyor, bunu önce oku
        # data-tezno hash olabildiğinden regex eşleşmesi varsa daima onu kullan
        for info in info_divs:
            raw = info.get_text(strip=True)
            m = re.search(r'Tez No\s*:?\s*(\d+)', raw, re.I)
            if m:
                tez_no = m.group(1)
                break
        # Hâlâ numeric değilse data-kayitno'yu dene
        if not tez_no.isdigit() and kayit_no.isdigit():
            tez_no = kayit_no

        records.append({
            'tez_no':      tez_no,
            'kayit_no':    kayit_no,
            'title_tr':    title_tr,
            'title':       title_en,   # EN başlık (eski 'title' alanıyla uyumlu)
            'author':      '',         # detail'den gelecek
            'year':        '',         # detail'den gelecek
            'university':  '',         # detail'den gelecek
            'thesis_type': '',         # detail'den gelecek
            'language':    '',         # detail'den gelecek
        })

    if not total and records:
        total = len(records)

    return total, records


def _fetch_detail(session, kayit_no: str, tez_no: str) -> dict:
    """tezBilgiDetay.jsp'den JSON olarak detay çeker. 429/503 durumunda yeniden dener."""
    if not kayit_no and not tez_no:
        return {}

    for attempt in range(_MAX_DETAIL_RETRIES + 1):
        try:
            resp = session.get(
                DETAIL_URL,
                params={'kayitNo': kayit_no, 'tezNo': tez_no},
                timeout=15,
                headers={'Referer': SEARCH_URL, 'X-Requested-With': 'XMLHttpRequest'},
            )
            resp.encoding = 'utf-8'
            logger.info(f'tezBilgiDetay kayitNo={kayit_no} tezNo={tez_no} '
                        f'status={resp.status_code} deneme={attempt + 1}')

            # Rate limit veya geçici hata — bekle ve yeniden dene
            if resp.status_code in (429, 503) and attempt < _MAX_DETAIL_RETRIES:
                wait = random.uniform(*_DELAY_DETAIL_RETRY) * (attempt + 1)
                logger.warning(f'YÖK Tez rate limit ({resp.status_code}), {wait:.1f}s beklenyor...')
                time.sleep(wait)
                continue

            break  # Başarılı ya da son deneme
        except Exception as e:
            if attempt < _MAX_DETAIL_RETRIES:
                time.sleep(random.uniform(*_DELAY_DETAIL_RETRY))
                continue
            logger.warning(f'tezBilgiDetay fetch hatası (kayitNo={kayit_no}): {e}')
            return {}

    try:
        data = resp.json()
    except Exception:
        # JSON değilse HTML'den parse et (eski format fallback)
        return _parse_detail_html(resp.text)

    try:

        result = {}

        # Danışman — "<strong>Danışman: </strong>DOÇ. DR. X" formatı
        danisman_raw = data.get('danisman', '')
        if danisman_raw:
            cleaned = _strip_html(danisman_raw)
            # "Danışman: " prefixini kaldır
            cleaned = re.sub(r'^Danışman\s*:\s*', '', cleaned, flags=re.I).strip()
            if cleaned:
                result['danisman'] = cleaned

        # Üniversite — "yer": "Akdeniz Üniversitesi / Sağlık Bilimleri / Beslenme"
        yer = data.get('yer', '')
        if yer:
            result['university'] = yer.split('/')[0].strip()

        # Türkçe özet
        tr_ozet = _strip_html(data.get('trOzet', ''))
        if tr_ozet:
            result['abstract_tr'] = tr_ozet

        # İngilizce özet
        en_ozet = _strip_html(data.get('enOzet', ''))
        if en_ozet:
            result['abstract_en'] = en_ozet

        # Anahtar kelimeler (HTML içerebilir)
        kw_tr = _strip_html(data.get('anahtarKelimeTr', ''))
        if kw_tr:
            result['keywords_tr'] = kw_tr
        kw_en = _strip_html(data.get('anahtarKelimeEn', ''))
        if kw_en:
            result['keywords_en'] = kw_en

        # Dil
        dil = data.get('dil', '')
        if dil:
            result['language'] = dil

        # Gerçek sayısal tez no — yeni API'de farklı key adları dene
        for key in ('tezNo', 'tez_no', 'TezNo', 'no', 'kayitNo', 'kayit_no', 'KayitNo', 'id'):
            val = str(data.get(key, '')).strip()
            if val and val.isdigit():
                result['tez_no'] = val
                break

        # APA referansından yazar, yıl, tez türü, üniversite çıkar
        # Ham: "AKTAR, M. (2026). <i>Başlık.</i> [Doktora tezi, Üniversite Adı]."
        apa_raw = data.get('apa_ref', '') or data.get('apaRef', '')
        apa = _strip_html(apa_raw)   # <i> gibi HTML taglerini temizle
        if apa:
            result['apa_ref'] = apa

            year_m = re.search(r'\((\d{4})\)', apa)
            if year_m:
                result['year'] = year_m.group(1)

            author_m = re.match(r'^([^(]+)\(', apa)
            if author_m:
                result['author'] = author_m.group(1).strip().rstrip(',').strip()

            # "[Doktora tezi, Üniversite Adı]"
            bracket_m = re.search(r'\[([^\]]+)\]', apa)
            if bracket_m:
                bracket_content = bracket_m.group(1)
                parts = [p.strip() for p in bracket_content.split(',')]
                if parts:
                    result.setdefault('thesis_type', parts[0])
                if len(parts) > 1:
                    result.setdefault('university', parts[1])

        # MLA'dan tez türü fallback
        mla = data.get('mla_ref', '') or data.get('mlaRef', '')
        if mla and 'thesis_type' not in result:
            type_m = re.search(r'(Yüksek Lisans Tezi|Doktora Tezi|Tıpta Uzmanlık|Sanatta Yeterlik)', mla, re.I)
            if type_m:
                result['thesis_type'] = type_m.group(1)

        return result

    except Exception as e:
        logger.warning(f'tezBilgiDetay fetch hatası (kayitNo={kayit_no}): {e}')
        return {}


def _parse_detail_html(html: str) -> dict:
    """Detay sayfası JSON değil HTML dönerse eski td tabanlı parse ile bilgi çıkar."""
    soup = BeautifulSoup(html, 'html.parser')
    tds = soup.find_all('td')
    result = {}
    if len(tds) > 6:
        lines = tds[6].get_text(separator='\n').split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('Danışman:'):
                result['danisman'] = line[len('Danışman:'):].strip()
    if len(tds) > 9:
        ozet_tr = tds[9].get_text(separator=' ').strip()
        if ozet_tr:
            result['abstract_tr'] = ozet_tr
    if len(tds) > 11:
        ozet_en = tds[11].get_text(separator=' ').strip()
        if ozet_en:
            result['abstract_en'] = ozet_en
    return result


def _year_ok(record: dict, year_from, year_to) -> bool:
    year_str = record.get('year', '')
    if not year_str or not year_str.isdigit():
        return True   # bilinmiyorsa dahil et
    y = int(year_str)
    if year_from and y < year_from:
        return False
    if year_to and y > year_to:
        return False
    return True


def _type_ok(record: dict, tur: str) -> bool:
    if not tur or tur == '0':
        return True
    expected = TUR_MAP.get(tur, '')
    rec_type = record.get('thesis_type', '').lower()
    return expected in rec_type


def _uni_ok(record: dict, universite: str) -> bool:
    if not universite:
        return True
    return universite.lower() in record.get('university', '').lower()


def search(tez_ad='', yazar='', danisman='', universite='',
           tur='0', yil_baslangic=None, yil_bitis=None, metin='',
           demo_limit=5) -> tuple[int, list[dict]]:
    """
    YÖK Tez araması yapar (yeni arayüz: islem=4).
    Returns: (total_count, demo_records)
    """
    with _yoktez_semaphore:
        return _search_impl(tez_ad=tez_ad, yazar=yazar, danisman=danisman,
                            universite=universite, tur=tur,
                            yil_baslangic=yil_baslangic, yil_bitis=yil_bitis,
                            metin=metin, demo_limit=demo_limit)


def _search_impl(tez_ad='', yazar='', danisman='', universite='',
                 tur='0', yil_baslangic=None, yil_bitis=None, metin='',
                 demo_limit=5) -> tuple[int, list[dict]]:
    session = _make_session()

    # Session çerezi al
    try:
        session.get(INIT_URL, timeout=15)
    except Exception as e:
        logger.warning(f'YÖK Tez session init hatası (devam ediliyor): {e}')

    # İnsan davranışını taklit: sayfa yüklendikten sonra biraz bekle
    _human_delay(*_DELAY_INIT_TO_SEARCH)

    keyword, nevi = _determine_query(tez_ad=tez_ad, yazar=yazar,
                                     danisman=danisman, metin=metin)
    if not keyword and universite:
        keyword = universite
        nevi = NEVI_TUMU

    logger.info(f'YÖK Tez arama: keyword="{keyword}" nevi={nevi}')

    form_data = _build_form(keyword=keyword, nevi=nevi,
                            universite=universite, yil_baslangic=yil_baslangic,
                            yil_bitis=yil_bitis, tur=tur)

    try:
        response = session.post(SEARCH_URL, data=form_data, timeout=45, allow_redirects=True)
        response.encoding = 'utf-8'
    except Exception as e:
        logger.error(f'YÖK Tez POST hatası: {e}')
        raise

    logger.info(f'YÖK Tez yanıt URL={response.url} status={response.status_code} boyut={len(response.text)}')

    # Hata sayfası kontrolü
    if 'tezSorguSonucHata' in response.url or 'hata' in response.url.lower():
        logger.warning(f'YÖK Tez hata sayfasına yönlendirildi: {response.url}')
        return _search_legacy(session, tez_ad=tez_ad, yazar=yazar, danisman=danisman,
                              universite=universite, tur=tur,
                              yil_baslangic=yil_baslangic, yil_bitis=yil_bitis,
                              metin=metin, demo_limit=demo_limit)

    total, records = _parse_results(response.text)
    if total == 0:
        total = len(records)

    # Kart yapısında yıl/üniversite/tür YOK — detail'den sonra filtrele.
    has_extra_filters = bool(
        (yil_baslangic or yil_bitis) or
        (universite) or
        (tur and tur != '0')
    )
    # Filtre varsa daha fazla aday çek; uniad server-side çalışırsa az yeterli, çalışmazsa 50'ye kadar tara
    if universite:
        candidate_count = min(len(records), 50)
    elif has_extra_filters:
        candidate_count = min(len(records), demo_limit * 5)
    else:
        candidate_count = demo_limit
    candidates = records[:candidate_count]

    enriched = []   # detail çekilmiş tüm adaylar
    demo = []       # filtreden geçenler

    for idx, rec in enumerate(candidates):
        # Her detail isteğinden önce insan benzeri bekleme (ilk kayıt hariç küçük ek gecikme)
        if idx > 0:
            _human_delay(*_DELAY_BETWEEN_DETAILS)

        detail = _fetch_detail(session, rec.get('kayit_no', ''), rec.get('tez_no', ''))
        if detail:
            for field in ('year', 'author', 'university', 'thesis_type', 'language',
                          'danisman', 'abstract_tr', 'abstract_en', 'keywords_tr',
                          'keywords_en', 'apa_ref'):
                if detail.get(field):
                    rec[field] = detail[field]
        enriched.append(rec)

        if (len(demo) < demo_limit
                and _year_ok(rec, yil_baslangic, yil_bitis)
                and _type_ok(rec, tur)):
            # _uni_ok yerel kontrolü kaldırıldı: YÖK uniad parametresiyle sunucu
            # tarafında filtreler; detail başarısız olunca university='' kalır ve
            # lokal filtre tüm kayıtları silerdi.
            demo.append(rec)
            if len(demo) >= demo_limit:
                break

    # Demo hâlâ boşsa (örn. detail'ler başarısız, yıl/tür filtresi de eşleşmedi)
    # en azından enriched kayıtların ilklerini göster
    if not demo and enriched:
        logger.info('YÖK Tez: filtreli demo bulunamadı, filtresiz fallback')
        demo = enriched[:demo_limit]

    logger.info(f'YÖK Tez tamamlandı: sunucu_toplam={total} demo={len(demo)}')
    return total, demo


def _search_legacy(session, tez_ad='', yazar='', danisman='', universite='',
                   tur='0', yil_baslangic=None, yil_bitis=None, metin='',
                   demo_limit=5) -> tuple[int, list[dict]]:
    """
    Eski YÖK Tez formu (islem=2) ile fallback arama.
    Yeni site bunu artık desteklemiyor olabilir.
    """
    logger.info('YÖK Tez: eski form (islem=2) deneniyor')
    form_data = {
        'TezNo': '', 'TezAd': tez_ad,
        'AdSoyad': yazar.upper() if yazar else '',
        'DanismanAdSoyad': danisman.upper() if danisman else '',
        'Universite': '0', 'Enstitu': '0', 'ABD': '0', 'BilimDali': '0',
        'uniad': universite.upper() if universite else '',
        'ensad': '', 'abdad': '', 'bilim': '',
        'Tur': tur or '0', 'Dil': '0', 'izin': '0', 'Durum': '3',
        'EnstituGrubu': '',
        'yil1': str(yil_baslangic) if yil_baslangic else '0',
        'yil2': str(yil_bitis) if yil_bitis else '0',
        'Dizin': '', 'Metin': metin, 'Konu': '', 'islem': '2', 'Bolum': '0',
    }
    try:
        resp = session.post(SEARCH_URL, data=form_data, timeout=30, allow_redirects=True)
        resp.encoding = 'utf-8'
    except Exception as e:
        logger.error(f'YÖK Tez legacy POST hatası: {e}')
        return 0, []

    if 'tezSorguSonucHata' in resp.url or len(resp.text) < 500:
        logger.warning('YÖK Tez: eski form da çalışmıyor')
        return 0, []

    # Eski format: var doc = {...} bloklarını parse et
    doc_blocks = re.findall(r'var\s+doc\s*=\s*\{(.*?)\};', resp.text, re.DOTALL)
    if not doc_blocks:
        logger.warning('YÖK Tez legacy: var doc bloğu bulunamadı')
        return 0, []

    def exf(block, key):
        m = re.search(key + r'\s*:\s*"((?:[^"\\]|\\.)*)"', block)
        return m.group(1) if m else ''

    records = []
    for block in doc_blocks:
        title_html = exf(block, 'weight')
        parts = re.split(r'<br\s*/?>', title_html, maxsplit=1)
        title_en = re.sub(r'<[^>]+>', '', parts[0]).strip()
        title_tr = re.sub(r'<[^>]+>', '', parts[1]).strip() if len(parts) > 1 else ''

        user_id_html = exf(block, 'userId')
        tez_no_m = re.search(r'>(\d+)<', user_id_html)
        tez_no = tez_no_m.group(1) if tez_no_m else ''

        id_m = re.search(r'(?<![a-zA-Z])id\s*:\s*"((?:[^"\\]|\\.)*)"', block)
        no_m = re.search(r'(?<![a-zA-Z])no\s*:\s*"((?:[^"\\]|\\.)*)"', block)
        detail_id = id_m.group(1) if id_m else ''
        detail_no = no_m.group(1) if no_m else ''

        if not detail_id:
            unesc = user_id_html.replace("\\'", "'").replace('\\"', '"')
            dm = re.search(r"""tezDetay\(['"]([\w\-+/=]+)['"]\s*,\s*['"]([\w\-+/=]+)['"]\)""", unesc)
            detail_id = dm.group(1) if dm else ''
            detail_no = dm.group(2) if dm else ''

        records.append({
            'tez_no': tez_no,
            'kayit_no': detail_id,   # legacy uyumluluk
            'title': title_en,
            'title_tr': title_tr,
            'author': exf(block, 'name').strip(),
            'year': exf(block, 'age').strip(),
            'university': exf(block, 'uni').strip(),
            'thesis_type': exf(block, 'important').strip(),
            'language': exf(block, 'height').strip(),
        })

    total = len(records)
    filtered = [r for r in records
                if _year_ok(r, yil_baslangic, yil_bitis)
                and _uni_ok(r, universite)
                and _type_ok(r, tur)]
    demo = (filtered or records)[:demo_limit]

    # Legacy detay (tezDetay.jsp HTML)
    legacy_detail_url = f'{BASE_URL}/tezDetay.jsp'
    for idx, rec in enumerate(demo):
        if rec.get('kayit_no') and rec.get('tez_no'):
            if idx > 0:
                _human_delay(*_DELAY_BETWEEN_DETAILS)
            try:
                dr = session.get(
                    legacy_detail_url,
                    params={'id': rec['kayit_no'], 'no': rec['tez_no']},
                    timeout=15,
                )
                dr.encoding = 'utf-8'
                detail = _parse_detail_html(dr.text)
                rec.update(detail)
            except Exception as e:
                logger.warning(f'YÖK Tez legacy detay hatası: {e}')

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
        lines.append(f'{i}. {r.get("title_tr") or r.get("title") or "(Başlık yok)"}')
        if r.get('title') and r.get('title_tr'):
            lines.append(f'   EN: {r["title"]}')
        lines.append(f'   Yazar: {r.get("author", "-")}')
        lines.append(f'   Yıl: {r.get("year", "-")} | Tür: {r.get("thesis_type", "-")} | Dil: {r.get("language", "-")}')
        lines.append(f'   Üniversite: {r.get("university", "-")}')
        lines.append(f'   Tez No: {r.get("tez_no", "-")}')
        if r.get('danisman'):
            lines.append(f'   Danışman: {r["danisman"]}')
        if r.get('abstract_tr'):
            lines.append(f'   Özet: {r["abstract_tr"][:500]}')
        if r.get('abstract_en'):
            lines.append(f'   Abstract: {r["abstract_en"][:500]}')
        lines.append('')
    return '\n'.join(lines)
