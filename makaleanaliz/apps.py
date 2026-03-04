from django.apps import AppConfig


class MakaleAnalizConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'makaleanaliz'
    verbose_name = 'Makale Analizi'

    def ready(self):
        # Global analiz worker'ını başlat (idempotent)
        try:
            from analizdestek.job_queue import start_worker
            start_worker()
        except Exception:
            pass
