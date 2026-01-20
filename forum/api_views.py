from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.timesince import timesince
from .models import JobProposal
from .utils import get_altinkaynak_rates

def widget_market_rates(request):
    """Altınkaynak verilerini JSON olarak döner"""
    data = get_altinkaynak_rates()
    return JsonResponse({'rates': data})

def widget_latest_proposals(request):
    """Analiz pazarındaki son teklifleri JSON olarak döner"""
    # Son 5 teklifi getir
    proposals = JobProposal.objects.select_related('job', 'expert').order_by('-created_at')[:5]
    
    data = []
    for p in proposals:
        data.append({
            'id': p.id,
            'job_title': p.job.title,
            'expert_name': p.expert.username,
            'price': f"{p.price:,.0f} ₺",
            'time_ago': timesince(p.created_at).split(',')[0] + " önce"
        })
    
    return JsonResponse({'proposals': data})