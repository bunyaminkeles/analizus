"""
Wilcoxon İşaret Testi (Wilcoxon Signed-Rank Test).
İki bağımlı (eşleştirilmiş) ölçümü karşılaştıran non-parametrik test.
Bağımlı t-testinin parametrik olmayan alternatifi.
"""
import io
import numpy as np
from scipy import stats


def analyze(df, col1: str, col2: str) -> dict:
    if col1 not in df.columns:
        raise ValueError(f'"{col1}" sütunu bulunamadı.')
    if col2 not in df.columns:
        raise ValueError(f'"{col2}" sütunu bulunamadı.')
    if col1 == col2:
        raise ValueError('İki farklı sütun seçilmelidir.')

    sub = df[[col1, col2]].dropna()
    if len(sub) < 5:
        raise ValueError(f'En az 5 eşleştirilmiş gözlem gereklidir, {len(sub)} çift bulundu.')

    x = sub[col1].values.astype(float)
    y = sub[col2].values.astype(float)

    diff = y - x
    nonzero = diff[diff != 0]
    if len(nonzero) == 0:
        raise ValueError('İki sütun arasında hiç fark bulunamadı (tüm farklar sıfır).')

    w_stat, p_val = stats.wilcoxon(x, y, alternative='two-sided')

    # Etki büyüklüğü: rank-biserial r = 1 - 2W / (n*(n+1)/2)
    n = len(nonzero)
    r_rb = 1 - (2 * float(w_stat)) / (n * (n + 1) / 2)

    n_total = len(sub)
    n_positive = int((diff > 0).sum())
    n_negative = int((diff < 0).sum())
    n_ties = int((diff == 0).sum())

    return {
        'col1': col1,
        'col2': col2,
        'n': n_total,
        'n_positive': n_positive,
        'n_negative': n_negative,
        'n_ties': n_ties,
        'median1': round(float(np.median(x)), 3),
        'median2': round(float(np.median(y)), 3),
        'mean1': round(float(x.mean()), 3),
        'mean2': round(float(y.mean()), 3),
        'std1': round(float(x.std(ddof=1)), 3),
        'std2': round(float(y.std(ddof=1)), 3),
        'mean_diff': round(float(diff.mean()), 3),
        'median_diff': round(float(np.median(diff)), 3),
        'w_stat': round(float(w_stat), 3),
        'p_value': round(float(p_val), 4),
        'r_rb': round(float(r_rb), 3),
        'effect_interpretation': _interpret_r(abs(float(r_rb))),
        'significant': float(p_val) < 0.05,
        'conclusion': _conclusion(p_val, col1, col2, np.median(x), np.median(y)),
    }


def _interpret_r(r: float) -> str:
    if r < 0.1:
        return 'İhmal edilebilir etki (r < .10)'
    if r < 0.3:
        return 'Küçük etki (.10 ≤ r < .30)'
    if r < 0.5:
        return 'Orta düzey etki (.30 ≤ r < .50)'
    return 'Büyük etki (r ≥ .50)'


def _conclusion(p, col1, col2, med1, med2) -> str:
    dir_str = 'artış' if med2 > med1 else 'azalış'
    if float(p) < 0.05:
        return (f'{col1} ile {col2} ölçümleri arasında istatistiksel olarak '
                f'anlamlı bir fark bulunmaktadır (p = {p:.4f}). '
                f'Medyan değerleri sırasıyla {med1:.3f} ve {med2:.3f} olup '
                f'ikinci ölçümde {dir_str} gözlemlenmiştir.')
    return (f'{col1} ile {col2} ölçümleri arasında istatistiksel olarak '
            f'anlamlı bir fark bulunmamaktadır (p = {p:.4f}). '
            f'Medyan değerleri sırasıyla {med1:.3f} ve {med2:.3f}tir.')


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
    story.append(Paragraph('Wilcoxon İşaret Testi Raporu', title_s))
    story.append(Paragraph(f'Dosya: {filename}', norm_s))
    story.append(Spacer(1, 0.4*cm))

    # Betimsel istatistikler
    story.append(Paragraph('Betimsel İstatistikler', h2_s))
    desc_header = ['', result['col1'], result['col2']]
    desc_rows = [
        desc_header,
        ['n', str(result['n']), str(result['n'])],
        ['Medyan', f"{result['median1']:.3f}", f"{result['median2']:.3f}"],
        ['Ortalama', f"{result['mean1']:.3f}", f"{result['mean2']:.3f}"],
        ['SS', f"{result['std1']:.3f}", f"{result['std2']:.3f}"],
    ]
    desc_tbl = Table(desc_rows, colWidths=[4*cm, 5.5*cm, 5.5*cm])
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

    # Fark istatistikleri
    story.append(Paragraph('Fark İstatistikleri', h2_s))
    diff_rows = [
        ['Pozitif fark (n)', str(result['n_positive'])],
        ['Negatif fark (n)', str(result['n_negative'])],
        ['Eşit (n)', str(result['n_ties'])],
        ['Ortalama fark', f"{result['mean_diff']:.3f}"],
        ['Medyan fark', f"{result['median_diff']:.3f}"],
    ]
    diff_tbl = Table(diff_rows, colWidths=[7*cm, 9*cm])
    diff_tbl.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(diff_tbl)
    story.append(Spacer(1, 0.4*cm))

    # Test sonuçları
    story.append(Paragraph('Test Sonuçları', h2_s))
    sig = result['significant']
    res_rows = [
        ['W istatistiği', f"{result['w_stat']:.3f}"],
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
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph('Tezinde Nasıl Raporlarsın?', h2_s))
    p_str = '< .001' if result['p_value'] < 0.001 else f"{result['p_value']:.3f}"
    sig_txt = ('istatistiksel olarak anlamlı bulunmuştur'
               if result['significant'] else 'istatistiksel olarak anlamlı bulunmamıştır')
    apa_text = (f"Wilcoxon işaret testi sonucunda {result['col1']} ve {result['col2']} ölçümleri "
                f"arasındaki fark {sig_txt}, "
                f"W = {result['w_stat']:.3f}, p {p_str}, "
                f"r = {abs(result['r_rb']):.3f} ({result['effect_interpretation']}) (N = {result['n']}).")
    apa_tbl = Table([[Paragraph(apa_text, norm_s)]], colWidths=[16*cm])
    apa_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff8f0')),
        ('BOX', (0, 0), (-1, -1), 1, HEADER_COLOR),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(apa_tbl)

    doc.build(story)
    return buf.getvalue()
