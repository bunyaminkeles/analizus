import feedparser
from django.core.cache import cache
from datetime import datetime
import time

CACHE_KEY = 'science_news_feed'
CACHE_TTL = 60 * 30  # 30 dakika

TOPICS = ['akademik', 'bilim', 'üniversite', 'araştırma', 'astronomi', 'tıp']
RSS_URL = (
    'https://news.google.com/rss/search'
    '?q=akademik+OR+bilim+OR+üniversite+OR+araştırma+OR+astronomi+OR+tıp'
    '&hl=tr&gl=TR&ceid=TR:tr'
)


def get_science_news(count=9):
    cached = cache.get(CACHE_KEY)
    if cached is not None:
        return cached

    try:
        feed = feedparser.parse(RSS_URL)
        news = []
        for entry in feed.entries[:count]:
            # Yayın tarihi
            published = ''
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                dt = datetime(*entry.published_parsed[:6])
                published = dt.strftime('%d.%m.%Y')

            # Kaynak (Google News başlıklara " - Kaynak" ekler)
            title = entry.title
            source = ''
            if ' - ' in title:
                parts = title.rsplit(' - ', 1)
                title = parts[0].strip()
                source = parts[1].strip()

            news.append({
                'title': title,
                'url': entry.link,
                'source': source,
                'published': published,
            })

        cache.set(CACHE_KEY, news, CACHE_TTL)
        return news
    except Exception:
        return []
