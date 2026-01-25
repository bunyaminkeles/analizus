"""
Twitter/X API Entegrasyonu
Otomatik içerik paylaşımı için servis modülü
"""
import logging
from django.conf import settings
from typing import Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TweetResult:
    """Tweet sonucu"""
    success: bool
    tweet_id: Optional[str] = None
    tweet_url: Optional[str] = None
    error: Optional[str] = None


class TwitterService:
    """Twitter/X API v2 servisi"""

    def __init__(self):
        self.client = None
        self.enabled = getattr(settings, 'TWITTER_ENABLED', False)
        self._initialize_client()

    def _initialize_client(self):
        """Twitter API istemcisini başlat"""
        if not self.enabled:
            logger.info("Twitter entegrasyonu devre dışı")
            return

        try:
            import tweepy

            # API anahtarlarını al
            api_key = getattr(settings, 'TWITTER_API_KEY', None)
            api_secret = getattr(settings, 'TWITTER_API_SECRET', None)
            access_token = getattr(settings, 'TWITTER_ACCESS_TOKEN', None)
            access_secret = getattr(settings, 'TWITTER_ACCESS_TOKEN_SECRET', None)
            bearer_token = getattr(settings, 'TWITTER_BEARER_TOKEN', None)

            if not all([api_key, api_secret, access_token, access_secret]):
                logger.warning("Twitter API anahtarları eksik!")
                self.enabled = False
                return

            # Twitter API v2 Client
            self.client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_secret,
                wait_on_rate_limit=True  # Rate limit aşımında otomatik bekle
            )

            # Bağlantıyı test et
            me = self.client.get_me()
            if me.data:
                logger.info(f"Twitter bağlantısı başarılı: @{me.data.username}")

        except ImportError:
            logger.error("tweepy kütüphanesi yüklü değil: pip install tweepy")
            self.enabled = False
        except Exception as e:
            logger.error(f"Twitter bağlantı hatası: {e}")
            self.enabled = False

    def is_available(self) -> bool:
        """Servis kullanılabilir mi?"""
        return self.enabled and self.client is not None

    def post_tweet(self, text: str, reply_to: Optional[str] = None) -> TweetResult:
        """
        Tweet gönder

        Args:
            text: Tweet metni (max 280 karakter)
            reply_to: Yanıtlanacak tweet ID'si (opsiyonel)

        Returns:
            TweetResult
        """
        if not self.is_available():
            return TweetResult(success=False, error="Twitter servisi kullanılamıyor")

        # Karakter limiti kontrolü
        if len(text) > 280:
            text = text[:277] + "..."

        try:
            response = self.client.create_tweet(
                text=text,
                in_reply_to_tweet_id=reply_to
            )

            tweet_id = response.data['id']
            # Kullanıcı adını al
            me = self.client.get_me()
            username = me.data.username if me.data else "user"
            tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"

            logger.info(f"Tweet gönderildi: {tweet_url}")
            return TweetResult(success=True, tweet_id=tweet_id, tweet_url=tweet_url)

        except Exception as e:
            logger.error(f"Tweet gönderme hatası: {e}")
            return TweetResult(success=False, error=str(e))

    def post_thread(self, tweets: List[str]) -> List[TweetResult]:
        """
        Twitter thread (dizi) gönder

        Args:
            tweets: Tweet metinleri listesi

        Returns:
            TweetResult listesi
        """
        if not self.is_available():
            return [TweetResult(success=False, error="Twitter servisi kullanılamıyor")]

        results = []
        previous_tweet_id = None

        for i, text in enumerate(tweets):
            # Thread numarası ekle
            if len(tweets) > 1:
                thread_indicator = f"[{i+1}/{len(tweets)}] "
                max_text_len = 280 - len(thread_indicator)
                if len(text) > max_text_len:
                    text = text[:max_text_len-3] + "..."
                text = thread_indicator + text

            result = self.post_tweet(text, reply_to=previous_tweet_id)
            results.append(result)

            if result.success:
                previous_tweet_id = result.tweet_id
            else:
                # Hata durumunda thread'i durdur
                break

        return results


# ═══════════════════════════════════════════════════════════════════════
# İÇERİK FORMATLAMA FONKSİYONLARI
# ═══════════════════════════════════════════════════════════════════════

def format_topic_tweet(topic, site_url: str = "https://analizus.com") -> str:
    """
    Yeni konu için tweet metni oluştur

    Args:
        topic: Topic model instance
        site_url: Site URL'si
    """
    # Kategori hashtag'i
    category_hashtags = {
        'spss': '#SPSS',
        'python': '#Python #DataScience',
        'r': '#RStats #RStudio',
        'excel': '#Excel',
        'istatistik': '#İstatistik #Statistics',
        'regresyon': '#Regression #MachineLearning',
        'anova': '#ANOVA #Statistics',
    }

    category_slug = topic.category.slug if topic.category else ''
    hashtag = category_hashtags.get(category_slug, '#VeriAnalizi')

    # URL
    topic_url = f"{site_url}{topic.get_absolute_url()}"

    # Tweet metnini oluştur
    subject = topic.subject
    max_subject_len = 180  # URL ve hashtag'ler için yer bırak
    if len(subject) > max_subject_len:
        subject = subject[:max_subject_len-3] + "..."

    tweet = f"🆕 Yeni Soru: {subject}\n\n{hashtag} #VeriAnalizi\n\n🔗 {topic_url}"

    return tweet


def format_daily_tip_tweet(tip, site_url: str = "https://analizus.com") -> str:
    """
    Günlük ipucu için tweet metni oluştur
    """
    category_emojis = {
        'spss': '📊',
        'python': '🐍',
        'r': '📈',
        'excel': '📗',
        'statistics': '📉',
        'methodology': '🔬',
        'academic': '📚',
    }

    emoji = category_emojis.get(tip.category, '💡')

    # İçeriği kısalt
    content = tip.content
    max_len = 200
    if len(content) > max_len:
        content = content[:max_len-3] + "..."

    tweet = f"{emoji} Günün İpucu: {tip.title}\n\n{content}\n\n#VeriAnalizi #{tip.get_category_display()}"

    return tweet


def format_job_tweet(job, site_url: str = "https://analizus.com") -> str:
    """
    İş ilanı için tweet metni oluştur
    """
    budget = f"💰 {job.budget_min:.0f}-{job.budget_max:.0f} TL"

    title = job.title
    if len(title) > 100:
        title = title[:97] + "..."

    job_url = f"{site_url}/jobs/{job.id}/"

    tweet = f"💼 Yeni İş İlanı: {title}\n\n{budget}\n\n#Freelance #VeriAnalizi #İşİlanı\n\n🔗 {job_url}"

    return tweet


# ═══════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCE
# ═══════════════════════════════════════════════════════════════════════

_twitter_service = None

def get_twitter_service() -> TwitterService:
    """Twitter servis singleton'ını döndür"""
    global _twitter_service
    if _twitter_service is None:
        _twitter_service = TwitterService()
    return _twitter_service


def post_to_twitter(text: str) -> TweetResult:
    """Kısa yol: Tweet gönder"""
    service = get_twitter_service()
    return service.post_tweet(text)
