"""
Ki-Kare Bağımsızlık Testi (χ²) — İki kategorik değişken arasındaki ilişki.
Pearson's Chi-Square test of independence + Cramér's V etki büyüklüğü.
"""
import io
from django.utils.translation import gettext, pgettext
import numpy as np


def analyze(df, col1: str, col2: str) -> dict:
    import pandas as pd
    from scipy import stats

    if col1 not in df.columns:
        raise ValueError(gettext('"%(col1)s" sütunu bulunamadı.') % {'col1': col1})
    if col2 not in df.columns:
        raise ValueError(gettext('"%(col2)s" sütunu bulunamadı.') % {'col2': col2})
    if col1 == col2:
        raise ValueError(gettext('İki farklı sütun seçmelisiniz.'))

    sub = df[[col1, col2]].dropna()
    n = len(sub)
    if n < 5:
        raise ValueError(gettext('En az 5 geçerli satır gereklidir.'))

    ct = pd.crosstab(sub[col1], sub[col2])
    if ct.shape[0] < 2 or ct.shape[1] < 2:
        raise ValueError(gettext('Her değişkenin en az 2 farklı kategorisi olmalıdır.'))

    chi2, p_val, dof, expected = stats.chi2_contingency(ct)

    r, c = ct.shape
    v = float(np.sqrt(chi2 / (n * (min(r, c) - 1)))) if min(r, c) > 1 else 0.0

    low_expected = int((expected < 5).sum())
    total_cells = int(expected.size)

    # Fisher's Exact Test — yalnızca 2×2 tablolar için geçerlidir
    if r == 2 and c == 2:
        odds_ratio, fisher_p = stats.fisher_exact(ct.values)
        fisher_result = {
            'odds_ratio': round(float(odds_ratio), 4),
            'p_value': round(float(fisher_p), 4),
            'is_significant': bool(fisher_p < 0.05),
        }
    else:
        fisher_result = None

    if v < 0.10:
        effect_label = gettext('Çok küçük etki')
        effect_color = 'secondary'
    elif v < 0.30:
        effect_label = gettext('Küçük etki')
        effect_color = 'info'
    elif v < 0.50:
        effect_label = gettext('Orta etki')
        effect_color = 'warning'
    else:
        effect_label = gettext('Büyük etki')
        effect_color = 'danger'

    is_significant = bool(p_val < 0.05)
    if is_significant:
        conclusion = (
            gettext("%(col1)s ile %(col2)s arasında istatistiksel olarak anlamlı bir ilişki bulunmuştur (p < .05). Cramér's V = %(v)s (%(v2)s).") % {'col1': col1, 'col2': col2, 'v': f'{v:.3f}', 'v2': effect_label.lower()}
        )
    else:
        conclusion = (
            gettext('%(col1)s ile %(col2)s arasında istatistiksel olarak anlamlı bir ilişki bulunmamıştır (p ≥ .05).') % {'col1': col1, 'col2': col2}
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
        'fisher': fisher_result,
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
    story.append(Paragraph(gettext('Ki-Kare Bağımsızlık Testi Raporu'), title_style))
    story.append(Paragraph(gettext('Dosya: %(filename)s') % {'filename': filename}, normal))
    story.append(Spacer(1, 0.3*cm))

    # Özet istatistikler tablosu
    story.append(Paragraph(gettext('Test Sonuçları'), h2))
    summary_data = [
        [gettext('Değişken 1'), gettext('Değişken 2'), 'N', 'χ²', 'df', 'p', gettext("Cramér's V"), gettext('Etki')],
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
    story.append(Paragraph(gettext('Yorum'), h2))
    story.append(Paragraph(result['conclusion'], normal))
    story.append(Spacer(1, 0.3*cm))

    if result['low_expected_warning']:
        story.append(Paragraph(
            gettext("⚠ Uyarı: %(low_expected_count)s hücrede beklenen frekans 5'in altındadır (toplam %(total_cells)s hücreden). Ki-kare testi bu durumda güvenilmez olabilir; Fisher's Exact Test değerlendirilmelidir.") % {'low_expected_count': result['low_expected_count'], 'total_cells': result['total_cells']},
            small,
        ))
        story.append(Spacer(1, 0.3*cm))

    # Fisher sonucu (2x2 ise)
    if result.get('fisher'):
        f = result['fisher']
        f_sig = gettext('anlamlı') if f['is_significant'] else gettext('anlamlı değil')
        story.append(Paragraph(gettext("Fisher's Exact Test (2×2 tablo)"), h2))
        fisher_data = [
            [gettext('Odds Ratio'), gettext('p (Fisher)'), gettext('Anlamlı?')],
            [f"{f['odds_ratio']:.4f}", f"{f['p_value']:.4f}", gettext('Evet') if f['is_significant'] else gettext('Hayır')],
        ]
        f_tbl = Table(fisher_data, colWidths=[4*cm, 4*cm, 4*cm])
        f_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), PURPLE),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 1), (-1, 1),
             colors.HexColor('#d4edda') if f['is_significant'] else colors.HexColor('#f8d7da')),
        ]))
        story.append(f_tbl)
        story.append(Spacer(1, 0.4*cm))

    # Çapraz tablo
    story.append(Paragraph(gettext('Çapraz Tablo (Gözlenen Frekanslar)'), h2))
    story.append(Paragraph(gettext('Sütunlar: %(col2)s') % {'col2': result['col2']}, small))
    story.append(Spacer(1, 0.15*cm))
    ct = result['contingency_table']
    header = [result['col1']] + ct['columns'] + [pgettext('tablo', 'Toplam')]
    rows = [header]
    for i, idx in enumerate(ct['index']):
        row = [idx] + [str(v) for v in ct['values'][i]] + [str(ct['row_totals'][i])]
        rows.append(row)
    total_row = [pgettext('tablo', 'Toplam')] + [str(v) for v in ct['col_totals']] + [str(ct['grand_total'])]
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

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(gettext('APA Formatında Raporlama'), h2))
    # 'p < .001' / 'p = 0.123'; anlamlı/anlamsız ayrı tam cümle — şablon JS ile ortak msgid
    v = dict(c1=result['col1'], c2=result['col2'], dof=result['dof'], n=result['n'], chi2=f"{result['chi2']:.3f}",
             p='p < .001' if result['p_value'] < 0.001 else f"p = {result['p_value']:.3f}",
             v=f"{result['cramers_v']:.3f}", effect=result['effect_label'].lower())
    if result['is_significant']:
        apa_text = gettext('Ki-kare bağımsızlık testi sonucunda {c1} ile {c2} arasında istatistiksel olarak anlamlı '
                           'bir ilişki bulunmuştur, χ²({dof}, N = {n}) = {chi2}, {p}, V = {v} ({effect}).').format(**v)
    else:
        apa_text = gettext('Ki-kare bağımsızlık testi sonucunda {c1} ile {c2} arasında anlamlı bir ilişki '
                           'bulunmamıştır, χ²({dof}, N = {n}) = {chi2}, {p}, V = {v} ({effect}).').format(**v)
    apa_tbl = Table([[Paragraph(apa_text, normal)]], colWidths=[16*cm])
    apa_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f0ff')),
        ('BOX', (0, 0), (-1, -1), 1, PURPLE),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(apa_tbl)

    doc.build(story)
    return buf.getvalue()
