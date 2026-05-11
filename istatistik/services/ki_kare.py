"""
Ki-Kare Bağımsızlık Testi (χ²) — İki kategorik değişken arasındaki ilişki.
Pearson's Chi-Square test of independence + Cramér's V etki büyüklüğü.
"""
import io
import numpy as np


def analyze(df, col1: str, col2: str) -> dict:
    import pandas as pd
    from scipy import stats

    if col1 not in df.columns:
        raise ValueError(f'"{col1}" sütunu bulunamadı.')
    if col2 not in df.columns:
        raise ValueError(f'"{col2}" sütunu bulunamadı.')
    if col1 == col2:
        raise ValueError('İki farklı sütun seçmelisiniz.')

    sub = df[[col1, col2]].dropna()
    n = len(sub)
    if n < 5:
        raise ValueError('En az 5 geçerli satır gereklidir.')

    ct = pd.crosstab(sub[col1], sub[col2])
    if ct.shape[0] < 2 or ct.shape[1] < 2:
        raise ValueError('Her değişkenin en az 2 farklı kategorisi olmalıdır.')

    chi2, p_val, dof, expected = stats.chi2_contingency(ct)

    r, c = ct.shape
    v = float(np.sqrt(chi2 / (n * (min(r, c) - 1)))) if min(r, c) > 1 else 0.0

    low_expected = int((expected < 5).sum())
    total_cells = int(expected.size)

    if v < 0.10:
        effect_label = 'Çok küçük etki'
        effect_color = 'secondary'
    elif v < 0.30:
        effect_label = 'Küçük etki'
        effect_color = 'info'
    elif v < 0.50:
        effect_label = 'Orta etki'
        effect_color = 'warning'
    else:
        effect_label = 'Büyük etki'
        effect_color = 'danger'

    is_significant = bool(p_val < 0.05)
    if is_significant:
        conclusion = (
            f'{col1} ile {col2} arasında istatistiksel olarak anlamlı bir ilişki '
            f'bulunmuştur (p < .05). Cramér\'s V = {v:.3f} ({effect_label.lower()}).'
        )
    else:
        conclusion = (
            f'{col1} ile {col2} arasında istatistiksel olarak anlamlı bir ilişki '
            f'bulunmamıştır (p ≥ .05).'
        )

    ct_index = [str(i) for i in ct.index]
    ct_cols = [str(c_) for c_ in ct.columns]
    ct_values = ct.values.tolist()
    row_totals = ct.sum(axis=1).tolist()
    col_totals = ct.sum(axis=0).tolist()

    return {
        'col1': col1,
        'col2': col2,
        'n': n,
        'chi2': round(float(chi2), 4),
        'dof': int(dof),
        'p_value': round(float(p_val), 4),
        'cramers_v': round(v, 4),
        'effect_label': effect_label,
        'effect_color': effect_color,
        'is_significant': is_significant,
        'conclusion': conclusion,
        'contingency_table': {
            'index': ct_index,
            'columns': ct_cols,
            'values': ct_values,
            'row_totals': [int(x) for x in row_totals],
            'col_totals': [int(x) for x in col_totals],
            'grand_total': int(n),
        },
        'low_expected_count': low_expected,
        'total_cells': total_cells,
        'low_expected_warning': low_expected > 0,
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
    PURPLE = colors.HexColor('#4c1d95')
    title_style = ParagraphStyle('T', parent=styles['Heading1'], fontSize=16, spaceAfter=6,
                                 fontName='DejaVuSans', textColor=PURPLE)
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, spaceAfter=4,
                        fontName='DejaVuSans', textColor=PURPLE)
    normal = ParagraphStyle('N', parent=styles['Normal'], fontName='DejaVuSans')
    small = ParagraphStyle('S', parent=styles['Normal'], fontName='DejaVuSans', fontSize=9)

    story = []
    story.append(Paragraph('Ki-Kare Bağımsızlık Testi Raporu', title_style))
    story.append(Paragraph(f'Dosya: {filename}', normal))
    story.append(Spacer(1, 0.3*cm))

    # Özet istatistikler tablosu
    story.append(Paragraph('Test Sonuçları', h2))
    summary_data = [
        ['Değişken 1', 'Değişken 2', 'N', 'χ²', 'df', 'p', 'Cramér\'s V', 'Etki'],
        [
            result['col1'], result['col2'],
            str(result['n']),
            f"{result['chi2']:.4f}",
            str(result['dof']),
            f"{result['p_value']:.4f}",
            f"{result['cramers_v']:.4f}",
            result['effect_label'],
        ],
    ]
    col_w = [3*cm, 3*cm, 1.5*cm, 2*cm, 1.2*cm, 2*cm, 2.5*cm, 3*cm]
    tbl = Table(summary_data, colWidths=col_w)
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PURPLE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, 1),
         colors.HexColor('#d4edda') if result['is_significant'] else colors.HexColor('#f8d7da')),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.4*cm))

    # Sonuç
    story.append(Paragraph('Yorum', h2))
    story.append(Paragraph(result['conclusion'], normal))
    story.append(Spacer(1, 0.3*cm))

    if result['low_expected_warning']:
        story.append(Paragraph(
            f'⚠ Uyarı: {result["low_expected_count"]} hücrede beklenen frekans 5\'in altındadır '
            f'(toplam {result["total_cells"]} hücreden). Ki-kare testi bu durumda güvenilmez '
            f'olabilir; Fisher\'s Exact Test değerlendirilmelidir.',
            small,
        ))
        story.append(Spacer(1, 0.3*cm))

    # Çapraz tablo
    story.append(Paragraph('Çapraz Tablo (Gözlenen Frekanslar)', h2))
    ct = result['contingency_table']
    header = [result['col1'] + ' \\ ' + result['col2']] + ct['columns'] + ['Toplam']
    rows = [header]
    for i, idx in enumerate(ct['index']):
        row = [idx] + [str(v) for v in ct['values'][i]] + [str(ct['row_totals'][i])]
        rows.append(row)
    total_row = ['Toplam'] + [str(v) for v in ct['col_totals']] + [str(ct['grand_total'])]
    rows.append(total_row)

    n_cols = len(header)
    col_w2 = [3*cm] + [2*cm] * (n_cols - 1)
    tbl2 = Table(rows, colWidths=col_w2)
    tbl2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ede9fe')),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ede9fe')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ede9fe')),
        ('BACKGROUND', (-1, 0), (-1, -1), colors.HexColor('#ede9fe')),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTNAME', (0, 0), (0, -1), 'DejaVuSans-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(tbl2)

    doc.build(story)
    return buf.getvalue()
