import logging
from django.core.mail import EmailMessage
from django.conf import settings
from django.db import close_old_connections
from django.utils import timezone

logger = logging.getLogger(__name__)


def _execute_job(job_id: str) -> None:
    from transcript.models import TranscriptJob, TranscriptSettings
    from transcript.services import get_video_info, get_duration_from_transcript, fetch_transcript

    close_old_connections()
    try:
        job = TranscriptJob.objects.get(id=job_id)
        job.status = TranscriptJob.STATUS_RUNNING
        job.save(update_fields=["status"])

        ts = TranscriptSettings.get()

        # 1. Video başlığı
        info = get_video_info(job.video_id)
        job.video_title = info["title"] or job.video_url
        job.save(update_fields=["video_title"])

        # 2. Süre kontrolü (transcript entry'lerinden tahmin)
        duration = get_duration_from_transcript(job.video_id)
        if duration:
            job.video_duration_seconds = duration
            job.save(update_fields=["video_duration_seconds"])
            max_seconds = ts.max_minutes_for(job.user) * 60
            if duration > max_seconds:
                raise Exception(
                    f"Video süresi ({duration // 60} dk) izin verilen "
                    f"sınırı ({ts.max_minutes_for(job.user)} dk) aşıyor."
                )

        # 3. Transcript çek
        result = fetch_transcript(job.video_id, job.language_requested)
        if result["error"]:
            raise Exception(result["error"])

        job.transcript_text = result["text"]
        job.language_used = result["language_used"]
        job.translated = result["translated"]
        job.status = TranscriptJob.STATUS_COMPLETED
        job.completed_at = timezone.now()
        job.save(update_fields=["transcript_text", "language_used", "translated", "status", "completed_at"])

        logger.info("Transcript tamamlandı: job=%s lang=%s translated=%s", job_id, result["language_used"], result["translated"])

        if job.delivery == TranscriptJob.DELIVERY_EMAIL:
            _send_email(job)

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


def _send_email(job) -> None:
    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in job.video_title)[:80]
    filename = f"transcript_{safe_title or job.video_id}.txt"

    lang_note = f"\n[NOT: YouTube otomatik çevirisi ile {job.language_used} diline çevrilmiştir.]" if job.translated else ""

    body = (
        f"YouTube Transcript — {job.video_title}\n"
        f"Video: {job.video_url}\n"
        f"Dil: {job.language_used}{lang_note}\n"
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
