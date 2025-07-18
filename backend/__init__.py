from flask import Flask
from backend.config import Config
from backend.routes import bp
import os


def create_app():
    app = Flask(
        __name__,
        static_folder=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "static")
        ),
        static_url_path="",  # <-- This is the key!
    )
    app.config.from_object(Config)
    app.register_blueprint(bp)
    return app
