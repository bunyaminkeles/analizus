"""
Türk Üniversitelerinin OAI-PMH Endpoint'lerini Keşfeder.

Kullanım:
    python scripts/oai_discover.py

Çıktı:
    - Konsola aktif/pasif sonuçlar
    - oai_endpoints.json (aktif endpoint listesi)

Bağımlılık: sadece requests (pip install requests)
SSL uyarıları kasıtlı olarak susturuldu (devlet üniversitelerinde sertifika sorunları yaygın).
"""

import json
import time
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Türkiye'deki üniversite domainleri
# Kaynak: yok.gov.tr üniversite listesi (manuel derlendi)
UNI_DOMAINS = [
    # Devlet Üniversiteleri
    ("Ankara Üniversitesi", "ankara.edu.tr"),
    ("İstanbul Üniversitesi", "istanbul.edu.tr"),
    ("Hacettepe Üniversitesi", "hacettepe.edu.tr"),
    ("ODTÜ", "metu.edu.tr"),
    ("İTÜ", "itu.edu.tr"),
    ("Ege Üniversitesi", "ege.edu.tr"),
    ("Dokuz Eylül Üniversitesi", "deu.edu.tr"),
    ("Gazi Üniversitesi", "gazi.edu.tr"),
    ("Selçuk Üniversitesi", "selcuk.edu.tr"),
    ("Erciyes Üniversitesi", "erciyes.edu.tr"),
    ("Akdeniz Üniversitesi", "akdeniz.edu.tr"),
    ("Çukurova Üniversitesi", "cu.edu.tr"),
    ("Uludağ Üniversitesi", "uludag.edu.tr"),
    ("Karadeniz Teknik Üniversitesi", "ktu.edu.tr"),
    ("Sakarya Üniversitesi", "sakarya.edu.tr"),
    ("Kocaeli Üniversitesi", "kocaeli.edu.tr"),
    ("Gaziantep Üniversitesi", "gantep.edu.tr"),
    ("Anadolu Üniversitesi", "anadolu.edu.tr"),
    ("Fırat Üniversitesi", "firat.edu.tr"),
    ("İnönü Üniversitesi", "inonu.edu.tr"),
    ("Cumhuriyet Üniversitesi", "cumhuriyet.edu.tr"),
    ("Pamukkale Üniversitesi", "pau.edu.tr"),
    ("Mersin Üniversitesi", "mersin.edu.tr"),
    ("Muğla Sıtkı Koçman Üniversitesi", "mu.edu.tr"),
    ("Balıkesir Üniversitesi", "balikesir.edu.tr"),
    ("Trakya Üniversitesi", "trakya.edu.tr"),
    ("Süleyman Demirel Üniversitesi", "sdu.edu.tr"),
    ("Afyon Kocatepe Üniversitesi", "aku.edu.tr"),
    ("Dumlupınar Üniversitesi", "dpu.edu.tr"),
    ("Adnan Menderes Üniversitesi", "adu.edu.tr"),
    ("Celal Bayar Üniversitesi", "cbu.edu.tr"),
    ("Eskişehir Osmangazi Üniversitesi", "ogu.edu.tr"),
    ("Gebze Teknik Üniversitesi", "gtu.edu.tr"),
    ("Yıldız Teknik Üniversitesi", "yildiz.edu.tr"),
    ("Marmara Üniversitesi", "marmara.edu.tr"),
    ("Boğaziçi Üniversitesi", "boun.edu.tr"),
    ("Galatasaray Üniversitesi", "gsu.edu.tr"),
    ("İstanbul Teknik Üniversitesi", "itu.edu.tr"),
    ("Orta Doğu Teknik Üniversitesi", "metu.edu.tr"),
    ("Ondokuz Mayıs Üniversitesi", "omu.edu.tr"),
    ("Atatürk Üniversitesi", "atauni.edu.tr"),
    ("Dicle Üniversitesi", "dicle.edu.tr"),
    ("Yüzüncü Yıl Üniversitesi", "yyu.edu.tr"),
    ("Gaziosmanpaşa Üniversitesi", "gop.edu.tr"),
    ("Abant İzzet Baysal Üniversitesi", "ibu.edu.tr"),
    ("Kafkas Üniversitesi", "kafkas.edu.tr"),
    ("Mustafa Kemal Üniversitesi", "mku.edu.tr"),
    ("Niğde Ömer Halisdemir Üniversitesi", "ohu.edu.tr"),
    ("Kırıkkale Üniversitesi", "kku.edu.tr"),
    ("Kastamonu Üniversitesi", "kastamonu.edu.tr"),
    ("Bartın Üniversitesi", "bartin.edu.tr"),
    ("Bülent Ecevit Üniversitesi", "beun.edu.tr"),
    ("Recep Tayyip Erdoğan Üniversitesi", "erdogan.edu.tr"),
    ("Giresun Üniversitesi", "giresun.edu.tr"),
    ("Ordu Üniversitesi", "odu.edu.tr"),
    ("Sinop Üniversitesi", "sinop.edu.tr"),
    ("Hitit Üniversitesi", "hitit.edu.tr"),
    ("Nevşehir Hacı Bektaş Veli Üniversitesi", "nevsehir.edu.tr"),
    ("Kırşehir Ahi Evran Üniversitesi", "ahievran.edu.tr"),
    ("Aksaray Üniversitesi", "aksaray.edu.tr"),
    ("Karaman Mehmet Akif Ersoy Üniversitesi", "mehmetakif.edu.tr"),
    ("Isparta Uygulamalı Bilimler Üniversitesi", "isparta.edu.tr"),
    ("Burdur Mehmet Akif Ersoy Üniversitesi", "mehmetakif.edu.tr"),
    ("Uşak Üniversitesi", "usak.edu.tr"),
    ("Manisa Celal Bayar Üniversitesi", "cbu.edu.tr"),
    ("Kütahya Dumlupınar Üniversitesi", "dpu.edu.tr"),
    ("Bilecik Şeyh Edebali Üniversitesi", "bilecik.edu.tr"),
    ("Bolu Abant İzzet Baysal Üniversitesi", "ibu.edu.tr"),
    ("Düzce Üniversitesi", "duzce.edu.tr"),
    ("Zonguldak Bülent Ecevit Üniversitesi", "beun.edu.tr"),
    # Vakıf Üniversiteleri
    ("Sabancı Üniversitesi", "sabanciuniv.edu"),
    ("Koç Üniversitesi", "ku.edu.tr"),
    ("Bilkent Üniversitesi", "bilkent.edu.tr"),
    ("Başkent Üniversitesi", "baskent.edu.tr"),
    ("Atılım Üniversitesi", "atilim.edu.tr"),
    ("TOBB ETÜ", "etu.edu.tr"),
    ("Özyeğin Üniversitesi", "ozyegin.edu.tr"),
    ("İzmir Ekonomi Üniversitesi", "ieu.edu.tr"),
]

# DSpace için standart URL kalıpları (öncelik sırasıyla)
DSPACE_PATTERNS = [
    "https://dspace.{domain}/oai/request",
    "http://dspace.{domain}/oai/request",
    "https://acikarsiv.{domain}/oai/request",
    "http://acikarsiv.{domain}/oai/request",
    "https://openaccess.{domain}/oai/request",
    "http://openaccess.{domain}/oai/request",
    "https://repository.{domain}/oai/request",
    "http://repository.{domain}/oai/request",
    "https://earsiv.{domain}/oai/request",
    "http://earsiv.{domain}/oai/request",
    "https://open.{domain}/oai/request",
    "http://open.{domain}/oai/request",
]

# EPrints için (Sabancı vb.)
EPRINTS_PATTERNS = [
    "https://research.{domain}/cgi/oai2",
    "http://research.{domain}/cgi/oai2",
    "https://{domain}/cgi/oai2",
]

ALL_PATTERNS = DSPACE_PATTERNS + EPRINTS_PATTERNS

TIMEOUT = 6
SLEEP_BETWEEN = 0.5  # saniye (firewall'ları tetiklememek için)


def check_oai_endpoint(url):
    """OAI-PMH endpoint'ini test eder. (name, url) veya None döner."""
    try:
        resp = requests.get(
            f"{url}?verb=Identify",
            timeout=TIMEOUT,
            verify=False,
            headers={"User-Agent": "Mozilla/5.0 (research; oai-harvest)"},
        )
        if resp.status_code == 200 and "repositoryName" in resp.text:
            # Repository adını XML'den çek
            import re
            match = re.search(r"<repositoryName>(.*?)</repositoryName>", resp.text)
            repo_name = match.group(1) if match else ""
            return repo_name
    except Exception:
        pass
    return None


def discover():
    valid = []
    not_found = []

    print(f"\n{'='*60}")
    print(f"OAI-PMH Endpoint Keşfi Başlıyor ({len(UNI_DOMAINS)} üniversite)")
    print(f"{'='*60}\n")

    for uni_name, domain in UNI_DOMAINS:
        found = False
        for pattern in ALL_PATTERNS:
            url = pattern.format(domain=domain)
            repo_name = check_oai_endpoint(url)
            if repo_name is not None:
                print(f"  BULUNDU: {uni_name}")
                print(f"           {url}")
                print(f"           Repo: {repo_name}\n")
                valid.append({
                    "university": uni_name,
                    "domain": domain,
                    "oai_url": url,
                    "repo_name": repo_name,
                })
                found = True
                break
            time.sleep(0.1)

        if not found:
            print(f"  - Bulunamadı: {uni_name} ({domain})")
            not_found.append({"university": uni_name, "domain": domain})

        time.sleep(SLEEP_BETWEEN)

    # Sonuçları kaydet
    output_path = "scripts/oai_endpoints.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(valid, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"SONUÇ: {len(valid)} aktif endpoint bulundu / {len(UNI_DOMAINS)} üniversite")
    print(f"Aktif endpoint listesi: {output_path}")
    print(f"{'='*60}\n")

    return valid, not_found


if __name__ == "__main__":
    discover()
