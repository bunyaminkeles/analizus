import logging
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET
from django.utils.text import slugify

from transcript.models import TranscriptJob, TranscriptSettings
from transcript.forms import TranscriptRequestForm
from transcript.services import extract_video_id

logger = logging.getLogger(__name__)

_SEO_GUIDE = {
    'intro': (
        'YouTube Transcript İndirici, herhangi bir YouTube videosunun altyazı metnini saniyeler '
        'içinde TXT dosyası olarak indirmenizi veya e-posta ile almanızı sağlar. Ders kayıtları, '
        'konferans sunumları, belgesel yorumları ve akademik içerikler için hızlı metin çıkarma '
        'aracıdır. Türkçe, Almanca ve İngilizce öncelikli otomatik dil seçimi ile YouTube\'un '
        'kendi altyazı altyapısını kullanır; API anahtarı veya ek yazılım gerekmez.'
    ),
    'when_to_use': (
        'Bir YouTube dersinin, seminer kaydının veya konferans sunumunun metnini not almak, '
        'alıntı yapmak ya da içerik analizine dahil etmek istediğinizde kullanın. Özellikle '
        'altyazısı olan eğitim kanalları, TED konuşmaları ve akademik sempozyum kayıtları '
        'için idealdir. Videoyu izleyecek vaktiniz olmadığında veya metni arama/indeksleme '
        'amacıyla kullanmanız gerektiğinde en pratik çözümdür.'
    ),
    'assumptions': (
        'Transcript yalnızca YouTube\'un sağladığı altyazılardan üretilir; videoda altyazı '
        'yoksa işlem tamamlanamaz. Otomatik oluşturulmuş altyazılarda (auto-generated) telaffuz '
        'hataları veya noktalama eksiklikleri olabilir. İstenen dilde altyazı bulunmazsa '
        'YouTube\'un otomatik çeviri özelliği devreye girer; bu durumda çeviri kalitesi '
        'YouTube altyapısına bağlıdır. Video süresi kullanıcı tipine göre sınırlıdır.'
    ),
    'how_to_interpret': (
        'İndirilen TXT dosyası, videodaki konuşmaları zaman damgası olmaksızın düz metin '
        'olarak içerir. Dosyanın başında video başlığı, URL ve kullanılan dil bilgisi yer alır. '
        'Otomatik çeviri kullanıldıysa bu dosyada belirtilir. Metni doğrudan akademik çalışmaya '
        'kaynak göstermeden önce videonun orijinal içeriğiyle karşılaştırarak doğrulamanız '
        'önerilir.'
    ),
    'apa_example': (
        'Yazar Soyadı, A. (Yıl, Ay Gün). Video başlığı [Video]. YouTube. '
        'https://www.youtube.com/watch?v=XXXXX'
    ),
    'faq': [
        {
            'q': 'Videoda altyazı yoksa ne olur?',
            'a': (
                'Altyazısı tamamen kapalı olan videolarda transcript oluşturulamaz ve hata '
                'mesajı gösterilir. Çoğu büyük kanal ve YouTube\'un otomatik altyazı '
                'oluşturduğu İngilizce/Türkçe içerikler desteklenir.'
            ),
        },
        {
            'q': 'İstediğim dilde altyazı yoksa ne olur?',
            'a': (
                'Seçilen dilde doğrudan altyazı bulunamazsa YouTube\'un otomatik çeviri '
                'özelliği denenir. O da yoksa videonun orijinal dilindeki altyazı kullanılır '
                've dosyada bu durum belirtilir.'
            ),
        },
        {
            'q': 'Video süre sınırı neden var?',
            'a': (
                'Çok uzun videolar yüksek işlem süresi ve kaynak tüketimine yol açar. '
                'Standart kullanıcılar için sınır admin kullanıcıların yarısıdır. '
                'Daha uzun videolar için yönetici hesabıyla giriş yapabilirsiniz.'
            ),
        },
        {
            'q': 'Transcript kalitesi ne kadar güvenilir?',
            'a': (
                'İnsan tarafından yazılmış altyazılar oldukça doğrudur. YouTube\'un otomatik '
                'altyazıları ise aksanlı konuşmalarda veya teknik terimlerde hata yapabilir. '
                'Akademik kullanımdan önce kritik bölümleri orijinal videoyla karşılaştırmanız önerilir.'
            ),
        },
    ],
    'related_tools': [
        ('/analiz/', 'İstatistik Analiz Araçları'),
        ('/bibliometrics/', 'Bibliometrik Analiz'),
        ('/yoktez/', 'YÖK Tez Tarama'),
    ],
}


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
