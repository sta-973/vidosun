from flask import Flask, request, render_template, send_from_directory, jsonify
from flask_cors import CORS
import subprocess, os, threading, time, uuid

app = Flask(__name__, template_folder='.')
CORS(app)

DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

download_queue = {}  # simpan status download per id

def download_video(task_id, url, format_opt):
    """Jalankan yt-dlp di thread terpisah"""
    filename = os.path.join(DOWNLOAD_FOLDER, f"{task_id}.%(ext)s")
    cmd = ['yt-dlp', '-f', format_opt, '-o', filename, url]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            if '[download]' in line and '%' in line:
                try:
                    perc = float(line.split('%')[0].split()[-1])
                    download_queue[task_id]['progress'] = int(perc)
                except:
                    pass
        proc.wait()
        # cari nama file hasil download
        files = os.listdir(DOWNLOAD_FOLDER)
        for f in files:
            if task_id in f:
                download_queue[task_id]['file'] = f
        download_queue[task_id]['status'] = 'done' if proc.returncode == 0 else 'error'
    except Exception as e:
        download_queue[task_id]['status'] = f'error: {e}'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/download', methods=['POST'])
def start_download():
    url = request.form.get('url')
    fmt = request.form.get('format', 'best')
    if not url:
        return jsonify({'status': 'error', 'message': 'URL tidak ada'}), 400

    task_id = str(uuid.uuid4())[:8]  # id unik per unduhan
    download_queue[task_id] = {'status': 'downloading', 'progress': 0, 'file': None}

    threading.Thread(target=download_video, args=(task_id, url, fmt), daemon=True).start()
    return jsonify({'status': 'started', 'task_id': task_id})


@app.route('/progress')
def progress():
    task_id = request.args.get('task')
    if not task_id or task_id not in download_queue:
        return jsonify({'status': 'not_found', 'progress': 0}), 200
    return jsonify(download_queue[task_id])


@app.route('/getfile')
def get_file():
    task_id = request.args.get('task')
    if not task_id or task_id not in download_queue:
        return "Task tidak ditemukan", 404

    task = download_queue[task_id]
    if task['status'] != 'done' or not task['file']:
        return jsonify({'error': 'file belum siap'}), 202

    return send_from_directory(DOWNLOAD_FOLDER, task['file'], as_attachment=True)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
