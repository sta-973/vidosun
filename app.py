from flask import Flask, render_template, request, send_file
from download_video import download_video
import os
import yt_dlp

app = Flask(__name__)

# ----- Folder dasar -----
BASE_DIR = os.path.dirname(__file__)
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ----- Peta cookies per domain -----
COOKIES_MAP = {
    "youtube.com": "/data/cookies/youtube.com_cookies.txt",
    "instagram.com": "/data/cookies/instagram.com_cookies.txt",
    "facebook.com": "/data/cookies/facebook.com_cookies.txt",
    "threads.net": "/data/cookies/threads.net_cookies.txt",
    "tiktok.com": "/data/cookies/tiktok.com_cookies.txt",
}

def get_cookies_file(url: str):
    """Deteksi domain dan pilih cookies yang sesuai."""
    for domain, path in COOKIES_MAP.items():
        if domain in url:
            if os.path.exists(path):
                print(f"🟢 Menggunakan cookies {domain} dari {path}")
                return path
            else:
                print(f"⚠️ File cookies untuk {domain} tidak ditemukan: {path}")
                return None
    return None

# ----- Ambil info video -----
def get_video_info(url, cookies_file=None):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'noplaylist': True,
    }

    if cookies_file and os.path.exists(cookies_file):
        ydl_opts['cookies'] = cookies_file

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'url': info.get('webpage_url')
            }
    except Exception as e:
        return {'error': str(e)}

@app.route('/', methods=['GET', 'POST'])
def home():
    message = ""
    file_path = None
    thumbnail_url = None
    video_title = None
    url = None

    if request.method == 'POST':
        url = request.form.get('url')
        action = request.form.get('action')

        if not url:
            message = "Masukkan URL terlebih dahulu."
        else:
            cookies_file = get_cookies_file(url)

            if action == "preview":
                info = get_video_info(url, cookies_file)
                if 'error' in info:
                    message = f"Gagal memuat info video: {info['error']}"
                else:
                    thumbnail_url = info['thumbnail']
                    video_title = info['title']

            elif action == "download":
                hasil = download_video(url)
                if isinstance(hasil, dict) and "error" in hasil:
                    message = hasil["error"]
                elif isinstance(hasil, str) and os.path.isfile(hasil):
                    file_path = hasil
                else:
                    message = "Gagal mengunduh video."

    return render_template(
        'index.html',
        message=message,
        file_path=file_path,
        thumbnail_url=thumbnail_url,
        video_title=video_title,
        url=url
    )

@app.route('/download/<filename>')
def download_file(filename):
    path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "File tidak ditemukan", 404

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/artikel/<nama>')
def artikel(nama):
    allowed_articles = ['artikel1', 'artikel2', 'artikel3']
    if nama in allowed_articles:
        return render_template(f"{nama}.html")
    return "Artikel tidak ditemukan", 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
