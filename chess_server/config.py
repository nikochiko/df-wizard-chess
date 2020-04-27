import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ENGINE_PATH = os.environ.get('ENGINE_PATH') or 'stockfish'

class Config(object):
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False