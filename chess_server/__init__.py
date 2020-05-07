import os

from flask import Flask

from chess_server import db

__version__ = "0.1.1"


def create_app(env="dev"):
    app = Flask(__name__)

    if env == "prod":
        app.config.from_object("config.ProdConfig")
    else:
        app.config.from_object("config.DevConfig")

    if not os.path.exists(app.config["IMG_DIR"]):
        os.mkdir(app.config["IMG_DIR"])

    db.init_app(app)

    with app.app_context():
        from chess_server import routes

        app.register_blueprint(routes.webhook_bp)

    return app
