"""
Tekrarlayan Ölçümler ANOVA (One-Way Repeated Measures ANOVA).
Aynı katılımcıların 3+ farklı koşulda/zamanda ölçüldüğü parametrik test.
Friedman testinin parametrik alternatifi (normallik varsayımı gerektirir).
"""
import io
import numpy as np
from itertools import combinations
from scipy import stats


def analyze(df, columns: list) -> dict:
    if not columns or len(columns) < 3:
        raise ValueError('Tekrarlayan ölçümler ANOVA için en az 3 sütun seçilmelidir.')

    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f'Sütunlar bulunamadı: {", ".join(missing)}')

    sub = df[columns].dropna()
    n = len(sub)
    k = len(columns)

    if n < 5:
        raise ValueError(f'En az 5 katılımcı gereklidir, {n} satır bulundu.')

    arrays = [sub[c].values.astype(float) for c in columns]

    # Betimsel istatistikler
    descriptives = []
    for c, vals in zip(columns, arrays):
        descriptives.append({
            'col': c,
            'n': n,
            'mean': round(float(vals.mean()), 3),
            'median': round(float(np.median(vals)), 3),
            'std': round(float(vals.std(ddof=1)), 3),
            'min': round(float(vals.min()), 3),
            'max': round(float(vals.max()), 3),
        })

    # RM ANOVA hesabı (elle — statsmodels AnovaRM wide→long dönüşümü ile)
    grand_mean = float(np.concatenate(arrays).mean())
    subject_means = sub.mean(axis=1).values  # her katılımcının ortalaması

    ss_between = n * sum((float(a.mean()) - grand_mean) ** 2 for a in arrays)
    ss_subjects = k * float(np.sum((subject_means - grand_mean) ** 2))
    ss_total = float(sum(np.sum((a - grand_mean) ** 2) for a in arrays))
    ss_error = ss_total - ss_between - ss_subjects

    df_between = k - 1
    df_subjects = n - 1
    df_error = (k - 1) * (n - 1)

    ms_between = ss_between / df_between if df_between > 0 else 0
    ms_error = ss_error / df_error if df_error > 0 else 1e-10

    F = ms_between / ms_error if ms_error > 0 else 0.0
    p_val = float(stats.f.sf(F, df_between, df_error))

    # Partial eta-squared: SS_between / (SS_between + SS_error)
    eta_sq = ss_between / (ss_between + ss_error) if (ss_between + ss_error) > 0 else 0.0

    # Mauchly küresellik testi (scipy yok, kısmi uygulama — notla)
    # Epsilon düzeltmesi için Greenhouse-Geisser — yalnızca bilgilendirici
    sphericity_note = ('Küresellik (Mauchly) testi bu sürümde desteklenmemektedir. '
                       'Küresellik ihlali şüphesi varsa Greenhouse-Geisser düzeltmeli '
                       'SPSS/JASP çıktısıyla karşılaştırın.')

    # Post-hoc: pairwise bağımlı t-test + Bonferroni
    pairs = list(combinations(range(k), 2))
    n_pairs = len(pairs)
    posthoc = []
    for i, j in pairs:
        t, p = stats.ttest_rel(arrays[i], arrays[j])
        p_adj = min(float(p) * n_pairs, 1.0)
        d = float((arrays[i] - arrays[j]).mean()) / float((arrays[i] - arrays[j]).std(ddof=1))
        posthoc.append({
            'col1': columns[i],
            'col2': columns[j],
            't': round(float(t), 3),
            'p': round(float(p), 4),
            'p_adj': round(p_adj, 4),
            'd': round(abs(d), 3),
            'significant': p_adj < 0.05,
        })

    return {
        'columns': columns,
        'n': n,
        'k': k,
        'F': round(float(F), 3),
        'df_between': df_between,
        'df_error': df_error,
        'ms_between': round(ms_between, 3),
        'ms_error': round(ms_error, 3),
        'ss_between': round(ss_between, 3),
        'ss_error': round(ss_error, 3),
        'p_value': round(p_val, 4),
        'eta_sq': round(eta_sq, 3),
        'effect_interpretation': _interpret_eta(eta_sq),
        'significant': p_val < 0.05,
        'descriptives': descriptives,
        'posthoc': posthoc,
        'sphericity_note': sphericity_note,
        'conclusion': _conclusion(p_val, F, df_between, df_error, columns),
    }


def _interpret_eta(eta: float) -> str:
    if eta < 0.01:
        return 'İhmal edilebilir etki (η² < .01)'
    if eta < 0.06:
        return 'Küçük etki (.01 ≤ η² < .06)'
    if eta < 0.14:
        return 'Orta düzey etki (.06 ≤ η² < .14)'
    return 'Büyük etki (η² ≥ .14)'


def _conclusion(p, F, df1, df2, columns: list) -> str:
    col_str = ', '.join(columns)
    if float(p) < 0.05:
        return (f'{col_str} ölçümleri arasında istatistiksel olarak anlamlı bir fark '
                f'bulunmaktadır, F({df1}, {df2}) = {F:.3f}, p = {p:.4f}. '
                f'Post-hoc karşılaştırmalarda Bonferroni düzeltmesi uygulanmıştır.')
    return (f'{col_str} ölçümleri arasında istatistiksel olarak anlamlı bir fark '
            f'bulunmamaktadır, F({df1}, {df2}) = {F:.3f}, p = {p:.4f}.')


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
    HEADER_COLOR = colors.HexColor('#1e3a5f')
    title_s = ParagraphStyle('T', parent=styles['Heading1'], fontSize=16, spaceAfter=6, fontName='DejaVuSans')
    h2_s    = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, spaceAfter=4, fontName='DejaVuSans')
    norm_s  = ParagraphStyle('N', parent=styles['Normal'], fontName='DejaVuSans', fontSize=9)
    small_s = ParagraphStyle('S', parent=styles['Normal'], fontName='DejaVuSans', fontSize=8,
                             textColor=colors.HexColor('#64748b'))

    story = []
    story.append(Paragraph('Tekrarlayan Ölçümler ANOVA Raporu', title_s))
    story.append(Paragraph(f'Dosya: {filename}', norm_s))
    story.append(Spacer(1, 0.4*cm))

    # Betimsel
    story.append(Paragraph('Betimsel İstatistikler', h2_s))
    desc_header = ['Ölçüm', 'n', 'Ort.', 'Med.', 'SS', 'Min', 'Maks']
    desc_rows = [desc_header] + [
        [d['col'], str(d['n']), f"{d['mean']:.3f}", f"{d['median']:.3f}",
         f"{d['std']:.3f}", f"{d['min']:.3f}", f"{d['max']:.3f}"]
        for d in result['descriptives']
    ]
    col_widths = [4.5*cm, 1.5*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2*cm]
    desc_tbl = Table(desc_rows, colWidths=col_widths)
    desc_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HEADER_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(desc_tbl)
    story.append(Spacer(1, 0.4*cm))

    # ANOVA tablosu
    story.append(Paragraph('ANOVA Tablosu', h2_s))
    sig = result['significant']
    anova_rows = [
        ['Kaynak', 'KT (SS)', 'sd', 'KO (MS)', 'F', 'p'],
        ['Ölçümler arası', f"{result['ss_between']:.3f}", str(result['df_between']),
         f"{result['ms_between']:.3f}", f"{result['F']:.3f}", f"{result['p_value']:.4f}"],
        ['Hata', f"{result['ss_error']:.3f}", str(result['df_error']),
         f"{result['ms_error']:.3f}", '', ''],
    ]
    anova_tbl = Table(anova_rows, colWidths=[4*cm, 2.5*cm, 1.5*cm, 2.5*cm, 2*cm, 2*cm])
    anova_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HEADER_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(anova_tbl)
    story.append(Spacer(1, 0.2*cm))

    eff_rows = [
        ['Partial η²', f"{result['eta_sq']:.3f}"],
        ['Etki Yorumu', result['effect_interpretation']],
        ['Sonuç', 'Anlamlı (p < .05)' if sig else 'Anlamlı değil (p ≥ .05)'],
    ]
    eff_tbl = Table(eff_rows, colWidths=[7*cm, 9*cm])
    eff_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HEADER_COLOR),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('BACKGROUND', (1, -1), (1, -1),
         colors.HexColor('#d4edda') if sig else colors.HexColor('#f8d7da')),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (1, 0), (1, -2), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(eff_tbl)
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(result['sphericity_note'], small_s))
    story.append(Spacer(1, 0.4*cm))

    # Post-hoc
    if sig and result['posthoc']:
        story.append(Paragraph('Post-Hoc Karşılaştırmalar (Bağımlı t-testi — Bonferroni)', h2_s))
        ph_header = ['Çift', 't', 'p', 'p (düz.)', "Cohen's d", 'Anlamlı?']
        ph_rows = [ph_header] + [
            [f"{r['col1']} vs {r['col2']}", f"{r['t']:.3f}", f"{r['p']:.4f}",
             f"{r['p_adj']:.4f}", f"{r['d']:.3f}", 'Evet *' if r['significant'] else 'Hayır']
            for r in result['posthoc']
        ]
        ph_tbl = Table(ph_rows, colWidths=[5*cm, 1.8*cm, 2.2*cm, 2.2*cm, 2.2*cm, 2.6*cm])
        ph_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HEADER_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(ph_tbl)
        story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph('Yorum', h2_s))
    story.append(Paragraph(result['conclusion'], norm_s))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph('Tezinde Nasıl Raporlarsın?', h2_s))
    p_str = '< .001' if result['p_value'] < 0.001 else f"{result['p_value']:.3f}"
    sig_txt = ('istatistiksel olarak anlamlı bulunmuştur'
               if result['significant'] else 'istatistiksel olarak anlamlı bulunmamıştır')
    cols_str = ', '.join(result['columns'])
    apa_text = (f"Tekrarlayan ölçümler ANOVA sonuçlarına göre {cols_str} koşulları arasındaki fark "
                f"{sig_txt}, F({result['df_between']}, {result['df_error']}) = {result['F']:.3f}, "
                f"p {p_str}, η² = {result['eta_sq']:.3f} ({result['effect_interpretation']}).")
    apa_tbl = Table([[Paragraph(apa_text, norm_s)]], colWidths=[16*cm])
    apa_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eff6ff')),
        ('BOX', (0, 0), (-1, -1), 1, HEADER_COLOR),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(apa_tbl)

    doc.build(story)
    return buf.getvalue()
