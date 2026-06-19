import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET
from django.utils.text import slugify

from transcript.models import TranscriptJob, TranscriptSettings
from transcript.forms import TranscriptRequestForm
from transcript.services import extract_video_id, list_available_languages

logger = logging.getLogger(__name__)


@login_required
def transcript_form(request):
    settings_obj = TranscriptSettings.get()
    max_minutes = settings_obj.max_minutes_for(request.user)

    if request.method == "POST":
        form = TranscriptRequestForm(request.POST)
        if form.is_valid():
            video_url = form.cleaned_data["video_url"]
            language = form.cleaned_data.get("language", "")
            delivery = form.cleaned_data["delivery"]
            email_address = form.cleaned_data.get("email", "")

            video_id = extract_video_id(video_url)
            if not video_id:
                form.add_error("video_url", "Geçerli bir YouTube linki giriniz.")
                return render(request, "transcript/form.html", {"form": form, "max_minutes": max_minutes})

            job = TranscriptJob.objects.create(
                user=request.user,
                video_url=video_url,
                video_id=video_id,
                language_requested=language,
                delivery=delivery,
                email_address=email_address,
            )

            from analizdestek.job_queue import enqueue
            enqueue("transcript", str(job.id))

            return redirect("transcript:status", job_id=job.id)
    else:
        form = TranscriptRequestForm()

    return render(request, "transcript/form.html", {"form": form, "max_minutes": max_minutes})


@login_required
@require_GET
def transcript_status(request, job_id):
    job = get_object_or_404(TranscriptJob, id=job_id, user=request.user)
    return render(request, "transcript/status.html", {"job": job})


@login_required
@require_GET
def transcript_status_api(request, job_id):
    job = get_object_or_404(TranscriptJob, id=job_id, user=request.user)
    return JsonResponse({
        "status": job.status,
        "video_title": job.video_title,
        "language_used": job.language_used,
        "translated": job.translated,
        "error_message": job.error_message,
    })


@login_required
@require_GET
def transcript_download(request, job_id):
    job = get_object_or_404(TranscriptJob, id=job_id, user=request.user)
    if job.status != TranscriptJob.STATUS_COMPLETED:
        return HttpResponse("Transcript henüz hazır değil.", status=400)

    safe_title = slugify(job.video_title or job.video_id)[:80] or job.video_id
    filename = f"transcript_{safe_title}.txt"

    lang_note = ""
    if job.translated:
        lang_note = f"\n[NOT: Bu transcript YouTube'un otomatik çevirisi kullanılarak {job.language_used} diline çevrilmiştir.]"

    content = (
        f"YouTube Transcript — {job.video_title}\n"
        f"Video: {job.video_url}\n"
        f"Dil: {job.language_used}"
        f"{lang_note}\n"
        f"{'─' * 50}\n\n"
        f"{job.transcript_text}"
    )

    response = HttpResponse(content, content_type="text/plain; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@login_required
@require_GET
def available_languages_api(request):
    """Video URL girildiğinde mevcut dilleri listeler (opsiyonel AJAX)."""
    video_url = request.GET.get("url", "")
    video_id = extract_video_id(video_url)
    if not video_id:
        return JsonResponse({"languages": []})
    langs = list_available_languages(video_id)
    return JsonResponse({"languages": langs, "video_id": video_id})
