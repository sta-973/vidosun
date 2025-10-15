from flask import Flask, request, render_template, send_from_directory, jsonify
import subprocess, os, threading

# === Inisialisasi ===
app = Flask(__name__, template_folder='.', static_folder='static')

DOWNLOAD_FOLDER = os.path.join('static', 'downloads')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

download_status = {}  # status per URL

# === Fungsi download video ===
def download_video(url, format_opt):
    global download_status
    download_status[url] = {'status': 'downloading', 'filename': None}
    try:
        cmd = [
            'yt-dlp',
            '-f', format_opt,
            '-o', os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            url
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        last_filename = None
        for line in proc.stdout:
            if 'Destination:' in line:
                last_filename = line.split('Destination:')[-1].strip()

        proc.wait()
        if proc.returncode == 0 and last_filename:
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

# === Ambil file terakhir ===
@app.route('/getfile')
def get_file():
    url = request.args.get('url')
    info = download_status.get(url)
    if info and info.get('filename'):
        filename = info['filename']
        file_path = os.path.join(DOWNLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)
    return jsonify({'error': 'file not ready'}), 404

# === Akses file download secara publik ===
@app.route('/static/downloads/<path:filename>')
def serve_download(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
