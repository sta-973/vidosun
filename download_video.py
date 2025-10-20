import os
import sys
import yt_dlp
import subprocess # <--- TAMBAHKAN INI

# Folder download
BASE_DIR = os.path.dirname(__file__)
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# --- PERUBAHAN 1: Path FFmpeg yang Dinamis ---
# Coba cari path ffmpeg yang umum di Linux. Jika tidak ada, yt-dlp akan mencarinya sendiri.
# Di server Linux, ffmpeg biasanya ada di /usr/bin/ffmpeg
FFMPEG_PATH = "/usr/bin/ffmpeg" 

# Mapping cookies per platform
COOKIES_MAP = {
    "youtube.com": os.path.join(BASE_DIR, "youtube.com_cookies.txt"),
    "instagram.com": os.path.join(BASE_DIR, "instagram.com_cookies.txt"),
    "facebook.com": os.path.join(BASE_DIR, "facebook.com_cookies.txt"),
    "threads.net": os.path.join(BASE_DIR, "threads.com_cookies.txt"),
    "tiktok.com": os.path.join(BASE_DIR, "tiktok.com_cookies.txt")
}

# --- PERUBAHAN 2: Update Yt-dlp Secara Manual ---
# Fungsi ini tidak dipanggil otomatis lagi untuk mencegah timeout.
# Anda harus menjalankannya manual di server (lihat petunjuk di bawah).
def manual_update_yt_dlp():
    """Update yt-dlp. Jalankan manual di server via SSH."""
    try:
        subprocess.run([sys.executable, "-m", "yt_dlp", "-U"], check=True)
        print("✅ yt-dlp berhasil diperbarui.")
    except Exception as e:
        print(f"⚠️ Gagal update yt-dlp: {e}")

def get_cookies_file(url: str):
    """Pilih file cookies sesuai platform"""
    for domain, path in COOKIES_MAP.items():
        if domain in url:
            return path if os.path.exists(path) else None
    return None

def download_video(url: str):
    """Download video dengan opsi yang lebih robust untuk server"""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    cookies_file = get_cookies_file(url)

    # --- PERUBAHAN 3: Opsi yt-dlp yang Lebih Baik ---
    ydl_opts = {
        # Format ini lebih aman. Coba gabungkan, jika gagal, ambil yang terbaik yang tersedia.
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(DOWNLOAD_DIR, "%(title).200B.%(ext)s"),
        'restrictfilenames': True,
        'noplaylist': True,
        'quiet': True, # Ubah ke False untuk debugging di server
        'no_warnings': False,
        # --- PERUBAHAN 4: Hapus ignoreerrors untuk melihat error asli ---
        # 'ignoreerrors': True, # Dikomentari agar kita tahu penyebab errornya
        'ffmpeg_location': FFMPEG_PATH,
        'cookies': cookies_file,
        # Tambahkan user-agent untuk meniru browser asli
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                raise Exception("Tidak bisa mengambil info video. Mungkin URL tidak valid atau diblokir.")

            # yt-dlp dengan 'merge_output_format' sudah cukup pintar untuk memberi nama file akhir yang benar
            final_filename = ydl.prepare_filename(info)
            
            # Cek jika file berhasil dibuat
            if os.path.exists(final_filename):
                print(f"\n✅ Berhasil disimpan di: {final_filename}")
                return final_filename
            else:
                # Kadang nama file ekstensi bisa berbeda, coba cari
                base_name = os.path.splitext(final_filename)[0]
                for ext in ['.mp4', '.mkv', '.webm']:
                    potential_file = base_name + ext
                    if os.path.exists(potential_file):
                        print(f"\n✅ Berhasil disimpan di: {potential_file}")
                        return potential_file
                
                raise Exception(f"File hasil tidak ditemukan setelah download. Cek folder {DOWNLOAD_DIR}.")

    except Exception as e:
        # Kembalikan error yang lebih jelas
        return {"error": f"Gagal mendownload video. Alasan: {str(e)}"}

if __name__ == "__main__":
    # Untuk testing di lokal, Anda bisa tetap gunakan path Windows
    # FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe" 
    url = input("Masukkan URL video: ")
    print(download_video(url))

