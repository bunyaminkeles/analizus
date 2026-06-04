_SLUG_TO_NAME = {
    'cronbach': 'Cronbach Alpha',
    'normallik': 'Normallik Testi',
    'betimsel': 'Betimsel İstatistik',
    'korelasyon': 'Korelasyon',
    'orneklem': 'Örneklem',
    'ttesti': 't-Testi',
    'anova': 'ANOVA',
    'mann-whitney': 'Mann-Whitney',
    'kruskal-wallis': 'Kruskal-Wallis',
    'ki-kare': 'Ki-Kare',
    'lineer-regresyon': 'Lineer Regresyon',
    'lojistik-regresyon': 'Lojistik Regresyon',
    'friedman': 'Friedman',
    'tekrarli-anova': 'Tekrarlı ANOVA',
    'karar-agaci': 'Karar Ağacı',
    'svm': 'SVM',
    'afa': 'AFA',
}


def resolve_tab_name(path: str) -> str:
    p = path.rstrip('/')
    if p in ('', '/'):
        return 'Ana Sayfa'
    if p.startswith(('/analiz', '/istatistik')):
        parts = [x for x in p.split('/') if x]
        slug = parts[1] if len(parts) > 1 else ''
        if not slug:
            return 'Analiz Hub'
        return 'Analiz: ' + _SLUG_TO_NAME.get(slug, slug.replace('-', ' ').title())
    if p.startswith('/tarama'):
        return 'Akademik Tarama'
    if p.startswith('/yoktez'):
        return 'YÖK Tez'
    if p.startswith('/tezanaliz'):
        return 'Tez Analizi'
    if p.startswith('/makaleanaliz'):
        return 'Makale Analizi'
    if p.startswith('/openalex'):
        return 'OpenAlex'
    if p.startswith('/bibliometrics'):
        return 'Bibliometrik Analiz'
    if p.startswith('/semanticscholar'):
        return 'Semantic Scholar'
    if p.startswith('/oaipmh'):
        return 'OAI-PMH'
    if p.startswith(('/hizmetler', '/market', '/jobs')):
        return 'Pazaryeri'
    if p.startswith('/blog'):
        return 'Blog'
    if p.startswith(('/odalar', '/studyroom')):
        return 'Çalışma Odaları'
    if p.startswith(('/inbox', '/mesajlar')):
        return 'Mesajlar'
    if p.startswith('/profil'):
        return 'Profil'
    if p.startswith('/hangi-test'):
        return 'Test Rehberi'
    if p.startswith('/ai-asistan'):
        return 'AI Asistan'
    if p.startswith('/neden-biz'):
        return 'Neden Biz?'
    if p.startswith(('/quiz', '/arena')):
        return 'İstatistik Arenası'
    if p.startswith(('/forum', '/konu', '/b/')):
        return 'Forum'
    if p.startswith('/onboarding'):
        return 'Onboarding'
    return path[:60]
