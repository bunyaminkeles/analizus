"""
t-Testi Analizi
Bağımsız örneklem t-testi ve bağımlı (eşleştirilmiş) örneklem t-testi.
"""
import io
from django.utils.translation import gettext
import numpy as np
from scipy import stats


def analyze(df, test_type: str, group_col: str = None,
            dep_col: str = None, col1: str = None, col2: str = None,
            test_value=None) -> dict:
    """
    test_type: 'independent', 'paired' veya 'one_sample'
    Bağımsız:     group_col (kategorik, 2 grup) + dep_col (sayısal)
    Bağımlı:      col1, col2 (her biri sayısal)
    Tek Örneklem: dep_col (sayısal) + test_value (teorik/referans ortalama)
    """
    if test_type == 'independent':
        return _independent(df, group_col, dep_col)
    elif test_type == 'paired':
        return _paired(df, col1, col2)
    elif test_type == 'one_sample':
        return _one_sample(df, dep_col, test_value)
    else:
        raise ValueError(gettext('Bilinmeyen test tipi: %(test_type)s') % {'test_type': test_type})


def _independent(df, group_col: str, dep_col: str) -> dict:
    if group_col not in df.columns:
        raise ValueError(gettext('"%(group_col)s" sütunu bulunamadı.') % {'group_col': group_col})
    if dep_col not in df.columns:
        raise ValueError(gettext('"%(dep_col)s" sütunu bulunamadı.') % {'dep_col': dep_col})

    groups = df[group_col].dropna().unique()
    if len(groups) != 2:
        raise ValueError(
            gettext('Bağımsız t-testi için tam 2 grup gereklidir. "%(group_col)s" sütununda %(groups)s farklı değer bulundu.') % {'group_col': group_col, 'groups': len(groups)})

    g1_label, g2_label = str(groups[0]), str(groups[1])
    g1 = df[df[group_col] == groups[0]][dep_col].dropna().values.astype(float)
    g2 = df[df[group_col] == groups[1]][dep_col].dropna().values.astype(float)

    if len(g1) < 3 or len(g2) < 3:
        raise ValueError(gettext('Her grupta en az 3 gözlem olmalıdır.'))

    t_stat, p_val = stats.ttest_ind(g1, g2, equal_var=True)
    # Levene varyans homojenliği testi
    levene_stat, levene_p = stats.levene(g1, g2)
    if levene_p < 0.05:
        # Welch t-testi
        t_stat, p_val = stats.ttest_ind(g1, g2, equal_var=False)
        used_welch = True
    else:
        used_welch = False

    df_val = len(g1) + len(g2) - 2 if not used_welch else _welch_df(g1, g2)

    # Cohen's d
    pooled_std = np.sqrt(((len(g1) - 1) * g1.std(ddof=1) ** 2 +
                          (len(g2) - 1) * g2.std(ddof=1) ** 2) /
                         (len(g1) + len(g2) - 2))
    cohens_d = (g1.mean() - g2.mean()) / pooled_std if pooled_std > 0 else 0.0

    # %95 güven aralığı
    diff = g1.mean() - g2.mean()
    se_diff = np.sqrt(g1.var(ddof=1) / len(g1) + g2.var(ddof=1) / len(g2))
    t_crit = stats.t.ppf(0.975, df=df_val)
    ci_low = diff - t_crit * se_diff
    ci_high = diff + t_crit * se_diff

    return {
        'test_type': 'independent',
        'test_label': gettext('Bağımsız Örneklem t-Testi') + (gettext(' (Welch)') if used_welch else ''),
        'group_col': group_col,
        'dep_col': dep_col,
        'g1_label': g1_label,
        'g2_label': g2_label,
        'g1_n': len(g1),
        'g2_n': len(g2),
        'g1_mean': round(float(g1.mean()), 3),
        'g2_mean': round(float(g2.mean()), 3),
        'g1_std': round(float(g1.std(ddof=1)), 3),
        'g2_std': round(float(g2.std(ddof=1)), 3),
        't_stat': round(float(t_stat), 3),
        'p_value': round(float(p_val), 4),
        'df': round(float(df_val), 1),
        'cohens_d': round(float(cohens_d), 3),
        'effect_interpretation': _interpret_d(abs(cohens_d)),
        'ci_low': round(float(ci_low), 3),
        'ci_high': round(float(ci_high), 3),
        'levene_p': round(float(levene_p), 4),
        'used_welch': used_welch,
        'significant': float(p_val) < 0.05,
        'conclusion': _conclusion_independent(p_val, g1_label, g2_label, dep_col, g1.mean(), g2.mean()),
    }


def _paired(df, col1: str, col2: str) -> dict:
    if col1 not in df.columns:
        raise ValueError(gettext('"%(col1)s" sütunu bulunamadı.') % {'col1': col1})
    if col2 not in df.columns:
        raise ValueError(gettext('"%(col2)s" sütunu bulunamadı.') % {'col2': col2})

    data = df[[col1, col2]].dropna()
    if len(data) < 5:
        raise ValueError(gettext('En az 5 çift gözlem gereklidir.'))

    a = data[col1].values.astype(float)
    b = data[col2].values.astype(float)

    t_stat, p_val = stats.ttest_rel(a, b)
    diff = a - b
    n = len(diff)
    df_val = n - 1

    cohens_d = diff.mean() / diff.std(ddof=1) if diff.std(ddof=1) > 0 else 0.0
    se_diff = diff.std(ddof=1) / np.sqrt(n)
    t_crit = stats.t.ppf(0.975, df=df_val)
    ci_low = diff.mean() - t_crit * se_diff
    ci_high = diff.mean() + t_crit * se_diff

    return {
        'test_type': 'paired',
        'test_label': gettext('Bağımlı Örneklem t-Testi (Eşleştirilmiş)'),
        'col1': col1,
        'col2': col2,
        'n': n,
        'col1_mean': round(float(a.mean()), 3),
        'col2_mean': round(float(b.mean()), 3),
        'col1_std': round(float(a.std(ddof=1)), 3),
        'col2_std': round(float(b.std(ddof=1)), 3),
        'diff_mean': round(float(diff.mean()), 3),
        'diff_std': round(float(diff.std(ddof=1)), 3),
        't_stat': round(float(t_stat), 3),
        'p_value': round(float(p_val), 4),
        'df': df_val,
        'cohens_d': round(float(cohens_d), 3),
        'effect_interpretation': _interpret_d(abs(cohens_d)),
        'ci_low': round(float(ci_low), 3),
        'ci_high': round(float(ci_high), 3),
        'significant': float(p_val) < 0.05,
        'conclusion': _conclusion_paired(p_val, col1, col2, diff.mean()),
    }


def _one_sample(df, dep_col: str, test_value) -> dict:
    if not dep_col or dep_col not in df.columns:
        raise ValueError(gettext('"%(dep_col)s" sütunu bulunamadı.') % {'dep_col': dep_col})
    if test_value is None or str(test_value).strip() == '':
        raise ValueError(gettext('Karşılaştırılacak teorik/referans değer (test değeri) girilmelidir.'))
    try:
        test_value = float(test_value)
    except (TypeError, ValueError):
        raise ValueError(gettext('Test değeri sayısal olmalıdır.'))

    data = df[dep_col].dropna().values.astype(float)
    n = len(data)
    if n < 5:
        raise ValueError(gettext('En az 5 gözlem gereklidir.'))

    t_stat, p_val = stats.ttest_1samp(data, test_value)
    mean = float(data.mean())
    std = float(data.std(ddof=1))
    df_val = n - 1

    cohens_d = (mean - test_value) / std if std > 0 else 0.0

    se = std / np.sqrt(n)
    t_crit = stats.t.ppf(0.975, df=df_val)
    ci_low = mean - t_crit * se
    ci_high = mean + t_crit * se

    return {
        'test_type': 'one_sample',
        'test_label': gettext('Tek Örneklem t-Testi'),
        'dep_col': dep_col,
        'test_value': round(test_value, 3),
        'n': n,
        'mean': round(mean, 3),
        'std': round(std, 3),
        't_stat': round(float(t_stat), 3),
        'p_value': round(float(p_val), 4),
        'df': df_val,
        'cohens_d': round(float(cohens_d), 3),
        'effect_interpretation': _interpret_d(abs(cohens_d)),
        'ci_low': round(float(ci_low), 3),
        'ci_high': round(float(ci_high), 3),
        'significant': float(p_val) < 0.05,
        'conclusion': _conclusion_one_sample(p_val, dep_col, test_value, mean),
    }


def _welch_df(g1, g2) -> float:
    v1, v2 = g1.var(ddof=1), g2.var(ddof=1)
    n1, n2 = len(g1), len(g2)
    num = (v1 / n1 + v2 / n2) ** 2
    den = (v1 / n1) ** 2 / (n1 - 1) + (v2 / n2) ** 2 / (n2 - 1)
    return num / den if den > 0 else n1 + n2 - 2


def _interpret_d(d: float) -> str:
    if d < 0.2:
        return gettext('İhmal edilebilir etki')
    if d < 0.5:
        return gettext('Küçük etki (d < 0.50)')
    if d < 0.8:
        return gettext('Orta düzey etki (0.50 ≤ d < 0.80)')
    return gettext('Büyük etki (d ≥ 0.80)')


# Sonuç cümleleri tam cümle msgid (yön/anlamlılık parçaları dillerde farklı
# çekimlenir — 'daha yüksek' + 'tir' gibi birleştirme çevrilemez)
def _conclusion_independent(p, g1, g2, dep, m1, m2) -> str:
    v = {'g1': g1, 'g2': g2, 'dep': dep, 'p': ('p < .001' if p < 0.001 else f'p = {p:.4f}'), 'm1': f'{m1:.3f}', 'm2': f'{m2:.3f}'}
    if p < 0.05:
        if m1 > m2:
            return gettext('{g1} grubu ile {g2} grubu arasında {dep} açısından istatistiksel olarak anlamlı '
                           'bir fark bulunmaktadır ({p}). {g1} grubunun ortalaması ({m1}), {g2} grubuna '
                           '({m2}) göre daha yüksektir.').format(**v)
        return gettext('{g1} grubu ile {g2} grubu arasında {dep} açısından istatistiksel olarak anlamlı '
                       'bir fark bulunmaktadır ({p}). {g1} grubunun ortalaması ({m1}), {g2} grubuna '
                       '({m2}) göre daha düşüktür.').format(**v)
    return gettext('{g1} grubu ile {g2} grubu arasında {dep} açısından istatistiksel olarak anlamlı '
                   'bir fark bulunmamaktadır ({p}).').format(**v)


def _conclusion_paired(p, c1, c2, diff_mean) -> str:
    v = {'c1': c1, 'c2': c2, 'p': ('p < .001' if p < 0.001 else f'p = {p:.4f}'), 'diff': f'{abs(diff_mean):.3f}'}
    if p < 0.05:
        # diff_mean = c1 − c2 (ttest_rel(a, b)): c2 > c1 ise ölçüm ARTMIŞTIR.
        # 25 Eylül 2026'ya kadar koşul ters (diff_mean > 0 → "artmıştır") idi.
        if diff_mean < 0:
            return gettext('{c1} ile {c2} arasındaki fark istatistiksel olarak anlamlıdır ({p}). '
                           'Ortalama fark {diff} olup ölçüm artmıştır.').format(**v)
        return gettext('{c1} ile {c2} arasındaki fark istatistiksel olarak anlamlıdır ({p}). '
                       'Ortalama fark {diff} olup ölçüm azalmıştır.').format(**v)
    return gettext('{c1} ile {c2} arasındaki fark istatistiksel olarak anlamlı değildir ({p}).').format(**v)


def _conclusion_one_sample(p, dep_col, test_value, mean) -> str:
    v = {'dep': dep_col, 'value': f'{test_value:.3f}', 'mean': f'{mean:.3f}',
         'p': ('p < .001' if p < 0.001 else f'p = {p:.4f}')}
    if p < 0.05:
        if mean > test_value:
            return gettext('{dep} değişkeninin ortalaması ({mean}), test değerinden ({value}) istatistiksel '
                           'olarak anlamlı şekilde yüksektir ({p}).').format(**v)
        return gettext('{dep} değişkeninin ortalaması ({mean}), test değerinden ({value}) istatistiksel '
                       'olarak anlamlı şekilde düşüktür ({p}).').format(**v)
    return gettext('{dep} değişkeninin ortalaması ({mean}) ile test değeri ({value}) arasında istatistiksel '
                   'olarak anlamlı bir fark bulunmamaktadır ({p}).').format(**v)


def build_pdf(result: dict, filename: str, df=None) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from .pdf_fonts import register_fonts, append_ai_comment
    register_fonts()

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title_s = ParagraphStyle('T', parent=styles['Heading1'], fontSize=16, spaceAfter=6, fontName='DejaVuSans')
    h2_s = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, spaceAfter=4, fontName='DejaVuSans')
    norm_s = ParagraphStyle('N', parent=styles['Normal'], fontName='DejaVuSans', fontSize=9)

    story = []
    story.append(Paragraph(gettext('%(test)s Raporu') % {'test': result['test_label']}, title_s))
    story.append(Paragraph(gettext('Dosya: %(filename)s') % {'filename': filename}, norm_s))
    story.append(Spacer(1, 0.4*cm))

    if result['test_type'] == 'independent':
        rows = [
            ['', result['g1_label'], result['g2_label']],
            ['n', str(result['g1_n']), str(result['g2_n'])],
            [gettext('Ortalama'), f"{result['g1_mean']:.3f}", f"{result['g2_mean']:.3f}"],
            ['SS', f"{result['g1_std']:.3f}", f"{result['g2_std']:.3f}"],
        ]
    elif result['test_type'] == 'paired':
        rows = [
            ['', result['col1'], result['col2']],
            [gettext('Ortalama'), f"{result['col1_mean']:.3f}", f"{result['col2_mean']:.3f}"],
            ['SS', f"{result['col1_std']:.3f}", f"{result['col2_std']:.3f}"],
        ]
    else:  # one_sample
        rows = [
            ['', result['dep_col'], gettext('Test Değeri')],
            ['n', str(result['n']), ''],
            [gettext('Ortalama'), f"{result['mean']:.3f}", f"{result['test_value']:.3f}"],
            ['SS', f"{result['std']:.3f}", ''],
        ]

    grp_tbl = Table(rows, colWidths=[6*cm, 5*cm, 5*cm])
    grp_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(Paragraph(gettext('Grup İstatistikleri'), h2_s))
    story.append(grp_tbl)
    story.append(Spacer(1, 0.5*cm))

    sig = result['significant']
    res_rows = [
        [gettext('t istatistiği'), f"{result['t_stat']:.3f}"],
        [gettext('Serbestlik Derecesi (df)'), str(result['df'])],
        [gettext('p-değeri'), f"{result['p_value']:.4f}"],
        [gettext("Cohen's d"), f"{result['cohens_d']:.3f}"],
        [gettext('%%95 GA (fark)') % {}, f"[{result['ci_low']:.3f}, {result['ci_high']:.3f}]"],  # %%: python-format msgid (EN: 95%% CI)
        [gettext('Sonuç'), gettext('Anlamlı (p < .05)') if sig else gettext('Anlamlı değil (p ≥ .05)')],
    ]
    res_tbl = Table(res_rows, colWidths=[7*cm, 9*cm])
    res_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('BACKGROUND', (1, -1), (1, -1),
         colors.HexColor('#d4edda') if sig else colors.HexColor('#f8d7da')),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (1, 0), (1, -2), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(Paragraph(gettext('Test Sonuçları'), h2_s))
    story.append(res_tbl)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(gettext('Yorum'), h2_s))
    story.append(Paragraph(result['conclusion'], norm_s))

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(gettext('APA Formatında Raporlama'), h2_s))
    # APA: 'p < .001' ya da 'p = 0.123' (önceden 'p = < .001'); şablon JS ile ortak msgid
    p_str = 'p < .001' if result['p_value'] < 0.001 else f"p = {result['p_value']:.3f}"
    if result['test_type'] == 'independent':
        apa_text = gettext('{group} grupları ({g1} ve {g2}) arasındaki {dep} farkı {test} ile test edilmiştir: '
                           't({df}) = {t}, {p}, d = {d} ({g1}: M = {m1}, SS = {s1}; {g2}: M = {m2}, SS = {s2}).').format(
            group=result['group_col'], g1=result['g1_label'], g2=result['g2_label'], dep=result['dep_col'],
            test=result['test_label'], df=result['df'], t=f"{result['t_stat']:.3f}", p=p_str,
            d=f"{result['cohens_d']:.3f}", m1=f"{result['g1_mean']:.3f}", s1=f"{result['g1_std']:.3f}",
            m2=f"{result['g2_mean']:.3f}", s2=f"{result['g2_std']:.3f}")
    elif result['test_type'] == 'paired':
        apa_text = gettext('{c1} ve {c2} arasındaki fark {test} ile test edilmiştir: t({df}) = {t}, {p}, d = {d}.').format(
            c1=result['col1'], c2=result['col2'], test=result['test_label'], df=result['df'],
            t=f"{result['t_stat']:.3f}", p=p_str, d=f"{result['cohens_d']:.3f}")
    else:  # one_sample
        apa_text = gettext('{dep} değişkeninin ortalaması, test değeri olan {value} ile {test} kullanılarak '
                           'karşılaştırılmıştır: t({df}) = {t}, {p}, d = {d} (M = {mean}, SS = {sd}).').format(
            dep=result['dep_col'], value=f"{result['test_value']:.3f}", test=result['test_label'],
            df=result['df'], t=f"{result['t_stat']:.3f}", p=p_str, d=f"{result['cohens_d']:.3f}",
            mean=f"{result['mean']:.3f}", sd=f"{result['std']:.3f}")
    apa_tbl = Table([[Paragraph(apa_text, norm_s)]], colWidths=[16*cm])
    apa_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f4ff')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1e3a5f')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(apa_tbl)
    append_ai_comment(story, result, norm_s, '#f0f4ff', '#1e3a5f')

    doc.build(story)
    return buf.getvalue()
