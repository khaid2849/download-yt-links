from flask import Flask, render_template, request, jsonify, send_file, session
from flask_cors import CORS
import yt_dlp
import os
import json
import threading
import time
import uuid
from pathlib import Path
from urllib.parse import urlparse
import shutil

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production
CORS(app)

# Configuration
UPLOAD_FOLDER = 'downloads'
TEMP_FOLDER = 'temp'
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
Path(TEMP_FOLDER).mkdir(exist_ok=True)

# Store download progress
download_progress = {}

def is_valid_youtube_url(url):
    """Check if the URL is a valid YouTube URL."""
    parsed = urlparse(url)
    return parsed.netloc in ['www.youtube.com', 'youtube.com', 'youtu.be', 'm.youtube.com']

def progress_hook(d, download_id):
    """Hook to track download progress"""
    if d['status'] == 'downloading':
        progress = {
            'status': 'downloading',
            'downloaded': d.get('downloaded_bytes', 0),
            'total': d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0),
            'speed': d.get('speed', 0),
            'eta': d.get('eta', 0),
            'filename': d.get('filename', 'Unknown'),
            'percent': d.get('_percent_str', '0%').strip()
        }
        download_progress[download_id] = progress
    elif d['status'] == 'finished':
        download_progress[download_id] = {
            'status': 'finished',
            'filename': d.get('filename', 'Unknown'),
            'percent': '100%'
        }

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/video-info', methods=['POST'])
def get_video_info():
    """Get video information without downloading"""
    data = request.json
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    if not is_valid_youtube_url(url):
        return jsonify({'error': 'Invalid YouTube URL'}), 400
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Format duration
            duration = info.get('duration', 0)
            if duration:
                minutes = duration // 60
                seconds = duration % 60
                duration_str = f"{minutes}:{seconds:02d}"
            else:
                duration_str = "Unknown"
            
            video_info = {
                'title': info.get('title', 'Unknown Title'),
                'duration': duration_str,
                'thumbnail': info.get('thumbnail', ''),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'resolution': f"{info.get('height', 'Unknown')}p",
                'fps': info.get('fps', 'Unknown'),
                'filesize_approx': info.get('filesize_approx', 0),
                'description': info.get('description', '')[:200] + '...' if info.get('description') else ''
            }
            
            return jsonify(video_info)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/download', methods=['POST'])
def download_video():
    """Start video download"""
    data = request.json
    urls = data.get('urls', [])
    quality = data.get('quality', 'best')
    
    if not urls:
        return jsonify({'error': 'No URLs provided'}), 400
    
    # Generate unique download ID
    download_id = str(uuid.uuid4())
    
    # Start download in background thread
    thread = threading.Thread(target=download_videos_background, args=(urls, quality, download_id))
    thread.start()
    
    return jsonify({'download_id': download_id, 'message': 'Download started'})

def download_videos_background(urls, quality, download_id):
    """Download videos in background"""
    # Create a unique folder for this download session
    session_folder = os.path.join(TEMP_FOLDER, download_id)
    Path(session_folder).mkdir(exist_ok=True)
    
    # Configure quality settings
    if quality == 'best':
        format_str = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    elif quality == 'high':
        format_str = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best'
    elif quality == 'medium':
        format_str = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best'
    else:  # low
        format_str = 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best'
    
    ydl_opts = {
        'outtmpl': os.path.join(session_folder, '%(title)s.%(ext)s'),
        'format': format_str,
        'noplaylist': True,
        'ignoreerrors': True,
        'merge_output_format': 'mp4',
        'progress_hooks': [lambda d: progress_hook(d, download_id)],
        'quiet': True,
        'no_warnings': True,
    }
    
    download_progress[download_id] = {
        'status': 'starting',
        'total_videos': len(urls),
        'current_video': 0,
        'successful': 0,
        'failed': 0,
        'files': []
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for i, url in enumerate(urls):
            url = url.strip()
            if not url or not is_valid_youtube_url(url):
                download_progress[download_id]['failed'] += 1
                continue
            
            download_progress[download_id]['current_video'] = i + 1
            
            try:
                # Download the video
                ydl.download([url])
                download_progress[download_id]['successful'] += 1
                
                # Find the downloaded file
                files = list(Path(session_folder).glob('*.mp4'))
                if files:
                    latest_file = max(files, key=os.path.getctime)
                    download_progress[download_id]['files'].append(latest_file.name)
                    
            except Exception as e:
                download_progress[download_id]['failed'] += 1
                print(f"Error downloading {url}: {str(e)}")
    
    download_progress[download_id]['status'] = 'completed'

@app.route('/progress/<download_id>')
def get_progress(download_id):
    """Get download progress"""
    progress = download_progress.get(download_id, {'status': 'not_found'})
    return jsonify(progress)

@app.route('/download-file/<download_id>')
def download_file(download_id):
    """Download the completed video files"""
    session_folder = os.path.join(TEMP_FOLDER, download_id)
    
    if not os.path.exists(session_folder):
        return jsonify({'error': 'Download not found'}), 404
    
    files = list(Path(session_folder).glob('*.mp4'))
    
    if not files:
        return jsonify({'error': 'No files found'}), 404
    
    if len(files) == 1:
        # Single file, download directly
        return send_file(files[0], as_attachment=True)
    else:
        # Multiple files, create zip
        zip_path = os.path.join(TEMP_FOLDER, f'{download_id}.zip')
        shutil.make_archive(zip_path[:-4], 'zip', session_folder)
        return send_file(zip_path, as_attachment=True, download_name='youtube_videos.zip')

@app.route('/cleanup/<download_id>', methods=['POST'])
def cleanup(download_id):
    """Clean up temporary files"""
    session_folder = os.path.join(TEMP_FOLDER, download_id)
    zip_path = os.path.join(TEMP_FOLDER, f'{download_id}.zip')
    
    try:
        if os.path.exists(session_folder):
            shutil.rmtree(session_folder)
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if download_id in download_progress:
            del download_progress[download_id]
        return jsonify({'message': 'Cleanup successful'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)