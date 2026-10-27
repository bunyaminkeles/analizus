"""
İstatistik analiz araçları için job runner.
Her araç kendi _run_<tool>(job, df) fonksiyonunu çağırır.
Dosya içeriği in-memory dict'te tutulur (bibliometrics pattern'i ile aynı).
"""
import io
import logging
import time

from django.utils.translation import gettext

logger = logging.getLogger(__name__)

SESSION_DATASET_TTL_SECONDS = 60 * 60 * 2  # 2 saat — SESSION_COOKIE_AGE ile hizalı

_pending_file_contents: dict[str, bytes] = {}
# Kullanıcının arayüz dili — aktif dil thread-local olduğundan işçi thread'i
# bilemez; run_job (istek thread'i) yakalar, _execute_job etkinleştirir.
_pending_job_languages: dict[str, str] = {}
_session_datasets: dict[str, tuple[bytes, str, float]] = {}  # session_key → (content, filename, saved_at)


def store_file_content(job_id: str, content: bytes):
    _pending_file_contents[job_id] = content


def save_session_dataset(session_key: str, content: bytes, filename: str):
    # Fırsatçı temizlik — harici (saatlik) cron bir ortamda (ör. Render) hiç
    # çalışmasa bile bu dict her yeni yüklemede süresi geçmiş girdilerden arınır.
    cleanup_expired_session_datasets()
    _session_datasets[session_key] = (content, filename, time.time())


def get_session_dataset(session_key: str) -> tuple[bytes, str] | None:
    stored = _session_datasets.get(session_key)
    if stored is None:
        return None
    content, filename, _saved_at = stored
    return content, filename


def move_session_dataset(old_key: str | None, new_key: str | None) -> None:
    """Login/register sırasında Django session_key'i cycle_key() ile değişiyor —
    RAM'deki veri setini eski anahtarda yetim bırakmamak için yeni anahtara taşır."""
    if not old_key or not new_key or old_key == new_key:
        return
    stored = _session_datasets.pop(old_key, None)
    if stored is not None:
        _session_datasets[new_key] = stored


def cleanup_expired_session_datasets(ttl_seconds: int = SESSION_DATASET_TTL_SECONDS) -> int:
    """TTL'i geçmiş session veri setlerini RAM'den siler. Cron endpoint'inden çağrılır."""
    cutoff = time.time() - ttl_seconds
    expired_keys = [key for key, (_, _, saved_at) in _session_datasets.items() if saved_at < cutoff]
    for key in expired_keys:
        _session_datasets.pop(key, None)
    return len(expired_keys)


def run_job(job_id: str):
    from django.utils import translation
    from analizdestek.job_queue import enqueue
    from istatistik.models import IstatistikJob
    job = IstatistikJob.objects.get(id=job_id)
    _pending_job_languages[job_id] = translation.get_language()
    enqueue(job.tool, job_id)


def _execute_job(job_id: str):
    """Worker thread'inde çalışır — sonuç metinleri ve PDF, işi başlatan
    kullanıcının dilinde üretilir."""
    from django.conf import settings
    from django.utils import translation
    lang = _pending_job_languages.pop(job_id, None) or settings.LANGUAGE_CODE
    with translation.override(lang):
        _execute_job_in_language(job_id)


def _execute_job_in_language(job_id: str):
    from istatistik.models import IstatistikJob
    try:
        job = IstatistikJob.objects.get(id=job_id)
    except IstatistikJob.DoesNotExist:
        logger.error(f'[istatistik] Job bulunamadı: {job_id}')
        return

    content = _pending_file_contents.pop(job_id, None)
    if content is None:
        job.mark_failed(gettext('Dosya içeriği bulunamadı. Lütfen tekrar yükleyin.'))
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
                test_value=opts.get('test_value'),
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
                target_category=opts.get('target_category', ''),
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
        elif job.tool == 'mediation':
            from .mediation import analyze, build_pdf
            opts = job.options or {}
            result_data = analyze(
                df,
                x_col=opts.get('x_col', ''),
                m_col=opts.get('m_col', ''),
                y_col=opts.get('y_col', ''),
            )
        elif job.tool == 'moderation':
            from .moderation import analyze, build_pdf
            opts = job.options or {}
            result_data = analyze(
                df,
                x_col=opts.get('x_col', ''),
                w_col=opts.get('w_col', ''),
                y_col=opts.get('y_col', ''),
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
        elif job.tool == 'kumeleme':
            from .kumeleme import analyze, build_pdf
            opts = job.options or {}
            result_data = analyze(
                df,
                columns=opts.get('columns') or [],
                method=opts.get('method', 'kmeans'),
                n_clusters=opts.get('n_clusters'),
            )
        elif job.tool == 'manova':
            from .manova import analyze, build_pdf
            opts = job.options or {}
            result_data = analyze(
                df,
                group_col=opts.get('group_col', ''),
                dep_cols=opts.get('dep_cols', []),
            )
        elif job.tool == 'sagkalim':
            from .sagkalim import analyze, build_pdf
            opts = job.options or {}
            result_data = analyze(
                df,
                method=opts.get('method', 'kaplan_meier'),
                duration_col=opts.get('duration_col', ''),
                event_col=opts.get('event_col', ''),
                event_category=opts.get('event_category', ''),
                group_col=opts.get('group_col', ''),
                covariate_cols=opts.get('covariate_cols', []),
            )
        elif job.tool == 'roc':
            from .roc import analyze, build_pdf
            opts = job.options or {}
            result_data = analyze(
                df,
                mode=opts.get('mode', 'single'),
                test_col=opts.get('test_col', ''),
                test_col2=opts.get('test_col2', ''),
                ref_col=opts.get('ref_col', ''),
                positive_category=opts.get('positive_category', ''),
            )
        else:
            job.mark_failed(gettext('Bilinmeyen araç: %(tool)s') % {'tool': job.tool})
            return

        try:
            _ai_comment_for_job(job, result_data)
        except Exception as e:
            logger.warning(f'[istatistik] AI Yorumu üretilemedi {job.tool}/{job_id}: {e}')

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
        job.mark_failed(gettext('Analiz sırasında hata oluştu: %(error)s') % {'error': e})
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
        raise ValueError(gettext('Desteklenmeyen dosya formatı. CSV veya Excel yükleyin.'))

    if df.empty:
        raise ValueError(gettext('Dosya boş veya okunamadı.'))
    if len(df) < 5:
        raise ValueError(gettext('En az 5 satır (katılımcı/gözlem) gereklidir, %(count)s satır bulundu.') % {'count': len(df)})

    return df


def _upload_pdf(pdf_bytes: bytes, job) -> str:
    from forum.s3_utils import upload_bytes_to_s3
    s3_key = f'istatistik/{job.tool}/{job.id}.pdf'
    url = upload_bytes_to_s3(pdf_bytes, s3_key, 'application/pdf')
    return url or ''


def cleanup_expired_istatistik_s3_files(days=7):
    """7 günden eski istatistik/ altındaki tüm PDF'leri S3'den siler (tüm araçlar
    tek `istatistik/<tool>/` ağacını paylaşır — pubmed ile aynı düz prefix kalıbı).
    DB'ye değil, S3'deki dosya tarihine bakar."""
    from django.utils import timezone
    from datetime import timedelta
    from istatistik.models import IstatistikJob
    from forum.s3_utils import cleanup_s3_prefix

    cutoff = timezone.now() - timedelta(days=days)
    deleted_count = cleanup_s3_prefix('istatistik/', days)

    # DB'deki URL referansını da temizle
    try:
        IstatistikJob.objects.filter(
            created_at__lt=cutoff,
        ).exclude(pdf_url='').update(pdf_url='')
    except Exception as e:
        logger.error(f"DB temizlik hatası (istatistik): {e}")

    logger.info(f"S3 temizlik (istatistik): {deleted_count} dosya silindi")
    return deleted_count


_AI_PROMPT_EXCLUDE_KEYS = {
    'tree_text',       # karar_agaci: uzun ASCII ağaç çıktısı, yorum için gereksiz
    'heatmap_b64',     # korelasyon: base64 PNG, metin yoruma hiç katkı sağlamıyor
    'scree_plot_b64',  # afa: base64 PNG, metin yoruma hiç katkı sağlamıyor
    'interaction_plot_b64',  # moderation: base64 PNG, metin yoruma hiç katkı sağlamıyor
    'diagnostic_plot_b64',   # kumeleme: base64 PNG (elbow/dendrogram), metin yoruma katkı sağlamıyor
    'scatter_plot_b64',      # kumeleme: base64 PNG, metin yoruma katkı sağlamıyor
    'profile_plot_b64',      # manova: base64 PNG, metin yoruma katkı sağlamıyor
    'km_plot_b64',           # sagkalim: base64 PNG, metin yoruma katkı sağlamıyor
    'curves',                # sagkalim: uzun zaman/olasılık dizileri, yorum için gereksiz
    'roc_plot_b64',          # roc: base64 PNG, metin yoruma katkı sağlamıyor
}


def _ai_comment_for_job(job, result_data: dict):
    """Claude ile kısa akademik yorum üretir, result_data['ai_comment']'e yazar.
    Hata/kota/flag durumunda sessizce atlar — iş sonucu AI yorumu olmadan tamamlanır."""
    from django.utils import translation
    from forum.models import SiteSettings, AIUsageLog
    from forum.services.claude_service import claude_summary_service

    if not SiteSettings.load().feature_ai_summary:
        return
    if not job.user or not AIUsageLog.can_use(job.user):
        return

    prompt = _build_ai_prompt(job.get_tool_display(), result_data)
    resp = claude_summary_service.generate_summary('istatistik', prompt, lang=translation.get_language())
    if resp['success'] and resp['text']:
        result_data['ai_comment'] = resp['text']
        AIUsageLog.record(job.user, 'istatistik', resp['input_tokens'], resp['output_tokens'])


def _build_ai_prompt(tool_label: str, result_data: dict) -> str:
    import json
    safe = {k: v for k, v in result_data.items() if k not in _AI_PROMPT_EXCLUDE_KEYS}
    data_json = json.dumps(safe, ensure_ascii=False, default=str)[:4000]
    return (
        f"Araç: {tool_label}\n\n"
        f"Analiz sonuç verileri (JSON):\n{data_json}\n\n"
        "Bu istatistiksel analiz sonucunu kullanıcıya akademik dilde yorumla."
    )
