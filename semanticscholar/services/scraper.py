import requests
import logging
import time
import random
import threading
import os

logger = logging.getLogger(__name__)

SS_API_BASE = "https://api.semanticscholar.org/graph/v1/paper/search"
CR_API_BASE = "https://api.crossref.org/works"
SS_MAX_LIMIT = 100
SS_FIELDS = "title,authors,year,abstract,externalIds,citationCount,publicationTypes,journal,fieldsOfStudy,openAccessPdf,publicationDate"

_ss_semaphore = threading.Semaphore(3)


class SemanticScholarScraper:
    """
    Semantic Scholar Graph API client.
    CrossRef, DOI'si olan kayıtlarda kurum ve ülke bilgisini zenginleştirir.
    """

    def __init__(self, timeout=30, max_retries=3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        api_key = os.environ.get('SEMANTIC_SCHOLAR_API_KEY', '')
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'AnalizusBot/1.0 (mailto:info@analizus.com)',
        }
        if api_key:
            headers['x-api-key'] = api_key
        self.session.headers.update(headers)

        self.cr_session = requests.Session()
        self.cr_session.headers.update({
            'User-Agent': 'AnalizusBot/1.0 (mailto:info@analizus.com; https://analizus.com)',
            'Accept': 'application/json',
        })

    def build_query(self, query_parts):
        """
        query_parts listesini Semantic Scholar query string'e çevirir.

        SS API sadece tek bir `query` parametresi alır (Boolean operatör desteklemiyor).
        Tüm keyword/title/author parçalarını birleştirip tek sorgu oluştururuz.
        year ve doi alanları ayrı parametrelerle veya lokal filtreyle işlenir.
        """
        terms = []
        year_filter = None
        doi_filter = None
        field_filter = None

        for part in query_parts:
            field = part.get('field', '')
            value = part.get('value', '').strip()
            if not value:
                continue

            if field == 'year':
                year_filter = value
            elif field == 'doi':
                doi_filter = value
            elif field == 'field_of_study':
                field_filter = value
            else:
                terms.append(value)

        query = ' '.join(terms) if terms else '*'
        return query, year_filter, doi_filter, field_filter

    def _fetch_page(self, query, offset=0, fields_of_study=None):
        """Tek sayfa çeker."""
        params = {
            'query': query,
            'fields': SS_FIELDS,
            'limit': SS_MAX_LIMIT,
            'offset': offset,
        }
        if fields_of_study:
            params['fieldsOfStudy'] = fields_of_study

        for attempt in range(self.max_retries):
            try:
                resp = self.session.get(SS_API_BASE, params=params, timeout=self.timeout)
                if resp.status_code == 429:
                    retry_after = int(resp.headers.get('Retry-After', 0))
                    if retry_after and attempt < self.max_retries - 1:
                        logger.warning(f"S2 rate limit 429, {retry_after}s bekleniyor...")
                        time.sleep(retry_after)
                        continue
                    raise requests.HTTPError(
                        "Semantic Scholar API rate limit aşıldı. Lütfen birkaç dakika bekleyip tekrar deneyin.",
                        response=resp,
                    )
                if resp.status_code == 403:
                    raise requests.HTTPError(
                        "Semantic Scholar API erişimi reddedildi (403). "
                        "API key geçersiz veya henüz aktif değil. "
                        "Key onaylandıktan sonra tekrar deneyin.",
                        response=resp,
                    )
                resp.raise_for_status()
                return resp.json()
            except requests.HTTPError:
                raise
            except requests.RequestException as e:
                logger.warning(f"S2 API attempt {attempt+1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt + random.uniform(0.5, 1.5))
                else:
                    raise

    def _enrich_with_crossref(self, doi):
        """CrossRef'ten kurum ve ülke bilgisi çeker. Hata olursa boş dict döner."""
        if not doi:
            return {}
        clean_doi = doi.replace('https://doi.org/', '').strip()
        try:
            resp = self.cr_session.get(
                f"{CR_API_BASE}/{clean_doi}",
                timeout=10,
            )
            if resp.status_code == 404:
                return {}
            resp.raise_for_status()
            data = resp.json().get('message', {})

            institutions = []
            countries = []
            for author in (data.get('author') or []):
                for aff in (author.get('affiliation') or []):
                    name = aff.get('name', '')
                    if name and name not in institutions:
                        institutions.append(name)

            publisher = data.get('publisher', '')
            subject = '; '.join(data.get('subject') or [])
            issn = (data.get('ISSN') or [''])[0]

            return {
                'institutions': '; '.join(institutions[:5]),
                'publisher': publisher,
                'subject': subject,
                'issn': issn,
            }
        except Exception as e:
            logger.debug(f"CrossRef zenginleştirme atlandı ({doi}): {e}")
            return {}

    def _parse_paper(self, paper, enrich=False):
        """API paper objesini normalize edilmiş dict'e çevirir."""
        external_ids = paper.get('externalIds') or {}
        doi = external_ids.get('DOI', '')

        authors = [a.get('name', '') for a in (paper.get('authors') or []) if a.get('name')]
        pub_types = paper.get('publicationTypes') or []
        journal = (paper.get('journal') or {}).get('name', '')
        fields = paper.get('fieldsOfStudy') or []
        oa_pdf = (paper.get('openAccessPdf') or {}).get('url', '')

        rec = {
            'id': paper.get('paperId', ''),
            'title': (paper.get('title') or '').strip(),
            'authors': ', '.join(authors),
            'year': paper.get('year') or '',
            'journal': journal,
            'doi': doi,
            'type': pub_types[0] if pub_types else '',
            'cited_by_count': paper.get('citationCount') or 0,
            'abstract': (paper.get('abstract') or '').strip(),
            'fields_of_study': fields[:5],
            'open_access_pdf': oa_pdf,
            'institutions': '',
            'publisher': '',
            'subject': '',
        }

        if enrich and doi:
            cr_data = self._enrich_with_crossref(doi)
            rec.update({k: v for k, v in cr_data.items() if v})
            time.sleep(random.uniform(0.2, 0.4))

        return rec

    def _local_year_filter(self, results, year_filter):
        """'2020-2023' veya '2021' formatındaki yıl filtresini lokalde uygular."""
        if not year_filter:
            return results
        parts = year_filter.split('-')
        try:
            if len(parts) == 2:
                y_from, y_to = int(parts[0].strip()), int(parts[1].strip())
            else:
                y_from = y_to = int(parts[0].strip())
        except ValueError:
            return results

        filtered = []
        for r in results:
            try:
                y = int(r.get('year') or 0)
                if y_from <= y <= y_to:
                    filtered.append(r)
            except (TypeError, ValueError):
                filtered.append(r)
        return filtered

    def search(self, query_parts, demo_limit=5):
        with _ss_semaphore:
            return self._search_impl(query_parts, demo_limit)

    def _search_impl(self, query_parts, demo_limit=5):
        query, year_filter, doi_filter, field_filter = self.build_query(query_parts)

        if doi_filter:
            # DOI araması: tek kayıt getir
            return self._search_by_doi(doi_filter, demo_limit)

        logger.info(f"S2 arama: query={query!r}  yıl={year_filter}  alan={field_filter}")

        data = self._fetch_page(query, offset=0, fields_of_study=field_filter)
        total_count = data.get('total', 0)
        papers = data.get('data') or []

        if total_count == 0 or not papers:
            return 0, [], [], query

        all_results = [self._parse_paper(p, enrich=False) for p in papers]
        demo_results = all_results[:demo_limit]

        from forum.models import SiteSettings
        max_records = SiteSettings.load().scrap_max_records or 5000

        SS_MAX_OFFSET = 1000  # Semantic Scholar API hard limit
        offset = SS_MAX_LIMIT
        while len(all_results) < min(total_count, max_records, SS_MAX_OFFSET):
            if offset >= SS_MAX_OFFSET:
                logger.info(f"S2 offset limiti ({SS_MAX_OFFSET}) aşıldı, durduruluyor.")
                break
            try:
                data = self._fetch_page(query, offset=offset, fields_of_study=field_filter)
                page_papers = data.get('data') or []
                if not page_papers:
                    break
                all_results.extend([self._parse_paper(p, enrich=False) for p in page_papers])
                offset += SS_MAX_LIMIT
                time.sleep(random.uniform(1.0, 2.0))
            except Exception as e:
                logger.error(f"S2 pagination hatası (offset={offset}): {e}")
                break

        if year_filter:
            before = len(all_results)
            all_results = self._local_year_filter(all_results, year_filter)
            total_count = len(all_results)
            demo_results = all_results[:demo_limit]
            logger.info(f"S2 yıl filtresi ({year_filter}): {before} → {total_count}")

        # Demo sonuçlara CrossRef zenginleştirme yap
        demo_results = [self._parse_paper_enrich(r) for r in demo_results]

        logger.info(f"S2 arama tamamlandı: {total_count} toplam, {len(all_results)} çekildi")
        return total_count, demo_results, all_results, query

    def _parse_paper_enrich(self, rec):
        """Zaten parse edilmiş kayıt için CrossRef zenginleştirme yap."""
        doi = rec.get('doi', '')
        if doi and not rec.get('institutions'):
            cr_data = self._enrich_with_crossref(doi)
            if cr_data:
                rec.update({k: v for k, v in cr_data.items() if v})
        return rec

    def _search_by_doi(self, doi, demo_limit):
        """Tek DOI için arama yapar."""
        clean_doi = doi.replace('https://doi.org/', '').strip()
        try:
            resp = self.session.get(
                f"https://api.semanticscholar.org/graph/v1/paper/DOI:{clean_doi}",
                params={'fields': SS_FIELDS},
                timeout=self.timeout,
            )
            if resp.status_code == 404:
                return 0, [], [], f"DOI:{clean_doi}"
            resp.raise_for_status()
            paper = resp.json()
            rec = self._parse_paper(paper, enrich=True)
            return 1, [rec], [rec], f"DOI:{clean_doi}"
        except Exception as e:
            logger.error(f"S2 DOI arama hatası: {e}")
            raise
