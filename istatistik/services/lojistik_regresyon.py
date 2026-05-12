"""
Lojistik Regresyon Analizi (Binary)
Statsmodels Logit; Wald testi, Odds Ratio, Nagelkerke R², sınıflandırma tablosu.
"""
import io
import numpy as np


def analyze(df, dep_col: str, indep_cols: list) -> dict:
    import pandas as pd
    import statsmodels.api as sm
    from scipy import stats

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

    dep_series = sub[dep_col]
    unique_vals = dep_series.unique()
    if len(unique_vals) != 2:
        raise ValueError(f'Lojistik regresyon için bağımlı değişkenin tam 2 kategorisi olmalıdır. '
                         f'"{dep_col}" sütununda {len(unique_vals)} farklı değer bulundu.')

    if n < len(indep_cols) + 5:
        raise ValueError(f'Yetersiz gözlem sayısı (n = {n}). '
                         f'En az {len(indep_cols) + 5} satır gereklidir.')

    sorted_vals = sorted(unique_vals, key=str)
    cat0, cat1 = str(sorted_vals[0]), str(sorted_vals[1])
    y = (dep_series == sorted_vals[1]).astype(int).values

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
    X_sm = sm.add_constant(X_np)

    try:
        model = sm.Logit(y, X_sm).fit(maxiter=200, disp=False)
    except Exception as e:
        raise ValueError(f'Model yakınsama hatası: {e}')

    # Model fit
    llf = float(model.llf)
    ll0 = float(model.llnull)
    chi2_stat = -2 * (ll0 - llf)
    chi2_df = int(model.df_model)
    chi2_p = float(stats.chi2.sf(chi2_stat, chi2_df))

    cox_snell = 1 - np.exp((2 / n) * (ll0 - llf))
    max_cox_snell = 1 - np.exp((2 / n) * ll0)
    nagelkerke = float(cox_snell / max_cox_snell) if max_cox_snell > 0 else 0.0

    # Katsayılar
    ci = model.conf_int()
    coefficients = [{
        'name': 'Sabit',
        'B': round(float(model.params[0]), 4),
        'se': round(float(model.bse[0]), 4),
        'wald': round(float(model.tvalues[0] ** 2), 3),
        'p': round(float(model.pvalues[0]), 4),
        'exp_b': round(float(np.exp(model.params[0])), 4),
        'ci_low_or': round(float(np.exp(ci.iloc[0, 0])), 4),
        'ci_high_or': round(float(np.exp(ci.iloc[0, 1])), 4),
        'significant': bool(model.pvalues[0] < 0.05),
    }]
    for i, name in enumerate(predictor_names):
        coefficients.append({
            'name': name,
            'B': round(float(model.params[i + 1]), 4),
            'se': round(float(model.bse[i + 1]), 4),
            'wald': round(float(model.tvalues[i + 1] ** 2), 3),
            'p': round(float(model.pvalues[i + 1]), 4),
            'exp_b': round(float(np.exp(model.params[i + 1])), 4),
            'ci_low_or': round(float(np.exp(ci.iloc[i + 1, 0])), 4),
            'ci_high_or': round(float(np.exp(ci.iloc[i + 1, 1])), 4),
            'significant': bool(model.pvalues[i + 1] < 0.05),
        })

    # Sınıflandırma tablosu
    y_pred_prob = model.predict()
    y_pred = (y_pred_prob >= 0.5).astype(int)
    tp = int(((y == 1) & (y_pred == 1)).sum())
    tn = int(((y == 0) & (y_pred == 0)).sum())
    fp = int(((y == 0) & (y_pred == 1)).sum())
    fn = int(((y == 1) & (y_pred == 0)).sum())
    accuracy = round((tp + tn) / n * 100, 1)

    sig_predictors = [c['name'] for c in coefficients[1:] if c['significant']]

    return {
        'dep_col': dep_col,
        'indep_cols': list(indep_cols),
        'predictor_names': predictor_names,
        'cat0': cat0,
        'cat1': cat1,
        'n': n,
        'chi2': round(chi2_stat, 3),
        'chi2_df': chi2_df,
        'chi2_p': round(chi2_p, 4),
        'log_likelihood': round(llf, 3),
        'cox_snell_r2': round(float(cox_snell), 4),
        'nagelkerke_r2': round(float(nagelkerke), 4),
        'significant': bool(chi2_p < 0.05),
        'coefficients': coefficients,
        'sig_predictors': sig_predictors,
        'classification': {
            'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn,
            'accuracy': accuracy,
            'cat0': cat0, 'cat1': cat1,
        },
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
    TEAL = colors.HexColor('#065f46')
    title_s = ParagraphStyle('T', parent=styles['Heading1'], fontSize=16, spaceAfter=6, fontName='DejaVuSans')
    h2_s = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, spaceAfter=4, fontName='DejaVuSans')
    norm_s = ParagraphStyle('N', parent=styles['Normal'], fontName='DejaVuSans', fontSize=9)

    story = []
    story.append(Paragraph('Lojistik Regresyon Raporu', title_s))
    story.append(Paragraph(f'Dosya: {filename}', norm_s))
    story.append(Spacer(1, 0.4*cm))

    # Model özeti
    story.append(Paragraph('Model Özeti', h2_s))
    sig = result['significant']
    p_str = '< .001' if result['chi2_p'] < 0.001 else f"{result['chi2_p']:.3f}"
    summary_rows = [
        ['Bağımlı Değişken', result['dep_col']],
        ['Referans Kategori (0)', result['cat0']],
        ['Hedef Kategori (1)', result['cat1']],
        ['Bağımsız Değişkenler', ', '.join(result['indep_cols'])],
        ['N', str(result['n'])],
        ['-2 Log Likelihood', f"{result['log_likelihood']:.3f}"],
        ['Model χ²', f"χ²({result['chi2_df']}) = {result['chi2']:.3f}"],
        ['p-değeri (Model)', p_str],
        ['Cox & Snell R²', f"{result['cox_snell_r2']:.4f}"],
        ['Nagelkerke R²', f"{result['nagelkerke_r2']:.4f}"],
        ['Doğruluk', f"{result['classification']['accuracy']}%"],
        ['Sonuç', 'Anlamlı (p < .05)' if sig else 'Anlamlı değil (p ≥ .05)'],
    ]
    sum_tbl = Table(summary_rows, colWidths=[6*cm, 10*cm])
    sum_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), TEAL),
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

    # Katsayılar
    story.append(Paragraph('Değişkenlerin Denklemdeki Değerleri', h2_s))
    coef_header = ['Değişken', 'B', 'SE', 'Wald', 'p', 'Exp(B)', '%95 GA Alt', '%95 GA Üst']
    coef_rows = [coef_header]
    for c in result['coefficients']:
        p_c = c['p']
        p_c_str = '< .001' if p_c < 0.001 else f"{p_c:.4f}"
        coef_rows.append([
            c['name'], f"{c['B']:.4f}", f"{c['se']:.4f}",
            f"{c['wald']:.3f}", p_c_str,
            f"{c['exp_b']:.4f}", f"{c['ci_low_or']:.4f}", f"{c['ci_high_or']:.4f}",
        ])

    col_w = [3.5*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2.2*cm, 2.2*cm]
    coef_tbl = Table(coef_rows, colWidths=col_w)
    coef_style = [
        ('BACKGROUND', (0, 0), (-1, 0), TEAL),
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
            coef_style.append(('BACKGROUND', (4, i), (4, i), colors.HexColor('#d4edda')))
    coef_tbl.setStyle(TableStyle(coef_style))
    story.append(coef_tbl)

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        '<font color="#666666" size="8">Not: Exp(B) = Odds Ratio. '
        'Exp(B) &gt; 1 pozitif ilişki, Exp(B) &lt; 1 negatif ilişki anlamına gelir.</font>',
        ParagraphStyle('note', parent=styles['Normal'], fontName='DejaVuSans', fontSize=8)
    ))

    # Sınıflandırma tablosu
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph('Sınıflandırma Tablosu', h2_s))
    cl = result['classification']
    n0 = cl['tn'] + cl['fp']
    n1 = cl['fn'] + cl['tp']
    cl_rows = [
        ['', f'Tahmin: {cl["cat0"]}', f'Tahmin: {cl["cat1"]}', 'Doğruluk'],
        [f'Gerçek: {cl["cat0"]}', str(cl['tn']), str(cl['fp']),
         f"{round(cl['tn'] / n0 * 100, 1)}%" if n0 > 0 else '—'],
        [f'Gerçek: {cl["cat1"]}', str(cl['fn']), str(cl['tp']),
         f"{round(cl['tp'] / n1 * 100, 1)}%" if n1 > 0 else '—'],
        ['Genel Doğruluk', '', '', f"{cl['accuracy']}%"],
    ]
    cl_tbl = Table(cl_rows, colWidths=[4*cm, 3.5*cm, 3.5*cm, 3*cm])
    cl_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TEAL),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 0), (0, -1), TEAL),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (1, 1), (-1, -2), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (1, 1), (1, 1), colors.HexColor('#d4edda')),
        ('BACKGROUND', (2, 2), (2, 2), colors.HexColor('#d4edda')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f5e9')),
    ]))
    story.append(cl_tbl)

    # APA
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph('Tezinde Nasıl Raporlarsın?', h2_s))
    apa_text = (f"Lojistik regresyon analizi sonucunda kurulan model istatistiksel açıdan "
                f"{'anlamlı bulunmuştur' if sig else 'anlamlı bulunmamıştır'}, "
                f"χ²({result['chi2_df']}) = {result['chi2']:.3f}, p = {p_str}, "
                f"Nagelkerke R² = {result['nagelkerke_r2']:.4f}. "
                f"Model gözlemlerin %{result['classification']['accuracy']} kadarını doğru sınıflandırmıştır.")
    if result['sig_predictors']:
        apa_text += f" Anlamlı yordayıcılar: {', '.join(result['sig_predictors'])}."
    apa_tbl = Table([[Paragraph(apa_text, norm_s)]], colWidths=[16*cm])
    apa_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0fff8')),
        ('BOX', (0, 0), (-1, -1), 1, TEAL),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(apa_tbl)

    doc.build(story)
    return buf.getvalue()
