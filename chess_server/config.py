import os
import tempfile

from chess_server.db import init_app


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(16))
    DATABASE = os.environ.get(
        "DATABASE", tempfile.mkstemp()[1]
    )  # Only the second value in the returned tuple
    IMG_DIR = os.environ.get("IMG_DIR", tempfile.mkdtemp())
    ENGINE_PATH = os.environ.get("ENGINE_PATH", "stockfish")
