"""
Bibliometri grafik üretimi için regresyon testleri.
Kapsam: yıl ekseni tam sayı tick'leri (A5), kısa dönem uyarısı (A6),
OpenAlex/PubMed TXT yeniden-yükleme (A7), demo CTA dil ayrımı (A8/A9),
rapor dili seçimi (A4).
"""
import matplotlib
matplotlib.use('Agg')

import pytest
from django.contrib.auth.models import User
from django.utils import translation

from forum.models import Profile

from bibliometrics.services.analyzer import (
    publication_trend,
    annual_citation_trend,
    publication_growth_rate,
    SHORT_SERIES_YEARS,
    canonical_author_key,
    _group_authors,
    top_authors,
    lotka_law,
    author_collaboration,
    normalize_keywords,
    _simple_depluralize,
    bradford_zones,
    bradford_law,
    keyword_clusters,
    keyword_cooccurrence,
    thematic_map_themes,
    thematic_map,
)
import bibliometrics.services.analyzer as analyzer_module
from bibliometrics.services.report_notes import build_report_notes
from bibliometrics.services.parser import (
    parse_openalex_txt, parse_pubmed_txt, detect_format, parse_file,
    _deduplicate_and_filter, _normalize_title_key,
)
from bibliometrics.services.pdf_builder import _demo_cta_text
from bibliometrics.models import BibliometricJob
from bibliometrics.services.job_runner import _in_user_language
from bibliometrics.services.enrichment import enrich_records_with_openalex, _apply_enrichment
from forum.models import SiteSettings
from openalex.services.scraper import OpenAlexScraper


def _records(years_counts):
    recs = []
    for year, count in years_counts.items():
        for _ in range(count):
            recs.append({'year': year, 'cited_by': 3})
    return recs


def _assert_integer_xticks(fig):
    ax = fig.axes[0]
    ticks = ax.get_xticks()
    assert len(ticks) > 0
    assert all(float(t).is_integer() for t in ticks)


def test_publication_trend_integer_ticks_short_series():
    fig = publication_trend(_records({2021: 5, 2022: 8, 2023: 12}))
    _assert_integer_xticks(fig)


def test_publication_trend_integer_ticks_long_series():
    fig = publication_trend(_records({y: (y % 7 + 2) for y in range(2004, 2024)}))
    _assert_integer_xticks(fig)


def test_annual_citation_trend_integer_ticks_short_series():
    fig = annual_citation_trend(_records({2021: 5, 2022: 8, 2023: 12}))
    _assert_integer_xticks(fig)


def test_publication_growth_rate_integer_ticks_short_series():
    fig = publication_growth_rate(_records({2021: 5, 2022: 8, 2023: 12}))
    _assert_integer_xticks(fig)


def test_publication_growth_rate_integer_ticks_long_series():
    fig = publication_growth_rate(_records({y: (y % 7 + 2) for y in range(2004, 2024)}))
    _assert_integer_xticks(fig)


def test_short_series_warning_shown_on_chart_and_notes():
    recs = _records({2021: 5, 2022: 8, 2023: 12})
    fig = publication_growth_rate(recs)
    chart_text = ' '.join(t.get_text() for t in fig.axes[0].texts)
    assert 'küçük taban etkisine açıktır' in chart_text
    notes = build_report_notes(recs)
    assert any('küçük taban etkisine açıktır' in l for l in notes['limitations'])


def test_long_series_no_short_series_warning():
    recs = _records({y: 5 for y in range(2018, 2018 + SHORT_SERIES_YEARS + 1)})
    fig = publication_growth_rate(recs)
    chart_text = ' '.join(t.get_text() for t in fig.axes[0].texts)
    assert 'küçük taban etkisine açıktır' not in chart_text
    notes = build_report_notes(recs)
    assert not any('küçük taban etkisine açıktır' in l for l in notes['limitations'])


class _StubJob:
    """openalex/pubmed job_runner'ın _generate_*_results_txt'inin ihtiyaç duyduğu
    minimum arayüz — DB'ye bağımlı olmadan üretici+ayrıştırıcıyı uçtan uca test eder."""
    total_results = 1

    def get_query_summary(self):
        return 'test sorgusu'


def test_parse_openalex_txt_roundtrip_with_real_generator():
    """Üretici (job_runner._generate_alex_results_txt) ile ayrıştırıcı (parse_openalex_txt)
    birbirinden kopmasın diye uçtan uca test — A7'de bulunan kök neden: üretici etiket
    hizasını dinamik (ljust) hesaplıyor, ayrıştırıcı sabit genişlik varsayıyordu."""
    from openalex.services.job_runner import _generate_alex_results_txt
    pub = {
        'title': 'Test Başlık Yazısı',
        'authors': 'Ahmet Yılmaz, Mehmet Demir',
        'journal': 'Test Dergisi',
        'year': 2024,
        'doi': 'https://doi.org/10.1234/test',
        'type': 'article',
        'cited_by_count': 5,
        'institutions': 'İstanbul Üniversitesi',
        'keywords': ['anahtar bir', 'anahtar iki', 'anahtar üç'],
    }
    txt = _generate_alex_results_txt([pub], _StubJob())
    recs = parse_openalex_txt(txt)
    assert len(recs) == 1
    r = recs[0]
    assert r['title'] == 'Test Başlık Yazısı'
    assert r['year'] == 2024
    assert r['journal'] == 'Test Dergisi'
    assert r['keywords'] == ['anahtar bir', 'anahtar iki', 'anahtar üç']
    assert len(r['authors']) == 2


def test_parse_pubmed_txt_robust_to_label_width_drift():
    """Gelecekte etiket uzunluğu (ve dolayısıyla üreticinin ljust genişliği) değişse bile
    ayrıştırıcı kırılmamalı — sabit genişlik varsayımı yerine regex kullanılıyor."""
    content = (
        '--- Yayın #1 ---\n'
        'Başlık : Test Makale\n'
        'Yazarlar : Ahmet Yılmaz\n'
        'Yıl : 2023\n'
        'Anahtar Kelimeler : test, örnek\n'
    )
    recs = parse_pubmed_txt(content)
    assert len(recs) == 1
    assert recs[0]['title'] == 'Test Makale'
    assert recs[0]['year'] == 2023
    assert recs[0]['keywords'] == ['test', 'örnek']


def test_demo_cta_tr_has_no_proje_talebi_link():
    """TR: sipariş sistemi var, proje talebi linkine yönlendirilmemeli (A8)."""
    with translation.override('tr'):
        text = _demo_cta_text()
    assert 'proje-talebi' not in text
    assert 'analizus.com' in text


def test_demo_cta_en_de_link_to_proje_talebi_with_language_prefix():
    """EN/DE: sipariş sistemi yok, proje talebine (dil önekiyle) yönlendirilmeli (A8)."""
    with translation.override('en'):
        en_text = _demo_cta_text()
    with translation.override('de'):
        de_text = _demo_cta_text()
    assert '/en/proje-talebi/' in en_text
    assert '/de/proje-talebi/' in de_text
    assert en_text != de_text


@pytest.mark.django_db
def test_report_language_overrides_profile_language():
    """job.report_language doluysa profil/arayüz dilinden bağımsız zorlanır (A4)."""
    user = User.objects.create_user(username='testrptlang', password='x', email='t@example.com')
    Profile.objects.create(user=user, preferred_language='tr')

    job_en = BibliometricJob.objects.create(user=user, report_language='en')
    seen = {}
    _in_user_language(str(job_en.id), lambda job_id: seen.update(lang=translation.get_language()))
    assert seen['lang'] == 'en'


@pytest.mark.django_db
def test_report_language_blank_falls_back_to_profile_language():
    """job.report_language boşsa mevcut davranış (profil dili) korunur (A4)."""
    user = User.objects.create_user(username='testrptlang2', password='x', email='t2@example.com')
    Profile.objects.create(user=user, preferred_language='tr')

    job_default = BibliometricJob.objects.create(user=user, report_language='')
    seen = {}
    _in_user_language(str(job_default.id), lambda job_id: seen.update(lang=translation.get_language()))
    assert seen['lang'] == 'tr'


OPENALEX_WEB_CSV_SAMPLE = (
    'Title,Author,Year,Citation count,Open access,Abstract\n'
    '"Test Başlık, Virgüllü",Ahmet Yılmaz|Mehmet Demir,2023,5,Open Access,"Test özeti."\n'
    'İkinci Başlık,Ayşe Kaya,2023,0,NOT Open Access,\n'
)


def test_detect_format_openalex_web_csv():
    """openalex.org'un gerçek 'Export CSV' formatı (A7) — dergi/DOI/kurum/ülke/
    anahtar kelime hiç yok, yazarlar '|' ile ayrılmış."""
    assert detect_format(OPENALEX_WEB_CSV_SAMPLE) == 'csv_openalex'


def test_parse_openalex_csv_splits_pipe_separated_authors():
    recs, fmt = parse_file(OPENALEX_WEB_CSV_SAMPLE)
    assert fmt == 'csv_openalex'
    assert len(recs) == 2
    rec = next(r for r in recs if 'Virgüllü' in r['title'])
    assert rec['authors'] == ['Ahmet Yılmaz', 'Mehmet Demir']
    assert rec['year'] == 2023
    assert rec['cited_by'] == 5
    assert rec['abstract'] == 'Test özeti.'
    # Bu formatta hiç olmayan alanlar boş kalmalı
    assert rec['journal'] == ''
    assert rec['doi'] == ''


def _fake_work(doi, cited_by=7, country='US', institution='MIT', keywords=('deep learning',),
                referenced_works=('https://openalex.org/W1',), author_id='https://openalex.org/A1'):
    return {
        'doi': f'https://doi.org/{doi}',
        'cited_by_count': cited_by,
        'keywords': [{'display_name': k} for k in keywords],
        'concepts': [],
        'referenced_works': list(referenced_works),
        'authorships': [{
            'author': {'id': author_id},
            'institutions': [{'display_name': institution}],
            'countries': [country],
        }],
    }


def test_apply_enrichment_fills_missing_fields_only():
    """Boş alanlar OpenAlex verisiyle doldurulur; dolu alanlara (kullanıcının kendi verisi) dokunulmaz."""
    rec = {'doi': '10.1/x', 'cited_by': 0, 'country': '', 'institution': '', 'keywords': []}
    work = _fake_work('10.1/x')
    _apply_enrichment(rec, work)
    assert rec['cited_by'] == 7
    assert rec['country'] == 'US'
    assert rec['institution'] == 'MIT'
    assert rec['keywords'] == ['deep learning']
    assert rec['referenced_works'] == ['https://openalex.org/W1']
    assert rec['author_ids'] == ['https://openalex.org/A1']


def test_apply_enrichment_does_not_overwrite_existing_values():
    rec = {'doi': '10.1/x', 'cited_by': 99, 'country': 'TR', 'institution': 'ODTÜ', 'keywords': ['mevcut']}
    _apply_enrichment(rec, _fake_work('10.1/x'))
    assert rec['cited_by'] == 99
    assert rec['country'] == 'TR'
    assert rec['institution'] == 'ODTÜ'
    assert rec['keywords'] == ['mevcut']
    # Yeni alanlar (başka yerde doldurulmuyor) yine de güncellenir
    assert rec['referenced_works'] == ['https://openalex.org/W1']


@pytest.mark.django_db
def test_enrich_records_skips_records_without_doi(monkeypatch):
    called = {}

    def fake_fetch(self, dois):
        called['dois'] = dois
        return {d.lower(): _fake_work(d) for d in dois}

    monkeypatch.setattr(OpenAlexScraper, 'fetch_works_by_dois', fake_fetch)

    records = [
        {'doi': '10.1/a', 'cited_by': 0, 'country': '', 'institution': '', 'keywords': []},
        {'doi': '', 'cited_by': 0, 'country': '', 'institution': '', 'keywords': []},
    ]
    stats = {}
    enrich_records_with_openalex(records, stats)

    assert stats['zenginlestirme_skipped_no_doi'] == 1
    assert stats['zenginlestirme_enriched'] == 1
    assert called['dois'] == ['10.1/a']
    assert records[0]['cited_by'] == 7
    assert records[1]['cited_by'] == 0  # DOI'siz kayıt dokunulmadan kaldı


@pytest.mark.django_db
def test_enrich_records_respects_max_kayit_limit(monkeypatch):
    settings_obj = SiteSettings.load()
    settings_obj.bibliometri_openalex_zenginlestirme_max_kayit = 1
    settings_obj.save(update_fields=['bibliometri_openalex_zenginlestirme_max_kayit'])

    called = {}

    def fake_fetch(self, dois):
        called['dois'] = dois
        return {d.lower(): _fake_work(d) for d in dois}

    monkeypatch.setattr(OpenAlexScraper, 'fetch_works_by_dois', fake_fetch)

    records = [
        {'doi': '10.1/a', 'cited_by': 0, 'country': '', 'institution': '', 'keywords': []},
        {'doi': '10.1/b', 'cited_by': 0, 'country': '', 'institution': '', 'keywords': []},
    ]
    stats = {}
    enrich_records_with_openalex(records, stats)

    assert called['dois'] == ['10.1/a']
    assert stats['zenginlestirme_enriched'] == 1
    assert records[1]['cited_by'] == 0


def test_fetch_works_by_dois_batches_and_normalizes_doi(monkeypatch):
    """50'den fazla DOI iki ayrı istek halinde gönderilir; dönen anahtar küçük harf, önekisiz."""
    seen_filters = []

    def fake_fetch_page(self, params, cursor=None):
        seen_filters.append(params['filter'])
        return {'results': [{'doi': 'https://doi.org/10.1/A'}]}

    monkeypatch.setattr(OpenAlexScraper, '_fetch_page', fake_fetch_page)

    dois = [f'10.1/{i}' for i in range(60)]
    result = OpenAlexScraper().fetch_works_by_dois(dois)

    assert len(seen_filters) == 2  # 60 DOI → 50 + 10
    assert '10.1/0' in seen_filters[0]
    assert '10.1/59' in seen_filters[1]
    assert '10.1/a' in result  # doi.org/10.1/A -> küçük harf


def _rec(title, year=None, doi=''):
    return {'title': title, 'year': year, 'doi': doi}


def test_dedup_same_title_same_year_is_duplicate():
    recs = [_rec('COVID-19: A Review', 2021), _rec('covid 19 a review', 2021)]
    result = _deduplicate_and_filter(recs)
    assert len(result) == 1


def test_dedup_same_title_different_years_kept_separate():
    """B1-2: aynı (genel) başlık farklı yıllarda yayınlanmışsa yanlışlıkla birleştirilmez."""
    recs = [_rec('Editöryal', 2020), _rec('Editöryal', 2021)]
    result = _deduplicate_and_filter(recs)
    assert len(result) == 2


def test_dedup_same_title_one_missing_year_still_duplicate():
    """Kaynaklardan biri yıl vermiyorsa eski davranış gibi yalnız başlığa güvenilir."""
    recs = [_rec('Örnek Başlık', 2020), _rec('Örnek Başlık', None)]
    result = _deduplicate_and_filter(recs)
    assert len(result) == 1


def test_dedup_doi_takes_priority_over_title():
    recs = [_rec('Başlık A', 2020, doi='10.1/x'), _rec('Başlık B', 2021, doi='10.1/x')]
    result = _deduplicate_and_filter(recs)
    assert len(result) == 1


def test_normalize_title_key_ignores_punctuation():
    assert _normalize_title_key('COVID-19: A Review!') == _normalize_title_key('covid 19 a review')


def test_canonical_author_key_matches_name_variants():
    """B1-3: 'Smith, J.' / 'John Smith' / 'JOHN SMITH' aynı kişi sayılmalı."""
    key = canonical_author_key('John Smith')
    assert canonical_author_key('Smith, J.') == key
    assert canonical_author_key('JOHN SMITH') == key
    assert canonical_author_key('Smith, J') == key


def test_canonical_author_key_ignores_accents_and_case():
    assert canonical_author_key('Şahin, A.') == canonical_author_key('ahmet sahin')


def test_canonical_author_key_distinguishes_different_surnames():
    assert canonical_author_key('John Smith') != canonical_author_key('John Doe')


def test_group_authors_merges_name_variants():
    records = [
        {'authors': ['Smith, J.', 'Ayşe Kaya']},
        {'authors': ['John Smith']},
        {'authors': ['John Smith']},
    ]
    counts, display = _group_authors(records)
    smith_key = canonical_author_key('John Smith')
    assert counts[smith_key] == 3
    assert display[smith_key] in ('John Smith', 'Smith, J.')
    assert len(counts) == 2  # Smith + Kaya


def test_top_authors_merges_variants_into_single_bar():
    records = [
        {'authors': ['Smith, J.']},
        {'authors': ['John Smith']},
        {'authors': ['John Smith']},
        {'authors': ['Ayşe Kaya']},
    ]
    fig = top_authors(records, n=15)
    ax = fig.axes[0]
    labels = [t.get_text() for t in ax.get_yticklabels()]
    assert len(labels) == 2
    bars = [p.get_width() for p in ax.patches]
    assert sorted(bars) == [1, 3]


def test_lotka_law_merges_variants():
    records = [
        {'authors': ['Smith, J.']},
        {'authors': ['John Smith']},
        {'authors': ['John Smith']},
        {'authors': ['Ayşe Kaya']},
    ]
    counts, _ = _group_authors(records)
    assert sorted(counts.values()) == [1, 3]
    fig = lotka_law(records)
    assert fig is not None


def test_author_collaboration_merges_variants_into_one_node():
    """Aynı yazarın 'Smith, J.' / 'John Smith' varyantları tek düğüme birleşmeli."""
    records = [
        {'authors': ['Smith, J.', 'Ayşe Kaya']},
        {'authors': ['John Smith', 'Mehmet Demir']},
    ]
    fig = author_collaboration(records, min_collab=1)
    assert fig is not None
    ax = fig.axes[0]
    node_collection = max(ax.collections, key=lambda c: c.get_offsets().shape[0])
    assert node_collection.get_offsets().shape[0] == 3  # Smith (birleşik) + Kaya + Demir


def test_simple_depluralize_basic_rules():
    assert _simple_depluralize('cats') == 'cat'
    assert _simple_depluralize('boxes') == 'box'
    assert _simple_depluralize('studies') == 'study'
    assert _simple_depluralize('glass') == 'glass'  # çift 's' — dokunulmaz
    assert _simple_depluralize('bus') == 'bus'  # çok kısa — dokunulmaz


def test_normalize_keywords_hyphen_and_space_are_equivalent():
    """B1-4: 'COVID-19' ve 'COVID 19' aynı anahtar kelimeye normalize edilmeli."""
    assert normalize_keywords(['COVID-19']) == normalize_keywords(['COVID 19'])


def test_normalize_keywords_falls_back_to_depluralize_when_lemmatization_unchanged(monkeypatch):
    """TR lemmatization kelimeyi değiştirmediyse (muhtemelen yabancı kelime) basit
    çoğul→tekil kuralı devreye girer (B1-4)."""
    monkeypatch.setattr(analyzer_module, 'lemmatize_word', lambda w: w)
    assert normalize_keywords(['cats']) == ['cat']


def _journal_records(counts: dict):
    recs = []
    for journal, n in counts.items():
        for _ in range(n):
            recs.append({'journal': journal})
    return recs


def test_bradford_zones_splits_into_three_equal_thirds():
    """B2-1: bölgeler yaklaşık eşit yayın sayısı taşımalı, az dergi çok yayın
    üretiyorsa (çekirdek) Bölge 1'in dergi sayısı Bölge 3'ten belirgin az olmalı."""
    counts = {f'J{i}': c for i, c in enumerate([30, 15, 10, 5, 5, 3, 3, 2, 2, 1])}
    records = _journal_records(counts)
    zones, totals = bradford_zones(records)
    total = sum(counts.values())
    assert sum(totals) == total
    assert len(zones[0]) < len(zones[2])
    # Her bölge toplamı hedef (total/3)'e yakın olmalı (son bölge kalanı taşır)
    for t in totals[:2]:
        assert abs(t - total / 3) <= max(counts.values())


def test_bradford_zones_insufficient_journals_returns_none():
    records = _journal_records({'J1': 5, 'J2': 3})  # yalnız 2 farklı dergi
    zones, totals = bradford_zones(records)
    assert zones is None and totals is None


def test_bradford_law_returns_none_without_enough_journals():
    assert bradford_law(_journal_records({'Tek Dergi': 10})) is None


def test_bradford_law_figure_table_matches_zone_totals():
    counts = {f'J{i}': c for i, c in enumerate([30, 15, 10, 5, 5, 3, 3, 2, 2, 1])}
    records = _journal_records(counts)
    zones, totals = bradford_zones(records)
    fig = bradford_law(records)
    assert fig is not None
    table = fig.axes[1].tables[0]
    cells = table.get_celld()
    # Satır 1 (ilk veri satırı, 0 başlık) → Bölge 1 dergi/yayın sayısı
    assert cells[(1, 1)].get_text().get_text() == str(len(zones[0]))
    assert cells[(1, 2)].get_text().get_text() == f'{totals[0]:,}'


_KEYWORD_TOPICS = {
    'A': ['machine learning', 'deep learning', 'neural network', 'classification'],
    'B': ['covid-19', 'public health', 'pandemic', 'vaccination'],
    'C': ['climate change', 'carbon emission', 'sustainability', 'renewable energy'],
}


def _topic_keyword_records(topics=_KEYWORD_TOPICS, per_topic=25, seed=3):
    import random
    rng = random.Random(seed)
    records = []
    for _ in range(per_topic * len(topics)):
        topic = rng.choice(list(topics.keys()))
        kws = rng.sample(topics[topic], k=rng.randint(2, 4))
        records.append({'keywords': kws})
    return records


def test_keyword_clusters_separates_distinct_topics():
    """B2-2: birbiriyle hiç eş geçmeyen 3 konu grubu 3 ayrı Louvain kümesine
    ayrılmalı, her kümenin kelimeleri yalnız kendi konu grubundan olmalı."""
    records = _topic_keyword_records()
    G, communities, all_kw = keyword_clusters(records)
    assert G is not None
    assert len(communities) == 3
    topic_sets = [set(normalize_keywords(v)) for v in _KEYWORD_TOPICS.values()]
    for comm in communities:
        assert any(comm <= topic_set for topic_set in topic_sets)


def test_keyword_clusters_deterministic_with_fixed_seed():
    """Louvain varsayılan olarak rastgele olabilir — sabit seed aynı sonucu vermeli."""
    records = _topic_keyword_records()
    _, communities1, _ = keyword_clusters(records)
    _, communities2, _ = keyword_clusters(records)
    assert communities1 == communities2


def test_keyword_clusters_insufficient_data_returns_none():
    G, communities, all_kw = keyword_clusters([{'keywords': []}])
    assert G is None and communities is None and all_kw is None


def test_keyword_cooccurrence_table_lists_all_clusters():
    records = _topic_keyword_records()
    _, communities, _ = keyword_clusters(records)
    fig = keyword_cooccurrence(records)
    assert fig is not None
    table = fig.axes[1].tables[0]
    n_data_rows = len({row for row, _ in table.get_celld().keys() if row > 0})
    assert n_data_rows == len(communities)


def test_thematic_map_themes_isolated_cluster_has_zero_centrality():
    """B2-3: dışa hiç bağlantısı olmayan (izole) bir küme merkeziyet=0 almalı —
    Callon merkeziyet tanımı: dışarıyla toplam eş-oluşum ağırlığı."""
    # 'data' A ve B'yi köprüler; C (iklim) hiçbir ortak kelime paylaşmaz → izole.
    topics = {
        'A': ['machine learning', 'deep learning', 'neural network', 'classification', 'data'],
        'B': ['covid-19', 'public health', 'pandemic', 'vaccination', 'data'],
        'C': ['climate change', 'carbon emission', 'sustainability', 'renewable energy'],
    }
    records = _topic_keyword_records(topics, per_topic=60, seed=5)
    themes, mean_c, mean_d = thematic_map_themes(records)
    assert themes is not None
    assert len(themes) == 3
    isolated = next(t for t in themes if 'climate change' in t['label'] or 'carbon emission' in t['label'])
    assert isolated['centrality'] == 0
    assert all(t['centrality'] >= 0 and t['density'] >= 0 for t in themes)


def test_thematic_map_themes_requires_at_least_two_clusters():
    """Tek kümeyle merkeziyet (dışa bağlantı) tanımsız — None dönmeli."""
    records = _topic_keyword_records({'A': _KEYWORD_TOPICS['A']}, per_topic=30, seed=1)
    themes, mean_c, mean_d = thematic_map_themes(records)
    assert themes is None


def test_thematic_map_figure_has_one_bubble_per_theme():
    records = _topic_keyword_records()
    themes, _, _ = thematic_map_themes(records)
    fig = thematic_map(records)
    assert fig is not None
    scatter = next(c for c in fig.axes[0].collections if hasattr(c, 'get_offsets')
                   and c.get_offsets().shape[0] > 0)
    assert scatter.get_offsets().shape[0] == len(themes)
