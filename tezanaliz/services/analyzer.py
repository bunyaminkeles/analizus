"""
Tez & Makale Analiz Modülü — 7 analiz
Beyaz/açık tema, profesyonel grafikler.
Her fonksiyon (title, matplotlib.figure.Figure) tuple döndürür.
"""
import logging
import re
from collections import Counter, defaultdict
from datetime import date

logger = logging.getLogger(__name__)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
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
    'axes.titlesize':       14,
    'axes.titleweight':     'bold',
    'axes.titlepad':        16,
    'axes.labelsize':       11,
    'axes.spines.top':      False,
    'axes.spines.right':    False,
    'figure.dpi':           100,
})

PALETTE = [
    '#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F',
    '#EDC948', '#B07AA1', '#FF9DA7', '#9C755F', '#BAB0AC',
]

# İngilizce stopwords (sklearn'deki ile uyumlu genişletilmiş set)
EN_STOPWORDS = {
    'the', 'of', 'and', 'in', 'a', 'an', 'to', 'is', 'are', 'was', 'were',
    'that', 'for', 'on', 'with', 'as', 'by', 'at', 'from', 'this', 'it',
    'be', 'have', 'has', 'been', 'or', 'not', 'but', 'which', 'their',
    'they', 'we', 'he', 'she', 'you', 'i', 'its', 'our', 'also', 'can',
    'will', 'may', 'than', 'these', 'those', 'such', 'more', 'between',
    'into', 'about', 'two', 'three', 'one', 'used', 'using', 'use',
    'based', 'result', 'results', 'study', 'paper', 'research', 'method',
    'approach', 'proposed', 'show', 'shown', 'found', 'well', 'both',
    'new', 'different', 'each', 'thus', 'where', 'while', 'however',
    'therefore', 'although', 'due', 'all', 'most', 'high', 'low',
    'order', 'number', 'significantly', 'significant',
}

# ─── Lemmatizer (NLTK, lazy init) ────────────────────────────────────────────

_lemmatizer = None
_lemmatizer_ready = False


def _get_lemmatizer():
    global _lemmatizer, _lemmatizer_ready
    if _lemmatizer_ready:
        return _lemmatizer
    try:
        import nltk
        from nltk.stem import WordNetLemmatizer
        try:
            from nltk.corpus import wordnet as _wn
            _wn.ensure_loaded()
        except LookupError:
            nltk.download('wordnet', quiet=True)
            nltk.download('omw-1.4', quiet=True)
        _lemmatizer = WordNetLemmatizer()
        logger.info('[tezanaliz] NLTK WordNetLemmatizer yüklendi.')
    except Exception as e:
        logger.warning(f'[tezanaliz] NLTK lemmatizer yüklenemedi, lemmatization atlanıyor: {e}')
        _lemmatizer = None
    _lemmatizer_ready = True
    return _lemmatizer


def _lemmatize_text(text: str) -> str:
    """İngilizce metni lemmatize et. NLTK yoksa orijinal metni döndür."""
    if not text:
        return text
    lem = _get_lemmatizer()
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    if lem is None:
        return ' '.join(words)
    return ' '.join(lem.lemmatize(w) for w in words)


def _get_english_text(rec: dict) -> str:
    """
    Record'dan İngilizce analiz metni oluştur.
    abstract_en varsa kullan, yoksa abstract_tr'yi fallback yap.
    """
    title = rec.get('title', '')
    abstract_en = rec.get('abstract_en', '')
    abstract_tr = rec.get('abstract_tr', '')
    # İngilizce özet tercih et, yoksa Türkçe'ye düş
    abstract = abstract_en or abstract_tr
    return ' '.join(p for p in [title, abstract] if p)


def _safe_year(rec) -> int | None:
    try:
        y = int(str(rec.get('year', '') or '').strip())
        if 1950 <= y <= date.today().year + 1:
            return y
    except (ValueError, TypeError):
        pass
    return None


def _normalize_type(raw: str) -> str:
    r = (raw or '').strip().lower()
    if 'doktora' in r or 'doctorate' in r or 'phd' in r:
        return 'Doktora'
    if 'tıpta' in r or 'tipta' in r or 'uzmanl' in r or 'medicine' in r:
        return 'Tıpta Uzmanlık'
    if 'yüksek' in r or 'yuksek' in r or 'master' in r or 'msc' in r:
        return 'Yüksek Lisans'
    if r:
        return raw.strip()
    return 'Diğer'


# ─── 1. Tez Türü Pasta Grafik ────────────────────────────────────────────────

def thesis_type_chart(records: list[dict]) -> tuple[str, plt.Figure] | None:
    counts = Counter(_normalize_type(r.get('thesis_type', '')) for r in records)
    counts.pop('Diğer', None)
    if not counts:
        return None

    fig, ax = plt.subplots(figsize=(7, 5))
    labels = list(counts.keys())
    values = list(counts.values())
    colors = PALETTE[:len(labels)]
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, colors=colors,
        autopct='%1.1f%%', startangle=90,
        wedgeprops={'linewidth': 1.5, 'edgecolor': 'white'},
    )
    for at in autotexts:
        at.set_fontsize(10)
    ax.set_title('Tez Türlerine Göre Dağılım')
    fig.tight_layout()
    return ('Tez Türleri Dağılımı', fig)


# ─── 2. Yıl × Tez Türü Stacked Bar ──────────────────────────────────────────

def type_year_trend(records: list[dict]) -> tuple[str, plt.Figure] | None:
    type_year: dict[str, Counter] = defaultdict(Counter)
    for r in records:
        y = _safe_year(r)
        t = _normalize_type(r.get('thesis_type', ''))
        if y and t != 'Diğer':
            type_year[t][y] += 1

    if not type_year:
        return None

    all_years = sorted({y for c in type_year.values() for y in c})
    if len(all_years) < 2:
        return None

    types = list(type_year.keys())
    data = {t: [type_year[t].get(y, 0) for y in all_years] for t in types}

    fig, ax = plt.subplots(figsize=(10, 5))
    bottoms = [0] * len(all_years)
    for i, t in enumerate(types):
        vals = data[t]
        ax.bar(all_years, vals, bottom=bottoms, label=t, color=PALETTE[i], width=0.7)
        bottoms = [b + v for b, v in zip(bottoms, vals)]

    ax.set_title('Yıllara Göre Tez Türü Trendi')
    ax.set_xlabel('Yıl')
    ax.set_ylabel('Tez Sayısı')
    ax.legend(loc='upper left', fontsize=9)
    ax.set_xticks(all_years)
    ax.tick_params(axis='x', rotation=45)
    ax.yaxis.grid(True)
    fig.tight_layout()
    return ('Yıl × Tez Türü Trendi', fig)


# ─── 3. Üniversite Üretkenliği ────────────────────────────────────────────────

def university_productivity(records: list[dict]) -> tuple[str, plt.Figure] | None:
    counts = Counter(
        (r.get('university') or '').strip()
        for r in records
        if (r.get('university') or '').strip()
    )
    if not counts:
        return None

    top = counts.most_common(15)
    labels = [u for u, _ in top]
    values = [c for _, c in top]

    # Uzun isimleri kısalt
    labels = [l if len(l) <= 35 else l[:33] + '…' for l in labels]

    fig, ax = plt.subplots(figsize=(9, max(5, len(labels) * 0.45)))
    bars = ax.barh(labels[::-1], values[::-1], color=PALETTE[0])
    ax.bar_label(bars, padding=3, fontsize=9)
    ax.set_title('Üniversite Bazında Tez Üretkenliği (Top 15)')
    ax.set_xlabel('Tez Sayısı')
    ax.xaxis.grid(True)
    fig.tight_layout()
    return ('Üniversite Üretkenliği', fig)


# ─── 4. TF-IDF Anahtar Kelime Bar ────────────────────────────────────────────

def keyword_tfidf_chart(records: list[dict]) -> tuple[str, plt.Figure] | None:
    texts = [_lemmatize_text(_get_english_text(r)) for r in records]
    texts = [t for t in texts if len(t) > 20]

    if len(texts) < 3:
        return None

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        min_df_val = 1 if len(texts) < 10 else 2
        vec = TfidfVectorizer(
            max_features=500,
            stop_words=list(EN_STOPWORDS),
            min_df=min_df_val,
            ngram_range=(1, 2),
            token_pattern=r'\b[a-zA-Z]{3,}\b',
        )
        X = vec.fit_transform(texts)
        scores = X.mean(axis=0).A1
        feature_names = vec.get_feature_names_out()
        top_idx = scores.argsort()[-20:][::-1]
        top_words = [feature_names[i] for i in top_idx]
        top_scores = [scores[i] for i in top_idx]
    except Exception as e:
        logger.warning(f'[tezanaliz] TF-IDF hatası: {e}')
        return None

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(top_words[::-1], top_scores[::-1], color=PALETTE[1])
    ax.set_title('TF-IDF Anahtar Kelimeler (İngilizce, Lemmatized)')
    ax.set_xlabel('TF-IDF Skoru')
    ax.xaxis.grid(True)
    fig.tight_layout()
    return ('TF-IDF Anahtar Kelimeler', fig)


# ─── 5. Son 5 Yıl Trend + Büyüme Oranı ──────────────────────────────────────

def trend_5year(records: list[dict]) -> tuple[str, plt.Figure] | None:
    current_year = date.today().year
    start_year = current_year - 5

    year_counts: Counter = Counter()
    for r in records:
        y = _safe_year(r)
        if y and y >= start_year:
            year_counts[y] += 1

    if len(year_counts) < 2:
        return None

    years = sorted(year_counts.keys())
    counts = [year_counts[y] for y in years]

    # Büyüme oranı (ilk yıl → son yıl)
    growth_pct = None
    if counts[0] > 0:
        growth_pct = ((counts[-1] - counts[0]) / counts[0]) * 100

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(years, counts, marker='o', color=PALETTE[0], linewidth=2.5, markersize=8)
    ax.fill_between(years, counts, alpha=0.15, color=PALETTE[0])

    # Büyüme annotation
    if growth_pct is not None:
        direction = '▲' if growth_pct >= 0 else '▼'
        color = '#059669' if growth_pct >= 0 else '#DC2626'
        ax.annotate(
            f'{direction} {abs(growth_pct):.1f}% büyüme\n({years[0]}→{years[-1]})',
            xy=(years[-1], counts[-1]),
            xytext=(-80, 15),
            textcoords='offset points',
            fontsize=10,
            color=color,
            fontweight='bold',
        )

    ax.set_title(f'Son 5 Yıl Tez Trendi ({start_year}–{current_year})')
    ax.set_xlabel('Yıl')
    ax.set_ylabel('Tez Sayısı')
    ax.set_xticks(years)
    ax.yaxis.grid(True)
    fig.tight_layout()
    return ('Son 5 Yıl Trendi', fig)


# ─── 6. LDA Konu Modelleme ────────────────────────────────────────────────────

def lda_topics_chart(records: list[dict]) -> tuple[str, plt.Figure] | None:
    texts = []
    for r in records:
        t = _lemmatize_text(_get_english_text(r))
        if len(t) > 50:
            texts.append(t)

    if len(texts) < 5:
        logger.info('[tezanaliz] LDA için yeterli metin yok, atlanıyor.')
        return None

    try:
        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.decomposition import LatentDirichletAllocation

        n_topics = min(5, max(2, len(texts) // 5))
        min_df_val = 1 if len(texts) < 10 else 2

        vec = CountVectorizer(
            max_features=300,
            stop_words=list(EN_STOPWORDS),
            min_df=min_df_val,
            token_pattern=r'\b[a-zA-Z]{4,}\b',
        )
        dtm = vec.fit_transform(texts)
        feature_names = vec.get_feature_names_out()

        lda = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42,
            max_iter=20,
        )
        lda.fit(dtm)
    except Exception as e:
        logger.warning(f'[tezanaliz] LDA hatası: {e}')
        return None

    n_top_words = 8
    topic_labels = []
    topic_words_list = []
    topic_scores_list = []

    for topic_idx, topic in enumerate(lda.components_):
        top_idx = topic.argsort()[:-n_top_words - 1:-1]
        words = [feature_names[i] for i in top_idx]
        scores = topic[top_idx]
        scores = scores / scores.sum()  # normalize
        topic_labels.append(f'Konu {topic_idx + 1}')
        topic_words_list.append(words)
        topic_scores_list.append(scores)

    # Yatay grouped bar grafik
    fig, axes = plt.subplots(1, n_topics, figsize=(4 * n_topics, 5), sharey=False)
    if n_topics == 1:
        axes = [axes]

    for i, (ax, label, words, scores) in enumerate(
        zip(axes, topic_labels, topic_words_list, topic_scores_list)
    ):
        color = PALETTE[i % len(PALETTE)]
        ax.barh(words[::-1], scores[::-1], color=color)
        ax.set_title(label, fontsize=11, fontweight='bold')
        ax.set_xlabel('Ağırlık')
        ax.tick_params(axis='y', labelsize=9)
        ax.xaxis.grid(True)

    fig.suptitle('LDA Konu Modelleme — Gizli Konular', fontsize=13, fontweight='bold', y=1.02)
    fig.tight_layout()
    return ('LDA Konu Modelleme', fig)


# ─── 7. İngilizce Kelime Bulutu ───────────────────────────────────────────────

def subject_wordcloud(records: list[dict]) -> tuple[str, plt.Figure] | None:
    """
    İngilizce abstract + title kelimelerinden kelime bulutu.
    Lemmatize edilmiş kelimeler, stopword filtreli.
    """
    word_freq: Counter = Counter()

    for r in records:
        text = _lemmatize_text(_get_english_text(r))
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text)
        for w in words:
            if w not in EN_STOPWORDS:
                word_freq[w] += 1

    if len(word_freq) < 5:
        logger.info('[tezanaliz] Yeterli İngilizce kelime yok, wordcloud atlanıyor.')
        return None

    try:
        from wordcloud import WordCloud
        wc = WordCloud(
            width=900,
            height=500,
            background_color='white',
            colormap='tab10',
            max_words=80,
            prefer_horizontal=0.8,
        ).generate_from_frequencies(word_freq)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('Anahtar Kelime Bulutu (İngilizce, Lemmatized)')
        fig.tight_layout()
        return ('Anahtar Kelime Bulutu', fig)
    except Exception as e:
        logger.warning(f'[tezanaliz] Wordcloud hatası: {e}')
        return None


# ─── Benzer Tezler (web display, PDF'e girmez) ───────────────────────────────

def compute_similar_theses(records: list[dict], query_text: str, top_n: int = 10) -> list[dict]:
    """
    Arama sorgusuna en benzer N tezi döndürür.
    TF-IDF cosine similarity kullanır.
    """
    if not query_text or len(records) < 3:
        return []

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        corpus = [_lemmatize_text(_get_english_text(r)) for r in records]
        all_texts = corpus + [_lemmatize_text(query_text)]
        vec = TfidfVectorizer(
            stop_words=list(EN_STOPWORDS),
            token_pattern=r'\b[a-zA-Z]{3,}\b',
        )
        X = vec.fit_transform(all_texts)
        query_vec = X[-1]
        corpus_vecs = X[:-1]

        sims = cosine_similarity(query_vec, corpus_vecs).flatten()
        top_idx = sims.argsort()[-top_n:][::-1]

        result = []
        for idx in top_idx:
            if sims[idx] < 0.01:
                continue
            r = records[idx]
            result.append({
                'title': r.get('title') or r.get('title_tr', ''),
                'title_tr': r.get('title_tr', ''),
                'author': r.get('author', ''),
                'year': r.get('year', ''),
                'university': r.get('university', ''),
                'thesis_type': _normalize_type(r.get('thesis_type', '')),
                'tez_no': r.get('tez_no', ''),
                'similarity': round(float(sims[idx]), 3),
            })
        return result
    except Exception as e:
        logger.warning(f'[tezanaliz] Benzer tez hesaplama hatası: {e}')
        return []


# ─── Ana çalıştırıcı ─────────────────────────────────────────────────────────

def run_all_analyses(records: list[dict]) -> list[tuple[str, plt.Figure]]:
    """
    7 analizi çalıştırır, geçerli (None olmayan) sonuçları döndürür.
    """
    funcs = [
        thesis_type_chart,
        type_year_trend,
        university_productivity,
        keyword_tfidf_chart,
        trend_5year,
        lda_topics_chart,
        subject_wordcloud,
    ]

    figures = []
    for fn in funcs:
        try:
            result = fn(records)
            if result is not None:
                figures.append(result)
        except Exception as e:
            logger.error(f'[tezanaliz] {fn.__name__} hatası: {e}', exc_info=True)

    return figures
