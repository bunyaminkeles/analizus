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
)
from bibliometrics.services.report_notes import build_report_notes
from bibliometrics.services.parser import parse_openalex_txt, parse_pubmed_txt, detect_format, parse_file
from bibliometrics.services.pdf_builder import _demo_cta_text
from bibliometrics.models import BibliometricJob
from bibliometrics.services.job_runner import _in_user_language


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
    assert rec['keywords'] == []
