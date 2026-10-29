"""
10 Bibliometrik Analiz Modülü
Beyaz/açık tema, çok renkli grafikler, profesyonel görünüm.
Her fonksiyon (title, matplotlib.figure.Figure) tuple döndürür.
"""
import io
import re
import logging
import unicodedata
from django.utils.translation import gettext
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

def _simple_depluralize(word: str) -> str:
    """Zeyrek'in tanıyamadığı (muhtemelen yabancı dil, ör. İngilizce) tek kelimeler için
    basit çoğul→tekil kuralı (B1-4) — kusursuz değil, pragmatik bir sezgisel kural
    (anahtar kelime normalizasyonunun geri kalanıyla aynı düzey)."""
    if len(word) > 4 and word.endswith('ies'):
        return word[:-3] + 'y'
    if len(word) > 4 and word.endswith(('ses', 'xes', 'zes', 'ches', 'shes')):
        return word[:-2]
    if len(word) > 3 and word.endswith('s') and not word.endswith('ss'):
        return word[:-1]
    return word


def normalize_keywords(keywords: list[str]) -> list[str]:
    """
    Keyword listesini normalize eder:
    - Küçük harf, tire/boşluk farkını yok say (B1-4: "COVID-19" ~ "COVID 19")
    - Stopword filtrele
    - Tek kelime ise Türkçe lemmatize et; başarısızsa basit çoğul→tekil kuralı dene (B1-4)
    - Çok kelimeli ifadeleri olduğu gibi bırak (makine öğrenmesi vb.)
    """
    stopwords = _get_tr_stopwords()
    result = []
    for kw in keywords:
        kw = kw.strip().lower().replace('-', ' ')
        kw = re.sub(r'\s+', ' ', kw).strip()
        if not kw or len(kw) < 2:
            continue
        if kw in stopwords:
            continue
        # Çok kelimeli → olduğu gibi bırak
        if ' ' in kw:
            result.append(kw)
        else:
            lemma = lemmatize_word(kw)
            if lemma == kw:
                lemma = _simple_depluralize(kw)
            result.append(lemma)
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

def _strip_accents(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))


def canonical_author_key(name: str) -> str:
    """Yazar adı varyantlarını ('Smith, J.' / 'John Smith' / 'JOHN SMITH') tek anahtar
    altında birleştirir: soyad + ilk adın baş harfi, aksan ve büyük/küçük harf yok
    sayılır (B1-2 tekilleştirmedeki normalizasyonla aynı pragmatik düzey — mükemmel
    değil, ör. çok parçalı soyadlarda yalnız son kelime soyad sayılır). OpenAlex
    author ID'si henüz kullanılmıyor: CSV/BibTeX yazar listesiyle OpenAlex authorship
    listesi arasında konumsal eşleme güvenilir değil, isim benzerliğiyle eşleme
    gerekir — Faz B2'de (eş-atıf ağları, yazar ID ile homonym çözümü) ele alınacak.
    """
    name = _strip_accents(name).lower().strip()
    name = re.sub(r'[.·]', '', name)
    if ',' in name:
        last, _, rest = name.partition(',')
        first_initial = next((c for c in rest.strip() if c.isalpha()), '')
    else:
        parts = [p for p in re.split(r'\s+', name) if p]
        if not parts:
            return ''
        last = parts[-1]
        first_initial = parts[0][0] if parts[0][:1].isalpha() else ''
    last = re.sub(r'[^a-z\s-]', '', last).strip()
    if not last:
        return ''
    return f'{last} {first_initial}'.strip()


def _group_authors(records: list[dict]):
    """Her kayıttaki yazar adlarını kanonik anahtara göre gruplar.
    Döner: (counts: {key: yayın sayısı}, display: {key: gösterilecek en uzun ad varyantı})."""
    counts = Counter()
    display = {}
    for r in records:
        for a in r.get('authors', []):
            a = a.strip()
            if not a:
                continue
            key = canonical_author_key(a)
            if not key:
                continue
            counts[key] += 1
            if key not in display or len(a) > len(display[key]):
                display[key] = a
    return counts, display


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


def run_all_analyses(records: list[dict], skipped: list = None, time_series: list = None,
                     has_citations: bool = True) -> list[tuple[str, bytes]]:
    """
    Tüm analizleri çalıştırır.
    Her figür üretilir üretilmez PNG bytes'a çevrilip kapatılır —
    tüm Figure nesnelerini aynı anda bellekte tutmak yerine sadece
    hafif PNG bytes listesi saklanır.
    skipped: verilirse üretilemeyen analizler (başlık, neden) olarak eklenir — rapor kısıtları için.
    time_series: verilirse zaman serisi grafiklerinin sonuç listesindeki sırası eklenir — PDF'te
    veri kesildiğinde (OpenAlex sınırı) bu sayfalara uyarı yazmak için.
    has_citations: False → kaynak atıf sayısı vermiyor (PubMed); atıfa dayanan analizler (Araştırma
    Boşluğu'nun dikey ekseni de ortalama atıf) çalıştırılmaz, nedeni kaynağa göre yazılır.
    """
    import gc as _gc
    no_year     = gettext('Tamamlanmış yıllara ait yayın yılı bilgisi yok.')
    no_author   = gettext('Yazar bilgisi yok.')
    no_citation = gettext('Atıf almış yayın yok.')
    # (başlık, fonksiyon, üretilemezse neden[, True = zaman serisi]) — neden fonksiyonun None döndürdüğü koşulu anlatır
    analyses = [
        (gettext('Yıllara Göre Yayın Trendi'),              lambda: publication_trend(records), no_year, True),
        (gettext('Yıllık Büyüme Oranı'),                    lambda: publication_growth_rate(records),
         gettext('En az 3 farklı yayın yılı gerekir.'), True),
        (gettext('En Verimli Yazarlar (Top 15)'),            lambda: top_authors(records), no_author),
        (gettext('Lotka Kanunu — Yazar Üretkenliği'),        lambda: lotka_law(records), no_author),
        (gettext('Anahtar Kelime Bulutu'),                   lambda: keyword_cloud(records),
         gettext('Anahtar kelime veya özet bilgisi yok.')),
        (gettext('Anahtar Kelime Eş-Oluşum Ağı'),           lambda: keyword_cooccurrence(records),
         gettext('Aynı yayında birlikte geçen anahtar kelime yok.')),
        (gettext('Anahtar Kelime Zaman Trendi'),             lambda: keyword_trend(records),
         gettext('Anahtar kelime bilgisi ve en az 3 farklı yayın yılı gerekir.'), True),
        (gettext('En Çok Atıf Alan Yayınlar (Top 10)'),      lambda: top_cited(records), no_citation),
        (gettext('En Çok Yayın Yapılan Dergiler'),           lambda: top_journals(records),
         gettext('Dergi / kaynak bilgisi yok.')),
        (gettext('Kurum / Ülke Dağılımı (Top 10)'),          lambda: top_institutions(records),
         gettext('Ülke veya kurum bilgisi yok.')),
        (gettext('Ülke İşbirliği Ağı'),                      lambda: country_collaboration(records),
         gettext('Birden fazla ülkeden yazarı olan yayın yok.')),
        (gettext('Yazar İşbirliği Ağı'),                     lambda: author_collaboration(records),
         gettext('Birden fazla yazarlı yayın yok.')),
        (gettext('Yayın Türleri Dağılımı'),                  lambda: publication_types(records),
         gettext('Yayın türü bilgisi yok.')),
        (gettext('Atıf Analizi ve H-index'),                 lambda: citation_analysis(records), no_citation),
        (gettext('Yıllık Atıf Trendi'),                      lambda: annual_citation_trend(records),
         gettext('Yayın yılı bilinen ve atıf almış yayın yok.'), True),
        (gettext('Araştırma Konusu Kümeleri (Topic Map)'),    lambda: topic_map(records),
         gettext('Birlikte geçen en az 4 anahtar kelimeden oluşan küme bulunamadı.')),
        (gettext('Araştırma Boşluğu Haritası (Research Gap)'), lambda: research_gap(records),
         gettext('Yayın yılı bilgisi ve en az 3 yayında geçen en az 5 anahtar kelime gerekir.'), True),
        (gettext('Bradford Kanunu — Çekirdek Dergi Bölgeleri'), lambda: bradford_law(records),
         gettext('En az 3 farklı dergi/kaynak gerekir.')),
        (gettext('Tematik Harita (Callon Merkeziyet × Yoğunluk)'), lambda: thematic_map(records),
         gettext('Anahtar kelime eş-oluşum ağında en az 2 küme gerekir.')),
        (gettext('Tematik Evrim (Dönemler Arası Tema Akışı)'), lambda: thematic_evolution(records),
         gettext('Her dönemde yeterli kayıt ve anahtar kelime kümesi ile dönemler arasında paylaşılan tema gerekir.')),
        (gettext('Üç Alan Grafiği (Yazar ↔ Anahtar Kelime ↔ Dergi)'), lambda: three_field_plot(records),
         gettext('En az 2 yazar, 2 anahtar kelime ve 2 dergi arasında birlikte geçme akışı gerekir.')),
        (gettext('Ülke İşbirliği: Tek Ülkeli ve Çok Ülkeli Yayınlar (SCP/MCP)'), lambda: scp_mcp_chart(records),
         gettext('Ülke veya kurum bilgisi yok.')),
        (gettext('Bibliyografik Eşleşme Ağı (Paylaşılan Referanslar)'), lambda: bibliographic_coupling(records),
         gettext('Referans listesi (en az 2 kayıtta, paylaşılan referansla) yok.')),
        (gettext('Yerel Atıf ve Küresel Atıf Karşılaştırması'), lambda: local_global_citations(records),
         gettext('Bu veri setindeki kayıtlar arasında referans üzerinden iç atıf bulunamadı.')),
    ]
    citation_based = {
        gettext('En Çok Atıf Alan Yayınlar (Top 10)'), gettext('Atıf Analizi ve H-index'),
        gettext('Yıllık Atıf Trendi'), gettext('Araştırma Boşluğu Haritası (Research Gap)'),
        gettext('Yerel Atıf ve Küresel Atıf Karşılaştırması'),
    }
    results = []
    for title, fn, reason, *is_series in analyses:
        if not has_citations and title in citation_based:
            if skipped is not None:
                skipped.append((title, gettext('Veri kaynağı (PubMed) atıf sayısı sağlamıyor.')))
            continue
        try:
            fig = fn()
            if fig is None:
                if skipped is not None:
                    skipped.append((title, reason))
            else:
                buf = io.BytesIO()
                fig.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
                buf.seek(0)
                png_bytes = buf.getvalue()
                buf.close()
                plt.close(fig)
                del fig
                _gc.collect()
                if is_series and time_series is not None:
                    time_series.append(len(results))
                results.append((title, png_bytes))
        except Exception as e:
            logger.warning(f'Analiz başarısız [{title}]: {e}')
            if skipped is not None:
                skipped.append((title, gettext('Hesaplama sırasında hata oluştu.')))
            try:
                plt.close('all')
            except Exception:
                pass
    return results


def _last_complete_year() -> int:
    """Zaman serilerinin son yılı: içinde bulunulan yıl eksik veri → yapay düşüş gösterir."""
    from datetime import date
    return date.today().year - 1


def _set_integer_year_ticks(ax, years: list[int], max_ticks: int = 15) -> None:
    """Yıl eksenini tam sayıya zorlar (AutoLocator kısa aralıkta ondalık yıl üretebilir).
    Uzun aralıklarda (>max_ticks) etiketler sıklaştırılır, son yıl her zaman korunur."""
    if not years:
        return
    if len(years) <= max_ticks:
        ticks = years
    else:
        step = -(-len(years) // max_ticks)  # ceil
        ticks = list(years[::step])
        if years[-1] not in ticks:
            ticks.append(years[-1])
    ax.set_xticks(ticks)
    if len(years) > 20:
        ax.tick_params(axis='x', rotation=45)


# ─────────────────────────── 1. Yayın Trendi ───────────────────────────

def publication_trend(records: list[dict]):
    years = [r['year'] for r in records if r.get('year') and 1900 < r['year'] <= _last_complete_year()]
    if not years:
        return None

    counter = Counter(years)
    # Yayın olmayan yıllar 0 olarak gösterilir (atlanırsa çizgi boşluğu gizler)
    sorted_years = list(range(min(counter), max(counter) + 1))
    counts = [counter.get(y, 0) for y in sorted_years]

    # Çubuk rengi: değer yoğunluğuna göre mavi gradyan
    max_c = max(counts) or 1
    bar_colors = [plt.cm.Blues(0.35 + 0.55 * c / max_c) for c in counts]

    fig, ax = plt.subplots(figsize=(10, 9))
    bars = ax.bar(sorted_years, counts, color=bar_colors, width=0.7, zorder=2,
                  edgecolor='white', linewidth=0.5)
    ax.plot(sorted_years, counts, color=TREND_RED, linewidth=2.5,
            marker='o', markersize=7, zorder=3, label=gettext('Yayın Trendi'), alpha=0.9)

    ax.set_xlabel(gettext('Yıl'), fontsize=12, labelpad=8)
    ax.set_ylabel(gettext('Yayın Sayısı'), fontsize=12, labelpad=8)
    ax.set_title(gettext('Yıllara Göre Yayın Trendi'))
    ax.grid(axis='y', zorder=1)
    ax.legend(fontsize=11)
    _add_bar_labels(ax, bars)
    _set_integer_year_ticks(ax, sorted_years)

    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 2. En Verimli Yazarlar ───────────────────────────

def top_authors(records: list[dict], n: int = 15):
    author_count, display = _group_authors(records)
    if not author_count:
        return None

    top = author_count.most_common(n)
    names = [display[key] for key, _ in top]
    counts = [c for _, c in top]
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(names))]

    fig, ax = plt.subplots(figsize=(9, max(10, len(names) * 0.75)))
    y_pos = range(len(names))
    bars = ax.barh(y_pos, counts, color=colors, alpha=0.9, height=0.7,
                   edgecolor='white', linewidth=0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel(gettext('Yayın Sayısı'), fontsize=12, labelpad=8)
    ax.set_title(gettext('En Verimli Yazarlar (Top {n})').format(n=len(names)))
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
    ax.set_title(gettext('Anahtar Kelime Bulutu'), fontsize=15, fontweight='bold', pad=18)
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
    ax.set_xlabel(gettext('Atıf Sayısı'), fontsize=12, labelpad=8)
    ax.set_title(gettext('En Çok Atıf Alan Yayınlar (Top {n})').format(n=len(top)))
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
    ax.set_xlabel(gettext('Yayın Sayısı'), fontsize=12, labelpad=8)
    ax.set_title(gettext('En Çok Yayın Yapılan Dergiler / Kaynaklar (Top {n})').format(n=len(top)))
    ax.grid(axis='x', zorder=1)
    _add_hbar_labels(ax, bars)
    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 6. Kurum / Ülke Dağılımı ───────────────────────────

def _country_label(c: str) -> str:
    """ISO-2 kodu (OpenAlex: US, TR) → etkin dilde ülke adı; ad gelirse (WoS/Scopus) aynen."""
    if len(c) != 2 or not c.isalpha() or not c.isupper():
        return c
    try:
        from babel import Locale
        from django.utils.translation import get_language
        lang = (get_language() or 'tr').split('-')[0]
        return Locale.parse(lang).territories.get(c, c)
    except Exception:
        return c


def _record_countries(r: dict) -> list[str]:
    """Kaydın farklı ülkeleri (tam sayım: her ülke yayın başına bir kez)."""
    names = []
    for c in (r.get('country') or '').replace(';', ',').split(','):
        c = c.strip()
        if c:
            label = _country_label(c)
            if label not in names:
                names.append(label)
    return names


def _record_institutions(r: dict) -> list[str]:
    """Kaydın farklı kurumları (tam sayım: her kurum yayın başına bir kez).
    WoS C1 "[Yazar A; Yazar B] Kurum, …; [Yazar C] Kurum2, …" — köşeli parantezli yazar
    grupları ';' içerdiği için bölmeden önce atılır."""
    import re
    raw = re.sub(r'\[[^\]]*\]\s*', '', r.get('institution') or '')
    names = []
    for inst in raw.split(';'):
        inst = inst.strip()
        if inst and inst not in names:
            names.append(inst)
    return names


def top_institutions(records: list[dict], n: int = 10):
    country_counter = Counter()
    inst_counter = Counter()
    for r in records:
        for c in _record_countries(r):
            country_counter[c] += 1
        for inst in _record_institutions(r):
            inst_counter[inst] += 1

    if country_counter:
        top = country_counter.most_common(n)
        title_str = gettext('Ülkelere Göre Yayın Dağılımı (Top {n})').format(n=min(n, len(top)))
    elif inst_counter:
        top = inst_counter.most_common(n)
        title_str = gettext('Kurumlara Göre Yayın Dağılımı (Top {n})').format(n=min(n, len(top)))
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
    ax.set_xlabel(gettext('Yayın Sayısı'), fontsize=12, labelpad=8)
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
    _, display = _group_authors(records)

    for r in records:
        keys = sorted(set(
            canonical_author_key(a.strip()) for a in r.get('authors', []) if a.strip()
        ) - {''})
        if len(keys) < 2:
            continue
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                pair = tuple(sorted([keys[i], keys[j]]))
                coauth_count[pair] += 1

    for (a1, a2), weight in coauth_count.items():
        if weight >= min_collab:
            G.add_edge(display[a1], display[a2], weight=weight)

    if G.number_of_nodes() == 0:
        for (a1, a2), weight in coauth_count.most_common(60):
            G.add_edge(display[a1], display[a2], weight=weight)

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
    cbar.set_label(gettext('Ortak Yazar Sayısı'), fontsize=10)

    ax.set_title(gettext('Yazar İşbirliği Ağı'))
    ax.axis('off')
    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 8. Yayın Türleri ───────────────────────────

def publication_types(records: list[dict]):
    types = [r.get('pub_type', '').strip().lower() for r in records if r.get('pub_type', '').strip()]
    if not types:
        return None

    TYPE_TR = {
        'article':          gettext('Makale'),
        'review':           gettext('Derleme'),
        'inproceedings':    gettext('Konferans Bildirisi'),
        'conference paper': gettext('Konferans Bildirisi'),
        'book chapter':     gettext('Kitap Bölümü'),
        'book':             gettext('Kitap'),
        'editorial':        gettext('Editoryal'),
        'letter':           gettext('Mektup'),
        'note':             gettext('Not'),
        'short survey':     gettext('Kısa Derleme'),
        'erratum':          gettext('Düzeltme'),
        'preprint':         gettext('Ön Baskı'),
        'dissertation':     gettext('Tez'),
        'dataset':          gettext('Veri Seti'),
        'other':            gettext('Diğer'),
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
    ax.set_title(gettext('Yayın Türleri Dağılımı'))
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
    # Ortalama/medyan tüm yayınlar üzerinden — 0 atıflıları dışlamak değeri şişirir
    all_cit = [r.get('cited_by') or 0 for r in records]
    mean_cit = total_cit / len(all_cit)
    median_cit = _median(all_cit)

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
    ax1.set_xlabel(gettext('Yayın Sırası (atıfa göre)'), fontsize=11, labelpad=8)
    ax1.set_ylabel(gettext('Atıf Sayısı'), fontsize=11, labelpad=8)
    ax1.set_title(gettext('Atıf Dağılımı'), fontsize=13, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(axis='y', zorder=0)

    # Sağ: İstatistik özet tablosu
    stats = [
        (gettext('Toplam Yayın'),          f'{len(records):,}'),
        (gettext('Atıflı Yayın'),          f'{len(citations):,}'),
        (gettext('H-index'),               str(h)),
        (gettext('Toplam Atıf'),           f'{total_cit:,}'),
        (gettext('Ort. Atıf / Yayın'),     f'{mean_cit:.1f}'),
        (gettext('En Çok Atıf'),           f'{citations[0]:,}' if citations else '0'),
        (gettext('Medyan Atıf'),           f'{median_cit:.1f}' if median_cit % 1 else f'{median_cit:.0f}'),
    ]
    ax2.axis('off')
    tbl = ax2.table(
        cellText=[[k, v] for k, v in stats],
        colLabels=[gettext('Metrik'), gettext('Değer')],
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
    ax2.set_title(gettext('Özet İstatistikler'), fontsize=13, fontweight='bold', pad=20)

    fig.suptitle(gettext('Atıf Analizi ve H-index'), fontsize=15, fontweight='bold', y=1.01)
    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 10. Yıllık Atıf Trendi ───────────────────────────

def annual_citation_trend(records: list[dict]):
    # Ortalama için o yılın tüm yayınları (0 atıflılar dahil) sayılır
    year_citations = defaultdict(list)
    for r in records:
        if r.get('year') and 1900 < r['year'] <= _last_complete_year():
            year_citations[r['year']].append(r.get('cited_by') or 0)

    if not any(sum(v) for v in year_citations.values()):
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
            label=gettext('Toplam Atıf'), width=0.7, zorder=2)
    ax2.plot(sorted_years, mean_per_year,
             color=TREND_RED, linewidth=2.5,
             marker='o', markersize=7, label=gettext('Ort. Atıf / Yayın'), zorder=3)

    ax1.set_xlabel(gettext('Yıl'), fontsize=12, labelpad=8)
    ax1.set_ylabel(gettext('Toplam Atıf Sayısı'), fontsize=12, color='#1e3a5f', labelpad=8)
    ax2.set_ylabel(gettext('Ortalama Atıf / Yayın'), fontsize=12, color=TREND_RED, labelpad=8)
    ax1.tick_params(axis='y', labelcolor='#1e3a5f')
    ax2.tick_params(axis='y', labelcolor=TREND_RED)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=11)
    ax1.set_title(gettext('Yıllık Atıf Trendi'))
    ax1.grid(axis='y', zorder=0)
    _set_integer_year_ticks(ax1, sorted_years)

    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 11. Büyüme Oranı ───────────────────────────

# Bu eşikten kısa zaman serilerinde büyüme oranı/CAGR küçük taban etkisine açıktır (A6)
SHORT_SERIES_YEARS = 5


def publication_growth_rate(records: list[dict]):
    years = [r['year'] for r in records if r.get('year') and 1900 < r['year'] <= _last_complete_year()]
    if not years:
        return None

    counter = Counter(years)
    sorted_years = sorted(counter.keys())
    if len(sorted_years) < 3:
        return None

    # Ardışık takvim yılları: yayın olmayan yıl 0; önceki yılı 0 olan yılın oranı
    # tanımsız → çubuk çizilmez (eskiden ardışık olmayan yıllar karşılaştırılıyordu)
    sorted_years = list(range(sorted_years[0], sorted_years[-1] + 1))
    counts = [counter.get(y, 0) for y in sorted_years]

    growth_years = sorted_years[1:]
    growth_rates = []
    for i in range(1, len(counts)):
        rate = (counts[i] - counts[i - 1]) / counts[i - 1] * 100 if counts[i - 1] else float('nan')
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

    ax.set_xlabel(gettext('Yıl'), fontsize=12, labelpad=8)
    ax.set_ylabel(gettext('Yıllık Büyüme Oranı (%)'), fontsize=12, labelpad=8)
    ax.set_title(gettext('Yıllık Yayın Büyüme Oranı'))
    ax.legend(fontsize=11)
    ax.grid(axis='y', zorder=0)

    cagr_text = f'CAGR ({sorted_years[0]}–{sorted_years[-1]}): {cagr:+.1f}%'
    if len(sorted_years) < SHORT_SERIES_YEARS:
        cagr_text += '\n' + gettext(
            'Veri {n} yıldan kısa bir dönemi kapsıyor; büyüme oranları küçük '
            'taban etkisine açıktır.').format(n=SHORT_SERIES_YEARS)
    ax.text(0.98, 0.97, cagr_text,
            transform=ax.transAxes, fontsize=11, va='top', ha='right',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#f1f5f9',
                      edgecolor='#cbd5e0', alpha=0.95))

    _set_integer_year_ticks(ax, growth_years)
    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 12. Lotka Kanunu ───────────────────────────

def lotka_law(records: list[dict]):
    author_count, _ = _group_authors(records)
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
           label=gettext('Gözlemlenen'), zorder=2, edgecolor='white')
    ax.plot(k_values, theoretical, color=TREND_RED, linewidth=2.5,
            marker='s', markersize=7, label=gettext('Lotka Teorisi (1/k²)'), zorder=3)

    ax.set_xlabel(gettext('Yayın Sayısı (k)'), fontsize=12, labelpad=8)
    ax.set_ylabel(gettext('Yazar Sayısı'), fontsize=12, labelpad=8)
    ax.set_title(gettext('Lotka Kanunu — Yazar Üretkenlik Dağılımı'))
    ax.legend(fontsize=11)
    ax.grid(axis='y', zorder=0)
    ax.set_xticks(k_values)

    # Tek yayınlı yazar oranı
    single_pct = prod_dist.get(1, 0) / len(author_count) * 100 if author_count else 0
    ax.text(0.98, 0.97,
            gettext('Tek yayınlı yazarlar: {pct}\nToplam yazar: {total}').format(pct=f'{single_pct:.1f}%', total=f'{len(author_count):,}'),
            transform=ax.transAxes, fontsize=10, va='top', ha='right',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#f1f5f9',
                      edgecolor='#cbd5e0', alpha=0.95))

    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 13. Anahtar Kelime Eş-Oluşum Ağı ───────────────────────────

def keyword_clusters(records: list[dict], max_kw: int = 40, min_cooccur: int = 2):
    """
    Anahtar kelime eş-oluşum grafı + Louvain kümeleri (B2-2). VOSviewer/bibliometrix
    eşitliği için sabit seed'li Louvain kullanılır (`networkx.algorithms.community.
    louvain_communities`) — tekrarlanabilir kümeler, her çalıştırmada aynı sonuç.
    Döner: (G, communities, all_kw) — communities büyükten küçüğe sıralı set listesi,
    ya da veri yetersizse (None, None, None).
    """
    try:
        import networkx as nx
        from networkx.algorithms.community import louvain_communities
    except ImportError:
        return None, None, None

    # Önce en sık geçen anahtar kelimeleri bul
    all_kw = Counter()
    for r in records:
        for k in normalize_keywords(r.get('keywords', [])):
            if len(k) > 2:
                all_kw[k] += 1

    if not all_kw:
        return None, None, None

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
        return None, None, None

    if G.number_of_nodes() > max_kw:
        top_nodes = sorted(G.degree, key=lambda x: x[1], reverse=True)[:max_kw]
        G = G.subgraph([n for n, _ in top_nodes]).copy()

    try:
        communities = sorted(
            (set(c) for c in louvain_communities(G, weight='weight', seed=42)),
            key=len, reverse=True,
        )
    except Exception:
        communities = [set(G.nodes())]

    return G, communities, all_kw


def keyword_cooccurrence(records: list[dict], max_kw: int = 40, min_cooccur: int = 2):
    import networkx as nx
    G, communities, all_kw = keyword_clusters(records, max_kw, min_cooccur)
    if G is None:
        return None

    node_community = {n: i for i, comm in enumerate(communities) for n in comm}
    n_clusters = len(communities)
    cluster_colors = PALETTE[:n_clusters] if n_clusters <= len(PALETTE) else PALETTE

    node_sizes = [300 + all_kw.get(n, 1) * 60 for n in G.nodes()]
    node_colors = [cluster_colors[node_community.get(n, 0) % len(cluster_colors)]
                   for n in G.nodes()]
    edge_weights = [G[u][v].get('weight', 1) for u, v in G.edges()]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 10),
                                   gridspec_kw={'width_ratios': [1.6, 1]})
    ax1.set_facecolor('#f8fafc')
    fig.patch.set_facecolor('white')

    pos = nx.spring_layout(G, seed=42, k=2.5, weight='weight')

    nx.draw_networkx_edges(G, pos, ax=ax1, alpha=0.25,
                           width=[min(w * 0.6, 4.0) for w in edge_weights],
                           edge_color='#94a3b8')
    nx.draw_networkx_nodes(G, pos, ax=ax1, node_size=node_sizes,
                           node_color=node_colors, alpha=0.88,
                           linewidths=1.2, edgecolors='white')
    nx.draw_networkx_labels(G, pos, ax=ax1, font_size=7.5,
                            font_color='#1e293b', font_weight='bold')

    legend_patches = [
        mpatches.Patch(color=cluster_colors[i % len(cluster_colors)],
                       label=gettext('Küme {n}').format(n=i + 1))
        for i in range(min(n_clusters, 8))
    ]
    ax1.legend(handles=legend_patches, loc='lower right', fontsize=8,
              framealpha=0.85, title=gettext('Araştırma Kümeleri'), title_fontsize=9)
    ax1.set_title(gettext('Eş-Oluşum Ağı'), fontsize=13, fontweight='bold')
    ax1.axis('off')

    # B2-2: küme başına ilk kelimeler tablosu
    ax2.axis('off')
    shown_clusters = communities[:8]

    def _top_terms_label(comm):
        terms = sorted(comm, key=lambda n: all_kw.get(n, 0), reverse=True)
        label, shown_n = '', 0
        for t in terms:
            candidate = f'{label}, {t}' if label else t
            if len(candidate) > 48 and shown_n > 0:
                break
            label, shown_n = candidate, shown_n + 1
        if shown_n < len(terms):
            label += '…'
        return label

    table_rows = [
        [gettext('Küme {n}').format(n=i + 1), _top_terms_label(comm)]
        for i, comm in enumerate(shown_clusters)
    ]
    table_frac = min(1.0, (len(table_rows) + 1) * 0.08)
    tbl = ax2.table(
        cellText=table_rows,
        colLabels=[gettext('Küme'), gettext('İlk Kelimeler')],
        cellLoc='left',
        colWidths=[0.2, 0.8],
        bbox=[0.0, 1 - table_frac, 1.0, table_frac],
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    for (row, col), cell in tbl.get_celld().items():
        cell.set_edgecolor('#cbd5e0')
        if row == 0:
            cell.set_facecolor('#1e3a5f')
            cell.set_text_props(color='white', fontweight='bold')
        else:
            cell.set_facecolor('white' if row % 2 else '#f8fafc')
            if col == 0:
                cell.set_text_props(color=cluster_colors[(row - 1) % len(cluster_colors)],
                                    fontweight='bold')
            else:
                cell.set_text_props(color='#1e293b')

    ax2.text(0.0, 1 - table_frac - 0.04,
             gettext('Toplam {n} anahtar kelime, {e} bağlantı, {c} küme').format(
                 n=G.number_of_nodes(), e=G.number_of_edges(), c=n_clusters),
             transform=ax2.transAxes, fontsize=9, color='#475569', va='top')
    ax2.set_title(gettext('Kümelere Göre İlk Kelimeler'), fontsize=13, fontweight='bold', pad=20)

    fig.suptitle(gettext('Anahtar Kelime Eş-Oluşum Ağı ve Kümeler (VOSviewer-style)'),
                fontsize=15, fontweight='bold', y=1.01)
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
    years = sorted({r['year'] for r in records if r.get('year') and 1900 < r['year'] <= _last_complete_year()})

    if len(years) < 3:
        return None
    years = list(range(years[0], years[-1] + 1))   # yayın olmayan yıllar 0

    from collections import defaultdict
    year_kw = defaultdict(lambda: defaultdict(int))
    for r in records:
        if not r.get('year') or not (1900 < r['year'] <= _last_complete_year()):
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

    ax.set_xlabel(gettext('Yıl'), fontsize=12, labelpad=8)
    ax.set_ylabel(gettext('Yayın Sayısı'), fontsize=12, labelpad=8)
    ax.set_title(gettext('Anahtar Kelime Zaman Trendi (Top {n})').format(n=plotted))
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
        countries = _record_countries(r)
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
    cbar.set_label(gettext('İşbirliği Sayısı'), fontsize=10)

    ax.set_title(gettext('Ülke İşbirliği Ağı'))
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

    # Bitmemiş yıl ve yılı olmayan kayıtlar trend hesabına girmez
    last_year = _last_complete_year()
    records = [r for r in records if r.get('year') and 1900 < r['year'] <= last_year]
    now_year = max((r['year'] for r in records), default=0)
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

    # Medyan çizgileri
    ax.axvline(med_trend,  color='#94a3b8', linestyle='--', linewidth=1.2, alpha=0.7)
    ax.axhline(med_impact, color='#94a3b8', linestyle='--', linewidth=1.2, alpha=0.7)

    # Scatter
    sc = ax.scatter(trends, impacts, s=sizes, c=colors, alpha=0.82,
                    edgecolors='white', linewidths=1.0, zorder=3)

    # Kadrant arkaplan renkleri — medyan çizgilerine göre (eksen yarısına göre değil)
    x0, x1 = min(trends) - 0.05, max(trends) + 0.05
    ax.set_xlim(x0, x1)
    y0, y1 = ax.get_ylim()
    ax.fill_between([x0, med_trend], med_impact, y1, color='#E15759',
                    alpha=0.06, linewidth=0, zorder=0)   # Research Gap bölgesi
    ax.fill_between([med_trend, x1], med_impact, y1, color='#4E79A7',
                    alpha=0.06, linewidth=0, zorder=0)   # Altın bölge
    ax.set_ylim(y0, y1)

    # Etiketler — sadece gap + altın alan (okunabilirlik)
    labeled = set()
    for i, p in enumerate(points):
        if colors[i] in ('#E15759', '#4E79A7') and p['kw'] not in labeled:
            ax.annotate(p['kw'], (p['trend'], p['impact_norm']),
                        fontsize=7.5, ha='center', va='bottom',
                        xytext=(0, 6), textcoords='offset points',
                        color='#1e293b', fontweight='bold')
            labeled.add(p['kw'])

    # Kadrant başlıkları — x veri, y eksen oranı: y ekseni 0'dan başlamayabilir,
    # veri koordinatlı y eksen dışına düşüp bbox_inches='tight' ile resmi uzatıyordu
    from matplotlib.transforms import blended_transform_factory
    xlim = ax.get_xlim()
    kw_args = dict(fontsize=9, alpha=0.55, fontstyle='italic',
                   transform=blended_transform_factory(ax.transData, ax.transAxes))
    ax.text(med_trend - (med_trend - xlim[0]) * 0.5, 0.97,
            '★ ' + gettext('RESEARCH GAP'), ha='center', va='top', color='#E15759', **kw_args)
    ax.text(med_trend + (xlim[1] - med_trend) * 0.5, 0.97,
            gettext('ALTIN ALAN'), ha='center', va='top', color='#4E79A7', **kw_args)
    ax.text(med_trend - (med_trend - xlim[0]) * 0.5, 0.03,
            gettext('DÜŞEN ALAN'), ha='center', va='bottom', color='#BAB0AC', **kw_args)
    ax.text(med_trend + (xlim[1] - med_trend) * 0.5, 0.03,
            gettext('YÜKSELİŞTEKİ ALAN'), ha='center', va='bottom', color='#76B7B2', **kw_args)

    # Legend
    from matplotlib.lines import Line2D
    legend_items = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#E15759',
               markersize=10, label=gettext('Research Gap (fırsat)')),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#4E79A7',
               markersize=10, label=gettext('Altın Alan (aktif & etkili)')),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#76B7B2',
               markersize=10, label=gettext('Yükselen Alan')),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#BAB0AC',
               markersize=10, label=gettext('Düşen Alan')),
    ]
    # Lejant eksenin üstünde: sağ-alt köşede kadran etiketinin üstüne biniyordu
    ax.legend(handles=legend_items, loc='lower center', bbox_to_anchor=(0.5, 1.0),
              ncol=4, fontsize=8.5, frameon=False)

    # Gap keywords listesi (alt açıklama)
    gap_kws = [points[i]['kw'] for i in gap_indices[:6]]
    if gap_kws:
        # 🎯 kaldırıldı: DejaVu Sans'ta glif yok, PDF'te boş kutu çıkıyordu
        gap_text = gettext('Önerilen Araştırma Boşlukları:') + ' ' + ' · '.join(gap_kws)
        fig.text(0.5, 0.01, gap_text, ha='center', fontsize=9,
                 color='#E15759', fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.4', fc='#fff5f5', ec='#E15759', alpha=0.8))

    ax.set_xlabel(gettext('Yayın Trendi  (← Azalıyor  |  Artıyor →)'), fontsize=11)
    ax.set_ylabel(gettext('Atıf Etkisi  (↑ Yüksek)'), fontsize=11)
    ax.set_title(gettext('Araştırma Boşluğu Haritası (Research Gap)'), pad=32)
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

        ax.text(x, y - 1.1, gettext('Küme {n}').format(n=idx + 1) + f'  ({topic["n_kw"]} kw)',
                ha='center', va='top', fontsize=8.5, color='#475569')

    ax.set_xlim(0, cols * 3.5 + 0.5)
    ax.set_ylim(0, (rows + 0.5) * 2.5)
    ax.axis('off')
    ax.set_title(gettext('Araştırma Konusu Kümeleri (Topic Map)'), pad=18)
    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 18. Bradford Kanunu ───────────────────────────

def bradford_zones(records: list[dict]):
    """
    Bradford Kanunu (B2-1) hesaplaması: dergiler yayın sayısına göre azalan sırada
    dizilip, toplam yayının üçte birini üreten ardışık dergi grupları 3 bölgeye
    ayrılır. Bölge 1 (çekirdek) en az dergiyle aynı yayın miktarını üretir; Bölge 2
    ve 3'te aynı miktar yayın için giderek daha fazla dergi gerekir — konunun az
    sayıda "çekirdek" dergide yoğunlaştığını gösterir.
    Döner: (zones: [[(dergi, yayın sayısı), ...] × 3], zone_totals: [int, int, int])
    veya veri yetersizse (None, None).
    """
    journals = [r['journal'].strip() for r in records if r.get('journal', '').strip()]
    if len(set(journals)) < 3:
        return None, None

    counter = Counter(journals)
    ranked = counter.most_common()  # (dergi, yayın sayısı), azalan sırada
    total = sum(c for _, c in ranked)
    zone_target = total / 3

    zones: list[list] = [[], [], []]
    zone_totals = [0, 0, 0]
    zone_idx = 0
    for journal, count in ranked:
        if zone_idx < 2 and zone_totals[zone_idx] >= zone_target:
            zone_idx += 1
        zones[zone_idx].append((journal, count))
        zone_totals[zone_idx] += count

    return zones, zone_totals


def bradford_law(records: list[dict]):
    """Bradford Kanunu grafiği — bölge hesabı için bkz. bradford_zones()."""
    zones, zone_totals = bradford_zones(records)
    if zones is None:
        return None
    total = sum(zone_totals)

    zone_colors = [TREND_RED, PALETTE[1], PALETTE[9]]
    zone_row_colors = ['#fee2e2', '#fef3c7', '#e0e7ff']
    zone_labels = [gettext('Bölge 1 (Çekirdek)'), gettext('Bölge 2'), gettext('Bölge 3')]

    # Bölge 1 ve 2 tek tek gösterilir (çekirdeği oluşturan dergiler); Bölge 3
    # genelde çok kalabalık olduğundan yalnız tabloda sayı/toplamla özetlenir.
    shown = zones[0] + zones[1]
    shown_names = [j[:45] + '…' if len(j) > 45 else j for j, _ in shown]
    shown_counts = [c for _, c in shown]
    shown_colors = [zone_colors[0]] * len(zones[0]) + [zone_colors[1]] * len(zones[1])

    fig_height = max(8, len(shown) * 0.45)
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(13, fig_height),
        gridspec_kw={'width_ratios': [1.3, 1]},
    )

    y_pos = range(len(shown_names))
    bars = ax1.barh(y_pos, shown_counts, color=shown_colors, alpha=0.9,
                    edgecolor='white', linewidth=0.5)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(shown_names, fontsize=9)
    ax1.invert_yaxis()
    ax1.set_xlabel(gettext('Yayın Sayısı'), fontsize=11, labelpad=8)
    ax1.set_title(gettext('Bölge 1 ve 2 Dergileri'), fontsize=13, fontweight='bold')
    ax1.grid(axis='x', zorder=1)
    _add_hbar_labels(ax1, bars)
    ax1.legend(handles=[mpatches.Patch(color=zone_colors[0], label=zone_labels[0]),
                        mpatches.Patch(color=zone_colors[1], label=zone_labels[1])],
               fontsize=9, loc='lower right')

    ax2.axis('off')
    table_rows = [
        [zone_labels[i], f'{len(zones[i]):,}', f'{zone_totals[i]:,}',
         f'%{round(100 * zone_totals[i] / total)}']
        for i in range(3)
    ]
    # Tablo yalnız 4 satır (başlık + 3 bölge) — sol panel uzun dergi listesiyle
    # yükseldiğinde ax2 de yükselir; tablo sabit ~2.6" yükseklikte üstte tutulur,
    # yoksa altında devasa boş alan kalır (Topic Map'teki boş alan sorunuyla aynı
    # kalıptan kaçınma).
    table_frac = min(1.0, 2.6 / fig_height)
    tbl = ax2.table(
        cellText=table_rows,
        colLabels=[gettext('Bölge'), gettext('Dergi Sayısı'), gettext('Yayın Sayısı'), gettext('Pay')],
        cellLoc='center',
        colWidths=[0.32, 0.26, 0.26, 0.16],
        bbox=[0.0, 1 - table_frac, 1.0, table_frac],
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10.5)
    for (row, col), cell in tbl.get_celld().items():
        if row == 0:
            cell.set_facecolor('#1e3a5f')
            cell.set_text_props(color='white', fontweight='bold')
        else:
            cell.set_facecolor(zone_row_colors[row - 1])
            cell.set_text_props(color='#1e293b')
        cell.set_edgecolor('#cbd5e0')
    ax2.set_title(gettext('Bradford Bölgeleri Özeti'), fontsize=13, fontweight='bold', pad=20)

    fig.suptitle(gettext('Bradford Kanunu — Çekirdek Dergi Bölgeleri'), fontsize=15, fontweight='bold', y=1.01)
    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 19. Tematik Harita ───────────────────────────

def thematic_map_themes(records: list[dict], max_kw: int = 40, min_cooccur: int = 2):
    """
    Tematik harita (B2-3, Callon merkeziyet × yoğunluk) hesabı. `keyword_clusters()`
    ile bulunan her Louvain kümesi (tema) için:
    - Merkeziyet: temanın DİĞER temalarla dışa bağlantı gücü — 10 × (kümeyle diğer
      kümeler arasındaki toplam eş-oluşum ağırlığı). Yüksekse tema alanın genelinde
      önemli/merkezi.
    - Yoğunluk: temanın İÇ tutarlılığı — 10 × (küme içi toplam eş-oluşum ağırlığı) /
      küme büyüklüğü. Yüksekse tema kendi içinde olgun/gelişmiş.
    Döner: (themes, mean_centrality, mean_density) — themes: [{'label', 'centrality',
    'density', 'weight'}, ...], ya da veri yetersizse (None, None, None).
    """
    G, communities, all_kw = keyword_clusters(records, max_kw, min_cooccur)
    if G is None or len(communities) < 2:
        return None, None, None

    node_cluster = {n: i for i, comm in enumerate(communities) for n in comm}
    internal_weight = defaultdict(float)
    external_weight = defaultdict(float)
    for u, v, data in G.edges(data=True):
        w = data.get('weight', 1)
        cu, cv = node_cluster[u], node_cluster[v]
        if cu == cv:
            internal_weight[cu] += w
        else:
            external_weight[cu] += w
            external_weight[cv] += w

    themes = []
    for i, comm in enumerate(communities):
        top_terms = sorted(comm, key=lambda n: all_kw.get(n, 0), reverse=True)[:2]
        themes.append({
            'label': ' / '.join(top_terms),
            'centrality': 10 * external_weight.get(i, 0),
            'density': 10 * internal_weight.get(i, 0) / len(comm),
            'weight': sum(all_kw.get(kw, 0) for kw in comm),
        })

    mean_centrality = sum(t['centrality'] for t in themes) / len(themes)
    mean_density = sum(t['density'] for t in themes) / len(themes)
    return themes, mean_centrality, mean_density


def thematic_map(records: list[dict]):
    """
    Tematik harita grafiği: her tema merkeziyet (x) × yoğunluk (y) düzleminde bir
    balon; ortalama değerler dört kadranı ayırır (bibliometrix/SciMAT kalıbı):
    sağ-üst Motor, sol-üst Niş, sağ-alt Temel, sol-alt Gelişen/Azalan Temalar.
    """
    themes, mean_c, mean_d = thematic_map_themes(records)
    if themes is None:
        return None

    max_weight = max(t['weight'] for t in themes) or 1
    sizes = [300 + 2200 * t['weight'] / max_weight for t in themes]
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(themes))]

    fig, ax = plt.subplots(figsize=(11, 10))
    ax.set_facecolor('#f8fafc')
    fig.patch.set_facecolor('white')

    xs = [t['centrality'] for t in themes]
    ys = [t['density'] for t in themes]
    x_pad = (max(xs) - min(xs)) * 0.25 or 1
    y_pad = (max(ys) - min(ys)) * 0.25 or 1
    x_min, x_max = min(0, min(xs) - x_pad), max(xs) + x_pad
    y_min, y_max = min(0, min(ys) - y_pad), max(ys) + y_pad

    # Kadran arka planı
    ax.axvspan(mean_c, x_max, ymin=(mean_d - y_min) / (y_max - y_min), ymax=1,
              color=TREND_RED, alpha=0.05, zorder=0)
    ax.axvspan(x_min, mean_c, ymin=(mean_d - y_min) / (y_max - y_min), ymax=1,
              color=PALETTE[1], alpha=0.05, zorder=0)
    ax.axvspan(mean_c, x_max, ymin=0, ymax=(mean_d - y_min) / (y_max - y_min),
              color=PALETTE[4], alpha=0.05, zorder=0)
    ax.axvspan(x_min, mean_c, ymin=0, ymax=(mean_d - y_min) / (y_max - y_min),
              color=PALETTE[9], alpha=0.05, zorder=0)

    ax.axvline(mean_c, color='#94a3b8', linestyle='--', linewidth=1, zorder=1)
    ax.axhline(mean_d, color='#94a3b8', linestyle='--', linewidth=1, zorder=1)

    ax.scatter(xs, ys, s=sizes, c=colors, alpha=0.85, edgecolors='white',
              linewidths=1.2, zorder=3)
    for t, x, y in zip(themes, xs, ys):
        ax.annotate(t['label'], (x, y), xytext=(0, 0), textcoords='offset points',
                    ha='center', va='center', fontsize=8.5, fontweight='bold',
                    color='#1e293b', zorder=4)

    quadrant_kwargs = dict(fontsize=10.5, fontweight='bold', color='#475569', alpha=0.8)
    ax.text(x_max, y_max, gettext('MOTOR TEMALAR'), ha='right', va='top', **quadrant_kwargs)
    ax.text(x_min, y_max, gettext('NİŞ TEMALAR'), ha='left', va='top', **quadrant_kwargs)
    ax.text(x_max, y_min, gettext('TEMEL TEMALAR'), ha='right', va='bottom', **quadrant_kwargs)
    ax.text(x_min, y_min, gettext('GELİŞEN veya AZALAN TEMALAR'), ha='left', va='bottom', **quadrant_kwargs)

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel(gettext('Merkeziyet (diğer temalarla bağlantı gücü)'), fontsize=11, labelpad=8)
    ax.set_ylabel(gettext('Yoğunluk (tema içi tutarlılık)'), fontsize=11, labelpad=8)
    ax.set_title(gettext('Tematik Harita (Callon Merkeziyet × Yoğunluk)'))
    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 20. Tematik Evrim ───────────────────────────

def thematic_evolution_periods(records: list[dict], n_periods: int = 2, min_per_period: int = 8):
    """
    Kayıtları yayın yılına göre `n_periods` eşit yıl aralığına böler (B2-4, otomatik
    dönemlendirme — kullanıcı kesim yılı girmiyor). Döner: [(dönem etiketi, dönem
    kayıtları), ...] ya da her dönemde en az `min_per_period` kayıt yoksa None.
    """
    last_year = _last_complete_year()
    years = sorted(r['year'] for r in records if r.get('year') and 1900 < r['year'] <= last_year)
    if len(years) < min_per_period * n_periods:
        return None

    min_y, max_y = years[0], years[-1]
    if max_y <= min_y:
        return None

    span = max_y - min_y + 1
    cuts = [min_y + round(span * i / n_periods) for i in range(n_periods + 1)]
    cuts[0], cuts[-1] = min_y, max_y + 1

    periods = []
    for i in range(n_periods):
        lo, hi = cuts[i], cuts[i + 1]
        if hi <= lo:
            return None
        label = str(lo) if hi - lo == 1 else f'{lo}–{hi - 1}'
        period_records = [r for r in records if r.get('year') and lo <= r['year'] < hi]
        if len(period_records) < min_per_period:
            return None
        periods.append((label, period_records))
    return periods


def thematic_evolution_themes(records: list[dict], n_periods: int = 2,
                              max_kw: int = 40, min_cooccur: int = 2):
    """
    Tematik evrim hesabı (B2-4): her dönem `keyword_clusters()` ile BAĞIMSIZ kümelenir
    (tema = küme); ardışık dönemler arasında paylaşılan anahtar kelime SAYISI akış (flow)
    genişliğini belirler. Her temanın büyüklüğü ('size') kendi kelime kümesinin eleman
    sayısıdır — iki ayrı dönemin kümeleri birbirinden bağımsız birer bölüntü (partition)
    olduğundan, bir temadan çıkan/bir temaya giren akışların toplamı o temanın
    büyüklüğünü asla aşamaz (şerit genişlikleri kutu yüksekliğine her zaman sığar).
    Döner: (period_labels, period_themes, flows) ya da yetersizse (None, None, None).
    period_themes: dönem başına [{'label', 'keywords', 'size'}, ...] (büyükten küçüğe sıralı).
    flows: [(dönem_i, tema_a_idx, tema_b_idx, paylaşılan_kelime_sayısı), ...]
    """
    periods = thematic_evolution_periods(records, n_periods)
    if periods is None:
        return None, None, None

    period_labels = []
    period_themes = []
    for label, period_records in periods:
        G, communities, all_kw = keyword_clusters(period_records, max_kw, min_cooccur)
        if G is None or not communities:
            return None, None, None
        themes = []
        for comm in communities:
            top_terms = sorted(comm, key=lambda n: all_kw.get(n, 0), reverse=True)[:2]
            themes.append({
                'label': ' / '.join(top_terms),
                'keywords': set(comm),
                'size': len(comm),
            })
        period_labels.append(label)
        period_themes.append(themes)

    flows = []
    for i in range(len(period_themes) - 1):
        for a_idx, theme_a in enumerate(period_themes[i]):
            for b_idx, theme_b in enumerate(period_themes[i + 1]):
                shared = theme_a['keywords'] & theme_b['keywords']
                if shared:
                    flows.append((i, a_idx, b_idx, len(shared)))

    if not flows:
        return None, None, None

    return period_labels, period_themes, flows


def _sankey_ribbon(ax, x0, x1, y0_top, y0_bot, y1_top, y1_bot, color, alpha=0.45):
    """İki dönem kutusu arasında düz Bezier eğrili akış şeridi (B2-4)."""
    from matplotlib.path import Path
    xm = (x0 + x1) / 2
    verts = [
        (x0, y0_top), (xm, y0_top), (xm, y1_top), (x1, y1_top),
        (x1, y1_bot), (xm, y1_bot), (xm, y0_bot), (x0, y0_bot),
        (x0, y0_top),
    ]
    codes = [Path.MOVETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4,
             Path.LINETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4,
             Path.CLOSEPOLY]
    ax.add_patch(mpatches.PathPatch(Path(verts, codes), facecolor=color,
                                    edgecolor='none', alpha=alpha, zorder=2))


def thematic_evolution(records: list[dict]):
    """
    Tematik Evrim grafiği (B2-4): dönemler arası tema akışı, alüvyal/Sankey benzeri
    diyagram. Veri yeterliyse 3 dönem, değilse 2 dönem denenir (otomatik).
    """
    period_labels = period_themes = flows = None
    for n_periods in (3, 2):
        period_labels, period_themes, flows = thematic_evolution_themes(records, n_periods)
        if period_labels is not None:
            break
    if period_labels is None:
        return None

    n_cols = len(period_labels)
    col_totals = [sum(t['size'] for t in themes) for themes in period_themes]
    max_total = max(col_totals)
    gap = max_total * 0.04

    fig, ax = plt.subplots(figsize=(4.5 + 3.3 * n_cols, 9))
    ax.set_facecolor('#f8fafc')
    fig.patch.set_facecolor('white')

    col_x = [i * 2.4 for i in range(n_cols)]
    box_width = 0.5

    col_boxes = []
    col_colors = []
    for themes in period_themes:
        y = max_total
        boxes = []
        colors = []
        for idx, t in enumerate(themes):
            y_top = y
            y_bot = y - t['size']
            boxes.append((y_top, y_bot))
            colors.append(PALETTE[idx % len(PALETTE)])
            y = y_bot - gap
        col_boxes.append(boxes)
        col_colors.append(colors)

    for i in range(n_cols - 1):
        out_cursor = [b[0] for b in col_boxes[i]]
        in_cursor = [b[0] for b in col_boxes[i + 1]]
        col_flows = sorted((f for f in flows if f[0] == i), key=lambda f: (f[1], f[2]))
        for (_, a_idx, b_idx, w) in col_flows:
            y0_top = out_cursor[a_idx]
            y0_bot = y0_top - w
            out_cursor[a_idx] = y0_bot
            y1_top = in_cursor[b_idx]
            y1_bot = y1_top - w
            in_cursor[b_idx] = y1_bot
            _sankey_ribbon(ax, col_x[i] + box_width / 2, col_x[i + 1] - box_width / 2,
                          y0_top, y0_bot, y1_top, y1_bot, color=col_colors[i][a_idx])

    for themes, boxes, colors, x in zip(period_themes, col_boxes, col_colors, col_x):
        for t, (y_top, y_bot), color in zip(themes, boxes, colors):
            ax.add_patch(mpatches.Rectangle((x - box_width / 2, y_bot), box_width,
                                            y_top - y_bot, facecolor=color, alpha=0.85,
                                            edgecolor='white', linewidth=1.2, zorder=3))
            ax.annotate(t['label'], (x, (y_top + y_bot) / 2), ha='center', va='center',
                       fontsize=8, fontweight='bold', color='#1e293b', zorder=4,
                       wrap=True)

    ax.set_xticks(col_x)
    ax.set_xticklabels(period_labels, fontsize=11, fontweight='bold')
    ax.set_xlim(col_x[0] - 1.8, col_x[-1] + 1.8)
    ax.set_ylim(-gap, max_total + gap)
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlabel(gettext('Dönem'), fontsize=11, labelpad=10)
    ax.set_title(gettext('Tematik Evrim (Dönemler Arası Tema Akışı)'))
    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 21. Üç Alan Grafiği ───────────────────────────

def three_field_plot_data(records: list[dict], top_authors_n: int = 10,
                          top_keywords_n: int = 10, top_journals_n: int = 10):
    """
    Üç Alan Grafiği hesabı (B2-5, bibliometrix 'Three Fields Plot' eşdeğeri):
    Yazar ↔ Anahtar Kelime ↔ Dergi arasında birlikte-geçme akışı.
    - Yazar/dergi kutu büyüklüğü: yalnız seçili (en sık) anahtar kelimelerle
      birlikte geçme TOPLAMI — bu kelimelerle hiç ortak geçmeyen yazar/dergi
      otomatik elenir, dolayısıyla akış toplamı kutu büyüklüğüne tam oturur.
    - Anahtar kelime kutu büyüklüğü: TÜM kayıtlardaki toplam frekans (sol ve
      sağ şeritler bu değeri BAĞIMSIZ olarak asla aşamaz — her ikisi de o
      kelimenin geçtiği yayınların birer alt kümesidir, B2-4'teki ispatla
      aynı mantık).
    Döner: (authors, keywords, journals, flows_ak, flows_kj) ya da yetersizse
    (None, None, None, None, None). authors/keywords/journals: [{'label','size'}, ...]
    büyükten küçüğe sıralı. flows_ak: [(yazar_idx, kelime_idx, ağırlık), ...],
    flows_kj: [(kelime_idx, dergi_idx, ağırlık), ...].
    """
    author_counts, author_display = _group_authors(records)
    if len(author_counts) < 2:
        return None, None, None, None, None

    kw_counts = Counter()
    for r in records:
        for k in set(normalize_keywords(r.get('keywords', []))):
            if len(k) > 2:
                kw_counts[k] += 1
    if len(kw_counts) < 2:
        return None, None, None, None, None

    journal_counts = Counter(r['journal'].strip() for r in records if r.get('journal', '').strip())
    if len(journal_counts) < 2:
        return None, None, None, None, None

    top_keywords = {kw for kw, _ in kw_counts.most_common(top_keywords_n)}

    author_kw_cooccur = Counter()
    kw_journal_cooccur = Counter()
    for r in records:
        rec_kws = {k for k in normalize_keywords(r.get('keywords', [])) if k in top_keywords}
        if not rec_kws:
            continue
        rec_authors = {canonical_author_key(a) for a in r.get('authors', []) if canonical_author_key(a)}
        journal = r.get('journal', '').strip()
        for k in rec_kws:
            for a in rec_authors:
                author_kw_cooccur[(a, k)] += 1
            if journal:
                kw_journal_cooccur[(k, journal)] += 1

    author_flow_total = Counter()
    for (a, k), w in author_kw_cooccur.items():
        author_flow_total[a] += w
    if len(author_flow_total) < 2:
        return None, None, None, None, None

    journal_flow_total = Counter()
    for (k, j), w in kw_journal_cooccur.items():
        journal_flow_total[j] += w
    if len(journal_flow_total) < 2:
        return None, None, None, None, None

    top_author_keys = [a for a, _ in author_flow_total.most_common(top_authors_n)]
    top_journal_keys = [j for j, _ in journal_flow_total.most_common(top_journals_n)]
    keywords_list = sorted(top_keywords, key=lambda k: kw_counts[k], reverse=True)

    author_index = {a: i for i, a in enumerate(top_author_keys)}
    kw_index = {k: i for i, k in enumerate(keywords_list)}
    journal_index = {j: i for i, j in enumerate(top_journal_keys)}

    flows_ak = [(author_index[a], kw_index[k], w) for (a, k), w in author_kw_cooccur.items()
                if a in author_index and k in kw_index]
    flows_kj = [(kw_index[k], journal_index[j], w) for (k, j), w in kw_journal_cooccur.items()
                if k in kw_index and j in journal_index]
    if not flows_ak or not flows_kj:
        return None, None, None, None, None

    authors = [{'label': author_display.get(a, a), 'size': author_flow_total[a]} for a in top_author_keys]
    keywords = [{'label': k, 'size': kw_counts[k]} for k in keywords_list]
    journals = [{'label': j[:40] + '…' if len(j) > 40 else j, 'size': journal_flow_total[j]}
                for j in top_journal_keys]

    return authors, keywords, journals, flows_ak, flows_kj


def three_field_plot(records: list[dict]):
    """
    Üç Alan Grafiği (B2-5): Yazar ↔ Anahtar Kelime ↔ Dergi arasında birlikte-geçme
    akışı, alüvyal/Sankey benzeri 3 sütunlu diyagram (bibliometrix 'Three Fields
    Plot' eşdeğeri). Çizim motoru `thematic_evolution()` ile aynı yapıdadır
    (`_sankey_ribbon()` paylaşılır) ama orada test edilen kodu bozmamak için
    ayrı tutulmuştur.
    """
    authors, keywords, journals, flows_ak, flows_kj = three_field_plot_data(records)
    if authors is None:
        return None

    col_items = [authors, keywords, journals]
    col_labels = [gettext('Yazarlar'), gettext('Anahtar Kelimeler'), gettext('Dergiler')]
    flows = [(0, a, k, w) for a, k, w in flows_ak] + [(1, k, j, w) for k, j, w in flows_kj]

    n_cols = 3
    col_totals = [sum(it['size'] for it in items) for items in col_items]
    max_total = max(col_totals)
    gap = max_total * 0.04
    # Sütun yüksekliği yalnız öğe büyüklükleri değil, aralarındaki boşlukları da
    # içermeli — yazar/dergi sütunlarında öğe sayısı (B2-4'teki dönem sayısından
    # farklı olarak) çift haneli olabiliyor, boşluklar toplamı max_total'ı aşıp
    # en alttaki kutuyu görünür alanın dışına itebiliyordu.
    canvas_height = max(total + max(0, len(items) - 1) * gap
                       for total, items in zip(col_totals, col_items))

    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_facecolor('#f8fafc')
    fig.patch.set_facecolor('white')

    col_x = [i * 2.6 for i in range(n_cols)]
    box_width = 0.5

    col_boxes = []
    col_colors = []
    for items in col_items:
        y = canvas_height
        boxes = []
        colors = []
        for idx, it in enumerate(items):
            y_top = y
            y_bot = y - it['size']
            boxes.append((y_top, y_bot))
            colors.append(PALETTE[idx % len(PALETTE)])
            y = y_bot - gap
        col_boxes.append(boxes)
        col_colors.append(colors)

    for i in range(n_cols - 1):
        out_cursor = [b[0] for b in col_boxes[i]]
        in_cursor = [b[0] for b in col_boxes[i + 1]]
        layer_flows = sorted((f for f in flows if f[0] == i), key=lambda f: (f[1], f[2]))
        for (_, a_idx, b_idx, w) in layer_flows:
            y0_top = out_cursor[a_idx]
            y0_bot = y0_top - w
            out_cursor[a_idx] = y0_bot
            y1_top = in_cursor[b_idx]
            y1_bot = y1_top - w
            in_cursor[b_idx] = y1_bot
            _sankey_ribbon(ax, col_x[i] + box_width / 2, col_x[i + 1] - box_width / 2,
                          y0_top, y0_bot, y1_top, y1_bot, color=col_colors[i][a_idx])

    for items, boxes, colors, x in zip(col_items, col_boxes, col_colors, col_x):
        for it, (y_top, y_bot), color in zip(items, boxes, colors):
            ax.add_patch(mpatches.Rectangle((x - box_width / 2, y_bot), box_width,
                                            y_top - y_bot, facecolor=color, alpha=0.85,
                                            edgecolor='white', linewidth=1.2, zorder=3))
            ax.annotate(it['label'], (x, (y_top + y_bot) / 2), ha='center', va='center',
                       fontsize=8, fontweight='bold', color='#1e293b', zorder=4)

    ax.set_xticks(col_x)
    ax.set_xticklabels(col_labels, fontsize=11, fontweight='bold')
    ax.set_xlim(col_x[0] - 1.8, col_x[-1] + 1.8)
    ax.set_ylim(-gap, canvas_height + gap)
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title(gettext('Üç Alan Grafiği (Yazar ↔ Anahtar Kelime ↔ Dergi)'))
    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 22. SCP/MCP (Ülke İşbirliği) ───────────────────────────

def scp_mcp_counts(records: list[dict]):
    """
    SCP/MCP hesabı (B2-6, bibliometrix 'Corresponding Author's Country' eşdeğeri):
    her kayıt, yazarlarının bulunduğu farklı ülke sayısına göre SCP (Single Country
    Publication — tek ülkeli) veya MCP (Multiple Country Publication — çok ülkeli
    işbirliği) olarak sınıflandırılır. Çok ülkeli bir yayın, o yayında adı geçen HER
    ülke için MCP olarak sayılır (ülke sayımındaki genel "tam sayım" kuralıyla
    tutarlı — bkz. `_record_countries()`).
    Döner: {ülke: {'scp': n, 'mcp': n}} ya da ülke bilgisi hiç yoksa None.
    """
    counts = defaultdict(lambda: {'scp': 0, 'mcp': 0})
    for r in records:
        countries = _record_countries(r)
        if len(countries) == 1:
            counts[countries[0]]['scp'] += 1
        elif len(countries) > 1:
            for c in countries:
                counts[c]['mcp'] += 1
    if not counts:
        return None
    return dict(counts)


def scp_mcp_chart(records: list[dict], n: int = 10):
    """
    SCP/MCP yığılmış çubuk grafiği (B2-6): en üretken top-N ülke, tek ülkeli (SCP)
    ve çok ülkeli işbirliği (MCP) yayın sayısına göre yığılmış yatay çubuklarla.
    """
    counts = scp_mcp_counts(records)
    if counts is None:
        return None

    ranked = sorted(counts.items(), key=lambda kv: kv[1]['scp'] + kv[1]['mcp'], reverse=True)[:n]
    if not ranked:
        return None

    countries = [c for c, _ in ranked]
    scp_vals = [v['scp'] for _, v in ranked]
    mcp_vals = [v['mcp'] for _, v in ranked]

    fig, ax = plt.subplots(figsize=(9, max(10, len(countries) * 0.75)))
    ax.set_facecolor('#f8fafc')
    fig.patch.set_facecolor('white')

    y_pos = range(len(countries))
    ax.barh(y_pos, scp_vals, color=PALETTE[0], alpha=0.9, height=0.7,
           edgecolor='white', linewidth=0.5, label=gettext('Tek Ülkeli (SCP)'), zorder=2)
    ax.barh(y_pos, mcp_vals, left=scp_vals, color=PALETTE[2], alpha=0.9, height=0.7,
           edgecolor='white', linewidth=0.5, label=gettext('Çok Ülkeli İşbirliği (MCP)'), zorder=2)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(countries, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel(gettext('Yayın Sayısı'), fontsize=12, labelpad=8)
    ax.set_title(gettext('Ülke İşbirliği: Tek Ülkeli ve Çok Ülkeli Yayınlar (SCP/MCP)'))
    ax.grid(axis='x', zorder=1)
    ax.legend(loc='lower right', fontsize=9, frameon=True, framealpha=0.95, edgecolor='#cbd5e0')

    for i, (s, m) in enumerate(zip(scp_vals, mcp_vals)):
        total = s + m
        if total > 0:
            ax.text(total + max(total * 0.01, 0.1), i, f'{total:,}',
                   ha='left', va='center', fontsize=9, color='#334155', fontweight='bold')

    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 23. Bibliyografik Eşleşme Ağı ───────────────────────────

def bibliographic_coupling(records: list[dict], min_shared: int = 2, max_nodes: int = 30):
    """
    Bibliyografik Eşleşme Ağı (B2-7, bibliometrix 'Bibliographic Coupling' eşdeğeri):
    iki yayın, aynı eserlere atıf yapıyorsa (referenced_works kesişimi) bağlanır;
    kenar ağırlığı paylaşılan referans sayısıdır. Yalnız referenced_works dolu
    kayıtlar (B1-1 OpenAlex zenginleştirmesinden geçmiş, DOI'li) katılır.
    """
    try:
        import networkx as nx
    except ImportError:
        logger.warning('networkx paketi yüklü değil')
        return None

    candidates = [r for r in records if r.get('referenced_works')]
    if len(candidates) < 2:
        return None

    # Her kayıt için kısa, benzersiz düğüm etiketi (aynı kısaltma 2. kez çıkarsa "(2)" eklenir)
    labels = []
    seen = Counter()
    for r in candidates:
        title = (r.get('title') or '').strip() or gettext('(başlıksız)')
        short = title[:45] + '…' if len(title) > 45 else title
        seen[short] += 1
        labels.append(f'{short} ({seen[short]})' if seen[short] > 1 else short)

    ref_sets = [set(r['referenced_works']) for r in candidates]

    coupling_count = Counter()
    for i in range(len(candidates)):
        for j in range(i + 1, len(candidates)):
            shared = len(ref_sets[i] & ref_sets[j])
            if shared > 0:
                coupling_count[(labels[i], labels[j])] = shared

    G = nx.Graph()
    for (l1, l2), w in coupling_count.items():
        if w >= min_shared:
            G.add_edge(l1, l2, weight=w)

    if G.number_of_nodes() == 0:
        for (l1, l2), w in coupling_count.most_common(40):
            G.add_edge(l1, l2, weight=w)

    if G.number_of_nodes() == 0:
        return None

    if G.number_of_nodes() > max_nodes:
        top_nodes = sorted(G.degree, key=lambda x: x[1], reverse=True)[:max_nodes]
        G = G.subgraph([n for n, _ in top_nodes]).copy()
        if G.number_of_nodes() == 0:
            return None

    degrees = dict(G.degree())
    max_deg = max(degrees.values()) if degrees else 1
    min_deg = min(degrees.values()) if degrees else 0
    span = (max_deg - min_deg) or 1

    node_colors = [plt.cm.viridis(0.15 + 0.7 * (degrees[n] - min_deg) / span)
                   for n in G.nodes()]
    node_sizes = [300 + degrees[n] * 130 for n in G.nodes()]
    edge_weights = [G[u][v].get('weight', 1) for u, v in G.edges()]

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_facecolor('#f8fafc')
    fig.patch.set_facecolor('white')

    pos = nx.spring_layout(G, seed=42, k=3.0)

    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.35,
                           width=[min(w * 0.6, 4.0) for w in edge_weights],
                           edge_color='#94a3b8')
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_sizes,
                           node_color=node_colors, alpha=0.9,
                           linewidths=0.8, edgecolors='white')

    degree_threshold = sorted(degrees.values(), reverse=True)[min(14, len(degrees) - 1)]
    label_dict = {n: n for n, d in degrees.items() if d >= degree_threshold}
    nx.draw_networkx_labels(G, pos, labels=label_dict, ax=ax,
                            font_size=7, font_color='#1e293b', font_weight='bold')

    sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis,
                               norm=plt.Normalize(vmin=min_deg, vmax=max_deg))
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label(gettext('Paylaşılan Referans Sayısı'), fontsize=10)

    ax.set_title(gettext('Bibliyografik Eşleşme Ağı (Paylaşılan Referanslar)'))
    ax.axis('off')
    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────── 24. Yerel / Küresel Atıf ───────────────────────────

def local_citation_counts(records: list[dict]):
    """
    Her openalex_id'li kayıt için "yerel atıf" sayısı (bu veri setindeki diğer
    kayıtlardan kaçının onu referenced_works üzerinden atıf yaptığı).
    Döner: {openalex_id: yerel_atıf_sayısı} (hiç iç atıf yoksa None).
    """
    own_ids = {r['openalex_id']: r for r in records if r.get('openalex_id')}
    if len(own_ids) < 2:
        return None

    local_count = Counter()
    for r in records:
        for ref in (r.get('referenced_works') or []):
            if ref in own_ids:
                local_count[ref] += 1

    if not local_count:
        return None
    return dict(local_count)


def local_global_citations(records: list[dict], n: int = 15):
    """
    Yerel Atıf vs Küresel Atıf (B2-7, bibliometrix 'Local Citations' eşdeğeri):
    "küresel atıf" (cited_by) yayının OpenAlex genelindeki toplam atıf sayısıdır;
    "yerel atıf" yalnız BU veri setindeki diğer kayıtlardan kaçının ona
    referenced_works üzerinden atıf yaptığıdır (derlemenin kendi iç etkisi).
    Yalnız openalex_id'si olan (B1-1 zenginleştirmesinden geçmiş) kayıtlar için
    hesaplanabilir.
    """
    local_count = local_citation_counts(records)
    if local_count is None:
        return None

    own_ids = {r['openalex_id']: r for r in records if r.get('openalex_id')}
    ranked = sorted(local_count.items(), key=lambda kv: kv[1], reverse=True)[:n]

    titles, local_vals, global_vals = [], [], []
    for oid, local in ranked:
        rec = own_ids[oid]
        title = (rec.get('title') or '').strip() or gettext('(başlıksız)')
        titles.append(title[:45] + '…' if len(title) > 45 else title)
        local_vals.append(local)
        global_vals.append(rec.get('cited_by') or 0)

    # Küresel atıf (tüm literatür) her zaman yerel atıftan (bu küçük veri setindeki iç
    # atıf) çok daha büyük olabilir — aynı eksende çift çubuk yerel çubuğu görünmez
    # kılardı; bu yüzden sıralama yerel atfa göre, küresel sayı her çubuğun yanında
    # metin olarak gösterilir (ölçek farkından bağımsız, her ikisi de okunabilir).
    fig, ax = plt.subplots(figsize=(10, max(10, len(titles) * 0.8)))
    ax.set_facecolor('#f8fafc')
    fig.patch.set_facecolor('white')

    y_pos = list(range(len(titles)))
    bars = ax.barh(y_pos, local_vals, color=PALETTE[2], alpha=0.9, height=0.7,
                   edgecolor='white', linewidth=0.5, zorder=2)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(titles, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel(gettext('Yerel Atıf Sayısı (Bu Veri Setinde)'), fontsize=12, labelpad=8)
    ax.set_title(gettext('En Çok Yerel Atıf Alan Yayınlar (Top {n})').format(n=len(titles)))
    ax.grid(axis='x', zorder=1)

    max_local = max(local_vals) or 1
    label_tmpl = gettext('{local} yerel · {glob} küresel atıf')
    for bar, local, glob in zip(bars, local_vals, global_vals):
        ax.text(bar.get_width() + max_local * 0.02, bar.get_y() + bar.get_height() / 2,
               label_tmpl.format(local=f'{local:,}', glob=f'{glob:,}'),
               ha='left', va='center', fontsize=8.5, color='#334155', fontweight='bold')

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
