"""
YÖK Tez Merkezi scraper service.
Mevcut yoktez.py'den refactor edildi + yıl-bölme (2000+ sonuç) desteği eklendi.
"""
import os
import time
import re
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from django.conf import settings


logger = logging.getLogger(__name__)

# Chrome için indirilen ekstra kütüphanelerin yolunu LD_LIBRARY_PATH'e ekle
_chrome_libs = os.path.join(settings.BASE_DIR, "chrome-libs", "lib")
if os.path.isdir(_chrome_libs):
    _ld = os.environ.get("LD_LIBRARY_PATH", "")
    if _chrome_libs not in _ld:
        os.environ["LD_LIBRARY_PATH"] = f"{_chrome_libs}:{_ld}" if _ld else _chrome_libs

URL = "https://tez.yok.gov.tr/UlusalTezMerkezi/"
MAX_RESULTS_PER_PAGE = 2000


class YokTezScraper:
    """YÖK Tez Merkezi scraper with year-splitting for large result sets."""

    def __init__(self, headless=True):
        self.headless = headless

    def _get_driver(self):
        ua = UserAgent()
        options = uc.ChromeOptions()
        options.add_argument(f'user-agent={ua.random}')
        if self.headless:
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')

        driver_kwargs = {'options': options, 'version_main': 144}
        if settings.CHROME_BINARY_PATH:
            driver_kwargs['browser_executable_path'] = settings.CHROME_BINARY_PATH

        driver = uc.Chrome(**driver_kwargs)
        driver.get(URL)
        time.sleep(3)
        return driver

    def _click_tarama(self, driver):
        driver.find_element(By.XPATH, '//*[@id="navigation2"]/ul/li[2]/a').click()
        time.sleep(3)

    def _konu_sec(self, driver, konu_adi):
        el = driver.find_element(By.ID, 'konu')
        el.click()
        time.sleep(1)
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

    def _set_dizin(self, driver, keyword):
        el = driver.find_element(By.NAME, 'Dizin')
        el.clear()
        el.send_keys(keyword)
        time.sleep(0.5)

    def _set_year_range(self, driver, year_from, year_to):
        yil1_path = '//*[@id="tabs-1"]/form/table/tbody/tr/td/table/tbody/tr[2]/td[6]/select[1]'
        yil2_path = '//*[@id="tabs-1"]/form/table/tbody/tr/td/table/tbody/tr[2]/td[6]/select[2]'
        driver.find_element(By.XPATH, yil1_path).send_keys(str(year_from))
        time.sleep(0.5)
        driver.find_element(By.XPATH, yil2_path).send_keys(str(year_to))
        time.sleep(0.5)

    def _click_bul(self, driver):
        driver.find_element(By.NAME, '-find').click()
        time.sleep(3)

    def _get_sonuc_sayisi(self, driver):
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        div = soup.find("div", {"id": "divuyari"})
        if not div:
            return 0
        nums = re.findall(r'\d+', div.text)
        return int(nums[0]) if nums else 0

    def _get_table(self, driver):
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        scripts = soup.find_all("script", {"type": "text/javascript"})
        if len(scripts) < 6:
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
                "baslik": title[i] if i < len(title) else "",
                "universite": universite[i] if i < len(universite) else "",
                "tez_turu": tez_turu[i] if i < len(tez_turu) else "",
                "konu": konu[i] if i < len(konu) else "",
                "tez_detay": tez_detay[i] if i < len(tez_detay) else "",
            })
        return results

    def _get_abstract(self, driver, tez_detay_js, tez_no, max_retry=10):
        driver.execute_script(tez_detay_js)
        time.sleep(0.3)

        soup = None
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
        if soup:
            try:
                en_abstract = soup.find(id='td1').text.strip()
            except Exception:
                pass
            try:
                tr_abstract = soup.find(id='td0').text.strip()
            except Exception:
                pass
        return en_abstract, tr_abstract

    def _fetch_single_batch(self, konu, keyword_str, year_from=None, year_to=None, abstract_limit=None):
        """Tek bir arama yapıp sonuçları döndürür. abstract_limit varsa sadece o kadar özet çeker."""
        driver = self._get_driver()
        try:
            self._click_tarama(driver)
            self._konu_sec(driver, konu)
            if keyword_str:
                self._set_dizin(driver, keyword_str)
            if year_from and year_to:
                self._set_year_range(driver, year_from, year_to)
            self._click_bul(driver)

            count = self._get_sonuc_sayisi(driver)
            if count == 0:
                return 0, []

            tezler = self._get_table(driver)

            # Özet çekme (abstract_limit varsa sınırla)
            fetch_count = len(tezler) if abstract_limit is None else min(abstract_limit, len(tezler))
            results = []
            for tez in tezler[:fetch_count]:
                en_abs, tr_abs = self._get_abstract(driver, tez['tez_detay'], tez['tez_no'])
                results.append({
                    'tez_no': tez['tez_no'],
                    'yil': tez['yil'],
                    'baslik': tez['baslik'],
                    'universite': tez['universite'],
                    'tez_turu': tez['tez_turu'],
                    'konu': tez['konu'],
                    'ozet_tr': tr_abs,
                    'ozet_en': en_abs,
                })

            # Kalan tezleri özetsiz ekle
            for tez in tezler[fetch_count:]:
                results.append({
                    'tez_no': tez['tez_no'],
                    'yil': tez['yil'],
                    'baslik': tez['baslik'],
                    'universite': tez['universite'],
                    'tez_turu': tez['tez_turu'],
                    'konu': tez['konu'],
                    'ozet_tr': None,
                    'ozet_en': None,
                })

            return count, results
        finally:
            driver.quit()

    def search(self, konu, keywords, demo_limit=3):
        """
        Ana arama fonksiyonu. 2000+ sonuçlar için yıl-bölme uygular.

        Returns:
            (total_count, demo_results, all_results)
            - demo_results: ilk demo_limit tezin özetleriyle birlikte
            - all_results: tüm tezler (özetler sadece demo kadar)
        """
        keyword_str = " ".join(keywords)
        current_year = datetime.now().year
        logger.info(f"Arama başlıyor: konu='{konu}', keywords='{keyword_str}'")

        # İlk arama - toplam sonuç sayısını öğren
        driver = self._get_driver()
        try:
            self._click_tarama(driver)
            self._konu_sec(driver, konu)
            if keyword_str:
                self._set_dizin(driver, keyword_str)
            self._click_bul(driver)
            total_count = self._get_sonuc_sayisi(driver)
        finally:
            driver.quit()

        logger.info(f"Toplam sonuç: {total_count}")

        if total_count == 0:
            return 0, [], []

        # --- Strateji: sonuç sayısına göre ---
        if total_count < MAX_RESULTS_PER_PAGE:
            # Tek çekimde hallolur
            count, results = self._fetch_single_batch(konu, keyword_str, abstract_limit=demo_limit)
            demo = [r for r in results[:demo_limit] if r.get('ozet_tr') or r.get('ozet_en')]
            return total_count, demo, results

        # Yıl bölme gerekiyor
        if total_count < 4000:
            window_size = 12
        else:
            window_size = 6

        all_results = []
        demo_results = []
        year_to = current_year

        while year_to >= 1950:
            year_from = max(year_to - window_size + 1, 1900)

            # Demo'ya hala ihtiyaç var mı?
            remaining_demo = max(0, demo_limit - len(demo_results))
            abs_limit = remaining_demo if remaining_demo > 0 else 0

            logger.info(f"Yıl aralığı: {year_from}-{year_to}")
            count, results = self._fetch_single_batch(
                konu, keyword_str, year_from, year_to, abstract_limit=abs_limit
            )

            if count > 0:
                # Demo sonuçlara ekle
                for r in results:
                    if len(demo_results) < demo_limit and (r.get('ozet_tr') or r.get('ozet_en')):
                        demo_results.append(r)
                all_results.extend(results)

            year_to = year_from - 1
            if count == 0 and year_from <= 1960:
                break

        logger.info(f"Toplam çekilen: {len(all_results)} tez")
        return total_count, demo_results, all_results
