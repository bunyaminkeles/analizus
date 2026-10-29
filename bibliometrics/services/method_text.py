"""
Tezine/makalesine yapıştırılabilir "Yöntem" paragrafı (B3-3).
report_notes.py'nin kaynak-türüne-göre-tam-cümle desenini izler; aynı
stats/source sözlüklerinden üretir, PDF'ten bağımsız düz metin döner.
"""
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import number_format
from django.utils.translation import gettext


def _num(n):
    return number_format(n, force_grouping=True)


def _source_sentence(source: dict, date_str: str) -> str:
    kind = source.get('kind')
    query = (source.get('query') or '').strip()
    if kind == 'openalex':
        if query:
            return gettext(
                'Bu çalışmada kullanılan bibliyometrik veri seti, {date} tarihinde OpenAlex '
                'veritabanından "{query}" sorgusuyla elde edilmiştir.'
            ).format(date=date_str, query=query)
        return gettext(
            'Bu çalışmada kullanılan bibliyometrik veri seti, {date} tarihinde OpenAlex '
            'veritabanından elde edilmiştir.'
        ).format(date=date_str)
    if kind == 'pubmed':
        if query:
            return gettext(
                'Bu çalışmada kullanılan bibliyometrik veri seti, {date} tarihinde PubMed '
                'veritabanından "{query}" sorgusuyla elde edilmiştir.'
            ).format(date=date_str, query=query)
        return gettext(
            'Bu çalışmada kullanılan bibliyometrik veri seti, {date} tarihinde PubMed '
            'veritabanından elde edilmiştir.'
        ).format(date=date_str)
    fmt = source.get('format') or ''
    return gettext(
        'Bu çalışmada kullanılan bibliyometrik veri seti, {date} tarihinde {format} '
        'formatında dışa aktarılan kayıtlardan elde edilmiştir.'
    ).format(date=date_str, format=fmt)


def _flow_sentence(records: list, stats: dict, source: dict) -> str:
    stats = stats or {}
    no_title = stats.get('no_title', 0)
    duplicate = stats.get('duplicate', 0)
    n = len(records)
    sentences = []

    if source.get('kind') in ('openalex', 'pubmed'):
        found, fetched = source.get('found', 0), source.get('fetched', 0)
        if found and fetched and found != fetched:
            sentences.append(gettext(
                'Toplam {found} kayıttan {fetched} tanesi çekilmiştir.'
            ).format(found=_num(found), fetched=_num(fetched)))

    sentences.append(gettext(
        'Başlığı olmayan {no_title} kayıt ve tekrar eden {duplicate} kayıt çıkarıldıktan sonra '
        '{n} kayıt analize dahil edilmiştir. Tekrar eden kayıtlar DOI bilgisine, DOI yoksa '
        'noktalama işaretlerinden arındırılmış başlık ve yayın yılına göre tespit edilmiştir.'
    ).format(no_title=_num(no_title), duplicate=_num(duplicate), n=_num(n)))

    if stats.get('zenginlestirme_enriched'):
        sentences.append(gettext(
            'DOI\'si olan {enriched} kayıt, eksik atıf sayısı, ülke, kurum ve/veya anahtar '
            'kelime bilgisini tamamlamak için OpenAlex ile zenginleştirilmiştir.'
        ).format(enriched=_num(stats['zenginlestirme_enriched'])))

    return ' '.join(sentences)


def _method_sentence(n_analyses: int) -> str:
    return gettext(
        'Veri seti üzerinde yayın trendi, atıf analizi, yazar/ülke/kurum işbirliği ağları, '
        'anahtar kelime eş-oluşum ağı ve kümeleme, Bradford Kanunu, tematik harita ve tematik '
        'evrim, üç alan grafiği, bibliyografik eşleşme ağı ve konu modelleme dahil olmak üzere '
        '{n} bibliyometrik analiz gerçekleştirilmiştir. Analizler Python programlama dili '
        '(pandas, networkx, scikit-learn ve matplotlib kütüphaneleri) kullanılarak Analizus '
        '(https://analizus.com) platformu üzerinde otomatik olarak üretilmiştir.'
    ).format(n=n_analyses)


def _citation_paragraph(date_str: str, year: int) -> str:
    return gettext(
        'Önerilen kaynak gösterimi:\nAnalizus ({year}). Bibliyometrik Analiz Aracı [Bilgisayar '
        'yazılımı]. https://analizus.com adresinden erişildi ({date}).'
    ).format(year=year, date=date_str)


def _disclaimer_paragraph() -> str:
    url = getattr(settings, 'SITE_URL', 'https://analizus.com') + reverse('proje_talebi') + '?source=bibliometrics'
    return gettext(
        'Not: Bu metin otomatik olarak üretilmiştir ve bir uzman tarafından incelenip '
        'onaylanmamıştır; tezinize/makalenize eklemeden önce içeriği danışmanınızla ve '
        'alanınızın yazım kurallarıyla karşılaştırmanız önerilir. Kapsamlı bir uzman '
        'doğrulaması için: {url}'
    ).format(url=url)


def build_method_text(records: list, stats: dict, source: dict, n_analyses: int) -> str:
    now = timezone.now()
    date_str = now.strftime('%d.%m.%Y')
    paragraphs = [
        _source_sentence(source, date_str),
        _flow_sentence(records, stats, source),
        _method_sentence(n_analyses),
        _citation_paragraph(date_str, now.year),
        _disclaimer_paragraph(),
    ]
    return '\n\n'.join(p for p in paragraphs if p)
