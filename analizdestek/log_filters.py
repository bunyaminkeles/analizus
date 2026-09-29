"""Logging filtreleri — hata e-postası (mail_admins) seli önleme."""
import logging
import threading
import time


class ThrottleAdminEmails(logging.Filter):
    """Aynı hata için pencere başına tek e-posta + saatlik üst sınır.

    Sayaç süreç belleğinde (DB/cache'e bağlı değil — hatanın kaynağı DB olabilir); her gunicorn
    worker'ı ayrı sayar. Amaç: kırık bir sayfa botlarca çağrılınca SMTP hesabının kilitlenmemesi.
    """

    def __init__(self, window=900, hourly_limit=20):
        super().__init__()
        self.window = window
        self.hourly_limit = hourly_limit
        self._last_sent = {}
        self._sent_times = []
        self._lock = threading.Lock()

    def _key(self, record):
        exc_type = record.exc_info[0].__name__ if record.exc_info and record.exc_info[0] else ''
        return (exc_type, record.getMessage()[:200])

    def filter(self, record):
        now = time.monotonic()
        key = self._key(record)
        with self._lock:
            self._sent_times = [t for t in self._sent_times if now - t < 3600]
            if len(self._sent_times) >= self.hourly_limit:
                return False
            if now - self._last_sent.get(key, -self.window) < self.window:
                return False
            self._last_sent[key] = now
            self._sent_times.append(now)
            if len(self._last_sent) > 500:
                self._last_sent = {k: v for k, v in self._last_sent.items() if now - v < self.window}
        return True
