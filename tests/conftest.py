import os
import shutil
import tempfile

import pytest

from chess_server import create_app
from chess_server.db import init_db


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    img_dir = tempfile.mkdtemp()

    # create the app with common test config
    app = create_app(
        {"TESTING": True, "DATABASE": db_path, "IMG_DIR": img_dir}
    )

    # create the database and load test data
    with app.app_context():
        init_db()

    yield app

    # close and remove the temporary db/dir
    os.close(db_fd)
    os.unlink(db_path)
    shutil.rmtree(img_dir)


@pytest.fixture
def client(app):
    """A test client for the app."""
    with app.app_context():
        return app.test_client()


@pytest.fixture
def context(app):
    """A fixture which provides the patched test with application context."""
    with app.app_context():
        yield
