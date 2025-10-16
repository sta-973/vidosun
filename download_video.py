import os
import yt_dlp
import uuid

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_video(url: str) -> str:
    """
    Download video dari YouTube, Instagram, Facebook.
    Return: path file jika sukses, else error string.
    """
    filename = os.path.join(DOWNLOAD_DIR, f"{uuid.uuid4()}.mp4")
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': filename,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return filename
    except Exception as e:
        return f"Gagal download: {e}"
