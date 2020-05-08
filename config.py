from os import environ, path, urandom
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))


class Config:
    """Base config"""

    FLASK_APP = "wsgi.py"
    SECRET_KEY = environ.get("SECRET_KEY", urandom(16))

    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(Config):
    DEBUG = True
    TESTING = True

    POSTGRES_NAME = environ.get("POSTGRES_NAME", "wizardchess")  # DB Name
    POSTGRES_USER = environ.get("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = environ.get("POSTGRES_PASSWORD", "postgres")
    POSTGRES_HOST = environ.get("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = environ.get("POSTGRES_PORT", "5432")

    SQLALCHEMY_DATABASE_URI = environ.get(
        "DATABASE_URL",
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}"
        f":{POSTGRES_PORT}/{POSTGRES_NAME}",
    )

    IMG_DIR = path.join(basedir, "dev-imgdir")

    ENGINE_PATH = "test-engine"


class ProdConfig(Config):
    DEBUG = False
    TESTING = False
    SERVER_NAME = environ.get("SERVER_NAME")

    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL")

    IMG_DIR = path.join(basedir, environ.get("IMG_DIR", "imgdir"))
    ENGINE_PATH = environ.get("ENGINE_PATH")


class TestConfig(Config):
    DEBUG = False
    TESTING = True

    POSTGRES_NAME = environ.get("POSTGRES_NAME", "wizardchess")  # DB Name
    POSTGRES_USER = environ.get("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = environ.get("POSTGRES_PASSWORD", "postgres")
    POSTGRES_HOST = environ.get("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = environ.get("POSTGRES_PORT", 5432)

    SQLALCHEMY_DATABASE_URI = environ.get(
        "DATABASE_URL",
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}"
        f":{POSTGRES_PORT}/{POSTGRES_NAME}",
    )

    ENGINE_PATH = environ.get("ENGINE_PATH", "stockfish")
