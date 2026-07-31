"""
İstatistik analiz araçları için job runner.
Her araç kendi _run_<tool>(job, df) fonksiyonunu çağırır.
Dosya içeriği in-memory dict'te tutulur (bibliometrics pattern'i ile aynı).
"""
import io
import logging
import time

logger = logging.getLogger(__name__)

SESSION_DATASET_TTL_SECONDS = 60 * 60 * 2  # 2 saat — SESSION_COOKIE_AGE ile hizalı

_pending_file_contents: dict[str, bytes] = {}
_session_datasets: dict[str, tuple[bytes, str, float]] = {}  # session_key → (content, filename, saved_at)


def store_file_content(job_id: str, content: bytes):
    _pending_file_contents[job_id] = content


def save_session_dataset(session_key: str, content: bytes, filename: str):
    _session_datasets[session_key] = (content, filename, time.time())


def get_session_dataset(session_key: str) -> tuple[bytes, str] | None:
    stored = _session_datasets.get(session_key)
    if stored is None:
        return None
    content, filename, _saved_at = stored
    return content, filename


def cleanup_expired_session_datasets(ttl_seconds: int = SESSION_DATASET_TTL_SECONDS) -> int:
    """TTL'i geçmiş session veri setlerini RAM'den siler. Cron endpoint'inden çağrılır."""
    cutoff = time.time() - ttl_seconds
    expired_keys = [key for key, (_, _, saved_at) in _session_datasets.items() if saved_at < cutoff]
    for key in expired_keys:
        _session_datasets.pop(key, None)
    return len(expired_keys)


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
            columns = (job.options or {}).get('columns') or None
            result_data = analyze(df, columns=columns)
        elif job.tool == 'korelasyon':
            from .korelasyon import analyze, build_pdf
            method = (job.options or {}).get('method', 'pearson')
            columns = (job.options or {}).get('columns') or None
            result_data = analyze(df, method=method, columns=columns)
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
        elif job.tool == 'ki_kare':
            from .ki_kare import analyze, build_pdf
            opts = job.options or {}
            result_data = analyze(
                df,
                col1=opts.get('group_col'),
                col2=opts.get('dep_col'),
            )
        elif job.tool == 'lineer_regresyon':
            from .lineer_regresyon import analyze, build_pdf
            opts = job.options or {}
            result_data = analyze(
                df,
                dep_col=opts.get('dep_col', ''),
                indep_cols=opts.get('indep_cols', []),
            )
        elif job.tool == 'lojistik_regresyon':
            from .lojistik_regresyon import analyze, build_pdf
            opts = job.options or {}
            result_data = analyze(
                df,
                dep_col=opts.get('dep_col', ''),
                indep_cols=opts.get('indep_cols', []),
            )
        elif job.tool == 'afa':
            from .afa import analyze, build_pdf
            opts = job.options or {}
            result_data = analyze(
                df,
                columns=opts.get('columns') or None,
                n_factors=opts.get('n_factors') or None,
                rotation=opts.get('rotation', 'varimax'),
            )
        elif job.tool == 'wilcoxon':
            from .wilcoxon import analyze, build_pdf
            opts = job.options or {}
            result_data = analyze(
                df,
                col1=opts.get('col1'),
                col2=opts.get('col2'),
            )
        elif job.tool == 'friedman':
            from .friedman import analyze, build_pdf
            opts = job.options or {}
            result_data = analyze(
                df,
                columns=opts.get('columns') or [],
            )
        elif job.tool == 'tekrarli_anova':
            from .tekrarli_anova import analyze, build_pdf
            opts = job.options or {}
            result_data = analyze(
                df,
                columns=opts.get('columns') or [],
            )
        elif job.tool == 'karar_agaci':
            from .karar_agaci import analyze, build_pdf
            opts = job.options or {}
            max_d = opts.get('max_depth', 5)
            t_size = opts.get('test_size', 0.2)
            result_data = analyze(
                df,
                target_col=opts.get('target_col', ''),
                feature_cols=opts.get('feature_cols', []),
                max_depth=int(max_d) if str(max_d).isdigit() else 5,
                test_size=float(t_size) if t_size else 0.2,
                criterion=opts.get('criterion', 'gini'),
            )
        elif job.tool == 'svm':
            from .svm import analyze, build_pdf
            opts = job.options or {}
            t_size = opts.get('test_size', 0.2)
            c_val = opts.get('C', 1.0)
            result_data = analyze(
                df,
                target_col=opts.get('target_col', ''),
                feature_cols=opts.get('feature_cols', []),
                kernel=opts.get('kernel', 'rbf'),
                C=float(c_val) if c_val else 1.0,
                test_size=float(t_size) if t_size else 0.2,
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
