"""
Basit Path Analizi — Çoklu Paralel Aracı Değişken Modeli (Hayes PROCESS
Model 4'ün çoklu aracı versiyonu). X (bağımsız) → M1, M2, ... Mk (paralel
aracı değişkenler, birbirinden bağımsız, aynı anda modellenir) → Y (bağımlı).
mediation.py (tek aracı değişkenli) ile aynı desen: statsmodels OLS +
bootstrap %95 güven aralığı (birincil, SPSS Process/Hayes ile eşleşir).
"""
import io
from django.utils.translation import gettext
import numpy as np


def _fit_ols(y, X):
    import statsmodels.api as sm
    X_sm = sm.add_constant(X, has_constant='add')
    return sm.OLS(y, X_sm).fit()


def analyze(df, x_col: str, m_cols: list, y_col: str, n_boot: int = 5000) -> dict:
    import pandas as pd

    if not x_col:
        raise ValueError(gettext('Bağımsız değişken (X) seçilmelidir.'))
    if not y_col:
        raise ValueError(gettext('Bağımlı değişken (Y) seçilmelidir.'))
    m_cols = list(m_cols or [])
    if len(m_cols) < 2:
        raise ValueError(gettext(
            'Basit path analizi için en az 2 aracı değişken seçilmelidir '
            '(tek aracı değişken için Aracılık Analizi (Mediation) aracını kullanın).'
        ))
    if len(m_cols) > 5:
        raise ValueError(gettext('En fazla 5 aracı değişken desteklenmektedir.'))

    all_cols = [x_col] + m_cols + [y_col]
    if len(set(all_cols)) != len(all_cols):
        raise ValueError(gettext('Bağımsız, aracı ve bağımlı değişkenler birbirinden farklı olmalıdır.'))
    missing = [c for c in all_cols if c not in df.columns]
    if missing:
        raise ValueError(gettext('Şu sütunlar bulunamadı: %(v)s') % {'v': ', '.join(missing)})

    sub = df[all_cols].dropna()
    n = len(sub)
    min_n = max(30, 10 * (len(m_cols) + 2))
    if n < min_n:
        raise ValueError(gettext(
            'Yetersiz gözlem sayısı (n = %(n)s). %(k)s aracı değişkenli path analizi için '
            'en az %(min_n)s satır gereklidir.'
        ) % {'n': n, 'k': len(m_cols), 'min_n': min_n})

    try:
        m_matrix = sub[m_cols].astype(float).values
        y = sub[y_col].astype(float).values
    except Exception:
        raise ValueError(gettext('Aracı değişkenler (M) ve bağımlı değişken (Y) sayısal olmalıdır.'))

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

    k = len(m_cols)
    x_2d = x.reshape(-1, 1)

    # c yolu: Y ~ X (toplam etki)
    model_c = _fit_ols(y, x_2d)
    c = float(model_c.params[1])
    c_se = float(model_c.bse[1])
    c_p = float(model_c.pvalues[1])

    # a_i yolları: M_i ~ X (her aracı değişken için ayrı model)
    a_paths = []
    for i in range(k):
        model_a = _fit_ols(m_matrix[:, i], x_2d)
        a_paths.append({
            'coef': float(model_a.params[1]),
            'se': float(model_a.bse[1]),
            'p': float(model_a.pvalues[1]),
        })

    # b_i yolları + c' (direkt etki): Y ~ X + M1 + ... + Mk (hepsi aynı anda)
    full_X = np.column_stack([x, m_matrix])
    model_full = _fit_ols(y, full_X)
    c_prime = float(model_full.params[1])
    c_prime_se = float(model_full.bse[1])
    c_prime_p = float(model_full.pvalues[1])
    b_paths = []
    for i in range(k):
        b_paths.append({
            'coef': float(model_full.params[2 + i]),
            'se': float(model_full.bse[2 + i]),
            'p': float(model_full.pvalues[2 + i]),
        })
    r_squared_full = float(model_full.rsquared)

    indirect_effects = [a_paths[i]['coef'] * b_paths[i]['coef'] for i in range(k)]
    total_indirect = float(sum(indirect_effects))

    # Bootstrap güven aralığı (percentile) — her aracı değişkenin dolaylı etkisi + toplam
    rng = np.random.default_rng(42)
    boot_indirect = np.empty((n_boot, k))
    boot_total = np.empty(n_boot)
    idx = np.arange(n)
    valid_count = 0
    for it in range(n_boot):
        resample = rng.choice(idx, size=n, replace=True)
        xb = x[resample]
        mb = m_matrix[resample, :]
        yb = y[resample]
        try:
            a_b = np.array([_fit_ols(mb[:, i], xb.reshape(-1, 1)).params[1] for i in range(k)])
            full_b = _fit_ols(yb, np.column_stack([xb, mb]))
            b_b = np.array([full_b.params[2 + i] for i in range(k)])
        except Exception:
            boot_indirect[it, :] = np.nan
            boot_total[it] = np.nan
            continue
        ind_b = a_b * b_b
        boot_indirect[it, :] = ind_b
        boot_total[it] = ind_b.sum()
        valid_count += 1

    mediator_results = []
    for i, col in enumerate(m_cols):
        valid = boot_indirect[~np.isnan(boot_indirect[:, i]), i]
        ci_low = float(np.percentile(valid, 2.5))
        ci_high = float(np.percentile(valid, 97.5))
        significant = not (ci_low <= 0 <= ci_high)
        mediator_results.append({
            'name': col,
            'a': {'coef': round(a_paths[i]['coef'], 4), 'se': round(a_paths[i]['se'], 4),
                  'p': round(a_paths[i]['p'], 4), 'significant': bool(a_paths[i]['p'] < 0.05)},
            'b': {'coef': round(b_paths[i]['coef'], 4), 'se': round(b_paths[i]['se'], 4),
                  'p': round(b_paths[i]['p'], 4), 'significant': bool(b_paths[i]['p'] < 0.05)},
            'indirect_effect': round(indirect_effects[i], 4),
            'bootstrap_ci_low': round(ci_low, 4),
            'bootstrap_ci_high': round(ci_high, 4),
            'significant': bool(significant),
        })

    valid_total = boot_total[~np.isnan(boot_total)]
    total_ci_low = float(np.percentile(valid_total, 2.5))
    total_ci_high = float(np.percentile(valid_total, 97.5))
    total_significant = not (total_ci_low <= 0 <= total_ci_high)

    c_prime_significant = c_prime_p < 0.05
    if total_significant and c_prime_significant:
        mediation_type = 'partial'
    elif total_significant and not c_prime_significant:
        mediation_type = 'full'
    else:
        mediation_type = 'none'

    return {
        'x_col': x_col,
        'm_cols': m_cols,
        'y_col': y_col,
        'x_is_categorical': x_is_categorical,
        'n': n,
        'n_boot': valid_count,
        'c': {'coef': round(c, 4), 'se': round(c_se, 4), 'p': round(c_p, 4), 'significant': bool(c_p < 0.05)},
        'c_prime': {'coef': round(c_prime, 4), 'se': round(c_prime_se, 4), 'p': round(c_prime_p, 4),
                    'significant': bool(c_prime_significant)},
        'r_squared_full': round(r_squared_full, 4),
        'mediators': mediator_results,
        'total_indirect_effect': round(total_indirect, 4),
        'total_bootstrap_ci_low': round(total_ci_low, 4),
        'total_bootstrap_ci_high': round(total_ci_high, 4),
        'total_significant': bool(total_significant),
        'mediation_type': mediation_type,
        'conclusion': _conclusion(mediation_type, mediator_results, x_col, y_col),
    }


_MEDIATION_LABELS = {
    'full': gettext('Tam Aracılık'),
    'partial': gettext('Kısmi Aracılık'),
    'none': gettext('Aracılık Etkisi Yok'),
}


def _conclusion(mediation_type, mediator_results, x_col, y_col) -> str:
    sig_mediators = [m['name'] for m in mediator_results if m['significant']]
    label = _MEDIATION_LABELS[mediation_type]
    if not sig_mediators:
        return gettext(
            'Seçilen aracı değişkenlerin hiçbiri %(x)s ile %(y)s arasındaki ilişkide anlamlı bir '
            'dolaylı etki göstermemiştir (%(label)s).'
        ) % {'x': x_col, 'y': y_col, 'label': label}
    return gettext(
        '%(x)s ile %(y)s arasındaki ilişkide şu aracı değişken(ler) anlamlı dolaylı etki göstermiştir: '
        '%(mediators)s (%(label)s).'
    ) % {'x': x_col, 'y': y_col, 'mediators': ', '.join(sig_mediators), 'label': label}


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
    PURPLE = colors.HexColor('#7c3aed')
    title_s = ParagraphStyle('T', parent=styles['Heading1'], fontSize=16, spaceAfter=6, fontName='DejaVuSans')
    h2_s = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, spaceAfter=4, fontName='DejaVuSans')
    norm_s = ParagraphStyle('N', parent=styles['Normal'], fontName='DejaVuSans', fontSize=9)

    def p_str(v):
        return '< .001' if v < 0.001 else f'{v:.4f}'

    story = []
    story.append(Paragraph(gettext('Basit Path Analizi Raporu (Çoklu Paralel Aracı Değişken)'), title_s))
    story.append(Paragraph(gettext('Dosya: %(filename)s') % {'filename': filename}, norm_s))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph(gettext('Model Özeti'), h2_s))
    summary_rows = [
        [gettext('Bağımsız Değişken (X)'), result['x_col']],
        [gettext('Aracı Değişkenler (M)'), ', '.join(result['m_cols'])],
        [gettext('Bağımlı Değişken (Y)'), result['y_col']],
        ['N', str(result['n'])],
        ['R² ' + gettext('(tam model)'), f"{result['r_squared_full']:.4f}"],
        [gettext('Sonuç'), _MEDIATION_LABELS[result['mediation_type']]],
    ]
    sum_tbl = Table(summary_rows, colWidths=[6*cm, 10*cm])
    sig_bg = colors.HexColor('#d4edda') if result['mediation_type'] != 'none' else colors.HexColor('#f8d7da')
    sum_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), PURPLE),
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

    story.append(Paragraph(gettext('Toplam ve Direkt Etki'), h2_s))
    ce_rows = [
        [gettext('c (Toplam Etki: X→Y)'), f"{result['c']['coef']:.4f}", f"{result['c']['se']:.4f}", p_str(result['c']['p'])],
        [gettext("c' (Direkt Etki: X→Y, aracılar kontrollü)"), f"{result['c_prime']['coef']:.4f}", f"{result['c_prime']['se']:.4f}", p_str(result['c_prime']['p'])],
    ]
    ce_tbl = Table([[gettext('Yol'), gettext('Katsayı'), 'SE', 'p']] + ce_rows, colWidths=[7*cm, 3*cm, 3*cm, 3*cm])
    ce_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PURPLE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(ce_tbl)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(gettext('Aracı Değişken Yolları (a × b)'), h2_s))
    med_rows = [[gettext('Aracı (M)'), 'a (X→M)', 'b (M→Y)', gettext('Dolaylı Etki'), '%95 GA', gettext('Anlamlı')]]
    for m in result['mediators']:
        med_rows.append([
            m['name'], f"{m['a']['coef']:.4f}", f"{m['b']['coef']:.4f}", f"{m['indirect_effect']:.4f}",
            f"[{m['bootstrap_ci_low']:.4f}, {m['bootstrap_ci_high']:.4f}]",
            gettext('Evet') if m['significant'] else gettext('Hayır'),
        ])
    med_tbl = Table(med_rows, colWidths=[3.5*cm, 2.3*cm, 2.3*cm, 2.6*cm, 4*cm, 1.8*cm])
    med_style = [
        ('BACKGROUND', (0, 0), (-1, 0), PURPLE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]
    for i, m in enumerate(result['mediators'], start=1):
        if m['significant']:
            med_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#d4edda')))
    med_tbl.setStyle(TableStyle(med_style))
    story.append(med_tbl)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(gettext('Toplam Dolaylı Etki'), h2_s))
    total_rows = [
        [gettext('Toplam Dolaylı Etki (Σ a×b)'), f"{result['total_indirect_effect']:.4f}"],
        [gettext('Bootstrap %95 Güven Aralığı'), f"[{result['total_bootstrap_ci_low']:.4f}, {result['total_bootstrap_ci_high']:.4f}]"],
    ]
    total_tbl = Table(total_rows, colWidths=[7*cm, 9*cm])
    total_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), PURPLE),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(total_tbl)
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        '<font color="#666666" size="8">' + gettext(
            'Not: Bootstrap güven aralığı %(n_boot)s yeniden örneklemeye dayanır; '
            'aralık sıfırı kapsamıyorsa dolaylı etki istatistiksel olarak anlamlıdır. '
            'Tüm aracı değişkenler aynı anda (paralel) modellenmiştir.') % {'n_boot': result['n_boot']} + '</font>',
        ParagraphStyle('note', parent=styles['Normal'], fontName='DejaVuSans', fontSize=8)
    ))

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(gettext('Yorum'), h2_s))
    story.append(Paragraph(result['conclusion'], norm_s))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(gettext('APA Formatında Raporlama'), h2_s))
    ci_text = f"[{result['total_bootstrap_ci_low']:.3f}, {result['total_bootstrap_ci_high']:.3f}]"
    apa_text = gettext(
        'Çoklu paralel aracı değişkenli path analizi sonucunda toplam dolaylı etki '
        '(Σ a×b = {total}) bootstrap %95 güven aralığında {ci} olarak bulunmuştur. {concl}'
    ).format(total=f"{result['total_indirect_effect']:.3f}", ci=ci_text, concl=result['conclusion'])
    apa_tbl = Table([[Paragraph(apa_text, norm_s)]], colWidths=[16*cm])
    apa_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f3ff')),
        ('BOX', (0, 0), (-1, -1), 1, PURPLE),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(apa_tbl)
    append_ai_comment(story, result, norm_s, '#f5f3ff', PURPLE)

    doc.build(story)
    return buf.getvalue()
