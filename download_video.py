import os
import sys
import subprocess
import yt_dlp

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def auto_update_yt_dlp():
    """Update yt-dlp otomatis untuk mengikuti perubahan situs"""
    try:
        print("🔄 Memeriksa pembaruan yt-dlp...")
        subprocess.run([sys.executable, "-m", "yt_dlp", "-U"], check=False)
    except Exception as e:
        print(f"⚠️ Gagal update yt-dlp: {e}")


def get_video_info(url: str):
    """Ambil info video tanpa download (judul + thumbnail)"""
    try:
        ydl_opts = {'quiet': True, 'noplaylist': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'uploader': info.get('uploader'),
                'duration': info.get('duration'),
            }
    except Exception as e:
        print(f"⚠️ Gagal ambil info: {e}")
        return None


def download_video(url: str):
    """Fungsi utama untuk mengunduh video dari berbagai platform"""
    auto_update_yt_dlp()

    try:
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"⬇️ Mengunduh: {url}")
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            print(f"✅ Berhasil: {filename}")
            return filename

    except Exception as e:
        error_text = str(e).lower()

        if "sign in" in error_text or "login required" in error_text:
            return "⚠️ Video ini memerlukan login (private atau dibatasi platform)."
        elif "rate-limit" in error_text:
            return "⚠️ Terlalu banyak permintaan. Tunggu beberapa menit lalu coba lagi."
        elif "cannot parse data" in error_text:
            return "⚠️ Situs ini baru mengubah formatnya. Tunggu update yt-dlp selanjutnya."
        elif "unavailable" in error_text or "404" in error_text:
            return "⚠️ Video tidak tersedia (mungkin dihapus atau di-private)."
        else:
            return f"❌ Gagal download: {e}"
