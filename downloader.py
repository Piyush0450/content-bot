import yt_dlp
import os
import time

def download_video(url, output_dir="downloads"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Generate a unique filename to avoid collisions
    timestamp = int(time.time())
    output_template = os.path.join(output_dir, f'%(title)s_{timestamp}.%(ext)s')

    ydl_opts = {
        'outtmpl': output_template,
        'format': 'best', # Download best available single file
        'noplaylist': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading {url}...", flush=True)
            info = ydl.extract_info(url, download=True)
            
            # Check for entries (playlist/carousel)
            paths = []
            if 'entries' in info:
                entries = info['entries']
            else:
                entries = [info]

            for entry in entries:
                fname = ydl.prepare_filename(entry)
                # Check for extensions
                base, ext = os.path.splitext(fname)
                potential_exts = ['.mp4', '.mkv', '.webm', '.jpg', '.jpeg', '.png', '.webp']
                found = False
                for pe in potential_exts:
                    if os.path.exists(base + pe):
                        paths.append(os.path.abspath(base + pe))
                        found = True
                        break
                if not found and os.path.exists(fname):
                    paths.append(os.path.abspath(fname))
            
            return paths

    except Exception as e:
        print(f"Error downloading {url}: {e}", flush=True)
        return []
