"""
Açıklayıcı Faktör Analizi (AFA / EFA)
Girdi: pandas DataFrame (satır=katılımcı, sütun=madde)
"""
import io
from django.utils.translation import gettext
import numpy as np


def _patch_sklearn_compat():
    """scikit-learn 1.6+ factor_analyzer uyumluluk yaması (force_all_finite kaldırıldı)."""
    try:
        import sklearn.utils.validation as _val
        _orig = _val.check_array
        import functools
        @functools.wraps(_orig)
        def _compat(*args, **kw):
            kw.pop('force_all_finite', None)
            return _orig(*args, **kw)
        _val.check_array = _compat
        try:
            import factor_analyzer.factor_analyzer as _fa
            _fa.check_array = _compat
        except Exception:
            pass
    except Exception:
        pass


def analyze(df, columns=None, n_factors=None, rotation='varimax', method='minres') -> dict:
    _patch_sklearn_compat()
    from factor_analyzer import FactorAnalyzer
    from factor_analyzer.factor_analyzer import calculate_kmo, calculate_bartlett_sphericity

    df_num = df.select_dtypes(include=[np.number])
    if columns:
        valid = [c for c in columns if c in df_num.columns]
        if not valid:
            raise ValueError(gettext('Seçilen sütunlar sayısal değil veya bulunamadı.'))
        df_num = df_num[valid]
    df_num = df_num.dropna()

    k = len(df_num.columns)
    n = len(df_num)

    if k < 3:
        raise ValueError(gettext('En az 3 madde (sütun) gereklidir.'))
    if n < 10:
        raise ValueError(gettext('En az 10 katılımcı (satır) gereklidir.'))

    warnings = []
    if n < k * 5:
        warnings.append(
            gettext('Örneklem yetersiz olabilir: %(n)s katılımcı / %(k)s madde = %(v)s:1 oran. Önerilen minimum 5:1 (ideali 10:1). Sonuçlar kararsız olabilir.') % {'n': n, 'k': k, 'v': f'{n / k:.1f}'}
        )

    data = df_num.values

    # KMO ve Bartlett testleri
    kmo_all, kmo_model = calculate_kmo(data)
    chi2, p_bartlett = calculate_bartlett_sphericity(data)

    # Faktör sayısı belirleme (eigenvalue > 1 kuralı)
    fa_eigen = FactorAnalyzer(n_factors=k, rotation=None)
    fa_eigen.fit(data)
    eigenvalues, _ = fa_eigen.get_eigenvalues()
    n_factors_auto = int(np.sum(eigenvalues > 1))
    if n_factors_auto < 1:
        n_factors_auto = 1
    if n_factors_auto > k - 1:
        n_factors_auto = k - 1

    # Kullanıcı n_factors vermişse onu kullan
    if n_factors is None:
        n_factors_used = n_factors_auto
    else:
        n_factors_used = int(n_factors)
        if n_factors_used < 1:
            n_factors_used = 1
        if n_factors_used > k - 1:
            n_factors_used = k - 1

    # Asıl analiz
    fa = FactorAnalyzer(n_factors=n_factors_used, rotation=rotation, method=method)
    fa.fit(data)

    loadings = fa.loadings_
    communalities = fa.get_communalities()
    variance = fa.get_factor_variance()  # (SS Loadings, % Variance, Cumulative Var)

    cols = list(df_num.columns)
    factor_names = [f'F{i+1}' for i in range(n_factors_used)]

    # Faktör yükleri tablosu
    loading_table = []
    for i, col in enumerate(cols):
        row = {'item': str(col)}
        for j in range(n_factors_used):
            row[factor_names[j]] = round(float(loadings[i, j]), 3)
        row['communality'] = round(float(communalities[i]), 3)
        loading_table.append(row)

    # Varyans açıklama tablosu
    variance_table = []
    for j in range(n_factors_used):
        variance_table.append({
            'factor': factor_names[j],
            'ss_loadings': round(float(variance[0][j]), 3),
            'pct_variance': round(float(variance[1][j]) * 100, 2),
            'cumulative_pct': round(float(variance[2][j]) * 100, 2),
        })

    # Eigenvalue tablosu (ilk 10 veya k tane)
    eigen_table = []
    for i, ev in enumerate(eigenvalues[:min(k, 15)]):
        eigen_table.append({
            'factor': i + 1,
            'eigenvalue': round(float(ev), 3),
            'pct_variance': round(float(ev / k) * 100, 2),
        })

    kmo_interpretation = _interpret_kmo(kmo_model)
    bartlett_sig = 'p < 0.001' if p_bartlett < 0.001 else f'p = {p_bartlett:.3f}'

    return {
        'n_items': k,
        'n_cases': n,
        'n_factors': n_factors_used,
        'n_factors_auto': n_factors_auto,
        'rotation': rotation,
        'kmo': round(float(kmo_model), 3),
        'kmo_interpretation': kmo_interpretation,
        'bartlett_chi2': round(float(chi2), 3),
        'bartlett_p': round(float(p_bartlett), 4),
        'bartlett_sig': bartlett_sig,
        'bartlett_ok': bool(p_bartlett < 0.05),
        'factor_names': factor_names,
        'loading_table': loading_table,
        'variance_table': variance_table,
        'eigen_table': eigen_table,
        'total_variance_explained': round(float(variance[2][-1]) * 100, 2),
        'warnings': warnings,
    }


def _interpret_kmo(kmo: float) -> str:
    if kmo >= 0.90:
        return gettext('Mükemmel (≥ 0.90)')
    if kmo >= 0.80:
        return gettext('Çok İyi (0.80–0.90)')
    if kmo >= 0.70:
        return gettext('İyi (0.70–0.80)')
    if kmo >= 0.60:
        return gettext('Orta (0.60–0.70)')
    if kmo >= 0.50:
        return gettext('Düşük (0.50–0.60)')
    return gettext('Kabul Edilemez (< 0.50)')


def _sentence_level(label: str) -> str:
    """'Orta (0.60–0.70)' → 'orta': cümle içi kullanım; Türkçede 'İ'.lower() sorunu."""
    from django.utils.translation import get_language
    level = label.split(' (')[0]
    if (get_language() or '').startswith('tr'):
        level = level.replace('İ', 'i').replace('I', 'ı')
    return level.lower()


def _apa_text(result: dict) -> str:
    """AFA APA paragrafı — ekrandaki JS (afa.html) ile AYNI msgid'ler.
    25 Eylül 2026 düzeltmeleri: Bartlett anlamsızsa 'anlamlı bulunmuştur'
    yazılmıyordu değil, HEP yazılıyordu; özdeğer>1 ifadesi faktör sayısı elle
    seçildiğinde de yazılıyordu; ekran ve PDF metinleri farklıydı."""
    pct = gettext('%%%(value)s') % {'value': result['total_variance_explained']}
    parts = [gettext('{k} maddeden oluşan ölçeğin faktör yapısını belirlemek amacıyla {rotation} rotasyonu ile '
                     'Açıklayıcı Faktör Analizi (AFA) uygulanmıştır (n = {n}).').format(
        k=result['n_items'], rotation=result['rotation'].capitalize(), n=result['n_cases'])]
    bv = dict(kmo=f"{result['kmo']:.3f}", level=_sentence_level(result['kmo_interpretation']),
              chi2=f"{result['bartlett_chi2']:.2f}",
              p='p < .001' if result['bartlett_p'] < 0.001 else f"p = {result['bartlett_p']:.3f}")
    if result['bartlett_ok']:
        parts.append(gettext('KMO örneklem yeterlilik katsayısı {kmo} ({level}) olarak hesaplanmış, Bartlett Küresellik '
                             'Testi anlamlı bulunmuştur (χ² = {chi2}, {p}).').format(**bv))
    else:
        parts.append(gettext('KMO örneklem yeterlilik katsayısı {kmo} ({level}) olarak hesaplanmış, Bartlett Küresellik '
                             'Testi anlamlı bulunmamıştır (χ² = {chi2}, {p}); veri faktör analizi için uygun '
                             'olmayabilir.').format(**bv))
    if result['n_factors'] == result['n_factors_auto']:
        parts.append(gettext('Özdeğer > 1 kriterine göre {nf} faktörlü yapı elde edilmiş ve bu yapı toplam varyansın '
                             '{pct} kadarını açıklamıştır.').format(nf=result['n_factors'], pct=pct))
    else:
        parts.append(gettext('Araştırmacı tarafından belirlenen {nf} faktörlü yapı toplam varyansın {pct} kadarını '
                             'açıklamıştır.').format(nf=result['n_factors'], pct=pct))
    return ' '.join(parts)


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
    TEAL = '#065f46'
    title_style = ParagraphStyle('T', parent=styles['Heading1'], fontSize=16, spaceAfter=6,
                                 fontName='DejaVuSans')
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, spaceAfter=4,
                        fontName='DejaVuSans')
    normal = ParagraphStyle('N', parent=styles['Normal'], fontName='DejaVuSans', fontSize=9)

    story = []
    story.append(Paragraph(gettext('Açıklayıcı Faktör Analizi Raporu'), title_style))
    story.append(Paragraph(gettext('Dosya: %(filename)s') % {'filename': filename}, normal))
    story.append(Spacer(1, 0.3*cm))

    # Özet
    kmo_ok = result['kmo'] >= 0.50
    summary = [
        [gettext('Madde Sayısı'), str(result['n_items'])],
        [gettext('Katılımcı Sayısı'), str(result['n_cases'])],
        [gettext('Çıkarılan Faktör Sayısı'), str(result['n_factors'])],
        [gettext('Rotasyon'), result['rotation'].capitalize()],
        [gettext('KMO Örneklem Yeterliliği'), f"{result['kmo']} — {result['kmo_interpretation']}"],
        [gettext('Bartlett Küresellik Testi'), f"χ²={result['bartlett_chi2']}, {result['bartlett_sig']}"],
        [gettext('Açıklanan Toplam Varyans'), gettext('%%%(value)s') % {'value': result['total_variance_explained']}],
    ]
    t = Table(summary, colWidths=[7*cm, 9*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor(TEAL)),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('BACKGROUND', (1, 4), (1, 4), colors.HexColor('#d4edda') if kmo_ok else colors.HexColor('#f8d7da')),
        ('BACKGROUND', (1, 5), (1, 5), colors.HexColor('#d4edda') if result['bartlett_ok'] else colors.HexColor('#f8d7da')),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))

    # Faktör yükleri tablosu
    story.append(Paragraph(gettext('Faktör Yük Matrisi (Rotasyonlu)'), h2))
    factor_names = result['factor_names']
    headers = [gettext('Madde')] + factor_names + [gettext('Communality')]
    rows = [headers]
    for row in result['loading_table']:
        r = [row['item']] + [f"{row[f]:.3f}" for f in factor_names] + [f"{row['communality']:.3f}"]
        rows.append(r)

    n_cols = len(headers)
    item_w = 4.5 * cm
    other_w = (16 - 4.5) / (n_cols - 1) * cm
    col_widths = [item_w] + [other_w] * (n_cols - 1)
    tbl = Table(rows, colWidths=col_widths)
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(TEAL)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.5*cm))

    # Varyans açıklama tablosu
    story.append(Paragraph(gettext('Açıklanan Varyans'), h2))
    var_headers = [gettext('Faktör'), gettext('SS Yüklemeler'), gettext('% Varyans'), gettext('Kümülatif %')]
    var_rows = [var_headers]
    for vr in result['variance_table']:
        var_rows.append([vr['factor'], f"{vr['ss_loadings']:.3f}",
                         gettext('%%%(value)s') % {'value': f"{vr['pct_variance']:.2f}"},
                         gettext('%%%(value)s') % {'value': f"{vr['cumulative_pct']:.2f}"}])
    var_tbl = Table(var_rows, colWidths=[3*cm, 4*cm, 4*cm, 5*cm])
    var_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(TEAL)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(var_tbl)
    story.append(Spacer(1, 0.5*cm))

    # APA raporlama
    story.append(Paragraph(gettext('APA Formatında Raporlama'), h2))
    apa = _apa_text(result)
    apa_tbl = Table([[Paragraph(apa, normal)]], colWidths=[16*cm])
    apa_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0fff4')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(TEAL)),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(apa_tbl)

    doc.build(story)
    return buf.getvalue()
