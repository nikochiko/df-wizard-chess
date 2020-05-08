import shutil
import tempfile

import pytest

from chess_server import create_app
from chess_server import db


@pytest.fixture
def app():
    test_config = {"IMG_DIR": tempfile.mkdtemp()}
    app = create_app(env="test", test_config=test_config)
    return app


@pytest.fixture
def client(app):

    with app.test_client() as client:
        yield client

    db.session.close()
    # db.session.commit()
    db.drop_all()
    shutil.rmtree(app.config["IMG_DIR"])


@pytest.fixture
def context(app):

    with app.test_request_context():
        yield

    db.session.close()
    # db.session.commit()
    db.drop_all()
    shutil.rmtree(app.config["IMG_DIR"])
