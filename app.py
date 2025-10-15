from flask import Flask, request, render_template, send_from_directory, jsonify
from flask_cors import CORS
import subprocess, os, threading

# === Inisialisasi ===
app = Flask(__name__, template_folder='.', static_folder='static')
CORS(app)

DOWNLOAD_FOLDER = os.path.join('static', 'downloads')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

download_status = {}  # status per URL

# === Fungsi download video ===
def download_video(url, format_opt):
    global download_status
    download_status[url] = {'status': 'downloading', 'filename': None}

    try:
        output_path = os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s')
        cmd = ['yt-dlp', '-f', format_opt, '-o', output_path, url]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        last_filename = None
        for line in proc.stdout:
            if 'Destination:' in line:
                last_filename = line.split('Destination:')[-1].strip()

        proc.wait()
        if proc.returncode == 0 and last_filename and os.path.exists(last_filename):
            download_status[url]['status'] = 'done'
            download_status[url]['filename'] = os.path.basename(last_filename)
        else:
            download_status[url]['status'] = 'error'
    except Exception as e:
        download_status[url] = {'status': f'error: {e}', 'filename': None}


# === Route utama ===
@app.route('/')
def index():
    return render_template('index.html')


# === Jalankan download ===
@app.route('/download', methods=['POST'])
def start_download():
    url = request.form.get('url')
    fmt = request.form.get('format', 'best')
    if url:
        threading.Thread(target=download_video, args=(url, fmt), daemon=True).start()
        return jsonify({'status': 'started'}), 200
    return jsonify({'status': 'error', 'message': 'URL tidak ada'}), 400


# === Ambil file jika sudah selesai ===
@app.route('/getfile')
def get_file():
    url = request.args.get('url')
    info = download_status.get(url)
    if info and info.get('status') == 'done' and info.get('filename'):
        file_path = os.path.join(DOWNLOAD_FOLDER, info['filename'])
        if os.path.exists(file_path):
            return jsonify({'status': 'ready', 'url': f'/static/downloads/{info["filename"]}'}), 200
    return jsonify({'error': 'file not ready'}), 404


# === Reset download ===
@app.route('/reset', methods=['POST'])
def reset_download():
    url = request.form.get('url')
    if url in download_status:
        download_status.pop(url)
    return jsonify({'status': 'reset'}), 200


# === Akses file download secara publik ===
@app.route('/static/downloads/<path:filename>')
def serve_download(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
