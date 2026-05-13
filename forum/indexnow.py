import threading
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

INDEXNOW_KEY = '534e22a9f9e4d375119c5bc6d006aad0'
INDEXNOW_ENDPOINT = 'https://api.indexnow.org/indexnow'
SITE_URL = 'https://www.analizus.com'


def _ping(urls: list[str]):
    if not urls:
        return
    payload = {
        'host': 'www.analizus.com',
        'key': INDEXNOW_KEY,
        'keyLocation': f'{SITE_URL}/{INDEXNOW_KEY}.txt',
        'urlList': urls[:10000],
    }
    try:
        r = requests.post(INDEXNOW_ENDPOINT, json=payload, timeout=10)
        if r.status_code in (200, 202):
            logger.info('IndexNow ping OK: %s URL(s)', len(urls))
        else:
            logger.warning('IndexNow ping %s: %s', r.status_code, r.text[:200])
    except Exception as exc:
        logger.warning('IndexNow ping failed: %s', exc)


def ping(urls: list[str]):
    """Verilen URL'leri arka planda IndexNow'a bildir."""
    threading.Thread(target=_ping, args=(urls,), daemon=True).start()


def ping_url(url: str):
    ping([url])
