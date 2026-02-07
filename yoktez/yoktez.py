"""
YÖK Tez Merkezi - Keyword bazlı tez arama scripti
Kullanım: python yoktez.py --konu "Halk Sağlığı" --keyword "obezite"
"""

import sys
import time
import re
import json
import numpy as np
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

URL = "https://tez.yok.gov.tr/UlusalTezMerkezi/"

# --- Driver ---
def get_driver(headless=False):
    ua = UserAgent()
    options = uc.ChromeOptions()
    options.add_argument(f'user-agent={ua.random}')
    if headless:
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
    driver = uc.Chrome(options=options, version_main=144)
    driver.get(URL)
    time.sleep(3)
    return driver

# --- Tarama sayfasına git ---
def click_tarama(driver):
    driver.find_element(By.XPATH, '//*[@id="navigation2"]/ul/li[2]/a').click()
    time.sleep(3)

# --- Konu seçimi ---
def konu_sec(driver, konu_adi):
    """Konu alanına bilim alanı adını yazar (ör: 'Halk Sağlığı')"""
    el = driver.find_element(By.ID, 'konu')
    el.click()
    time.sleep(1)
    # Yeni pencere açıldıysa popup'tan seç, açılmadıysa text yaz
    if len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(2)
        driver.find_element(By.LINK_TEXT, konu_adi).click()
        time.sleep(1)
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(1)
    else:
        el.clear()
        el.send_keys(konu_adi)
        time.sleep(0.5)

def set_tez_adi(driver, keyword):
    """Tarama formundaki 'Tez Adı' alanına keyword girer (Row 4)"""
    el = driver.find_element(By.NAME, 'TezAd')
    el.clear()
    el.send_keys(keyword)
    time.sleep(0.5)

def set_dizin(driver, keyword):
    """Tarama formundaki 'Dizin' alanına keyword girer (Row 7)"""
    el = driver.find_element(By.NAME, 'Dizin')
    el.clear()
    el.send_keys(keyword)
    time.sleep(0.5)

def set_ozet(driver, keyword):
    """Tarama formundaki 'Özet' alanına keyword girer (Row 7)"""
    el = driver.find_element(By.NAME, 'Metin')
    el.clear()
    el.send_keys(keyword)
    time.sleep(0.5)

# --- Bul butonuna bas ---
def click_bul(driver):
    driver.find_element(By.NAME, '-find').click()
    time.sleep(3)

# --- Sonuç sayısını al ---
def get_sonuc_sayisi(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    div = soup.find("div", {"id": "divuyari"})
    if not div:
        return 0
    nums = re.findall(r'\d+', div.text)
    return int(nums[0]) if nums else 0

# --- Tablodan tez bilgilerini çek ---
def get_table(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    scripts = soup.find_all("script", {"type": "text/javascript"})
    if len(scripts) < 6:
        print("Tablo verisi bulunamadı.")
        return []

    data = str(scripts[5])
    tez_no = re.findall(r'(?<=\)>)\d+(?=</span>)', data)
    yil = re.findall(r'(?<=age: ")\d+(?=",)', data)
    title_raw = re.findall(r'(?<=weight: ")(.*?)(?=</span>)', data)
    title = [re.sub(r'<[^>]+>', ' ', t).strip() for t in title_raw]
    universite = re.findall(r'(?<=uni:")(.*?)(?=",)', data)
    tez_turu = re.findall(r'(?<=important: ")(.*?)(?=",)', data)
    konu = re.findall(r'(?<=someDate: ")(.*?)(?=",)', data)
    tez_detay = re.findall(r'#FF0000;\\\"(.+?)>', data)

    results = []
    for i in range(len(tez_no)):
        results.append({
            "tez_no": tez_no[i] if i < len(tez_no) else "",
            "yil": yil[i] if i < len(yil) else "",
            "title": title[i] if i < len(title) else "",
            "universite": universite[i] if i < len(universite) else "",
            "tez_turu": tez_turu[i] if i < len(tez_turu) else "",
            "konu": konu[i] if i < len(konu) else "",
            "tez_detay": tez_detay[i] if i < len(tez_detay) else "",
        })
    return results

# --- Tek bir tezin özetini çek ---
def get_abstract(driver, tez_detay_js, tez_no, max_retry=10):
    driver.execute_script(tez_detay_js)
    time.sleep(0.3)

    for _ in range(max_retry):
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        rows = soup.find_all("tr", {"class": "renkp"})
        if rows:
            tezno = rows[0].find_all("td")[0].text.replace("\n\t", "").strip()
            if tezno == tez_no:
                break
        driver.execute_script(tez_detay_js)
        time.sleep(0.3)

    en_abstract = None
    tr_abstract = None
    try:
        en_abstract = soup.find(id='td1').text.strip()
    except Exception:
        pass
    try:
        tr_abstract = soup.find(id='td0').text.strip()
    except Exception:
        pass
    return en_abstract, tr_abstract


# --- Ana arama fonksiyonu ---
def search_tez(konu, keywords, limit=3, headless=False):
    """
    Bilim alanı ve keyword ile YÖK Tez Merkezi'nde arama yapar.

    Args:
        konu: str - bilim alanı (ör: "Halk Sağlığı", "Eğitim ve Öğretim")
        keywords: list of str - aranacak anahtar kelimeler
        limit: int - maksimum çekilecek tez sayısı (demo için 3)
        headless: bool - tarayıcıyı görünmez çalıştır

    Returns:
        list of dict - tez bilgileri
    """
    keyword_str = " ".join(keywords)
    print(f"Konu    : '{konu}'")
    print(f"Keyword : '{keyword_str}'")
    print("-" * 50)

    driver = get_driver(headless=headless)

    try:
        # Tarama sayfasına git
        click_tarama(driver)

        # 1) Konu seç (popup'tan bilim alanı)
        konu_sec(driver, konu)

        # 2) Dizin alanına keyword gir
        if keyword_str:
            set_dizin(driver, keyword_str)

        # Ara
        click_bul(driver)

        # Sonuç sayısı
        sonuc = get_sonuc_sayisi(driver)
        print(f"Toplam sonuç: {sonuc}")

        if sonuc == 0:
            print("Sonuç bulunamadı.")
            return []

        # Tablo verilerini çek
        tezler = get_table(driver)
        print(f"Tabloda {len(tezler)} tez bulundu.")

        # Limit kadar tezin abstract'ini çek
        results = []
        for i, tez in enumerate(tezler[:limit]):
            print(f"  [{i+1}/{min(limit, len(tezler))}] Tez No: {tez['tez_no']} - Özet çekiliyor...")
            en_abs, tr_abs = get_abstract(driver, tez['tez_detay'], tez['tez_no'])
            tez_info = {
                "tez_no": tez['tez_no'],
                "yil": tez['yil'],
                "baslik": tez['title'],
                "universite": tez['universite'],
                "tez_turu": tez['tez_turu'],
                "konu": tez['konu'],
                "ozet_tr": tr_abs,
                "ozet_en": en_abs,
            }
            results.append(tez_info)
            print(f"    ✓ {tez['title'][:60]}...")

        return results

    finally:
        driver.quit()


def print_results(results):
    """Sonuçları güzel formatta yazdır"""
    if not results:
        print("Sonuç yok.")
        return

    for i, tez in enumerate(results, 1):
        print(f"\n{'='*60}")
        print(f"  TEZ #{i}")
        print(f"{'='*60}")
        print(f"  Tez No    : {tez['tez_no']}")
        print(f"  Yıl       : {tez['yil']}")
        print(f"  Başlık    : {tez['baslik']}")
        print(f"  Üniversite: {tez['universite']}")
        print(f"  Tez Türü  : {tez['tez_turu']}")
        print(f"  Konu      : {tez['konu']}")
        if tez['ozet_tr']:
            print(f"  Özet (TR) : {tez['ozet_tr'][:200]}...")
        if tez['ozet_en']:
            print(f"  Özet (EN) : {tez['ozet_en'][:200]}...")


# --- CLI ---
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="YÖK Tez Merkezi Arama")
    parser.add_argument("--konu", required=True, help="Bilim alanı (ör: 'Halk Sağlığı')")
    parser.add_argument("--keyword", nargs="+", default=[], help="Anahtar kelimeler")
    parser.add_argument("--limit", type=int, default=3, help="Max tez sayısı (varsayılan: 3)")
    args = parser.parse_args()

    results = search_tez(args.konu, args.keyword, limit=args.limit, headless=False)
    print_results(results)

    # JSON olarak kaydet
    output_file = "yoktez_sonuc.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSonuçlar '{output_file}' dosyasına kaydedildi.")
