from flask import Flask, request, send_file, render_template, jsonify
import os
import subprocess
import threading

app = Flask(__name__, template_folder='.', static_folder='static')

DOWNLOAD_FOLDER = os.path.join('static', 'downloads')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

download_status = {}

def sanitize_filename(name):
    return "".join(c for c in name if c.isalnum() or c in " ._-").strip()

def download_video(url):
    global download_status
    try:
        output_template = os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s')
        proc = subprocess.run([
            'yt-dlp',
            '-f', 'best',
            '-o', output_template,
            url
        ], capture_output=True, text=True)

        if proc.returncode != 0:
            download_status[url] = {'status': 'error', 'message': proc.stderr}
            return

        files = [os.path.join(DOWNLOAD_FOLDER, f) for f in os.listdir(DOWNLOAD_FOLDER)]
        latest_file = max(files, key=os.path.getctime)
        filename = sanitize_filename(os.path.basename(latest_file))
        download_status[url] = {'status': 'done', 'filename': filename}
    except Exception as e:
        download_status[url] = {'status': 'error', 'message': str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url:
        return "URL tidak ditemukan!", 400

    download_status[url] = {'status': 'downloading', 'filename': None}
    threading.Thread(target=download_video, args=(url,), daemon=True).start()
    return jsonify({'status': 'started'})

@app.route('/getfile')
def getfile():
    url = request.args.get('url')
    info = download_status.get(url)
    if info and info.get('status') == 'done':
        return jsonify({'status': 'ready', 'url': f'/static/downloads/{info["filename"]}'})
    elif info and info.get('status') == 'error':
        return jsonify({'status': 'error', 'message': info.get('message')}), 500
    return jsonify({'status': 'pending'}), 404

@app.route('/reset', methods=['POST'])
def reset():
    url = request.form.get('url')
    if url and url in download_status:
        del download_status[url]
    return jsonify({'status': 'reset'})

@app.route('/readme')
def readme():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
        return f"<pre style='white-space: pre-wrap; color: #fff; background: #111; padding:20px;'>{content}</pre>"
    except:
        return "README.md tidak ditemukan", 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
