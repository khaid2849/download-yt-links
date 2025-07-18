import yt_dlp
from urllib.parse import urlparse
from pathlib import Path
import os
import uuid
import shutil
from .progress import set_progress, get_progress
from backend.config import Config


def is_valid_youtube_url(url):
    parsed = urlparse(url)
    return parsed.netloc in [
        "www.youtube.com",
        "youtube.com",
        "youtu.be",
        "m.youtube.com",
    ]


def progress_hook(d, download_id):
    if d["status"] == "downloading":
        progress = {
            "status": "downloading",
            "downloaded": d.get("downloaded_bytes", 0),
            "total": d.get("total_bytes", 0) or d.get("total_bytes_estimate", 0),
            "speed": d.get("speed", 0),
            "eta": d.get("eta", 0),
            "filename": d.get("filename", "Unknown"),
            "percent": d.get("_percent_str", "0%").strip(),
        }
        set_progress(download_id, progress)
    elif d["status"] == "finished":
        set_progress(
            download_id,
            {
                "status": "finished",
                "filename": d.get("filename", "Unknown"),
                "percent": "100%",
            },
        )


def download_videos_background(urls, quality, download_id):
    session_folder = os.path.join(Config.TEMP_FOLDER, download_id)
    Path(session_folder).mkdir(exist_ok=True)
    if quality == "best":
        format_str = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
    elif quality == "high":
        format_str = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best"
    elif quality == "medium":
        format_str = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best"
    else:
        format_str = "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best"
    ydl_opts = {
        "outtmpl": os.path.join(session_folder, "%(title)s.%(ext)s"),
        "format": format_str,
        "noplaylist": True,
        "ignoreerrors": True,
        "merge_output_format": "mp4",
        "progress_hooks": [lambda d: progress_hook(d, download_id)],
        "quiet": True,
        "no_warnings": True,
    }
    set_progress(
        download_id,
        {
            "status": "starting",
            "total_videos": len(urls),
            "current_video": 0,
            "successful": 0,
            "failed": 0,
            "files": [],
        },
    )
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for i, url in enumerate(urls):
            url = url.strip()
            if not url or not is_valid_youtube_url(url):
                prog = get_progress(download_id)
                prog["failed"] += 1
                set_progress(download_id, prog)
                continue
            prog = get_progress(download_id)
            prog["current_video"] = i + 1
            set_progress(download_id, prog)
            try:
                ydl.download([url])
                prog = get_progress(download_id)
                prog["successful"] += 1
                files = list(Path(session_folder).glob("*.mp4"))
                if files:
                    latest_file = max(files, key=os.path.getctime)
                    prog["files"].append(latest_file.name)
                set_progress(download_id, prog)
            except Exception as e:
                prog = get_progress(download_id)
                prog["failed"] += 1
                set_progress(download_id, prog)
    prog = get_progress(download_id)
    prog["status"] = "completed"
    set_progress(download_id, prog)
