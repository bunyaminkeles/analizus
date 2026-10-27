"""
ROC Eğrisi / Tanısal Tarama Analizi — sürekli bir test/biyobelirteç
değişkeninin, ikili bir referans (altın standart) değişkeni ayırt etme
gücünü ölçer. Tek test modunda AUC (Hanley & McNeil, 1982 kapalı-form güven
aralığı), Youden J indeksine göre optimal kesim noktası ve o noktadaki
duyarlılık/özgüllük/PPV/NPV/LR+/LR- tablosu raporlanır. İki test
karşılaştırma modunda aynı örneklem üzerinde ölçülen iki testin AUC farkı
DeLong testi (DeLong, DeLong & Clarke-Pearson, 1988) ile sınanır.
"""
import io
from django.utils.translation import gettext
import numpy as np


def _encode_reference(series, ref_col: str, positive_category: str = ''):
    """lojistik_regresyon.py/sagkalim.py ile aynı 2-kategori → 0/1 kodlama deseni."""
    unique_vals = series.unique()
    if len(unique_vals) != 2:
        raise ValueError(gettext(
            'Referans (altın standart) değişkeninin tam 2 kategorisi olmalıdır. '
            '"%(col)s" sütununda %(n)s farklı değer bulundu.'
        ) % {'col': ref_col, 'n': len(unique_vals)})
    unique_vals_list = unique_vals.tolist()
    try:
        sorted_vals = sorted(unique_vals_list, key=float)
    except (TypeError, ValueError):
        sorted_vals = sorted(unique_vals_list, key=str)
    target_match = next((v for v in unique_vals if str(v) == str(positive_category)), None) if positive_category else None
    if target_match is not None:
        positive_label = str(target_match)
        y = (series == target_match).astype(int).values
    else:
        positive_label = str(sorted_vals[1])
        y = (series == sorted_vals[1]).astype(int).values
    return y, positive_label


def analyze(df, mode: str = 'single', test_col: str = '', test_col2: str = '',
            ref_col: str = '', positive_category: str = '') -> dict:
    mode = mode if mode in ('single', 'compare') else 'single'

    if not ref_col:
        raise ValueError(gettext('Referans (altın standart) değişkeni seçilmelidir.'))
    if ref_col not in df.columns:
        raise ValueError(gettext('"%(col)s" sütunu bulunamadı.') % {'col': ref_col})
    if not test_col:
        raise ValueError(gettext('Test değişkeni seçilmelidir.'))
    if test_col not in df.columns:
        raise ValueError(gettext('"%(col)s" sütunu bulunamadı.') % {'col': test_col})
    if test_col == ref_col:
        raise ValueError(gettext('Test ve referans değişkeni farklı sütunlar olmalıdır.'))

    cols = [ref_col, test_col]
    if mode == 'compare':
        if not test_col2:
            raise ValueError(gettext('İkinci test değişkeni seçilmelidir.'))
        if test_col2 not in df.columns:
            raise ValueError(gettext('"%(col)s" sütunu bulunamadı.') % {'col': test_col2})
        if test_col2 in (test_col, ref_col):
            raise ValueError(gettext('İkinci test değişkeni, birinci test veya referans değişkeniyle aynı olamaz.'))
        cols.append(test_col2)

    sub = df[cols].dropna()
    n = len(sub)
    if n < 10:
        raise ValueError(gettext('En az 10 gözlem gereklidir, %(n)s satır bulundu.') % {'n': n})

    y, positive_label = _encode_reference(sub[ref_col], ref_col, positive_category)
    n_pos = int(y.sum())
    n_neg = n - n_pos
    if n_pos < 5 or n_neg < 5:
        raise ValueError(gettext(
            'Her iki grupta (referans pozitif/negatif) en az 5 gözlem gereklidir '
            '(pozitif = %(n_pos)s, negatif = %(n_neg)s).'
        ) % {'n_pos': n_pos, 'n_neg': n_neg})

    try:
        x1 = sub[test_col].astype(float).values
    except Exception:
        raise ValueError(gettext('"%(col)s" sayısal bir değişken olmalıdır.') % {'col': test_col})

    if mode == 'single':
        roc1 = _roc_for_test(x1, y, test_col)
        plot_b64 = _build_roc_plot([roc1])
        return {
            'mode': 'single',
            'ref_col': ref_col,
            'positive_label': positive_label,
            'n': n,
            'n_pos': n_pos,
            'n_neg': n_neg,
            'roc': roc1,
            'roc_plot_b64': plot_b64,
            'conclusion': _single_conclusion(roc1, ref_col),
        }

    try:
        x2 = sub[test_col2].astype(float).values
    except Exception:
        raise ValueError(gettext('"%(col)s" sayısal bir değişken olmalıdır.') % {'col': test_col2})

    roc1 = _roc_for_test(x1, y, test_col)
    roc2 = _roc_for_test(x2, y, test_col2)
    delong = _delong_test(x1, x2, y, roc1['direction_reversed'], roc2['direction_reversed'])
    plot_b64 = _build_roc_plot([roc1, roc2])

    return {
        'mode': 'compare',
        'ref_col': ref_col,
        'positive_label': positive_label,
        'n': n,
        'n_pos': n_pos,
        'n_neg': n_neg,
        'roc1': roc1,
        'roc2': roc2,
        'delong': delong,
        'roc_plot_b64': plot_b64,
        'conclusion': _compare_conclusion(roc1, roc2, delong),
    }


def _roc_for_test(x, y, test_name: str) -> dict:
    from sklearn.metrics import roc_curve, auc as sklearn_auc

    fpr, tpr, thresholds = roc_curve(y, x)
    auc_val = float(sklearn_auc(fpr, tpr))
    direction_reversed = False
    if auc_val < 0.5:
        fpr, tpr, thresholds = roc_curve(y, -x)
        auc_val = float(sklearn_auc(fpr, tpr))
        thresholds = -thresholds
        direction_reversed = True

    youden = tpr - fpr
    best_idx = int(np.argmax(youden))
    best_threshold = float(thresholds[best_idx])
    sens = float(tpr[best_idx])
    spec = float(1 - fpr[best_idx])

    x_for_cm = (-x if direction_reversed else x)
    pred_pos = x_for_cm >= (-best_threshold if direction_reversed else best_threshold)
    tp = int(np.sum(pred_pos & (y == 1)))
    fp = int(np.sum(pred_pos & (y == 0)))
    tn = int(np.sum(~pred_pos & (y == 0)))
    fn = int(np.sum(~pred_pos & (y == 1)))

    ppv = tp / (tp + fp) if (tp + fp) > 0 else None
    npv = tn / (tn + fn) if (tn + fn) > 0 else None
    accuracy = (tp + tn) / len(y) if len(y) > 0 else None
    lr_plus = (sens / (1 - spec)) if spec < 1 else None
    lr_minus = ((1 - sens) / spec) if spec > 0 else None

    n_pos = int(np.sum(y == 1))
    n_neg = int(np.sum(y == 0))
    se, ci_low, ci_high, p_value = _hanley_mcneil_ci(auc_val, n_pos, n_neg)

    n_points = len(fpr)
    if n_points > 60:
        idx = np.linspace(0, n_points - 1, 60).round().astype(int)
        fpr_plot = fpr[idx]
        tpr_plot = tpr[idx]
    else:
        fpr_plot = fpr
        tpr_plot = tpr

    return {
        'test_col': test_name,
        'auc': round(auc_val, 4),
        'se': round(se, 4),
        'ci_low': round(ci_low, 4),
        'ci_high': round(ci_high, 4),
        'p_value': round(p_value, 4),
        'significant': bool(p_value < 0.05),
        'interpretation': _interpret_auc(auc_val),
        'direction_reversed': direction_reversed,
        'best_threshold': round(best_threshold, 4),
        'sensitivity': round(sens, 4),
        'specificity': round(spec, 4),
        'ppv': round(ppv, 4) if ppv is not None else None,
        'npv': round(npv, 4) if npv is not None else None,
        'accuracy': round(accuracy, 4) if accuracy is not None else None,
        'lr_plus': round(lr_plus, 4) if lr_plus is not None else None,
        'lr_minus': round(lr_minus, 4) if lr_minus is not None else None,
        'confusion': {'tp': tp, 'fp': fp, 'tn': tn, 'fn': fn},
        'fpr': [round(float(v), 4) for v in fpr_plot],
        'tpr': [round(float(v), 4) for v in tpr_plot],
    }


def _hanley_mcneil_ci(auc_val: float, n_pos: int, n_neg: int):
    """Hanley & McNeil (1982) — AUC standart hatası için kapalı form formül."""
    from scipy.stats import norm

    q1 = auc_val / (2 - auc_val)
    q2 = (2 * auc_val ** 2) / (1 + auc_val)
    variance = (
        auc_val * (1 - auc_val)
        + (n_pos - 1) * (q1 - auc_val ** 2)
        + (n_neg - 1) * (q2 - auc_val ** 2)
    ) / (n_pos * n_neg)
    se = float(np.sqrt(max(variance, 0.0)))
    z = (auc_val - 0.5) / se if se > 0 else 0.0
    p_value = float(2 * (1 - norm.cdf(abs(z))))
    ci_low = max(0.0, auc_val - 1.96 * se)
    ci_high = min(1.0, auc_val + 1.96 * se)
    return se, ci_low, ci_high, p_value


def _interpret_auc(auc_val: float) -> str:
    """Şencan (2005) / yaygın akademik literatürdeki AUC yorum eşikleri."""
    if auc_val < 0.5:
        return gettext('Ayırt edicilik yok / ters yönlü (AUC < 0.50)')
    if auc_val < 0.60:
        return gettext('Zayıf (0.50–0.60)')
    if auc_val < 0.70:
        return gettext('Orta (0.60–0.70)')
    if auc_val < 0.80:
        return gettext('İyi (0.70–0.80)')
    if auc_val < 0.90:
        return gettext('Çok iyi (0.80–0.90)')
    return gettext('Mükemmel (≥ 0.90)')


def _delong_placements(x, y):
    """Her pozitif/negatif gözlem için DeLong (1988) yerleşim (placement) değerleri."""
    pos = x[y == 1]
    neg = x[y == 0]
    diff = pos[:, None] - neg[None, :]
    psi = np.where(diff > 0, 1.0, np.where(diff == 0, 0.5, 0.0))
    v10 = psi.mean(axis=1)
    v01 = psi.mean(axis=0)
    auc_val = float(psi.mean())
    return auc_val, v10, v01


def _delong_test(x1, x2, y, reversed1: bool, reversed2: bool) -> dict:
    from scipy.stats import norm

    xa = -x1 if reversed1 else x1
    xb = -x2 if reversed2 else x2

    auc1, v10_1, v01_1 = _delong_placements(xa, y)
    auc2, v10_2, v01_2 = _delong_placements(xb, y)
    n_pos = len(v10_1)
    n_neg = len(v01_1)

    s10 = np.cov(np.vstack([v10_1, v10_2]))
    s01 = np.cov(np.vstack([v01_1, v01_2]))

    var1 = s10[0, 0] / n_pos + s01[0, 0] / n_neg
    var2 = s10[1, 1] / n_pos + s01[1, 1] / n_neg
    cov12 = s10[0, 1] / n_pos + s01[0, 1] / n_neg

    se_diff = float(np.sqrt(max(var1 + var2 - 2 * cov12, 0.0)))
    diff = auc1 - auc2
    z = diff / se_diff if se_diff > 0 else 0.0
    p_value = float(2 * (1 - norm.cdf(abs(z))))

    return {
        'auc_diff': round(float(diff), 4),
        'se_diff': round(se_diff, 4),
        'z': round(float(z), 3),
        'p_value': round(p_value, 4),
        'significant': bool(p_value < 0.05),
    }


def _build_roc_plot(roc_list) -> str:
    import base64
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 5.2), dpi=110)
    cmap = plt.get_cmap('tab10')
    for i, roc in enumerate(roc_list):
        label = gettext('%(name)s (AUC = %(auc)s)') % {'name': roc['test_col'], 'auc': f"{roc['auc']:.3f}"}
        ax.plot(roc['fpr'], roc['tpr'], color=cmap(i % 10), linewidth=2, label=label)
    ax.plot([0, 1], [0, 1], linestyle='--', color='#999999', linewidth=1)
    ax.set_xlabel(gettext('1 − Özgüllük (Yanlış Pozitif Oranı)'))
    ax.set_ylabel(gettext('Duyarlılık (Doğru Pozitif Oranı)'))
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.legend(fontsize=8, loc='lower right')
    ax.grid(alpha=0.2)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('ascii')


def _single_conclusion(roc: dict, ref_col: str) -> str:
    p_str = 'p < .001' if roc['p_value'] < 0.001 else f"p = {roc['p_value']:.4f}"
    return gettext(
        '%(test)s değişkeni %(ref_col)s durumunu ayırt etmede AUC = %(auc)s ile %(interp)s düzeyinde bir '
        'performans göstermiştir (%%95 GA [%(lo)s, %(hi)s], %(p)s).'
    ) % {
        'test': roc['test_col'], 'ref_col': ref_col, 'auc': f"{roc['auc']:.3f}",
        'interp': roc['interpretation'].split(' (')[0].lower(), 'lo': f"{roc['ci_low']:.3f}",
        'hi': f"{roc['ci_high']:.3f}", 'p': p_str,
    }


def _compare_conclusion(roc1: dict, roc2: dict, delong: dict) -> str:
    p_str = 'p < .001' if delong['p_value'] < 0.001 else f"p = {delong['p_value']:.4f}"
    if delong['significant']:
        better = roc1['test_col'] if roc1['auc'] > roc2['auc'] else roc2['test_col']
        return gettext(
            'DeLong testine göre %(t1)s (AUC = %(a1)s) ile %(t2)s (AUC = %(a2)s) arasındaki fark '
            'istatistiksel olarak anlamlıdır (z = %(z)s, %(p)s); %(better)s değişkeni daha iyi ayırt '
            'edicilik göstermektedir.'
        ) % {
            't1': roc1['test_col'], 'a1': f"{roc1['auc']:.3f}", 't2': roc2['test_col'],
            'a2': f"{roc2['auc']:.3f}", 'z': f"{delong['z']:.3f}", 'p': p_str, 'better': better,
        }
    return gettext(
        'DeLong testine göre %(t1)s (AUC = %(a1)s) ile %(t2)s (AUC = %(a2)s) arasındaki fark '
        'istatistiksel olarak anlamlı değildir (z = %(z)s, %(p)s).'
    ) % {
        't1': roc1['test_col'], 'a1': f"{roc1['auc']:.3f}", 't2': roc2['test_col'],
        'a2': f"{roc2['auc']:.3f}", 'z': f"{delong['z']:.3f}", 'p': p_str,
    }


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
    BLUE = colors.HexColor('#1d4ed8')
    title_s = ParagraphStyle('T', parent=styles['Heading1'], fontSize=16, spaceAfter=6, fontName='DejaVuSans')
    h2_s = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, spaceAfter=4, fontName='DejaVuSans')
    norm_s = ParagraphStyle('N', parent=styles['Normal'], fontName='DejaVuSans', fontSize=9)

    def p_str(v):
        return '< .001' if v < 0.001 else f'{v:.4f}'

    def roc_table(roc):
        rows = [
            [gettext('AUC'), f"{roc['auc']:.4f}"],
            ['%95 GA', f"[{roc['ci_low']:.4f}, {roc['ci_high']:.4f}]"],
            ['p (AUC = 0.5)', p_str(roc['p_value'])],
            [gettext('Yorum'), roc['interpretation']],
            [gettext('Optimal Kesim Noktası (Youden J)'), f"{roc['best_threshold']:.4f}"],
            [gettext('Duyarlılık (Sensitivity)'), f"{roc['sensitivity']:.4f}"],
            [gettext('Özgüllük (Specificity)'), f"{roc['specificity']:.4f}"],
            ['PPV', f"{roc['ppv']:.4f}" if roc['ppv'] is not None else '—'],
            ['NPV', f"{roc['npv']:.4f}" if roc['npv'] is not None else '—'],
            [gettext('Doğruluk (Accuracy)'), f"{roc['accuracy']:.4f}" if roc['accuracy'] is not None else '—'],
            ['LR+', f"{roc['lr_plus']:.4f}" if roc['lr_plus'] is not None else '—'],
            ['LR−', f"{roc['lr_minus']:.4f}" if roc['lr_minus'] is not None else '—'],
        ]
        tbl = Table(rows, colWidths=[7*cm, 9*cm])
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), BLUE),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.whitesmoke, colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        return tbl

    story = []
    story.append(Paragraph(gettext('ROC Eğrisi / Tanısal Tarama Analizi Raporu'), title_s))
    story.append(Paragraph(gettext('Dosya: %(filename)s') % {'filename': filename}, norm_s))
    story.append(Spacer(1, 0.4*cm))

    summary_rows = [
        [gettext('Referans Değişkeni'), f"{result['ref_col']} = {result['positive_label']}"],
        ['N', str(result['n'])],
        [gettext('Pozitif / Negatif'), f"{result['n_pos']} / {result['n_neg']}"],
    ]
    sum_tbl = Table(summary_rows, colWidths=[6*cm, 10*cm])
    sum_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), BLUE),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(sum_tbl)
    story.append(Spacer(1, 0.5*cm))

    if result['mode'] == 'single':
        story.append(Paragraph(gettext('ROC Analizi: %(test)s') % {'test': result['roc']['test_col']}, h2_s))
        story.append(roc_table(result['roc']))
    else:
        story.append(Paragraph(gettext('ROC Analizi: %(test)s') % {'test': result['roc1']['test_col']}, h2_s))
        story.append(roc_table(result['roc1']))
        story.append(Spacer(1, 0.4*cm))
        story.append(Paragraph(gettext('ROC Analizi: %(test)s') % {'test': result['roc2']['test_col']}, h2_s))
        story.append(roc_table(result['roc2']))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(gettext('ROC Eğrisi'), h2_s))
    if result.get('roc_plot_b64'):
        import base64
        img_data = base64.b64decode(result['roc_plot_b64'])
        story.append(Image(io.BytesIO(img_data), width=11*cm, height=9.5*cm))
    story.append(Spacer(1, 0.5*cm))

    if result['mode'] == 'compare':
        dl = result['delong']
        story.append(Paragraph(gettext("DeLong Testi (İki Test Karşılaştırması)"), h2_s))
        dl_rows = [
            [gettext('AUC Farkı'), f"{dl['auc_diff']:.4f}"],
            ['SE', f"{dl['se_diff']:.4f}"],
            ['z', f"{dl['z']:.3f}"],
            ['p', p_str(dl['p_value'])],
            [gettext('Sonuç'), gettext('Anlamlı fark (p < .05)') if dl['significant'] else gettext('Anlamlı fark yok (p ≥ .05)')],
        ]
        dl_tbl = Table(dl_rows, colWidths=[6*cm, 10*cm])
        sig_bg = colors.HexColor('#d4edda') if dl['significant'] else colors.HexColor('#f8d7da')
        dl_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), BLUE),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('BACKGROUND', (1, -1), (1, -1), sig_bg),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ROWBACKGROUNDS', (1, 0), (1, -2), [colors.whitesmoke, colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(dl_tbl)
        story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(gettext('Yorum'), h2_s))
    story.append(Paragraph(result['conclusion'], norm_s))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(gettext('APA Formatında Raporlama'), h2_s))
    apa_tbl = Table([[Paragraph(result['conclusion'], norm_s)]], colWidths=[16*cm])
    apa_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eff6ff')),
        ('BOX', (0, 0), (-1, -1), 1, BLUE),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(apa_tbl)
    append_ai_comment(story, result, norm_s, '#eff6ff', BLUE)

    doc.build(story)
    return buf.getvalue()
