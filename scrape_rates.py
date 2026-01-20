import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def get_altinkaynak_rates():
    """
    Altınkaynak sitesinden güncel döviz ve altın kurlarını çeker.
    Not: Sitenin HTML yapısı değişirse seçicilerin (selectors) güncellenmesi gerekir.
    """
    url = "https://www.altinkaynak.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return {"error": f"Siteye erişilemedi: {response.status_code}"}

        soup = BeautifulSoup(response.content, 'html.parser')
        rates = []

        # Hedeflenen veriler ve olası HTML ID'leri
        # Not: Bu ID'ler örnektir. Sitenin güncel yapısına göre tarayıcıda 'Inspect' ile bakılarak güncellenmelidir.
        targets = [
            {'code': 'USD', 'name': 'Dolar', 'id': 'USDOZ'},     # Örnek ID
            {'code': 'EUR', 'name': 'Euro', 'id': 'EUROZ'},      # Örnek ID
            {'code': 'GA', 'name': 'Gr. Altın', 'id': 'HASOZ'},  # Örnek ID
            {'code': 'QC', 'name': 'Çeyrek', 'id': 'CEYREKOZ'}   # Örnek ID
        ]

        for target in targets:
            # Elementi bul
            element = soup.find(id=target['id'])
            
            # Eğer ID ile bulunamazsa, alternatif olarak class veya text içeriği ile aranabilir
            # Örn: element = soup.find("td", text="Dolar").find_next("td")
            
            price = element.text.strip() if element else "0.00"
            
            rates.append({
                "code": target['code'],
                "name": target['name'],
                "buy": price,
                "sell": price, # Genellikle alış/satış ayrı elementlerdedir, burada basitleştirildi
                "change": 0.0
            })

        return {
            "source": "Altınkaynak",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": rates
        }

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("Altınkaynak verileri çekiliyor...")
    data = get_altinkaynak_rates()
    print(json.dumps(data, indent=2, ensure_ascii=False))