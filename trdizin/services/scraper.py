import requests
import logging
import time

logger = logging.getLogger(__name__)

API_BASE = "https://search.trdizin.gov.tr/api/defaultSearch/publication/"
MAX_PAGE_SIZE = 100


class TRDizinScraper:
    """TR Dizin REST API client."""

    def __init__(self, timeout=30, max_retries=3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        })

    def build_lucene_query(self, query_parts):
        """
        Yapısal sorgu parçalarını Lucene query string'e çevirir.

        query_parts: [
            {"field": "title", "value": "ankara", "operator": "AND"},
            {"field": "abstract", "value": "sağlık AND yönetimi", "operator": "AND"},
            {"field": "year", "value": "2020-2022", "operator": "AND"},
            {"field": "language", "value": "TUR,ENG", "operator": "AND"},
            {"field": "institution", "value": "Hacettepe", "operator": "AND"},
        ]
        """
        clauses = []

        for part in query_parts:
            field = part.get('field', '')
            value = part.get('value', '').strip()
            if not value:
                continue

            if field == 'year':
                # Yıl aralığı: "2020-2022" → year : ([2020 TO 2022])
                years = value.split('-')
                if len(years) == 2:
                    clause = f'year : ([{years[0].strip()} TO {years[1].strip()}])'
                else:
                    clause = f'year : ([{value} TO {value}])'
            elif field == 'language':
                # Dil: "TUR,ENG" → language : ( "TUR" OR "ENG" )
                langs = [v.strip() for v in value.split(',') if v.strip()]
                if len(langs) == 1:
                    clause = f'language : ( "{langs[0]}" )'
                else:
                    lang_str = ' OR '.join(f'"{l}"' for l in langs)
                    clause = f'language : ( {lang_str} )'
            else:
                # Diğer alanlar: title, abstract, author, keyword, journal, institution, doi
                # Değer zaten AND/OR içerebilir (kullanıcı girişi)
                if ' AND ' in value or ' OR ' in value:
                    # Kullanıcı kendi operatörlerini girmiş
                    clause = f'{field} : ( {value} )'
                else:
                    # Çok kelimeli değerleri TR Dizin formatına çevir:
                    # "halk sağlığı" → "halk" AND "sağlığı"
                    words = value.split()
                    if len(words) > 1:
                        word_str = ' AND '.join(f'"{w}"' for w in words)
                        clause = f'{field} : ( {word_str} )'
                    else:
                        clause = f'{field} : ( "{value}" )'

            clauses.append(clause)

        if not clauses:
            return '*'

        # Parçaları operatörlerle birleştir
        result_parts = []
        for i, part in enumerate(query_parts):
            if not part.get('value', '').strip():
                continue
            if i > 0 and result_parts:
                operator = part.get('operator', 'AND')
                result_parts.append(f' {operator} ')
            # İlgili clause'u bul
            clause_idx = len([p for p in query_parts[:i+1] if p.get('value', '').strip()]) - 1
            if clause_idx < len(clauses):
                result_parts.append(clauses[clause_idx])

        query = ''.join(result_parts)
        return f'({query})'

    def _fetch_page(self, lucene_query, page=1, limit=20, order='publicationYear-DESC'):
        """TR Dizin API'den tek sayfa sonuç çeker."""
        params = {
            'q': lucene_query,
            'order': order,
            'page': page,
            'limit': limit,
        }

        for attempt in range(self.max_retries):
            try:
                response = self.session.get(
                    API_BASE, params=params, timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                logger.warning(f"TR Dizin API attempt {attempt+1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise

    def _parse_hit(self, hit):
        """API hit'ini yapısal dict'e çevirir."""
        source = hit.get('_source', {})

        # Başlık ve özetler abstracts dizisinden
        abstracts_list = source.get('abstracts', []) or []
        title = ''
        abstract_tr = ''
        abstract_en = ''
        keywords_tr = []
        keywords_en = []

        for ab in abstracts_list:
            lang = (ab.get('language') or '').upper()
            if lang == 'TUR':
                if not title:
                    title = ab.get('title', '')
                abstract_tr = ab.get('abstract', '')
                keywords_tr = ab.get('keywords', []) or []
            elif lang == 'ENG':
                if not title:
                    title = ab.get('title', '')
                abstract_en = ab.get('abstract', '')
                keywords_en = ab.get('keywords', []) or []

        # Başlık bulunamazsa ilk abstract'ın title'ını al
        if not title and abstracts_list:
            title = abstracts_list[0].get('title', '')

        # Yazarlar
        authors_list = source.get('authors', []) or []
        author_names = []
        for a in sorted(authors_list, key=lambda x: x.get('order', 0)):
            name = a.get('inPublicationName') or a.get('name', '')
            if name:
                author_names.append(name)

        # Dergi bilgisi
        journal = source.get('journal') or {}
        journal_name = ''
        if isinstance(journal, dict):
            journal_name = journal.get('name') or journal.get('title', '')
        elif isinstance(journal, str):
            journal_name = journal

        return {
            'id': source.get('id', ''),
            'title': title,
            'authors': ', '.join(author_names),
            'year': source.get('publicationYear', ''),
            'journal': journal_name,
            'doi': source.get('doi') or '',
            'publication_type': source.get('publicationType') or '',
            'access_type': source.get('accessType') or '',
            'language': source.get('language') or '',
            'abstract_tr': abstract_tr,
            'abstract_en': abstract_en,
            'keywords_tr': keywords_tr,
            'keywords_en': keywords_en,
        }

    def search(self, query_parts, demo_limit=3):
        """
        Ana arama metodu.

        Returns: (total_count, demo_results, all_results, lucene_query)
        - demo_results: İlk demo_limit sonuç (özetlerle birlikte)
        - all_results: Tüm sonuçlar
        - lucene_query: Oluşturulan Lucene sorgusu
        """
        lucene_query = self.build_lucene_query(query_parts)
        logger.info(f"TR Dizin arama: {lucene_query}")

        # İlk sayfa: toplam sonuç sayısı + demo sonuçlar
        data = self._fetch_page(lucene_query, page=1, limit=MAX_PAGE_SIZE)

        total_count = data.get('hits', {}).get('total', {}).get('value', 0)
        hits = data.get('hits', {}).get('hits', [])

        if total_count == 0:
            return 0, [], [], lucene_query

        # Demo sonuçlar
        demo_results = [self._parse_hit(h) for h in hits[:demo_limit]]

        # Tüm sonuçları çek (pagination)
        all_results = [self._parse_hit(h) for h in hits]

        page = 2
        while len(all_results) < total_count:
            try:
                data = self._fetch_page(lucene_query, page=page, limit=MAX_PAGE_SIZE)
                page_hits = data.get('hits', {}).get('hits', [])
                if not page_hits:
                    break
                all_results.extend([self._parse_hit(h) for h in page_hits])
                page += 1
                time.sleep(0.5)  # API'ye saygılı ol
            except Exception as e:
                logger.error(f"TR Dizin pagination hatası (sayfa {page}): {e}")
                break

            # Maksimum sonuç limiti (admin panelinden ayarlanabilir)
            from forum.models import SiteSettings
            max_records = SiteSettings.load().scrap_max_records or 5000
            if len(all_results) >= max_records:
                logger.info(f"Maksimum sonuç limitine ulaşıldı: {len(all_results)}")
                break

        logger.info(f"TR Dizin arama tamamlandı: {total_count} toplam, {len(all_results)} çekildi")
        return total_count, demo_results, all_results, lucene_query
