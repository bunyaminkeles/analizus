"""
10 Bibliometrik Analiz Modülü
Beyaz/açık tema, çok renkli grafikler, profesyonel görünüm.
Her fonksiyon (title, matplotlib.figure.Figure) tuple döndürür.
"""
import io
import logging
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)

# ── Türkçe Lemmatization (zeyrek) ──────────────────────────────────
_tr_analyzer = None
_tr_stopwords = None

def _get_tr_analyzer():
    global _tr_analyzer
    if _tr_analyzer is None:
        try:
            import zeyrek
            _tr_analyzer = zeyrek.MorphAnalyzer()
        except Exception as e:
            logger.warning(f'zeyrek yüklenemedi: {e}')
            _tr_analyzer = False
    return _tr_analyzer if _tr_analyzer is not False else None

def _get_tr_stopwords():
    global _tr_stopwords
    if _tr_stopwords is None:
        try:
            import nltk
            try:
                _tr_stopwords = set(nltk.corpus.stopwords.words('turkish'))
            except LookupError:
                nltk.download('stopwords', quiet=True)
                _tr_stopwords = set(nltk.corpus.stopwords.words('turkish'))
        except Exception:
            _tr_stopwords = set()
    return _tr_stopwords

def lemmatize_word(word: str) -> str:
    """Tek Türkçe kelimeyi lemmatize eder. Başarısızsa orijinali döner."""
    analyzer = _get_tr_analyzer()
    if not analyzer:
        return word
    try:
        result = analyzer.lemmatize(word)
        if result and result[0][1]:
            lemma = result[0][1][0].lower()
            if len(lemma) >= 2:
                return lemma
    except Exception:
        pass
    return word

def normalize_keywords(keywords: list[str]) -> list[str]:
    """
    Keyword listesini normalize eder:
    - Stopword filtrele
    - Tek kelime ise lemmatize et
    - Çok kelimeli ifadeleri olduğu gibi bırak (makine öğrenmesi vb.)
    """
    stopwords = _get_tr_stopwords()
    result = []
    for kw in keywords:
        kw = kw.strip().lower()
        if not kw or len(kw) < 2:
            continue
        if kw in stopwords:
            continue
        # Çok kelimeli → olduğu gibi bırak
        if ' ' in kw:
            result.append(kw)
        else:
            result.append(lemmatize_word(kw))
    return result

def normalize_abstract_words(abstract: str) -> list[str]:
    """Abstract'tan anlamlı kelimeleri çıkarır, lemmatize eder."""
    stopwords = _get_tr_stopwords()
    words = []
    for w in abstract.split():
        w = w.strip('.,;:()[]{}"\'-').lower()
        if len(w) < 4 or w in stopwords:
            continue
        words.append(lemmatize_word(w))
    return words

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Beyaz profesyonel tema ──────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor':     'white',
    'axes.facecolor':       '#f8fafc',
    'axes.edgecolor':       '#cbd5e0',
    'axes.labelcolor':      '#1e293b',
    'xtick.color':          '#475569',
    'ytick.color':          '#475569',
    'text.color':           '#1e293b',
    'grid.color':           '#e2e8f0',
    'grid.linestyle':       '--',
    'grid.alpha':           0.8,
    'font.family':          'DejaVu Sans',
    'font.size':            11,
    'axes.titlesize':       15,
    'axes.titleweight':     'bold',
    'axes.titlepad':        18,
    'axes.labelsize':       12,
    'axes.spines.top':      False,
    'axes.spines.right':    False,
    'figure.dpi':           100,
})

# ── Tableau-10 renk paleti (renk körü dostu, profesyonel) ──────────
PALETTE = [
    '#4E79A7',  # Mavi
    '#F28E2B',  # Turuncu
    '#E15759',  # Kırmızı
    '#76B7B2',  # Teal
    '#59A14F',  # Yeşil
    '#EDC948',  # Sarı
    '#B07AA1',  # Mor
    '#FF9DA7',  # Pembe
    '#9C755F',  # Kahverengi
    '#BAB0AC',  # Gri
    '#4E79A7',  # Tekrar başlar
    '#F28E2B',
    '#E15759',
    '#76B7B2',
    '#59A14F',
]

TREND_BLUE  = '#2563EB'
TREND_RED   = '#DC2626'
TREND_AMBER = '#D97706'


def run_all_analyses(records: list[dict]) -> list[tuple[str, bytes]]:
    """
    Tüm analizleri çalıştırır.
    Her figür üretilir üretilmez PNG bytes'a çevrilip kapatılır —
    tüm Figure nesnelerini aynı anda bellekte tutmak yerine sadece
    hafif PNG bytes listesi saklanır.
    """
    import gc as _gc
    analyses = [
        ('Yıllara Göre Yayın Trendi',              lambda: publication_trend(records)),
        ('Yıllık Büyüme Oranı',                    lambda: publication_growth_rate(records)),
        ('En Verimli Yazarlar (Top 15)',            lambda: top_authors(records)),
        ('Lotka Kanunu — Yazar Üretkenliği',        lambda: lotka_law(records)),
        ('Anahtar Kelime Bulutu',                   lambda: keyword_cloud(records)),
        ('Anahtar Kelime Eş-Oluşum Ağı',           lambda: keyword_cooccurrence(records)),
        ('Anahtar Kelime Zaman Trendi',             lambda: keyword_trend(records)),
        ('En Çok Atıf Alan Yayınlar (Top 10)',      lambda: top_cited(records)),
        ('En Çok Yayın Yapılan Dergiler',           lambda: top_journals(records)),
        ('Kurum / Ülke Dağılımı (Top 10)',          lambda: top_institutions(records)),
        ('Ülke İşbirliği Ağı',                      lambda: country_collaboration(records)),
        ('Yazar İşbirliği Ağı',                     lambda: author_collaboration(records)),
        ('Yayın Türleri Dağılımı',                  lambda: publication_types(records)),
        ('Atıf Analizi ve H-index',                 lambda: citation_analysis(records)),
        ('Yıllık Atıf Trendi',                      lambda: annual_citation_trend(records)),
        ('Araştırma Konusu Kümeleri (Topic Map)',    lambda: topic_map(records)),
        ('Araştırma Boşluğu Haritası (Research Gap)', lambda: research_gap(records)),
    ]
    results = []
    for title, fn in analyses:
        try:
            fig = fn()
            if fig is not None:
                buf = io.BytesIO()
                fig.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
                buf.seek(0)
                png_bytes = buf.getvalue()
                buf.close()
                plt.close(fig)
                del fig
                _gc.collect()
                results.append((title, png_bytes))
        except Exception as e:
            logger.warning(f'Analiz başarısız [{title}]: {e}')
            try:
                plt.close('all')
            except Exception:
                pass
    return results


# ─────────────────────────── 1. Yayın Trendi ───────────────────────────

def publication_trend(records: list[dict]):
    years = [r['year'] for r in records if r.get('year') and 1900 < r['year'] < 2100]
    if not years:
        return None

    counter = Counter(years)
    sorted_years = sorted(counter.keys())
    counts = [counter[y] for y in sorted_years]

    # Çubuk rengi: değer yoğunluğuna göre mavi gradyan
    max_c = max(counts) or 1
    bar_colors = [plt.cm.Blues(0.35 + 0.55 * c / max_c) for c in counts]

    fig, ax = plt.subplots(figsize=(10, 9))
    bars = ax.bar(sorted_years, counts, color=bar_colors, width=0.7, zorder=2,
                  edgecolor='white', linewidth=0.5)
    ax.plot(sorted_years, counts, color=TREND_RED, linewidth=2.5,
            marker='o', markersize=7, zorder=3, label='Yayın Trendi', alpha=0.9)

    ax.set_xlabel('Yıl', fontsize=12, labelpad=8)
    ax.set_ylabel('Yayın Sayısı', fontsize=12, labelpad=8)
    ax.set_title('Yıllara Göre Yayın Trendi')
    ax.grid(axis='y', zorder=1)
    ax.legend(fontsize=11)
    _add_bar_labels(ax, bars)

    if len(sorted_years) > 20:
        ax.tick_params(axis='x', rotation=45)

    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 2. En Verimli Yazarlar ───────────────────────────

def top_authors(records: list[dict], n: int = 15):
    author_count = Counter()
    for r in records:
        for a in r.get('authors', []):
            if a:
                author_count[a.strip()] += 1
    if not author_count:
        return None

    top = author_count.most_common(n)
    names, counts = zip(*top)
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(names))]

    fig, ax = plt.subplots(figsize=(9, max(10, len(names) * 0.75)))
    y_pos = range(len(names))
    bars = ax.barh(y_pos, counts, color=colors, alpha=0.9, height=0.7,
                   edgecolor='white', linewidth=0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel('Yayın Sayısı', fontsize=12, labelpad=8)
    ax.set_title(f'En Verimli Yazarlar (Top {len(names)})')
    ax.grid(axis='x', zorder=1)
    _add_hbar_labels(ax, bars)
    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 3. Anahtar Kelime Bulutu ───────────────────────────

def keyword_cloud(records: list[dict]):
    try:
        from wordcloud import WordCloud
    except ImportError:
        logger.warning('wordcloud paketi yüklü değil')
        return None

    all_kw = []
    for r in records:
        all_kw.extend(normalize_keywords(r.get('keywords', [])))
        all_kw.extend(normalize_abstract_words(r.get('abstract', '')))

    if not all_kw:
        return None

    text = ' '.join(all_kw)
    wc = WordCloud(
        width=1400, height=900,
        background_color='white',
        colormap='tab20',
        max_words=200,
        prefer_horizontal=0.75,
        collocations=False,
        min_font_size=10,
        max_font_size=120,
    ).generate(text)

    fig, ax = plt.subplots(figsize=(10, 9))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    ax.set_facecolor('white')
    fig.patch.set_facecolor('white')
    ax.set_title('Anahtar Kelime Bulutu', fontsize=15, fontweight='bold', pad=18)
    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 4. En Çok Atıf Alan ───────────────────────────

def top_cited(records: list[dict], n: int = 10):
    with_citations = [(r['title'], r['cited_by']) for r in records if r.get('cited_by', 0) > 0]
    if not with_citations:
        return None

    top = sorted(with_citations, key=lambda x: x[1], reverse=True)[:n]
    titles, counts = zip(*top)
    short_titles = [t[:65] + '…' if len(t) > 65 else t for t in titles]
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(top))]

    fig, ax = plt.subplots(figsize=(9, max(10, len(top) * 0.75)))
    y_pos = range(len(short_titles))
    bars = ax.barh(y_pos, counts, color=colors, alpha=0.9, height=0.7,
                   edgecolor='white', linewidth=0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(short_titles, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel('Atıf Sayısı', fontsize=12, labelpad=8)
    ax.set_title(f'En Çok Atıf Alan Yayınlar (Top {len(top)})')
    ax.grid(axis='x', zorder=1)
    _add_hbar_labels(ax, bars)
    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 5. En Çok Yayın Yapılan Dergiler ───────────────────────────

def top_journals(records: list[dict], n: int = 10):
    journals = [r['journal'].strip() for r in records if r.get('journal', '').strip()]
    if not journals:
        return None

    counter = Counter(journals)
    top = counter.most_common(n)
    names, counts = zip(*top)
    short_names = [nm[:60] + '…' if len(nm) > 60 else nm for nm in names]
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(top))]

    fig, ax = plt.subplots(figsize=(9, max(10, len(top) * 0.75)))
    y_pos = range(len(short_names))
    bars = ax.barh(y_pos, counts, color=colors, alpha=0.9, height=0.7,
                   edgecolor='white', linewidth=0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(short_names, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel('Yayın Sayısı', fontsize=12, labelpad=8)
    ax.set_title(f'En Çok Yayın Yapılan Dergiler / Kaynaklar (Top {len(top)})')
    ax.grid(axis='x', zorder=1)
    _add_hbar_labels(ax, bars)
    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 6. Kurum / Ülke Dağılımı ───────────────────────────

def top_institutions(records: list[dict], n: int = 10):
    country_counter = Counter()
    inst_counter = Counter()
    for r in records:
        if r.get('country'):
            country_counter[r['country'].strip()] += 1
        if r.get('institution'):
            inst = r['institution'].split(';')[0].strip()
            if inst:
                inst_counter[inst] += 1

    if country_counter:
        top = country_counter.most_common(n)
        title_str = f'Ülkelere Göre Yayın Dağılımı (Top {min(n, len(top))})'
    elif inst_counter:
        top = inst_counter.most_common(n)
        title_str = f'Kurumlara Göre Yayın Dağılımı (Top {min(n, len(top))})'
    else:
        return None

    names, counts = zip(*top)
    short_names = [nm[:60] + '…' if len(nm) > 60 else nm for nm in names]
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(top))]

    fig, ax = plt.subplots(figsize=(9, max(10, len(top) * 0.75)))
    y_pos = range(len(short_names))
    bars = ax.barh(y_pos, counts, color=colors, alpha=0.9, height=0.7,
                   edgecolor='white', linewidth=0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(short_names, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel('Yayın Sayısı', fontsize=12, labelpad=8)
    ax.set_title(title_str)
    ax.grid(axis='x', zorder=1)
    _add_hbar_labels(ax, bars)
    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 7. Yazar İşbirliği Ağı ───────────────────────────

def author_collaboration(records: list[dict], max_authors: int = 35, min_collab: int = 2):
    try:
        import networkx as nx
    except ImportError:
        logger.warning('networkx paketi yüklü değil')
        return None

    G = nx.Graph()
    coauth_count = Counter()

    for r in records:
        authors = [a.strip() for a in r.get('authors', []) if a.strip()]
        if len(authors) < 2:
            continue
        for i in range(len(authors)):
            for j in range(i + 1, len(authors)):
                pair = tuple(sorted([authors[i], authors[j]]))
                coauth_count[pair] += 1

    for (a1, a2), weight in coauth_count.items():
        if weight >= min_collab:
            G.add_edge(a1, a2, weight=weight)

    if G.number_of_nodes() == 0:
        for (a1, a2), weight in coauth_count.most_common(60):
            G.add_edge(a1, a2, weight=weight)

    if G.number_of_nodes() == 0:
        return None

    if G.number_of_nodes() > max_authors:
        top_nodes = sorted(G.degree, key=lambda x: x[1], reverse=True)[:max_authors]
        G = G.subgraph([n for n, _ in top_nodes]).copy()

    degrees = dict(G.degree())
    max_deg = max(degrees.values()) if degrees else 1
    min_deg = min(degrees.values()) if degrees else 0
    span = (max_deg - min_deg) or 1

    # Node rengi: derece yoğunluğuna göre (plasma: sarı=az, mor=çok)
    node_colors = [plt.cm.plasma(0.15 + 0.7 * (degrees[n] - min_deg) / span)
                   for n in G.nodes()]
    node_sizes = [250 + degrees[n] * 120 for n in G.nodes()]
    edge_weights = [G[u][v].get('weight', 1) for u, v in G.edges()]

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_facecolor('#f8fafc')
    fig.patch.set_facecolor('white')

    pos = nx.spring_layout(G, seed=42, k=2.8)

    nx.draw_networkx_edges(G, pos, ax=ax,
                           alpha=0.35,
                           width=[min(w * 0.9, 4.0) for w in edge_weights],
                           edge_color='#94a3b8')

    nx.draw_networkx_nodes(G, pos, ax=ax,
                           node_size=node_sizes,
                           node_color=node_colors,
                           alpha=0.92,
                           linewidths=0.8,
                           edgecolors='white')

    # Sadece yüksek dereceli düğümlere etiket
    degree_threshold = sorted(degrees.values(), reverse=True)[min(19, len(degrees) - 1)]
    label_dict = {n: n for n, d in degrees.items() if d >= degree_threshold}
    nx.draw_networkx_labels(G, pos, labels=label_dict, ax=ax,
                            font_size=8, font_color='#1e293b', font_weight='bold')

    # Renk ölçeği (colorbar)
    sm = plt.cm.ScalarMappable(cmap=plt.cm.plasma,
                               norm=plt.Normalize(vmin=min_deg, vmax=max_deg))
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label('Ortak Yazar Sayısı', fontsize=10)

    ax.set_title('Yazar İşbirliği Ağı')
    ax.axis('off')
    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 8. Yayın Türleri ───────────────────────────

def publication_types(records: list[dict]):
    types = [r.get('pub_type', '').strip().lower() for r in records if r.get('pub_type', '').strip()]
    if not types:
        return None

    TYPE_TR = {
        'article':          'Makale',
        'review':           'Derleme',
        'inproceedings':    'Konferans Bildirisi',
        'conference paper': 'Konferans Bildirisi',
        'book chapter':     'Kitap Bölümü',
        'book':             'Kitap',
        'editorial':        'Editoryal',
        'letter':           'Mektup',
        'note':             'Not',
        'short survey':     'Kısa Derleme',
        'erratum':          'Düzeltme',
        'preprint':         'Ön Baskı',
        'dissertation':     'Tez',
        'dataset':          'Veri Seti',
        'other':            'Diğer',
    }
    translated = [TYPE_TR.get(t, t.title()) for t in types]
    counter = Counter(translated)

    labels = list(counter.keys())
    sizes = list(counter.values())
    # Yeterli farklı renk sağla
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(labels))]

    fig, ax = plt.subplots(figsize=(9, 9))
    ax.set_facecolor('white')
    fig.patch.set_facecolor('white')

    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=None,
        autopct=lambda p: f'{p:.1f}%' if p >= 2 else '',
        colors=colors,
        startangle=140,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2},
        pctdistance=0.78,
    )
    for at in autotexts:
        at.set_color('white')
        at.set_fontsize(10)
        at.set_fontweight('bold')

    ax.legend(
        wedges,
        [f'{l}  ({s})' for l, s in zip(labels, sizes)],
        loc='lower center',
        bbox_to_anchor=(0.5, -0.16),
        ncol=min(3, len(labels)),
        fontsize=10,
        frameon=True,
        framealpha=0.95,
        edgecolor='#cbd5e0',
    )
    ax.set_title('Yayın Türleri Dağılımı')
    fig.tight_layout(pad=2.5)
    return fig


# ─────────────────────────── 9. Atıf Analizi + H-index ───────────────────────────

def citation_analysis(records: list[dict]):
    citations = sorted(
        [r.get('cited_by', 0) for r in records if r.get('cited_by', 0) > 0],
        reverse=True,
    )
    if not citations:
        return None

    h = sum(c >= (i + 1) for i, c in enumerate(citations))
    total_cit = sum(citations)
    mean_cit = total_cit / len(citations) if citations else 0

    max_c = max(citations) or 1
    bar_colors = [plt.cm.Blues(0.3 + 0.6 * c / max_c) for c in citations]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 9))

    # Sol: Sıralı atıf grafiği (Lotka eğrisi)
    ax1.bar(range(1, len(citations) + 1), citations,
            color=bar_colors, alpha=0.9, zorder=2)
    ax1.axvline(x=h, color=TREND_RED, linewidth=2.5, linestyle='--',
                label=f'H-index = {h}', zorder=3)
    ax1.axhline(y=h, color=TREND_AMBER, linewidth=1.5, linestyle=':',
                alpha=0.7, zorder=3)
    ax1.fill_betweenx([0, h], [0, 0], [h, h],
                      alpha=0.07, color=TREND_RED, zorder=1)
    ax1.set_xlabel('Yayın Sırası (atıfa göre)', fontsize=11, labelpad=8)
    ax1.set_ylabel('Atıf Sayısı', fontsize=11, labelpad=8)
    ax1.set_title('Atıf Dağılımı', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(axis='y', zorder=0)

    # Sağ: İstatistik özet tablosu
    stats = [
        ('Toplam Yayın',          f'{len(records):,}'),
        ('Atıflı Yayın',          f'{len(citations):,}'),
        ('H-index',               str(h)),
        ('Toplam Atıf',           f'{total_cit:,}'),
        ('Ort. Atıf / Yayın',     f'{mean_cit:.1f}'),
        ('En Çok Atıf',           f'{citations[0]:,}' if citations else '0'),
        ('Medyan Atıf',           f'{_median(citations):.0f}'),
    ]
    ax2.axis('off')
    tbl = ax2.table(
        cellText=[[k, v] for k, v in stats],
        colLabels=['Metrik', 'Değer'],
        cellLoc='center',
        loc='center',
        colWidths=[0.62, 0.38],
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(11)
    tbl.scale(1.1, 2.2)
    for (row, col), cell in tbl.get_celld().items():
        if row == 0:
            cell.set_facecolor('#1e3a5f')
            cell.set_text_props(color='white', fontweight='bold')
        elif row % 2 == 0:
            cell.set_facecolor('#f1f5f9')
            cell.set_text_props(color='#1e293b')
        else:
            cell.set_facecolor('white')
            cell.set_text_props(color='#1e293b')
        cell.set_edgecolor('#cbd5e0')
    ax2.set_title('Özet İstatistikler', fontsize=13, fontweight='bold', pad=20)

    fig.suptitle('Atıf Analizi ve H-index', fontsize=15, fontweight='bold', y=1.01)
    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 10. Yıllık Atıf Trendi ───────────────────────────

def annual_citation_trend(records: list[dict]):
    year_citations = defaultdict(list)
    for r in records:
        if r.get('year') and 1900 < r['year'] < 2100 and r.get('cited_by', 0) > 0:
            year_citations[r['year']].append(r['cited_by'])

    if not year_citations:
        return None

    sorted_years = sorted(year_citations.keys())
    total_per_year = [sum(year_citations[y]) for y in sorted_years]
    mean_per_year  = [sum(year_citations[y]) / len(year_citations[y]) for y in sorted_years]

    # Çubuk rengi: mavi gradyan (yoğunluğa göre)
    max_t = max(total_per_year) or 1
    bar_colors = [plt.cm.Blues(0.35 + 0.55 * t / max_t) for t in total_per_year]

    fig, ax1 = plt.subplots(figsize=(10, 9))
    ax2 = ax1.twinx()

    ax1.bar(sorted_years, total_per_year, color=bar_colors, alpha=0.85,
            label='Toplam Atıf', width=0.7, zorder=2)
    ax2.plot(sorted_years, mean_per_year,
             color=TREND_RED, linewidth=2.5,
             marker='o', markersize=7, label='Ort. Atıf / Yayın', zorder=3)

    ax1.set_xlabel('Yıl', fontsize=12, labelpad=8)
    ax1.set_ylabel('Toplam Atıf Sayısı', fontsize=12, color='#1e3a5f', labelpad=8)
    ax2.set_ylabel('Ortalama Atıf / Yayın', fontsize=12, color=TREND_RED, labelpad=8)
    ax1.tick_params(axis='y', labelcolor='#1e3a5f')
    ax2.tick_params(axis='y', labelcolor=TREND_RED)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=11)
    ax1.set_title('Yıllık Atıf Trendi')
    ax1.grid(axis='y', zorder=0)

    if len(sorted_years) > 20:
        ax1.tick_params(axis='x', rotation=45)

    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 11. Büyüme Oranı ───────────────────────────

def publication_growth_rate(records: list[dict]):
    years = [r['year'] for r in records if r.get('year') and 1900 < r['year'] < 2100]
    if not years:
        return None

    counter = Counter(years)
    sorted_years = sorted(counter.keys())
    if len(sorted_years) < 3:
        return None

    counts = [counter[y] for y in sorted_years]

    growth_years = sorted_years[1:]
    growth_rates = []
    for i in range(1, len(counts)):
        rate = (counts[i] - counts[i - 1]) / counts[i - 1] * 100 if counts[i - 1] else 0
        growth_rates.append(rate)

    n = sorted_years[-1] - sorted_years[0]
    cagr = ((counts[-1] / counts[0]) ** (1 / n) - 1) * 100 if n > 0 and counts[0] > 0 else 0

    colors = [PALETTE[0] if r >= 0 else PALETTE[2] for r in growth_rates]

    fig, ax = plt.subplots(figsize=(10, 9))
    ax.bar(growth_years, growth_rates, color=colors, alpha=0.85,
           width=0.7, edgecolor='white', zorder=2)
    ax.axhline(0, color='#64748b', linewidth=0.8, zorder=1)
    ax.axhline(cagr, color=TREND_RED, linewidth=2.0, linestyle='--',
               zorder=3, label=f'CAGR = {cagr:+.1f}%')

    ax.set_xlabel('Yıl', fontsize=12, labelpad=8)
    ax.set_ylabel('Yıllık Büyüme Oranı (%)', fontsize=12, labelpad=8)
    ax.set_title('Yıllık Yayın Büyüme Oranı')
    ax.legend(fontsize=11)
    ax.grid(axis='y', zorder=0)

    ax.text(0.98, 0.97,
            f'CAGR ({sorted_years[0]}–{sorted_years[-1]}): {cagr:+.1f}%',
            transform=ax.transAxes, fontsize=11, va='top', ha='right',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#f1f5f9',
                      edgecolor='#cbd5e0', alpha=0.95))

    if len(growth_years) > 20:
        ax.tick_params(axis='x', rotation=45)
    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 12. Lotka Kanunu ───────────────────────────

def lotka_law(records: list[dict]):
    author_count = Counter()
    for r in records:
        for a in r.get('authors', []):
            if a.strip():
                author_count[a.strip()] += 1
    if not author_count:
        return None

    max_k = min(20, max(author_count.values()))
    prod_dist = Counter(author_count.values())
    k_values = list(range(1, max_k + 1))
    observed = [prod_dist.get(k, 0) for k in k_values]
    total_authors = sum(observed)

    lotka_norm = sum(1 / k ** 2 for k in k_values)
    theoretical = [total_authors * (1 / k ** 2) / lotka_norm for k in k_values]

    colors = [PALETTE[i % len(PALETTE)] for i in range(len(k_values))]

    fig, ax = plt.subplots(figsize=(10, 9))
    ax.bar(k_values, observed, color=colors, alpha=0.85,
           label='Gözlemlenen', zorder=2, edgecolor='white')
    ax.plot(k_values, theoretical, color=TREND_RED, linewidth=2.5,
            marker='s', markersize=7, label='Lotka Teorisi (1/k²)', zorder=3)

    ax.set_xlabel('Yayın Sayısı (k)', fontsize=12, labelpad=8)
    ax.set_ylabel('Yazar Sayısı', fontsize=12, labelpad=8)
    ax.set_title('Lotka Kanunu — Yazar Üretkenlik Dağılımı')
    ax.legend(fontsize=11)
    ax.grid(axis='y', zorder=0)
    ax.set_xticks(k_values)

    # Tek yayınlı yazar oranı
    single_pct = prod_dist.get(1, 0) / len(author_count) * 100 if author_count else 0
    ax.text(0.98, 0.97,
            f'Tek yayınlı yazarlar: {single_pct:.1f}%\nToplam yazar: {len(author_count):,}',
            transform=ax.transAxes, fontsize=10, va='top', ha='right',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#f1f5f9',
                      edgecolor='#cbd5e0', alpha=0.95))

    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 13. Anahtar Kelime Eş-Oluşum Ağı ───────────────────────────

def keyword_cooccurrence(records: list[dict], max_kw: int = 40, min_cooccur: int = 2):
    try:
        import networkx as nx
    except ImportError:
        return None

    # Önce en sık geçen anahtar kelimeleri bul
    all_kw = Counter()
    for r in records:
        for k in normalize_keywords(r.get('keywords', [])):
            if len(k) > 2:
                all_kw[k] += 1

    if not all_kw:
        return None

    top_kw_set = {kw for kw, _ in all_kw.most_common(80)}

    cooccur = Counter()
    for r in records:
        kws = list({k for k in normalize_keywords(r.get('keywords', []))
                    if k in top_kw_set})
        if len(kws) < 2:
            continue
        for i in range(len(kws)):
            for j in range(i + 1, len(kws)):
                cooccur[tuple(sorted([kws[i], kws[j]]))] += 1

    G = nx.Graph()
    for (k1, k2), w in cooccur.items():
        if w >= min_cooccur:
            G.add_edge(k1, k2, weight=w)

    if G.number_of_nodes() == 0:
        for (k1, k2), w in cooccur.most_common(60):
            G.add_edge(k1, k2, weight=w)

    if G.number_of_nodes() == 0:
        return None

    if G.number_of_nodes() > max_kw:
        top_nodes = sorted(G.degree, key=lambda x: x[1], reverse=True)[:max_kw]
        G = G.subgraph([n for n, _ in top_nodes]).copy()

    # Community detection (VOSviewer-style cluster renklendirmesi)
    try:
        from networkx.algorithms.community import greedy_modularity_communities
        communities = list(greedy_modularity_communities(G, weight='weight'))
        node_community = {}
        for i, comm in enumerate(communities):
            for node in comm:
                node_community[node] = i
    except Exception:
        node_community = {n: 0 for n in G.nodes()}

    n_clusters = max(node_community.values()) + 1 if node_community else 1
    cluster_colors = PALETTE[:n_clusters] if n_clusters <= len(PALETTE) else PALETTE

    degrees = dict(G.degree())
    node_sizes = [300 + all_kw.get(n, 1) * 60 for n in G.nodes()]
    node_colors = [cluster_colors[node_community.get(n, 0) % len(cluster_colors)]
                   for n in G.nodes()]
    edge_weights = [G[u][v].get('weight', 1) for u, v in G.edges()]

    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_facecolor('#f8fafc')
    fig.patch.set_facecolor('white')

    pos = nx.spring_layout(G, seed=42, k=2.5, weight='weight')

    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.25,
                           width=[min(w * 0.6, 4.0) for w in edge_weights],
                           edge_color='#94a3b8')
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_sizes,
                           node_color=node_colors, alpha=0.88,
                           linewidths=1.2, edgecolors='white')
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=7.5,
                            font_color='#1e293b', font_weight='bold')

    # Cluster legend
    legend_patches = [
        mpatches.Patch(color=cluster_colors[i % len(cluster_colors)],
                       label=f'Küme {i + 1}')
        for i in range(min(n_clusters, 8))
    ]
    ax.legend(handles=legend_patches, loc='lower right', fontsize=8,
              framealpha=0.85, title='Araştırma Kümeleri', title_fontsize=9)

    ax.set_title('Anahtar Kelime Eş-Oluşum Ağı (VOSviewer-style)')
    ax.axis('off')
    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 14. Anahtar Kelime Zaman Trendi ───────────────────────────

def keyword_trend(records: list[dict], top_n: int = 8):
    all_kw = Counter()
    for r in records:
        for k in normalize_keywords(r.get('keywords', [])):
            all_kw[k] += 1

    if not all_kw:
        return None

    top_kws = [kw for kw, _ in all_kw.most_common(top_n)]
    years = sorted({r['year'] for r in records if r.get('year') and 1900 < r['year'] < 2100})

    if len(years) < 3:
        return None

    from collections import defaultdict
    year_kw = defaultdict(lambda: defaultdict(int))
    for r in records:
        if not r.get('year') or not (1900 < r['year'] < 2100):
            continue
        for k in normalize_keywords(r.get('keywords', [])):
            if k in top_kws:
                year_kw[r['year']][k] += 1

    fig, ax = plt.subplots(figsize=(10, 9))
    plotted = 0
    for i, kw in enumerate(top_kws):
        counts = [year_kw[y].get(kw, 0) for y in years]
        if sum(counts) == 0:
            continue
        ax.plot(years, counts, color=PALETTE[i % len(PALETTE)],
                linewidth=2.5, marker='o', markersize=6,
                label=kw.title(), alpha=0.9)
        plotted += 1

    if plotted == 0:
        plt.close(fig)
        return None

    ax.set_xlabel('Yıl', fontsize=12, labelpad=8)
    ax.set_ylabel('Yayın Sayısı', fontsize=12, labelpad=8)
    ax.set_title(f'Anahtar Kelime Zaman Trendi (Top {plotted})')
    ax.legend(bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=9,
              frameon=True, framealpha=0.95, edgecolor='#cbd5e0')
    ax.grid(True, zorder=0)

    if len(years) > 20:
        ax.tick_params(axis='x', rotation=45)

    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 15. Ülke İşbirliği Ağı ───────────────────────────

def country_collaboration(records: list[dict], min_collab: int = 2, max_countries: int = 30):
    try:
        import networkx as nx
    except ImportError:
        return None

    coauth = Counter()
    for r in records:
        raw = r.get('country', '')
        if not raw:
            continue
        countries = list({c.strip() for c in raw.replace(';', ',').split(',') if c.strip()})
        if len(countries) < 2:
            continue
        for i in range(len(countries)):
            for j in range(i + 1, len(countries)):
                coauth[tuple(sorted([countries[i], countries[j]]))] += 1

    G = nx.Graph()
    for (c1, c2), w in coauth.items():
        if w >= min_collab:
            G.add_edge(c1, c2, weight=w)

    if G.number_of_nodes() == 0:
        for (c1, c2), w in coauth.most_common(40):
            G.add_edge(c1, c2, weight=w)

    if G.number_of_nodes() == 0:
        return None

    if G.number_of_nodes() > max_countries:
        top_nodes = sorted(G.degree, key=lambda x: x[1], reverse=True)[:max_countries]
        G = G.subgraph([n for n, _ in top_nodes]).copy()

    degrees = dict(G.degree())
    max_deg = max(degrees.values()) if degrees else 1
    min_deg = min(degrees.values()) if degrees else 0
    span = (max_deg - min_deg) or 1

    node_colors = [plt.cm.cool(0.15 + 0.7 * (degrees[n] - min_deg) / span)
                   for n in G.nodes()]
    node_sizes = [400 + degrees[n] * 150 for n in G.nodes()]
    edge_weights = [G[u][v].get('weight', 1) for u, v in G.edges()]

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_facecolor('#f8fafc')
    fig.patch.set_facecolor('white')

    pos = nx.spring_layout(G, seed=42, k=3.5)

    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.35,
                           width=[min(w * 0.8, 5.0) for w in edge_weights],
                           edge_color='#94a3b8')
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_sizes,
                           node_color=node_colors, alpha=0.9,
                           linewidths=0.8, edgecolors='white')
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=8,
                            font_color='#1e293b', font_weight='bold')

    sm = plt.cm.ScalarMappable(cmap=plt.cm.cool,
                               norm=plt.Normalize(vmin=min_deg, vmax=max_deg))
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label('İşbirliği Sayısı', fontsize=10)

    ax.set_title('Ülke İşbirliği Ağı')
    ax.axis('off')
    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 17. Research Gap ───────────────────────────

def research_gap(records: list[dict], top_n: int = 30, recent_years: int = 3):
    """
    Research Gap Haritası: Keyword bazında Trend × Atıf Etkisi quadrant analizi.
    - X ekseni: Yayın trendi (son N yıl vs önceki dönem, normalize)
    - Y ekseni: Ortalama atıf etkisi (log-scale'den normalize)
    - Sol-üst kadran (düşen trend + yüksek atıf) = Research Gap fırsatı
    """
    import math

    now_year = max((r.get('year') or 0) for r in records if r.get('year'))
    if not now_year:
        return None

    cutoff = now_year - recent_years  # son 3 yıl sınırı

    # Her keyword için: eski/yeni yayın sayısı + toplam atıf
    kw_stats = {}
    for r in records:
        year = r.get('year') or 0
        citations = r.get('cited_by_count') or r.get('cited_by') or 0
        for k in normalize_keywords(r.get('keywords', [])):
            if len(k) < 3:
                continue
            if k not in kw_stats:
                kw_stats[k] = {'old': 0, 'new': 0, 'citations': 0, 'total': 0}
            kw_stats[k]['total'] += 1
            kw_stats[k]['citations'] += citations
            if year > cutoff:
                kw_stats[k]['new'] += 1
            else:
                kw_stats[k]['old'] += 1

    # En az 3 yayında geçen keyword'leri al
    kw_stats = {k: v for k, v in kw_stats.items() if v['total'] >= 3}
    if len(kw_stats) < 5:
        return None

    # Trend skoru: (yeni - eski) / toplam  →  [-1, +1]
    # Atıf etkisi: ortalama atıf (log1p normalize)
    points = []
    for kw, s in kw_stats.items():
        trend = (s['new'] - s['old']) / s['total']
        avg_cite = s['citations'] / s['total']
        points.append({'kw': kw, 'trend': trend, 'impact': avg_cite,
                       'total': s['total']})

    # Top N (toplam yayın sayısına göre)
    points = sorted(points, key=lambda x: x['total'], reverse=True)[:top_n]

    if not points:
        return None

    # Normalize impact için log1p
    max_impact = max(math.log1p(p['impact']) for p in points) or 1
    for p in points:
        p['impact_norm'] = math.log1p(p['impact']) / max_impact

    trends   = [p['trend'] for p in points]
    impacts  = [p['impact_norm'] for p in points]
    labels   = [p['kw'] for p in points]
    sizes    = [80 + p['total'] * 12 for p in points]

    # Medyan kesim noktaları
    med_trend  = sorted(trends)[len(trends) // 2]
    med_impact = sorted(impacts)[len(impacts) // 2]

    # Renk: Research Gap (sol-üst) = kırmızı/turuncu, diğerleri gri tonları
    colors = []
    gap_indices = []
    for i, p in enumerate(points):
        if p['trend'] < med_trend and p['impact_norm'] >= med_impact:
            colors.append('#E15759')   # Research Gap
            gap_indices.append(i)
        elif p['trend'] >= med_trend and p['impact_norm'] >= med_impact:
            colors.append('#4E79A7')   # Altın Alan
        elif p['trend'] >= med_trend and p['impact_norm'] < med_impact:
            colors.append('#76B7B2')   # Yükselen Alan
        else:
            colors.append('#BAB0AC')   # Düşen Alan

    fig, ax = plt.subplots(figsize=(13, 9))
    ax.set_facecolor('#f8fafc')
    fig.patch.set_facecolor('white')

    # Kadrant arkaplan renkleri
    ax.axvspan(min(trends) - 0.05, med_trend, ymin=0.5, ymax=1.0,
               alpha=0.06, color='#E15759')   # Research Gap bölgesi
    ax.axvspan(med_trend, max(trends) + 0.05, ymin=0.5, ymax=1.0,
               alpha=0.06, color='#4E79A7')   # Altın bölge

    # Medyan çizgileri
    ax.axvline(med_trend,  color='#94a3b8', linestyle='--', linewidth=1.2, alpha=0.7)
    ax.axhline(med_impact, color='#94a3b8', linestyle='--', linewidth=1.2, alpha=0.7)

    # Scatter
    sc = ax.scatter(trends, impacts, s=sizes, c=colors, alpha=0.82,
                    edgecolors='white', linewidths=1.0, zorder=3)

    # Etiketler — sadece gap + altın alan (okunabilirlik)
    labeled = set()
    for i, p in enumerate(points):
        if colors[i] in ('#E15759', '#4E79A7') and p['kw'] not in labeled:
            ax.annotate(p['kw'], (p['trend'], p['impact_norm']),
                        fontsize=7.5, ha='center', va='bottom',
                        xytext=(0, 6), textcoords='offset points',
                        color='#1e293b', fontweight='bold')
            labeled.add(p['kw'])

    # Kadrant başlıkları
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    kw_args = dict(fontsize=9, alpha=0.55, fontstyle='italic')
    ax.text(med_trend - (med_trend - xlim[0]) * 0.5, ylim[1] * 0.97,
            '★ RESEARCH GAP', ha='center', color='#E15759', **kw_args)
    ax.text(med_trend + (xlim[1] - med_trend) * 0.5, ylim[1] * 0.97,
            'ALTIN ALAN', ha='center', color='#4E79A7', **kw_args)
    ax.text(med_trend - (med_trend - xlim[0]) * 0.5, med_impact * 0.15,
            'DÜŞEN ALAN', ha='center', color='#BAB0AC', **kw_args)
    ax.text(med_trend + (xlim[1] - med_trend) * 0.5, med_impact * 0.15,
            'YÜKSELİŞTEKİ ALAN', ha='center', color='#76B7B2', **kw_args)

    # Legend
    from matplotlib.lines import Line2D
    legend_items = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#E15759',
               markersize=10, label='Research Gap (fırsat)'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#4E79A7',
               markersize=10, label='Altın Alan (aktif & etkili)'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#76B7B2',
               markersize=10, label='Yükselen Alan'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#BAB0AC',
               markersize=10, label='Düşen Alan'),
    ]
    ax.legend(handles=legend_items, loc='lower right', fontsize=8.5,
              framealpha=0.9, edgecolor='#e2e8f0')

    # Gap keywords listesi (alt açıklama)
    gap_kws = [points[i]['kw'] for i in gap_indices[:6]]
    if gap_kws:
        gap_text = '🎯 Önerilen Araştırma Boşlukları: ' + ' · '.join(gap_kws)
        fig.text(0.5, 0.01, gap_text, ha='center', fontsize=9,
                 color='#E15759', fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.4', fc='#fff5f5', ec='#E15759', alpha=0.8))

    ax.set_xlabel('Yayın Trendi  (← Azalıyor  |  Artıyor →)', fontsize=11)
    ax.set_ylabel('Atıf Etkisi  (↑ Yüksek)', fontsize=11)
    ax.set_title('Araştırma Boşluğu Haritası (Research Gap)', pad=18)
    fig.subplots_adjust(bottom=0.12, top=0.93, left=0.09, right=0.97)
    return fig


# ─────────────────────────── 16. Topic Map ───────────────────────────

def topic_map(records: list[dict], n_topics: int = 8, top_kw_per_topic: int = 8):
    """
    Keyword community detection ile araştırma konusu kümeleri.
    Her küme bir balon, boyutu o kümede kaç yayın var, rengi küme kimliği.
    """
    try:
        import networkx as nx
        from networkx.algorithms.community import greedy_modularity_communities
    except ImportError:
        return None

    # Keyword frekansı ve co-occurrence
    all_kw = Counter()
    for r in records:
        for k in normalize_keywords(r.get('keywords', [])):
            if len(k) > 2:
                all_kw[k] += 1

    if len(all_kw) < 4:
        return None

    top_kw_set = {kw for kw, _ in all_kw.most_common(100)}

    cooccur = Counter()
    for r in records:
        kws = list({k for k in normalize_keywords(r.get('keywords', []))
                    if k in top_kw_set})
        for i in range(len(kws)):
            for j in range(i + 1, len(kws)):
                cooccur[tuple(sorted([kws[i], kws[j]]))] += 1

    G = nx.Graph()
    for (k1, k2), w in cooccur.items():
        if w >= 2:
            G.add_edge(k1, k2, weight=w)

    if G.number_of_nodes() < 4:
        return None

    communities = list(greedy_modularity_communities(G, weight='weight'))
    communities = sorted(communities, key=len, reverse=True)[:n_topics]

    # Her topluluk için: top keyword'ler + kapsanan yayın sayısı
    topic_data = []
    for comm in communities:
        kws_sorted = sorted(comm, key=lambda k: all_kw.get(k, 0), reverse=True)
        label_kws = kws_sorted[:top_kw_per_topic]
        pub_count = sum(all_kw.get(k, 0) for k in kws_sorted[:3])
        topic_data.append({'keywords': label_kws, 'size': pub_count, 'n_kw': len(comm)})

    if not topic_data:
        return None

    # Bubble chart
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_facecolor('#f8fafc')
    fig.patch.set_facecolor('white')

    import math
    cols = min(4, len(topic_data))
    rows = math.ceil(len(topic_data) / cols)

    for idx, topic in enumerate(topic_data):
        col = idx % cols
        row = idx // cols
        x = col * 3.5 + 1.5
        y = (rows - row) * 2.5

        size = 800 + topic['size'] * 15
        color = PALETTE[idx % len(PALETTE)]

        ax.scatter(x, y, s=size, color=color, alpha=0.75, zorder=2,
                   edgecolors='white', linewidths=2)

        label = '\n'.join(topic['keywords'][:5])
        ax.text(x, y, label, ha='center', va='center',
                fontsize=7.5, fontweight='bold', color='white',
                zorder=3, multialignment='center',
                bbox=dict(boxstyle='round,pad=0.1', fc='none', ec='none'))

        ax.text(x, y - 1.1, f'Küme {idx + 1}  ({topic["n_kw"]} kw)',
                ha='center', va='top', fontsize=8.5, color='#475569')

    ax.set_xlim(0, cols * 3.5 + 0.5)
    ax.set_ylim(0, (rows + 0.5) * 2.5)
    ax.axis('off')
    ax.set_title('Araştırma Konusu Kümeleri (Topic Map)', pad=18)
    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── Yardımcılar ───────────────────────────

def _add_bar_labels(ax, bars, fmt='{:.0f}'):
    for bar in bars:
        h = bar.get_height()
        if h > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                h + max(h * 0.01, 0.1),
                fmt.format(h),
                ha='center', va='bottom', fontsize=9,
                color='#334155', fontweight='bold',
            )


def _add_hbar_labels(ax, bars, fmt='{:.0f}'):
    for bar in bars:
        w = bar.get_width()
        if w > 0:
            ax.text(
                w + max(w * 0.01, 0.05),
                bar.get_y() + bar.get_height() / 2,
                fmt.format(w),
                ha='left', va='center', fontsize=9,
                color='#334155', fontweight='bold',
            )


def _median(lst: list) -> float:
    if not lst:
        return 0
    s = sorted(lst)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2


def fig_to_bytes(fig) -> bytes:
    """matplotlib Figure → PNG bytes (beyaz arka plan)"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    buf.seek(0)
    return buf.read()
