import os

from flask import Flask

from chess_server import db

__version__ = "0.1.0"


def create_app(test_config=None, prod=False):
    """Initialize the Flask app"""
    app = Flask(__name__, instance_relative_config=True)
    if prod:
        app.config.from_object("config.ProdConfig")
    else:
        app.config.from_object("config.DevConfig")

    # Update config if test_config is provided
    app.config.update(test_config or {})

    # Initialize db
    db.init_app(app)

    with app.app_context():
        # Include routes
        from chess_server import routes

        return app
