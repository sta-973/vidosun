from flask import Flask, request, render_template, send_from_directory, jsonify, url_for
from flask_cors import CORS
import subprocess, os, threading, uuid

# === Inisialisasi ===
app = Flask(__name__, template_folder='.', static_folder='static')
CORS(app)

DOWNLOAD_FOLDER = os.path.join('static', 'downloads')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

download_status = {}  # status per task_id


# === Fungsi download video ===
def download_video(task_id, url, format_opt):
    download_status[task_id] = {'status': 'downloading', 'progress': 0, 'filename': None}
    try:
        cmd = [
            'yt-dlp',
            '-f', format_opt,
            '-o', os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            url
        ]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        last_filename = None
        for line in proc.stdout:
            line = line.strip()
            print(line)  # log ke console Render
            # Tangkap progres
            if '[download]' in line and '%' in line:
                try:
                    perc = float(line.split('%')[0].split()[-1])
                    download_status[task_id]['progress'] = int(perc)
                except:
                    pass
            # Tangkap nama file hasil
            if 'Destination:' in line:
                last_filename = line.split('Destination:')[-1].strip()

        proc.wait()
        if proc.returncode == 0:
            download_status[task_id]['status'] = 'done'
            download_status[task_id]['filename'] = os.path.basename(last_filename)
        else:
            download_status[task_id]['status'] = 'error'
    except Exception as e:
        download_status[task_id] = {'status': f'error: {e}', 'progress': 0, 'filename': None}


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
        task_id = str(uuid.uuid4())
        threading.Thread(target=download_video, args=(task_id, url, fmt), daemon=True).start()
        return jsonify({'status': 'started', 'task_id': task_id}), 200
    return jsonify({'status': 'error', 'message': 'URL tidak ada'}), 400


# === Pantau progres ===
@app.route('/progress')
def progress():
    task_id = request.args.get('task_id')
    if task_id in download_status:
        return jsonify(download_status[task_id]), 200
    return jsonify({'status': 'not_started', 'progress': 0}), 200


# === Ambil file terakhir ===
@app.route('/getfile')
def get_file():
    task_id = request.args.get('task_id')
    info = download_status.get(task_id)
    if info and info.get('filename'):
        filename = info['filename']
        file_path = os.path.join(DOWNLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            public_url = url_for('serve_download', filename=filename, _external=True)
            return jsonify({'status': 'ready', 'url': public_url}), 200
    return jsonify({'error': 'file not ready'}), 404


# === Akses file download secara publik ===
@app.route('/static/downloads/<path:filename>')
def serve_download(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
