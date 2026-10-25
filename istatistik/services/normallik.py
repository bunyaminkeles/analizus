"""
Normallik Testi — Shapiro-Wilk, çarpıklık/basıklık, Q-Q plot
Girdi: pandas DataFrame (her sütun bir değişken)
"""
import io
import math
import numpy as np
from django.utils.translation import gettext


def analyze(df, columns=None) -> dict:
    from scipy import stats as sp_stats

    df_num = df.select_dtypes(include=[np.number])
    if columns:
        valid = [c for c in columns if c in df_num.columns]
        if not valid:
            raise ValueError(gettext('Seçilen sütunlar sayısal değil veya bulunamadı.'))
        df_num = df_num[valid]
    if df_num.empty:
        raise ValueError(gettext('Hiç sayısal sütun bulunamadı.'))

    results = []
    for col in df_num.columns:
        data = df_num[col].dropna().values
        n = len(data)
        if n < 3:
            continue

        skew = float(sp_stats.skew(data))
        kurt = float(sp_stats.kurtosis(data))  # excess kurtosis

        if n <= 5000:
            stat, p = sp_stats.shapiro(data)
            test_name = gettext('Shapiro-Wilk')
            test_stat_label = 'W'
        else:
            # Shapiro-Wilk 5000+ için güvenilmez; D'Agostino K² kullan
            stat, p = sp_stats.normaltest(data)
            test_name = gettext("D'Agostino K²")
            test_stat_label = 'K²'

        is_normal = bool(p >= 0.05)

        # ±1.96 kritik değer çarpıklık/basıklığın standart hatasına bölünmüş
        # z-skoruna uygulanır, ham değere değil (views.py "Çarpıklık &
        # Basıklık" açıklamasıyla tutarlı)
        ses = math.sqrt(6 * n * (n - 1) / ((n - 2) * (n + 1) * (n + 3)))
        skew_ok = abs(skew / ses) < 1.96
        if n > 3:
            sek = 2 * ses * math.sqrt((n * n - 1) / ((n - 3) * (n + 5)))
            kurt_ok = abs(kurt / sek) < 1.96
        else:
            kurt_ok = True

        if is_normal and skew_ok and kurt_ok:
            recommendation = gettext('Parametrik test kullanılabilir')
            rec_color = 'success'
        elif is_normal or (skew_ok and kurt_ok):
            recommendation = gettext('Parametrik test kullanılabilir (sınırda)')
            rec_color = 'warning'
        else:
            recommendation = gettext('Non-parametrik test önerilir')
            rec_color = 'danger'

        results.append({
            'variable': str(col),
            'n': n,
            'mean': round(float(data.mean()), 3),
            'std': round(float(data.std(ddof=1)), 3),
            'skewness': round(skew, 3),
            'kurtosis': round(kurt, 3),
            'shapiro_stat': round(float(stat), 4),
            'shapiro_p': round(float(p), 4),
            'test_name': test_name,
            'test_stat_label': test_stat_label,
            'is_normal': is_normal,
            'recommendation': recommendation,
            'rec_color': rec_color,
        })

    if not results:
        raise ValueError(gettext('En az 3 geçerli değere sahip sayısal değişken bulunamadı.'))

    all_normal = all(r['is_normal'] for r in results)
    any_normal = any(r['is_normal'] for r in results)
    if all_normal:
        overall = gettext('Tüm değişkenler normal dağılım gösteriyor. Parametrik testler uygundur.')
    elif any_normal:
        overall = gettext('Bazı değişkenler normal dağılımdan sapıyor. Değişken bazında karar veriniz.')
    else:
        overall = gettext('Değişkenler normal dağılım göstermiyor. Non-parametrik testler önerilir.')

    return {'variables': results, 'overall_recommendation': overall}


def build_pdf(result: dict, filename: str, df=None) -> bytes:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from scipy import stats as sp_stats
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
    )
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    # Türkçe karakter desteği için DejaVu fontlarını kaydet
    _register_fonts()
    from .pdf_fonts import append_ai_comment

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
    story.append(Paragraph(gettext('Normallik Testi Raporu'), title_style))
    story.append(Paragraph(gettext('Dosya: %(filename)s') % {'filename': filename}, normal))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(result['overall_recommendation'], normal))
    story.append(Spacer(1, 0.5*cm))

    # Özet tablo
    story.append(Paragraph(gettext('Normallik Test Sonuçları'), h2_style))
    headers = [gettext('Değişken'), 'N', gettext('Ort.'), gettext('SS'), gettext('Çarpıklık'), gettext('Basıklık'), gettext('Test'), gettext('İstatistik'), 'p', gettext('Normal?')]
    rows = [headers]
    for r in result['variables']:
        rows.append([
            str(r['variable']),
            str(r['n']),
            f"{r['mean']:.3f}",
            f"{r['std']:.3f}",
            f"{r['skewness']:.3f}",
            f"{r['kurtosis']:.3f}",
            r['test_name'],
            f"{r['test_stat_label']} = {r['shapiro_stat']:.4f}",
            f"{r['shapiro_p']:.4f}",
            gettext('Evet') if r['is_normal'] else gettext('Hayır'),
        ])

    col_w = [2.6*cm, 0.8*cm, 1.5*cm, 1.5*cm, 1.7*cm, 1.7*cm, 2.2*cm, 2.2*cm, 1.4*cm, 1.3*cm]
    tbl = Table(rows, colWidths=col_w)
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    # Renklendir: hayır = kırmızı
    for i, r in enumerate(result['variables'], start=1):
        bg = colors.HexColor('#d4edda') if r['is_normal'] else colors.HexColor('#f8d7da')
        tbl.setStyle(TableStyle([('BACKGROUND', (-1, i), (-1, i), bg)]))
    story.append(tbl)

    # Q-Q plotlar (ilk 6 değişken)
    vars_for_plot = result['variables'][:6]
    if vars_for_plot:
        story.append(Spacer(1, 0.6*cm))
        story.append(Paragraph(gettext('Q-Q Grafikleri'), h2_style))
        df_num = df.select_dtypes(include=[np.number]) if df is not None else None
        for r in vars_for_plot:
            col_data = None
            if df_num is not None and r['variable'] in df_num.columns:
                col_data = df_num[r['variable']].dropna().values
            img_buf = _qq_plot(r, col_data)
            img = Image(img_buf, width=14*cm, height=7*cm)
            story.append(img)
            story.append(Spacer(1, 0.3*cm))

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(gettext('APA Formatında Raporlama'), h2_style))
    apa_lines = []
    for r in result['variables']:
        # APA: 'p < .001' ya da 'p = 0.11' (önceden 'p = < .001' yazıyordu)
        p_s = 'p < .001' if r['shapiro_p'] < 0.001 else f"p = {r['shapiro_p']}"
        # Tam cümle msgid — dillerde kelime sırası farklı; {test}/{stat} gerçekte
        # uygulanan yönteme göre değişir (n<=5000 Shapiro-Wilk, n>5000 D'Agostino K²)
        # {süslü} yer tutucu: şablondaki {% trans %} %-işaretini kaçışladığından
        # Python ve JS ancak bu biçimde AYNI msgid'i paylaşır
        tmpl = (gettext('{var} değişkeni {test} testi ile incelenmiş ve normal dağılım gösterdiği belirlenmiştir ({stat} = {w}, {p}).')
                if r['is_normal'] else
                gettext('{var} değişkeni {test} testi ile incelenmiş ve normal dağılım göstermediği belirlenmiştir ({stat} = {w}, {p}).'))
        apa_lines.append(tmpl.format(var=r['variable'], test=r['test_name'], stat=r['test_stat_label'], w=r['shapiro_stat'], p=p_s))
    apa_text = ' '.join(apa_lines)
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


def _register_fonts():
    from .pdf_fonts import register_fonts
    register_fonts()


def _qq_plot(r: dict, data=None) -> io.BytesIO:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from scipy import stats as sp_stats

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    fig.suptitle(gettext('Değişken: %(var)s (N=%(n)s)') % {'var': r['variable'], 'n': r['n']}, fontsize=12)

    # Histogram
    ax1 = axes[0]
    ax1.set_title(gettext('Dağılım Histogramı'))
    ax1.set_xlabel(gettext('Değer'))
    ax1.set_ylabel(gettext('Frekans'))
    if data is not None and len(data) > 0:
        ax1.hist(data, bins='auto', color='steelblue', edgecolor='white', alpha=0.8)
        # Normal eğrisi üst üste
        import numpy as _np
        x = _np.linspace(data.min(), data.max(), 200)
        pdf = sp_stats.norm.pdf(x, loc=data.mean(), scale=data.std(ddof=1))
        ax1_twin = ax1.twinx()
        ax1_twin.plot(x, pdf, 'r-', linewidth=1.5, label='Normal')
        ax1_twin.set_ylabel(gettext('Yoğunluk'), color='red', fontsize=8)
        ax1_twin.tick_params(axis='y', labelcolor='red', labelsize=7)
    else:
        ax1.text(0.5, 0.5, gettext('Ham veri mevcut değil'), ha='center', va='center',
                 transform=ax1.transAxes, color='grey')

    # Q-Q plot
    ax2 = axes[1]
    ax2.set_title(gettext('Q-Q Plot (Teorik Normal)'))
    if data is not None and len(data) > 0:
        (osm, osr), (slope, intercept, _) = sp_stats.probplot(data, dist='norm')
        ax2.scatter(osm, osr, s=15, color='steelblue', alpha=0.7)
        import numpy as _np
        line_x = _np.array([osm[0], osm[-1]])
        ax2.plot(line_x, slope * line_x + intercept, 'r-', linewidth=1.5)
        ax2.set_xlabel(gettext('Teorik Kantiller'))
        ax2.set_ylabel(gettext('Örnek Kantiller'))
        color = '#28a745' if r['is_normal'] else '#dc3545'
        ax2.text(0.05, 0.95,
                 f"W={r['shapiro_stat']}, p={r['shapiro_p']}",
                 ha='left', va='top', transform=ax2.transAxes,
                 fontsize=9, color=color,
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
    else:
        color = '#28a745' if r['is_normal'] else '#dc3545'
        ax2.text(0.5, 0.5,
                 f"W = {r['shapiro_stat']}\np = {r['shapiro_p']}\n{r['recommendation']}",
                 ha='center', va='center', transform=ax2.transAxes,
                 fontsize=12, color=color,
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        ax2.axis('off')

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf
