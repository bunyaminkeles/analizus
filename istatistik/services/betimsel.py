"""
Betimleyici İstatistik Raporu
Girdi: pandas DataFrame
"""
import io
from django.utils.translation import gettext
import numpy as np


def analyze(df, columns=None) -> dict:
    from scipy import stats as sp_stats

    if columns:
        valid = [c for c in columns if c in df.columns]
        if valid:
            df = df[valid]
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
            skew = float(sp_stats.skew(numeric))
            kurt = float(sp_stats.kurtosis(numeric))  # excess kurtosis
            mode_val = _mode_or_none(numeric)
            results.append({
                'variable': str(col),
                'type': 'continuous',
                'n': n,
                'mean': round(float(numeric.mean()), 3),
                'std': round(float(numeric.std(ddof=1)), 3),
                'variance': round(float(numeric.var(ddof=1)), 3),
                'mode': mode_val,
                'min': round(float(numeric.min()), 3),
                'max': round(float(numeric.max()), 3),
                'median': round(float(numeric.median()), 3),
                'q1': round(q1, 3),
                'q3': round(q3, 3),
                'skewness': round(skew, 3),
                'kurtosis': round(kurt, 3),
                'shape_interpretation': _interpret_shape(skew, kurt),
            })

    if not results:
        raise ValueError(gettext('Analiz edilecek sütun bulunamadı.'))

    return {'variables': results, 'n_rows': len(df)}


def _mode_or_none(numeric):
    """En sık tekrar eden değer (>1 kez); tüm değerler tekilse (gerçek sürekli
    veri) mod anlamsız olduğundan None döner."""
    counts = numeric.value_counts()
    if counts.empty or counts.iloc[0] <= 1:
        return None
    top_count = counts.iloc[0]
    return round(float(counts[counts == top_count].index.min()), 3)


def _interpret_shape(skew: float, kurt: float) -> str:
    if abs(skew) <= 1:
        skew_label = gettext('Normal')
    elif abs(skew) <= 2:
        skew_label = gettext('Hafif çarpık')
    else:
        skew_label = gettext('Belirgin çarpık')
    kurt_label = gettext('Normal') if abs(kurt) <= 2 else gettext('Aşırı')
    return gettext('Çarpıklık: %(s)s · Basıklık: %(k)s') % {'s': skew_label, 'k': kurt_label}


def build_pdf(result: dict, filename: str, df=None) -> bytes:
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
    from .pdf_fonts import register_fonts, append_ai_comment
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
    h3_style = ParagraphStyle('H3', parent=styles['Heading3'], fontSize=10, spaceAfter=3,
                              fontName='DejaVuSans')
    normal = ParagraphStyle('Normal2', parent=styles['Normal'], fontName='DejaVuSans')

    story = []
    story.append(Paragraph(gettext('Betimleyici İstatistik Raporu'), title_style))
    story.append(Paragraph(gettext('Dosya: %(filename)s') % {'filename': filename} + '  |  ' + gettext('Satır sayısı: %(n)s') % {'n': result['n_rows']}, normal))
    story.append(Spacer(1, 0.5*cm))

    cont_vars = [v for v in result['variables'] if v['type'] == 'continuous']
    cat_vars = [v for v in result['variables'] if v['type'] == 'categorical']

    # Sürekli değişkenler özet tablosu
    if cont_vars:
        story.append(Paragraph(gettext('Sürekli Değişkenler'), h2_style))
        headers = [gettext('Değişken'), 'N', gettext('Ort.'), gettext('SS'), 'Min', gettext('Medyan'), gettext('Maks'), 'Q1', 'Q3']
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

        # Dağılım şekli ve ek ölçüler (Mod, Varyans, Çarpıklık, Basıklık)
        story.append(Paragraph(gettext('Dağılım Şekli ve Ek Ölçüler'), h2_style))
        shape_headers = [gettext('Değişken'), gettext('Mod'), gettext('Varyans'),
                          gettext('Çarpıklık'), gettext('Basıklık'), gettext('Yorum')]
        shape_rows = [shape_headers]
        for v in cont_vars:
            shape_rows.append([
                str(v['variable']),
                f"{v['mode']:.3f}" if v['mode'] is not None else '—',
                f"{v['variance']:.3f}",
                f"{v['skewness']:.3f}",
                f"{v['kurtosis']:.3f}",
                v['shape_interpretation'],
            ])
        shape_col_w = [3*cm, 1.8*cm, 2*cm, 2*cm, 2*cm, 6*cm]
        shape_tbl = Table(shape_rows, colWidths=shape_col_w)
        shape_tbl.setStyle(_base_table_style())
        story.append(shape_tbl)
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
        story.append(Paragraph(gettext('Kategorik Değişkenler'), h2_style))
        for v in cat_vars:
            story.append(Paragraph(gettext('%(var)s  (N=%(n)s, %(k)s kategori)') % {'var': v['variable'], 'n': v['n'], 'k': v['unique']}, h3_style))
            freq_rows = [[gettext('Değer'), gettext('Frekans'), gettext('Yüzde (%)')]]
            for row in v['freq_table'][:20]:
                freq_rows.append([str(row['value']), str(row['freq']), gettext('%%%(value)s') % {'value': f"{row['pct']:.1f}"}])
            tbl2 = Table(freq_rows, colWidths=[7*cm, 4*cm, 4*cm])
            tbl2.setStyle(_base_table_style())
            story.append(tbl2)

            # Bar grafik
            img_buf = _bar_chart(v)
            img = Image(img_buf, width=12*cm, height=5*cm)
            story.append(img)
            story.append(Spacer(1, 0.4*cm))

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(gettext('APA Formatında Raporlama'), h2_style))
    cont_vars_for_apa = [v for v in result['variables'] if v['type'] == 'continuous']
    # {süslü} yer tutucular — şablondaki JS ile aynı msgid'ler
    if cont_vars_for_apa:
        lines = [gettext('{var} değişkeni için ortalama = {mean} (SS = {sd})').format(
                     var=v['variable'], mean=f"{v['mean']:.2f}", sd=f"{v['std']:.2f}")
                 for v in cont_vars_for_apa]
        apa_text = gettext('Araştırmaya katılan {n} kişinin puanlarına ilişkin betimleyici istatistikler '
                           'incelendiğinde {lines} olarak bulunmuştur.').format(n=result['n_rows'], lines='; '.join(lines))
    else:
        apa_text = gettext('Araştırmaya katılan {n} kişiye ait {k} değişkene ilişkin betimleyici istatistikler '
                           'yukarıda sunulmuştur.').format(n=result['n_rows'], k=len(result['variables']))
    apa_tbl = Table([[Paragraph(apa_text, normal)]], colWidths=[16*cm])
    apa_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f4ff')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1e3a5f')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(apa_tbl)
    append_ai_comment(story, result, normal, '#f0f4ff', '#1e3a5f')

    doc.build(story)
    return buf.getvalue()


def _base_table_style():
    from reportlab.lib import colors
    from reportlab.platypus import TableStyle
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
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
    ax.bar(['Min', 'Q1', gettext('Medyan'), 'Q3', gettext('Maks')],
           [v['min'], v['q1'], v['median'], v['q3'], v['max']],
           color=['#6c757d', '#17a2b8', '#007bff', '#17a2b8', '#6c757d'])
    ax.set_title(gettext('%(var)s — Özet  (Ort=%(mean)s, SS=%(sd)s)') % {'var': v['variable'], 'mean': f"{v['mean']:.2f}", 'sd': f"{v['std']:.2f}"})
    ax.set_ylabel(gettext('Değer'))
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
    ax.set_title(gettext('%(var)s — Frekans Dağılımı') % {'var': v['variable']})
    ax.set_ylabel(gettext('Frekans'))
    for bar, row in zip(bars, top):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                gettext('%%%(value)s') % {'value': f"{row['pct']:.1f}"}, ha='center', va='bottom', fontsize=7)
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf
