from flask import Blueprint, request, jsonify, send_file, send_from_directory
import threading
import os
import shutil
from pathlib import Path
from .yt_utils import is_valid_youtube_url, download_videos_background
from .progress import get_progress, clear_progress
from backend.config import Config

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    static_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "static")
    )
    return send_from_directory(static_dir, "index.html")


@bp.route("/video-info", methods=["POST"])
def get_video_info():
    import yt_dlp

    data = request.json
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    if not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid YouTube URL"}), 400
    try:
        ydl_opts = {"quiet": True, "no_warnings": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            duration = info.get("duration", 0)
            if duration:
                minutes = duration // 60
                seconds = duration % 60
                duration_str = f"{minutes}:{seconds:02d}"
            else:
                duration_str = "Unknown"
            video_info = {
                "title": info.get("title", "Unknown Title"),
                "duration": duration_str,
                "thumbnail": info.get("thumbnail", ""),
                "uploader": info.get("uploader", "Unknown"),
                "view_count": info.get("view_count", 0),
                "resolution": f"{info.get('height', 'Unknown')}p",
                "fps": info.get("fps", "Unknown"),
                "filesize_approx": info.get("filesize_approx", 0),
                "description": (
                    info.get("description", "")[:200] + "..."
                    if info.get("description")
                    else ""
                ),
            }
            return jsonify(video_info)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@bp.route("/download", methods=["POST"])
def download_video():
    data = request.json
    urls = data.get("urls", [])
    quality = data.get("quality", "best")
    if not urls:
        return jsonify({"error": "No URLs provided"}), 400
    import uuid

    download_id = str(uuid.uuid4())
    thread = threading.Thread(
        target=download_videos_background, args=(urls, quality, download_id)
    )
    thread.start()
    return jsonify({"download_id": download_id, "message": "Download started"})


@bp.route("/progress/<download_id>")
def progress(download_id):
    return jsonify(get_progress(download_id))


@bp.route("/download-file/<download_id>")
def download_file(download_id):
    session_folder = os.path.join(Config.TEMP_FOLDER, download_id)
    if not os.path.exists(session_folder):
        return jsonify({"error": "Download not found"}), 404
    
    files = list(Path(session_folder).glob("*.mp4"))
    if not files:
        return jsonify({"error": "No files found"}), 404
    
    # Single file - return direct download with proper headers
    if len(files) == 1:
        file_path = files[0]
        filename = file_path.name
        
        # Set headers to trigger browser download
        response = send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='video/mp4'
        )
        
        # Add headers to ensure browser triggers download dialog
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.headers['Content-Type'] = 'video/mp4'
        
        return response
    else:
        # Multiple files - create and return zip
        zip_path = os.path.join(Config.TEMP_FOLDER, f"{download_id}.zip")
        shutil.make_archive(zip_path[:-4], "zip", session_folder)
        
        response = send_file(
            zip_path,
            as_attachment=True,
            download_name="youtube_videos.zip",
            mimetype='application/zip'
        )
        
        response.headers['Content-Disposition'] = 'attachment; filename="youtube_videos.zip"'
        response.headers['Content-Type'] = 'application/zip'
        
        return response


@bp.route("/cleanup/<download_id>", methods=["POST"])
def cleanup(download_id):
    session_folder = os.path.join(Config.TEMP_FOLDER, download_id)
    zip_path = os.path.join(Config.TEMP_FOLDER, f"{download_id}.zip")
    try:
        if os.path.exists(session_folder):
            shutil.rmtree(session_folder)
        if os.path.exists(zip_path):
            os.remove(zip_path)
        clear_progress(download_id)
        return jsonify({"message": "Cleanup successful"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
