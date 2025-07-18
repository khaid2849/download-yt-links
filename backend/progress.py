# Download progress tracking

download_progress = {}


def set_progress(download_id, progress):
    download_progress[download_id] = progress


def get_progress(download_id):
    return download_progress.get(download_id, {"status": "not_found"})


def clear_progress(download_id):
    if download_id in download_progress:
        del download_progress[download_id]
