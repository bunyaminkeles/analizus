import logging
import requests
from bs4 import BeautifulSoup
from django.core.cache import cache

logger = logging.getLogger(__name__)

def get_altinkaynak_rates():
    """
    Altınkaynak sitesinden döviz ve altın kurlarını çeker.
    Veriyi 5 dakika (300 saniye) boyunca cache'ler.
    """
    # Cache kontrolü
    cached_data = cache.get('market_rates_data')
    if cached_data:
        return cached_data

    url = "https://www.altinkaynak.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    rates = []
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Hedeflenen veriler (ID'ler sitenin yapısına göre güncellenmelidir)
            # Not: Eğer ID'ler değişirse burası boş dönebilir, try-except ile yönetiyoruz.
            targets = [
                {'code': 'USD', 'name': 'Dolar', 'id': 'USDOZ'},
                {'code': 'EUR', 'name': 'Euro', 'id': 'EUROZ'},
                {'code': 'GA', 'name': 'Gr. Altın', 'id': 'HASOZ'},
                {'code': 'QC', 'name': 'Çeyrek', 'id': 'CEYREKOZ'}
            ]

            for target in targets:
                element = soup.find(id=target['id'])
                # Eğer ID bulunamazsa varsayılan değer ata
                price = element.text.strip() if element else "---"
                
                rates.append({
                    "code": target['code'],
                    "name": target['name'],
                    "price": price,
                    "trend": "up" # Gerçek trend analizi için geçmiş veri gerekir, şimdilik statik
                })
            
            # Veriyi cache'e kaydet (5 dakika)
            if rates:
                cache.set('market_rates_data', rates, 300)
                
    except Exception as e:
        logger.error(f"Scraping hatası: {e}")
        # Hata durumunda boş liste veya cache'deki eski veriyi döndürebiliriz
        return []

    return rates
