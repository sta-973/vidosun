from flask import Flask, render_template, request, send_file
from download_video import download_video_public
import os

app = Flask(__name__)

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

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
            try:
                if action == "preview":
                    # Info video publik (thumbnail + title)
                    ydl_opts = {'quiet': True, 'skip_download': True}
                    import yt_dlp
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        thumbnail_url = info.get('thumbnail')
                        video_title = info.get('title')

                elif action == "download":
                    hasil = download_video_public(url)
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
    ALLOWED_ARTICLES = ['artikel1', 'artikel2', 'artikel3']
    if nama in ALLOWED_ARTICLES:
        return render_template(f"{nama}.html")
    return "Artikel tidak ditemukan", 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
