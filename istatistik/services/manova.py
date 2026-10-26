"""
Çok Değişkenli Varyans Analizi (MANOVA) — tek kategorik bağımsız (grup)
değişken, 2+ sürekli bağımlı değişken. statsmodels.multivariate.manova.MANOVA
ile Wilks' Lambda / Pillai's Trace / Hotelling-Lawley Trace / Roy's Largest
Root hesaplanır (SPSS "Multivariate Tests" çıktısıyla aynı). Birincil
anlamlılık Wilks' Lambda'ya göre belirlenir. Anlamlıysa her bağımlı değişken
için Bonferroni düzeltmeli (α/m) takip ANOVA'ları (mevcut anova.py yeniden
kullanılarak) ve Box's M (kovaryans matrisi homojenliği) testi raporlanır.
"""
import io
from django.utils.translation import gettext
import numpy as np
from scipy import stats


def analyze(df, group_col: str, dep_cols: list) -> dict:
    import pandas as pd
    from statsmodels.multivariate.manova import MANOVA
    from .anova import analyze as _anova_analyze, _interpret_eta

    if not group_col:
        raise ValueError(gettext('Grup değişkeni seçilmelidir.'))
    if group_col not in df.columns:
        raise ValueError(gettext('"%(group_col)s" sütunu bulunamadı.') % {'group_col': group_col})
    dep_cols = list(dep_cols or [])
    if len(dep_cols) < 2:
        raise ValueError(gettext('MANOVA için en az 2 bağımlı değişken seçilmelidir (tek değişken için ANOVA kullanın).'))
    if len(dep_cols) > 8:
        raise ValueError(gettext('En fazla 8 bağımlı değişken desteklenmektedir.'))
    missing = [c for c in dep_cols if c not in df.columns]
    if missing:
        raise ValueError(gettext('Şu sütunlar bulunamadı: %(v)s') % {'v': ', '.join(missing)})
    if group_col in dep_cols:
        raise ValueError(gettext('Grup değişkeni, bağımlı değişkenler arasında olamaz.'))

    sub = df[[group_col] + dep_cols].dropna()
    raw_labels = sub[group_col].unique().tolist()
    try:
        group_labels = sorted(raw_labels, key=float)
    except (TypeError, ValueError):
        group_labels = sorted(raw_labels, key=str)

    if len(group_labels) < 2:
        raise ValueError(gettext('En az 2 grup gereklidir.'))
    if len(group_labels) > 10:
        raise ValueError(gettext('MANOVA için en fazla 10 grup desteklenmektedir.'))

    p = len(dep_cols)
    groups_data = []
    for lbl in group_labels:
        arr = sub[sub[group_col] == lbl][dep_cols].values.astype(float)
        if len(arr) < p + 3:
            raise ValueError(gettext(
                '"%(lbl)s" grubunda en az %(min_n)s gözlem olmalıdır (bağımlı değişken sayısı + 3).'
            ) % {'lbl': lbl, 'min_n': p + 3})
        groups_data.append(arr)
    n = len(sub)
    k = len(group_labels)

    # Patsy formülü için güvenli (ASCII, boşluksuz) sütun adları
    rename_map = {group_col: '_grp'}
    rename_map.update({c: f'_dv{i}' for i, c in enumerate(dep_cols)})
    safe = sub.rename(columns=rename_map)
    formula = ' + '.join(f'_dv{i}' for i in range(p)) + ' ~ C(_grp)'
    manova_result = MANOVA.from_formula(formula, data=safe).mv_test()
    stat_df = manova_result.results['C(_grp)']['stat']

    name_map = {
        "Wilks' lambda": gettext("Wilks' Lambda"),
        "Pillai's trace": gettext("Pillai's Trace"),
        'Hotelling-Lawley trace': gettext('Hotelling-Lawley Trace'),
        "Roy's greatest root": gettext("Roy's Largest Root"),
    }
    multivariate_tests = []
    for idx in stat_df.index:
        row = stat_df.loc[idx]
        p_val = float(row['Pr > F'])
        multivariate_tests.append({
            'name': name_map.get(idx, str(idx)),
            'value': round(float(row['Value']), 4),
            'df1': round(float(row['Num DF']), 2),
            'df2': round(float(row['Den DF']), 2),
            'f': round(float(row['F Value']), 3),
            'p': round(p_val, 4),
            'significant': bool(p_val < 0.05),
        })

    wilks = next(t for t in multivariate_tests if t['name'] == gettext("Wilks' Lambda"))
    significant = wilks['significant']

    # Wilks' Lambda'dan çok değişkenli kısmi eta-kare yaklaşımı (Cohen): 1 − Λ^(1/s)
    s = min(p, k - 1)
    partial_eta_sq = round(1 - wilks['value'] ** (1 / s), 3) if s > 0 and wilks['value'] > 0 else 0.0

    box_m = _box_m_test(groups_data, p, k, n)

    # Her bağımlı değişken için grup bazlı betimsel istatistikler (profil grafiği + rapor tablosu)
    dv_group_stats = []
    for i, dc in enumerate(dep_cols):
        rows = []
        for lbl, arr in zip(group_labels, groups_data):
            vals = arr[:, i]
            rows.append({
                'label': str(lbl),
                'n': len(vals),
                'mean': round(float(vals.mean()), 3),
                'std': round(float(vals.std(ddof=1)), 3),
            })
        dv_group_stats.append({'dv': dc, 'stats': rows})

    profile_plot_b64 = _build_profile_plot(dep_cols, [str(l) for l in group_labels], dv_group_stats)

    alpha_corrected = 0.05 / p
    followup_anovas = []
    if significant:
        for dc in dep_cols:
            r = _anova_analyze(sub[[group_col, dc]], group_col, dc, posthoc='bonferroni')
            r['alpha_corrected'] = round(alpha_corrected, 5)
            r['significant_corrected'] = bool(r['p_value'] < alpha_corrected)
            followup_anovas.append(r)

    return {
        'group_col': group_col,
        'dep_cols': dep_cols,
        'n': n,
        'k_groups': k,
        'group_labels': [str(l) for l in group_labels],
        'multivariate_tests': multivariate_tests,
        'wilks': wilks,
        'significant': significant,
        'partial_eta_sq': partial_eta_sq,
        'effect_interpretation': _interpret_eta(partial_eta_sq),
        'box_m': box_m,
        'dv_group_stats': dv_group_stats,
        'profile_plot_b64': profile_plot_b64,
        'alpha_corrected': round(alpha_corrected, 5),
        'followup_anovas': followup_anovas,
        'conclusion': _conclusion(significant, wilks, group_col, dep_cols),
    }


def _box_m_test(groups_data, p: int, k: int, n: int) -> dict | None:
    """Box's M testi (kovaryans matrisi homojenliği) — Box (1949).
    Normallik ihlaline ve büyük örneklem büyüklüğüne aşırı duyarlıdır; anlamlı
    çıksa bile Pillai's Trace bu varsayım ihlaline nispeten dayanıklıdır."""
    try:
        ns = np.array([len(g) for g in groups_data], dtype=float)
        covs = [np.cov(g, rowvar=False, ddof=1) for g in groups_data]
        pooled = sum((ni - 1) * c for ni, c in zip(ns, covs)) / (n - k)

        def logdet(m):
            sign, ld = np.linalg.slogdet(m)
            if sign <= 0:
                raise np.linalg.LinAlgError('Tekil (singular) kovaryans matrisi')
            return ld

        log_det_pooled = logdet(pooled)
        m_stat = (n - k) * log_det_pooled - sum((ni - 1) * logdet(c) for ni, c in zip(ns, covs))

        sum_inv = float(sum(1.0 / (ni - 1) for ni in ns))
        c_correction = ((sum_inv - 1.0 / (n - k)) * (2 * p ** 2 + 3 * p - 1)) / (6 * (p + 1) * (k - 1))
        chi2_stat = m_stat * (1 - c_correction)
        df = 0.5 * p * (p + 1) * (k - 1)
        p_value = float(stats.chi2.sf(chi2_stat, df))
        return {
            'chi2': round(float(chi2_stat), 3),
            'df': round(float(df), 1),
            'p': round(p_value, 4),
            'homogeneous': bool(p_value >= 0.05),
        }
    except np.linalg.LinAlgError:
        return None


def _build_profile_plot(dep_cols, group_labels, dv_group_stats) -> str:
    import base64
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 4.2), dpi=110)
    x = list(range(len(dep_cols)))
    cmap = plt.get_cmap('tab10')
    for gi, lbl in enumerate(group_labels):
        means = [dv_group_stats[di]['stats'][gi]['mean'] for di in range(len(dep_cols))]
        ax.plot(x, means, 'o-', color=cmap(gi % 10), label=lbl, linewidth=2)
    ax.set_xticks(x)
    ax.set_xticklabels(dep_cols, rotation=15, ha='right')
    ax.set_ylabel(gettext('Ortalama'))
    ax.set_title(gettext('Profil Grafiği (Grup Ortalamaları)'))
    ax.legend(fontsize=8)
    ax.grid(alpha=0.2)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('ascii')


def _conclusion(significant, wilks, group_col, dep_cols) -> str:
    dep_joined = ', '.join(dep_cols)
    p_str = 'p < .001' if wilks['p'] < 0.001 else f"p = {wilks['p']:.4f}"
    if not significant:
        return gettext(
            '%(group_col)s gruplarının %(dep_cols)s değişkenlerinin bileşimi üzerinde istatistiksel olarak '
            'anlamlı bir etkisi bulunmamaktadır [Wilks\' Λ = %(lambda)s, %(p)s].'
        ) % {'group_col': group_col, 'dep_cols': dep_joined, 'lambda': f"{wilks['value']:.3f}", 'p': p_str}
    return gettext(
        '%(group_col)s gruplarının %(dep_cols)s değişkenlerinin bileşimi üzerinde istatistiksel olarak '
        'anlamlı bir etkisi bulunmaktadır [Wilks\' Λ = %(lambda)s, %(p)s]. Hangi bağımlı değişken(ler)in bu '
        'farka kaynaklık ettiğini belirlemek için aşağıdaki takip (follow-up) ANOVA sonuçlarına bakınız.'
    ) % {'group_col': group_col, 'dep_cols': dep_joined, 'lambda': f"{wilks['value']:.3f}", 'p': p_str}


def build_pdf(result: dict, filename: str, df=None) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from .pdf_fonts import register_fonts, append_ai_comment
    register_fonts()

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    PURPLE = colors.HexColor('#6d28d9')
    title_s = ParagraphStyle('T', parent=styles['Heading1'], fontSize=16, spaceAfter=6, fontName='DejaVuSans')
    h2_s = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, spaceAfter=4, fontName='DejaVuSans')
    norm_s = ParagraphStyle('N', parent=styles['Normal'], fontName='DejaVuSans', fontSize=9)

    def p_str(v):
        return '< .001' if v < 0.001 else f'{v:.4f}'

    story = []
    story.append(Paragraph(gettext('Çok Değişkenli Varyans Analizi (MANOVA) Raporu'), title_s))
    story.append(Paragraph(gettext('Dosya: %(filename)s') % {'filename': filename}, norm_s))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph(gettext('Model Özeti'), h2_s))
    summary_rows = [
        [gettext('Grup Değişkeni'), result['group_col']],
        [gettext('Bağımlı Değişkenler'), ', '.join(result['dep_cols'])],
        [gettext('Grup Sayısı'), str(result['k_groups'])],
        ['N', str(result['n'])],
        [gettext('Sonuç'), gettext('Anlamlı (p < .05)') if result['significant'] else gettext('Anlamlı değil (p ≥ .05)')],
    ]
    sum_tbl = Table(summary_rows, colWidths=[6*cm, 10*cm])
    sig_bg = colors.HexColor('#d4edda') if result['significant'] else colors.HexColor('#f8d7da')
    sum_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), PURPLE),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('BACKGROUND', (1, -1), (1, -1), sig_bg),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (1, 0), (1, -2), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(sum_tbl)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(gettext('Çok Değişkenli Testler (Multivariate Tests)'), h2_s))
    mv_rows = [[gettext('Test'), gettext('Değer'), 'F', 'df1', 'df2', 'p']]
    for t in result['multivariate_tests']:
        mv_rows.append([t['name'], f"{t['value']:.4f}", f"{t['f']:.3f}", f"{t['df1']:.1f}", f"{t['df2']:.1f}", p_str(t['p'])])
    mv_tbl = Table(mv_rows, colWidths=[4.5*cm, 2.5*cm, 2.5*cm, 2*cm, 2*cm, 2.5*cm])
    mv_style = [
        ('BACKGROUND', (0, 0), (-1, 0), PURPLE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]
    for i, t in enumerate(result['multivariate_tests'], start=1):
        if t['name'] == result['wilks']['name']:
            mv_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#ede9fe')))
    mv_tbl.setStyle(TableStyle(mv_style))
    story.append(mv_tbl)
    story.append(Paragraph(
        gettext('Kısmi η² (Wilks\' Λ\'dan): %(eta)s — %(interp)s') % {'eta': f"{result['partial_eta_sq']:.3f}", 'interp': result['effect_interpretation']},
        norm_s))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(gettext("Box's M Testi (Kovaryans Matrisi Homojenliği)"), h2_s))
    if result['box_m']:
        bm = result['box_m']
        story.append(Paragraph(
            gettext('χ² = %(chi2)s, df = %(df)s, %(p)s — %(concl)s') % {
                'chi2': f"{bm['chi2']:.3f}", 'df': f"{bm['df']:.1f}", 'p': p_str(bm['p']),
                'concl': gettext('kovaryans matrisleri homojen (p ≥ .05)') if bm['homogeneous'] else gettext('kovaryans matrisleri homojen değil (p < .05)'),
            }, norm_s))
        story.append(Paragraph(
            '<font color="#666666" size="8">' + gettext(
                "Not: Box's M testi normallik ihlaline ve büyük örneklem büyüklüğüne aşırı duyarlıdır; "
                "anlamlı çıksa bile Pillai's Trace bu varsayım ihlaline nispeten dayanıklıdır."
            ) + '</font>', norm_s))
    else:
        story.append(Paragraph(gettext('Hesaplanamadı (tekil/singular kovaryans matrisi).'), norm_s))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(gettext('Profil Grafiği'), h2_s))
    if result.get('profile_plot_b64'):
        import base64
        img_data = base64.b64decode(result['profile_plot_b64'])
        story.append(Image(io.BytesIO(img_data), width=13*cm, height=7.8*cm))
    story.append(Spacer(1, 0.5*cm))

    if result['followup_anovas']:
        story.append(Paragraph(gettext('Takip (Follow-up) ANOVA Sonuçları'), h2_s))
        story.append(Paragraph(
            gettext('Düzeltilmiş anlamlılık eşiği (Bonferroni, α / %(m)s değişken): α = %(alpha)s') % {
                'm': len(result['dep_cols']), 'alpha': f"{result['alpha_corrected']:.5f}"}, norm_s))
        story.append(Spacer(1, 0.2*cm))
        fu_rows = [[gettext('Değişken'), 'F', 'df1', 'df2', 'p', gettext('Anlamlı (düz.)')]]
        for r in result['followup_anovas']:
            fu_rows.append([r['dep_col'], f"{r['f_stat']:.3f}", str(r['df_between']), str(r['df_within']),
                            p_str(r['p_value']), gettext('Evet') if r['significant_corrected'] else gettext('Hayır')])
        fu_tbl = Table(fu_rows, colWidths=[4.5*cm, 2.3*cm, 1.7*cm, 1.7*cm, 2.8*cm, 3*cm])
        fu_style = [
            ('BACKGROUND', (0, 0), (-1, 0), PURPLE),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ]
        for i, r in enumerate(result['followup_anovas'], start=1):
            if r['significant_corrected']:
                fu_style.append(('BACKGROUND', (5, i), (5, i), colors.HexColor('#d4edda')))
        fu_tbl.setStyle(TableStyle(fu_style))
        story.append(fu_tbl)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(gettext('Yorum'), h2_s))
    story.append(Paragraph(result['conclusion'], norm_s))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(gettext('APA Formatında Raporlama'), h2_s))
    v = dict(group=result['group_col'], dep=', '.join(result['dep_cols']),
             lam=f"{result['wilks']['value']:.3f}", df1=f"{result['wilks']['df1']:.1f}",
             df2=f"{result['wilks']['df2']:.1f}", f=f"{result['wilks']['f']:.3f}",
             p=p_str(result['wilks']['p']), eta=f"{result['partial_eta_sq']:.3f}")
    if result['significant']:
        apa_text = gettext(
            "Çok değişkenli varyans analizi (MANOVA) sonucunda {group} gruplarının {dep} değişkenlerinin "
            "bileşimi üzerinde anlamlı bir etkisi bulunmuştur, Wilks' Λ = {lam}, F({df1}, {df2}) = {f}, "
            "{p}, kısmi η² = {eta}."
        ).format(**v)
    else:
        apa_text = gettext(
            "Çok değişkenli varyans analizi (MANOVA) sonucunda {group} gruplarının {dep} değişkenlerinin "
            "bileşimi üzerinde anlamlı bir etkisi bulunmamıştır, Wilks' Λ = {lam}, F({df1}, {df2}) = {f}, "
            "{p}, kısmi η² = {eta}."
        ).format(**v)
    apa_tbl = Table([[Paragraph(apa_text, norm_s)]], colWidths=[16*cm])
    apa_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f3ff')),
        ('BOX', (0, 0), (-1, -1), 1, PURPLE),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(apa_tbl)
    append_ai_comment(story, result, norm_s, '#f5f3ff', PURPLE)

    doc.build(story)
    return buf.getvalue()
