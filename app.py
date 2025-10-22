from flask import Flask, render_template, request, send_file
from download_video import probe_video, download_video_public
import os

app = Flask(__name__)

# ----- Folder dasar -----
BASE_DIR = os.path.dirname(__file__)
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def home():
    message = ""
    file_path = None
    thumbnail_url = None
    video_title = None
    url = None
    status = None
    reason = None

    if request.method == 'POST':
        url = request.form.get('url')
        action = request.form.get('action')

        if not url:
            message = "Masukkan URL terlebih dahulu."
        else:
            if action == "preview":
                info = probe_video(url)
                status = info['status']
                reason = info.get('reason')
                if status == 'public':
                    thumbnail_url = info['thumbnail']
                    video_title = info['title']

            elif action == "download":
                info = probe_video(url)
                status = info['status']
                reason = info.get('reason')
                if status == 'public':
                    hasil = download_video_public(url)
                    if isinstance(hasil, str) and os.path.isfile(hasil):
                        file_path = hasil
                    else:
                        message = hasil.get('error', 'Gagal mengunduh video.')
                else:
                    message = f"Tidak bisa download: {reason}"

    return render_template(
        'index.html',
        message=message,
        file_path=file_path,
        thumbnail_url=thumbnail_url,
        video_title=video_title,
        url=url,
        status=status,
        reason=reason
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
