"""
Tek Yönlü ANOVA + Tukey / Bonferroni post-hoc testleri.
"""
import io
import numpy as np
from scipy import stats
from itertools import combinations


def analyze(df, group_col: str, dep_col: str, posthoc: str = 'tukey') -> dict:
    if group_col not in df.columns:
        raise ValueError(f'"{group_col}" sütunu bulunamadı.')
    if dep_col not in df.columns:
        raise ValueError(f'"{dep_col}" sütunu bulunamadı.')

    sub = df[[group_col, dep_col]].dropna()
    group_labels = sorted(sub[group_col].unique(), key=str)

    if len(group_labels) < 2:
        raise ValueError('En az 2 grup gereklidir.')
    if len(group_labels) > 20:
        raise ValueError('En fazla 20 grup desteklenmektedir.')

    groups = [sub[sub[group_col] == g][dep_col].values.astype(float)
              for g in group_labels]
    for g, lbl in zip(groups, group_labels):
        if len(g) < 3:
            raise ValueError(f'"{lbl}" grubunda en az 3 gözlem olmalıdır.')

    f_stat, p_val = stats.f_oneway(*groups)

    # Eta-kare (η²) etki büyüklüğü
    grand_mean = np.concatenate(groups).mean()
    ss_between = sum(len(g) * (g.mean() - grand_mean) ** 2 for g in groups)
    ss_total = sum(((v - grand_mean) ** 2) for g in groups for v in g)
    eta_sq = ss_between / ss_total if ss_total > 0 else 0.0

    # Levene varyans homojenliği
    levene_stat, levene_p = stats.levene(*groups)

    # Grup istatistikleri
    group_stats = []
    for g, lbl in zip(groups, group_labels):
        group_stats.append({
            'label': str(lbl),
            'n': len(g),
            'mean': round(float(g.mean()), 3),
            'std': round(float(g.std(ddof=1)), 3),
            'min': round(float(g.min()), 3),
            'max': round(float(g.max()), 3),
        })

    # Post-hoc testler
    posthoc_results = []
    if float(p_val) < 0.05:
        pairs = list(combinations(range(len(group_labels)), 2))
        n_comparisons = len(pairs)
        for i, j in pairs:
            t_s, p_pair = stats.ttest_ind(groups[i], groups[j])
            if posthoc == 'bonferroni':
                p_adj = min(p_pair * n_comparisons, 1.0)
                method = 'Bonferroni'
            else:
                # Tukey HSD yaklaşımı: Bonferroni ile karşılaştırılabilir ve scipy ile uygulanabilir
                # Tam Tukey için statsmodels gerekir; burada Bonferroni fallback kullanıyoruz
                p_adj = min(p_pair * n_comparisons, 1.0)
                method = 'Tukey (Bonferroni yaklaşımı)'
            posthoc_results.append({
                'g1': str(group_labels[i]),
                'g2': str(group_labels[j]),
                'mean_diff': round(float(groups[i].mean() - groups[j].mean()), 3),
                'p_value': round(float(p_pair), 4),
                'p_adj': round(float(p_adj), 4),
                'significant': float(p_adj) < 0.05,
            })

    return {
        'test_label': 'Tek Yönlü ANOVA',
        'group_col': group_col,
        'dep_col': dep_col,
        'k_groups': len(group_labels),
        'f_stat': round(float(f_stat), 3),
        'p_value': round(float(p_val), 4),
        'df_between': len(group_labels) - 1,
        'df_within': len(sub) - len(group_labels),
        'eta_sq': round(float(eta_sq), 3),
        'effect_interpretation': _interpret_eta(eta_sq),
        'levene_p': round(float(levene_p), 4),
        'significant': float(p_val) < 0.05,
        'group_stats': group_stats,
        'posthoc': posthoc_results,
        'posthoc_method': method if float(p_val) < 0.05 else '—',
        'conclusion': _conclusion(p_val, group_col, dep_col, posthoc_results),
    }


def _interpret_eta(eta: float) -> str:
    if eta < 0.01:
        return 'İhmal edilebilir etki (η² < .01)'
    if eta < 0.06:
        return 'Küçük etki (.01 ≤ η² < .06)'
    if eta < 0.14:
        return 'Orta düzey etki (.06 ≤ η² < .14)'
    return 'Büyük etki (η² ≥ .14)'


def _conclusion(p, group_col, dep_col, posthoc) -> str:
    if p >= 0.05:
        return (f'Gruplar arasında {dep_col} açısından istatistiksel olarak '
                f'anlamlı bir fark bulunmamaktadır [F = —, p = {p:.4f}].')
    sig_pairs = [f'{r["g1"]} – {r["g2"]}' for r in posthoc if r['significant']]
    base = (f'Gruplar arasında {dep_col} açısından istatistiksel olarak '
            f'anlamlı bir fark bulunmaktadır (p = {p:.4f}).')
    if sig_pairs:
        base += f' Post-hoc analizde anlamlı farklılık gösteren çiftler: {", ".join(sig_pairs)}.'
    return base


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
    title_s = ParagraphStyle('T', parent=styles['Heading1'], fontSize=16, spaceAfter=6, fontName='DejaVuSans')
    h2_s = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, spaceAfter=4, fontName='DejaVuSans')
    norm_s = ParagraphStyle('N', parent=styles['Normal'], fontName='DejaVuSans', fontSize=9)

    story = []
    story.append(Paragraph('Tek Yönlü ANOVA Raporu', title_s))
    story.append(Paragraph(f'Dosya: {filename}', norm_s))
    story.append(Spacer(1, 0.4*cm))

    # Grup istatistikleri
    story.append(Paragraph('Grup İstatistikleri', h2_s))
    gs_header = ['Grup', 'n', 'Ort.', 'SS', 'Min', 'Maks']
    gs_rows = [gs_header] + [
        [s['label'], str(s['n']), f"{s['mean']:.3f}", f"{s['std']:.3f}",
         f"{s['min']:.3f}", f"{s['max']:.3f}"]
        for s in result['group_stats']
    ]
    gs_tbl = Table(gs_rows, colWidths=[4*cm, 2*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
    gs_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(gs_tbl)
    story.append(Spacer(1, 0.5*cm))

    # ANOVA tablosu
    story.append(Paragraph('ANOVA Tablosu', h2_s))
    sig = result['significant']
    anova_rows = [
        ['F istatistiği', f"{result['f_stat']:.3f}"],
        ['df (gruplar arası)', str(result['df_between'])],
        ['df (gruplar içi)', str(result['df_within'])],
        ['p-değeri', f"{result['p_value']:.4f}"],
        ['Eta-kare (η²)', f"{result['eta_sq']:.3f}"],
        ['Etki Büyüklüğü', result['effect_interpretation']],
        ['Levene p', f"{result['levene_p']:.4f}"],
        ['Sonuç', 'Anlamlı (p < .05)' if sig else 'Anlamlı değil (p ≥ .05)'],
    ]
    a_tbl = Table(anova_rows, colWidths=[7*cm, 9*cm])
    a_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('BACKGROUND', (1, -1), (1, -1),
         colors.HexColor('#d4edda') if sig else colors.HexColor('#f8d7da')),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (1, 0), (1, -2), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(a_tbl)

    # Post-hoc
    if result['posthoc']:
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(f'Post-Hoc Testler ({result["posthoc_method"]})', h2_s))
        ph_header = ['Grup 1', 'Grup 2', 'Ort. Fark', 'p', 'p (düzeltilmiş)', 'Anlamlı']
        ph_rows = [ph_header] + [
            [r['g1'], r['g2'], f"{r['mean_diff']:.3f}", f"{r['p_value']:.4f}",
             f"{r['p_adj']:.4f}", 'Evet' if r['significant'] else 'Hayır']
            for r in result['posthoc']
        ]
        ph_tbl = Table(ph_rows, colWidths=[3*cm, 3*cm, 3*cm, 2.5*cm, 3.5*cm, 2*cm])
        ph_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
        ]
        for idx, r in enumerate(result['posthoc'], start=1):
            if r['significant']:
                ph_style.append(('BACKGROUND', (5, idx), (5, idx), colors.HexColor('#d4edda')))
        ph_tbl.setStyle(TableStyle(ph_style))
        story.append(ph_tbl)

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph('Yorum', h2_s))
    story.append(Paragraph(result['conclusion'], norm_s))

    doc.build(story)
    return buf.getvalue()
