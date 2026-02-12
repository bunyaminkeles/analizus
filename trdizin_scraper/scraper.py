import time
import re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote

def get_driver(headless=False):
    """Selenium WebDriver'ı başlatır ve yapılandırır."""
    ua = UserAgent()
    options = uc.ChromeOptions()
    options.add_argument(f'user-agent={ua.random}')
    if headless:
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
    
    print("WebDriver başlatılıyor...")
    driver = uc.Chrome(options=options)
    return driver

def search_trdizin(driver, search_query, start_year=None, end_year=None):
    """
    Belirtilen arama sorgusu ve filtrelerle TR Dizin'de arama yapar.
    Yıl filtresi, arama sorgusuna eklenerek yapılır.
    """
    try:
        # Yıl filtresi sorgusunu oluştur
        year_filter_query = ""
        if start_year or end_year:
            start = start_year if start_year else "*"
            end = end_year if end_year else "*"
            year_filter_query = f"(Year: year : ([{start} TO {end}]))"

        # Ana sorgu ile yıl filtresini birleştir
        final_query = search_query
        if final_query and year_filter_query:
            # Fazladan parantez eklemeden birleştirme yap
            final_query = f"{final_query} AND {year_filter_query}"
        elif year_filter_query:
            final_query = year_filter_query

        # URL-safe arama sorgusu oluştur
        encoded_query = quote(final_query)
        search_url = f"https://search.trdizin.gov.tr/en/yayin/ara?q={encoded_query}"
        
        print(f"URL'ye gidiliyor: {search_url}")
        driver.get(search_url)

        wait = WebDriverWait(driver, 20)
        
        # Sonuçların stabil hale gelmesi için bekle
        wait.until(EC.presence_of_element_located((By.ID, 'article-list')))
        print("Arama ve filtreleme tamamlandı.")

    except Exception as e:
        print(f"Arama ve filtreleme sırasında bir hata oluştu: {e}")
        return False
    return True

def parse_results(driver):
    """
    Arama sonuçları sayfasını analiz eder ve makale bilgilerini çıkarır.
    """
    print("Arama sonuçları ayrıştırılıyor...")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    results = []
    
    article_list_container = soup.find(id='article-list')
    if not article_list_container:
        print("Makale listesi bulunamadı.")
        return []
        
    articles = article_list_container.find_all('div', class_='article-item')
    print(f"{len(articles)} adet makale bulundu.")

    for article_soup in articles:
        try:
            title_tag = article_soup.find('h5', class_='card-title').find('a')
            title = title_tag.text.strip()
            
            trdizin_id = ''
            id_match = re.search(r'/journal-article/(\d+)', title_tag['href'])
            if id_match:
                trdizin_id = id_match.group(1)

            authors_p = article_soup.find('p', class_='card-text')
            authors = [author.strip() for author in authors_p.text.split(',')] if authors_p else []

            journal_info = article_soup.find('p', class_='card-info')
            journal_text = journal_info.text.strip() if journal_info else ''
            
            publication_year = None
            year_match = re.re.search(r'(\d{4});', journal_text)
            if year_match:
                publication_year = int(year_match.group(1))

            article_data = {
                'trdizin_id': trdizin_id,
                'title': title,
                'authors': authors,
                'publication_year': publication_year,
                'journal': journal_text,
                'abstract': '',
                'keywords': []
            }
            results.append(article_data)
        except Exception as e:
            print(f"Bir makale ayrıştırılırken hata oluştu: {e}")
            continue
            
    return results

def run_scraper(search_query, start_year=None, end_year=None, headless=True):
    """
    TR Dizin scraper'ını tam döngüde çalıştırır ve sonuçları veritabanına kaydeder.
    """
    from .models import TrdizinArticle

    driver = get_driver(headless=headless)
    
    try:
        if not search_trdizin(driver, search_query, start_year, end_year):
            return []
            
        articles_data = parse_results(driver)
        
        saved_articles = []
        for article_data in articles_data:
            if not article_data.get('trdizin_id'):
                continue
            
            article, created = TrdizinArticle.objects.update_or_create(
                trdizin_id=article_data['trdizin_id'],
                defaults={
                    'title': article_data['title'],
                    'authors': article_data['authors'],
                    'publication_year': article_data['publication_year'],
                    'journal': article_data['journal'],
                }
            )
            saved_articles.append(article)
        
        print(f"Toplam {len(saved_articles)} makale veritabanına işlendi.")
        return saved_articles
        
    except Exception as e:
        print(f"Scraper çalışırken bir hata oluştu: {e}")
        return None
    finally:
        print("WebDriver kapatılıyor.")
        driver.quit()

if __name__ == '__main__':
    QUERY = "sağlıkta makine öğrenmesi"
    scraped_articles = run_scraper(QUERY, start_year="2020", end_year="2022", headless=False)
    if scraped_articles:
        for i, article in enumerate(scraped_articles, 1):
            print(f"\n--- Makale {i} ---")
            print(f"ID: {article.trdizin_id}")
            print(f"Başlık: {article.title}")
            print(f"Yazarlar: {article.authors}")
            print(f"Yıl: {article.publication_year}")
