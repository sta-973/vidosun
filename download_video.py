import os
import sys
import yt_dlp
import subprocess
from datetime import datetime
import requests

# ----- Folder download -----
BASE_DIR = os.path.dirname(__file__)
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ----- Folder log -----
LOG_FILE = os.path.join(BASE_DIR, "download.log")

# ----- Auto-detect FFmpeg path -----
POSSIBLE_FFMPEG_PATHS = [
    "/usr/bin/ffmpeg",
    "/usr/local/bin/ffmpeg",
    "ffmpeg"
]

FFMPEG_PATH = None
for path in POSSIBLE_FFMPEG_PATHS:
    if os.path.exists(path) or path == "ffmpeg":
        FFMPEG_PATH = path
        break

if not FFMPEG_PATH:
    print("⚠️ FFmpeg tidak ditemukan. Pastikan sudah diinstall di server.")
    sys.exit(1)

# ----- Cookies per platform -----
COOKIES_MAP = {
    "youtube.com": os.path.join(BASE_DIR, "youtube.com_cookies.txt"),
    "instagram.com": os.path.join(BASE_DIR, "instagram.com_cookies.txt"),
    "facebook.com": os.path.join(BASE_DIR, "facebook.com_cookies.txt"),
    "threads.net": os.path.join(BASE_DIR, "threads.com_cookies.txt"),
    "tiktok.com": os.path.join(BASE_DIR, "tiktok.com_cookies.txt")
}

# ----- Logging helper -----
def log(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {message}\n")
    print(message)

# ----- Get cookies file -----
def get_cookies_file(url: str):
    for domain, path in COOKIES_MAP.items():
        if domain in url:
            if os.path.exists(path):
                return path
            else:
                log(f"⚠️ Cookies file untuk {domain} tidak ditemukan: {path}")
                return None
    return None

# ----- Cek validitas cookies -----
def check_cookies(url: str):
    cookies_file = get_cookies_file(url)
    if not cookies_file:
        return False

    domain = None
    for d in COOKIES_MAP.keys():
        if d in url:
            domain = d
            break
    if not domain:
        return True

    test_url_map = {
        "youtube.com": "https://www.youtube.com/",
        "instagram.com": "https://www.instagram.com/",
        "facebook.com": "https://www.facebook.com/",
        "threads.net": "https://www.threads.net/",
        "tiktok.com": "https://www.tiktok.com/"
    }
    test_url = test_url_map.get(domain, url)

    try:
        with open(cookies_file, "r", encoding="utf-8") as f:
            cookies_lines = f.readlines()
        cookies_dict = {}
        for line in cookies_lines:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.strip().split("\t")
            if len(parts) >= 7:
                cookies_dict[parts[5]] = parts[6]

        resp = requests.get(test_url, cookies=cookies_dict, timeout=10)
        if resp.status_code in [200, 302]:
            return True
        else:
            log(f"⚠️ Cookies mungkin expired untuk {domain}, status code: {resp.status_code}")
            return False
    except Exception as e:
        log(f"⚠️ Gagal cek cookies {cookies_file}: {e}")
        return False

# ----- Download single video -----
def download_video(url: str):
    if not check_cookies(url):
        log(f"❌ Download dibatalkan. Cookies tidak valid untuk URL: {url}")
        return

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    cookies_file = get_cookies_file(url)

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(DOWNLOAD_DIR, "%(title).200B.%(ext)s"),
        'restrictfilenames': True,
        'noplaylist': True,
        'quiet': False,
        'no_warnings': False,
        'ffmpeg_location': FFMPEG_PATH,
        'cookies': cookies_file,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            final_filename = ydl.prepare_filename(info)
            if os.path.exists(final_filename):
                log(f"✅ Berhasil: {final_filename}")
            else:
                base_name = os.path.splitext(final_filename)[0]
                found = False
                for ext in ['.mp4', '.mkv', '.webm']:
                    potential_file = base_name + ext
                    if os.path.exists(potential_file):
                        log(f"✅ Berhasil: {potential_file}")
                        found = True
                        break
                if not found:
                    log(f"❌ Gagal menyimpan file untuk URL: {url}")
    except Exception as e:
        log(f"❌ Error download URL {url}: {e}")

# ----- Multi-download dari list.txt -----
def download_from_list(file_path="list.txt"):
    if not os.path.exists(file_path):
        log(f"⚠️ File {file_path} tidak ditemukan.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    valid_urls = []
    for url in urls:
        if check_cookies(url):
            valid_urls.append(url)
        else:
            log(f"❌ Cookies tidak valid, URL dilewati: {url}")

    log(f"🟢 Mulai download {len(valid_urls)} video dari {file_path}")
    for url in valid_urls:
        log(f"⬇️ Download: {url}")
        download_video(url)
    log("✅ Semua download selesai.")

# ----- Main -----
if __name__ == "__main__":
    choice = input("Masukkan URL video atau ketik 'list' untuk multi-download: ").strip()
    if choice.lower() == "list":
        download_from_list()
    else:
        download_video(choice)
