import os
import shutil
import tempfile

import pytest
from chess_server import main
from chess_server.db import init_db


@pytest.fixture
def client():
    db_fd, main.app.config["DATABASE"] = tempfile.mkstemp()
    main.app.config["IMG_DIR"] = tempfile.mkdtemp()
    main.app.config["TESTING"] = True

    with main.app.test_client() as client:
        with main.app.app_context():
            init_db()

        yield client

    os.close(db_fd)
    os.unlink(main.app.config["DATABASE"])
    shutil.rmtree(main.app.config["IMG_DIR"])


@pytest.fixture
def context():
    db_fd, main.app.config["DATABASE"] = tempfile.mkstemp()
    main.app.config["IMG_DIR"] = tempfile.mkdtemp()
    main.app.config["TESTING"] = True

    with main.app.test_request_context():
        init_db()

        yield

    os.close(db_fd)
    os.unlink(main.app.config["DATABASE"])
    shutil.rmtree(main.app.config["IMG_DIR"])
