"""
İstatistik analiz araçları için job runner.
Her araç kendi _run_<tool>(job, df) fonksiyonunu çağırır.
Dosya içeriği in-memory dict'te tutulur (bibliometrics pattern'i ile aynı).
"""
import io
import logging

logger = logging.getLogger(__name__)

_pending_file_contents: dict[str, bytes] = {}


def store_file_content(job_id: str, content: bytes):
    _pending_file_contents[job_id] = content


def run_job(job_id: str):
    from analizdestek.job_queue import enqueue
    from istatistik.models import IstatistikJob
    job = IstatistikJob.objects.get(id=job_id)
    enqueue(job.tool, job_id)


def _execute_job(job_id: str):
    """Worker thread'inde çalışır."""
    from istatistik.models import IstatistikJob
    try:
        job = IstatistikJob.objects.get(id=job_id)
    except IstatistikJob.DoesNotExist:
        logger.error(f'[istatistik] Job bulunamadı: {job_id}')
        return

    content = _pending_file_contents.pop(job_id, None)
    if content is None:
        job.mark_failed('Dosya içeriği bulunamadı. Lütfen tekrar yükleyin.')
        return

    job.mark_running()

    try:
        df = _parse_file(content, job.original_filename)
        if job.tool == 'cronbach':
            from .cronbach import analyze, build_pdf
            columns = (job.options or {}).get('columns') or None
            result_data = analyze(df, columns=columns)
        elif job.tool == 'normallik':
            from .normallik import analyze, build_pdf
            columns = (job.options or {}).get('columns') or None
            result_data = analyze(df, columns=columns)
        elif job.tool == 'betimsel':
            from .betimsel import analyze, build_pdf
            result_data = analyze(df)
        elif job.tool == 'korelasyon':
            from .korelasyon import analyze, build_pdf
            method = (job.options or {}).get('method', 'pearson')
            result_data = analyze(df, method=method)
        elif job.tool == 'ttesti':
            from .ttesti import analyze, build_pdf
            opts = job.options or {}
            result_data = analyze(
                df,
                test_type=opts.get('test_type', 'independent'),
                group_col=opts.get('group_col'),
                dep_col=opts.get('dep_col'),
                col1=opts.get('col1'),
                col2=opts.get('col2'),
            )
        elif job.tool == 'anova':
            from .anova import analyze, build_pdf
            opts = job.options or {}
            result_data = analyze(
                df,
                group_col=opts.get('group_col'),
                dep_col=opts.get('dep_col'),
                posthoc=opts.get('posthoc', 'tukey'),
            )
        elif job.tool == 'mann_whitney':
            from .mann_whitney import analyze, build_pdf
            opts = job.options or {}
            result_data = analyze(
                df,
                group_col=opts.get('group_col'),
                dep_col=opts.get('dep_col'),
            )
        elif job.tool == 'kruskal_wallis':
            from .kruskal_wallis import analyze, build_pdf
            opts = job.options or {}
            result_data = analyze(
                df,
                group_col=opts.get('group_col'),
                dep_col=opts.get('dep_col'),
            )
        else:
            job.mark_failed(f'Bilinmeyen araç: {job.tool}')
            return

        pdf_bytes = build_pdf(result_data, job.original_filename, df)
        pdf_url = _upload_pdf(pdf_bytes, job)
        job.mark_completed(result_data=result_data, pdf_url=pdf_url)
        logger.info(f'[istatistik] Tamamlandı: {job.tool}/{job_id}')

        try:
            from forum.signals import on_istatistik_job_completed
            on_istatistik_job_completed(job)
        except Exception as e:
            logger.warning(f'[istatistik] Gamification güncellenemedi: {e}')

    except ValueError as e:
        job.mark_failed(str(e))
        logger.warning(f'[istatistik] Veri hatası {job.tool}/{job_id}: {e}')
    except Exception as e:
        job.mark_failed(f'Analiz sırasında hata oluştu: {e}')
        logger.error(f'[istatistik] Hata {job.tool}/{job_id}: {e}', exc_info=True)


def _parse_file(content: bytes, filename: str):
    import pandas as pd
    name_lower = filename.lower()
    if name_lower.endswith('.csv'):
        try:
            df = pd.read_csv(io.BytesIO(content))
        except Exception:
            df = pd.read_csv(io.BytesIO(content), encoding='latin-1')
    elif name_lower.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(io.BytesIO(content))
    else:
        raise ValueError('Desteklenmeyen dosya formatı. CSV veya Excel yükleyin.')

    if df.empty:
        raise ValueError('Dosya boş veya okunamadı.')
    if len(df) < 5:
        raise ValueError(f'En az 5 satır (katılımcı/gözlem) gereklidir, {len(df)} satır bulundu.')

    return df


def _upload_pdf(pdf_bytes: bytes, job) -> str:
    from forum.s3_utils import upload_bytes_to_s3
    s3_key = f'istatistik/{job.tool}/{job.id}.pdf'
    url = upload_bytes_to_s3(pdf_bytes, s3_key, 'application/pdf')
    return url or ''
