from flask import Flask, render_template, request, send_file
from download_video import download_video
import os

app = Flask(__name__)

# Folder download
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def home():
    message = ""
    file_path = None
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            hasil = download_video(url)
            if os.path.isfile(hasil):
                file_path = hasil
            else:
                message = hasil
    return render_template('index.html', message=message, file_path=file_path)

@app.route('/download/<filename>')
def download_file(filename):
    path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "File tidak ditemukan", 404

if __name__ == '__main__':
    app.run(debug=True)