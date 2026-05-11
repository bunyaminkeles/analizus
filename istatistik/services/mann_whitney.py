"""
Mann-Whitney U Testi (Wilcoxon sıra toplamı testi).
İki bağımsız grubun dağılımını karşılaştıran non-parametrik test.
t-testinin parametrik olmayan alternatifi.
"""
import io
import numpy as np
from scipy import stats


def analyze(df, group_col: str, dep_col: str) -> dict:
    if group_col not in df.columns:
        raise ValueError(f'"{group_col}" sütunu bulunamadı.')
    if dep_col not in df.columns:
        raise ValueError(f'"{dep_col}" sütunu bulunamadı.')

    sub = df[[group_col, dep_col]].dropna()
    groups = sub[group_col].unique()
    if len(groups) != 2:
        raise ValueError(
            f'Mann-Whitney U testi için tam 2 grup gereklidir. '
            f'"{group_col}" sütununda {len(groups)} farklı değer bulundu.')

    g1_label, g2_label = str(groups[0]), str(groups[1])
    g1 = sub[sub[group_col] == groups[0]][dep_col].values.astype(float)
    g2 = sub[sub[group_col] == groups[1]][dep_col].values.astype(float)

    if len(g1) < 3 or len(g2) < 3:
        raise ValueError('Her grupta en az 3 gözlem olmalıdır.')

    u_stat, p_val = stats.mannwhitneyu(g1, g2, alternative='two-sided')

    # Rank-biserial korelasyon (etki büyüklüğü)
    n1, n2 = len(g1), len(g2)
    r_rb = 1 - (2 * u_stat) / (n1 * n2)

    # Ortalama sıralar
    all_vals = np.concatenate([g1, g2])
    all_ranks = stats.rankdata(all_vals)
    mean_rank_g1 = all_ranks[:n1].mean()
    mean_rank_g2 = all_ranks[n1:].mean()

    group_stats = [
        {
            'label': g1_label, 'n': n1,
            'median': round(float(np.median(g1)), 3),
            'mean': round(float(g1.mean()), 3),
            'std': round(float(g1.std(ddof=1)), 3),
            'mean_rank': round(float(mean_rank_g1), 3),
        },
        {
            'label': g2_label, 'n': n2,
            'median': round(float(np.median(g2)), 3),
            'mean': round(float(g2.mean()), 3),
            'std': round(float(g2.std(ddof=1)), 3),
            'mean_rank': round(float(mean_rank_g2), 3),
        },
    ]

    return {
        'test_label': 'Mann-Whitney U Testi',
        'group_col': group_col,
        'dep_col': dep_col,
        'g1_label': g1_label,
        'g2_label': g2_label,
        'u_stat': round(float(u_stat), 3),
        'p_value': round(float(p_val), 4),
        'r_rb': round(float(r_rb), 3),
        'effect_interpretation': _interpret_r(abs(float(r_rb))),
        'significant': float(p_val) < 0.05,
        'group_stats': group_stats,
        'conclusion': _conclusion(p_val, g1_label, g2_label, dep_col,
                                  group_stats[0]['median'], group_stats[1]['median']),
    }


def _interpret_r(r: float) -> str:
    if r < 0.1:
        return 'İhmal edilebilir etki (r < .10)'
    if r < 0.3:
        return 'Küçük etki (.10 ≤ r < .30)'
    if r < 0.5:
        return 'Orta düzey etki (.30 ≤ r < .50)'
    return 'Büyük etki (r ≥ .50)'


def _conclusion(p, g1, g2, dep, med1, med2) -> str:
    dir_str = 'daha yüksek' if med1 > med2 else 'daha düşük'
    if float(p) < 0.05:
        return (f'{g1} grubu ile {g2} grubu arasında {dep} açısından '
                f'istatistiksel olarak anlamlı bir fark bulunmaktadır (p = {p:.4f}). '
                f'{g1} grubunun medyanı ({med1:.3f}), {g2} grubuna ({med2:.3f}) göre {dir_str}tir.')
    return (f'{g1} grubu ile {g2} grubu arasında {dep} açısından '
            f'istatistiksel olarak anlamlı bir fark bulunmamaktadır (p = {p:.4f}).')


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
    HEADER_COLOR = colors.HexColor('#92400e')
    title_s = ParagraphStyle('T', parent=styles['Heading1'], fontSize=16, spaceAfter=6, fontName='DejaVuSans')
    h2_s    = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, spaceAfter=4, fontName='DejaVuSans')
    norm_s  = ParagraphStyle('N', parent=styles['Normal'], fontName='DejaVuSans', fontSize=9)

    story = []
    story.append(Paragraph('Mann-Whitney U Testi Raporu', title_s))
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
        ['U istatistiği', f"{result['u_stat']:.3f}"],
        ['p-değeri', f"{result['p_value']:.4f}"],
        ['Etki Büyüklüğü (r)', f"{result['r_rb']:.3f}"],
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
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph('Yorum', h2_s))
    story.append(Paragraph(result['conclusion'], norm_s))

    doc.build(story)
    return buf.getvalue()
