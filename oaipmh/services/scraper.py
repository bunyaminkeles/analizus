"""
OAI-PMH Scraper — Türk üniversite açık arşivleri için.

Keyword modu: 19 üniversiteye paralel sorgu, title/abstract filtreleme
Browse modu: Tek üniversitenin tüm tez kayıtları
"""
import logging
import threading
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from sickle import Sickle
from sickle.oaiexceptions import NoRecordsMatch, OAIError
logger = logging.getLogger(__name__)

MAX_RECORDS_PER_UNI = 2000  # keyword modda üniversite başına max kayıt
CONNECT_TIMEOUT = 15        # TCP bağlantı kurma timeout (saniye)
READ_TIMEOUT = 60           # Sunucudan veri okuma timeout (saniye) — DSpace sayfalama için uzun tutuldu
THREAD_TIMEOUT = 180        # Üniversite başına hard limit (saniye)
PER_UNI_DEMO = 2            # keyword modda üniversite başına max demo kayıt


def _get_sickle(oai_url):
    """Retry adapter + uzun timeout ile Sickle istemcisi döndürür."""
    session = requests.Session()
    # urllib3 düzeyinde retry: ConnectionReset, read timeout, 5xx yanıtlar için
    retry = Retry(
        total=3,
        connect=3,       # bağlantı hatalarında yeniden dene (ConnectionResetError dahil)
        read=2,          # okuma timeout'larında yeniden dene
        backoff_factor=1,  # 0s, 1s, 2s arasında bekle
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update({'User-Agent': 'Mozilla/5.0 (OAI-Harvest; analizus.com)'})
    # Sickle'ın kendi max_retries'ını 0 bırakıyoruz — retry'ı urllib3 katmanı yapıyor
    sickle = Sickle(oai_url, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT), max_retries=0, verify=False)
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
    """
    Kaydın tez olup olmadığını dc.type üzerinden kontrol eder.
    dc:type boşsa dahil et — çoğu Türk üniversitesi bu alanı doldurmaz.
    Sadece açıkça makale/kitap olduğu belli olanları çıkar.
    """
    meta = record.metadata
    types = [t.lower() for t in meta.get('type', [])]
    if not types:
        return True  # dc:type yoksa varsayılan olarak dahil et
    joined = ' '.join(types)
    non_thesis = ['article', 'journalarticle', 'journal article', 'book',
                  'bookchapter', 'book chapter', 'conference', 'preprint',
                  'report', 'makale', 'bildiri', 'dataset']
    if any(kw in joined for kw in non_thesis):
        return False
    return True


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
            count = 0
            matched = 0
            try:
                sickle = _get_sickle(uni.oai_url)
                # Tarih parametrelerini sunucuya gönderme — çoğu üniversite OAI-PMH sunucusu
                # from/until'i desteklemez ve NoRecordsMatch döndürür.
                # Yıl filtresi _year_in_range ile lokal yapılır.
                records = sickle.ListRecords(metadataPrefix='oai_dc')
                try:
                    for record in records:
                        if count >= MAX_RECORDS_PER_UNI:
                            break
                        count += 1
                        try:
                            if not _is_thesis(record):
                                continue
                            parsed = _parse_record(record, uni.name)
                            if not _year_in_range(parsed, year_from, year_to):
                                continue
                            if not _keyword_matches(parsed, title_query=keyword, abstract_query=abstract_query):
                                continue
                            with results_lock:
                                all_results.append(parsed)
                            matched += 1
                        except Exception:
                            continue
                except Exception as e:
                    logger.warning(f"OAI-PMH [{uni.name}] sayfalama hatası ({count} kayıt tarandı): {e}")

            except NoRecordsMatch:
                logger.info(f"OAI-PMH [{uni.name}]: Sonuç yok")
            except Exception as e:
                logger.warning(f"OAI-PMH [{uni.name}] bağlantı hatası: {e}")

            logger.info(f"OAI-PMH keyword [{uni.name}]: {matched} eşleşme / {count} kayıt tarandı")

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

    def browse_university(self, university, demo_limit=5, max_records=5000):
        """
        Tek üniversitenin tüm tezlerini çeker.
        Returns: (total_count, demo_results, all_results)
        """
        all_results = []
        count = 0
        try:
            sickle = _get_sickle(university.oai_url)
            records = sickle.ListRecords(metadataPrefix='oai_dc')
            try:
                for record in records:
                    if count >= max_records:
                        logger.info(f"OAI-PMH browse [{university.name}]: max kayıt limitine ulaşıldı ({max_records})")
                        break
                    count += 1
                    try:
                        parsed = _parse_record(record, university.name)
                        if _is_thesis(record):
                            all_results.append(parsed)
                    except Exception:
                        continue
            except Exception as e:
                logger.warning(f"OAI-PMH browse [{university.name}] sayfalama hatası ({count} kayıt tarandı): {e}")

        except NoRecordsMatch:
            logger.info(f"OAI-PMH browse [{university.name}]: Kayıt yok")
        except Exception as e:
            logger.error(f"OAI-PMH browse [{university.name}] bağlantı hatası: {e}")

        logger.info(f"OAI-PMH browse [{university.name}]: {len(all_results)} tez / {count} toplam kayıt")

        # Yıla göre sırala
        all_results.sort(key=lambda r: r.get('year', '0'), reverse=True)

        total = len(all_results)
        demo = all_results[:demo_limit]
        return total, demo, all_results
