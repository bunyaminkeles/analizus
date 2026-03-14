"""
Güvenilirlik Analizi — Cronbach Alpha
Girdi: pandas DataFrame (satır=katılımcı, sütun=madde)
"""
import io
import numpy as np


def analyze(df) -> dict:
    # Sayısal sütunları al
    df_num = df.select_dtypes(include=[np.number]).dropna()
    k = len(df_num.columns)
    n = len(df_num)

    if k < 2:
        raise ValueError('En az 2 sayısal sütun (madde) gereklidir.')
    if n < 5:
        raise ValueError('En az 5 geçerli satır (katılımcı) gereklidir.')

    data = df_num.values  # (n, k)

    # Toplam puan
    total = data.sum(axis=1)

    # Madde varyansları toplamı
    item_vars = data.var(axis=0, ddof=1)
    sum_item_var = item_vars.sum()

    # Toplam varyans
    total_var = total.var(ddof=1)

    if total_var == 0:
        raise ValueError('Toplam varyans sıfır — tüm satırlar aynı değere sahip.')

    alpha = (k / (k - 1)) * (1 - sum_item_var / total_var)

    # Madde istatistikleri
    item_stats = []
    cols = list(df_num.columns)
    for i, col in enumerate(cols):
        item = data[:, i]
        rest = total - item  # madde çıkarılmış toplam

        # Düzeltilmiş madde-toplam korelasyonu
        corr = float(np.corrcoef(item, rest)[0, 1])

        # Madde silindiğinde alpha
        rest_data = np.delete(data, i, axis=1)
        k2 = k - 1
        iv2 = rest_data.var(axis=0, ddof=1).sum()
        tv2 = rest_data.sum(axis=1).var(ddof=1)
        alpha_if_deleted = float((k2 / (k2 - 1)) * (1 - iv2 / tv2)) if tv2 > 0 else float('nan')

        item_stats.append({
            'item': str(col),
            'mean': round(float(item.mean()), 3),
            'std': round(float(item.std(ddof=1)), 3),
            'corrected_itc': round(corr, 3),
            'alpha_if_deleted': round(alpha_if_deleted, 3),
        })

    return {
        'n_items': k,
        'n_cases': n,
        'alpha': round(float(alpha), 3),
        'interpretation': _interpret(alpha),
        'item_stats': item_stats,
    }


def _interpret(alpha: float) -> str:
    if alpha < 0.50:
        return 'Kabul Edilemez (α < 0.50)'
    if alpha < 0.60:
        return 'Düşük (0.50 ≤ α < 0.60)'
    if alpha < 0.70:
        return 'Kabul Edilebilir (0.60 ≤ α < 0.70)'
    if alpha < 0.80:
        return 'İyi (0.70 ≤ α < 0.80)'
    if alpha < 0.90:
        return 'Çok İyi (0.80 ≤ α < 0.90)'
    return 'Mükemmel (α ≥ 0.90)'


def build_pdf(result: dict, filename: str, df=None) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    )
    from .pdf_fonts import register_fonts
    register_fonts()

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title2', parent=styles['Heading1'], fontSize=16, spaceAfter=6,
                                 fontName='DejaVuSans')
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, spaceAfter=4,
                              fontName='DejaVuSans')
    normal = ParagraphStyle('Normal2', parent=styles['Normal'], fontName='DejaVuSans')

    story = []

    # Başlık
    story.append(Paragraph('Güvenilirlik Analizi Raporu', title_style))
    story.append(Paragraph(f'Dosya: {filename}', normal))
    story.append(Spacer(1, 0.4*cm))

    # Özet kutusu
    alpha = result['alpha']
    summary_data = [
        ['Madde Sayısı', str(result['n_items'])],
        ['Katılımcı Sayısı', str(result['n_cases'])],
        ['Cronbach Alpha (α)', f"{alpha:.3f}"],
        ['Yorum', result['interpretation']],
    ]
    t = Table(summary_data, colWidths=[7*cm, 9*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('BACKGROUND', (1, 2), (1, 2), _alpha_color(alpha)),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.6*cm))

    # Madde istatistikleri tablosu
    story.append(Paragraph('Madde İstatistikleri', h2_style))
    headers = ['Madde', 'Ort.', 'SS', 'Düz. M-T Kor.', 'Silinince α']
    rows = [headers]
    for s in result['item_stats']:
        rows.append([
            str(s['item']),
            f"{s['mean']:.3f}",
            f"{s['std']:.3f}",
            f"{s['corrected_itc']:.3f}",
            f"{s['alpha_if_deleted']:.3f}",
        ])

    col_w = [5*cm, 2.5*cm, 2.5*cm, 3.5*cm, 3*cm]
    tbl = Table(rows, colWidths=col_w)
    tbl.setStyle(TableStyle([
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
    story.append(tbl)

    doc.build(story)
    return buf.getvalue()


def _alpha_color(alpha: float):
    from reportlab.lib import colors
    if alpha >= 0.80:
        return colors.HexColor('#d4edda')
    if alpha >= 0.70:
        return colors.HexColor('#fff3cd')
    return colors.HexColor('#f8d7da')
