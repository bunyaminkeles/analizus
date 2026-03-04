from django.apps import AppConfig


class TezAnalizConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tezanaliz'
    verbose_name = 'Analiz Servisleri'

    def ready(self):
        # Global analiz worker'ını başlat (idempotent)
        try:
            from analizdestek.job_queue import start_worker
            start_worker()
        except Exception:
            pass
