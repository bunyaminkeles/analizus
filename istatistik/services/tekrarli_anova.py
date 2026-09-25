"""
Tekrarlayan Ölçümler ANOVA (One-Way Repeated Measures ANOVA).
Aynı katılımcıların 3+ farklı koşulda/zamanda ölçüldüğü parametrik test.
Friedman testinin parametrik alternatifi (normallik varsayımı gerektirir).
"""
import io
from django.utils.translation import gettext
import numpy as np
from itertools import combinations
from scipy import stats


def analyze(df, columns: list) -> dict:
    if not columns or len(columns) < 3:
        raise ValueError(gettext('Tekrarlayan ölçümler ANOVA için en az 3 sütun seçilmelidir.'))

    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(gettext('Sütunlar bulunamadı: %(v)s') % {'v': ', '.join(missing)})

    sub = df[columns].dropna()
    n = len(sub)
    k = len(columns)

    if n < 5:
        raise ValueError(gettext('En az 5 katılımcı gereklidir, %(n)s satır bulundu.') % {'n': n})

    arrays = [sub[c].values.astype(float) for c in columns]

    # Betimsel istatistikler
    descriptives = []
    for c, vals in zip(columns, arrays):
        descriptives.append({
            'col': c,
            'n': n,
            'mean': round(float(vals.mean()), 3),
            'median': round(float(np.median(vals)), 3),
            'std': round(float(vals.std(ddof=1)), 3),
            'min': round(float(vals.min()), 3),
            'max': round(float(vals.max()), 3),
        })

    # RM ANOVA hesabı (elle — statsmodels AnovaRM wide→long dönüşümü ile)
    grand_mean = float(np.concatenate(arrays).mean())
    subject_means = sub.mean(axis=1).values  # her katılımcının ortalaması

    ss_between = n * sum((float(a.mean()) - grand_mean) ** 2 for a in arrays)
    ss_subjects = k * float(np.sum((subject_means - grand_mean) ** 2))
    ss_total = float(sum(np.sum((a - grand_mean) ** 2) for a in arrays))
    ss_error = ss_total - ss_between - ss_subjects

    df_between = k - 1
    df_subjects = n - 1
    df_error = (k - 1) * (n - 1)

    ms_between = ss_between / df_between if df_between > 0 else 0
    ms_error = ss_error / df_error if df_error > 0 else 1e-10

    F = ms_between / ms_error if ms_error > 0 else 0.0
    p_val = float(stats.f.sf(F, df_between, df_error))

    # Partial eta-squared: SS_between / (SS_between + SS_error)
    eta_sq = ss_between / (ss_between + ss_error) if (ss_between + ss_error) > 0 else 0.0

    # Mauchly küresellik testi (scipy yok, kısmi uygulama — notla)
    # Epsilon düzeltmesi için Greenhouse-Geisser — yalnızca bilgilendirici
    sphericity_note = (gettext('Küresellik (Mauchly) testi bu sürümde desteklenmemektedir. Küresellik ihlali şüphesi varsa Greenhouse-Geisser düzeltmeli SPSS/JASP çıktısıyla karşılaştırın.'))

    # Post-hoc: pairwise bağımlı t-test + Bonferroni
    pairs = list(combinations(range(k), 2))
    n_pairs = len(pairs)
    posthoc = []
    for i, j in pairs:
        t, p = stats.ttest_rel(arrays[i], arrays[j])
        p_adj = min(float(p) * n_pairs, 1.0)
        d = float((arrays[i] - arrays[j]).mean()) / float((arrays[i] - arrays[j]).std(ddof=1))
        posthoc.append({
            'col1': columns[i],
            'col2': columns[j],
            't': round(float(t), 3),
            'p': round(float(p), 4),
            'p_adj': round(p_adj, 4),
            'd': round(abs(d), 3),
            'significant': p_adj < 0.05,
        })

    return {
        'columns': columns,
        'n': n,
        'k': k,
        'F': round(float(F), 3),
        'df_between': df_between,
        'df_error': df_error,
        'ms_between': round(ms_between, 3),
        'ms_error': round(ms_error, 3),
        'ss_between': round(ss_between, 3),
        'ss_error': round(ss_error, 3),
        'p_value': round(p_val, 4),
        'eta_sq': round(eta_sq, 3),
        'effect_interpretation': _interpret_eta(eta_sq),
        'significant': p_val < 0.05,
        'descriptives': descriptives,
        'posthoc': posthoc,
        'sphericity_note': sphericity_note,
        'conclusion': _conclusion(p_val, F, df_between, df_error, columns),
    }


def _interpret_eta(eta: float) -> str:
    if eta < 0.01:
        return gettext('İhmal edilebilir etki (η² < .01)')
    if eta < 0.06:
        return gettext('Küçük etki (.01 ≤ η² < .06)')
    if eta < 0.14:
        return gettext('Orta düzey etki (.06 ≤ η² < .14)')
    return gettext('Büyük etki (η² ≥ .14)')


def _conclusion(p, F, df1, df2, columns: list) -> str:
    col_str = ', '.join(columns)
    if float(p) < 0.05:
        return (gettext('%(col_str)s ölçümleri arasında istatistiksel olarak anlamlı bir fark bulunmaktadır, F(%(df1)s, %(df2)s) = %(F)s, p = %(p)s. Post-hoc karşılaştırmalarda Bonferroni düzeltmesi uygulanmıştır.') % {'col_str': col_str, 'df1': df1, 'df2': df2, 'F': f'{F:.3f}', 'p': f'{p:.4f}'})
    return (gettext('%(col_str)s ölçümleri arasında istatistiksel olarak anlamlı bir fark bulunmamaktadır, F(%(df1)s, %(df2)s) = %(F)s, p = %(p)s.') % {'col_str': col_str, 'df1': df1, 'df2': df2, 'F': f'{F:.3f}', 'p': f'{p:.4f}'})


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
    HEADER_COLOR = colors.HexColor('#1e3a5f')
    title_s = ParagraphStyle('T', parent=styles['Heading1'], fontSize=16, spaceAfter=6, fontName='DejaVuSans')
    h2_s    = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, spaceAfter=4, fontName='DejaVuSans')
    norm_s  = ParagraphStyle('N', parent=styles['Normal'], fontName='DejaVuSans', fontSize=9)
    small_s = ParagraphStyle('S', parent=styles['Normal'], fontName='DejaVuSans', fontSize=8,
                             textColor=colors.HexColor('#64748b'))

    story = []
    story.append(Paragraph(gettext('Tekrarlayan Ölçümler ANOVA Raporu'), title_s))
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

    # ANOVA tablosu
    story.append(Paragraph(gettext('ANOVA Tablosu'), h2_s))
    sig = result['significant']
    anova_rows = [
        [gettext('Kaynak'), gettext('KT (SS)'), 'sd', gettext('KO (MS)'), 'F', 'p'],
        [gettext('Ölçümler arası'), f"{result['ss_between']:.3f}", str(result['df_between']),
         f"{result['ms_between']:.3f}", f"{result['F']:.3f}", f"{result['p_value']:.4f}"],
        [gettext('Hata'), f"{result['ss_error']:.3f}", str(result['df_error']),
         f"{result['ms_error']:.3f}", '', ''],
    ]
    anova_tbl = Table(anova_rows, colWidths=[4*cm, 2.5*cm, 1.5*cm, 2.5*cm, 2*cm, 2*cm])
    anova_tbl.setStyle(TableStyle([
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
    story.append(anova_tbl)
    story.append(Spacer(1, 0.2*cm))

    eff_rows = [
        [gettext('Partial η²'), f"{result['eta_sq']:.3f}"],
        [gettext('Etki Yorumu'), result['effect_interpretation']],
        [gettext('Sonuç'), gettext('Anlamlı (p < .05)') if sig else gettext('Anlamlı değil (p ≥ .05)')],
    ]
    eff_tbl = Table(eff_rows, colWidths=[7*cm, 9*cm])
    eff_tbl.setStyle(TableStyle([
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
    story.append(eff_tbl)
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(result['sphericity_note'], small_s))
    story.append(Spacer(1, 0.4*cm))

    # Post-hoc
    if sig and result['posthoc']:
        story.append(Paragraph(gettext('Post-Hoc Karşılaştırmalar (Bağımlı t-testi — Bonferroni)'), h2_s))
        ph_header = [gettext('Çift'), 't', 'p', gettext('p (düz.)'), gettext("Cohen's d"), gettext('Anlamlı?')]
        ph_rows = [ph_header] + [
            [f"{r['col1']} vs {r['col2']}", f"{r['t']:.3f}", f"{r['p']:.4f}",
             f"{r['p_adj']:.4f}", f"{r['d']:.3f}", gettext('Evet *') if r['significant'] else gettext('Hayır')]
            for r in result['posthoc']
        ]
        ph_tbl = Table(ph_rows, colWidths=[5*cm, 1.8*cm, 2.2*cm, 2.2*cm, 2.2*cm, 2.6*cm])
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
        story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph(gettext('Yorum'), h2_s))
    story.append(Paragraph(result['conclusion'], norm_s))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(gettext('APA Formatında Raporlama'), h2_s))
    # 'p < .001' / 'p = 0.123' (önceden 'p 0.123' — eşittir eksikti); şablon JS ile ortak msgid
    v = dict(cols=', '.join(result['columns']), df1=result['df_between'], df2=result['df_error'],
             f=f"{result['F']:.3f}", p='p < .001' if result['p_value'] < 0.001 else f"p = {result['p_value']:.3f}",
             eta=f"{result['eta_sq']:.3f}", effect=result['effect_interpretation'])
    if result['significant']:
        apa_text = gettext('Tekrarlayan ölçümler ANOVA sonuçlarına göre {cols} koşulları arasındaki fark istatistiksel '
                           'olarak anlamlı bulunmuştur, F({df1}, {df2}) = {f}, {p}, η² = {eta} ({effect}).').format(**v)
    else:
        apa_text = gettext('Tekrarlayan ölçümler ANOVA sonuçlarına göre {cols} koşulları arasındaki fark istatistiksel '
                           'olarak anlamlı bulunmamıştır, F({df1}, {df2}) = {f}, {p}, η² = {eta} ({effect}).').format(**v)
    apa_tbl = Table([[Paragraph(apa_text, norm_s)]], colWidths=[16*cm])
    apa_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eff6ff')),
        ('BOX', (0, 0), (-1, -1), 1, HEADER_COLOR),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(apa_tbl)

    doc.build(story)
    return buf.getvalue()
