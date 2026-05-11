"""
t-Testi Analizi
Bağımsız örneklem t-testi ve bağımlı (eşleştirilmiş) örneklem t-testi.
"""
import io
import numpy as np
from scipy import stats


def analyze(df, test_type: str, group_col: str = None,
            dep_col: str = None, col1: str = None, col2: str = None) -> dict:
    """
    test_type: 'independent' veya 'paired'
    Bağımsız: group_col (kategorik, 2 grup) + dep_col (sayısal)
    Bağımlı:  col1, col2 (her biri sayısal)
    """
    if test_type == 'independent':
        return _independent(df, group_col, dep_col)
    elif test_type == 'paired':
        return _paired(df, col1, col2)
    else:
        raise ValueError(f'Bilinmeyen test tipi: {test_type}')


def _independent(df, group_col: str, dep_col: str) -> dict:
    if group_col not in df.columns:
        raise ValueError(f'"{group_col}" sütunu bulunamadı.')
    if dep_col not in df.columns:
        raise ValueError(f'"{dep_col}" sütunu bulunamadı.')

    groups = df[group_col].dropna().unique()
    if len(groups) != 2:
        raise ValueError(
            f'Bağımsız t-testi için tam 2 grup gereklidir. '
            f'"{group_col}" sütununda {len(groups)} farklı değer bulundu.')

    g1_label, g2_label = str(groups[0]), str(groups[1])
    g1 = df[df[group_col] == groups[0]][dep_col].dropna().values.astype(float)
    g2 = df[df[group_col] == groups[1]][dep_col].dropna().values.astype(float)

    if len(g1) < 3 or len(g2) < 3:
        raise ValueError('Her grupta en az 3 gözlem olmalıdır.')

    t_stat, p_val = stats.ttest_ind(g1, g2, equal_var=True)
    # Levene varyans homojenliği testi
    levene_stat, levene_p = stats.levene(g1, g2)
    if levene_p < 0.05:
        # Welch t-testi
        t_stat, p_val = stats.ttest_ind(g1, g2, equal_var=False)
        used_welch = True
    else:
        used_welch = False

    df_val = len(g1) + len(g2) - 2 if not used_welch else _welch_df(g1, g2)

    # Cohen's d
    pooled_std = np.sqrt(((len(g1) - 1) * g1.std(ddof=1) ** 2 +
                          (len(g2) - 1) * g2.std(ddof=1) ** 2) /
                         (len(g1) + len(g2) - 2))
    cohens_d = (g1.mean() - g2.mean()) / pooled_std if pooled_std > 0 else 0.0

    # %95 güven aralığı
    diff = g1.mean() - g2.mean()
    se_diff = np.sqrt(g1.var(ddof=1) / len(g1) + g2.var(ddof=1) / len(g2))
    t_crit = stats.t.ppf(0.975, df=df_val)
    ci_low = diff - t_crit * se_diff
    ci_high = diff + t_crit * se_diff

    return {
        'test_type': 'independent',
        'test_label': 'Bağımsız Örneklem t-Testi' + (' (Welch)' if used_welch else ''),
        'group_col': group_col,
        'dep_col': dep_col,
        'g1_label': g1_label,
        'g2_label': g2_label,
        'g1_n': len(g1),
        'g2_n': len(g2),
        'g1_mean': round(float(g1.mean()), 3),
        'g2_mean': round(float(g2.mean()), 3),
        'g1_std': round(float(g1.std(ddof=1)), 3),
        'g2_std': round(float(g2.std(ddof=1)), 3),
        't_stat': round(float(t_stat), 3),
        'p_value': round(float(p_val), 4),
        'df': round(float(df_val), 1),
        'cohens_d': round(float(cohens_d), 3),
        'effect_interpretation': _interpret_d(abs(cohens_d)),
        'ci_low': round(float(ci_low), 3),
        'ci_high': round(float(ci_high), 3),
        'levene_p': round(float(levene_p), 4),
        'used_welch': used_welch,
        'significant': float(p_val) < 0.05,
        'conclusion': _conclusion_independent(p_val, g1_label, g2_label, dep_col, g1.mean(), g2.mean()),
    }


def _paired(df, col1: str, col2: str) -> dict:
    if col1 not in df.columns:
        raise ValueError(f'"{col1}" sütunu bulunamadı.')
    if col2 not in df.columns:
        raise ValueError(f'"{col2}" sütunu bulunamadı.')

    data = df[[col1, col2]].dropna()
    if len(data) < 5:
        raise ValueError('En az 5 çift gözlem gereklidir.')

    a = data[col1].values.astype(float)
    b = data[col2].values.astype(float)

    t_stat, p_val = stats.ttest_rel(a, b)
    diff = a - b
    n = len(diff)
    df_val = n - 1

    cohens_d = diff.mean() / diff.std(ddof=1) if diff.std(ddof=1) > 0 else 0.0
    se_diff = diff.std(ddof=1) / np.sqrt(n)
    t_crit = stats.t.ppf(0.975, df=df_val)
    ci_low = diff.mean() - t_crit * se_diff
    ci_high = diff.mean() + t_crit * se_diff

    return {
        'test_type': 'paired',
        'test_label': 'Bağımlı Örneklem t-Testi (Eşleştirilmiş)',
        'col1': col1,
        'col2': col2,
        'n': n,
        'col1_mean': round(float(a.mean()), 3),
        'col2_mean': round(float(b.mean()), 3),
        'col1_std': round(float(a.std(ddof=1)), 3),
        'col2_std': round(float(b.std(ddof=1)), 3),
        'diff_mean': round(float(diff.mean()), 3),
        'diff_std': round(float(diff.std(ddof=1)), 3),
        't_stat': round(float(t_stat), 3),
        'p_value': round(float(p_val), 4),
        'df': df_val,
        'cohens_d': round(float(cohens_d), 3),
        'effect_interpretation': _interpret_d(abs(cohens_d)),
        'ci_low': round(float(ci_low), 3),
        'ci_high': round(float(ci_high), 3),
        'significant': float(p_val) < 0.05,
        'conclusion': _conclusion_paired(p_val, col1, col2, diff.mean()),
    }


def _welch_df(g1, g2) -> float:
    v1, v2 = g1.var(ddof=1), g2.var(ddof=1)
    n1, n2 = len(g1), len(g2)
    num = (v1 / n1 + v2 / n2) ** 2
    den = (v1 / n1) ** 2 / (n1 - 1) + (v2 / n2) ** 2 / (n2 - 1)
    return num / den if den > 0 else n1 + n2 - 2


def _interpret_d(d: float) -> str:
    if d < 0.2:
        return 'İhmal edilebilir etki'
    if d < 0.5:
        return 'Küçük etki (d < 0.50)'
    if d < 0.8:
        return 'Orta düzey etki (0.50 ≤ d < 0.80)'
    return 'Büyük etki (d ≥ 0.80)'


def _conclusion_independent(p, g1, g2, dep, m1, m2) -> str:
    dir_str = 'daha yüksek' if m1 > m2 else 'daha düşük'
    if p < 0.05:
        return (f'{g1} grubu ile {g2} grubu arasında {dep} açısından '
                f'istatistiksel olarak anlamlı bir fark bulunmaktadır (p = {p:.4f}). '
                f'{g1} grubunun ortalaması ({m1:.3f}), {g2} grubuna ({m2:.3f}) göre {dir_str}tir.')
    return (f'{g1} grubu ile {g2} grubu arasında {dep} açısından '
            f'istatistiksel olarak anlamlı bir fark bulunmamaktadır (p = {p:.4f}).')


def _conclusion_paired(p, c1, c2, diff_mean) -> str:
    dir_str = 'artmıştır' if diff_mean > 0 else 'azalmıştır'
    if p < 0.05:
        return (f'{c1} ile {c2} arasındaki fark istatistiksel olarak anlamlıdır (p = {p:.4f}). '
                f'Ortalama fark {abs(diff_mean):.3f} olup ölçüm {dir_str}.')
    return (f'{c1} ile {c2} arasındaki fark istatistiksel olarak anlamlı değildir (p = {p:.4f}).')


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
    story.append(Paragraph(result['test_label'] + ' Raporu', title_s))
    story.append(Paragraph(f'Dosya: {filename}', norm_s))
    story.append(Spacer(1, 0.4*cm))

    if result['test_type'] == 'independent':
        rows = [
            ['', result['g1_label'], result['g2_label']],
            ['n', str(result['g1_n']), str(result['g2_n'])],
            ['Ortalama', f"{result['g1_mean']:.3f}", f"{result['g2_mean']:.3f}"],
            ['SS', f"{result['g1_std']:.3f}", f"{result['g2_std']:.3f}"],
        ]
    else:
        rows = [
            ['', result['col1'], result['col2']],
            ['Ortalama', f"{result['col1_mean']:.3f}", f"{result['col2_mean']:.3f}"],
            ['SS', f"{result['col1_std']:.3f}", f"{result['col2_std']:.3f}"],
        ]

    grp_tbl = Table(rows, colWidths=[6*cm, 5*cm, 5*cm])
    grp_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(Paragraph('Grup İstatistikleri', h2_s))
    story.append(grp_tbl)
    story.append(Spacer(1, 0.5*cm))

    sig = result['significant']
    res_rows = [
        ['t istatistiği', f"{result['t_stat']:.3f}"],
        ['Serbestlik Derecesi (df)', str(result['df'])],
        ['p-değeri', f"{result['p_value']:.4f}"],
        ['Cohen\'s d', f"{result['cohens_d']:.3f}"],
        ['%95 GA (fark)', f"[{result['ci_low']:.3f}, {result['ci_high']:.3f}]"],
        ['Sonuç', 'Anlamlı (p < .05)' if sig else 'Anlamlı değil (p ≥ .05)'],
    ]
    res_tbl = Table(res_rows, colWidths=[7*cm, 9*cm])
    res_tbl.setStyle(TableStyle([
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
    story.append(Paragraph('Test Sonuçları', h2_s))
    story.append(res_tbl)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph('Yorum', h2_s))
    story.append(Paragraph(result['conclusion'], norm_s))

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph('Tezinde Nasıl Raporlarsın?', h2_s))
    p_str = '< .001' if result['p_value'] < 0.001 else f"{result['p_value']:.3f}"
    if result['test_type'] == 'independent':
        apa_text = (f"{result['group_col']} grupları ({result['g1_label']} ve {result['g2_label']}) "
                    f"arasındaki {result['dep_col']} farkı {result['test_label']} ile test edilmiştir: "
                    f"t({result['df']}) = {result['t_stat']:.3f}, p = {p_str}, "
                    f"d = {result['cohens_d']:.3f} "
                    f"({result['g1_label']}: M = {result['g1_mean']:.3f}, SS = {result['g1_std']:.3f}; "
                    f"{result['g2_label']}: M = {result['g2_mean']:.3f}, SS = {result['g2_std']:.3f}).")
    else:
        apa_text = (f"{result['col1']} ve {result['col2']} arasındaki fark {result['test_label']} "
                    f"ile test edilmiştir: t({result['df']}) = {result['t_stat']:.3f}, "
                    f"p = {p_str}, d = {result['cohens_d']:.3f}.")
    apa_tbl = Table([[Paragraph(apa_text, norm_s)]], colWidths=[16*cm])
    apa_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f4ff')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1e3a5f')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(apa_tbl)

    doc.build(story)
    return buf.getvalue()
