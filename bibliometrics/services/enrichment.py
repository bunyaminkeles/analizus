"""
DOI'si olan bibliometri kayıtlarını OpenAlex verisiyle zenginleştirir (Grup B, B1-1).
Mevcut alanların üzerine yazmaz — yalnız eksik olanı doldurur. Ağ hatası tüm işi
düşürmez: log'lanır, sayaçlar 0 kalır.
"""
import logging

logger = logging.getLogger(__name__)


def enrich_records_with_openalex(records: list, stats: dict) -> None:
    """records listesini yerinde günceller. stats'a 'zenginlestirme_*' sayaçları ekler."""
    from forum.models import SiteSettings
    from openalex.services.scraper import OpenAlexScraper

    candidates = [r for r in records if (r.get('doi') or '').strip()]
    stats['zenginlestirme_skipped_no_doi'] = len(records) - len(candidates)

    max_records = SiteSettings.load().bibliometri_openalex_zenginlestirme_max_kayit or 2000
    candidates = candidates[:max_records]

    if not candidates:
        stats['zenginlestirme_enriched'] = 0
        stats['zenginlestirme_not_found'] = 0
        return

    try:
        works_by_doi = OpenAlexScraper().fetch_works_by_dois([c['doi'] for c in candidates])
    except Exception as e:
        logger.error(f"[bibliometrics] OpenAlex zenginleştirme hatası: {e}", exc_info=True)
        stats['zenginlestirme_enriched'] = 0
        stats['zenginlestirme_not_found'] = len(candidates)
        return

    enriched = 0
    for rec in candidates:
        work = works_by_doi.get(rec['doi'].strip().lower())
        if not work:
            continue
        _apply_enrichment(rec, work)
        enriched += 1

    stats['zenginlestirme_enriched'] = enriched
    stats['zenginlestirme_not_found'] = len(candidates) - enriched


def _apply_enrichment(rec: dict, work: dict) -> None:
    """Kayıttaki eksik alanları OpenAlex ham work verisinden doldurur; dolu alana dokunmaz."""
    if not rec.get('cited_by'):
        rec['cited_by'] = work.get('cited_by_count') or 0

    authorships = work.get('authorships') or []

    if not (rec.get('country') or '').strip():
        countries = []
        for auth in authorships:
            for cc in (auth.get('countries') or []):
                if cc and cc not in countries:
                    countries.append(cc)
        if countries:
            rec['country'] = countries[0]

    if not (rec.get('institution') or '').strip():
        institutions = []
        for auth in authorships:
            for inst in (auth.get('institutions') or []):
                name = inst.get('display_name', '')
                if name and name not in institutions:
                    institutions.append(name)
        if institutions:
            rec['institution'] = '; '.join(institutions[:5])

    if not any((k or '').strip() for k in (rec.get('keywords') or [])):
        keywords = [kw.get('display_name') for kw in (work.get('keywords') or []) if kw.get('display_name')]
        if not keywords:
            keywords = [c.get('display_name') for c in (work.get('concepts') or []) if c.get('display_name')]
        if keywords:
            rec['keywords'] = keywords[:5]

    # Faz B2 (ortak atıf ağları, yazar ID ile homonym çözümü) için ham veri — başka yerde
    # doldurulmuyor, bu yüzden her zaman güncellenir.
    rec['referenced_works'] = work.get('referenced_works') or []
    rec['author_ids'] = [
        a.get('author', {}).get('id', '') for a in authorships if a.get('author', {}).get('id')
    ]
    # B2-7: kaydın kendi OpenAlex ID'si — başka kayıtların referenced_works'ünde
    # bu ID geçiyorsa "yerel atıf" (bu veri setindeki iç atıf) sayılabilir.
    rec['openalex_id'] = work.get('id') or ''
