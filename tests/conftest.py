import os
import shutil
import tempfile

import pytest

from chess_server import create_app
from chess_server.db import init_db


@pytest.fixture
def app():
    app = create_app()
    return app


@pytest.fixture
def client(app):
    db_fd, app.config["DATABASE"] = tempfile.mkstemp()
    app.config["IMG_DIR"] = tempfile.mkdtemp()
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            init_db()

        yield client

    os.close(db_fd)
    os.unlink(app.config["DATABASE"])
    shutil.rmtree(app.config["IMG_DIR"])


@pytest.fixture
def context(app):
    db_fd, app.config["DATABASE"] = tempfile.mkstemp()
    app.config["IMG_DIR"] = tempfile.mkdtemp()
    app.config["TESTING"] = True

    with app.test_request_context():
        init_db()

        yield

    os.close(db_fd)
    os.unlink(app.config["DATABASE"])
    shutil.rmtree(app.config["IMG_DIR"])
