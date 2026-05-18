"""
tezanaliz view'ları /yoktez/ altında birleştirildi (mayıs 2026).
Bu dosya 301 yönlendirme ve backward-compat shim içerir.
"""
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


def tezanaliz_landing(request):
    return redirect('/yoktez/', permanent=True)


@login_required
@require_POST
def create_from_yoktez(request, yok_job_id):
    from yoktez.views import create_analiz
    return create_analiz(request, yok_job_id)


@login_required
def tezanaliz_status(request, job_id):
    from yoktez.views import analiz_status
    return analiz_status(request, job_id)


@login_required
def tezanaliz_results(request, job_id):
    return redirect(f'/yoktez/sonuc/{job_id}/', permanent=True)
