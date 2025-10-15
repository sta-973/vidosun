from flask import Flask, request, render_template, send_from_directory, jsonify
from flask_cors import CORS
import subprocess, os, threading, time

app = Flask(__name__, template_folder='.', static_folder='static')
CORS(app)

DOWNLOAD_FOLDER = os.path.join('static', 'downloads')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

download_status = {}  # status per URL

# === Fungsi download video ===
def download_video(url, format_opt):
    global download_status
    download_status[url] = {'status': 'downloading', 'progress': 0, 'filename': None, 'eta': 0}
    try:
        cmd = [
            'yt-dlp',
            '-f', format_opt,
            '-o', os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            url
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        start_time = time.time()
        last_filename = None
        for line in proc.stdout:
            # Tangkap progres
            if '[download]' in line and '%' in line:
                try:
                    perc = float(line.split('%')[0].split()[-1])
                    download_status[url]['progress'] = int(perc)
                    elapsed = time.time() - start_time
                    if perc > 0:
                        remaining = int(elapsed * (100/perc - 1))
                        download_status[url]['eta'] = remaining
                except:
                    pass
            # Tangkap nama file hasil
            if 'Destination:' in line:
                last_filename = line.strip().split('Destination:')[-1].strip()
                download_status[url]['filename'] = os.path.basename(last_filename)

        proc.wait()
        if proc.returncode == 0:
            download_status[url]['status'] = 'done'
        else:
            download_status[url]['status'] = 'error'
    except Exception as e:
        download_status[url] = {'status': f'error: {e}', 'progress': 0, 'filename': None, 'eta': 0}

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

# === Pantau progres ===
@app.route('/progress')
def progress():
    url = request.args.get('url')
    if url in download_status:
        info = download_status[url]
        return jsonify({
            'status': info.get('status'),
            'progress': info.get('progress',0),
            'eta': info.get('eta',0)
        })
    return jsonify({'status': 'not_started', 'progress': 0, 'eta':0}), 200

# === Ambil file terakhir ===
@app.route('/getfile')
def get_file():
    url = request.args.get('url')
    info = download_status.get(url)
    if info and info.get('filename'):
        filename = info['filename']
        file_path = os.path.join(DOWNLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            public_url = f"/static/downloads/{filename}"  # link publik
            return jsonify({'status': 'ready', 'url': public_url}), 200
    return jsonify({'error': 'file not ready'}), 404

# === Reset download ===
@app.route('/reset', methods=['POST'])
def reset_download():
    url = request.form.get('url')
    if url in download_status:
        filename = download_status[url].get('filename')
        if filename:
            file_path = os.path.join(DOWNLOAD_FOLDER, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        download_status.pop(url)
    return jsonify({'status': 'reset'}), 200

# === Akses file download secara publik ===
@app.route('/static/downloads/<path:filename>')
def serve_download(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
