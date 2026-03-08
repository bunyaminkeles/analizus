"""
Global analiz iş kuyruğu.
Aynı anda yalnızca 1 analiz çalışır; diğerleri sırayla beklenir.

Mimari: in-memory queue.Queue + tek daemon worker thread.
Tek process (Daphne ASGI / gunicorn -w 1) için yeterlidir.
"""
import threading
import queue
import logging

logger = logging.getLogger(__name__)

_job_queue = queue.Queue()
_worker_lock = threading.Lock()
_worker_started = False


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

        simple_models = [
            (TezAnaliz, 'tezanaliz'),
            (MakaleAnaliz, 'makaleanaliz'),
            (YokTezSearchJob, 'yoktez'),
            (AlexSearchJob, 'openalex'),
            (DizinSearchJob, 'trdizin'),
        ]

        for Model, job_type in simple_models:
            for job in Model.objects.filter(status='running'):
                job.status = 'pending'
                job.save(update_fields=['status'])
                logger.info(f'[job_queue] Recovery: {job_type}/{job.id} running→pending')
            for job in Model.objects.filter(status='pending').order_by('created_at'):
                _job_queue.put((job_type, str(job.id)))
                logger.info(f'[job_queue] Recovery: {job_type}/{job.id} kuyruğa eklendi')

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


def _worker():
    """Tek worker thread — işleri sırayla çalıştırır."""
    _recover()
    logger.info('[job_queue] Worker başladı, kuyruk dinleniyor...')
    while True:
        job_type, job_id = _job_queue.get()
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
            else:
                logger.warning(f'[job_queue] Bilinmeyen job_type: {job_type}')
        except Exception as e:
            logger.error(f'[job_queue] {job_type}/{job_id} hatası: {e}', exc_info=True)
        finally:
            _job_queue.task_done()


def start_worker():
    """Worker thread'i başlat (idempotent — bir kez başlar)."""
    global _worker_started
    with _worker_lock:
        if not _worker_started:
            t = threading.Thread(target=_worker, daemon=True, name='analysis-worker')
            t.start()
            _worker_started = True
            logger.info('[job_queue] Worker thread başlatıldı.')


def enqueue(job_type: str, job_id: str):
    """Bir analiz işini kuyruğa ekler ve worker'ı başlatır."""
    start_worker()
    _job_queue.put((job_type, job_id))
    logger.info(f'[job_queue] Kuyruğa eklendi: {job_type}/{job_id} (kuyruk≈{_job_queue.qsize()})')


def get_queue_position(job_type: str, job_id: str) -> int:
    """
    İşin kuyruk pozisyonunu döndürür.
    0  → çalışıyor veya tamamlandı/başarısız
    1  → sıradaki (running bittikten hemen çalışacak)
    2+ → bekliyor
    -1 → hesaplanamadı
    """
    try:
        from tezanaliz.models import TezAnaliz
        from makaleanaliz.models import MakaleAnaliz
        from yoktez.models import YokTezSearchJob
        from openalex.models import AlexSearchJob
        from trdizin.models import DizinSearchJob
        from bibliometrics.models import BibliometricJob

        model_map = {
            'tezanaliz': TezAnaliz,
            'makaleanaliz': MakaleAnaliz,
            'yoktez': YokTezSearchJob,
            'openalex': AlexSearchJob,
            'trdizin': DizinSearchJob,
            'bibliometrics': BibliometricJob,
            'bibliometrics_openalex': BibliometricJob,
        }
        Model = model_map.get(job_type)
        if not Model:
            return -1

        job = Model.objects.filter(id=job_id, status='pending').first()
        if not job:
            return 0

        created_at = job.created_at

        before = (
            TezAnaliz.objects.filter(status='pending', created_at__lt=created_at).count() +
            MakaleAnaliz.objects.filter(status='pending', created_at__lt=created_at).count() +
            YokTezSearchJob.objects.filter(status='pending', created_at__lt=created_at).count() +
            AlexSearchJob.objects.filter(status='pending', created_at__lt=created_at).count() +
            DizinSearchJob.objects.filter(status='pending', created_at__lt=created_at).count() +
            BibliometricJob.objects.filter(status='pending', created_at__lt=created_at).count()
        )
        running = (
            TezAnaliz.objects.filter(status='running').count() +
            MakaleAnaliz.objects.filter(status='running').count() +
            YokTezSearchJob.objects.filter(status='running').count() +
            AlexSearchJob.objects.filter(status='running').count() +
            DizinSearchJob.objects.filter(status='running').count() +
            BibliometricJob.objects.filter(status='running').count()
        )
        return before + running + 1

    except Exception:
        return -1
