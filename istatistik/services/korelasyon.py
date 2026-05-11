"""
Korelasyon Matrisi Analizi
Girdi: pandas DataFrame (satır=gözlem, sütun=değişken)
Yöntem: Pearson, Spearman veya Kendall
"""
import io
import numpy as np


METHOD_LABELS = {
    'pearson': 'Pearson',
    'spearman': 'Spearman',
    'kendall': 'Kendall',
}


def analyze(df, method: str = 'pearson') -> dict:
    import pandas as pd
    from scipy import stats

    if method not in ('pearson', 'spearman', 'kendall'):
        method = 'pearson'

    df_num = df.select_dtypes(include=[np.number]).dropna()
    cols = list(df_num.columns)
    k = len(cols)
    n = len(df_num)

    if k < 2:
        raise ValueError('En az 2 sayısal sütun (değişken) gereklidir.')
    if n < 5:
        raise ValueError('En az 5 geçerli satır (gözlem) gereklidir.')

    corr_matrix = []
    pval_matrix = []

    for i, c1 in enumerate(cols):
        corr_row = []
        pval_row = []
        for j, c2 in enumerate(cols):
            if i == j:
                corr_row.append(1.0)
                pval_row.append(0.0)
            elif j < i:
                # Simetri — önceki değeri al
                corr_row.append(corr_matrix[j][i])
                pval_row.append(pval_matrix[j][i])
            else:
                x = df_num[c1].values
                y = df_num[c2].values
                if method == 'pearson':
                    r, p = stats.pearsonr(x, y)
                elif method == 'spearman':
                    r, p = stats.spearmanr(x, y)
                else:
                    r, p = stats.kendalltau(x, y)
                corr_row.append(round(float(r), 3))
                pval_row.append(round(float(p), 3))
        corr_matrix.append(corr_row)
        pval_matrix.append(pval_row)

    heatmap_png = _build_heatmap(corr_matrix, cols, method)

    return {
        'method': method,
        'method_label': METHOD_LABELS[method],
        'n_vars': k,
        'n_cases': n,
        'columns': cols,
        'corr_matrix': corr_matrix,
        'pval_matrix': pval_matrix,
        'heatmap_b64': heatmap_png,
    }


def _build_heatmap(corr_matrix, cols, method: str) -> str:
    """Matplotlib heatmap → base64 PNG string."""
    import base64
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors

    n = len(cols)
    fig_size = max(5, n * 0.8 + 2)
    fig, ax = plt.subplots(figsize=(fig_size, fig_size))
    fig.patch.set_facecolor('#0f0f23')
    ax.set_facecolor('#0f0f23')

    data = np.array(corr_matrix)
    cmap = plt.cm.RdYlGn
    im = ax.imshow(data, cmap=cmap, vmin=-1, vmax=1, aspect='auto')

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(cols, rotation=45, ha='right', color='white', fontsize=8)
    ax.set_yticklabels(cols, color='white', fontsize=8)

    for i in range(n):
        for j in range(n):
            val = corr_matrix[i][j]
            color = 'black' if 0.3 <= abs(val) <= 0.7 else 'white'
            ax.text(j, i, f'{val:.2f}', ha='center', va='center',
                    color=color, fontsize=max(6, 10 - n // 3))

    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.yaxis.set_tick_params(color='white')
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color='white')

    ax.set_title(f'{METHOD_LABELS[method]} Korelasyon Matrisi',
                 color='white', fontsize=11, pad=12)
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_edgecolor('#333366')

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


def build_pdf(result: dict, filename: str, df=None) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
    )
    from .pdf_fonts import register_fonts
    register_fonts()

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title2', parent=styles['Heading1'], fontSize=16,
                                 spaceAfter=6, fontName='DejaVuSans')
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12,
                              spaceAfter=4, fontName='DejaVuSans')
    normal = ParagraphStyle('Normal2', parent=styles['Normal'], fontName='DejaVuSans',
                            fontSize=9)

    story = []

    story.append(Paragraph('Korelasyon Matrisi Raporu', title_style))
    story.append(Paragraph(f'Dosya: {filename}', normal))
    story.append(Spacer(1, 0.3*cm))

    summary_data = [
        ['Yöntem', result['method_label']],
        ['Değişken Sayısı', str(result['n_vars'])],
        ['Gözlem Sayısı', str(result['n_cases'])],
    ]
    t = Table(summary_data, colWidths=[7*cm, 9*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.6*cm))

    # Heatmap
    if result.get('heatmap_b64'):
        import base64
        img_data = base64.b64decode(result['heatmap_b64'])
        img_buf = io.BytesIO(img_data)
        n = result['n_vars']
        img_size = min(14*cm, max(8*cm, n * 1.2 * cm))
        story.append(Paragraph('Korelasyon Isı Haritası', h2_style))
        story.append(Image(img_buf, width=img_size, height=img_size))
        story.append(Spacer(1, 0.6*cm))

    # Korelasyon tablosu
    story.append(Paragraph('Korelasyon Katsayıları (r)', h2_style))
    cols = result['columns']
    col_w = 16 * cm / (len(cols) + 1)
    header = [''] + [str(c)[:10] for c in cols]
    rows = [header]
    for i, c in enumerate(cols):
        row = [str(c)[:10]]
        for j in range(len(cols)):
            row.append(f"{result['corr_matrix'][i][j]:.3f}")
        rows.append(row)

    tbl = Table(rows, colWidths=[col_w] * (len(cols) + 1))
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), max(6, 9 - len(cols) // 4)),
        ('ROWBACKGROUNDS', (1, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ]
    # Köşegen hücreler gri
    for i in range(len(cols)):
        style_cmds.append(('BACKGROUND', (i+1, i+1), (i+1, i+1), colors.HexColor('#e8e8e8')))
    tbl.setStyle(TableStyle(style_cmds))
    story.append(tbl)
    story.append(Spacer(1, 0.6*cm))

    # P-değeri tablosu
    story.append(Paragraph('P-Değerleri', h2_style))
    p_rows = [header]
    for i, c in enumerate(cols):
        row = [str(c)[:10]]
        for j in range(len(cols)):
            p = result['pval_matrix'][i][j]
            row.append('—' if i == j else f"{p:.3f}")
        p_rows.append(row)

    ptbl = Table(p_rows, colWidths=[col_w] * (len(cols) + 1))
    pstyle_cmds = list(style_cmds)
    # p < 0.05 olan hücreleri yeşile boyama
    for i in range(len(cols)):
        for j in range(len(cols)):
            if i != j and result['pval_matrix'][i][j] < 0.05:
                pstyle_cmds.append(
                    ('BACKGROUND', (j+1, i+1), (j+1, i+1), colors.HexColor('#d4edda'))
                )
    ptbl.setStyle(TableStyle(pstyle_cmds))
    story.append(ptbl)

    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(
        '<font color="#666666" size="8">Not: Yeşil hücreler p &lt; 0.05 anlamına gelir (istatistiksel olarak anlamlı).</font>',
        ParagraphStyle('note', parent=styles['Normal'], fontName='DejaVuSans', fontSize=8)
    ))

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph('Tezinde Nasıl Raporlarsın?', h2_style))
    apa_text = (f"Değişkenler arasındaki ilişkiler {result['method_label']} korelasyon analizi ile "
                f"incelenmiştir (n = {result['n_cases']}). Korelasyon katsayıları ve p-değerleri "
                f"raporun ek tablosunda sunulmuştur (Cohen, 1988).")
    apa_tbl = Table([[Paragraph(apa_text, normal)]], colWidths=[16*cm])
    apa_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f4ff')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1e3a5f')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(apa_tbl)

    doc.build(story)
    return buf.getvalue()
