from flask import Flask, render_template, request, send_file
from download_video import download_video
import os
import yt_dlp

app = Flask(__name__)

# Folder download
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# File cookies YouTube
COOKIE_FILE = os.path.join(os.path.dirname(__file__), "youtube.com_cookies.txt")

# Daftar artikel
ALLOWED_ARTICLES = ['artikel1', 'artikel2', 'artikel3']

def get_video_info(url):
    """Ambil info video dengan cookies"""
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'noplaylist': True,
        'cookies': COOKIE_FILE if os.path.exists(COOKIE_FILE) else None
    }
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
        action = request.form.get('action')  # "preview" atau "download"

        if not url:
            message = "Masukkan URL terlebih dahulu."
        else:
            try:
                if action == "preview":
                    info = get_video_info(url)
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

            except Exception as e:
                message = f"Gagal memuat info video: {e}"

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
    if nama in ALLOWED_ARTICLES:
        return render_template(f"{nama}.html")
    return "Artikel tidak ditemukan", 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
