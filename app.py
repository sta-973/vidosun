from flask import Flask, render_template, request, send_file
from download_video import probe_video, download_video_public
import os

app = Flask(__name__)
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/', methods=['GET','POST'])
def home():
    message = ""
    file_path = None
    thumbnail_url = None
    video_title = None
    url = None
    status = None
    reason = None

    if request.method == 'POST':
        url = request.form.get('url','').strip()
        action = request.form.get('action')
        if not url:
            message = "Masukkan URL terlebih dahulu."
        else:
            probe = probe_video(url)
            status = probe.get('status')
            video_title = probe.get('title')
            thumbnail_url = probe.get('thumbnail')
            reason = probe.get('reason')

            if action=="preview":
                if status=='public':
                    message="Video publik — siap untuk diunduh."
                elif status=='needs_cookies':
                    message="Butuh login / cookies untuk mengakses video ini."
                elif status=='private':
                    message="Video bersifat privat — tidak dapat diunduh."
                elif status=='age_restricted':
                    message="Video terikat batas umur."
                elif status=='region_restricted':
                    message="Video dibatasi wilayah."
                elif status=='not_found':
                    message="Video tidak ditemukan."
                else:
                    message=f"Status: {status}. {reason or ''}"

            elif action=="download":
                if status!='public':
                    message=f"Gagal: video bukan publik ({status}). {reason or ''}"
                else:
                    hasil = download_video_public(url)
                    if isinstance(hasil, dict) and 'error' in hasil:
                        message=hasil['error']
                    elif isinstance(hasil,str) and os.path.exists(hasil):
                        file_path=hasil
                        message="Selesai: video berhasil diunduh."
                    else:
                        message="Gagal mengunduh video."

    return render_template('index.html', message=message, file_path=file_path,
                           thumbnail_url=thumbnail_url, video_title=video_title,
                           url=url, status=status, reason=reason)

@app.route('/download/<filename>')
def download_file(filename):
    path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "File tidak ditemukan",404

if __name__=="__main__":
    port = int(os.environ.get("PORT",10000))
    app.run(host='0.0.0.0', port=port, debug=False)
