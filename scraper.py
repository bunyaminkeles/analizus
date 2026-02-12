"""
TR Dizin Scraper Service.
YÖK Tez scraper yapısı baz alınarak oluşturulmuştur.
"""
import os
import time
import re
import logging
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.conf import settings
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

# Chrome kütüphane ayarları (YÖK Tez ile ortak)
_chrome_libs = os.path.join(settings.BASE_DIR, "chrome-libs", "lib")
if os.path.isdir(_chrome_libs):
    _ld = os.environ.get("LD_LIBRARY_PATH", "")
    if _chrome_libs not in _ld:
        os.environ["LD_LIBRARY_PATH"] = f"{_chrome_libs}:{_ld}" if _ld else _chrome_libs

URL = "https://search.trdizin.gov.tr/"

class TrDizinScraper:
    """TR Dizin Scraper Service"""

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
        if hasattr(settings, 'CHROME_BINARY_PATH') and settings.CHROME_BINARY_PATH:
            driver_kwargs['browser_executable_path'] = settings.CHROME_BINARY_PATH

        driver = uc.Chrome(**driver_kwargs)
        return driver

    def search(self, keywords, fields=None, limit=10):
        """
        TR Dizin üzerinde arama yapar. Belirli alanlarda arama yapabilir.
        
        Args:
            keywords (list): Aranacak anahtar kelimeler.
            fields (list, optional): Aramanın yapılacağı alanlar (ör: ['title', 'abstract']). 
                                     None ise genel arama yapılır. Defaults to None.
            limit (int): Maksimum sonuç sayısı.
            
        Returns:
            list: Makale sonuçları
        """
        if fields is None:
            fields = ['title', 'abstract']

        keyword_str = " ".join(keywords)
        logger.info(f"TR Dizin Arama: Anahtar Kelimeler='{keyword_str}', Alanlar='{fields}'")
        
        driver = self._get_driver()
        results = []
        
        try:
            # Gelişmiş arama sorgusunu oluştur
            if fields and keywords:
                keyword_part = " AND ".join([f'"{k}"' for k in keywords])
                field_queries = [f'({field}:({keyword_part}))' for field in fields]
                query = " OR ".join(field_queries)
            else:
                query = keyword_str

            search_url = f"https://search.trdizin.gov.tr/en/yayin/ara?q={quote_plus(query)}"
            logger.info(f"Oluşturulan Sorgu URL'si: {search_url}")
            driver.get(search_url)
            
            # Sayfanın yüklenmesini bekle (dinamik içerik için)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "search-results"))
            )
            time.sleep(3) # Ek render süresi
            
            while len(results) < limit:
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Sonuç listesini bul (yeni yapı)
                items = soup.select("div.card.record-card")
                
                if not items:
                    logger.warning("Sonuç öğeleri bulunamadı. Sayfa yapısı değişmiş olabilir veya arama sonucu boş olabilir.")
                    break

                for item in items:
                    if len(results) >= limit:
                        break
                        
                    try:
                        # Başlık ve Link
                        title_tag = item.select_one("h5.card-title a")
                        if not title_tag:
                            continue
                            
                        title = title_tag.get_text(strip=True)
                        link = title_tag.get("href", "")
                        if link and not link.startswith("http"):
                            link = "https://search.trdizin.gov.tr" + link

                        # Yıl
                        year_tag = item.select_one("span.text-muted.pr-3")
                        year = year_tag.get_text(strip=True) if year_tag else ""
                        if not year:
                            text_content = item.get_text(" ", strip=True)
                            year_match = re.search(r'\b(19|20)\d{2}\b', text_content)
                            year = year_match.group(0) if year_match else ""
                        
                        # Özet (Varsa)
                        abstract_tag = item.select_one("div.card-text")
                        abstract = abstract_tag.get_text(strip=True) if abstract_tag else ""

                        # Sonuç ekle (Tekrarları önle)
                        if link and not any(r['link'] == link for r in results):
                            results.append({
                                "baslik": title,
                                "yil": year,
                                "link": link,
                                "ozet": abstract,
                                "kaynak": "TR Dizin"
                            })
                            
                    except Exception as e:
                        logger.error(f"TR Dizin sonuç ayrıştırma hatası: {e}", exc_info=True)
                        continue
                
                # Sayfalama
                if len(results) < limit:
                    try:
                        # Sonraki sayfa butonu (yeni yapı)
                        next_button = driver.find_element(By.CSS_SELECTOR, "a[rel='next']")
                        if next_button:
                            driver.execute_script("arguments[0].click();", next_button)
                            WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.ID, "search-results"))
                            )
                            time.sleep(3) # Ek render süresi
                        else:
                            break
                    except:
                        break
            
            logger.info(f"TR Dizin: {len(results)} sonuç bulundu.")
            return results

        except Exception as e:
            logger.error(f"TR Dizin arama sırasında genel bir hata oluştu: {e}", exc_info=True)
            return []
        finally:
            driver.quit()