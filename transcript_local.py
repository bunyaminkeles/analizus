"""
YouTube Lokal Transcript Aracı
================================
Gereksinimler (bir kez kur):
    pip install faster-whisper yt-dlp
    # Linux/Mac: sudo apt install ffmpeg  veya  brew install ffmpeg
    # Windows:   https://ffmpeg.org/download.html

Kullanım:
    python transcript_local.py <youtube_url>
    python transcript_local.py <youtube_url> --language tr
    python transcript_local.py <youtube_url> --model medium
    python transcript_local.py <youtube_url> --output dosya.txt

Modeller: tiny | base | small (varsayılan) | medium | large-v3
"""

import argparse
import os
import sys
import tempfile

def main():
    parser = argparse.ArgumentParser(description="YouTube video ses → metin (Whisper STT)")
    parser.add_argument("url", help="YouTube video URL'si")
    parser.add_argument("--language", "-l", default="", help="Dil kodu (tr, de, en...). Boş = otomatik algıla")
    parser.add_argument("--model", "-m", default="small", choices=["tiny", "base", "small", "medium", "large-v3"], help="Whisper model boyutu (varsayılan: small)")
    parser.add_argument("--output", "-o", default="", help="Çıktı dosyası (varsayılan: otomatik isim)")
    args = parser.parse_args()

    try:
        import yt_dlp
    except ImportError:
        print("Hata: yt-dlp kurulu değil. Kurmak için: pip install yt-dlp")
        sys.exit(1)

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("Hata: faster-whisper kurulu değil. Kurmak için: pip install faster-whisper")
        sys.exit(1)

    print(f"Video bilgisi alınıyor...")
    with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
        try:
            info = ydl.extract_info(args.url, download=False)
            title = info.get("title", "transcript")
            duration = info.get("duration", 0)
            print(f"Başlık : {title}")
            print(f"Süre   : {duration // 60} dk {duration % 60} sn")
        except Exception as e:
            print(f"Hata: Video bilgisi alınamadı — {e}")
            sys.exit(1)

    with tempfile.TemporaryDirectory() as tmpdir:
        print("Ses indiriliyor...")
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(tmpdir, "audio.%(ext)s"),
            "quiet": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([args.url])
            except Exception as e:
                print(f"Hata: Ses indirilemedi — {e}")
                sys.exit(1)

        audio_files = [f for f in os.listdir(tmpdir) if f.startswith("audio.")]
        if not audio_files:
            print("Hata: Ses dosyası bulunamadı.")
            sys.exit(1)
        audio_path = os.path.join(tmpdir, audio_files[0])

        print(f"Transkripsiyon başlıyor (model: {args.model})...")
        model = WhisperModel(args.model, device="cpu", compute_type="int8")
        lang_hint = args.language if args.language else None
        segments, info = model.transcribe(
            audio_path,
            language=lang_hint,
            beam_size=5,
            vad_filter=True,
        )

        lines = []
        for segment in segments:
            text = segment.text.strip()
            if text:
                lines.append(text)
                print(f"  [{segment.start:.0f}s] {text}")

        detected_lang = info.language if hasattr(info, "language") else (args.language or "?")
        full_text = "\n".join(lines)

    # Çıktı dosyasını belirle
    if args.output:
        output_path = args.output
    else:
        safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)[:60]
        output_path = f"transcript_{safe}.txt"

    header = (
        f"YouTube Transcript\n"
        f"Başlık : {title}\n"
        f"Video  : {args.url}\n"
        f"Dil    : {detected_lang}\n"
        f"Model  : {args.model}\n"
        f"{'─' * 50}\n\n"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(header + full_text)

    print(f"\nTamamlandı! Dosya: {output_path}")
    print(f"Toplam {len(lines)} cümle, {len(full_text)} karakter.")


if __name__ == "__main__":
    main()
