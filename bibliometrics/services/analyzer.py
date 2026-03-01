"""
10 Bibliometrik Analiz Modülü
Her fonksiyon (title, matplotlib.figure.Figure) tuple döndürür.
Koyu tema, Türkçe etiketler.
"""
import io
import logging
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)

# ── Matplotlib backend ayarı (sunucu ortamında display yok) ──
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

DARK_BG = '#1a1a2e'
ACCENT   = '#00d2ff'
ACCENT2  = '#a78bfa'
ACCENT3  = '#34d399'
TEXT_CLR = '#e2e8f0'
GRID_CLR = '#2d3748'

plt.rcParams.update({
    'figure.facecolor': DARK_BG,
    'axes.facecolor':   DARK_BG,
    'axes.edgecolor':   GRID_CLR,
    'axes.labelcolor':  TEXT_CLR,
    'xtick.color':      TEXT_CLR,
    'ytick.color':      TEXT_CLR,
    'text.color':       TEXT_CLR,
    'grid.color':       GRID_CLR,
    'grid.linestyle':   '--',
    'grid.alpha':       0.5,
    'font.family':      'DejaVu Sans',
    'font.size':        10,
})


def run_all_analyses(records: list[dict]) -> list[tuple[str, object]]:
    """
    Tüm 10 analizi çalıştırır.
    Returns: [(title, Figure), ...]  — hatalı analizler atlanır
    """
    analyses = [
        ('Yıllara Göre Yayın Trendi',        lambda: publication_trend(records)),
        ('En Verimli Yazarlar (Top 15)',       lambda: top_authors(records)),
        ('Anahtar Kelime Bulutu',              lambda: keyword_cloud(records)),
        ('En Çok Atıf Alan Yayınlar (Top 10)', lambda: top_cited(records)),
        ('En Çok Yayın Yapılan Dergiler',      lambda: top_journals(records)),
        ('Kurum / Ülke Dağılımı (Top 10)',     lambda: top_institutions(records)),
        ('Yazar İşbirliği Ağı',                lambda: author_collaboration(records)),
        ('Yayın Türleri Dağılımı',             lambda: publication_types(records)),
        ('Atıf Analizi ve H-index',            lambda: citation_analysis(records)),
        ('Yıllık Atıf Trendi',                 lambda: annual_citation_trend(records)),
    ]

    results = []
    for title, fn in analyses:
        try:
            fig = fn()
            if fig is not None:
                results.append((title, fig))
        except Exception as e:
            logger.warning(f'Analiz başarısız [{title}]: {e}')
    return results


# ─────────────────────────── 1. Yayın Trendi ───────────────────────────

def publication_trend(records: list[dict]):
    years = [r['year'] for r in records if r.get('year') and 1900 < r['year'] < 2100]
    if not years:
        return None

    counter = Counter(years)
    sorted_years = sorted(counter.keys())
    counts = [counter[y] for y in sorted_years]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(sorted_years, counts, color=ACCENT, alpha=0.8, zorder=2)
    ax.plot(sorted_years, counts, color=ACCENT2, linewidth=2, marker='o',
            markersize=5, zorder=3, label='Trend')

    ax.set_xlabel('Yıl')
    ax.set_ylabel('Yayın Sayısı')
    ax.set_title('Yıllara Göre Yayın Trendi', fontsize=14, fontweight='bold', pad=15)
    ax.grid(axis='y', zorder=1)
    ax.legend()
    _add_bar_labels(ax, bars)
    fig.tight_layout()
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

    fig, ax = plt.subplots(figsize=(10, max(5, n * 0.45)))
    y_pos = range(len(names))
    bars = ax.barh(y_pos, counts, color=ACCENT2, alpha=0.85)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel('Yayın Sayısı')
    ax.set_title(f'En Verimli Yazarlar (Top {len(names)})', fontsize=14, fontweight='bold', pad=15)
    ax.grid(axis='x')
    _add_hbar_labels(ax, bars)
    fig.tight_layout()
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
        all_kw.extend(r.get('keywords', []))
        # Abstract'tan da kelime çek (ilk 5 kelime hariç, stop-word benzeri)
        words = r.get('abstract', '').split()
        all_kw.extend([w.lower() for w in words if len(w) > 5])

    if not all_kw:
        return None

    text = ' '.join(all_kw)
    wc = WordCloud(
        width=900, height=500,
        background_color=DARK_BG,
        colormap='cool',
        max_words=150,
        prefer_horizontal=0.8,
    ).generate(text)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    ax.set_title('Anahtar Kelime Bulutu', fontsize=14, fontweight='bold', pad=15)
    fig.tight_layout()
    return fig


# ─────────────────────────── 4. En Çok Atıf Alan ───────────────────────────

def top_cited(records: list[dict], n: int = 10):
    with_citations = [(r['title'], r['cited_by']) for r in records if r.get('cited_by', 0) > 0]
    if not with_citations:
        return None

    top = sorted(with_citations, key=lambda x: x[1], reverse=True)[:n]
    titles, counts = zip(*top)
    short_titles = [t[:60] + '…' if len(t) > 60 else t for t in titles]

    fig, ax = plt.subplots(figsize=(11, max(5, n * 0.55)))
    y_pos = range(len(short_titles))
    bars = ax.barh(y_pos, counts, color=ACCENT3, alpha=0.85)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(short_titles, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel('Atıf Sayısı')
    ax.set_title(f'En Çok Atıf Alan Yayınlar (Top {len(top)})', fontsize=14, fontweight='bold', pad=15)
    ax.grid(axis='x')
    _add_hbar_labels(ax, bars)
    fig.tight_layout()
    return fig


# ─────────────────────────── 5. En Çok Yayın Yapılan Dergiler ───────────────────────────

def top_journals(records: list[dict], n: int = 10):
    journals = [r['journal'].strip() for r in records if r.get('journal', '').strip()]
    if not journals:
        return None

    counter = Counter(journals)
    top = counter.most_common(n)
    names, counts = zip(*top)
    short_names = [n[:55] + '…' if len(n) > 55 else n for n in names]

    fig, ax = plt.subplots(figsize=(11, max(5, n * 0.5)))
    y_pos = range(len(short_names))
    bars = ax.barh(y_pos, counts, color=ACCENT, alpha=0.85)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(short_names, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel('Yayın Sayısı')
    ax.set_title(f'En Çok Yayın Yapılan Dergiler / Kaynaklar (Top {len(top)})', fontsize=14, fontweight='bold', pad=15)
    ax.grid(axis='x')
    _add_hbar_labels(ax, bars)
    fig.tight_layout()
    return fig


# ─────────────────────────── 6. Kurum / Ülke Dağılımı ───────────────────────────

def top_institutions(records: list[dict], n: int = 10):
    # Önce ülke dene, yoksa kurum
    country_counter = Counter()
    inst_counter = Counter()
    for r in records:
        if r.get('country'):
            country_counter[r['country'].strip()] += 1
        if r.get('institution'):
            # İlk kurumu al (noktalı virgülle ayrılmış olabilir)
            inst = r['institution'].split(';')[0].strip()
            if inst:
                inst_counter[inst] += 1

    if country_counter:
        top = country_counter.most_common(n)
        label = 'Ülke'
        title_str = f'Ülkelere Göre Yayın Dağılımı (Top {min(n, len(top))})'
    elif inst_counter:
        top = inst_counter.most_common(n)
        label = 'Kurum'
        title_str = f'Kurumlara Göre Yayın Dağılımı (Top {min(n, len(top))})'
    else:
        return None

    names, counts = zip(*top)
    short_names = [nm[:55] + '…' if len(nm) > 55 else nm for nm in names]

    fig, ax = plt.subplots(figsize=(11, max(5, len(top) * 0.5)))
    y_pos = range(len(short_names))
    bars = ax.barh(y_pos, counts, color=ACCENT2, alpha=0.85)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(short_names, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel('Yayın Sayısı')
    ax.set_title(title_str, fontsize=14, fontweight='bold', pad=15)
    ax.grid(axis='x')
    _add_hbar_labels(ax, bars)
    fig.tight_layout()
    return fig


# ─────────────────────────── 7. Yazar İşbirliği Ağı ───────────────────────────

def author_collaboration(records: list[dict], max_authors: int = 30, min_collab: int = 2):
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

    # Yalnızca min_collab ve üzeri işbirliklerini ekle
    for (a1, a2), weight in coauth_count.items():
        if weight >= min_collab:
            G.add_edge(a1, a2, weight=weight)

    if G.number_of_nodes() == 0:
        # min_collab karşılanmıyorsa tüm kenarları ekle
        for (a1, a2), weight in coauth_count.most_common(50):
            G.add_edge(a1, a2, weight=weight)

    if G.number_of_nodes() == 0:
        return None

    # En bağlantılı max_authors düğümü tut
    if G.number_of_nodes() > max_authors:
        top_nodes = sorted(G.degree, key=lambda x: x[1], reverse=True)[:max_authors]
        top_node_names = [n for n, _ in top_nodes]
        G = G.subgraph(top_node_names).copy()

    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_facecolor(DARK_BG)

    pos = nx.spring_layout(G, seed=42, k=2.5)
    degrees = dict(G.degree())
    node_sizes = [300 + degrees[n] * 100 for n in G.nodes()]
    edge_weights = [G[u][v].get('weight', 1) for u, v in G.edges()]

    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.4, width=[w * 0.8 for w in edge_weights],
                           edge_color=GRID_CLR)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_sizes,
                           node_color=ACCENT, alpha=0.9)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=7,
                            font_color=TEXT_CLR, font_weight='bold')

    ax.set_title('Yazar İşbirliği Ağı', fontsize=14, fontweight='bold', pad=15)
    ax.axis('off')
    fig.tight_layout()
    return fig


# ─────────────────────────── 8. Yayın Türleri ───────────────────────────

def publication_types(records: list[dict]):
    types = [r.get('pub_type', '').strip().lower() for r in records if r.get('pub_type', '').strip()]
    if not types:
        return None

    TYPE_TR = {
        'article': 'Makale',
        'review': 'Derleme',
        'inproceedings': 'Konferans Bildirisi',
        'conference paper': 'Konferans Bildirisi',
        'book chapter': 'Kitap Bölümü',
        'book': 'Kitap',
        'editorial': 'Editoryal',
        'letter': 'Mektup',
        'note': 'Not',
        'short survey': 'Kısa Derleme',
        'erratum': 'Düzeltme',
    }
    translated = [TYPE_TR.get(t, t.title()) for t in types]
    counter = Counter(translated)

    labels = list(counter.keys())
    sizes = list(counter.values())
    colors = plt.cm.Set2.colors[:len(labels)]

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=None, autopct='%1.1f%%',
        colors=colors, startangle=140,
        wedgeprops={'edgecolor': DARK_BG, 'linewidth': 2},
        pctdistance=0.8,
    )
    for at in autotexts:
        at.set_color(DARK_BG)
        at.set_fontsize(9)
        at.set_fontweight('bold')

    ax.legend(wedges, [f'{l} ({s})' for l, s in zip(labels, sizes)],
              loc='lower center', bbox_to_anchor=(0.5, -0.15),
              ncol=2, fontsize=9, framealpha=0.3)
    ax.set_title('Yayın Türleri Dağılımı', fontsize=14, fontweight='bold', pad=15)
    fig.tight_layout()
    return fig


# ─────────────────────────── 9. Atıf Analizi + H-index ───────────────────────────

def citation_analysis(records: list[dict]):
    citations = sorted(
        [r.get('cited_by', 0) for r in records if r.get('cited_by', 0) > 0],
        reverse=True,
    )
    if not citations:
        return None

    # H-index hesapla
    h = sum(c >= (i + 1) for i, c in enumerate(citations))
    total_cit = sum(citations)
    mean_cit = total_cit / len(citations)

    # Atıf dağılımı histogram
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # Sol: Sıralı atıf grafiği (Lotka eğrisi)
    ax1.bar(range(1, len(citations) + 1), citations, color=ACCENT, alpha=0.75)
    ax1.axvline(x=h, color=ACCENT2, linewidth=2, linestyle='--', label=f'H-index = {h}')
    ax1.set_xlabel('Yayın Sırası (atıfa göre)')
    ax1.set_ylabel('Atıf Sayısı')
    ax1.set_title('Atıf Dağılımı (Azalan Sıra)', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(axis='y')

    # Sağ: İstatistik özet kutusu
    stats = {
        'Toplam Yayın': len(records),
        'Atıflı Yayın': len(citations),
        f'H-index': h,
        'Toplam Atıf': total_cit,
        'Ort. Atıf / Yayın': f'{mean_cit:.1f}',
        'En Çok Atıf': citations[0] if citations else 0,
        'Orta Değer (Medyan)': _median(citations),
    }

    ax2.axis('off')
    table_data = [[k, str(v)] for k, v in stats.items()]
    tbl = ax2.table(
        cellText=table_data,
        colLabels=['Metrik', 'Değer'],
        cellLoc='center', loc='center',
        colWidths=[0.6, 0.4],
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(11)
    tbl.scale(1.2, 2.0)
    for (row, col), cell in tbl.get_celld().items():
        cell.set_facecolor(DARK_BG if row > 0 else '#16213e')
        cell.set_edgecolor(GRID_CLR)
        cell.set_text_props(color=TEXT_CLR if row > 0 else ACCENT)
    ax2.set_title('Özet İstatistikler', fontsize=12, fontweight='bold', pad=20)

    fig.suptitle('Atıf Analizi ve H-index', fontsize=14, fontweight='bold', y=1.01)
    fig.tight_layout()
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
    mean_per_year = [sum(year_citations[y]) / len(year_citations[y]) for y in sorted_years]

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()

    ax1.bar(sorted_years, total_per_year, color=ACCENT, alpha=0.6, label='Toplam Atıf')
    ax2.plot(sorted_years, mean_per_year, color=ACCENT2, linewidth=2.5,
             marker='o', markersize=6, label='Ort. Atıf / Yayın')

    ax1.set_xlabel('Yıl')
    ax1.set_ylabel('Toplam Atıf Sayısı', color=ACCENT)
    ax2.set_ylabel('Ortalama Atıf / Yayın', color=ACCENT2)
    ax1.tick_params(axis='y', labelcolor=ACCENT)
    ax2.tick_params(axis='y', labelcolor=ACCENT2)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    ax1.set_title('Yıllık Atıf Trendi', fontsize=14, fontweight='bold', pad=15)
    ax1.grid(axis='y')
    fig.tight_layout()
    return fig


# ─────────────────────────── Yardımcılar ───────────────────────────

def _add_bar_labels(ax, bars):
    for bar in bars:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.1,
                    str(int(h)), ha='center', va='bottom', fontsize=8, color=TEXT_CLR)


def _add_hbar_labels(ax, bars):
    for bar in bars:
        w = bar.get_width()
        if w > 0:
            ax.text(w + 0.05, bar.get_y() + bar.get_height() / 2,
                    str(int(w)), ha='left', va='center', fontsize=8, color=TEXT_CLR)


def _median(lst: list) -> float:
    if not lst:
        return 0
    s = sorted(lst)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2


def fig_to_bytes(fig) -> bytes:
    """matplotlib Figure → PNG bytes"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                facecolor=DARK_BG)
    plt.close(fig)
    buf.seek(0)
    return buf.read()
