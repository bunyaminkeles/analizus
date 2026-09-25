"""
Mann-Whitney U Testi (Wilcoxon sıra toplamı testi).
İki bağımsız grubun dağılımını karşılaştıran non-parametrik test.
t-testinin parametrik olmayan alternatifi.
"""
import io
from django.utils.translation import gettext
import numpy as np
from scipy import stats


def analyze(df, group_col: str, dep_col: str) -> dict:
    if group_col not in df.columns:
        raise ValueError(gettext('"%(group_col)s" sütunu bulunamadı.') % {'group_col': group_col})
    if dep_col not in df.columns:
        raise ValueError(gettext('"%(dep_col)s" sütunu bulunamadı.') % {'dep_col': dep_col})

    sub = df[[group_col, dep_col]].dropna()
    groups = sub[group_col].unique()
    if len(groups) != 2:
        raise ValueError(
            gettext('Mann-Whitney U testi için tam 2 grup gereklidir. "%(group_col)s" sütununda %(groups)s farklı değer bulundu.') % {'group_col': group_col, 'groups': len(groups)})

    g1_label, g2_label = str(groups[0]), str(groups[1])
    g1 = sub[sub[group_col] == groups[0]][dep_col].values.astype(float)
    g2 = sub[sub[group_col] == groups[1]][dep_col].values.astype(float)

    if len(g1) < 3 or len(g2) < 3:
        raise ValueError(gettext('Her grupta en az 3 gözlem olmalıdır.'))

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
        'test_label': gettext('Mann-Whitney U Testi'),
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
        return gettext('İhmal edilebilir etki (r < .10)')
    if r < 0.3:
        return gettext('Küçük etki (.10 ≤ r < .30)')
    if r < 0.5:
        return gettext('Orta düzey etki (.30 ≤ r < .50)')
    return gettext('Büyük etki (r ≥ .50)')


def _conclusion(p, g1, g2, dep, med1, med2) -> str:
    # Tam cümle msgid'ler (yön parçası + 'tir' eki çevrilemez)
    v = {'g1': g1, 'g2': g2, 'dep': dep, 'p': ('p < .001' if p < 0.001 else f'p = {p:.4f}'), 'm1': f'{med1:.3f}', 'm2': f'{med2:.3f}'}
    if float(p) < 0.05:
        if med1 > med2:
            return gettext('{g1} grubu ile {g2} grubu arasında {dep} açısından istatistiksel olarak anlamlı '
                           'bir fark bulunmaktadır ({p}). {g1} grubunun medyanı ({m1}), {g2} grubuna '
                           '({m2}) göre daha yüksektir.').format(**v)
        return gettext('{g1} grubu ile {g2} grubu arasında {dep} açısından istatistiksel olarak anlamlı '
                       'bir fark bulunmaktadır ({p}). {g1} grubunun medyanı ({m1}), {g2} grubuna '
                       '({m2}) göre daha düşüktür.').format(**v)
    return gettext('{g1} grubu ile {g2} grubu arasında {dep} açısından istatistiksel olarak anlamlı '
                   'bir fark bulunmamaktadır ({p}).').format(**v)


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
    story.append(Paragraph(gettext('Mann-Whitney U Testi Raporu'), title_s))
    story.append(Paragraph(gettext('Dosya: %(filename)s') % {'filename': filename}, norm_s))
    story.append(Spacer(1, 0.4*cm))

    # Grup istatistikleri
    story.append(Paragraph(gettext('Grup İstatistikleri'), h2_s))
    gs_header = [gettext('Grup'), 'n', gettext('Medyan'), gettext('Ort.'), 'SS', gettext('Ort. Sıra')]
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
    story.append(Paragraph(gettext('Test Sonuçları'), h2_s))
    sig = result['significant']
    res_rows = [
        [gettext('U istatistiği'), f"{result['u_stat']:.3f}"],
        [gettext('p-değeri'), f"{result['p_value']:.4f}"],
        [gettext('Etki Büyüklüğü (r)'), f"{result['r_rb']:.3f}"],
        [gettext('Etki Yorumu'), result['effect_interpretation']],
        [gettext('Sonuç'), gettext('Anlamlı (p < .05)') if sig else gettext('Anlamlı değil (p ≥ .05)')],
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

    story.append(Paragraph(gettext('Yorum'), h2_s))
    story.append(Paragraph(result['conclusion'], norm_s))

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(gettext('APA Formatında Raporlama'), h2_s))
    # 'p < .001' / 'p = 0.123'; anlamlı/anlamsız ayrı tam cümle — şablon JS ile ortak msgid
    v = dict(group=result['group_col'], g1=result['g1_label'], g2=result['g2_label'], dep=result['dep_col'],
             u=f"{result['u_stat']:.3f}",
             p='p < .001' if result['p_value'] < 0.001 else f"p = {result['p_value']:.3f}",
             r=f"{abs(result['r_rb']):.3f}", effect=result['effect_interpretation'])
    if result['significant']:
        apa_text = gettext('Mann-Whitney U testi sonucunda {group} grupları ({g1} ve {g2}) arasında {dep} açısından '
                           'istatistiksel olarak anlamlı bir fark bulunmuştur, U = {u}, {p}, r = {r} ({effect}).').format(**v)
    else:
        apa_text = gettext('Mann-Whitney U testi sonucunda {group} grupları ({g1} ve {g2}) arasında {dep} açısından '
                           'anlamlı bir fark bulunmamıştır, U = {u}, {p}, r = {r} ({effect}).').format(**v)
    apa_tbl = Table([[Paragraph(apa_text, norm_s)]], colWidths=[16*cm])
    apa_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff8f0')),
        ('BOX', (0, 0), (-1, -1), 1, HEADER_COLOR),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(apa_tbl)

    doc.build(story)
    return buf.getvalue()
