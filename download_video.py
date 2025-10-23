import os
import yt_dlp

# Folder download
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_video(url):
    """
    Download video publik dari YouTube, TikTok, Instagram, Facebook tanpa cookies.
    Mengembalikan path file jika berhasil, atau dict error jika gagal.
    """
    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'retries': 2,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            if info is None:
                # Video tidak bisa diunduh (privat, age restricted, atau dibatasi)
                return {
                    'error': (
                        "Video ini tidak dapat diunduh karena bersifat privat, dibatasi usia, "
                        "atau platform membatasi akses. Vidosun hanya mendukung video publik."
                    )
                }

            # Siapkan nama file hasil download
            filename = ydl.prepare_filename(info)
            if not os.path.exists(filename):
                return {'error': "Gagal menyimpan file. Cek URL atau format video."}

            return filename

    except yt_dlp.utils.DownloadError as e:
        # Error khusus yt-dlp (login, rate-limit, atau dibatasi)
        return {'error': (
            "Video ini memerlukan login, dibatasi usia, atau bersifat privat. "
            "Vidosun hanya mendukung video publik."
        )}

    except Exception as e:
        return {'error': f"Gagal mengunduh: {e}"}

# Contoh pemanggilan
if __name__ == "__main__":
    url = input("Masukkan URL video: ").strip()
    hasil = download_video(url)
    print("Hasil:", hasil)
