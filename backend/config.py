import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-here")
    UPLOAD_FOLDER = "downloads"
    TEMP_FOLDER = "temp"
