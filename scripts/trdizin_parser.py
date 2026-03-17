"""
TR Dizin TXT → Tableau CSV Parser
Analizus - www.analizus.com

Kullanım:
    python trdizin_parser.py dosya_adi.txt

Çıktı:
    dosya_adi_tableau.csv (aynı klasöre kaydeder)
"""

import csv, re, sys, os
from collections import Counter

# ── DOSYA YOLU ──
if len(sys.argv) > 1:
    input_file = sys.argv[1]
else:
    input_file = input("TR Dizin TXT dosya yolunu girin: ").strip()

if not os.path.exists(input_file):
    print(f"HATA: '{input_file}' bulunamadı!")
    sys.exit(1)

output_csv = os.path.splitext(input_file)[0] + '_tableau.csv'

# ── 1. PARSE ──
records = []
current = {}
current_field = None

with open(input_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n')
        if line.startswith('--- Yayın #'):
            if current and 'Başlık' in current:
                records.append(current)
            current = {'No': re.search(r'#(\d+)', line).group(1)}
            current_field = None
        elif line.startswith('Başlık    : '):
            current['Başlık'] = line[12:]; current_field = 'Başlık'
        elif line.startswith('Yazarlar  : '):
            current['Yazarlar'] = line[12:]; current_field = 'Yazarlar'
        elif line.startswith('Dergi     : '):
            current['Dergi'] = line[12:]; current_field = 'Dergi'
        elif line.startswith('Yıl       : '):
            current['Yıl'] = line[12:].strip(); current_field = 'Yıl'
        elif line.startswith('DOI       : '):
            current['DOI'] = line[12:]; current_field = 'DOI'
        elif line.startswith('Dil       : '):
            current['Dil'] = line[12:].strip(); current_field = 'Dil'
        elif line.startswith('Tür       : '):
            current['Tür'] = line[12:].strip(); current_field = 'Tür'
        elif line.startswith('Anahtar   : '):
            current['Anahtar'] = line[12:]; current_field = 'Anahtar'
        elif line.startswith('Özet      : '):
            current['Özet'] = line[12:]; current_field = 'Özet'
        elif line.strip() and current_field == 'Özet' and not line.startswith('---') and not line.startswith('==='):
            current['Özet'] = current.get('Özet', '') + ' ' + line.strip()

if current and 'Başlık' in current:
    records.append(current)

print(f"✓ Parse edilen: {len(records)} yayın")

# ── 2. KONU SINIFLANDIRMA SÖZLÜĞÜ ──
keywords_map = {
    'Yapay Zeka': ['yapay zeka', 'artificial intelligence', 'makine öğren', 'machine learn', 'derin öğrenme', 'deep learning'],
    'COVID-19': ['covid', 'pandemi', 'salgın', 'koronavirüs', 'coronavirus'],
    'Sağlık Okuryazarlığı': ['sağlık okuryazarlığı', 'health literacy'],
    'Ruh Sağlığı': ['ruh sağlığı', 'mental', 'psikoloj', 'depresyon', 'anksiyete', 'tükenmişlik', 'burnout', 'stres'],
    'Hemşirelik': ['hemşire', 'nursing', 'nurse'],
    'Sağlık Yönetimi': ['sağlık yönetim', 'hastane yönetim', 'sağlık hizmet', 'health management', 'sağlık kurum'],
    'Sağlık Politikası': ['sağlık politika', 'health policy', 'sağlık sigorta', 'sosyal güven'],
    'Sağlık Turizmi': ['sağlık turizm', 'medikal turizm', 'health tourism'],
    'Dijital Sağlık': ['dijital sağlık', 'e-sağlık', 'telesağlık', 'telehealth', 'mobil sağlık', 'mhealth'],
    'Beslenme': ['beslenme', 'diyet', 'obezite', 'nutrition', 'gıda'],
    'İş Sağlığı': ['iş sağlığı', 'iş güvenliği', 'meslek hastalık', 'occupational'],
    'Yaşlı Sağlığı': ['yaşlı', 'geriatri', 'aging', 'elderly'],
    'Kadın Sağlığı': ['kadın sağlığ', 'gebe', 'anne', 'maternal', 'doğum'],
    'Çocuk Sağlığı': ['çocuk sağlığ', 'pediatr', 'bebek', 'yenidoğan'],
    'Kronik Hastalık': ['kronik', 'diyabet', 'hipertansiyon', 'kanser', 'cancer', 'kardiyovasküler'],
    'Eğitim': ['eğitim', 'öğrenci', 'müfredat', 'education', 'training'],
    'Etik': ['etik', 'ethics', 'biyoetik'],
}

# ── 3. YÖNTEM TESPİT SÖZLÜĞÜ ──
method_keywords = {
    'Nicel': ['nicel', 'quantitative', 'anket', 'ölçek', 'istatistik', 'regresyon', 'anova', 'spss', 'korelasyon', 't testi', 'ki kare', 'varyans'],
    'Nitel': ['nitel', 'qualitative', 'fenomenoloj', 'görüşme', 'mülakat', 'tematik analiz', 'içerik analiz'],
    'Karma': ['karma', 'mixed method'],
    'Derleme': ['derleme', 'review', 'sistematik', 'meta-analiz', 'meta analiz', 'literatür taramas'],
    'Deneysel': ['deneysel', 'experimental', 'randomize', 'rct', 'kontrol grubu'],
    'Kesitsel': ['kesitsel', 'cross-sectional', 'cross sectional'],
    'Bibliyometrik': ['bibliyometri', 'bibliometric', 'vosviewer'],
}

# ── 4. ZENGİNLEŞTİRME ──
for rec in records:
    combined = (rec.get('Başlık', '') + ' ' + rec.get('Özet', '') + ' ' + rec.get('Anahtar', '')).lower()

    # Yazar bilgileri
    authors = [a.strip() for a in rec.get('Yazarlar', '').split(',') if a.strip()]
    rec['Yazar Sayısı'] = len(authors)
    rec['İlk Yazar'] = authors[0] if authors else ''

    # Kelime sayıları
    rec['Başlık Kelime Sayısı'] = len(rec.get('Başlık', '').split())
    rec['Özet Kelime Sayısı'] = len(rec.get('Özet', '').split())

    # DOI varlığı
    rec['DOI Var'] = 'Evet' if rec.get('DOI', '').strip() else 'Hayır'

    # Dil normalizasyonu
    dil_raw = rec.get('Dil', '').upper()
    if dil_raw in ('TUR', 'TR'):
        rec['Dil Etiketi'] = 'Türkçe'
    elif dil_raw in ('ENG', 'EN'):
        rec['Dil Etiketi'] = 'İngilizce'
    elif dil_raw:
        rec['Dil Etiketi'] = dil_raw
    else:
        # Başlıktan tahmin et
        has_eng = bool(re.search(r'[A-Za-z]{5,}', rec.get('Başlık', '')))
        has_tr = bool(re.search(r'[çğışöüÇĞİŞÖÜ]', rec.get('Başlık', '')))
        rec['Dil Etiketi'] = 'Türkçe' if has_tr and not has_eng else ('İngilizce' if has_eng and not has_tr else 'Çift Dilli/Karma')

    # Konu sınıflandırma
    topics = [t for t, kws in keywords_map.items() if any(k in combined for k in kws)]
    rec['Ana Konu'] = topics[0] if topics else 'Diğer'
    rec['Tüm Konular'] = '; '.join(topics) if topics else 'Diğer'
    rec['Konu Sayısı'] = len(topics) if topics else 1

    # Araştırma yöntemi
    methods = [m for m, kws in method_keywords.items() if any(k in combined for k in kws)]
    rec['Araştırma Yöntemi'] = methods[0] if methods else 'Belirtilmemiş'

    # Dergi alan sınıflandırma
    dergi = rec.get('Dergi', '').lower()
    if any(x in dergi for x in ['hemşire', 'nursing']): rec['Dergi Alanı'] = 'Hemşirelik'
    elif any(x in dergi for x in ['tıp', 'medical', 'klinik']): rec['Dergi Alanı'] = 'Tıp'
    elif any(x in dergi for x in ['sağlık bilim', 'health sci']): rec['Dergi Alanı'] = 'Sağlık Bilimleri'
    elif any(x in dergi for x in ['sosyal', 'social']): rec['Dergi Alanı'] = 'Sosyal Bilimler'
    elif any(x in dergi for x in ['halk sağlığı', 'public health']): rec['Dergi Alanı'] = 'Halk Sağlığı'
    elif any(x in dergi for x in ['beslenme', 'diyet', 'nutrition']): rec['Dergi Alanı'] = 'Beslenme'
    elif any(x in dergi for x in ['işletme', 'yönetim', 'management']): rec['Dergi Alanı'] = 'Yönetim'
    elif any(x in dergi for x in ['eğitim', 'education']): rec['Dergi Alanı'] = 'Eğitim'
    else: rec['Dergi Alanı'] = 'Diğer'

# ── 5. CSV YAZMA ──
fields = [
    'No', 'Başlık', 'İlk Yazar', 'Yazarlar', 'Yazar Sayısı',
    'Dergi', 'Dergi Alanı', 'Yıl', 'DOI', 'DOI Var',
    'Dil', 'Dil Etiketi', 'Tür', 'Anahtar',
    'Ana Konu', 'Tüm Konular', 'Konu Sayısı',
    'Araştırma Yöntemi',
    'Başlık Kelime Sayısı', 'Özet Kelime Sayısı',
]

with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(records)

# ── 6. ÖZET RAPOR ──
print(f"✓ CSV kaydedildi: {output_csv}")
print(f"\n{'='*50}")
print(f"  ÖZET İSTATİSTİKLER")
print(f"{'='*50}")
print(f"  Toplam yayın  : {len(records)}")
print(f"  Farklı dergi  : {len(set(r['Dergi'] for r in records))}")
years = [r['Yıl'] for r in records if r.get('Yıl')]
if years:
    print(f"  Yıl aralığı   : {min(years)} - {max(years)}")

print(f"\n--- Konu Dağılımı (Top 10) ---")
for t, c in Counter(r['Ana Konu'] for r in records).most_common(10):
    bar = '█' * (c // 20)
    print(f"  {t:<25} {c:>5}  {bar}")

print(f"\n--- Araştırma Yöntemi ---")
for m, c in Counter(r['Araştırma Yöntemi'] for r in records).most_common():
    bar = '█' * (c // 20)
    print(f"  {m:<20} {c:>5}  {bar}")

print(f"\n--- Yıl Dağılımı ---")
for y, c in sorted(Counter(r['Yıl'] for r in records if r.get('Yıl')).items()):
    bar = '█' * (c // 15)
    print(f"  {y}: {c:>5}  {bar}")

print(f"\n✓ Tableau'ya yüklemek için: {output_csv} dosyasını kullanın")
