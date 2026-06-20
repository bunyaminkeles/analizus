import re
import logging
import requests
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled

logger = logging.getLogger(__name__)

AUTO_LANGUAGE_PRIORITY = ["tr", "de", "en"]

_ytt = YouTubeTranscriptApi()


def extract_video_id(url: str) -> str | None:
    match = re.search(r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})", url)
    return match.group(1) if match else None


def get_video_info(video_id: str) -> dict:
    """YouTube oEmbed ile video başlığını getirir (API anahtarı gerektirmez)."""
    try:
        resp = requests.get(
            "https://www.youtube.com/oembed",
            params={"url": f"https://www.youtube.com/watch?v={video_id}", "format": "json"},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            return {"title": data.get("title", ""), "duration": None}
    except Exception as exc:
        logger.warning("oEmbed video bilgisi alınamadı: %s", exc)
    return {"title": "", "duration": None}


def fetch_transcript(video_id: str, language_requested: str = "") -> dict:
    """
    YouTube altyazısını çeker.
    Öncelik: istenilen dil → tr → de → en → YouTube auto-translate → orijinal dil.

    Returns:
        {"text": str, "language_used": str, "translated": bool, "error": str|None}
    """
    try:
        transcript_list = _ytt.list(video_id)
    except TranscriptsDisabled:
        return {"text": "", "language_used": "", "translated": False,
                "error": "Bu video için altyazı devre dışı bırakılmış."}
    except Exception as exc:
        return {"text": "", "language_used": "", "translated": False, "error": str(exc)}

    if language_requested:
        priority = [language_requested] + [l for l in AUTO_LANGUAGE_PRIORITY if l != language_requested]
    else:
        priority = AUTO_LANGUAGE_PRIORITY

    # 1. İstenilen dilde doğrudan transcript
    for lang in priority:
        try:
            transcript = transcript_list.find_transcript([lang])
            entries = transcript.fetch()
            return {
                "text": _to_text(entries),
                "language_used": lang,
                "translated": False,
                "error": None,
            }
        except NoTranscriptFound:
            continue
        except Exception:
            continue

    # 2. Mevcut ilk transcript'i al, çevirmeyi dene
    try:
        available = list(transcript_list)
        if not available:
            return {"text": "", "language_used": "", "translated": False,
                    "error": "Bu video için hiç altyazı bulunamadı."}

        source = available[0]
        target_lang = priority[0]

        try:
            translated = source.translate(target_lang)
            entries = translated.fetch()
            return {
                "text": _to_text(entries),
                "language_used": target_lang,
                "translated": True,
                "error": None,
            }
        except Exception:
            entries = source.fetch()
            return {
                "text": _to_text(entries),
                "language_used": source.language_code,
                "translated": False,
                "error": None,
            }
    except Exception as exc:
        return {"text": "", "language_used": "", "translated": False, "error": str(exc)}


def get_duration_from_transcript(video_id: str) -> int | None:
    """Transcript entry'lerinden video süresini (saniye) tahmin eder."""
    try:
        transcript_list = _ytt.list(video_id)
        available = list(transcript_list)
        if not available:
            return None
        entries = available[0].fetch()
        if not entries:
            return None
        last = entries[-1]
        start = getattr(last, "start", None) or (last.get("start") if isinstance(last, dict) else None)
        dur = getattr(last, "duration", None) or (last.get("duration") if isinstance(last, dict) else None)
        if start is not None:
            return int(start + (dur or 0))
    except Exception:
        pass
    return None


def _to_text(entries) -> str:
    lines = []
    for entry in entries:
        text = entry.get("text", "") if isinstance(entry, dict) else getattr(entry, "text", "")
        text = text.strip()
        if text:
            lines.append(text)
    return "\n".join(lines)
