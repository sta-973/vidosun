from flask import Flask, request, render_template, send_from_directory, jsonify
from flask_cors import CORS
import subprocess, os, threading

# --- arahkan template ke root folder ---
app = Flask(__name__, template_folder='.')
CORS(app)

DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

download_status = {}

def download_video(url, format_opt):
    """Menjalankan yt-dlp dan memantau progres unduhan"""
    global download_status
    download_status[url] = {'status': 'downloading', 'progress': 0}
    try:
        cmd = [
            'yt-dlp',
            '-f', format_opt,
            '-o', os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            url
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            if '[download]' in line and '%' in line:
                try:
                    perc = float(line.split('%')[0].split()[-1])
                    download_status[url]['progress'] = int(perc)
                except:
                    pass
        proc.wait()
        download_status[url]['status'] = 'done' if proc.returncode == 0 else 'error'
    except Exception as e:
        download_status[url] = {'status': f'error: {e}', 'progress': 0}

@app.route('/')
def index():
    # render index.html dari root folder
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def start_download():
    url = request.form.get('url')
    fmt = request.form.get('format', 'best')
    if url:
        threading.Thread(target=download_video, args=(url, fmt), daemon=True).start()
        return jsonify({'status': 'started'}), 200
    return jsonify({'status': 'error', 'message': 'URL tidak ada'}), 400

@app.route('/progress')
def progress():
    url = request.args.get('url')
    if url in download_status:
        return jsonify(download_status[url]), 200
    return jsonify({'status': 'not_started', 'progress': 0}), 200

@app.route('/getfile')
def get_file():
    files = os.listdir(DOWNLOAD_FOLDER)
    if files:
        files.sort(key=lambda x: os.path.getmtime(os.path.join(DOWNLOAD_FOLDER, x)), reverse=True)
        filename = files[0]
        return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)
    return 'File belum tersedia', 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
