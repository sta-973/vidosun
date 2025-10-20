import os
import sys
import subprocess
import yt_dlp

# Folder download
BASE_DIR = os.path.dirname(__file__)
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# File cookies YouTube
COOKIES_FILE = os.path.join(BASE_DIR, "youtube.com_cookies.txt")

# Lokasi FFmpeg (ubah sesuai tempat ffmpeg.exe di PC kamu)
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"  # Windows
# FFMPEG_PATH = "/usr/bin/ffmpeg"          # Linux / macOS

def auto_update_yt_dlp():
    """Update yt-dlp otomatis"""
    try:
        subprocess.run([sys.executable, "-m", "yt_dlp", "-U"], check=False)
    except Exception as e:
        print(f"⚠️ Gagal update yt-dlp: {e}")

def download_video(url: str):
    """Download video + audio DASH otomatis dan merge jadi MP4"""
    auto_update_yt_dlp()
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title).200B.%(ext)s"),
        "restrictfilenames": True,
        "noplaylist": True,
        "quiet": False,
        "no_warnings": False,
        "ignoreerrors": True,
        "ffmpeg_location": FFMPEG_PATH,
        "cookies": COOKIES_FILE if os.path.exists(COOKIES_FILE) else None,
        "progress_hooks": [
            lambda d: print(f"🔹 status: {d['status']}, filename: {d.get('filename','')}")
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                raise Exception("Tidak bisa ambil info video.")

            final_filename = ydl.prepare_filename(info).replace('.webm', '.mp4').replace('.m4a', '.mp4')

            if not os.path.exists(final_filename):
                base_name = os.path.splitext(ydl.prepare_filename(info))[0]
                for ext in ['.mp4', '.mkv', '.webm']:
                    potential_file = base_name + ext
                    if os.path.exists(potential_file):
                        final_filename = potential_file
                        break

            if os.path.exists(final_filename):
                return final_filename
            else:
                raise Exception(f"File hasil tidak ditemukan. Cek folder {DOWNLOAD_DIR}.")

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    url = input("Masukkan URL video YouTube: ")
    print(download_video(url))
