from os import environ

from chess_server import create_app

ENV = environ.get("ENV", "dev")

# Run with `gunicorn wsgi:app`
app = create_app(env=ENV)
