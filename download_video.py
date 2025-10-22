import os
import yt_dlp

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_video_public(url):
    """Download video publik tanpa cookies"""
    try:
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'format': 'best',
            'noplaylist': True,
            'quiet': True,  # supaya tidak terlalu banyak log
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename

    except Exception as e:
        return {"error": f"Gagal mengunduh: {e}"}
