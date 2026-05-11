"""
Kruskal-Wallis H Testi.
3 veya daha fazla bağımsız grubun dağılımını karşılaştıran non-parametrik test.
Tek yönlü ANOVA'nın parametrik olmayan alternatifi.
Post-hoc: çiftli Mann-Whitney U + Bonferroni düzeltmesi.
"""
import io
import numpy as np
from scipy import stats
from itertools import combinations


def analyze(df, group_col: str, dep_col: str) -> dict:
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

    h_stat, p_val = stats.kruskal(*groups)

    # Eta-kare (η²_H) etki büyüklüğü
    n_total = sum(len(g) for g in groups)
    k = len(group_labels)
    eta_sq = (h_stat - k + 1) / (n_total - k) if (n_total - k) > 0 else 0.0
    eta_sq = max(0.0, float(eta_sq))

    # Ortalama sıralar
    all_vals = np.concatenate(groups)
    all_ranks = stats.rankdata(all_vals)
    idx = 0
    group_stats = []
    for g, lbl in zip(groups, group_labels):
        n = len(g)
        g_ranks = all_ranks[idx:idx + n]
        idx += n
        group_stats.append({
            'label': str(lbl),
            'n': n,
            'median': round(float(np.median(g)), 3),
            'mean': round(float(g.mean()), 3),
            'std': round(float(g.std(ddof=1)), 3),
            'mean_rank': round(float(g_ranks.mean()), 3),
        })

    # Post-hoc: çiftli Mann-Whitney U + Bonferroni
    posthoc_results = []
    if float(p_val) < 0.05:
        pairs = list(combinations(range(k), 2))
        n_comparisons = len(pairs)
        for i, j in pairs:
            u_s, p_pair = stats.mannwhitneyu(groups[i], groups[j], alternative='two-sided')
            p_adj = min(float(p_pair) * n_comparisons, 1.0)
            posthoc_results.append({
                'g1': str(group_labels[i]),
                'g2': str(group_labels[j]),
                'median_diff': round(float(np.median(groups[i]) - np.median(groups[j])), 3),
                'u_stat': round(float(u_s), 3),
                'p_value': round(float(p_pair), 4),
                'p_adj': round(float(p_adj), 4),
                'significant': float(p_adj) < 0.05,
            })

    return {
        'test_label': 'Kruskal-Wallis H Testi',
        'group_col': group_col,
        'dep_col': dep_col,
        'k_groups': k,
        'n_total': n_total,
        'h_stat': round(float(h_stat), 3),
        'df': k - 1,
        'p_value': round(float(p_val), 4),
        'eta_sq': round(float(eta_sq), 3),
        'effect_interpretation': _interpret_eta(eta_sq),
        'significant': float(p_val) < 0.05,
        'group_stats': group_stats,
        'posthoc': posthoc_results,
        'posthoc_method': 'Mann-Whitney U + Bonferroni' if float(p_val) < 0.05 else '—',
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
    if float(p) >= 0.05:
        return (f'Gruplar arasında {dep_col} açısından istatistiksel olarak '
                f'anlamlı bir fark bulunmamaktadır (p = {p:.4f}).')
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
    HEADER_COLOR = colors.HexColor('#065f46')
    title_s = ParagraphStyle('T', parent=styles['Heading1'], fontSize=16, spaceAfter=6, fontName='DejaVuSans')
    h2_s    = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, spaceAfter=4, fontName='DejaVuSans')
    norm_s  = ParagraphStyle('N', parent=styles['Normal'], fontName='DejaVuSans', fontSize=9)

    story = []
    story.append(Paragraph('Kruskal-Wallis H Testi Raporu', title_s))
    story.append(Paragraph(f'Dosya: {filename}', norm_s))
    story.append(Spacer(1, 0.4*cm))

    # Grup istatistikleri
    story.append(Paragraph('Grup İstatistikleri', h2_s))
    gs_header = ['Grup', 'n', 'Medyan', 'Ort.', 'SS', 'Ort. Sıra']
    gs_rows = [gs_header] + [
        [s['label'], str(s['n']), f"{s['median']:.3f}", f"{s['mean']:.3f}",
         f"{s['std']:.3f}", f"{s['mean_rank']:.3f}"]
        for s in result['group_stats']
    ]
    gs_tbl = Table(gs_rows, colWidths=[3.5*cm, 2*cm, 2.5*cm, 2.5*cm, 2.5*cm, 3*cm])
    gs_tbl.setStyle(TableStyle([
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
    story.append(gs_tbl)
    story.append(Spacer(1, 0.5*cm))

    # Test sonuçları
    story.append(Paragraph('Test Sonuçları', h2_s))
    sig = result['significant']
    res_rows = [
        ['H istatistiği', f"{result['h_stat']:.3f}"],
        ['Serbestlik Derecesi (df)', str(result['df'])],
        ['p-değeri', f"{result['p_value']:.4f}"],
        ['Eta-kare (η²)', f"{result['eta_sq']:.3f}"],
        ['Etki Yorumu', result['effect_interpretation']],
        ['Sonuç', 'Anlamlı (p < .05)' if sig else 'Anlamlı değil (p ≥ .05)'],
    ]
    res_tbl = Table(res_rows, colWidths=[7*cm, 9*cm])
    res_tbl.setStyle(TableStyle([
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
    story.append(res_tbl)

    # Post-hoc
    if result['posthoc']:
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(f'Post-Hoc Testler ({result["posthoc_method"]})', h2_s))
        ph_header = ['Grup 1', 'Grup 2', 'Med. Fark', 'U', 'p', 'p (Bonf.)', 'Anlamlı']
        ph_rows = [ph_header] + [
            [r['g1'], r['g2'], f"{r['median_diff']:.3f}", f"{r['u_stat']:.1f}",
             f"{r['p_value']:.4f}", f"{r['p_adj']:.4f}", 'Evet' if r['significant'] else 'Hayır']
            for r in result['posthoc']
        ]
        ph_tbl = Table(ph_rows, colWidths=[2.5*cm, 2.5*cm, 2.5*cm, 2*cm, 2.5*cm, 2.5*cm, 1.5*cm])
        ph_style = [
            ('BACKGROUND', (0, 0), (-1, 0), HEADER_COLOR),
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
                ph_style.append(('BACKGROUND', (6, idx), (6, idx), colors.HexColor('#d4edda')))
        ph_tbl.setStyle(TableStyle(ph_style))
        story.append(ph_tbl)

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph('Yorum', h2_s))
    story.append(Paragraph(result['conclusion'], norm_s))

    doc.build(story)
    return buf.getvalue()
