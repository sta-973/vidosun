import os
import yt_dlp
import webbrowser

# Folder utama download
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Lokasi folder cookies utama (Render)
COOKIES_DIR = "/data/cookies"
LOCAL_COOKIES_DIR = os.path.join(os.path.dirname(__file__), "cookies")
os.makedirs(LOCAL_COOKIES_DIR, exist_ok=True)

def get_cookie_file(domain):
    """Cari file cookies untuk domain tertentu"""
    paths = [
        os.path.join(COOKIES_DIR, f"{domain}_cookies.txt"),
        os.path.join(LOCAL_COOKIES_DIR, f"{domain}_cookies.txt"),
        os.path.join(os.path.dirname(__file__), f"{domain}_cookies.txt"),
    ]
    for path in paths:
        if os.path.exists(path):
            return path
    return None


def update_expired_cookies():
    """Cek dan minta update jika cookies hilang"""
    domains = ["youtube.com", "tiktok.com", "instagram.com", "facebook.com", "threads.net"]
    for domain in domains:
        cookie_path = get_cookie_file(domain)
        if not cookie_path:
            print(f"⚠️ File cookies /data/cookies/{domain}_cookies.txt tidak ditemukan.")
            print(f"🌐 Membuka browser untuk update cookies {domain}")
            print(f"➡️ Silakan login, export cookies ke: /data/cookies/{domain}_cookies.txt")
            if domain == "threads.net":
                webbrowser.open("https://www.threads.net")
            elif domain == "tiktok.com":
                webbrowser.open("https://www.tiktok.com")
            elif domain == "instagram.com":
                webbrowser.open("https://www.instagram.com")
            elif domain == "facebook.com":
                webbrowser.open("https://www.facebook.com")
            elif domain == "youtube.com":
                webbrowser.open("https://www.youtube.com")


def download_video(url, cookie_file=None):
    """Download video tunggal"""
    try:
        # Deteksi domain
        domain = ""
        if "youtube" in url:
            domain = "youtube.com"
        elif "tiktok" in url:
            domain = "tiktok.com"
        elif "instagram" in url:
            domain = "instagram.com"
        elif "facebook" in url:
            domain = "facebook.com"
        elif "threads" in url:
            domain = "threads.net"

        # Tentukan cookies
        cookie_path = cookie_file or get_cookie_file(domain)
        if not cookie_path or not os.path.exists(cookie_path):
            return {"error": f"❌ Download dibatalkan. Cookies tidak valid untuk URL: {url}"}

        # Opsi yt-dlp
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'format': 'best',
            'noplaylist': True,
            'cookies': cookie_path,
        }

        # Download video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            print(f"✅ Video berhasil diunduh: {filename}")
            return filename

    except Exception as e:
        print(f"❌ Gagal mengunduh: {e}")
        return {"error": f"Gagal mengunduh: {e}"}


def download_from_list():
    """Multi-download dari file list.txt"""
    list_path = os.path.join(os.path.dirname(__file__), "list.txt")
    if not os.path.exists(list_path):
        print("❌ File list.txt tidak ditemukan.")
        return

    with open(list_path, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    for url in urls:
        print(f"\n🔗 Mengunduh: {url}")
        download_video(url)


if __name__ == "__main__":
    update_expired_cookies()
    choice = input("Masukkan URL video atau ketik 'list' untuk multi-download: ").strip()
    if choice.lower() == "list":
        download_from_list()
    else:
        download_video(choice)
