from django.shortcuts import render
from .scraper import run_scraper

def search_page(request):
    """
    TR Dizin arama sayfasını oluşturur. POST isteklerinde
    scraper'ı tetikler ve sonuçları gösterir.
    """
    context = {}
    if request.method == 'POST':
        title_query = request.POST.get('title_query', '').strip()
        abstract_query = request.POST.get('abstract_query', '').strip()
        start_year = request.POST.get('start_year')
        end_year = request.POST.get('end_year')
        
        context = {
            'title_query': title_query,
            'abstract_query': abstract_query,
            'start_year': start_year,
            'end_year': end_year,
        }

        # Arama sorgusunu oluştur
        query_parts = []
        if title_query:
            query_parts.append(f'(Title: title : ("""{title_query}""))')
        if abstract_query:
            query_parts.append(f'(Abstract: abstract : ("""{abstract_query}""))')
        
        if not query_parts:
            # Arama yapacak bir kriter yoksa boş dön
            context['error'] = "Arama yapmak için en az bir kriter girmelisiniz."
            return render(request, 'trdizin_scraper/search.html', context)

        search_query = " AND ".join(query_parts)
        context['query'] = search_query # Arama sonuçlarında göstermek için

        # Scraper'ı çalıştır ve sonuçları al
        articles = run_scraper(
            search_query=search_query,
            start_year=start_year, 
            end_year=end_year, 
            headless=True
        )
        
        context['articles'] = articles
        
    return render(request, 'trdizin_scraper/search.html', context)