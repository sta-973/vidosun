import os
import sys
import subprocess
import yt_dlp

BASE_DIR = os.path.dirname(__file__)
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def auto_update_yt_dlp():
    """Update yt-dlp otomatis"""
    try:
        print("🔄 Memeriksa pembaruan yt-dlp...")
        subprocess.run([sys.executable, "-m", "yt_dlp", "-U"], check=False)
    except Exception as e:
        print(f"⚠️ Gagal update yt-dlp: {e}")


def download_video(url: str):
    """Download video lengkap (video + audio)"""
    auto_update_yt_dlp()
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    try:
        ydl_opts = {
            "format": "bv*+ba/best",
            "merge_output_format": "mp4",
            "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
            "noplaylist": True,
            "quiet": False,
            "no_warnings": False,
            "ignoreerrors": True,
            "extractor_args": {"youtube": {"player_client": ["tv"]}},
            "postprocessors": [
                {
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4",
                }
            ],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"\n⬇️ Mengunduh: {url}")
            info = ydl.extract_info(url, download=True)

            if not info:
                raise Exception("Tidak bisa ambil info video (mungkin URL tidak valid).")

            filename = ydl.prepare_filename(info)
            if not os.path.exists(filename):
                # cari file mirip (misal .webm atau .mkv)
                folder_files = os.listdir(DOWNLOAD_DIR)
                match_files = [
                    f for f in folder_files if info.get("title", "")[:15] in f
                ]
                if match_files:
                    filename = os.path.join(DOWNLOAD_DIR, match_files[0])
                else:
                    raise Exception(f"File hasil tidak ditemukan: {filename}")

            print(f"\n✅ Berhasil disimpan sebagai: {filename}")

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

            return filename

    except Exception as e:
        print(f"❌ ERROR DETAIL: {e}")
        return {"error": str(e)}
