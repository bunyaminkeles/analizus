import requests
import logging
import time
import os

logger = logging.getLogger(__name__)

API_BASE = "https://api.openalex.org/works"
MAX_PER_PAGE = 200


class OpenAlexScraper:
    """OpenAlex REST API client."""

    def __init__(self, timeout=60, max_retries=3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        # Polite pool: email header ile daha yüksek rate limit
        email = os.environ.get('OPENALEX_EMAIL', 'info@analizus.com')
        self.session.headers.update({
            'User-Agent': f'AnalizusBot/1.0 (mailto:{email})',
            'Accept': 'application/json',
            'Accept-Encoding': 'identity',  # gzip decompress hatalarını önle
        })
        self.api_key = os.environ.get('OPENALEX_API_KEY', '')

    def build_api_params(self, query_parts):
        """
        Yapısal sorgu parçalarını OpenAlex API parametrelerine çevirir.

        OpenAlex filter mantığı:
        - Virgülle ayrılan filtreler AND ile birleşir
        - Aynı filtre içinde pipe | ile OR
        - search parametresi genel arama için

        query_parts: [
            {"field": "title", "value": "machine learning", "operator": "AND"},
            {"field": "year", "value": "2020-2023", "operator": "AND"},
            {"field": "type", "value": "journal-article", "operator": "AND"},
        ]
        """
        filters = []
        search_terms = []

        for part in query_parts:
            field = part.get('field', '')
            value = part.get('value', '').strip()
            if not value:
                continue

            if field == 'title':
                filters.append(f'title.search:{value}')
            elif field == 'abstract':
                filters.append(f'abstract.search:{value}')
            elif field == 'author':
                filters.append(f'authorships.author.display_name.search:{value}')
            elif field == 'keyword':
                # Anahtar kelime → genel arama ile birleştir
                search_terms.append(value)
            elif field == 'journal':
                filters.append(f'primary_location.source.display_name.search:{value}')
            elif field == 'institution':
                filters.append(f'authorships.institutions.display_name.search:{value}')
            elif field == 'year':
                # "2020-2023" → publication_year:2020-2023 (OpenAlex range filter)
                # "2020" → publication_year:2020
                filters.append(f'publication_year:{value}')
            elif field == 'doi':
                # DOI tam eşleşme
                doi_val = value
                if not doi_val.startswith('https://doi.org/'):
                    doi_val = f'https://doi.org/{doi_val}'
                filters.append(f'doi:{doi_val}')
            elif field == 'type':
                # Yayın türü: journal-article, book, dissertation, etc.
                filters.append(f'type:{value}')

        params = {
            'per_page': MAX_PER_PAGE,
            'sort': 'publication_year:desc',
        }

        if self.api_key:
            params['api_key'] = self.api_key

        if filters:
            params['filter'] = ','.join(filters)

        if search_terms:
            params['search'] = ' '.join(search_terms)

        return params

    def _build_query_description(self, params):
        """API parametrelerinin okunabilir açıklaması."""
        parts = []
        if 'filter' in params:
            parts.append(f"filter={params['filter']}")
        if 'search' in params:
            parts.append(f"search={params['search']}")
        return ' & '.join(parts) if parts else '*'

    def _fetch_page(self, params, cursor=None):
        """OpenAlex API'den tek sayfa sonuç çeker."""
        req_params = dict(params)
        if cursor:
            req_params['cursor'] = cursor
        else:
            req_params['cursor'] = '*'

        for attempt in range(self.max_retries):
            try:
                response = self.session.get(
                    API_BASE, params=req_params, timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                logger.warning(f"OpenAlex API attempt {attempt+1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise

    @staticmethod
    def _reconstruct_abstract(inverted_index):
        """OpenAlex inverted_index formatını düz metne çevirir."""
        if not inverted_index or not isinstance(inverted_index, dict):
            return ''
        try:
            word_positions = []
            for word, positions in inverted_index.items():
                for pos in positions:
                    word_positions.append((pos, word))
            word_positions.sort(key=lambda x: x[0])
            return ' '.join(w for _, w in word_positions)
        except Exception:
            return ''

    def _parse_work(self, work):
        """API work objesini yapısal dict'e çevirir."""
        # Başlık
        title = work.get('display_name') or work.get('title') or ''

        # Yazarlar
        authorships = work.get('authorships') or []
        author_names = []
        institutions = []
        for auth in authorships:
            author = auth.get('author', {}) or {}
            name = author.get('display_name', '')
            if name:
                author_names.append(name)
            for inst in (auth.get('institutions') or []):
                inst_name = inst.get('display_name', '')
                if inst_name and inst_name not in institutions:
                    institutions.append(inst_name)

        # Dergi/Kaynak
        primary_location = work.get('primary_location') or {}
        source = primary_location.get('source') or {}
        journal_name = source.get('display_name') or ''

        # Abstract
        abstract = self._reconstruct_abstract(work.get('abstract_inverted_index'))

        # Anahtar kelimeler
        keywords = []
        for kw in (work.get('keywords') or []):
            keyword = kw.get('display_name') or kw.get('keyword', '')
            if keyword:
                keywords.append(keyword)

        # Concepts (eski yöntem, bazı kayıtlarda hala var)
        concepts = []
        for c in (work.get('concepts') or []):
            concept_name = c.get('display_name', '')
            if concept_name:
                concepts.append(concept_name)

        return {
            'id': work.get('id', ''),
            'title': title,
            'authors': ', '.join(author_names),
            'year': work.get('publication_year') or '',
            'journal': journal_name,
            'doi': work.get('doi') or '',
            'type': work.get('type') or '',
            'cited_by_count': work.get('cited_by_count') or 0,
            'abstract': abstract,
            'keywords': keywords,
            'concepts': concepts[:5],
            'institutions': ', '.join(institutions[:5]),
            'open_access': (work.get('open_access') or {}).get('is_oa', False),
        }

    def search(self, query_parts, demo_limit=5):
        """
        Ana arama metodu.

        Returns: (total_count, demo_results, all_results, api_query_desc)
        """
        params = self.build_api_params(query_parts)
        api_query_desc = self._build_query_description(params)
        logger.info(f"OpenAlex arama: {api_query_desc}")

        # İlk sayfa
        data = self._fetch_page(params)

        total_count = data.get('meta', {}).get('count', 0)
        results = data.get('results') or []

        if total_count == 0:
            return 0, [], [], api_query_desc

        # Tüm sonuçları topla
        all_results = [self._parse_work(w) for w in results]
        demo_results = all_results[:demo_limit]

        # Pagination (cursor-based)
        next_cursor = data.get('meta', {}).get('next_cursor')

        while next_cursor and len(all_results) < total_count:
            try:
                data = self._fetch_page(params, cursor=next_cursor)
                page_results = data.get('results') or []
                if not page_results:
                    break
                all_results.extend([self._parse_work(w) for w in page_results])
                next_cursor = data.get('meta', {}).get('next_cursor')
                time.sleep(0.1)  # API'ye saygılı ol (polite pool)
            except Exception as e:
                logger.error(f"OpenAlex pagination hatası: {e}")
                break

            # Güvenlik: maksimum 5000 sonuç
            if len(all_results) >= 5000:
                logger.info(f"Maksimum sonuç limitine ulaşıldı: {len(all_results)}")
                break

        logger.info(f"OpenAlex arama tamamlandı: {total_count} toplam, {len(all_results)} çekildi")
        return total_count, demo_results, all_results, api_query_desc
