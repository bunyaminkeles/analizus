import logging
import os
import random
import re
import threading
import time
import xml.etree.ElementTree as ET

import requests

logger = logging.getLogger(__name__)

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
MAX_PER_PAGE = 200
# esearch geçmişinden (WebEnv) en fazla 10.000 kayıt alınabilir (NCBI kısıtı)
EUTILS_MAX_RETRIEVABLE = 10000

# NCBI kuralı: anahtarsız 3 istek/sn, NCBI_API_KEY ile 10 istek/sn — tüm thread'ler için ortak sınır.
_rate_lock = threading.Lock()
_last_request_at = [0.0]

# Sorgu alanı → PubMed alan etiketi. 'keyword' etiketsiz (PubMed'in otomatik terim eşlemesi).
FIELD_TAGS = {
    'title': 'ti',
    'tiab': 'tiab',
    'author': 'au',
    'mesh': 'mh',
    'journal': 'ta',
    'affiliation': 'ad',
    'doi': 'aid',
    'type': 'pt',
    'year': 'dp',
}


_EMAIL_TAIL_RE = re.compile(r'\s*Electronic address:.*$', re.IGNORECASE)
_EMAIL_RE = re.compile(r'\S+@\S+')


def _redact_api_key(text):
    """Hata metnindeki api_key değerini gizler (log'a NCBI anahtarı yazılmasın)."""
    return re.sub(r'(api_key=)[^&\s]+', r'\1***', str(text))


class PubMedScraper:
    """NCBI E-utilities client (esearch + efetch)."""

    def __init__(self, timeout=60, max_retries=3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.email = os.environ.get('NCBI_EMAIL') or os.environ.get('OPENALEX_EMAIL', 'info@analizus.com')
        self.session.headers.update({
            'User-Agent': f'AnalizusBot/1.0 (mailto:{self.email})',
            'Accept-Encoding': 'identity',
        })
        self.api_key = os.environ.get('NCBI_API_KEY', '')
        self.min_interval = 0.11 if self.api_key else 0.34

    def build_term(self, query_parts):
        """Yapısal sorgu parçalarını PubMed arama ifadesine çevirir (parçalar AND ile birleşir).

        query_parts: [{"field": "title", "value": "machine learning", "operator": "AND"},
                      {"field": "year", "value": "2020-2023", "operator": "AND"}, ...]
        """
        terms = []
        for part in query_parts:
            field = part.get('field', '')
            value = (part.get('value') or '').strip()
            if not value:
                continue
            if field == 'year':
                # "2020-2023" → 2020:2023[dp], "2020" → 2020[dp]
                years = re.findall(r'\d{4}', value)
                if not years:
                    continue
                value = f'{years[0]}:{years[1]}' if len(years) > 1 else years[0]
                terms.append(f'{value}[dp]')
                continue
            if field == 'doi':
                value = re.sub(r'^https?://(dx\.)?doi\.org/', '', value)
            value = value.replace('"', '')
            tag = FIELD_TAGS.get(field)
            if tag:
                # Çok kelimeli değerde her kelime alanda aranır (tırnaksız tam ifade PubMed'de
                # çoğu zaman sonuç vermez); tek kelimede doğrudan etiket
                words = value.split()
                if field in ('author', 'journal', 'mesh', 'type', 'doi') or len(words) == 1:
                    terms.append(f'"{value}"[{tag}]' if len(words) > 1 else f'{value}[{tag}]')
                else:
                    terms.append('(' + ' AND '.join(f'{w}[{tag}]' for w in words) + ')')
            else:
                terms.append(f'({value})')
        return ' AND '.join(terms)

    def _throttle(self):
        with _rate_lock:
            wait = self.min_interval - (time.monotonic() - _last_request_at[0])
            if wait > 0:
                time.sleep(wait)
            _last_request_at[0] = time.monotonic()

    def _get(self, endpoint, params):
        """Tek E-utilities isteği. 429 ve 5xx'te bekleyip yeniden dener."""
        req_params = dict(params, tool='analizus', email=self.email)
        if self.api_key:
            req_params['api_key'] = self.api_key
        for attempt in range(self.max_retries):
            self._throttle()
            try:
                response = self.session.get(EUTILS_BASE + endpoint, params=req_params, timeout=self.timeout)
                if (response.status_code == 429 or response.status_code >= 500) and attempt < self.max_retries - 1:
                    retry_after = int(response.headers.get('Retry-After', 0) or 0)
                    wait = max(retry_after, 2 ** attempt + random.uniform(1.0, 2.0))
                    logger.warning(f"PubMed {endpoint} {response.status_code}, {wait:.1f}s bekleniyor...")
                    time.sleep(wait)
                    continue
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                safe_msg = _redact_api_key(e)
                logger.warning(f"PubMed {endpoint} deneme {attempt + 1} başarısız: {safe_msg}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt + random.uniform(0.5, 1.5))
                else:
                    # Hata metni istek URL'sini (api_key dahil) taşır — yukarıdaki tüm log/traceback'ler
                    # anahtarsız görsün diye aynı türde, temizlenmiş mesajla yeniden fırlatılır
                    raise type(e)(safe_msg, response=e.response, request=e.request) from None

    def _esearch(self, term):
        """Returns: (count, webenv, query_key, query_translation)"""
        data = self._get('esearch.fcgi', {
            'db': 'pubmed', 'term': term, 'usehistory': 'y', 'retmode': 'json',
            'retmax': 0, 'sort': 'pub_date',
        }).json().get('esearchresult', {})
        if data.get('ERROR'):
            raise ValueError(data['ERROR'])
        return (int(data.get('count') or 0), data.get('webenv', ''), data.get('querykey', ''),
                data.get('querytranslation', ''))

    def _efetch(self, webenv, query_key, retstart, retmax):
        response = self._get('efetch.fcgi', {
            'db': 'pubmed', 'query_key': query_key, 'WebEnv': webenv,
            'retstart': retstart, 'retmax': retmax, 'retmode': 'xml',
        })
        root = ET.fromstring(response.content)
        return [self._parse_article(a) for a in root.findall('PubmedArticle')]

    @staticmethod
    def _text(el):
        """İç içe biçim etiketleri (<i>, <sup>) dahil tüm metin."""
        if el is None:
            return ''
        return re.sub(r'\s+', ' ', ''.join(el.itertext())).strip()

    def _parse_article(self, art):
        """PubmedArticle XML öğesini yapısal dict'e çevirir. Anahtarlar OpenAlex kaydıyla uyumlu
        (TXT/bibliometri ortak); PubMed'de atıf sayısı yok → 'cited_by_count' anahtarı eklenmez."""
        mc = art.find('MedlineCitation')
        article = mc.find('Article') if mc is not None else None
        if article is None:
            return {}

        pmid = self._text(mc.find('PMID'))
        title = self._text(article.find('ArticleTitle'))

        # Özet: bölümlü özetlerde "ETİKET: metin"
        abstract_parts = []
        for at in article.findall('Abstract/AbstractText'):
            text = self._text(at)
            if not text:
                continue
            label = at.get('Label')
            abstract_parts.append(f'{label}: {text}' if label else text)
        abstract = ' '.join(abstract_parts)

        # Yazarlar + adres (affiliation) metinleri
        author_names = []
        affiliations = []
        for au in article.findall('AuthorList/Author'):
            if au.get('ValidYN') == 'N':
                continue
            last = self._text(au.find('LastName'))
            fore = self._text(au.find('ForeName')) or self._text(au.find('Initials'))
            collective = self._text(au.find('CollectiveName'))
            name = f'{fore} {last}'.strip() if last else collective
            if name:
                author_names.append(name)
            for aff in au.findall('AffiliationInfo/Affiliation'):
                # PubMed adrese yazar e-postası ekler ("... China. Electronic address: x@y.com.") → kişisel veri
                # dosyaya taşınmasın, aynı kurum e-postalı/e-postasız iki kez sayılmasın
                aff_text = _EMAIL_RE.sub('', _EMAIL_TAIL_RE.sub('', self._text(aff))).strip(' ;,.')
                if aff_text and aff_text not in affiliations:
                    affiliations.append(aff_text)

        journal_el = article.find('Journal')
        journal = self._text(journal_el.find('Title')) if journal_el is not None else ''
        if not journal:
            journal = self._text(mc.find('MedlineJournalInfo/MedlineTA'))

        # Yıl: PubDate/Year, yoksa MedlineDate ("2023 Jan-Feb"), yoksa ArticleDate
        year = ''
        if journal_el is not None:
            pub_date = journal_el.find('JournalIssue/PubDate')
            if pub_date is not None:
                year = self._text(pub_date.find('Year'))
                if not year:
                    m = re.search(r'\d{4}', self._text(pub_date.find('MedlineDate')))
                    year = m.group(0) if m else ''
        if not year:
            year = self._text(article.find('ArticleDate/Year'))

        doi = ''
        for aid in art.findall('PubmedData/ArticleIdList/ArticleId'):
            if aid.get('IdType') == 'doi':
                doi = self._text(aid)
                break
        if not doi:
            for eloc in article.findall('ELocationID'):
                if eloc.get('EIdType') == 'doi':
                    doi = self._text(eloc)
                    break

        pub_types = [self._text(pt) for pt in article.findall('PublicationTypeList/PublicationType')]
        keywords = [self._text(k) for k in mc.findall('KeywordList/Keyword') if self._text(k)]
        mesh_terms = [self._text(d) for d in mc.findall('MeshHeadingList/MeshHeading/DescriptorName')]
        language = self._text(article.find('Language'))

        return {
            'id': pmid,
            'pmid': pmid,
            'title': title,
            'authors': ', '.join(author_names),
            'author_list': author_names,
            'year': int(year) if year.isdigit() else '',
            'journal': journal,
            'doi': f'https://doi.org/{doi}' if doi else '',
            'type': pub_types[0] if pub_types else '',
            'publication_types': pub_types,
            'abstract': abstract,
            'keywords': keywords,
            'mesh_terms': mesh_terms,
            # Kurum = yazar adres metni (PubMed kurum/ülke alanı ayrıştırılmış vermez)
            'institutions': '; '.join(affiliations[:5]),
            'affiliation_list': affiliations,
            'language': language,
        }

    def search(self, query_parts, demo_limit=5, max_results=None):
        """
        max_results: en fazla çekilecek kayıt (None → admin ayarı scrap_max_records). Arama yalnız
        ilk sayfayı çeker (max_results=MAX_PER_PAGE); tam veri job_runner.ensure_full_results ile.

        Returns: (total_count, demo_results, all_results, api_query_desc)
        """
        term = self.build_term(query_parts)
        if not term:
            raise ValueError('Boş sorgu')
        logger.info(f"PubMed arama: {term}")

        total_count, webenv, query_key, translation = self._esearch(term)
        api_query_desc = translation or term
        if total_count == 0:
            return 0, [], [], api_query_desc

        if max_results is None:
            from forum.models import SiteSettings
            max_results = SiteSettings.load().scrap_max_records or 5000
        target = min(total_count, max_results, EUTILS_MAX_RETRIEVABLE)

        all_results = []
        retstart = 0
        while retstart < target:
            batch = min(MAX_PER_PAGE, target - retstart)
            try:
                page = self._efetch(webenv, query_key, retstart, batch)
            except Exception as e:
                if retstart == 0:
                    raise
                logger.error(f"PubMed sayfalama hatası (retstart={retstart}): {e}")
                break
            if not page:
                break
            all_results.extend(r for r in page if r)
            retstart += batch

        demo_results = all_results[:demo_limit]
        logger.info(f"PubMed arama tamamlandı: {total_count} toplam, {len(all_results)} çekildi")
        return total_count, demo_results, all_results, api_query_desc
