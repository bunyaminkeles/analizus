"""
YÖK Tez tam veri çekici.
Mevcut yoktez scraper fonksiyonlarını import ederek tüm sayfalardaki kayıtları alır,
her kayıt için detay (özet, konu, dizin) çeker.
"""
import time
import logging
import re

logger = logging.getLogger(__name__)

MAX_RECORDS = 300
PAGE_DELAY = 3.0   # saniye — sayfa istekleri arası
DETAIL_DELAY = 1.5  # saniye — detay istekleri arası


def fetch_all(
    tez_ad='', yazar='', universite='', tur='0',
    yil_baslangic=None, yil_bitis=None, metin='',
    max_records=MAX_RECORDS,
    page_delay=PAGE_DELAY,
    detail_delay=DETAIL_DELAY,
) -> list[dict]:
    """
    YÖK Tez'den tüm sayfalardaki temel kayıtları çeker,
    ardından her kayıt için detay (özet, konu, dizin) alır.
    Toplam max_records kayıtla sınırlıdır.

    Returns: List[dict] — tam doldurulmuş kayıtlar
    """
    from yoktez.services.scraper import (
        _make_session, _build_form, _parse_results, _fetch_detail,
        SEARCH_URL, INIT_URL,
    )

    session = _make_session()

    # Session başlat
    try:
        session.get(INIT_URL, timeout=15)
    except Exception as e:
        logger.warning(f'[tezanaliz fetcher] Session init hatası (devam): {e}')

    form_data = _build_form(
        tez_ad=tez_ad,
        yazar=yazar,
        universite=universite,
        tur=tur or '0',
        yil1=yil_baslangic,
        yil2=yil_bitis,
        metin=metin,
    )

    # --- Sayfa 1 ---
    all_basic = []
    total_count = 0

    try:
        response = session.post(SEARCH_URL, data=form_data, timeout=30, allow_redirects=False)
        if response.status_code in (301, 302, 303, 307, 308):
            redirect_url = response.headers.get('location', '')
            if redirect_url.startswith('http://'):
                redirect_url = redirect_url.replace('http://', 'https://', 1)
            if redirect_url:
                response = session.get(redirect_url, timeout=30)
        response.encoding = 'utf-8'
        total_count, page_records = _parse_results(response.text)
        all_basic.extend(page_records)
        logger.info(f'[tezanaliz fetcher] Sayfa 1: {len(page_records)} kayıt, toplam={total_count}')

        # --- Ek sayfalar ---
        # YÖK Tez HTML'inde sayfalama linkleri arar
        next_page_urls = _find_next_pages(response.text, total_count, len(page_records))
        for page_url in next_page_urls:
            if len(all_basic) >= max_records:
                break
            time.sleep(page_delay)
            try:
                pg_resp = session.get(page_url, timeout=30)
                pg_resp.encoding = 'utf-8'
                _, pg_records = _parse_results(pg_resp.text)
                if not pg_records:
                    break
                all_basic.extend(pg_records)
                logger.info(f'[tezanaliz fetcher] Ek sayfa: {len(pg_records)} kayıt (toplam şimdiye kadar: {len(all_basic)})')
            except Exception as e:
                logger.warning(f'[tezanaliz fetcher] Ek sayfa hatası: {e}')
                break

    except Exception as e:
        logger.error(f'[tezanaliz fetcher] İlk arama hatası: {e}', exc_info=True)
        return []

    # Limitle
    all_basic = all_basic[:max_records]

    if not all_basic:
        logger.warning('[tezanaliz fetcher] Hiç kayıt bulunamadı.')
        return []

    # --- Detay çekimi (özet, konu, dizin) ---
    results = []
    for i, rec in enumerate(all_basic):
        detail = _fetch_detail(session, rec.get('detail_id', ''), rec.get('detail_no', ''))
        rec.update(detail)
        results.append(rec)
        if i < len(all_basic) - 1:
            time.sleep(detail_delay)
        if (i + 1) % 20 == 0:
            logger.info(f'[tezanaliz fetcher] Detay: {i+1}/{len(all_basic)} tamamlandı')

    logger.info(f'[tezanaliz fetcher] Toplam {len(results)} kayıt hazır.')
    return results


def _find_next_pages(html: str, total_count: int, first_page_count: int) -> list[str]:
    """
    YÖK Tez HTML'inden ek sayfa URL'lerini çıkar.
    İlk sayfada tüm sonuçlar geliyorsa boş liste döner.
    """
    from yoktez.services.scraper import BASE_URL

    if not first_page_count or total_count <= first_page_count:
        return []

    # Sayfalama linklerini ara — YÖK Tez genellikle `?pg=2` veya `/SearchTez?...&pg=2` kullanır
    page_links = re.findall(
        r'href=["\']([^"\']*(?:pg|page|sayfa)=(\d+)[^"\']*)["\']',
        html,
        re.IGNORECASE,
    )

    urls = []
    seen_pages = {1}
    for href, pg_num in page_links:
        pg = int(pg_num)
        if pg in seen_pages:
            continue
        seen_pages.add(pg)
        if href.startswith('http'):
            urls.append(href)
        elif href.startswith('/'):
            urls.append(BASE_URL.rstrip('/') + href)
        else:
            urls.append(BASE_URL + '/' + href)

    # Sayfalama linki bulunamazsa, sayfa sayısını tahmin et ve form-based pagination dene
    if not urls and total_count > first_page_count:
        logger.info(
            f'[tezanaliz fetcher] HTML\'de sayfalama linki bulunamadı '
            f'(total={total_count}, first_page={first_page_count}). '
            f'İlk sayfadaki tüm kayıtlar kullanılacak.'
        )

    return urls
