import re
import logging
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
import yt_dlp

logger = logging.getLogger(__name__)

# Otomatik dil öncelik sırası: Türkçe → Almanca → İngilizce → ilk mevcut
AUTO_LANGUAGE_PRIORITY = ["tr", "de", "en"]


def extract_video_id(url: str) -> str | None:
    """YouTube URL'sinden video ID'sini çıkarır."""
    patterns = [
        r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_video_info(video_id: str) -> dict:
    """yt-dlp ile video başlığını ve süresini (saniye) getirir."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": False,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title", ""),
                "duration": info.get("duration"),  # saniye cinsinden int
            }
    except Exception as exc:
        logger.warning("yt-dlp video bilgisi alınamadı: %s", exc)
        return {"title": "", "duration": None}


def fetch_transcript(video_id: str, language_requested: str = "") -> dict:
    """
    Transcript metnini döndürür.

    Returns:
        {
            "text": str,          # birleşik düz metin
            "language_used": str, # kullanılan dil kodu
            "translated": bool,   # YouTube auto-translate kullanıldı mı
            "error": str | None,
        }
    """
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    except TranscriptsDisabled:
        return {"text": "", "language_used": "", "translated": False, "error": "Bu video için altyazı devre dışı bırakılmış."}
    except Exception as exc:
        return {"text": "", "language_used": "", "translated": False, "error": str(exc)}

    # Dil sıralaması belirle
    if language_requested:
        priority = [language_requested] + [l for l in AUTO_LANGUAGE_PRIORITY if l != language_requested]
    else:
        priority = AUTO_LANGUAGE_PRIORITY

    # 1. İstenilen/öncelikli dilde doğrudan transcript ara
    for lang in priority:
        try:
            transcript = transcript_list.find_transcript([lang])
            entries = transcript.fetch()
            return {
                "text": _entries_to_text(entries),
                "language_used": lang,
                "translated": False,
                "error": None,
            }
        except NoTranscriptFound:
            continue
        except Exception:
            continue

    # 2. Doğrudan bulunamadı → mevcut ilk transcript'i al, çevirmeyi dene
    try:
        available = list(transcript_list)
        if not available:
            return {"text": "", "language_used": "", "translated": False, "error": "Bu video için hiç altyazı bulunamadı."}

        source_transcript = available[0]
        target_lang = priority[0]  # kullanıcı seçimi veya tr

        try:
            translated = source_transcript.translate(target_lang)
            entries = translated.fetch()
            return {
                "text": _entries_to_text(entries),
                "language_used": target_lang,
                "translated": True,
                "error": None,
            }
        except Exception:
            # Çeviri de başarısız → orijinal dilde ver
            entries = source_transcript.fetch()
            return {
                "text": _entries_to_text(entries),
                "language_used": source_transcript.language_code,
                "translated": False,
                "error": None,
            }

    except Exception as exc:
        return {"text": "", "language_used": "", "translated": False, "error": str(exc)}


def list_available_languages(video_id: str) -> list[dict]:
    """Video için mevcut altyazı dillerini döndürür."""
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        langs = []
        for t in transcript_list:
            langs.append({
                "code": t.language_code,
                "name": t.language,
                "is_generated": t.is_generated,
                "is_translatable": t.is_translatable,
            })
        return langs
    except Exception:
        return []


def _entries_to_text(entries) -> str:
    """FetchedTranscript ya da dict listesini düz metne çevirir."""
    lines = []
    for entry in entries:
        if isinstance(entry, dict):
            text = entry.get("text", "")
        else:
            text = getattr(entry, "text", "")
        text = text.strip()
        if text:
            lines.append(text)
    return "\n".join(lines)
