from flask import Flask, request, send_file, render_template
import os
import subprocess

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
        return "URL tidak ditemukan!", 400

    try:
        output_template = os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s')

        # Gunakan python -m yt_dlp agar path executable pasti ada
        proc = subprocess.run([
            'python', '-m', 'yt_dlp',
            '-o', output_template,
            url
        ], capture_output=True, text=True)

        if proc.returncode != 0:
            print(proc.stderr)
            return f"Gagal download: {proc.stderr}", 500

        files = [os.path.join(DOWNLOAD_FOLDER, f) for f in os.listdir(DOWNLOAD_FOLDER)]
        if not files:
            return "File tidak ditemukan setelah download.", 500

        latest_file = max(files, key=os.path.getctime)
        filename = sanitize_filename(os.path.basename(latest_file))

        return send_file(latest_file, as_attachment=True, download_name=filename)

    except Exception as e:
        print(e)
        return f"Gagal download: {e}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
