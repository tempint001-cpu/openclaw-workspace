#!/usr/bin/env python3
"""Direct YouTube downloader that Nexa can call."""
import os
import sys
import yt_dlp
import json

def download(url: str, user_id: int = 7924461837) -> dict:
    DOWNLOAD_DIR = "/root/Downloads"
    user_dir = os.path.join(DOWNLOAD_DIR, f"user_{user_id}")
    os.makedirs(user_dir, exist_ok=True)
    
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': os.path.join(user_dir, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)
            return {
                'success': True,
                'filepath': filepath,
                'title': info.get('title', 'Unknown'),
                'file_size': os.path.getsize(filepath)
            }
    except Exception as e:
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else None
    if url:
        result = download(url)
        print(json.dumps(result))
    else:
        print(json.dumps({'success': False, 'error': 'No URL provided'}))
