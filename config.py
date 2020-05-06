from os import environ, path, urandom
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))


class Config:
    """Base config"""

    FLASK_APP = "wsgi.py"
    SECRET_KEY = environ.get("SECRET_KEY", urandom(16))


class DevConfig(Config):
    DEBUG = True
    TESTING = True
    # SERVER_NAME = "https://testserver/"

    IMG_DIR = path.join(basedir, "dev-imgdir")
    DATABASE = path.join(basedir, "dev-db.db")

    ENGINE_PATH = "test-engine"


class ProdConfig(Config):
    DEBUG = False
    TESTING = False
    # SERVER_NAME = environ.get("SERVER_NAME")

    IMG_DIR = path.join(basedir, environ.get("IMG_DIR", "img"))
    DATABASE = path.join(basedir, environ.get("DATABASE", "prod.db"))

    ENGINE_PATH = environ.get("ENGINE_PATH")
