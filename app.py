from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import subprocess
import os
import uuid

app = Flask(__name__)
CORS(app)

# Folder download (otomatis dibuat kalau belum ada)
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'success': False, 'error': 'URL kosong!'})

    try:
        # Nama file unik
        unique_name = str(uuid.uuid4()) + ".mp4"
        output_path = os.path.join(DOWNLOAD_FOLDER, unique_name)

        # Jalankan yt-dlp melalui python -m agar pasti terdeteksi
        cmd = [
            "python", "-m", "yt_dlp",
            "-f", "b",
            "-o", output_path,
            url
        ]
        subprocess.run(cmd, check=True)

        # Pastikan file berhasil diunduh
        if not os.path.exists(output_path):
            return jsonify({'success': False, 'error': 'File tidak ditemukan setelah unduh.'})

        # Kirim link unduhan (Render akan menyediakan URL publik)
        file_url = f"/getfile/{unique_name}"
        return jsonify({'success': True, 'url': file_url})

    except subprocess.CalledProcessError as e:
        return jsonify({'success': False, 'error': f'Gagal download: {e}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/getfile/<filename>')
def get_file(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return app.send_static_file(file_path)
    else:
        return "File tidak ditemukan", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))



