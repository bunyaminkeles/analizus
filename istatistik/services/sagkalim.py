"""
Sağkalım Analizi (Kaplan-Meier / Cox Regresyon) — statsmodels.duration modülü
kullanılır (SurvfuncRight, survdiff, PHReg); harici bağımlılık gerekmez
(lifelines pandas>=3.0 ile uyumsuz olduğu için statsmodels'in kendi sağkalım
analizi altyapısı tercih edildi). Kaplan-Meier opsiyonel grup karşılaştırması
(log-rank testi) destekler; Cox Regresyon çoklu kovaryat ile hazard oranı,
concordance index ve oransal tehlikeler (PH) varsayım testi (Grambsch &
Therneau, 1994 yaklaşımı) raporlar.
"""
import io
from django.utils.translation import gettext
import numpy as np


def _encode_event(series, event_col: str, event_category: str = ''):
    """lojistik_regresyon.py ile aynı 2-kategori → 0/1 kodlama deseni."""
    unique_vals = series.unique()
    if len(unique_vals) != 2:
        raise ValueError(gettext(
            'Olay değişkeninin tam 2 kategorisi olmalıdır (ör. 0/1, Öldü/Sağ). '
            '"%(col)s" sütununda %(n)s farklı değer bulundu.'
        ) % {'col': event_col, 'n': len(unique_vals)})
    unique_vals_list = unique_vals.tolist()
    try:
        sorted_vals = sorted(unique_vals_list, key=float)
    except (TypeError, ValueError):
        sorted_vals = sorted(unique_vals_list, key=str)
    target_match = next((v for v in unique_vals if str(v) == str(event_category)), None) if event_category else None
    if target_match is not None:
        event_label = str(target_match)
        status = (series == target_match).astype(int).values
    else:
        event_label = str(sorted_vals[1])
        status = (series == sorted_vals[1]).astype(int).values
    return status, event_label


def analyze(df, method: str = 'kaplan_meier', duration_col: str = '', event_col: str = '',
            event_category: str = '', group_col: str = '', covariate_cols=None) -> dict:
    method = method if method in ('kaplan_meier', 'cox') else 'kaplan_meier'

    if not duration_col:
        raise ValueError(gettext('Süre değişkeni seçilmelidir.'))
    if duration_col not in df.columns:
        raise ValueError(gettext('"%(col)s" sütunu bulunamadı.') % {'col': duration_col})
    if not event_col:
        raise ValueError(gettext('Olay değişkeni seçilmelidir.'))
    if event_col not in df.columns:
        raise ValueError(gettext('"%(col)s" sütunu bulunamadı.') % {'col': event_col})
    if duration_col == event_col:
        raise ValueError(gettext('Süre ve olay değişkeni farklı sütunlar olmalıdır.'))

    cols = [duration_col, event_col]
    group_col = group_col or ''
    if method == 'kaplan_meier' and group_col:
        if group_col in (duration_col, event_col):
            raise ValueError(gettext('Grup değişkeni, süre veya olay değişkeniyle aynı olamaz.'))
        if group_col not in df.columns:
            raise ValueError(gettext('"%(col)s" sütunu bulunamadı.') % {'col': group_col})
        cols.append(group_col)

    covariate_cols = list(covariate_cols or [])
    if method == 'cox':
        if not covariate_cols:
            raise ValueError(gettext('Cox regresyon için en az 1 kovaryat seçilmelidir.'))
        missing = [c for c in covariate_cols if c not in df.columns]
        if missing:
            raise ValueError(gettext('Şu sütunlar bulunamadı: %(v)s') % {'v': ', '.join(missing)})
        if duration_col in covariate_cols or event_col in covariate_cols:
            raise ValueError(gettext('Süre veya olay değişkeni kovaryatlar arasında olamaz.'))
        cols.extend(covariate_cols)

    sub = df[cols].dropna()
    n = len(sub)
    if n < 10:
        raise ValueError(gettext('En az 10 gözlem gereklidir, %(n)s satır bulundu.') % {'n': n})

    try:
        duration = sub[duration_col].astype(float).values
    except Exception:
        raise ValueError(gettext('"%(col)s" sayısal bir değişken olmalıdır.') % {'col': duration_col})
    if np.any(duration < 0):
        raise ValueError(gettext('Süre değişkeni negatif değer içeremez.'))

    status, event_label = _encode_event(sub[event_col], event_col, event_category)
    n_events = int(status.sum())
    if n_events < 5:
        raise ValueError(gettext('En az 5 olay (event) gereklidir, %(n)s olay bulundu.') % {'n': n_events})

    if method == 'kaplan_meier':
        return _analyze_kaplan_meier(sub, duration, status, event_label, event_col, duration_col, group_col)
    return _analyze_cox(sub, duration, status, event_label, event_col, duration_col, covariate_cols)


def _curve_dict(label: str, sf, n: int, n_events: int) -> dict:
    try:
        median = sf.quantile(0.5)
        median = None if median != median else round(float(median), 3)
    except Exception:
        median = None
    return {
        'label': label,
        'n': n,
        'n_events': n_events,
        'median_survival': median,
        'times': [_safe_round(t, 4) for t in sf.surv_times],
        'surv_prob': [_safe_round(p, 4) for p in sf.surv_prob],
        'surv_prob_se': [_safe_round(s, 4) for s in sf.surv_prob_se],
    }


def _safe_round(v, ndigits: int):
    """NaN/inf → None — Postgres JSONField NaN/Infinity kabul etmez
    (CLAUDE.md: 'result_data kaydetmeden önce inf/nan temizle')."""
    v = float(v)
    if v != v or np.isinf(v):
        return None
    return round(v, ndigits)


def _analyze_kaplan_meier(sub, duration, status, event_label, event_col, duration_col, group_col) -> dict:
    from statsmodels.duration.survfunc import SurvfuncRight, survdiff

    n = len(duration)
    curves = []
    logrank = None

    if group_col:
        raw_labels = sub[group_col].unique().tolist()
        try:
            group_labels = sorted(raw_labels, key=float)
        except (TypeError, ValueError):
            group_labels = sorted(raw_labels, key=str)
        if len(group_labels) < 2:
            raise ValueError(gettext('Grup değişkeninde en az 2 farklı değer olmalıdır.'))
        if len(group_labels) > 6:
            raise ValueError(gettext('En fazla 6 grup desteklenmektedir.'))
        group_vals = sub[group_col].values
        for lbl in group_labels:
            mask = group_vals == lbl
            if int(mask.sum()) < 5:
                raise ValueError(gettext('"%(lbl)s" grubunda en az 5 gözlem olmalıdır.') % {'lbl': lbl})
            sf = SurvfuncRight(duration[mask], status[mask])
            curves.append(_curve_dict(str(lbl), sf, int(mask.sum()), int(status[mask].sum())))
        chisq, p_val = survdiff(duration, status, group_vals)
        logrank = {
            'chisq': round(float(chisq), 3),
            'df': len(group_labels) - 1,
            'p': round(float(p_val), 4),
            'significant': bool(p_val < 0.05),
        }
    else:
        sf = SurvfuncRight(duration, status)
        curves.append(_curve_dict(gettext('Tüm Örneklem'), sf, n, int(status.sum())))

    km_plot_b64 = _build_km_plot(curves)

    return {
        'method': 'kaplan_meier',
        'method_label': gettext('Kaplan-Meier'),
        'duration_col': duration_col,
        'event_col': event_col,
        'event_label': event_label,
        'group_col': group_col,
        'n': n,
        'n_events': int(status.sum()),
        'curves': curves,
        'logrank': logrank,
        'km_plot_b64': km_plot_b64,
        'conclusion': _km_conclusion(curves, logrank, group_col),
    }


def _build_km_plot(curves) -> str:
    import base64
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=110)
    cmap = plt.get_cmap('tab10')
    for i, c in enumerate(curves):
        times = [0.0] + c['times']
        probs = [1.0] + c['surv_prob']
        ax.step(times, probs, where='post', label=c['label'], color=cmap(i % 10), linewidth=2)
    ax.set_xlabel(gettext('Süre'))
    ax.set_ylabel(gettext('Sağkalım Olasılığı'))
    ax.set_ylim(0, 1.05)
    if len(curves) > 1:
        ax.legend(fontsize=8)
    ax.grid(alpha=0.2)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('ascii')


def _km_conclusion(curves, logrank, group_col) -> str:
    if not group_col:
        c = curves[0]
        if c['median_survival'] is not None:
            return gettext(
                'Medyan sağkalım süresi %(median)s olarak hesaplanmıştır (N = %(n)s, olay sayısı = %(e)s).'
            ) % {'median': c['median_survival'], 'n': c['n'], 'e': c['n_events']}
        return gettext(
            'Örneklemin yarısından azı gözlem süresi içinde olay yaşadığı için medyan sağkalım süresi '
            'hesaplanamamıştır (N = %(n)s, olay sayısı = %(e)s).'
        ) % {'n': c['n'], 'e': c['n_events']}
    p_str = 'p < .001' if logrank['p'] < 0.001 else f"p = {logrank['p']:.4f}"
    if logrank['significant']:
        return gettext(
            'Log-rank testine göre gruplar arasında sağkalım süreleri açısından istatistiksel olarak '
            'anlamlı bir fark bulunmaktadır [χ²(%(df)s) = %(chisq)s, %(p)s].'
        ) % {'df': logrank['df'], 'chisq': f"{logrank['chisq']:.3f}", 'p': p_str}
    return gettext(
        'Log-rank testine göre gruplar arasında sağkalım süreleri açısından istatistiksel olarak anlamlı '
        'bir fark bulunmamaktadır [χ²(%(df)s) = %(chisq)s, %(p)s].'
    ) % {'df': logrank['df'], 'chisq': f"{logrank['chisq']:.3f}", 'p': p_str}


def _analyze_cox(sub, duration, status, event_label, event_col, duration_col, covariate_cols) -> dict:
    import pandas as pd
    from statsmodels.duration.hazard_regression import PHReg

    n = len(duration)
    n_events = int(status.sum())
    min_events_needed = 10 * len(covariate_cols)
    if n_events < min_events_needed:
        raise ValueError(gettext(
            'Cox regresyon için önerilen minimum olay sayısına ulaşılamadı: değişken başına en az 10 '
            'olay gerekir (gerekli ≥ %(need)s, mevcut = %(have)s).'
        ) % {'need': min_events_needed, 'have': n_events})

    X_df = pd.DataFrame(index=sub.index)
    feature_names = []
    for col in covariate_cols:
        series = sub[col]
        if series.dtype == object or series.nunique() <= 10:
            dummies = pd.get_dummies(series, prefix=col, drop_first=True, dtype=float)
            if dummies.shape[1] == 0:
                raise ValueError(gettext('"%(col)s" sütununda yeterli varyasyon yok.') % {'col': col})
            X_df = pd.concat([X_df, dummies], axis=1)
            feature_names.extend(list(dummies.columns))
        else:
            X_df[col] = series.astype(float)
            feature_names.append(col)

    X = X_df.values.astype(float)
    model = PHReg(duration, X, status=status, ties='efron')
    res = model.fit()

    params = np.asarray(res.params)
    bse = np.asarray(res.bse)
    pvalues = np.asarray(res.pvalues)
    ci_log = np.asarray(res.conf_int())
    hr = np.exp(params)
    hr_ci = np.exp(ci_log)

    coef_table = []
    for i, name in enumerate(feature_names):
        coef_table.append({
            'name': name,
            'coef': round(float(params[i]), 4),
            'se': round(float(bse[i]), 4),
            'hr': round(float(hr[i]), 4),
            'hr_ci_low': round(float(hr_ci[i, 0]), 4),
            'hr_ci_high': round(float(hr_ci[i, 1]), 4),
            'p': round(float(pvalues[i]), 4),
            'significant': bool(pvalues[i] < 0.05),
        })

    concordance = _concordance_index(duration, status, X @ params)
    ph_test = _ph_assumption_test(res, model, feature_names)

    return {
        'method': 'cox',
        'method_label': gettext('Cox Regresyon'),
        'duration_col': duration_col,
        'event_col': event_col,
        'event_label': event_label,
        'covariate_cols': covariate_cols,
        'feature_names': feature_names,
        'n': n,
        'n_events': n_events,
        'coef_table': coef_table,
        'concordance_index': round(float(concordance), 4) if concordance == concordance else None,
        'ph_test': ph_test,
        'log_likelihood': round(float(res.llf), 3),
        'conclusion': _cox_conclusion(coef_table, event_col),
    }


def _concordance_index(times, events, risk_scores) -> float:
    """Harrell's C-index — zamana göre sıralanmış, olay yaşayan her gözlem için
    daha sonra gerçekleşen tüm gözlemlerle karşılaştırılabilir çiftler üzerinden
    hesaplanır (eşit risk skorunda 0.5 ağırlık)."""
    times = np.asarray(times)
    events = np.asarray(events)
    risk = np.asarray(risk_scores)
    order = np.argsort(times)
    times = times[order]
    events = events[order]
    risk = risk[order]
    n = len(times)
    concordant = 0.0
    comparable = 0.0
    for i in range(n):
        if events[i] != 1:
            continue
        mask = times[i + 1:] > times[i]
        if not np.any(mask):
            continue
        rj = risk[i + 1:][mask]
        comparable += len(rj)
        concordant += np.sum(risk[i] > rj) + 0.5 * np.sum(risk[i] == rj)
    return concordant / comparable if comparable > 0 else float('nan')


def _ph_assumption_test(res, model, feature_names) -> dict | None:
    """Oransal tehlikeler (proportional hazards) varsayım testi — ölçeklenmiş
    Schoenfeld rezidülerinin olay zamanının sırasıyla (rank) korelasyonu
    (Grambsch & Therneau, 1994 yaklaşımı; R'deki survival::cox.zph ile aynı
    mantık, basitleştirilmiş). Anlamlı korelasyon (p < .05) o değişkenin
    etkisinin zamana göre sabit olmadığına işaret eder."""
    from scipy.stats import rankdata, pearsonr

    sch = res.schoenfeld_residuals
    if sch.shape[0] == 0:
        return None
    valid = ~np.isnan(sch[:, 0])
    n_events = int(valid.sum())
    if n_events < 3:
        return None

    cov_beta = np.asarray(res.cov_params())
    r_event = sch[valid]
    scaled = n_events * (r_event @ cov_beta) + np.asarray(res.params)[None, :]
    event_times = np.asarray(model.endog)[valid]
    ranked_t = rankdata(event_times)

    per_covariate = []
    for j, name in enumerate(feature_names):
        try:
            corr, p_val = pearsonr(ranked_t, scaled[:, j])
        except Exception:
            corr, p_val = float('nan'), float('nan')
        per_covariate.append({
            'name': name,
            'correlation': round(float(corr), 4) if corr == corr else None,
            'p': round(float(p_val), 4) if p_val == p_val else None,
            'violated': bool(p_val < 0.05) if p_val == p_val else False,
        })
    return {
        'per_covariate': per_covariate,
        'any_violated': any(c['violated'] for c in per_covariate),
    }


def _cox_conclusion(coef_table, event_col) -> str:
    sig = [c for c in coef_table if c['significant']]
    if not sig:
        return gettext(
            'Modeldeki hiçbir kovaryat %(event_col)s riski üzerinde istatistiksel olarak anlamlı bir '
            'etki göstermemiştir.'
        ) % {'event_col': event_col}
    parts = []
    for c in sig:
        direction = gettext('artırmaktadır') if c['hr'] > 1 else gettext('azaltmaktadır')
        parts.append(gettext('%(name)s (HR = %(hr)s) riski %(direction)s') % {
            'name': c['name'], 'hr': f"{c['hr']:.3f}", 'direction': direction})
    return gettext('Şu değişkenler istatistiksel olarak anlamlı bulunmuştur: %(v)s.') % {'v': '; '.join(parts)}


def build_pdf(result: dict, filename: str, df=None) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from .pdf_fonts import register_fonts, append_ai_comment
    register_fonts()

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    TEAL = colors.HexColor('#0f766e')
    title_s = ParagraphStyle('T', parent=styles['Heading1'], fontSize=16, spaceAfter=6, fontName='DejaVuSans')
    h2_s = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, spaceAfter=4, fontName='DejaVuSans')
    norm_s = ParagraphStyle('N', parent=styles['Normal'], fontName='DejaVuSans', fontSize=9)

    def p_str(v):
        return '< .001' if v < 0.001 else f'{v:.4f}'

    story = []
    story.append(Paragraph(gettext('Sağkalım Analizi Raporu (%(method)s)') % {'method': result['method_label']}, title_s))
    story.append(Paragraph(gettext('Dosya: %(filename)s') % {'filename': filename}, norm_s))
    story.append(Spacer(1, 0.4*cm))

    if result['method'] == 'kaplan_meier':
        summary_rows = [
            [gettext('Süre Değişkeni'), result['duration_col']],
            [gettext('Olay Değişkeni'), f"{result['event_col']} = {result['event_label']}"],
            ['N', str(result['n'])],
            [gettext('Olay Sayısı'), str(result['n_events'])],
        ]
        sum_tbl = Table(summary_rows, colWidths=[6*cm, 10*cm])
        sum_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), TEAL),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.whitesmoke, colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(sum_tbl)
        story.append(Spacer(1, 0.5*cm))

        story.append(Paragraph(gettext('Sağkalım Eğrisi (Kaplan-Meier)'), h2_s))
        if result.get('km_plot_b64'):
            img_data = __import__('base64').b64decode(result['km_plot_b64'])
            story.append(Image(io.BytesIO(img_data), width=13*cm, height=8.4*cm))
        story.append(Spacer(1, 0.4*cm))

        story.append(Paragraph(gettext('Grup Özeti'), h2_s))
        curve_rows = [[gettext('Grup'), 'N', gettext('Olay'), gettext('Medyan Sağkalım')]]
        for c in result['curves']:
            curve_rows.append([c['label'], str(c['n']), str(c['n_events']),
                               str(c['median_survival']) if c['median_survival'] is not None else gettext('Ulaşılamadı')])
        curve_tbl = Table(curve_rows, colWidths=[6*cm, 2.5*cm, 2.5*cm, 5*cm])
        curve_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), TEAL),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(curve_tbl)
        story.append(Spacer(1, 0.5*cm))

        if result.get('logrank'):
            lr = result['logrank']
            story.append(Paragraph(gettext('Log-Rank Testi'), h2_s))
            story.append(Paragraph(
                gettext('χ²(%(df)s) = %(chisq)s, %(p)s — %(concl)s') % {
                    'df': lr['df'], 'chisq': f"{lr['chisq']:.3f}", 'p': p_str(lr['p']),
                    'concl': gettext('anlamlı fark var') if lr['significant'] else gettext('anlamlı fark yok'),
                }, norm_s))
            story.append(Spacer(1, 0.5*cm))

    else:  # cox
        summary_rows = [
            [gettext('Süre Değişkeni'), result['duration_col']],
            [gettext('Olay Değişkeni'), f"{result['event_col']} = {result['event_label']}"],
            [gettext('Kovaryatlar'), ', '.join(result['covariate_cols'])],
            ['N', str(result['n'])],
            [gettext('Olay Sayısı'), str(result['n_events'])],
            [gettext('Concordance Index (C)'), f"{result['concordance_index']:.4f}" if result['concordance_index'] is not None else '—'],
            [gettext('Log-Likelihood'), f"{result['log_likelihood']:.3f}"],
        ]
        sum_tbl = Table(summary_rows, colWidths=[6*cm, 10*cm])
        sum_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), TEAL),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.whitesmoke, colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(sum_tbl)
        story.append(Spacer(1, 0.5*cm))

        story.append(Paragraph(gettext('Hazard Oranları (Cox Regresyon)'), h2_s))
        coef_rows = [[gettext('Değişken'), 'HR', '%95 GA', 'p']]
        for c in result['coef_table']:
            coef_rows.append([c['name'], f"{c['hr']:.3f}", f"[{c['hr_ci_low']:.3f}, {c['hr_ci_high']:.3f}]", p_str(c['p'])])
        coef_tbl = Table(coef_rows, colWidths=[6*cm, 2.5*cm, 4.5*cm, 3*cm])
        coef_style = [
            ('BACKGROUND', (0, 0), (-1, 0), TEAL),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ]
        for i, c in enumerate(result['coef_table'], start=1):
            if c['significant']:
                coef_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#d4edda')))
        coef_tbl.setStyle(TableStyle(coef_style))
        story.append(coef_tbl)
        story.append(Spacer(1, 0.5*cm))

        if result.get('ph_test'):
            story.append(Paragraph(gettext('Oransal Tehlikeler (Proportional Hazards) Varsayım Testi'), h2_s))
            ph_rows = [[gettext('Değişken'), gettext('Korelasyon'), 'p', gettext('Varsayım İhlali')]]
            for c in result['ph_test']['per_covariate']:
                ph_rows.append([c['name'],
                                f"{c['correlation']:.4f}" if c['correlation'] is not None else '—',
                                p_str(c['p']) if c['p'] is not None else '—',
                                gettext('Evet') if c['violated'] else gettext('Hayır')])
            ph_tbl = Table(ph_rows, colWidths=[6*cm, 3*cm, 3*cm, 4*cm])
            ph_style = [
                ('BACKGROUND', (0, 0), (-1, 0), TEAL),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
                ('FONTSIZE', (0, 0), (-1, -1), 8.5),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ]
            for i, c in enumerate(result['ph_test']['per_covariate'], start=1):
                if c['violated']:
                    ph_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8d7da')))
            ph_tbl.setStyle(TableStyle(ph_style))
            story.append(ph_tbl)
            story.append(Paragraph(
                '<font color="#666666" size="8">' + gettext(
                    'Anlamlı korelasyon (p &lt; .05) ilgili değişkenin etkisinin zamana göre sabit '
                    'olmayabileceğine (oransal tehlikeler varsayımının ihlal edildiğine) işaret eder.'
                ) + '</font>', norm_s))
            story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(gettext('Yorum'), h2_s))
    story.append(Paragraph(result['conclusion'], norm_s))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(gettext('APA Formatında Raporlama'), h2_s))
    if result['method'] == 'kaplan_meier':
        if result.get('logrank'):
            lr = result['logrank']
            apa_text = gettext(
                'Kaplan-Meier sağkalım analizi sonucunda, log-rank testine göre gruplar arasında sağkalım '
                'süreleri açısından {concl}, χ²({df}) = {chisq}, {p}.'
            ).format(
                concl=gettext('anlamlı bir fark bulunmuştur') if lr['significant'] else gettext('anlamlı bir fark bulunmamıştır'),
                df=lr['df'], chisq=f"{lr['chisq']:.3f}", p=p_str(lr['p']))
        else:
            c = result['curves'][0]
            apa_text = gettext(
                'Kaplan-Meier sağkalım analizi uygulanmış (N = {n}, olay sayısı = {e}), medyan sağkalım '
                'süresi {median} olarak bulunmuştur.'
            ).format(n=c['n'], e=c['n_events'], median=c['median_survival'] if c['median_survival'] is not None else gettext('ulaşılamadı'))
    else:
        sig = [c for c in result['coef_table'] if c['significant']]
        if sig:
            top = sig[0]
            apa_text = gettext(
                'Cox orantılı tehlikeler (proportional hazards) regresyon modeli uygulanmıştır (N = {n}, '
                'olay sayısı = {e}, Concordance Index = {ci}). {name} değişkeni istatistiksel olarak anlamlı '
                'bulunmuştur, HR = {hr}, %95 GA [{lo}, {hi}], {p}.'
            ).format(n=result['n'], e=result['n_events'],
                     ci=f"{result['concordance_index']:.3f}" if result['concordance_index'] is not None else '—',
                     name=top['name'], hr=f"{top['hr']:.3f}", lo=f"{top['hr_ci_low']:.3f}",
                     hi=f"{top['hr_ci_high']:.3f}", p=p_str(top['p']))
        else:
            apa_text = gettext(
                'Cox orantılı tehlikeler (proportional hazards) regresyon modeli uygulanmıştır (N = {n}, '
                'olay sayısı = {e}, Concordance Index = {ci}). Modeldeki hiçbir kovaryat istatistiksel '
                'olarak anlamlı bulunmamıştır.'
            ).format(n=result['n'], e=result['n_events'],
                     ci=f"{result['concordance_index']:.3f}" if result['concordance_index'] is not None else '—')
    apa_tbl = Table([[Paragraph(apa_text, norm_s)]], colWidths=[16*cm])
    apa_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0fdfa')),
        ('BOX', (0, 0), (-1, -1), 1, TEAL),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(apa_tbl)
    append_ai_comment(story, result, norm_s, '#f0fdfa', TEAL)

    doc.build(story)
    return buf.getvalue()
