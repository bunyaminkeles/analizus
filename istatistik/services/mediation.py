"""
Aracılık (Mediation) Analizi — basit, tek aracı değişkenli model.
X (bağımsız) → M (aracı) → Y (bağımlı). Statsmodels OLS tabanlı (lineer_regresyon.py
ile aynı desen); dolaylı etkinin (a×b) anlamlılığı bootstrap güven aralığı
(birincil, SPSS Process/Hayes ile eşleşir) + Sobel testi (ek) ile raporlanır.
"""
import io
from django.utils.translation import gettext
import numpy as np


def _fit_ols(y, X):
    import statsmodels.api as sm
    X_sm = sm.add_constant(X, has_constant='add')
    return sm.OLS(y, X_sm).fit()


def analyze(df, x_col: str, m_col: str, y_col: str, n_boot: int = 5000) -> dict:
    import pandas as pd

    for col, label in ((x_col, gettext('Bağımsız değişken (X)')), (m_col, gettext('Aracı değişken (M)')), (y_col, gettext('Bağımlı değişken (Y)'))):
        if not col:
            raise ValueError(gettext('%(label)s seçilmelidir.') % {'label': label})
        if col not in df.columns:
            raise ValueError(gettext('"%(col)s" sütunu bulunamadı.') % {'col': col})
    if len({x_col, m_col, y_col}) < 3:
        raise ValueError(gettext('Bağımsız, aracı ve bağımlı değişkenler birbirinden farklı olmalıdır.'))

    sub = df[[x_col, m_col, y_col]].dropna()
    n = len(sub)
    if n < 20:
        raise ValueError(gettext('Yetersiz gözlem sayısı (n = %(n)s). Aracılık analizi için en az 20 satır gereklidir.') % {'n': n})

    try:
        m = sub[m_col].astype(float).values
        y = sub[y_col].astype(float).values
    except Exception:
        raise ValueError(gettext('Aracı (M) ve bağımlı (Y) değişkenler sayısal olmalıdır.'))

    x_series = sub[x_col]
    if x_series.dtype == object or x_series.nunique() <= 10:
        if x_series.nunique() < 2:
            raise ValueError(gettext('Bağımsız değişkende (X) en az 2 farklı değer olmalıdır.'))
        dummies = pd.get_dummies(x_series, drop_first=True, dtype=float)
        if dummies.shape[1] != 1:
            raise ValueError(gettext('Bağımsız değişken (X) sayısal veya yalnızca 2 kategorili olmalıdır.'))
        x = dummies.iloc[:, 0].values
        x_is_categorical = True
    else:
        try:
            x = x_series.astype(float).values
        except Exception:
            raise ValueError(gettext('"%(col)s" sayısal bir değişken olmalıdır.') % {'col': x_col})
        x_is_categorical = False

    x_col2 = x.reshape(-1, 1)

    # c yolu: Y ~ X (toplam etki)
    model_c = _fit_ols(y, x_col2)
    c = float(model_c.params[1])
    c_se = float(model_c.bse[1])
    c_p = float(model_c.pvalues[1])

    # a yolu: M ~ X
    model_a = _fit_ols(m, x_col2)
    a = float(model_a.params[1])
    a_se = float(model_a.bse[1])
    a_p = float(model_a.pvalues[1])

    # b yolu + c' (direkt etki): Y ~ X + M
    xm = np.column_stack([x, m])
    model_full = _fit_ols(y, xm)
    c_prime = float(model_full.params[1])
    c_prime_se = float(model_full.bse[1])
    c_prime_p = float(model_full.pvalues[1])
    b = float(model_full.params[2])
    b_se = float(model_full.bse[2])
    b_p = float(model_full.pvalues[2])

    indirect = a * b

    # Sobel testi
    sobel_se = float(np.sqrt(b**2 * a_se**2 + a**2 * b_se**2))
    sobel_z = indirect / sobel_se if sobel_se > 0 else 0.0
    from scipy.stats import norm
    sobel_p = float(2 * (1 - norm.cdf(abs(sobel_z))))

    # Bootstrap güven aralığı (percentile)
    rng = np.random.default_rng(42)
    boot_indirect = np.empty(n_boot)
    idx = np.arange(n)
    for i in range(n_boot):
        resample = rng.choice(idx, size=n, replace=True)
        xb, mb, yb = x[resample], m[resample], y[resample]
        try:
            a_b = _fit_ols(mb, xb.reshape(-1, 1)).params[1]
            full_b = _fit_ols(yb, np.column_stack([xb, mb]))
            b_b = full_b.params[2]
        except Exception:
            boot_indirect[i] = np.nan
            continue
        boot_indirect[i] = a_b * b_b
    boot_indirect = boot_indirect[~np.isnan(boot_indirect)]
    ci_low = float(np.percentile(boot_indirect, 2.5))
    ci_high = float(np.percentile(boot_indirect, 97.5))
    indirect_significant = not (ci_low <= 0 <= ci_high)

    c_prime_significant = c_prime_p < 0.05
    if indirect_significant and c_prime_significant:
        mediation_type = 'partial'
    elif indirect_significant and not c_prime_significant:
        mediation_type = 'full'
    else:
        mediation_type = 'none'

    return {
        'x_col': x_col,
        'm_col': m_col,
        'y_col': y_col,
        'x_is_categorical': x_is_categorical,
        'n': n,
        'n_boot': int(len(boot_indirect)),
        'paths': {
            'c': {'coef': round(c, 4), 'se': round(c_se, 4), 'p': round(c_p, 4), 'significant': bool(c_p < 0.05)},
            'a': {'coef': round(a, 4), 'se': round(a_se, 4), 'p': round(a_p, 4), 'significant': bool(a_p < 0.05)},
            'b': {'coef': round(b, 4), 'se': round(b_se, 4), 'p': round(b_p, 4), 'significant': bool(b_p < 0.05)},
            'c_prime': {'coef': round(c_prime, 4), 'se': round(c_prime_se, 4), 'p': round(c_prime_p, 4), 'significant': bool(c_prime_significant)},
        },
        'indirect_effect': round(indirect, 4),
        'bootstrap_ci_low': round(ci_low, 4),
        'bootstrap_ci_high': round(ci_high, 4),
        'indirect_significant': bool(indirect_significant),
        'sobel_z': round(sobel_z, 3),
        'sobel_se': round(sobel_se, 4),
        'sobel_p': round(sobel_p, 4),
        'mediation_type': mediation_type,
    }


_MEDIATION_LABELS = {
    'full': gettext('Tam Aracılık'),
    'partial': gettext('Kısmi Aracılık'),
    'none': gettext('Aracılık Etkisi Yok'),
}


def build_pdf(result: dict, filename: str, df=None) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
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

    story = []
    story.append(Paragraph(gettext('Aracılık (Mediation) Analizi Raporu'), title_s))
    story.append(Paragraph(gettext('Dosya: %(filename)s') % {'filename': filename}, norm_s))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph(gettext('Model Özeti'), h2_s))
    summary_rows = [
        [gettext('Bağımsız Değişken (X)'), result['x_col']],
        [gettext('Aracı Değişken (M)'), result['m_col']],
        [gettext('Bağımlı Değişken (Y)'), result['y_col']],
        ['N', str(result['n'])],
        [gettext('Sonuç'), _MEDIATION_LABELS[result['mediation_type']]],
    ]
    sum_tbl = Table(summary_rows, colWidths=[6*cm, 10*cm])
    sig_bg = colors.HexColor('#d4edda') if result['mediation_type'] != 'none' else colors.HexColor('#f8d7da')
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

    story.append(Paragraph(gettext('Yol Katsayıları'), h2_s))
    p = result['paths']

    def p_str(v):
        return '< .001' if v < 0.001 else f'{v:.4f}'

    path_rows = [
        [gettext('Yol'), gettext('Katsayı'), 'SE', 'p'],
        [gettext('c (Toplam Etki: X→Y)'), f"{p['c']['coef']:.4f}", f"{p['c']['se']:.4f}", p_str(p['c']['p'])],
        [gettext('a (X→M)'), f"{p['a']['coef']:.4f}", f"{p['a']['se']:.4f}", p_str(p['a']['p'])],
        [gettext('b (M→Y)'), f"{p['b']['coef']:.4f}", f"{p['b']['se']:.4f}", p_str(p['b']['p'])],
        [gettext("c' (Direkt Etki: X→Y, M kontrollü)"), f"{p['c_prime']['coef']:.4f}", f"{p['c_prime']['se']:.4f}", p_str(p['c_prime']['p'])],
    ]
    path_tbl = Table(path_rows, colWidths=[7*cm, 3*cm, 3*cm, 3*cm])
    path_tbl.setStyle(TableStyle([
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
    story.append(path_tbl)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(gettext('Dolaylı Etki (a × b)'), h2_s))
    indirect_rows = [
        [gettext('Dolaylı Etki (a × b)'), f"{result['indirect_effect']:.4f}"],
        [gettext('Bootstrap %95 Güven Aralığı'), f"[{result['bootstrap_ci_low']:.4f}, {result['bootstrap_ci_high']:.4f}]"],
        [gettext('Sobel z'), f"{result['sobel_z']:.3f}"],
        [gettext('Sobel p'), p_str(result['sobel_p'])],
    ]
    indirect_tbl = Table(indirect_rows, colWidths=[7*cm, 9*cm])
    indirect_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), BLUE),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(indirect_tbl)
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        '<font color="#666666" size="8">' + gettext(
            'Not: Bootstrap güven aralığı %(n_boot)s yeniden örneklemeye dayanır; '
            'aralık sıfırı kapsamıyorsa dolaylı etki istatistiksel olarak anlamlıdır. '
            "Sobel testi klasik/ek bir doğrulama olarak sunulur.") % {'n_boot': result['n_boot']} + '</font>',
        ParagraphStyle('note', parent=styles['Normal'], fontName='DejaVuSans', fontSize=8)
    ))

    # APA
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(gettext('APA Formatında Raporlama'), h2_s))
    ci_text = f"[{result['bootstrap_ci_low']:.3f}, {result['bootstrap_ci_high']:.3f}]"
    if result['mediation_type'] == 'full':
        concl = gettext('{m} değişkeninin {x} ile {y} arasındaki ilişkide tam aracılık rolü üstlendiği görülmüştür ({x} değişkeninin doğrudan etkisi M kontrol edildiğinde anlamlılığını yitirmiştir, c\' = {cprime}, p {cprime_p}).').format(
            m=result['m_col'], x=result['x_col'], y=result['y_col'],
            cprime=f"{p['c_prime']['coef']:.3f}", cprime_p=p_str(p['c_prime']['p']))
    elif result['mediation_type'] == 'partial':
        concl = gettext('{m} değişkeninin {x} ile {y} arasındaki ilişkide kısmi aracılık rolü üstlendiği görülmüştür ({x} değişkeninin doğrudan etkisi M kontrol edildiğinde anlamlılığını korumuştur, c\' = {cprime}, p {cprime_p}).').format(
            m=result['m_col'], x=result['x_col'], y=result['y_col'],
            cprime=f"{p['c_prime']['coef']:.3f}", cprime_p=p_str(p['c_prime']['p']))
    else:
        concl = gettext('{m} değişkeni, {x} ile {y} arasındaki ilişkide anlamlı bir aracılık etkisi göstermemiştir.').format(
            m=result['m_col'], x=result['x_col'], y=result['y_col'])
    apa_text = gettext(
        'Aracılık analizi sonucunda dolaylı etki (a×b = {ind}) bootstrap %95 güven '
        'aralığında {ci} olarak bulunmuştur (Sobel z = {z}, p {sp}). {concl}'
    ).format(ind=f"{result['indirect_effect']:.3f}", ci=ci_text, z=f"{result['sobel_z']:.3f}",
             sp=p_str(result['sobel_p']), concl=concl)
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
