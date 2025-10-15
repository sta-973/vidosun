from flask import Flask, request, send_file, render_template
import os
import subprocess
import urllib.parse

app = Flask(__name__, template_folder='.', static_folder='static')

# Folder untuk simpan sementara file download
DOWNLOAD_FOLDER = os.path.join('static', 'downloads')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def sanitize_filename(name):
    # Hapus karakter yang bermasalah di filename
    return "".join(c for c in name if c.isalnum() or c in " ._-").strip()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url:
        return "URL tidak ditemukan!", 400

    try:
        # Tentukan output file sementara
        output_template = os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s')

        # Jalankan yt-dlp
        proc = subprocess.run([
            'yt-dlp',
            '-f', 'best',
            '-o', output_template,
            url
        ], capture_output=True, text=True)

        if proc.returncode != 0:
            print(proc.stderr)
            return "Gagal download", 500

        # Cari file terbaru di folder
        files = [os.path.join(DOWNLOAD_FOLDER, f) for f in os.listdir(DOWNLOAD_FOLDER)]
        latest_file = max(files, key=os.path.getctime)

        # Kirim file ke user
        filename = sanitize_filename(os.path.basename(latest_file))
        return send_file(latest_file, as_attachment=True, download_name=filename)

    except Exception as e:
        print(e)
        return f"Gagal download: {e}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
