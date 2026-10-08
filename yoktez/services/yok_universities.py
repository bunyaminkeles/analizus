"""
YÖK Tez Merkezi'nin 'Universite' arama parametresi için eski/sayısal ID -> isim
haritası. Yeni arayüzün ürettiği opak 'kod' değeri bu alanda ÇALIŞMIYOR — canlı
test (8 Ekim 2026) sonucu YÖK'ün SearchTez uç noktasının hâlâ eski, küçük, sıralı
sayısal bir ID beklediği doğrulandı. Harita, tek seferlik kontrollü bir tarama ile
(her ID için "istatistik" anahtar kelimesiyle arama + ilk sonucun "yer" alanından
üniversite adı okuma) çıkarıldı.

NOT: Bu liste TAM değil — ID 1-80 arası tarandı (81-260 aralığı YÖK'ün ardışık
isteklerde bağlantıyı kesmesi nedeniyle tamamlanamadı, 8 Ekim 2026). ~140 üniversite
daha eksik; tam liste için daha yavaş, ayrı bir oturumda tekrar taranmalı.
"""

UNIVERSITE_ID_BY_NAME = {
    'AKDENİZ ÜNİVERSİTESİ': '1',
    'ANADOLU ÜNİVERSİTESİ': '2',
    'ANKARA ÜNİVERSİTESİ': '3',
    'ATATÜRK ÜNİVERSİTESİ': '4',
    'İHSAN DOĞRAMACI BİLKENT ÜNİVERSİTESİ': '5',
    'BOĞAZİÇİ ÜNİVERSİTESİ': '6',
    'CUMHURİYET ÜNİVERSİTESİ': '7',
    'ÇUKUROVA ÜNİVERSİTESİ': '8',
    'DİCLE ÜNİVERSİTESİ': '9',
    'DOKUZ EYLÜL ÜNİVERSİTESİ': '10',
    'EGE ÜNİVERSİTESİ': '11',
    'ERCİYES ÜNİVERSİTESİ': '12',
    'FIRAT ÜNİVERSİTESİ': '13',
    'GAZİ ÜNİVERSİTESİ': '14',
    'GAZİANTEP ÜNİVERSİTESİ': '15',
    'HACETTEPE ÜNİVERSİTESİ': '16',
    'İNÖNÜ ÜNİVERSİTESİ': '17',
    'İSTANBUL TEKNİK ÜNİVERSİTESİ': '18',
    'İSTANBUL ÜNİVERSİTESİ': '19',
    'KARADENİZ TEKNİK ÜNİVERSİTESİ': '20',
    'MARMARA ÜNİVERSİTESİ': '21',
    'MİMAR SİNAN GÜZEL SANATLAR ÜNİVERSİTESİ': '22',
    'ONDOKUZ MAYIS ÜNİVERSİTESİ': '23',
    'ORTA DOĞU TEKNİK ÜNİVERSİTESİ': '24',
    'SELÇUK ÜNİVERSİTESİ': '25',
    'TRAKYA ÜNİVERSİTESİ': '26',
    'ULUDAĞ ÜNİVERSİTESİ': '27',
    'YILDIZ TEKNİK ÜNİVERSİTESİ': '28',
    'YÜZÜNCÜ YIL ÜNİVERSİTESİ': '29',
    'ABANT İZZET BAYSAL ÜNİVERSİTESİ': '30',
    'ADNAN MENDERES ÜNİVERSİTESİ': '31',
    'AFYON KOCATEPE ÜNİVERSİTESİ': '32',
    'BALIKESİR ÜNİVERSİTESİ': '33',
    'BAŞKENT ÜNİVERSİTESİ': '34',
    'CELAL BAYAR ÜNİVERSİTESİ': '35',
    'ÇANAKKALE ONSEKİZ MART ÜNİVERSİTESİ': '36',
    'DUMLUPINAR ÜNİVERSİTESİ': '37',
    'GAZİOSMANPAŞA ÜNİVERSİTESİ': '38',
    'GEBZE YÜKSEK TEKNOLOJİ ENSTİTÜSÜ': '39',
    'HARRAN ÜNİVERSİTESİ': '40',
    'İZMİR YÜKSEK TEKNOLOJİ ENSTİTÜSÜ': '41',
    'KAFKAS ÜNİVERSİTESİ': '42',
    'KAHRAMANMARAŞ SÜTÇÜ İMAM ÜNİVERSİTESİ': '43',
    'KIRIKKALE ÜNİVERSİTESİ': '44',
    'KOCAELİ ÜNİVERSİTESİ': '45',
    'KOÇ ÜNİVERSİTESİ': '46',
    'MERSİN ÜNİVERSİTESİ': '47',
    'MUĞLA ÜNİVERSİTESİ': '48',
    'MUSTAFA KEMAL ÜNİVERSİTESİ': '49',
    'NİĞDE ÜNİVERSİTESİ': '50',
    'PAMUKKALE ÜNİVERSİTESİ': '51',
    'SAKARYA ÜNİVERSİTESİ': '52',
    'SÜLEYMAN DEMİREL ÜNİVERSİTESİ': '53',
    'ZONGULDAK KARAELMAS ÜNİVERSİTESİ': '54',
    'SAĞLIK BAKANLIĞI': '55',
    'ESKİŞEHİR OSMANGAZİ ÜNİVERSİTESİ': '57',
    'GALATASARAY ÜNİVERSİTESİ': '58',
    'YEDİTEPE ÜNİVERSİTESİ': '60',
    'RECEP TAYYİP ERDOĞAN ÜNİVERSİTESİ': '61',
    'FATİH ÜNİVERSİTESİ': '63',
    'ATILIM ÜNİVERSİTESİ': '64',
    'BAHÇEŞEHİR ÜNİVERSİTESİ': '65',
    'BEYKENT ÜNİVERSİTESİ': '66',
    'ÇANKAYA ÜNİVERSİTESİ': '68',
    'DOĞUŞ ÜNİVERSİTESİ': '69',
    'HALİÇ ÜNİVERSİTESİ': '70',
    'IŞIK ÜNİVERSİTESİ': '71',
}

_NAME_BY_ID = {v: k for k, v in UNIVERSITE_ID_BY_NAME.items()}


def get_universite_id(name: str) -> str:
    """Üniversite adından YÖK'ün eski sayısal ID'sini döner; eşleşme yoksa '0' (tümü)."""
    if not name:
        return '0'
    return UNIVERSITE_ID_BY_NAME.get(name.strip(), '0')


def universite_choices():
    """Form <select> için (value, label) listesi — alfabetik, 'Tümü' en başta."""
    names = sorted(UNIVERSITE_ID_BY_NAME.keys())
    return [('', 'Tümü')] + [(name, name) for name in names]
