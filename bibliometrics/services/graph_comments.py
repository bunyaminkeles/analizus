"""
Grafik başına kural tabanlı otomatik yorum cümlesi (B3-4, Faz B3).
Her cümle, ilgili grafiğin kendi sayılarından üretilir — LLM kullanılmaz, bu yüzden
grafikle çelişme riski yoktur. Zaten ayrılmış saf hesap fonksiyonları (bradford_zones,
keyword_clusters, thematic_map_themes, research_gap_points, topic_map_topics,
thematic_evolution_themes, three_field_plot_data, scp_mcp_counts, local_citation_counts,
_author_collaboration_graph, _country_collaboration_graph, _bibliographic_coupling_graph,
_group_authors, _last_complete_year, pub_type_labels) burada da kullanılır; grafik çizen
fonksiyonların kendisine dokunulmaz.

Her fonksiyon `(records, context=None)` imzasına uyar — `context` şimdilik yalnız
{'topic_data': (topics, assignments)} taşır (NMF konu modellemesi run_all_analyses'te
bir kez hesaplanıp iki grafikte de kullanılıyor — yorum da aynı hesabı tekrar üretmesin
diye paylaşılır).
"""
from collections import Counter, defaultdict

from django.utils.formats import number_format
from django.utils.translation import gettext
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from bibliometrics.services.analyzer import (
    _author_collaboration_graph,
    _bibliographic_coupling_graph,
    _country_collaboration_graph,
    _group_authors,
    _last_complete_year,
    _record_countries,
    _record_institutions,
    bradford_zones,
    keyword_clusters,
    local_citation_counts,
    normalize_abstract_words,
    normalize_keywords,
    pub_type_labels,
    research_gap_points,
    scp_mcp_counts,
    thematic_evolution_themes,
    thematic_map_themes,
    three_field_plot_data,
    topic_map_topics,
    topic_modeling_data,
)


def comment_publication_trend(records: list[dict], context: dict = None) -> str | None:
    years = [r['year'] for r in records if r.get('year') and 1900 < r['year'] <= _last_complete_year()]
    if not years:
        return None
    counter = Counter(years)
    peak_year, peak_count = counter.most_common(1)[0]
    return gettext(
        'Yayınlar {start}-{end} yılları arasında toplam {total} adet; en yoğun yıl '
        '{peak_year} olup bu yılda {peak_count} yayın yapılmış.'
    ).format(start=min(years), end=max(years), total=number_format(len(years), force_grouping=True),
             peak_year=peak_year, peak_count=number_format(peak_count, force_grouping=True))


def comment_publication_growth_rate(records: list[dict], context: dict = None) -> str | None:
    years = [r['year'] for r in records if r.get('year') and 1900 < r['year'] <= _last_complete_year()]
    if not years:
        return None
    counter = Counter(years)
    sorted_years = sorted(counter.keys())
    if len(sorted_years) < 3:
        return None
    sorted_years = list(range(sorted_years[0], sorted_years[-1] + 1))
    counts = [counter.get(y, 0) for y in sorted_years]
    n = sorted_years[-1] - sorted_years[0]
    cagr = ((counts[-1] / counts[0]) ** (1 / n) - 1) * 100 if n > 0 and counts[0] > 0 else 0
    return gettext(
        '{start}-{end} arasında yıllık bileşik büyüme oranı (CAGR) {cagr}.'
    ).format(start=sorted_years[0], end=sorted_years[-1], cagr=f'{cagr:+.1f}%')


def comment_top_authors(records: list[dict], context: dict = None) -> str | None:
    counts, display = _group_authors(records)
    if not counts:
        return None
    key, count = counts.most_common(1)[0]
    total = len(records)
    pct = round(100 * count / total) if total else 0
    return gettext(
        'En üretken yazar {name}, {count} yayınla ({total} yayının %{pct} payıyla) '
        'listenin başında.'
    ).format(name=display[key], count=number_format(count, force_grouping=True),
             total=number_format(total, force_grouping=True), pct=pct)


def comment_lotka_law(records: list[dict], context: dict = None) -> str | None:
    author_count, _ = _group_authors(records)
    if not author_count:
        return None
    prod_dist = Counter(author_count.values())
    total_authors = len(author_count)
    single_pct = round(100 * prod_dist.get(1, 0) / total_authors) if total_authors else 0
    return gettext(
        'Toplam {total} farklı yazarın %{pct} payı yalnızca 1 yayın yapmış.'
    ).format(total=number_format(total_authors, force_grouping=True), pct=single_pct)


def comment_keyword_cloud(records: list[dict], context: dict = None) -> str | None:
    all_kw = Counter()
    for r in records:
        all_kw.update(normalize_keywords(r.get('keywords', [])))
        all_kw.update(normalize_abstract_words(r.get('abstract', '')))
    if not all_kw:
        return None
    # normalize_abstract_words yalnız TR stopword filtreler — İngilizce özetlerde
    # "this"/"that" gibi kelimeler sızabilir (keyword_cloud() grafiğinde de aynı
    # kısıt var, orada bir balon arasında kayboluyor; tek cümlelik yorumda ise göze
    # çarpıyor). sklearn zaten requirements'ta (topic_modeling_data) — ek paket yok.
    filtered = {k: v for k, v in all_kw.items() if k not in ENGLISH_STOP_WORDS} or all_kw
    kw, count = Counter(filtered).most_common(1)[0]
    return gettext(
        'En sık geçen terim "{kw}" olup {count} kez kullanılmış.'
    ).format(kw=kw, count=number_format(count, force_grouping=True))


def comment_keyword_cooccurrence(records: list[dict], context: dict = None) -> str | None:
    G, communities, all_kw = keyword_clusters(records)
    if G is None:
        return None
    largest = communities[0]
    terms = sorted(largest, key=lambda n: all_kw.get(n, 0), reverse=True)[:3]
    return gettext(
        'Anahtar kelime ağı {n_clusters} kümeye ayrıldı; en büyük küme ({size} kelime) '
        'şu terimlerde yoğunlaşıyor: {terms}.'
    ).format(n_clusters=len(communities), size=len(largest), terms=', '.join(terms))


def comment_keyword_trend(records: list[dict], context: dict = None) -> str | None:
    all_kw = Counter()
    for r in records:
        all_kw.update(normalize_keywords(r.get('keywords', [])))
    if not all_kw:
        return None
    kw, count = all_kw.most_common(1)[0]
    return gettext(
        'En sık geçen anahtar kelime "{kw}" olup {count} kez kullanılmış.'
    ).format(kw=kw, count=number_format(count, force_grouping=True))


def comment_top_cited(records: list[dict], context: dict = None) -> str | None:
    with_citations = [(r.get('title'), r['cited_by']) for r in records
                      if r.get('cited_by', 0) > 0 and r.get('title')]
    if not with_citations:
        return None
    title, count = max(with_citations, key=lambda x: x[1])
    short = title[:65] + '…' if len(title) > 65 else title
    return gettext(
        'En çok atıf alan yayın "{title}" olup {count} atıf almış.'
    ).format(title=short, count=number_format(count, force_grouping=True))


def comment_top_journals(records: list[dict], context: dict = None) -> str | None:
    journals = [r['journal'].strip() for r in records if r.get('journal', '').strip()]
    if not journals:
        return None
    name, count = Counter(journals).most_common(1)[0]
    return gettext(
        'En çok yayının yapıldığı dergi/kaynak {name} olup {count} yayınla öne çıkıyor.'
    ).format(name=name, count=number_format(count, force_grouping=True))


def comment_top_institutions(records: list[dict], context: dict = None) -> str | None:
    country_counter = Counter()
    inst_counter = Counter()
    for r in records:
        for c in _record_countries(r):
            country_counter[c] += 1
        for inst in _record_institutions(r):
            inst_counter[inst] += 1
    if country_counter:
        name, count = country_counter.most_common(1)[0]
        return gettext(
            'En çok yayının geldiği ülke {name} olup {count} yayınla öne çıkıyor.'
        ).format(name=name, count=number_format(count, force_grouping=True))
    if inst_counter:
        name, count = inst_counter.most_common(1)[0]
        return gettext(
            'En çok yayının geldiği kurum {name} olup {count} yayınla öne çıkıyor.'
        ).format(name=name, count=number_format(count, force_grouping=True))
    return None


def comment_country_collaboration(records: list[dict], context: dict = None) -> str | None:
    G = _country_collaboration_graph(records)
    if G is None:
        return None
    degrees = dict(G.degree())
    top_country = max(degrees, key=degrees.get)
    return gettext(
        'İşbirliği ağı {n_countries} ülke ve {n_edges} bağlantıdan oluşuyor; en çok işbirliği '
        'yapılan ülke {country} ({degree} ülkeyle bağlantılı).'
    ).format(n_countries=G.number_of_nodes(), n_edges=G.number_of_edges(),
             country=top_country, degree=degrees[top_country])


def comment_author_collaboration(records: list[dict], context: dict = None) -> str | None:
    G = _author_collaboration_graph(records)
    if G is None:
        return None
    degrees = dict(G.degree())
    top_author = max(degrees, key=degrees.get)
    return gettext(
        'İşbirliği ağı {n_authors} yazar ve {n_edges} bağlantıdan oluşuyor; en çok işbirliği '
        'yapan yazar {author} ({degree} farklı yazarla ortak yayını var).'
    ).format(n_authors=G.number_of_nodes(), n_edges=G.number_of_edges(),
             author=top_author, degree=degrees[top_author])


def comment_publication_types(records: list[dict], context: dict = None) -> str | None:
    types = [r.get('pub_type', '').strip().lower() for r in records if r.get('pub_type', '').strip()]
    if not types:
        return None
    labels = pub_type_labels()
    translated = [labels.get(t, t.title()) for t in types]
    name, count = Counter(translated).most_common(1)[0]
    pct = round(100 * count / len(types)) if types else 0
    return gettext(
        'En yaygın yayın türü {name}, yayınların %{pct} payını oluşturuyor.'
    ).format(name=name, pct=pct)


def comment_citation_analysis(records: list[dict], context: dict = None) -> str | None:
    citations = sorted([r.get('cited_by', 0) for r in records if r.get('cited_by', 0) > 0], reverse=True)
    if not citations:
        return None
    h = sum(c >= (i + 1) for i, c in enumerate(citations))
    total_cit = sum(r.get('cited_by') or 0 for r in records)
    avg = total_cit / len(records) if records else 0
    return gettext(
        'H-index değeri {h}; toplam {total} atıf, yayın başına ortalama {avg} atıf.'
    ).format(h=h, total=number_format(total_cit, force_grouping=True), avg=number_format(avg, 1))


def comment_annual_citation_trend(records: list[dict], context: dict = None) -> str | None:
    year_citations = defaultdict(list)
    for r in records:
        if r.get('year') and 1900 < r['year'] <= _last_complete_year():
            year_citations[r['year']].append(r.get('cited_by') or 0)
    if not any(sum(v) for v in year_citations.values()):
        return None
    sorted_years = sorted(year_citations.keys())
    total_per_year = [sum(year_citations[y]) for y in sorted_years]
    peak_idx = total_per_year.index(max(total_per_year))
    return gettext(
        'Toplam atıf en yüksek {year} yılında gerçekleşmiş ({count} atıf).'
    ).format(year=sorted_years[peak_idx],
             count=number_format(total_per_year[peak_idx], force_grouping=True))


def comment_topic_map(records: list[dict], context: dict = None) -> str | None:
    topic_data = topic_map_topics(records)
    if topic_data is None:
        return None
    top = topic_data[0]
    terms = ', '.join(top['keywords'][:3])
    return gettext(
        'Araştırma konuları {n} kümeye ayrıldı; en büyük küme ({n_kw} anahtar kelime) şu '
        'terimlerde yoğunlaşıyor: {terms}.'
    ).format(n=len(topic_data), n_kw=top['n_kw'], terms=terms)


def comment_research_gap(records: list[dict], context: dict = None) -> str | None:
    points, med_trend, med_impact = research_gap_points(records)
    if points is None:
        return None
    gap_kws = [p['kw'] for p in points if p['trend'] < med_trend and p['impact_norm'] >= med_impact]
    if not gap_kws:
        return None
    return gettext(
        '{n} anahtar kelime "Research Gap" bölgesinde (azalan ilgi + yüksek atıf etkisi): {terms}.'
    ).format(n=len(gap_kws), terms=', '.join(gap_kws[:5]))


def comment_bradford_law(records: list[dict], context: dict = None) -> str | None:
    zones, zone_totals = bradford_zones(records)
    if zones is None:
        return None
    total = sum(zone_totals)
    pct = round(100 * zone_totals[0] / total) if total else 0
    return gettext(
        'Bölge 1, {n} çekirdek dergiyle toplam {total} yayının %{pct} payını oluşturuyor.'
    ).format(n=number_format(len(zones[0]), force_grouping=True),
             total=number_format(total, force_grouping=True), pct=pct)


def comment_thematic_map(records: list[dict], context: dict = None) -> str | None:
    themes, mean_c, mean_d = thematic_map_themes(records)
    if themes is None:
        return None
    dominant = max(themes, key=lambda t: t['weight'])
    high_c = dominant['centrality'] >= mean_c
    high_d = dominant['density'] >= mean_d
    if high_c and high_d:
        text = gettext('En baskın tema "{label}", yüksek merkeziyet ve yoğunlukla Motor '
                       'Temalar bölgesinde yer alıyor.')
    elif not high_c and high_d:
        text = gettext('En baskın tema "{label}", düşük merkeziyet fakat yüksek '
                       'yoğunlukla Niş Temalar bölgesinde yer alıyor.')
    elif high_c and not high_d:
        text = gettext('En baskın tema "{label}", yüksek merkeziyet fakat düşük '
                       'yoğunlukla Temel Temalar bölgesinde yer alıyor.')
    else:
        text = gettext('En baskın tema "{label}", düşük merkeziyet ve yoğunlukla '
                       'Gelişen veya Azalan Temalar bölgesinde yer alıyor.')
    return text.format(label=dominant['label'])


def comment_thematic_evolution(records: list[dict], context: dict = None) -> str | None:
    period_labels, period_themes, flows = thematic_evolution_themes(records)
    if period_labels is None:
        return None
    period_i, a_idx, b_idx, shared = max(flows, key=lambda f: f[3])
    label_from = period_themes[period_i][a_idx]['label']
    label_to = period_themes[period_i + 1][b_idx]['label']
    return gettext(
        '{p_from} döneminden {p_to} dönemine en güçlü tema akışı: "{from_label}" → '
        '"{to_label}" ({n} ortak anahtar kelime).'
    ).format(p_from=period_labels[period_i], p_to=period_labels[period_i + 1],
             from_label=label_from, to_label=label_to, n=shared)


def comment_three_field_plot(records: list[dict], context: dict = None) -> str | None:
    authors, keywords, journals, flows_ak, flows_kj = three_field_plot_data(records)
    if authors is None:
        return None
    return gettext(
        'En baskın bağlantı: yazar {author}, anahtar kelime "{kw}" ve dergi {journal} arasında.'
    ).format(author=authors[0]['label'], kw=keywords[0]['label'], journal=journals[0]['label'])


def comment_scp_mcp(records: list[dict], context: dict = None) -> str | None:
    counts = scp_mcp_counts(records)
    if counts is None:
        return None
    ranked = sorted(counts.items(), key=lambda kv: kv[1]['scp'] + kv[1]['mcp'], reverse=True)
    if not ranked:
        return None
    country, v = ranked[0]
    return gettext(
        'En üretken ülke {country}: {scp} tek ülkeli (SCP), {mcp} çok ülkeli işbirliği '
        '(MCP) yayını var.'
    ).format(country=country, scp=number_format(v['scp'], force_grouping=True),
             mcp=number_format(v['mcp'], force_grouping=True))


def comment_bibliographic_coupling(records: list[dict], context: dict = None) -> str | None:
    G = _bibliographic_coupling_graph(records)
    if G is None:
        return None
    degrees = dict(G.degree())
    top_node = max(degrees, key=degrees.get)
    return gettext(
        'Ağ {n} yayın ve {e} eşleşmeden oluşuyor; en çok paylaşılan referansa sahip yayın '
        '{node} ({degree} yayınla bağlantılı).'
    ).format(n=G.number_of_nodes(), e=G.number_of_edges(), node=top_node, degree=degrees[top_node])


def comment_local_global_citations(records: list[dict], context: dict = None) -> str | None:
    local_count = local_citation_counts(records)
    if local_count is None:
        return None
    own_ids = {r['openalex_id']: r for r in records if r.get('openalex_id')}
    oid, local = max(local_count.items(), key=lambda kv: kv[1])
    rec = own_ids[oid]
    title = (rec.get('title') or '').strip() or gettext('(başlıksız)')
    short = title[:65] + '…' if len(title) > 65 else title
    glob = rec.get('cited_by') or 0
    return gettext(
        'En çok yerel atıf alan yayın "{title}" olup bu veri setinde {local} yerel, '
        'genelde {glob} küresel atıf almış.'
    ).format(title=short, local=number_format(local, force_grouping=True),
             glob=number_format(glob, force_grouping=True))


def _topic_modeling_context_data(records: list[dict], context: dict = None):
    cached = (context or {}).get('topic_data')
    return cached if cached is not None else topic_modeling_data(records)


def comment_topic_modeling_words(records: list[dict], context: dict = None) -> str | None:
    topics, _assignments = _topic_modeling_context_data(records, context)
    if topics is None:
        return None
    dominant = max(topics, key=lambda t: t['size'])
    terms = ', '.join(dominant['words'][:3])
    return gettext(
        'Konu modellemesi (NMF) {n} konu buldu; en büyük konu ({size} kayıt) şu '
        'kelimelerle öne çıkıyor: {terms}.'
    ).format(n=len(topics), size=dominant['size'], terms=terms)


def comment_topic_modeling_trend(records: list[dict], context: dict = None) -> str | None:
    topics, assignments = _topic_modeling_context_data(records, context)
    if topics is None:
        return None
    years = [y for y, _ in assignments if y and 1900 < y <= _last_complete_year()]
    if len(set(years)) < 2:
        return None
    dominant = max(topics, key=lambda t: t['size'])
    terms = ', '.join(dominant['words'][:3])
    return gettext(
        '{start}-{end} yılları arasında en sık görülen konu ({terms}) toplam {size} '
        'kayıtta baskın.'
    ).format(start=min(years), end=max(years), terms=terms, size=dominant['size'])


# (başlık TR msgid → yorum fonksiyonu) — başlıklar run_all_analyses'teki `analyses`
# listesinin TR kaynak metinleriyle birebir aynı olmalı.
_COMMENT_BUILDERS_TR = {
    'Yıllara Göre Yayın Trendi': comment_publication_trend,
    'Yıllık Büyüme Oranı': comment_publication_growth_rate,
    'En Verimli Yazarlar (Top 15)': comment_top_authors,
    'Lotka Kanunu — Yazar Üretkenliği': comment_lotka_law,
    'Anahtar Kelime Bulutu': comment_keyword_cloud,
    'Anahtar Kelime Eş-Oluşum Ağı': comment_keyword_cooccurrence,
    'Anahtar Kelime Zaman Trendi': comment_keyword_trend,
    'En Çok Atıf Alan Yayınlar (Top 10)': comment_top_cited,
    'En Çok Yayın Yapılan Dergiler': comment_top_journals,
    'Kurum / Ülke Dağılımı (Top 10)': comment_top_institutions,
    'Ülke İşbirliği Ağı': comment_country_collaboration,
    'Yazar İşbirliği Ağı': comment_author_collaboration,
    'Yayın Türleri Dağılımı': comment_publication_types,
    'Atıf Analizi ve H-index': comment_citation_analysis,
    'Yıllık Atıf Trendi': comment_annual_citation_trend,
    'Araştırma Konusu Kümeleri (Topic Map)': comment_topic_map,
    'Araştırma Boşluğu Haritası (Research Gap)': comment_research_gap,
    'Bradford Kanunu — Çekirdek Dergi Bölgeleri': comment_bradford_law,
    'Tematik Harita (Callon Merkeziyet × Yoğunluk)': comment_thematic_map,
    'Tematik Evrim (Dönemler Arası Tema Akışı)': comment_thematic_evolution,
    'Üç Alan Grafiği (Yazar ↔ Anahtar Kelime ↔ Dergi)': comment_three_field_plot,
    'Ülke İşbirliği: Tek Ülkeli ve Çok Ülkeli Yayınlar (SCP/MCP)': comment_scp_mcp,
    'Bibliyografik Eşleşme Ağı (Paylaşılan Referanslar)': comment_bibliographic_coupling,
    'Yerel Atıf ve Küresel Atıf Karşılaştırması': comment_local_global_citations,
    'Konu Modelleme (NMF) — Konu Başına En Belirleyici Kelimeler': comment_topic_modeling_words,
    'Konulara Göre Yıllık Yayın Payı (NMF)': comment_topic_modeling_trend,
}


def comment_builders() -> dict:
    """Analiz başlığı (aktif dile çevrilmiş) → yorum fonksiyonu eşlemesi.
    Anahtarlar burada da gettext() ile aktif dile çevrilir — run_all_analyses'teki
    `citation_based` kümesiyle aynı desen (analyzer.py)."""
    return {gettext(title_tr): fn for title_tr, fn in _COMMENT_BUILDERS_TR.items()}
