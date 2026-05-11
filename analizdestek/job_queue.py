"""
Global analiz iş kuyruğu.
Aynı anda MAX_WORKERS kadar analiz paralel çalışır; fazlası sırayla beklenir.

Mimari: in-memory queue.Queue + dispatcher thread + ThreadPoolExecutor.
Tek process (Daphne ASGI / gunicorn -w 1) için tasarlanmıştır.
"""
import threading
import queue
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from django.conf import settings

logger = logging.getLogger(__name__)

# Hetzner kapasitesine göre ayarla — settings.py'de JOB_MAX_WORKERS ile override edilebilir
MAX_WORKERS = getattr(settings, 'JOB_MAX_WORKERS', 5)

STUCK_THRESHOLD_MINUTES = 30  # bu süreyi aşan running joblar stuck sayılır

_job_queue = queue.Queue()
_worker_lock = threading.Lock()
_worker_started = False
_executor: ThreadPoolExecutor | None = None


def _recover():
    """
    Sunucu yeniden başlatma sonrası kurtarma:
    - 'running' durumundaki işleri 'pending'e döndür (crash recovery)
    - 'pending' işleri kuyruğa ekle (created_at sırasına göre)
    """
    try:
        from tezanaliz.models import TezAnaliz
        from makaleanaliz.models import MakaleAnaliz
        from yoktez.models import YokTezSearchJob
        from openalex.models import AlexSearchJob
        from trdizin.models import DizinSearchJob
        from bibliometrics.models import BibliometricJob
        from istatistik.models import IstatistikJob

        from django.utils import timezone
        stuck_cutoff = timezone.now() - timedelta(minutes=STUCK_THRESHOLD_MINUTES)

        simple_models = [
            (TezAnaliz, 'tezanaliz'),
            (MakaleAnaliz, 'makaleanaliz'),
            (YokTezSearchJob, 'yoktez'),
            (AlexSearchJob, 'openalex'),
            (DizinSearchJob, 'trdizin'),
        ]

        for Model, job_type in simple_models:
            for job in Model.objects.filter(status='running'):
                # Uzun süredir running olan joblar stuck — failed yap
                if job.updated_at < stuck_cutoff if hasattr(job, 'updated_at') else job.created_at < stuck_cutoff:
                    job.status = 'failed'
                    job.error_message = 'Sunucu yeniden başlatıldı, iş tamamlanamadı (30+ dk).'
                    job.save(update_fields=['status', 'error_message'])
                    logger.warning(f'[job_queue] Recovery: {job_type}/{job.id} stuck→failed')
                else:
                    job.status = 'pending'
                    job.save(update_fields=['status'])
                    logger.info(f'[job_queue] Recovery: {job_type}/{job.id} running→pending')
            for job in Model.objects.filter(status='pending').order_by('created_at'):
                _job_queue.put((job_type, str(job.id)))
                logger.info(f'[job_queue] Recovery: {job_type}/{job.id} kuyruğa eklendi')

        # İstatistik araçları — dosya içeriği bellekte tutulduğundan restart sonrası kurtarılamaz
        for job in IstatistikJob.objects.filter(status__in=['running', 'pending']):
            job.status = 'failed'
            job.error_message = 'Sunucu yeniden başlatıldı, lütfen dosyayı tekrar yükleyin.'
            job.save(update_fields=['status', 'error_message'])
            logger.info(f'[job_queue] Recovery: istatistik/{job.id} failed (dosya yok)')

        # Bibliometrics upload — dosya içeriği bellekte tutulduğundan restart sonrası kurtarılamaz
        for job in BibliometricJob.objects.filter(status__in=['running', 'pending'], source='upload'):
            job.status = 'failed'
            job.error_message = 'Sunucu yeniden başlatıldı, lütfen dosyayı tekrar yükleyin.'
            job.save(update_fields=['status', 'error_message'])
            logger.info(f'[job_queue] Recovery: bibliometrics/{job.id} failed (upload, dosya yok)')

        # Bibliometrics openalex — DB'den okunabilir, kurtarılabilir
        for job in BibliometricJob.objects.filter(status='running', source='openalex'):
            job.status = 'pending'
            job.save(update_fields=['status'])
            logger.info(f'[job_queue] Recovery: bibliometrics_openalex/{job.id} running→pending')
        for job in BibliometricJob.objects.filter(status='pending', source='openalex').order_by('created_at'):
            _job_queue.put(('bibliometrics_openalex', str(job.id)))
            logger.info(f'[job_queue] Recovery: bibliometrics_openalex/{job.id} kuyruğa eklendi')

    except Exception as e:
        logger.warning(f'[job_queue] Recovery atlandı (normal ilk çalıştırmada): {e}')


def _run_job(job_type: str, job_id: str):
    """Tek bir işi çalıştırır — ThreadPoolExecutor worker thread'inde koşar."""
    try:
        logger.info(f'[job_queue] Başlıyor: {job_type}/{job_id}')
        if job_type == 'tezanaliz':
            from tezanaliz.services.job_runner import _execute_job
            _execute_job(job_id)
        elif job_type == 'makaleanaliz':
            from makaleanaliz.services.job_runner import _execute_job
            _execute_job(job_id)
        elif job_type == 'yoktez':
            from yoktez.services.job_runner import _execute_job
            _execute_job(job_id)
        elif job_type == 'openalex':
            from openalex.services.job_runner import _execute_job
            _execute_job(job_id)
        elif job_type == 'trdizin':
            from trdizin.services.job_runner import _execute_job
            _execute_job(job_id)
        elif job_type == 'bibliometrics':
            from bibliometrics.services.job_runner import _execute_job
            _execute_job(job_id)
        elif job_type == 'bibliometrics_openalex':
            from bibliometrics.services.job_runner import _execute_job_openalex
            _execute_job_openalex(job_id)
        elif job_type in ('cronbach', 'normallik', 'betimsel', 'korelasyon', 'ttesti', 'anova', 'mann_whitney', 'kruskal_wallis', 'ki_kare'):
            from istatistik.services.job_runner import _execute_job
            _execute_job(job_id)
        else:
            logger.warning(f'[job_queue] Bilinmeyen job_type: {job_type}')
    except Exception as e:
        logger.error(f'[job_queue] {job_type}/{job_id} hatası: {e}', exc_info=True)


def _dispatcher():
    """
    Dispatcher thread — kuyruktaki işleri ThreadPoolExecutor'a dağıtır.
    MAX_WORKERS iş aynı anda çalışabilir; pool dolarsa executor kendi iç kuyruğunda bekletir.
    """
    _recover()
    logger.info(f'[job_queue] Dispatcher başladı, max {MAX_WORKERS} paralel iş destekleniyor.')
    while True:
        job_type, job_id = _job_queue.get()
        try:
            _executor.submit(_run_job, job_type, job_id)
            logger.info(f'[job_queue] Pool\'a gönderildi: {job_type}/{job_id} (kuyruk≈{_job_queue.qsize()})')
        except Exception as e:
            logger.error(f'[job_queue] Dispatcher submit hatası: {e}', exc_info=True)
        finally:
            _job_queue.task_done()


def start_worker():
    """Dispatcher thread ve worker pool'u başlat (idempotent — bir kez başlar)."""
    global _worker_started, _executor
    with _worker_lock:
        if not _worker_started:
            _executor = ThreadPoolExecutor(
                max_workers=MAX_WORKERS,
                thread_name_prefix='job-worker',
            )
            t = threading.Thread(target=_dispatcher, daemon=True, name='job-dispatcher')
            t.start()
            _worker_started = True
            logger.info(f'[job_queue] Dispatcher ve {MAX_WORKERS} worker başlatıldı.')


def enqueue(job_type: str, job_id: str):
    """Bir analiz işini kuyruğa ekler ve worker'ı başlatır."""
    start_worker()
    _job_queue.put((job_type, job_id))
    logger.info(f'[job_queue] Kuyruğa eklendi: {job_type}/{job_id} (kuyruk≈{_job_queue.qsize()})')


def get_queue_position(job_type: str, job_id: str) -> int:
    """
    İşin kuyruk pozisyonunu döndürür.
    0  → çalışıyor veya tamamlandı/başarısız
    1  → sıradaki (bir worker boşalınca hemen çalışacak)
    2+ → bekliyor
    -1 → hesaplanamadı

    Not: MAX_WORKERS iş eş zamanlı çalışabilir. Önünde MAX_WORKERS'tan az running
    iş varsa pozisyon 1 döner (hemen başlayabilir demektir).
    """
    try:
        from tezanaliz.models import TezAnaliz
        from makaleanaliz.models import MakaleAnaliz
        from yoktez.models import YokTezSearchJob
        from openalex.models import AlexSearchJob
        from trdizin.models import DizinSearchJob
        from bibliometrics.models import BibliometricJob
        from istatistik.models import IstatistikJob

        model_map = {
            'tezanaliz': TezAnaliz,
            'makaleanaliz': MakaleAnaliz,
            'yoktez': YokTezSearchJob,
            'openalex': AlexSearchJob,
            'trdizin': DizinSearchJob,
            'bibliometrics': BibliometricJob,
            'bibliometrics_openalex': BibliometricJob,
            'cronbach': IstatistikJob,
            'normallik': IstatistikJob,
            'betimsel': IstatistikJob,
            'korelasyon': IstatistikJob,
            'ttesti': IstatistikJob,
            'anova': IstatistikJob,
            'mann_whitney': IstatistikJob,
            'kruskal_wallis': IstatistikJob,
            'ki_kare': IstatistikJob,
        }
        Model = model_map.get(job_type)
        if not Model:
            return -1

        job = Model.objects.filter(id=job_id, status='pending').first()
        if not job:
            return 0  # zaten çalışıyor ya da bitti

        created_at = job.created_at

        pending_before = (
            TezAnaliz.objects.filter(status='pending', created_at__lt=created_at).count() +
            MakaleAnaliz.objects.filter(status='pending', created_at__lt=created_at).count() +
            YokTezSearchJob.objects.filter(status='pending', created_at__lt=created_at).count() +
            AlexSearchJob.objects.filter(status='pending', created_at__lt=created_at).count() +
            DizinSearchJob.objects.filter(status='pending', created_at__lt=created_at).count() +
            BibliometricJob.objects.filter(status='pending', created_at__lt=created_at).count() +
            IstatistikJob.objects.filter(status='pending', created_at__lt=created_at).count()
        )
        running_count = (
            TezAnaliz.objects.filter(status='running').count() +
            MakaleAnaliz.objects.filter(status='running').count() +
            YokTezSearchJob.objects.filter(status='running').count() +
            AlexSearchJob.objects.filter(status='running').count() +
            DizinSearchJob.objects.filter(status='running').count() +
            BibliometricJob.objects.filter(status='running').count() +
            IstatistikJob.objects.filter(status='running').count()
        )

        # Boş worker slotu var mı?
        free_slots = MAX_WORKERS - running_count
        if free_slots > 0 and pending_before < free_slots:
            return 1  # hemen başlayabilir

        return pending_before + 1

    except Exception:
        return -1
