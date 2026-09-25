"""
Wilcoxon İşaret Testi (Wilcoxon Signed-Rank Test).
İki bağımlı (eşleştirilmiş) ölçümü karşılaştıran non-parametrik test.
Bağımlı t-testinin parametrik olmayan alternatifi.
"""
import io
from django.utils.translation import gettext
import numpy as np
from scipy import stats


def analyze(df, col1: str, col2: str) -> dict:
    if col1 not in df.columns:
        raise ValueError(gettext('"%(col1)s" sütunu bulunamadı.') % {'col1': col1})
    if col2 not in df.columns:
        raise ValueError(gettext('"%(col2)s" sütunu bulunamadı.') % {'col2': col2})
    if col1 == col2:
        raise ValueError(gettext('İki farklı sütun seçilmelidir.'))

    sub = df[[col1, col2]].dropna()
    if len(sub) < 5:
        raise ValueError(gettext('En az 5 eşleştirilmiş gözlem gereklidir, %(sub)s çift bulundu.') % {'sub': len(sub)})

    x = sub[col1].values.astype(float)
    y = sub[col2].values.astype(float)

    diff = y - x
    nonzero = diff[diff != 0]
    if len(nonzero) == 0:
        raise ValueError(gettext('İki sütun arasında hiç fark bulunamadı (tüm farklar sıfır).'))

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
        return gettext('İhmal edilebilir etki (r < .10)')
    if r < 0.3:
        return gettext('Küçük etki (.10 ≤ r < .30)')
    if r < 0.5:
        return gettext('Orta düzey etki (.30 ≤ r < .50)')
    return gettext('Büyük etki (r ≥ .50)')


def _conclusion(p, col1, col2, med1, med2) -> str:
    # Tam cümle msgid'ler — 'artış/azalış' parçası ve '…tir' eki çevrilemez.
    # Yön: diff = col2 − col1 → med2 > med1 ise ikinci ölçümde artış (doğru).
    v = {'c1': col1, 'c2': col2, 'p': ('p < .001' if p < 0.001 else f'p = {p:.4f}'), 'm1': f'{med1:.3f}', 'm2': f'{med2:.3f}'}
    if float(p) < 0.05:
        if med2 > med1:
            return gettext('{c1} ile {c2} ölçümleri arasında istatistiksel olarak anlamlı bir fark bulunmaktadır '
                           '({p}). Medyan değerleri sırasıyla {m1} ve {m2} olup ikinci ölçümde artış '
                           'gözlemlenmiştir.').format(**v)
        return gettext('{c1} ile {c2} ölçümleri arasında istatistiksel olarak anlamlı bir fark bulunmaktadır '
                       '({p}). Medyan değerleri sırasıyla {m1} ve {m2} olup ikinci ölçümde azalış '
                       'gözlemlenmiştir.').format(**v)
    return gettext('{c1} ile {c2} ölçümleri arasında istatistiksel olarak anlamlı bir fark bulunmamaktadır '
                   '({p}). Medyan değerleri sırasıyla {m1} ve {m2} olarak bulunmuştur.').format(**v)


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
    story.append(Paragraph(gettext('Wilcoxon İşaret Testi Raporu'), title_s))
    story.append(Paragraph(gettext('Dosya: %(filename)s') % {'filename': filename}, norm_s))
    story.append(Spacer(1, 0.4*cm))

    # Betimsel istatistikler
    story.append(Paragraph(gettext('Betimsel İstatistikler'), h2_s))
    desc_header = ['', result['col1'], result['col2']]
    desc_rows = [
        desc_header,
        ['n', str(result['n']), str(result['n'])],
        [gettext('Medyan'), f"{result['median1']:.3f}", f"{result['median2']:.3f}"],
        [gettext('Ortalama'), f"{result['mean1']:.3f}", f"{result['mean2']:.3f}"],
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
    story.append(Paragraph(gettext('Fark İstatistikleri'), h2_s))
    diff_rows = [
        [gettext('Pozitif fark (n)'), str(result['n_positive'])],
        [gettext('Negatif fark (n)'), str(result['n_negative'])],
        [gettext('Eşit (n)'), str(result['n_ties'])],
        [gettext('Ortalama fark'), f"{result['mean_diff']:.3f}"],
        [gettext('Medyan fark'), f"{result['median_diff']:.3f}"],
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
    story.append(Paragraph(gettext('Test Sonuçları'), h2_s))
    sig = result['significant']
    res_rows = [
        [gettext('W istatistiği'), f"{result['w_stat']:.3f}"],
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
    # 'p < .001' / 'p = 0.123' (önceden 'p 0.123' — eşittir eksikti); şablon JS ile ortak msgid
    v = dict(c1=result['col1'], c2=result['col2'], w=f"{result['w_stat']:.3f}",
             p='p < .001' if result['p_value'] < 0.001 else f"p = {result['p_value']:.3f}",
             r=f"{abs(result['r_rb']):.3f}", effect=result['effect_interpretation'], n=result['n'])
    if result['significant']:
        apa_text = gettext('Wilcoxon işaret testi sonucunda {c1} ve {c2} ölçümleri arasındaki fark istatistiksel olarak '
                           'anlamlı bulunmuştur, W = {w}, {p}, r = {r} ({effect}) (N = {n}).').format(**v)
    else:
        apa_text = gettext('Wilcoxon işaret testi sonucunda {c1} ve {c2} ölçümleri arasındaki fark istatistiksel olarak '
                           'anlamlı bulunmamıştır, W = {w}, {p}, r = {r} ({effect}) (N = {n}).').format(**v)
    apa_tbl = Table([[Paragraph(apa_text, norm_s)]], colWidths=[16*cm])
    apa_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff8f0')),
        ('BOX', (0, 0), (-1, -1), 1, HEADER_COLOR),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(apa_tbl)

    doc.build(story)
    return buf.getvalue()
