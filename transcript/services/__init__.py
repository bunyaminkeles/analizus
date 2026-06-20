import re
import os
import logging
import tempfile
import threading
import yt_dlp

logger = logging.getLogger(__name__)

# Model cache — bir kez yükle, thread-safe kilitle koru
_model_cache: dict = {}
_model_lock = threading.Lock()

# Cookie dosyası — YouTube bot engelini aşmak için
# Hetzner'de: /app/youtube_cookies.txt olarak bırakın
COOKIES_FILE = os.environ.get("YOUTUBE_COOKIES_FILE", "/app/youtube_cookies.txt")


def _yt_opts_base(extra: dict = None) -> dict:
    """Ortak yt-dlp seçeneklerini döndürür; cookie varsa ekler."""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "js_runtimes": ["node"],
        "extractor_args": {"youtube": {"player_client": ["ios", "web"]}},
    }
    if os.path.isfile(COOKIES_FILE):
        opts["cookiefile"] = COOKIES_FILE
    if extra:
        opts.update(extra)
    return opts


def extract_video_id(url: str) -> str | None:
    """YouTube URL'sinden video ID'sini çıkarır."""
    match = re.search(r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})", url)
    return match.group(1) if match else None


def get_video_info(video_id: str) -> dict:
    """yt-dlp ile video başlığını ve süresini (saniye) getirir."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = _yt_opts_base({"skip_download": True})
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {"title": info.get("title", ""), "duration": info.get("duration")}
    except Exception as exc:
        logger.warning("yt-dlp video bilgisi alınamadı: %s", exc)
        return {"title": "", "duration": None}


def download_audio(video_id: str, output_dir: str) -> str:
    """Videodan ses dosyasını indirir, dosya yolunu döndürür."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    output_template = os.path.join(output_dir, "audio.%(ext)s")
    ydl_opts = _yt_opts_base({
        "format": "bestaudio/best",
        "outtmpl": output_template,
    })
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    for fname in os.listdir(output_dir):
        if fname.startswith("audio."):
            return os.path.join(output_dir, fname)
    raise FileNotFoundError("Ses dosyası indirilemedi.")


def _get_model(model_size: str):
    """Whisper modelini cache'den döndürür; ilk çağrıda yükler."""
    with _model_lock:
        if model_size not in _model_cache:
            from faster_whisper import WhisperModel
            logger.info("Whisper modeli yükleniyor: %s", model_size)
            _model_cache[model_size] = WhisperModel(
                model_size,
                device="cpu",
                compute_type="int8",  # CPU için hızlı ve az bellek
            )
            logger.info("Whisper modeli hazır: %s", model_size)
        return _model_cache[model_size]


def transcribe_audio(audio_path: str, language: str = "", model_size: str = "small") -> dict:
    """
    Ses dosyasını Whisper ile metne çevirir.

    Returns:
        {"text": str, "language_used": str, "error": str | None}
    """
    try:
        model = _get_model(model_size)
        lang_hint = language if language else None
        segments, info = model.transcribe(
            audio_path,
            language=lang_hint,
            beam_size=5,
            vad_filter=True,       # sessiz bölümleri atla
            vad_parameters={"min_silence_duration_ms": 500},
        )
        text = "\n".join(segment.text.strip() for segment in segments if segment.text.strip())
        detected_lang = info.language if hasattr(info, "language") else (language or "")
        return {"text": text, "language_used": detected_lang, "error": None}
    except Exception as exc:
        logger.error("Whisper transkripsiyon hatası: %s", exc, exc_info=True)
        return {"text": "", "language_used": "", "error": str(exc)}
