"""
Düzenleyici Değişken (Moderation) Analizi — Y ~ X + W + X*W (Aiken & West, 1991
merkezleme standardı). X (yordayıcı) ve Y (sonuç) sayısal/sürekli olmalı; W
(düzenleyici) sürekli veya 2 kategorili olabilir. Etkileşim teriminin (b3)
anlamlılığı düzenleme etkisini belirler; basit eğimler (simple slopes) W'nin
düşük/orta/yüksek (veya 2 kategorili) düzeylerinde X'in koşullu etkisini
raporlar — Hayes/Process Model 1 ile aynı mantık.
"""
import io
import base64
from django.utils.translation import gettext
import numpy as np


def _fit_ols(y, X):
    import statsmodels.api as sm
    X_sm = sm.add_constant(X, has_constant='add')
    return sm.OLS(y, X_sm).fit()


def analyze(df, x_col: str, w_col: str, y_col: str) -> dict:
    import pandas as pd
    from scipy.stats import t as t_dist

    for col, label in ((x_col, gettext('Bağımsız/yordayıcı değişken (X)')), (w_col, gettext('Düzenleyici değişken (W)')), (y_col, gettext('Bağımlı değişken (Y)'))):
        if not col:
            raise ValueError(gettext('%(label)s seçilmelidir.') % {'label': label})
        if col not in df.columns:
            raise ValueError(gettext('"%(col)s" sütunu bulunamadı.') % {'col': col})
    if len({x_col, w_col, y_col}) < 3:
        raise ValueError(gettext('Bağımsız, düzenleyici ve bağımlı değişkenler birbirinden farklı olmalıdır.'))

    sub = df[[x_col, w_col, y_col]].dropna()
    n = len(sub)
    if n < 30:
        raise ValueError(gettext('Yetersiz gözlem sayısı (n = %(n)s). Düzenleyici değişken analizi için en az 30 satır gereklidir.') % {'n': n})

    try:
        x = sub[x_col].astype(float).values
        y = sub[y_col].astype(float).values
    except Exception:
        raise ValueError(gettext('Bağımsız (X) ve bağımlı (Y) değişkenler sayısal olmalıdır.'))

    w_series = sub[w_col]
    if w_series.dtype == object or w_series.nunique() <= 10:
        if w_series.nunique() < 2:
            raise ValueError(gettext('Düzenleyici değişkende (W) en az 2 farklı değer olmalıdır.'))
        dummies = pd.get_dummies(w_series, drop_first=True, dtype=float)
        if dummies.shape[1] != 1:
            raise ValueError(gettext('Düzenleyici değişken (W) sayısal veya yalnızca 2 kategorili olmalıdır.'))
        w = dummies.iloc[:, 0].values
        w_is_categorical = True
    else:
        try:
            w = w_series.astype(float).values
        except Exception:
            raise ValueError(gettext('"%(col)s" sayısal bir değişken olmalıdır.') % {'col': w_col})
        w_is_categorical = False

    x_mean, w_mean = float(np.mean(x)), float(np.mean(w))
    xc = x - x_mean
    wc = w - w_mean
    inter = xc * wc

    full_X = np.column_stack([xc, wc, inter])
    model = _fit_ols(y, full_X)
    reduced_X = np.column_stack([xc, wc])
    model_reduced = _fit_ols(y, reduced_X)

    b1, b2, b3 = (float(model.params[i]) for i in (1, 2, 3))
    se1, se2, se3 = (float(model.bse[i]) for i in (1, 2, 3))
    p1, p2, p3 = (float(model.pvalues[i]) for i in (1, 2, 3))

    r2_full = float(model.rsquared)
    r2_reduced = float(model_reduced.rsquared)
    delta_r2 = r2_full - r2_reduced
    interaction_significant = p3 < 0.05

    # Basit eğimler (simple slopes)
    cov = np.asarray(model.cov_params())
    df_resid = int(model.df_resid)

    def slope_at(wc_level):
        effect = b1 + b3 * wc_level
        var = cov[1, 1] + (wc_level ** 2) * cov[3, 3] + 2 * wc_level * cov[1, 3]
        se = float(np.sqrt(var)) if var > 0 else 0.0
        tval = effect / se if se > 0 else 0.0
        pval = float(2 * (1 - t_dist.cdf(abs(tval), df_resid)))
        return effect, se, tval, pval

    simple_slopes = []
    if w_is_categorical:
        levels = [(gettext('W = 0'), 0.0 - w_mean, 0.0), (gettext('W = 1'), 1.0 - w_mean, 1.0)]
    else:
        w_std = float(np.std(w, ddof=1))
        levels = [
            (gettext('Düşük W (Ort. − 1SS)'), -w_std, w_mean - w_std),
            (gettext('Orta W (Ortalama)'), 0.0, w_mean),
            (gettext('Yüksek W (Ort. + 1SS)'), w_std, w_mean + w_std),
        ]
    for label, wc_level, w_original in levels:
        effect, se, tval, pval = slope_at(wc_level)
        simple_slopes.append({
            'label': label,
            'w_value': round(float(w_original), 4),
            'effect': round(effect, 4),
            'se': round(se, 4),
            't': round(tval, 3),
            'p': round(pval, 4),
            'significant': bool(pval < 0.05),
        })

    plot_b64 = _build_interaction_plot(x, y, x_mean, w_mean, model.params, w_is_categorical, w_std=None if w_is_categorical else float(np.std(w, ddof=1)))

    return {
        'x_col': x_col,
        'w_col': w_col,
        'y_col': y_col,
        'w_is_categorical': w_is_categorical,
        'n': n,
        'b1': {'coef': round(b1, 4), 'se': round(se1, 4), 'p': round(p1, 4), 'significant': bool(p1 < 0.05)},
        'b2': {'coef': round(b2, 4), 'se': round(se2, 4), 'p': round(p2, 4), 'significant': bool(p2 < 0.05)},
        'b3': {'coef': round(b3, 4), 'se': round(se3, 4), 'p': round(p3, 4), 'significant': bool(interaction_significant)},
        'r_squared_full': round(r2_full, 4),
        'r_squared_reduced': round(r2_reduced, 4),
        'delta_r_squared': round(delta_r2, 4),
        'interaction_significant': bool(interaction_significant),
        'simple_slopes': simple_slopes,
        'interaction_plot_b64': plot_b64,
    }


def _build_interaction_plot(x, y, x_mean, w_mean, params, w_is_categorical, w_std):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    const, b1, b2, b3 = (float(p) for p in params[:4])
    x_min, x_max = float(np.min(x)), float(np.max(x))
    x_range = np.linspace(x_min, x_max, 50)

    if w_is_categorical:
        w_levels = [(gettext('W = 0'), 0.0), (gettext('W = 1'), 1.0)]
    else:
        w_levels = [
            (gettext('Düşük W (Ort. − 1SS)'), w_mean - w_std),
            (gettext('Orta W (Ortalama)'), w_mean),
            (gettext('Yüksek W (Ort. + 1SS)'), w_mean + w_std),
        ]

    fig, ax = plt.subplots(figsize=(6, 4.2), dpi=110)
    colors = ['#f87171', '#60a5fa', '#4ade80']
    for i, (label, w_val) in enumerate(w_levels):
        wc_val = w_val - w_mean
        y_hat = const + b1 * (x_range - x_mean) + b2 * wc_val + b3 * (x_range - x_mean) * wc_val
        ax.plot(x_range, y_hat, label=label, color=colors[i % len(colors)], linewidth=2)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.2)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('ascii')


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
    BLUE = colors.HexColor('#1e3a5f')
    title_s = ParagraphStyle('T', parent=styles['Heading1'], fontSize=16, spaceAfter=6, fontName='DejaVuSans')
    h2_s = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, spaceAfter=4, fontName='DejaVuSans')
    norm_s = ParagraphStyle('N', parent=styles['Normal'], fontName='DejaVuSans', fontSize=9)

    def p_str(v):
        return '< .001' if v < 0.001 else f'{v:.4f}'

    story = []
    story.append(Paragraph(gettext('Düzenleyici Değişken (Moderation) Analizi Raporu'), title_s))
    story.append(Paragraph(gettext('Dosya: %(filename)s') % {'filename': filename}, norm_s))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph(gettext('Model Özeti'), h2_s))
    summary_rows = [
        [gettext('Bağımsız Değişken (X)'), result['x_col']],
        [gettext('Düzenleyici Değişken (W)'), result['w_col']],
        [gettext('Bağımlı Değişken (Y)'), result['y_col']],
        ['N', str(result['n'])],
        ['R² ' + gettext('(tam model)'), f"{result['r_squared_full']:.4f}"],
        ['ΔR² ' + gettext('(etkileşim katkısı)'), f"{result['delta_r_squared']:.4f}"],
        [gettext('Sonuç'), gettext('Düzenleyici Etki Anlamlı') if result['interaction_significant'] else gettext('Düzenleyici Etki Yok')],
    ]
    sum_tbl = Table(summary_rows, colWidths=[6*cm, 10*cm])
    sig_bg = colors.HexColor('#d4edda') if result['interaction_significant'] else colors.HexColor('#f8d7da')
    sum_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), BLUE),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('BACKGROUND', (1, -1), (1, -1), sig_bg),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (1, 0), (1, -2), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(sum_tbl)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(gettext('Katsayılar'), h2_s))
    coef_rows = [
        [gettext('Terim'), gettext('Katsayı'), 'SE', 'p'],
        [gettext('b1 (X ana etkisi)'), f"{result['b1']['coef']:.4f}", f"{result['b1']['se']:.4f}", p_str(result['b1']['p'])],
        [gettext('b2 (W ana etkisi)'), f"{result['b2']['coef']:.4f}", f"{result['b2']['se']:.4f}", p_str(result['b2']['p'])],
        [gettext('b3 (Etkileşim: X×W)'), f"{result['b3']['coef']:.4f}", f"{result['b3']['se']:.4f}", p_str(result['b3']['p'])],
    ]
    coef_tbl = Table(coef_rows, colWidths=[7*cm, 3*cm, 3*cm, 3*cm])
    coef_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(coef_tbl)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(gettext('Basit Eğimler (Simple Slopes)'), h2_s))
    slope_rows = [[gettext('Düzey'), 'W', gettext('X Etkisi'), 'SE', 't', 'p']]
    for s in result['simple_slopes']:
        slope_rows.append([s['label'], f"{s['w_value']:.3f}", f"{s['effect']:.4f}", f"{s['se']:.4f}", f"{s['t']:.3f}", p_str(s['p'])])
    slope_tbl = Table(slope_rows, colWidths=[5.5*cm, 2*cm, 2.8*cm, 2.3*cm, 1.9*cm, 2.3*cm])
    slope_style = [
        ('BACKGROUND', (0, 0), (-1, 0), BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]
    for i, s in enumerate(result['simple_slopes'], start=1):
        if s['significant']:
            slope_style.append(('BACKGROUND', (5, i), (5, i), colors.HexColor('#d4edda')))
    slope_tbl.setStyle(TableStyle(slope_style))
    story.append(slope_tbl)
    story.append(Spacer(1, 0.5*cm))

    if result.get('interaction_plot_b64'):
        story.append(Paragraph(gettext('Etkileşim Grafiği'), h2_s))
        img_data = base64.b64decode(result['interaction_plot_b64'])
        img_buf = io.BytesIO(img_data)
        story.append(Image(img_buf, width=13*cm, height=9.1*cm))
        story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph(gettext('APA Formatında Raporlama'), h2_s))
    if result['interaction_significant']:
        apa_text = gettext(
            '{x} değişkeninin {y} üzerindeki etkisinin {w} tarafından düzenlendiği '
            'bulunmuştur, b = {b3}, SE = {se3}, p {p3}. Etkileşim terimi modele '
            'ek olarak ΔR² = {dr2} varyans açıklamıştır.'
        ).format(x=result['x_col'], y=result['y_col'], w=result['w_col'],
                 b3=f"{result['b3']['coef']:.3f}", se3=f"{result['b3']['se']:.3f}",
                 p3=p_str(result['b3']['p']), dr2=f"{result['delta_r_squared']:.4f}")
    else:
        apa_text = gettext(
            '{x} değişkeninin {y} üzerindeki etkisinin {w} tarafından anlamlı '
            'şekilde düzenlenmediği bulunmuştur, b = {b3}, SE = {se3}, p {p3}.'
        ).format(x=result['x_col'], y=result['y_col'], w=result['w_col'],
                 b3=f"{result['b3']['coef']:.3f}", se3=f"{result['b3']['se']:.3f}",
                 p3=p_str(result['b3']['p']))
    apa_tbl = Table([[Paragraph(apa_text, norm_s)]], colWidths=[16*cm])
    apa_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f4ff')),
        ('BOX', (0, 0), (-1, -1), 1, BLUE),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(apa_tbl)
    append_ai_comment(story, result, norm_s, '#f0f4ff', BLUE)

    doc.build(story)
    return buf.getvalue()
