import logging
import tempfile
from django.core.mail import EmailMessage
from django.conf import settings
from django.db import close_old_connections
from django.utils import timezone

logger = logging.getLogger(__name__)


def _execute_job(job_id: str) -> None:
    """Global kuyruk worker'ı tarafından çağrılır — senkron çalışır."""
    from transcript.models import TranscriptJob, TranscriptSettings
    from transcript.services import get_video_info, download_audio, transcribe_audio

    close_old_connections()
    try:
        job = TranscriptJob.objects.get(id=job_id)
        job.status = TranscriptJob.STATUS_RUNNING
        job.save(update_fields=["status"])

        ts = TranscriptSettings.get()

        # 1. Video bilgisi (başlık + süre)
        info = get_video_info(job.video_id)
        job.video_title = info["title"] or job.video_url
        if info["duration"] is not None:
            job.video_duration_seconds = info["duration"]
        job.save(update_fields=["video_title", "video_duration_seconds"])

        # 2. Süre limiti kontrolü
        if job.video_duration_seconds:
            max_seconds = ts.max_minutes_for(job.user) * 60
            if job.video_duration_seconds > max_seconds:
                raise Exception(
                    f"Video süresi ({job.video_duration_seconds // 60} dk) izin verilen "
                    f"sınırı ({ts.max_minutes_for(job.user)} dk) aşıyor."
                )

        # 3. Ses indir + transkripsiyon (temp klasör otomatik temizlenir)
        with tempfile.TemporaryDirectory() as tmpdir:
            logger.info("Ses indiriliyor: %s", job.video_id)
            audio_path = download_audio(job.video_id, tmpdir)
            logger.info("Transkripsiyon başlıyor: model=%s, lang=%s", ts.whisper_model, job.language_requested)
            result = transcribe_audio(audio_path, job.language_requested, ts.whisper_model)

        if result["error"]:
            raise Exception(result["error"])

        job.transcript_text = result["text"]
        job.language_used = result["language_used"]
        job.translated = False  # Whisper doğrudan transkripsiyon yapar, çeviri değil
        job.status = TranscriptJob.STATUS_COMPLETED
        job.completed_at = timezone.now()
        job.save(update_fields=["transcript_text", "language_used", "translated", "status", "completed_at"])

        logger.info("Transcript tamamlandı: job=%s lang=%s", job_id, result["language_used"])

        # 4. E-posta teslimatı
        if job.delivery == TranscriptJob.DELIVERY_EMAIL:
            _send_transcript_email(job)

    except TranscriptJob.DoesNotExist:
        logger.error("Transcript job bulunamadı: %s", job_id)
    except Exception as exc:
        logger.error("Transcript job hatası [%s]: %s", job_id, exc, exc_info=True)
        close_old_connections()
        try:
            job = TranscriptJob.objects.get(id=job_id)
            job.status = TranscriptJob.STATUS_FAILED
            job.error_message = str(exc)
            job.save(update_fields=["status", "error_message"])
        except Exception:
            pass


def _send_transcript_email(job) -> None:
    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in job.video_title)[:80]
    filename = f"transcript_{safe_title or job.video_id}.txt"

    body = (
        f"YouTube Transcript — {job.video_title}\n"
        f"Video: {job.video_url}\n"
        f"Dil: {job.language_used}\n"
        f"{'─' * 50}\n\n"
        f"{job.transcript_text}"
    )

    email = EmailMessage(
        subject=f"YouTube Transcript: {job.video_title[:60]}",
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[job.email_address],
    )
    email.attach(filename, job.transcript_text, "text/plain")
    email.send()
    logger.info("Transcript e-postası gönderildi: job=%s → %s", job.id, job.email_address)
