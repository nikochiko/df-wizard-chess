import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

__version__ = "0.2.0"

db = SQLAlchemy()


def create_app(env="dev", test_config=None):
    app = Flask(__name__)

    if env == "prod":  # pragma: no cover
        app.config.from_object("config.ProdConfig")
    elif env == "test":
        app.config.from_object("config.TestConfig")
        app.config.update(test_config or {})
    else:  # pragma: no cover
        app.config.from_object("config.DevConfig")

    if not os.path.exists(app.config["IMG_DIR"]):  # pragma: no cover
        os.mkdir(app.config["IMG_DIR"])

    db.init_app(app)

    with app.app_context():
        from chess_server import routes, models  # noqa: F401

        app.register_blueprint(routes.webhook_bp)

        # Initialize database
        db.create_all()

    return app
