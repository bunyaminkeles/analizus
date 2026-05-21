import requests
import logging
import time
import random
import threading

logger = logging.getLogger(__name__)

API_BASE = "https://search.trdizin.gov.tr/api/defaultSearch/publication/"
MAX_PAGE_SIZE = 100

# Aynı anda en fazla 3 job TR Dizin API'sine istek atabilir.
_trdizin_semaphore = threading.Semaphore(3)

_USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
]


class TRDizinScraper:
    """TR Dizin REST API client."""

    def __init__(self, timeout=30, max_retries=3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': random.choice(_USER_AGENTS),
            'Accept': 'application/json',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8',
            'DNT': '1',
        })

    @staticmethod
    def parse_abstract_filter(query_parts):
        """
        query_parts içinden özet filtresini ayıklar.
        TR Dizin API'sinde 'abstract' alan adı Lucene sorgusunda çalışmıyor
        (API'deki gerçek alan adı 'abstracts'); lokal filtreleme yapılır.
        Returns: str veya ''
        """
        for part in query_parts:
            if part.get('field') == 'abstract':
                return part.get('value', '').strip()
        return ''

    @staticmethod
    def parse_year_filter(query_parts):
        """
        query_parts içinden yıl filtresini ayıklar.
        Returns: (year_from, year_to) veya (None, None)

        TR Dizin API'sinin Lucene `year` ve `publicationYear` alanları
        sunucu tarafında güvenilir çalışmıyor; yıl filtrelemesi lokal yapılır.
        """
        for part in query_parts:
            if part.get('field') == 'year':
                val = part.get('value', '').strip()
                parts = val.split('-')
                if len(parts) == 2:
                    try:
                        return int(parts[0].strip()), int(parts[1].strip())
                    except ValueError:
                        pass
                elif val.isdigit():
                    y = int(val)
                    return y, y
        return None, None

    def build_lucene_query(self, query_parts):
        """
        Yapısal sorgu parçalarını Lucene query string'e çevirir.
        NOT: year alanı lokal filtreleme için ayrıştırılır, Lucene sorgusuna dahil edilmez.

        query_parts: [
            {"field": "title", "value": "ankara", "operator": "AND"},
            {"field": "abstract", "value": "sağlık AND yönetimi", "operator": "AND"},
            {"field": "year", "value": "2020-2022", "operator": "AND"},
        ]
        """
        clauses = []

        for part in query_parts:
            field = part.get('field', '')
            value = part.get('value', '').strip()
            if not value:
                continue

            if field in ('year', 'abstract'):
                # Lokal filtreleme — API'de güvenilir çalışmıyor
                continue
            else:
                # Alanlar: title, abstract, author, keyword, doi
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

            clauses.append((clause, part.get('operator', 'AND')))

        if not clauses:
            return '*'

        # Parçaları operatörlerle birleştir
        result_parts = []
        for i, (clause, operator) in enumerate(clauses):
            if i > 0:
                result_parts.append(f' {operator} ')
            result_parts.append(clause)

        query = ''.join(result_parts)
        return f'({query})'

    def _fetch_page(self, lucene_query, page=1, limit=20, order='publicationYear-DESC'):
        """TR Dizin API'den tek sayfa sonuç çeker. 429/503'te backoff ile yeniden dener."""
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
                if response.status_code in (429, 503) and attempt < self.max_retries - 1:
                    wait = random.uniform(5.0, 10.0) * (attempt + 1)
                    logger.warning(f"TR Dizin rate limit ({response.status_code}), {wait:.1f}s bekleniyor...")
                    time.sleep(wait)
                    continue
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                logger.warning(f"TR Dizin API attempt {attempt+1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt + random.uniform(0.5, 1.5))
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
        - all_results: Tüm sonuçlar (yıl filtresi uygulanmış)
        - lucene_query: Oluşturulan Lucene sorgusu
        """
        with _trdizin_semaphore:
            return self._search_impl(query_parts, demo_limit)

    def _search_impl(self, query_parts, demo_limit=3):
        lucene_query = self.build_lucene_query(query_parts)
        year_from, year_to = self.parse_year_filter(query_parts)
        abstract_filter = self.parse_abstract_filter(query_parts)
        logger.info(f"TR Dizin arama: {lucene_query}  yıl_filtresi={year_from}-{year_to}  özet_filtresi={abstract_filter!r}")

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
                time.sleep(random.uniform(0.5, 1.5))  # API'ye saygılı ol
            except Exception as e:
                logger.error(f"TR Dizin pagination hatası (sayfa {page}): {e}")
                break

            # Maksimum sonuç limiti (admin panelinden ayarlanabilir)
            from forum.models import SiteSettings
            max_records = SiteSettings.load().scrap_max_records or 5000
            if len(all_results) >= max_records:
                logger.info(f"Maksimum sonuç limitine ulaşıldı: {len(all_results)}")
                break

        # Lokal yıl filtresi — TR Dizin API Lucene yıl alanı güvenilir çalışmıyor
        if year_from or year_to:
            before = len(all_results)
            all_results = [
                r for r in all_results
                if self._year_in_range(r.get('year'), year_from, year_to)
            ]
            total_count = len(all_results)
            demo_results = all_results[:demo_limit]
            logger.info(f"TR Dizin yıl filtresi ({year_from}-{year_to}): {before} → {total_count} kayıt")

        # Lokal özet filtresi — API'de 'abstract' alan adı tanınmıyor
        if abstract_filter:
            before = len(all_results)
            all_results = [
                r for r in all_results
                if self._abstract_matches(r, abstract_filter)
            ]
            total_count = len(all_results)
            demo_results = all_results[:demo_limit]
            logger.info(f"TR Dizin özet filtresi ({abstract_filter!r}): {before} → {total_count} kayıt")

        logger.info(f"TR Dizin arama tamamlandı: {total_count} toplam, {len(all_results)} çekildi")
        return total_count, demo_results, all_results, lucene_query

    @staticmethod
    def _abstract_matches(record: dict, filter_value: str) -> bool:
        """
        Kayıt özetinin filtre değerini içerip içermediğini kontrol eder.
        Çok kelimeli değerler AND mantığıyla, 'OR' içerenler OR mantığıyla değerlendirilir.
        """
        combined = (
            (record.get('abstract_tr') or '') + ' ' +
            (record.get('abstract_en') or '')
        ).lower()

        if ' OR ' in filter_value.upper():
            terms = [t.strip().lower() for t in filter_value.upper().split(' OR ')]
            return any(t in combined for t in terms)
        elif ' AND ' in filter_value.upper():
            terms = [t.strip().lower() for t in filter_value.upper().split(' AND ')]
            return all(t in combined for t in terms)
        else:
            # Tek veya çok kelime — tümü bulunmalı (AND)
            terms = [t.lower() for t in filter_value.split()]
            return all(t in combined for t in terms)

    @staticmethod
    def _year_in_range(year, year_from, year_to):
        """Yıl değeri verilen aralıkta mı?"""
        if year is None:
            return True
        try:
            y = int(year)
        except (TypeError, ValueError):
            return True
        if year_from and y < year_from:
            return False
        if year_to and y > year_to:
            return False
        return True
