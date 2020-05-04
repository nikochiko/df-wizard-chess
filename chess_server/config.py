import os

from flask import current_app

from chess_server.db import init_app


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(16)
    DATABASE = os.environ.get("DATABASE") or os.path.join(
        current_app.instance_path, "df-fulfillment.db"
    )
    IMG_DIR = os.environ.get("IMG_DIR") or os.path.join(
        current_app.instace_path, "img_dir"
    )
    ENGINE_PATH = os.environ.get("ENGINE_PATH") or "stockfish"


def configure_app(app):
    app.config.from_object(Config)
    init_app(app)
