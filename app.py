from flask import Flask, request, send_file, render_template, jsonify
import os
import subprocess
import glob

app = Flask(__name__, template_folder='.', static_folder='static')

DOWNLOAD_FOLDER = os.path.join('static', 'downloads')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def sanitize_filename(name):
    return "".join(c for c in name if c.isalnum() or c in " ._-").strip()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url:
        return jsonify({"status":"error","message":"URL tidak ditemukan"}), 400

    try:
        output_template = os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s')

        # Header untuk menghindari 429
        headers = [
            'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept-Language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7'
        ]
        header_args = []
        for h in headers:
            header_args += ['--add-header', h]

        # Gunakan cookies (optional) untuk video terbatas
        cookies_path = os.path.join('cookies.txt')
        cookie_args = ['--cookies', cookies_path] if os.path.exists(cookies_path) else []

        proc = subprocess.run([
            'yt-dlp',
            *header_args,
            *cookie_args,
            '-o', output_template,
            url
        ], capture_output=True, text=True)

        if proc.returncode != 0:
            print(proc.stderr)
            return jsonify({"status":"error","message":"Gagal download"}), 500

        files = glob.glob(os.path.join(DOWNLOAD_FOLDER, '*'))
        latest_file = max(files, key=os.path.getctime)
        filename = sanitize_filename(os.path.basename(latest_file))

        return send_file(latest_file, as_attachment=True, download_name=filename)

    except Exception as e:
        print(e)
        return jsonify({"status":"error","message":str(e)}), 500

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
