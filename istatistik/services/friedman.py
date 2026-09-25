"""
Friedman Testi — non-parametrik tekrarlayan ölçümler testi.
3+ bağımlı (eşleştirilmiş) grubun medyanlarını karşılaştırır.
Tek yönlü tekrarlayan ölçümler ANOVA'nın parametrik olmayan alternatifi.
"""
import io
from django.utils.translation import gettext
import numpy as np
from itertools import combinations
from scipy import stats


def analyze(df, columns: list) -> dict:
    if not columns or len(columns) < 3:
        raise ValueError(gettext('Friedman testi için en az 3 sütun seçilmelidir.'))

    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(gettext('Sütunlar bulunamadı: %(v)s') % {'v': ', '.join(missing)})

    sub = df[columns].dropna()
    n = len(sub)
    k = len(columns)

    if n < 5:
        raise ValueError(gettext('En az 5 katılımcı gereklidir, %(n)s satır bulundu.') % {'n': n})

    arrays = [sub[c].values.astype(float) for c in columns]
    chi2, p_val = stats.friedmanchisquare(*arrays)

    # Kendall's W etki büyüklüğü
    kendall_w = float(chi2) / (n * (k - 1))
    df_val = k - 1

    # Betimsel istatistikler
    descriptives = []
    for c in columns:
        vals = sub[c].values.astype(float)
        descriptives.append({
            'col': c,
            'n': n,
            'mean': round(float(vals.mean()), 3),
            'median': round(float(np.median(vals)), 3),
            'std': round(float(vals.std(ddof=1)), 3),
            'min': round(float(vals.min()), 3),
            'max': round(float(vals.max()), 3),
        })

    # Post-hoc: pairwise Wilcoxon + Bonferroni
    pairs = list(combinations(range(k), 2))
    n_pairs = len(pairs)
    posthoc = []
    for i, j in pairs:
        w, p = stats.wilcoxon(arrays[i], arrays[j], alternative='two-sided')
        p_adj = min(float(p) * n_pairs, 1.0)
        posthoc.append({
            'col1': columns[i],
            'col2': columns[j],
            'W': round(float(w), 3),
            'p': round(float(p), 4),
            'p_adj': round(p_adj, 4),
            'significant': p_adj < 0.05,
        })

    return {
        'columns': columns,
        'n': n,
        'k': k,
        'chi2': round(float(chi2), 3),
        'df': df_val,
        'p_value': round(float(p_val), 4),
        'kendall_w': round(kendall_w, 3),
        'effect_interpretation': _interpret_w(kendall_w),
        'significant': float(p_val) < 0.05,
        'descriptives': descriptives,
        'posthoc': posthoc,
        'conclusion': _conclusion(p_val, columns),
    }


def _interpret_w(w: float) -> str:
    if w < 0.1:
        return gettext('İhmal edilebilir etki (W < .10)')
    if w < 0.3:
        return gettext('Küçük etki (.10 ≤ W < .30)')
    if w < 0.5:
        return gettext('Orta düzey etki (.30 ≤ W < .50)')
    return gettext('Büyük etki (W ≥ .50)')


def _conclusion(p, columns: list) -> str:
    col_str = ', '.join(columns)
    if float(p) < 0.05:
        return (gettext('%(col_str)s ölçümleri arasında istatistiksel olarak anlamlı bir fark bulunmaktadır (p = %(p)s). Post-hoc Wilcoxon testi (Bonferroni düzeltmeli) ile anlamlı farklı çiftler belirlenmiştir.') % {'col_str': col_str, 'p': f'{p:.4f}'})
    return (gettext('%(col_str)s ölçümleri arasında istatistiksel olarak anlamlı bir fark bulunmamaktadır (p = %(p)s).') % {'col_str': col_str, 'p': f'{p:.4f}'})


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
    HEADER_COLOR = colors.HexColor('#065f46')
    title_s = ParagraphStyle('T', parent=styles['Heading1'], fontSize=16, spaceAfter=6, fontName='DejaVuSans')
    h2_s    = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, spaceAfter=4, fontName='DejaVuSans')
    norm_s  = ParagraphStyle('N', parent=styles['Normal'], fontName='DejaVuSans', fontSize=9)

    story = []
    story.append(Paragraph(gettext('Friedman Testi Raporu'), title_s))
    story.append(Paragraph(gettext('Dosya: %(filename)s') % {'filename': filename}, norm_s))
    story.append(Spacer(1, 0.4*cm))

    # Betimsel
    story.append(Paragraph(gettext('Betimsel İstatistikler'), h2_s))
    desc_header = [gettext('Ölçüm'), 'n', gettext('Ort.'), gettext('Med.'), 'SS', gettext('Min'), gettext('Maks')]
    desc_rows = [desc_header] + [
        [d['col'], str(d['n']), f"{d['mean']:.3f}", f"{d['median']:.3f}",
         f"{d['std']:.3f}", f"{d['min']:.3f}", f"{d['max']:.3f}"]
        for d in result['descriptives']
    ]
    col_widths = [4.5*cm, 1.5*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2*cm]
    desc_tbl = Table(desc_rows, colWidths=col_widths)
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

    # Test sonuçları
    story.append(Paragraph(gettext('Test Sonuçları'), h2_s))
    sig = result['significant']
    res_rows = [
        [gettext('χ² istatistiği'), f"{result['chi2']:.3f}"],
        [gettext('Serbestlik derecesi (df)'), str(result['df'])],
        [gettext('p-değeri'), f"{result['p_value']:.4f}"],
        [gettext("Kendall's W"), f"{result['kendall_w']:.3f}"],
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
    story.append(Spacer(1, 0.4*cm))

    # Post-hoc
    if sig and result['posthoc']:
        story.append(Paragraph(gettext('Post-Hoc Karşılaştırmalar (Wilcoxon — Bonferroni)'), h2_s))
        ph_header = [gettext('Çift'), 'W', 'p', gettext('p (düz.)'), gettext('Anlamlı mı?')]
        ph_rows = [ph_header] + [
            [f"{r['col1']} vs {r['col2']}", f"{r['W']:.3f}",
             f"{r['p']:.4f}", f"{r['p_adj']:.4f}",
             gettext('Evet *') if r['significant'] else gettext('Hayır')]
            for r in result['posthoc']
        ]
        ph_tbl = Table(ph_rows, colWidths=[5.5*cm, 2*cm, 2.5*cm, 2.5*cm, 3.5*cm])
        ph_tbl.setStyle(TableStyle([
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
        story.append(ph_tbl)
        story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph(gettext('Yorum'), h2_s))
    story.append(Paragraph(result['conclusion'], norm_s))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(gettext('APA Formatında Raporlama'), h2_s))
    # 'p < .001' / 'p = 0.123' (önceden 'p 0.123' — eşittir eksikti); şablon JS ile ortak msgid
    v = dict(cols=', '.join(result['columns']), df=result['df'], n=result['n'], chi2=f"{result['chi2']:.3f}",
             p='p < .001' if result['p_value'] < 0.001 else f"p = {result['p_value']:.3f}",
             w=f"{result['kendall_w']:.3f}", effect=result['effect_interpretation'])
    if result['significant']:
        apa_text = gettext('Friedman testi sonucuna göre {cols} ölçümleri arasındaki fark istatistiksel olarak anlamlı '
                           'bulunmuştur, χ²({df}, N = {n}) = {chi2}, {p}, W = {w} ({effect}).').format(**v)
    else:
        apa_text = gettext('Friedman testi sonucuna göre {cols} ölçümleri arasındaki fark istatistiksel olarak anlamlı '
                           'bulunmamıştır, χ²({df}, N = {n}) = {chi2}, {p}, W = {w} ({effect}).').format(**v)
    apa_tbl = Table([[Paragraph(apa_text, norm_s)]], colWidths=[16*cm])
    apa_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0fdf4')),
        ('BOX', (0, 0), (-1, -1), 1, HEADER_COLOR),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(apa_tbl)

    doc.build(story)
    return buf.getvalue()
