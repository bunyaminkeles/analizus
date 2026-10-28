"""
Bibliometri grafik üretimi için regresyon testleri.
Kapsam: yıl ekseni tam sayı tick'leri (A5), kısa dönem uyarısı (A6),
OpenAlex/PubMed TXT yeniden-yükleme (A7), demo CTA dil ayrımı (A8/A9).
"""
import matplotlib
matplotlib.use('Agg')

from django.utils import translation

from bibliometrics.services.analyzer import (
    publication_trend,
    annual_citation_trend,
    publication_growth_rate,
    SHORT_SERIES_YEARS,
)
from bibliometrics.services.report_notes import build_report_notes
from bibliometrics.services.parser import parse_openalex_txt, parse_pubmed_txt
from bibliometrics.services.pdf_builder import _demo_cta_text


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
