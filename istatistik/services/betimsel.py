"""
Betimleyici İstatistik Raporu
Girdi: pandas DataFrame
"""
import io
import numpy as np


def analyze(df) -> dict:
    results = []
    for col in df.columns:
        series = df[col].dropna()
        n = len(series)
        if n == 0:
            continue

        unique_count = series.nunique()
        # Kategorik eşiği: 10 veya altı unique değer VEYA object dtype
        is_categorical = (series.dtype == object) or (unique_count <= 10)

        if is_categorical:
            freq = series.value_counts()
            freq_table = [
                {
                    'value': str(v),
                    'freq': int(c),
                    'pct': round(c / n * 100, 1),
                }
                for v, c in freq.items()
            ]
            results.append({
                'variable': str(col),
                'type': 'categorical',
                'n': n,
                'unique': unique_count,
                'freq_table': freq_table,
            })
        else:
            numeric = series.astype(float)
            q1 = float(numeric.quantile(0.25))
            q3 = float(numeric.quantile(0.75))
            results.append({
                'variable': str(col),
                'type': 'continuous',
                'n': n,
                'mean': round(float(numeric.mean()), 3),
                'std': round(float(numeric.std(ddof=1)), 3),
                'min': round(float(numeric.min()), 3),
                'max': round(float(numeric.max()), 3),
                'median': round(float(numeric.median()), 3),
                'q1': round(q1, 3),
                'q3': round(q3, 3),
            })

    if not results:
        raise ValueError('Analiz edilecek sütun bulunamadı.')

    return {'variables': results, 'n_rows': len(df)}


def build_pdf(result: dict, filename: str) -> bytes:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
    )

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title2', parent=styles['Heading1'], fontSize=16, spaceAfter=6)
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, spaceAfter=4)
    h3_style = ParagraphStyle('H3', parent=styles['Heading3'], fontSize=10, spaceAfter=3)
    normal = styles['Normal']

    story = []
    story.append(Paragraph('Betimleyici İstatistik Raporu', title_style))
    story.append(Paragraph(f'Dosya: {filename}  |  Satır sayısı: {result["n_rows"]}', normal))
    story.append(Spacer(1, 0.5*cm))

    cont_vars = [v for v in result['variables'] if v['type'] == 'continuous']
    cat_vars = [v for v in result['variables'] if v['type'] == 'categorical']

    # Sürekli değişkenler özet tablosu
    if cont_vars:
        story.append(Paragraph('Sürekli Değişkenler', h2_style))
        headers = ['Değişken', 'N', 'Ort.', 'SS', 'Min', 'Medyan', 'Maks', 'Q1', 'Q3']
        rows = [headers]
        for v in cont_vars:
            rows.append([
                str(v['variable']),
                str(v['n']),
                f"{v['mean']:.3f}",
                f"{v['std']:.3f}",
                f"{v['min']:.3f}",
                f"{v['median']:.3f}",
                f"{v['max']:.3f}",
                f"{v['q1']:.3f}",
                f"{v['q3']:.3f}",
            ])
        col_w = [3.5*cm, 1.2*cm, 2*cm, 2*cm, 2*cm, 2.3*cm, 2*cm, 1.8*cm, 1.8*cm]
        tbl = Table(rows, colWidths=col_w)
        tbl.setStyle(_base_table_style())
        story.append(tbl)
        story.append(Spacer(1, 0.4*cm))

        # Histogram'lar (ilk 4)
        for v in cont_vars[:4]:
            img_buf = _histogram(v)
            img = Image(img_buf, width=13*cm, height=5*cm)
            story.append(img)
            story.append(Spacer(1, 0.2*cm))

    # Kategorik değişkenler
    if cat_vars:
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph('Kategorik Değişkenler', h2_style))
        for v in cat_vars:
            story.append(Paragraph(f"{v['variable']}  (N={v['n']}, {v['unique']} kategori)", h3_style))
            freq_rows = [['Değer', 'Frekans', 'Yüzde (%)']]
            for row in v['freq_table'][:20]:
                freq_rows.append([str(row['value']), str(row['freq']), f"{row['pct']:.1f}%"])
            tbl2 = Table(freq_rows, colWidths=[7*cm, 4*cm, 4*cm])
            tbl2.setStyle(_base_table_style())
            story.append(tbl2)

            # Bar grafik
            img_buf = _bar_chart(v)
            img = Image(img_buf, width=12*cm, height=5*cm)
            story.append(img)
            story.append(Spacer(1, 0.4*cm))

    doc.build(story)
    return buf.getvalue()


def _base_table_style():
    from reportlab.lib import colors
    from reportlab.platypus import TableStyle
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ])


def _histogram(v: dict) -> io.BytesIO:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.bar(['Min', 'Q1', 'Medyan', 'Q3', 'Maks'],
           [v['min'], v['q1'], v['median'], v['q3'], v['max']],
           color=['#6c757d', '#17a2b8', '#007bff', '#17a2b8', '#6c757d'])
    ax.set_title(f"{v['variable']} — Özet  (Ort={v['mean']:.2f}, SS={v['std']:.2f})")
    ax.set_ylabel('Değer')
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf


def _bar_chart(v: dict) -> io.BytesIO:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    top = v['freq_table'][:10]
    labels = [r['value'] for r in top]
    freqs = [r['freq'] for r in top]

    fig, ax = plt.subplots(figsize=(8, 3.5))
    bars = ax.bar(range(len(labels)), freqs, color='#007bff', alpha=0.8)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=30, ha='right', fontsize=8)
    ax.set_title(f"{v['variable']} — Frekans Dağılımı")
    ax.set_ylabel('Frekans')
    for bar, row in zip(bars, top):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f"{row['pct']:.1f}%", ha='center', va='bottom', fontsize=7)
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf
