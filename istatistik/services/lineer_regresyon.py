"""
Çoklu Doğrusal Regresyon Analizi (OLS)
Statsmodels tabanlı; standardize beta, VIF, güven aralıkları dahil.
"""
import io
import numpy as np


def analyze(df, dep_col: str, indep_cols: list) -> dict:
    import pandas as pd
    import statsmodels.api as sm
    from statsmodels.stats.outliers_influence import variance_inflation_factor

    if dep_col not in df.columns:
        raise ValueError(f'"{dep_col}" bağımlı değişken sütunu bulunamadı.')
    missing = [c for c in indep_cols if c not in df.columns]
    if missing:
        raise ValueError(f'Şu sütunlar bulunamadı: {", ".join(missing)}')
    if not indep_cols:
        raise ValueError('En az 1 bağımsız değişken seçilmelidir.')
    if dep_col in indep_cols:
        raise ValueError('Bağımlı değişken, bağımsız değişkenler arasında olamaz.')

    sub = df[[dep_col] + list(indep_cols)].dropna()
    n = len(sub)
    if n < len(indep_cols) + 3:
        raise ValueError(f'Yetersiz gözlem sayısı (n = {n}). '
                         f'En az {len(indep_cols) + 3} satır gereklidir.')

    try:
        y = sub[dep_col].astype(float).values
    except Exception:
        raise ValueError(f'"{dep_col}" sayısal bir değişken olmalıdır.')

    # Bağımsız değişkenler: kategorik → dummy
    X_df = pd.DataFrame(index=sub.index)
    predictor_names = []
    for col in indep_cols:
        series = sub[col]
        if series.dtype == object or series.nunique() <= 10:
            dummies = pd.get_dummies(series, prefix=col, drop_first=True, dtype=float)
            X_df = pd.concat([X_df, dummies], axis=1)
            predictor_names.extend(list(dummies.columns))
        else:
            X_df[col] = series.astype(float)
            predictor_names.append(col)

    if X_df.empty or X_df.shape[1] == 0:
        raise ValueError('Bağımsız değişkenler işlenemedi.')

    X_np = X_df.values.astype(float)
    p = X_np.shape[1]

    # OLS
    X_sm = sm.add_constant(X_np)
    try:
        model = sm.OLS(y, X_sm).fit()
    except Exception as e:
        raise ValueError(f'Model hesaplama hatası: {e}')

    # Standardize beta
    from sklearn.preprocessing import StandardScaler
    scaler_x = StandardScaler()
    scaler_y = StandardScaler()
    X_std = scaler_x.fit_transform(X_np)
    y_std = scaler_y.fit_transform(y.reshape(-1, 1)).ravel()
    model_std = sm.OLS(y_std, sm.add_constant(X_std)).fit()
    betas = model_std.params[1:]

    # VIF
    try:
        vifs = [variance_inflation_factor(X_sm.astype(float), i + 1) for i in range(p)]
    except Exception:
        vifs = [None] * p

    # Katsayılar
    ci = np.array(model.conf_int())
    coefficients = [{
        'name': 'Sabit',
        'B': round(float(model.params[0]), 4),
        'beta': '—',
        'se': round(float(model.bse[0]), 4),
        't': round(float(model.tvalues[0]), 3),
        'p': round(float(model.pvalues[0]), 4),
        'ci_low': round(float(ci[0, 0]), 4),
        'ci_high': round(float(ci[0, 1]), 4),
        'vif': '—',
        'significant': bool(model.pvalues[0] < 0.05),
    }]
    for i, name in enumerate(predictor_names):
        vif_val = vifs[i]
        coefficients.append({
            'name': name,
            'B': round(float(model.params[i + 1]), 4),
            'beta': round(float(betas[i]), 4),
            'se': round(float(model.bse[i + 1]), 4),
            't': round(float(model.tvalues[i + 1]), 3),
            'p': round(float(model.pvalues[i + 1]), 4),
            'ci_low': round(float(ci[i + 1, 0]), 4),
            'ci_high': round(float(ci[i + 1, 1]), 4),
            'vif': (round(float(vif_val), 3) if (vif_val is not None and not np.isnan(vif_val) and not np.isinf(vif_val)) else '—'),
            'significant': bool(model.pvalues[i + 1] < 0.05),
        })

    sig_predictors = [c['name'] for c in coefficients[1:] if c['significant']]

    return {
        'dep_col': dep_col,
        'indep_cols': list(indep_cols),
        'predictor_names': predictor_names,
        'n': n,
        'p': p,
        'r_squared': round(float(model.rsquared), 4),
        'adj_r_squared': round(float(model.rsquared_adj), 4),
        'f_stat': round(float(model.fvalue), 3),
        'f_p': round(float(model.f_pvalue), 4),
        'df_model': int(model.df_model),
        'df_resid': int(model.df_resid),
        'significant': bool(model.f_pvalue < 0.05),
        'coefficients': coefficients,
        'sig_predictors': sig_predictors,
    }


def build_pdf(result: dict, filename: str, df=None) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from .pdf_fonts import register_fonts
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
    story.append(Paragraph('Çoklu Doğrusal Regresyon Raporu', title_s))
    story.append(Paragraph(f'Dosya: {filename}', norm_s))
    story.append(Spacer(1, 0.4*cm))

    # Model özeti
    story.append(Paragraph('Model Özeti', h2_s))
    sig = result['significant']
    p_str = '< .001' if result['f_p'] < 0.001 else f"{result['f_p']:.3f}"
    summary_rows = [
        ['Bağımlı Değişken', result['dep_col']],
        ['Bağımsız Değişkenler', ', '.join(result['indep_cols'])],
        ['N', str(result['n'])],
        ['R²', f"{result['r_squared']:.4f}"],
        ['Düzeltilmiş R²', f"{result['adj_r_squared']:.4f}"],
        ['F istatistiği', f"F({result['df_model']}, {result['df_resid']}) = {result['f_stat']:.3f}"],
        ['p-değeri', p_str],
        ['Sonuç', 'Anlamlı (p < .05)' if sig else 'Anlamlı değil (p ≥ .05)'],
    ]
    sum_tbl = Table(summary_rows, colWidths=[6*cm, 10*cm])
    sum_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), BLUE),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('BACKGROUND', (1, -1), (1, -1),
         colors.HexColor('#d4edda') if sig else colors.HexColor('#f8d7da')),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (1, 0), (1, -2), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(sum_tbl)
    story.append(Spacer(1, 0.5*cm))

    # Katsayılar tablosu
    story.append(Paragraph('Katsayılar', h2_s))
    coef_header = ['Değişken', 'B', 'β', 'SE', 't', 'p', '%95 GA Alt', '%95 GA Üst', 'VIF']
    coef_rows = [coef_header]
    for c in result['coefficients']:
        beta_str = str(c['beta']) if c['beta'] == '—' else f"{c['beta']:.4f}"
        vif_str = str(c['vif']) if c['vif'] == '—' else f"{c['vif']:.3f}"
        p_c = c['p']
        p_c_str = '< .001' if p_c < 0.001 else f"{p_c:.4f}"
        coef_rows.append([
            c['name'], f"{c['B']:.4f}", beta_str, f"{c['se']:.4f}",
            f"{c['t']:.3f}", p_c_str,
            f"{c['ci_low']:.4f}", f"{c['ci_high']:.4f}", vif_str,
        ])

    col_w = [3.5*cm, 1.8*cm, 1.8*cm, 1.8*cm, 1.8*cm, 1.8*cm, 2*cm, 2*cm, 1.5*cm]
    coef_tbl = Table(coef_rows, colWidths=col_w)
    coef_style = [
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
    for i, c in enumerate(result['coefficients'], start=1):
        if c['significant'] and c['name'] != 'Sabit':
            coef_style.append(('BACKGROUND', (5, i), (5, i), colors.HexColor('#d4edda')))
    coef_tbl.setStyle(TableStyle(coef_style))
    story.append(coef_tbl)

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        '<font color="#666666" size="8">Not: VIF &gt; 10 çoklu bağlantı sorununa işaret edebilir. '
        'β = standardize edilmiş katsayı (yordayıcılar arası etki büyüklüğü karşılaştırması için kullanılır).</font>',
        ParagraphStyle('note', parent=styles['Normal'], fontName='DejaVuSans', fontSize=8)
    ))

    # APA
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph('Tezinde Nasıl Raporlarsın?', h2_s))
    apa_text = (f"Çoklu doğrusal regresyon analizi sonucunda kurulan model istatistiksel açıdan "
                f"{'anlamlı bulunmuştur' if sig else 'anlamlı bulunmamıştır'}, "
                f"F({result['df_model']}, {result['df_resid']}) = {result['f_stat']:.3f}, "
                f"p = {p_str}, R² = {result['r_squared']:.4f}, "
                f"düzeltilmiş R² = {result['adj_r_squared']:.4f}.")
    if result['sig_predictors']:
        apa_text += f" Anlamlı yordayıcılar: {', '.join(result['sig_predictors'])}."
    apa_tbl = Table([[Paragraph(apa_text, norm_s)]], colWidths=[16*cm])
    apa_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f4ff')),
        ('BOX', (0, 0), (-1, -1), 1, BLUE),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(apa_tbl)

    doc.build(story)
    return buf.getvalue()
