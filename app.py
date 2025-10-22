from flask import Flask, render_template, request, send_file
import os
import yt_dlp
import logging

# ----- Logging debug -----
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# ----- Folder download -----
BASE_DIR = os.path.dirname(__file__)
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ----- Probe video (cek status tanpa download) -----
def probe_video(url):
    """
    Mengembalikan status video dan metadata tanpa download.
    status: public | private | age_restricted | not_found | error
    """
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'nocheckcertificate': True,
        'noplaylist': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info is None:
                return {'status':'not_found','title':None,'thumbnail':None,'reason':'Tidak ada info.'}

            # cek age_limit
            if info.get('age_limit',0) >= 18:
                return {'status':'age_restricted','title':info.get('title'),'thumbnail':info.get('thumbnail'),'reason':'Perlu verifikasi umur.'}

            return {'status':'public','title':info.get('title'),'thumbnail':info.get('thumbnail'),'reason':None}

    except yt_dlp.utils.DownloadError as e:
        msg = str(e)
        if 'private' in msg.lower():
            return {'status':'private','title':None,'thumbnail':None,'reason':'Video bersifat privat.'}
        if 'not available' in msg.lower() or '404' in msg:
            return {'status':'not_found','title':None,'thumbnail':None,'reason':msg}
        return {'status':'error','title':None,'thumbnail':None,'reason':msg}
    except Exception as e:
        return {'status':'error','title':None,'thumbnail':None,'reason':str(e)}

# ----- Download video publik -----
def download_video(url):
    """Download video publik tanpa cookies"""
    try:
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'format': 'best',
            'noplaylist': True,
            'quiet': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        return {'error': f"Gagal mengunduh: {e}"}

# ----- Route utama -----
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
            try:
                info = probe_video(url)
                status = info['status']
                video_title = info.get('title')
                thumbnail_url = info.get('thumbnail')
                reason = info.get('reason')

                if action == "download":
                    if status == "public":
                        hasil = download_video(url)
                        if isinstance(hasil, dict) and "error" in hasil:
                            message = hasil["error"]
                        elif isinstance(hasil, str) and os.path.isfile(hasil):
                            file_path = hasil
                        else:
                            message = "Gagal mengunduh video."
                    else:
                        message = "Video tidak bisa diunduh karena bersifat private / terbatas."

            except Exception as e:
                message = f"Gagal memproses URL: {e}"
                status = "error"
                reason = str(e)

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

# ----- Route download file -----
@app.route('/download/<filename>')
def download_file(filename):
    path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "File tidak ditemukan", 404

# ----- Route privacy & terms -----
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

# ----- Route artikel -----
@app.route('/artikel/<nama>')
def artikel(nama):
    allowed_articles = ['artikel1', 'artikel2', 'artikel3']
    if nama in allowed_articles:
        return render_template(f"{nama}.html")
    return "Artikel tidak ditemukan", 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
