import os
import yt_dlp

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def probe_video(url):
    """
    Mengembalikan status video dan metadata tanpa download.
    status: public | private | needs_cookies | age_restricted | region_restricted | not_found | error
    """
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'forcejson': True,
        'nocheckcertificate': True,
        'noplaylist': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info is None:
                return {'status':'not_found','title':None,'thumbnail':None,'reason':'Tidak ada info.'}

            # cek age_limit
            if info.get('age_limit',0) >= 18:
                return {'status':'age_restricted','title':info.get('title'),'thumbnail':info.get('thumbnail'),'reason':'Perlu verifikasi umur.'}

            return {'status':'public','title':info.get('title'),'thumbnail':info.get('thumbnail'),'reason':None}

    except yt_dlp.utils.DownloadError as e:
        msg = str(e)
        if 'Sign in to confirm' in msg or 'cookies' in msg.lower() or 'login' in msg.lower():
            return {'status':'needs_cookies','title':None,'thumbnail':None,'reason':'Perlu login / cookies untuk mengakses video ini.'}
        if 'private' in msg.lower():
            return {'status':'private','title':None,'thumbnail':None,'reason':'Video bersifat privat.'}
        if 'not available' in msg.lower() or '404' in msg:
            return {'status':'not_found','title':None,'thumbnail':None,'reason':msg}
        return {'status':'error','title':None,'thumbnail':None,'reason':msg}
    except Exception as e:
        return {'status':'error','title':None,'thumbnail':None,'reason':str(e)}


def download_video_public(url):
    """Download video publik tanpa cookies"""
    try:
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'format': 'best',
            'noplaylist': True,
            'quiet': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        return {'error': f"Gagal mengunduh: {e}"}
