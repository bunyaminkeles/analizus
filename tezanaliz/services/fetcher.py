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
PAGE_DELAY = 2.0    # saniye — sayfa istekleri arası
DETAIL_DELAY = 1.0  # saniye — detay istekleri arası
JOB_TIMEOUT = 12 * 60  # saniye — toplam iş zaman aşımı (12 dk)


def fetch_all(
    tez_ad='', yazar='', universite='', tur='0',
    yil_baslangic=None, yil_bitis=None, metin='',
    max_records=MAX_RECORDS,
    page_delay=PAGE_DELAY,
    detail_delay=DETAIL_DELAY,
    job_timeout=JOB_TIMEOUT,
) -> list[dict]:
    """
    YÖK Tez'den tüm sayfalardaki temel kayıtları çeker,
    ardından her kayıt için detay (özet, konu, dizin) alır.
    Toplam max_records kayıtla sınırlıdır.

    Returns: List[dict] — tam doldurulmuş kayıtlar
    """
    from yoktez.services.scraper import (
        _make_session, _build_form, _determine_query, _parse_results, _fetch_detail,
        SEARCH_URL, INIT_URL,
    )

    session = _make_session()

    # Session başlat
    try:
        session.get(INIT_URL, timeout=15)
    except Exception as e:
        logger.warning(f'[tezanaliz fetcher] Session init hatası (devam): {e}')

    keyword, nevi = _determine_query(
        tez_ad=tez_ad,
        yazar=yazar,
        danisman='',
        metin=metin,
    )
    form_data = _build_form(keyword=keyword, nevi=nevi,
                            universite=universite, yil_baslangic=yil_baslangic,
                            yil_bitis=yil_bitis, tur=tur)

    # --- Sayfa 1 ---
    all_basic = []
    total_count = 0
    search_result_url = SEARCH_URL  # fallback pagination için

    try:
        response = session.post(SEARCH_URL, data=form_data, timeout=30, allow_redirects=False)
        if response.status_code in (301, 302, 303, 307, 308):
            redirect_url = response.headers.get('location', '')
            if redirect_url.startswith('http://'):
                redirect_url = redirect_url.replace('http://', 'https://', 1)
            if redirect_url and not redirect_url.startswith('http'):
                from urllib.parse import urljoin
                redirect_url = urljoin('https://tez.yok.gov.tr', redirect_url)
            if redirect_url:
                response = session.get(redirect_url, timeout=30)
                search_result_url = response.url  # final URL — ek sayfalar için kullanılacak
        response.encoding = 'utf-8'
        total_count, page_records = _parse_results(response.text)
        all_basic.extend(page_records)
        logger.info(f'[tezanaliz fetcher] Sayfa 1: {len(page_records)} kayıt, toplam={total_count}')

        # --- Ek sayfalar ---
        page_size = len(page_records)
        if page_size > 0 and total_count > page_size and len(all_basic) < max_records:
            next_page_urls = _find_next_pages(response.text, total_count, page_size)

            if next_page_urls:
                # HTML'de link bulundu — doğrudan kullan
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
                        logger.info(f'[tezanaliz fetcher] Ek sayfa (link): {len(pg_records)} kayıt '
                                    f'(toplam şimdiye kadar: {len(all_basic)})')
                    except Exception as e:
                        logger.warning(f'[tezanaliz fetcher] Ek sayfa hatası: {e}')
                        break
            else:
                # Fallback: ?pg=2, ?pg=3 ... ile dene
                sep = '&' if '?' in search_result_url else '?'
                page_num = 2
                consecutive_empty = 0
                while len(all_basic) < max_records:
                    page_url = f'{search_result_url}{sep}pg={page_num}'
                    time.sleep(page_delay)
                    try:
                        pg_resp = session.get(page_url, timeout=30)
                        pg_resp.encoding = 'utf-8'
                        _, pg_records = _parse_results(pg_resp.text)
                        if not pg_records:
                            consecutive_empty += 1
                            if consecutive_empty >= 2:
                                logger.info(f'[tezanaliz fetcher] Sayfa {page_num}: boş döndü, duruluyor.')
                                break
                        else:
                            consecutive_empty = 0
                            all_basic.extend(pg_records)
                            logger.info(f'[tezanaliz fetcher] Sayfa {page_num} (pg=): {len(pg_records)} kayıt '
                                        f'(toplam: {len(all_basic)})')
                        page_num += 1
                    except Exception as e:
                        logger.warning(f'[tezanaliz fetcher] Sayfa {page_num} hatası: {e}')
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
    import time as _time
    deadline = _time.monotonic() + job_timeout

    uni_filter = universite.strip().lower() if universite else ''

    results = []
    for i, rec in enumerate(all_basic):
        if _time.monotonic() > deadline:
            logger.warning(
                f'[tezanaliz fetcher] Zaman aşımı ({job_timeout}s). '
                f'{i}/{len(all_basic)} detay tamamlanmıştı, mevcut kayıtlarla devam ediliyor.'
            )
            break
        try:
            detail = _fetch_detail(session, rec.get('kayit_no', '') or rec.get('detail_id', ''), rec.get('tez_no', '') or rec.get('detail_no', ''))
        except Exception as e:
            logger.warning(f'[tezanaliz fetcher] Detay hatası kayıt {i}: {e}')
            detail = {}
        rec.update(detail)

        # Üniversite filtresi — detay çekildikten sonra uygulanır
        if uni_filter and uni_filter not in rec.get('university', '').lower():
            continue

        results.append(rec)
        if i < len(all_basic) - 1:
            time.sleep(detail_delay)
        if (i + 1) % 20 == 0:
            logger.info(f'[tezanaliz fetcher] Detay: {i+1}/{len(all_basic)} tamamlandı')

    logger.info(f'[tezanaliz fetcher] Toplam {len(results)} kayıt hazır (üniversite filtresi: {uni_filter or "yok"}).')
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

    if not urls and total_count > first_page_count:
        logger.info(
            f'[tezanaliz fetcher] HTML\'de sayfalama linki bulunamadı '
            f'(total={total_count}, first_page={first_page_count}). '
            f'Fallback pagination denenecek.'
        )

    return urls
