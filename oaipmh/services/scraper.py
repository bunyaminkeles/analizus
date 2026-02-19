"""
OAI-PMH Scraper — Türk üniversite açık arşivleri için.

Keyword modu: 19 üniversiteye paralel sorgu, title/abstract filtreleme
Browse modu: Tek üniversitenin tüm tez kayıtları
"""
import logging
import threading
import requests
from sickle import Sickle
from sickle.oaiexceptions import NoRecordsMatch, OAIError
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger(__name__)

MAX_RECORDS_PER_UNI = 500   # keyword modda üniversite başına max kayıt
CONNECT_TIMEOUT = 10        # TCP bağlantı kurma timeout (saniye)
READ_TIMEOUT = 20           # Sunucudan veri okuma timeout (saniye)
THREAD_TIMEOUT = 35         # Üniversite başına hard limit (saniye)
PER_UNI_DEMO = 2            # keyword modda üniversite başına max demo kayıt


def _get_sickle(oai_url):
    """SSL hatalarını yoksayan Sickle istemcisi döndürür."""
    session = requests.Session()
    session.verify = False
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (OAI-Harvest; analizus.com)',
    })
    # Sickle 0.7.0'da session parametresi yok; sickle.session'ı doğrudan atıyoruz.
    # timeout, request_args'a gidiyor ve session.request(timeout=...) olarak iletiliyor.
    sickle = Sickle(oai_url, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT), max_retries=1, verify=False)
    sickle.session = session
    return sickle


def _parse_record(record, university_name=""):
    """Dublin Core OAI kaydını dict'e çevirir."""
    meta = record.metadata
    def get_first(field, default=""):
        values = meta.get(field, [])
        return values[0].strip() if values else default
    def get_all(field):
        return [v.strip() for v in meta.get(field, []) if v.strip()]

    # Yazar: dc.contributor.author > dc.creator
    authors = get_all('contributor') or get_all('creator')
    # Yıl: dc.date'den ilk 4 haneli sayı
    raw_date = get_first('date')
    year = ""
    for part in raw_date.replace('-', ' ').split():
        if part.isdigit() and len(part) == 4:
            year = part
            break
    # Link: dc.identifier içinde http olan ilk değer
    link = ""
    for ident in meta.get('identifier', []):
        if ident.startswith('http'):
            link = ident.strip()
            break

    return {
        'title': get_first('title'),
        'authors': '; '.join(authors[:5]),
        'year': year,
        'abstract': get_first('description'),
        'subject': '; '.join(get_all('subject')[:10]),
        'type': get_first('type'),
        'link': link,
        'university': university_name,
        'publisher': get_first('publisher'),
    }


def _is_thesis(record):
    """Kaydın tez olup olmadığını dc.type üzerinden kontrol eder."""
    meta = record.metadata
    types = [t.lower() for t in meta.get('type', [])]
    thesis_keywords = ['thesis', 'tez', 'masterthesis', 'doctoralthesis',
                       'master', 'doctoral', 'dissertation', 'yüksek lisans', 'doktora']
    return any(kw in ' '.join(types) for kw in thesis_keywords)


def _keyword_matches(record_dict, title_query=None, abstract_query=None):
    """Başlık/özet filtreleri eşleşiyor mu? AND mantığı: belirtilen her filtre eşleşmeli."""
    if not title_query and not abstract_query:
        return True
    if title_query and title_query.lower() not in record_dict['title'].lower():
        return False
    if abstract_query and abstract_query.lower() not in record_dict['abstract'].lower():
        return False
    return True


def _year_in_range(record_dict, year_from, year_to):
    """Kaydın yılı aralıkta mı?"""
    year = record_dict.get('year', '')
    if not year or not year.isdigit():
        return True  # yıl bilinmiyorsa dahil et
    y = int(year)
    if year_from and y < year_from:
        return False
    if year_to and y > year_to:
        return False
    return True


class OAIPMHScraper:

    def search_keyword(self, universities, keyword=None, abstract_query=None,
                       year_from=None, year_to=None, demo_limit=5):
        """
        Birden fazla üniversitede paralel arama.
        keyword: başlık filtresi, abstract_query: özet filtresi (AND mantığı)
        universities: University queryset veya liste
        Returns: (total_count, demo_results, all_results)
        """
        results_lock = threading.Lock()
        all_results = []

        def _search_one(uni):
            try:
                sickle = _get_sickle(uni.oai_url)
                params = {'metadataPrefix': 'oai_dc'}
                if year_from:
                    params['from'] = f"{year_from}-01-01"
                if year_to:
                    params['until'] = f"{year_to}-12-31"

                records = sickle.ListRecords(**params)
                count = 0
                found = []
                for record in records:
                    if count >= MAX_RECORDS_PER_UNI:
                        break
                    count += 1
                    try:
                        parsed = _parse_record(record, uni.name)
                        if not _year_in_range(parsed, year_from, year_to):
                            continue
                        if not _keyword_matches(parsed, title_query=keyword, abstract_query=abstract_query):
                            continue
                        found.append(parsed)
                    except Exception:
                        continue

                with results_lock:
                    all_results.extend(found)
                logger.info(f"OAI-PMH keyword [{uni.name}]: {len(found)} eşleşme / {count} kayıt tarandı")

            except NoRecordsMatch:
                logger.info(f"OAI-PMH [{uni.name}]: Sonuç yok")
            except Exception as e:
                logger.warning(f"OAI-PMH [{uni.name}] hata: {e}")

        threads = [threading.Thread(target=_search_one, args=(uni,)) for uni in universities]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=THREAD_TIMEOUT)

        # Yıla göre sırala (yeni → eski)
        all_results.sort(key=lambda r: r.get('year', '0'), reverse=True)

        total = len(all_results)
        demo = all_results[:demo_limit]
        return total, demo, all_results

    def browse_university(self, university, demo_limit=5):
        """
        Tek üniversitenin tüm tezlerini çeker.
        Returns: (total_count, demo_results, all_results)
        """
        all_results = []
        try:
            sickle = _get_sickle(university.oai_url)
            records = sickle.ListRecords(metadataPrefix='oai_dc')
            count = 0
            for record in records:
                count += 1
                try:
                    parsed = _parse_record(record, university.name)
                    if _is_thesis(record):
                        all_results.append(parsed)
                except Exception:
                    continue

            logger.info(f"OAI-PMH browse [{university.name}]: {len(all_results)} tez / {count} toplam kayıt")

        except NoRecordsMatch:
            logger.info(f"OAI-PMH browse [{university.name}]: Kayıt yok")
        except Exception as e:
            logger.error(f"OAI-PMH browse [{university.name}] hata: {e}")

        # Yıla göre sırala
        all_results.sort(key=lambda r: r.get('year', '0'), reverse=True)

        total = len(all_results)
        demo = all_results[:demo_limit]
        return total, demo, all_results
