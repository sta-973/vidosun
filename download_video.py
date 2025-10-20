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
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"

def auto_update_yt_dlp():
    """Update yt-dlp otomatis"""
    try:
        print("🔄 Memeriksa pembaruan yt-dlp...")
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
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title).200B.%(ext)s"),  # batasi nama
        "restrictfilenames": True,
        "noplaylist": True,
        "quiet": False,
        "no_warnings": False,
        "ignoreerrors": True,
        "ffmpeg_location": FFMPEG_PATH,
        "cookies": COOKIES_FILE,  # <- pakai cookies YouTube
        "progress_hooks": [
            lambda d: print(f"🔹 status: {d['status']}, filename: {d.get('filename','')}")
        ],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"\n⬇️ Mengunduh: {url}")
            info = ydl.extract_info(url, download=True)

            if not info:
                raise Exception("Tidak bisa ambil info video (mungkin URL tidak valid).")

            final_filename = ydl.prepare_filename(info).replace('.webm', '.mp4').replace('.m4a', '.mp4')

            if not os.path.exists(final_filename):
                base_name = os.path.splitext(ydl.prepare_filename(info))[0]
                for ext in ['.mp4', '.mkv', '.webm']:
                    potential_file = base_name + ext
                    if os.path.exists(potential_file):
                        final_filename = potential_file
                        break

            if os.path.exists(final_filename):
                print(f"\n✅ Berhasil disimpan sebagai: {final_filename}")
            else:
                raise Exception(f"File hasil tidak ditemukan setelah download. Cek folder {DOWNLOAD_DIR} secara manual.")

            # buka folder hasil
            try:
                if sys.platform == "win32":
                    os.startfile(DOWNLOAD_DIR)
                elif sys.platform == "darwin":
                    subprocess.run(["open", DOWNLOAD_DIR])
                else:
                    subprocess.run(["xdg-open", DOWNLOAD_DIR])
            except Exception as open_err:
                print(f"⚠️ Gagal membuka folder: {open_err}")

            return final_filename

    except Exception as e:
        print(f"❌ ERROR DETAIL: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    url = input("Masukkan URL video YouTube: ")
    download_video(url)
