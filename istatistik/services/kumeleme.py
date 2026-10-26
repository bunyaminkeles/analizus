"""
Kümeleme Analizi (K-means / Hiyerarşik Cluster) — pazarlama, işletme ve eğitim
tezlerinde yaygın kullanılan gözetimsiz (unsupervised) bir makine öğrenmesi
yöntemi. Seçilen sayısal değişkenler StandardScaler ile ölçeklenir; küme
sayısı (k) verilmezse k=2..10 arasında silhouette skoruna göre otomatik
seçilir. K-means için elbow/silhouette grafiği, hiyerarşik (Ward) yöntem için
dendrogram üretilir.
"""
import io
import base64
from django.utils.translation import gettext
import numpy as np

_MAX_ROWS = 3000
_MAX_K = 10


def analyze(df, columns=None, method: str = 'kmeans', n_clusters=None) -> dict:
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    from scipy.cluster.hierarchy import linkage, fcluster

    method = method if method in ('kmeans', 'hierarchical') else 'kmeans'

    df_num = df.select_dtypes(include=[np.number])
    if columns:
        valid = [c for c in columns if c in df_num.columns]
        if not valid:
            raise ValueError(gettext('Seçilen sütunlar sayısal değil veya bulunamadı.'))
        df_num = df_num[valid]
    df_num = df_num.dropna()

    n_vars = len(df_num.columns)
    n = len(df_num)

    if n_vars < 2:
        raise ValueError(gettext('En az 2 sayısal değişken seçilmelidir.'))
    if n < 20:
        raise ValueError(gettext('En az 20 gözlem (satır) gereklidir, %(n)s satır bulundu.') % {'n': n})

    sampled = False
    if n > _MAX_ROWS:
        df_num = df_num.sample(_MAX_ROWS, random_state=42)
        n = len(df_num)
        sampled = True

    cols = list(df_num.columns)
    X_raw = df_num.values.astype(float)
    scaler = StandardScaler()
    X = scaler.fit_transform(X_raw)

    max_k = min(_MAX_K, n - 1)
    if max_k < 2:
        raise ValueError(gettext('Kümeleme için yetersiz gözlem sayısı.'))

    Z = linkage(X, method='ward') if method == 'hierarchical' else None

    def _fit(k):
        if method == 'kmeans':
            model = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = model.fit_predict(X)
            return labels, float(model.inertia_), model.cluster_centers_
        labels = fcluster(Z, k, criterion='maxclust') - 1
        return labels, None, None

    candidate_ks = list(range(2, max_k + 1))
    diagnostics = []
    cache = {}
    for k in candidate_ks:
        labels, inertia, centers = _fit(k)
        sil = float(silhouette_score(X, labels))
        diagnostics.append({
            'k': k,
            'silhouette': round(sil, 4),
            'inertia': round(inertia, 2) if inertia is not None else None,
        })
        cache[k] = (labels, centers, sil)

    k_auto = max(diagnostics, key=lambda d: d['silhouette'])['k']

    if n_clusters:
        k_used = int(n_clusters)
        if k_used < 2 or k_used > max_k:
            raise ValueError(gettext('Küme sayısı 2 ile %(max_k)s arasında olmalıdır.') % {'max_k': max_k})
    else:
        k_used = k_auto

    labels, centers, silhouette_overall = cache[k_used]

    cluster_profile = []
    for c in range(k_used):
        mask = labels == c
        cnt = int(mask.sum())
        row = {'cluster': c + 1, 'n': cnt, 'pct': round(cnt / n * 100, 1)}
        for i, col in enumerate(cols):
            row[col] = round(float(X_raw[mask, i].mean()), 3)
        cluster_profile.append(row)

    diagnostic_plot_b64 = _build_diagnostic_plot(diagnostics, method, k_used, Z)
    scatter_plot_b64, pca_used = _build_scatter_plot(X, labels, cols, centers)

    return {
        'method': method,
        'method_label': gettext('K-means') if method == 'kmeans' else gettext('Hiyerarşik (Ward)'),
        'columns': cols,
        'n': n,
        'n_vars': n_vars,
        'sampled': sampled,
        'k_used': k_used,
        'k_auto': k_auto,
        'k_manual': bool(n_clusters),
        'max_k': max_k,
        'silhouette': round(float(silhouette_overall), 4),
        'silhouette_interpretation': _interpret_silhouette(silhouette_overall),
        'cluster_profile': cluster_profile,
        'diagnostics': diagnostics,
        'diagnostic_plot_b64': diagnostic_plot_b64,
        'scatter_plot_b64': scatter_plot_b64,
        'pca_used': pca_used,
    }


def _interpret_silhouette(s: float) -> str:
    """Kaufman & Rousseeuw (1990) silhouette yorum eşikleri."""
    if s >= 0.71:
        return gettext('Güçlü küme yapısı (≥ 0.71)')
    if s >= 0.51:
        return gettext('Makul küme yapısı (0.51–0.70)')
    if s >= 0.26:
        return gettext('Zayıf küme yapısı (0.26–0.50)')
    return gettext('Anlamlı küme yapısı bulunamadı (≤ 0.25)')


def _build_diagnostic_plot(diagnostics, method, k_used, Z) -> str:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    if method == 'kmeans':
        ks = [d['k'] for d in diagnostics]
        inertias = [d['inertia'] for d in diagnostics]
        sils = [d['silhouette'] for d in diagnostics]
        fig, ax1 = plt.subplots(figsize=(6.5, 4.2), dpi=110)
        ax1.plot(ks, inertias, 'o-', color='#60a5fa', label=gettext('Küme İçi Hata Kareler Toplamı (WCSS)'))
        ax1.set_xlabel(gettext('Küme Sayısı (k)'))
        ax1.set_ylabel(gettext('WCSS'), color='#60a5fa')
        ax1.tick_params(axis='y', labelcolor='#60a5fa')
        ax1.set_xticks(ks)
        ax2 = ax1.twinx()
        ax2.plot(ks, sils, 's--', color='#4ade80', label=gettext('Silhouette Skoru'))
        ax2.set_ylabel(gettext('Silhouette Skoru'), color='#4ade80')
        ax2.tick_params(axis='y', labelcolor='#4ade80')
        ax1.axvline(x=k_used, color='#f87171', linestyle=':', linewidth=1.5)
        fig.tight_layout()
    else:
        from scipy.cluster.hierarchy import dendrogram
        fig, ax = plt.subplots(figsize=(6.5, 4.2), dpi=110)
        dendrogram(Z, truncate_mode='lastp', p=15, show_leaf_counts=True, ax=ax)
        ax.set_xlabel(gettext('Gözlem Kümeleri (parantez: eleman sayısı)'))
        ax.set_ylabel(gettext('Bağlantı Mesafesi (Ward)'))
        fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('ascii')


def _build_scatter_plot(X, labels, cols, centers):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    n_vars = X.shape[1]
    if n_vars == 2:
        coords = X
        center_coords = centers
        xlabel, ylabel = cols[0], cols[1]
        pca_used = False
    else:
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2, random_state=42)
        coords = pca.fit_transform(X)
        center_coords = pca.transform(centers) if centers is not None else None
        xlabel, ylabel = 'PC1', 'PC2'
        pca_used = True

    fig, ax = plt.subplots(figsize=(6, 4.5), dpi=110)
    cmap = plt.get_cmap('tab10')
    for c in sorted(set(labels)):
        mask = labels == c
        ax.scatter(coords[mask, 0], coords[mask, 1], s=18, alpha=0.7,
                   color=cmap(c % 10), label=gettext('Küme %(c)s') % {'c': c + 1})
    if center_coords is not None:
        ax.scatter(center_coords[:, 0], center_coords[:, 1], marker='X', s=160,
                   color='black', edgecolor='white', linewidths=1.2, label=gettext('Merkezler'))
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(fontsize=7, loc='best')
    ax.grid(alpha=0.2)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('ascii'), pca_used


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
    TEAL = colors.HexColor('#0e7490')
    title_s = ParagraphStyle('T', parent=styles['Heading1'], fontSize=16, spaceAfter=6, fontName='DejaVuSans')
    h2_s = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, spaceAfter=4, fontName='DejaVuSans')
    norm_s = ParagraphStyle('N', parent=styles['Normal'], fontName='DejaVuSans', fontSize=9)

    def p_str(v):
        return '< .001' if v < 0.001 else f'{v:.4f}'

    story = []
    story.append(Paragraph(gettext('Kümeleme Analizi Raporu'), title_s))
    story.append(Paragraph(gettext('Dosya: %(filename)s') % {'filename': filename}, norm_s))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph(gettext('Model Özeti'), h2_s))
    summary_rows = [
        [gettext('Yöntem'), result['method_label']],
        [gettext('Değişkenler'), ', '.join(result['columns'])],
        ['N', str(result['n']) + (' ' + gettext('(örneklenmiş)') if result['sampled'] else '')],
        [gettext('Küme Sayısı (k)'), f"{result['k_used']}" + (gettext(' (elle seçildi)') if result['k_manual'] else gettext(' (otomatik seçildi)'))],
        [gettext('Silhouette Skoru'), f"{result['silhouette']:.4f} — {result['silhouette_interpretation']}"],
    ]
    sum_tbl = Table(summary_rows, colWidths=[6*cm, 10*cm])
    sum_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), TEAL),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(sum_tbl)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(gettext('Küme Sayısı (k) Seçim Diyagnostiği'), h2_s))
    diag_rows = [[gettext('k'), gettext('Silhouette'), gettext('WCSS')]]
    for d in result['diagnostics']:
        diag_rows.append([str(d['k']), f"{d['silhouette']:.4f}", f"{d['inertia']:.2f}" if d['inertia'] is not None else '—'])
    diag_tbl = Table(diag_rows, colWidths=[3*cm, 4*cm, 4*cm])
    diag_style = [
        ('BACKGROUND', (0, 0), (-1, 0), TEAL),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]
    for i, d in enumerate(result['diagnostics'], start=1):
        if d['k'] == result['k_used']:
            diag_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#d4edda')))
    diag_tbl.setStyle(TableStyle(diag_style))
    story.append(diag_tbl)
    story.append(Spacer(1, 0.4*cm))

    if result.get('diagnostic_plot_b64'):
        img_data = base64.b64decode(result['diagnostic_plot_b64'])
        story.append(Image(io.BytesIO(img_data), width=13*cm, height=8.4*cm))
        story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(gettext('Küme Profili'), h2_s))
    profile_headers = [gettext('Küme'), 'N', '%'] + result['columns']
    profile_rows = [profile_headers]
    for row in result['cluster_profile']:
        profile_rows.append([str(row['cluster']), str(row['n']), f"{row['pct']}%"] + [f"{row[c]:.3f}" for c in result['columns']])
    n_cols = len(profile_headers)
    first_w = 1.5 * cm
    n_w = 1.5 * cm
    pct_w = 1.5 * cm
    other_w = (16 - first_w/cm - n_w/cm - pct_w/cm) / (n_cols - 3) * cm
    col_widths = [first_w, n_w, pct_w] + [other_w] * (n_cols - 3)
    profile_tbl = Table(profile_rows, colWidths=col_widths)
    profile_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TEAL),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(profile_tbl)
    story.append(Spacer(1, 0.5*cm))

    if result.get('scatter_plot_b64'):
        story.append(Paragraph(gettext('Küme Dağılım Grafiği'), h2_s))
        if result.get('pca_used'):
            story.append(Paragraph(
                '<font color="#666666" size="8">' + gettext('İkiden fazla değişken seçildiği için '
                'gösterim PCA (Temel Bileşenler Analizi) ile 2 boyuta indirgenmiştir.') + '</font>',
                norm_s
            ))
        img_data = base64.b64decode(result['scatter_plot_b64'])
        story.append(Image(io.BytesIO(img_data), width=12*cm, height=9*cm))
        story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph(gettext('APA Formatında Raporlama'), h2_s))
    apa_text = gettext(
        '{n} gözlem üzerinde {n_vars} değişken ({cols}) kullanılarak {method} kümeleme analizi '
        'uygulanmıştır. Silhouette katsayısına göre en uygun küme sayısı k = {k} olarak '
        'belirlenmiş (silhouette katsayısı = {sil}), bu değer {interp} düzeyinde bir küme '
        'yapısına işaret etmektedir.'
    ).format(n=result['n'], n_vars=result['n_vars'], cols=', '.join(result['columns']),
             method=result['method_label'], k=result['k_used'], sil=f"{result['silhouette']:.3f}",
             interp=result['silhouette_interpretation'].split(' (')[0].lower())
    apa_tbl = Table([[Paragraph(apa_text, norm_s)]], colWidths=[16*cm])
    apa_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecfeff')),
        ('BOX', (0, 0), (-1, -1), 1, TEAL),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(apa_tbl)
    append_ai_comment(story, result, norm_s, '#ecfeff', TEAL)

    doc.build(story)
    return buf.getvalue()
