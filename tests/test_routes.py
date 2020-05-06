import os

import pytest
from flask import url_for

from tests.utils import get_dummy_webhook_request_for_google, get_random_session_id


class TestWebhookForGoogle:
    def setup_method(self):
        self.result = {"spam": "eggs"}

    def test_webhook_welcome(self, client, mocker):
        mock_welcome = mocker.patch(
            "chess_server.routes.welcome", return_value=self.result
        )

        req_data = get_dummy_webhook_request_for_google(action="welcome")

        resp = client.post("/webhook", json=req_data)

        assert resp.get_json() == self.result
        mock_welcome.assert_called_with(req_data)

    def test_webhook_choose_color(self, client, mocker):
        mock_choose_color = mocker.patch(
            "chess_server.routes.choose_color", return_value=self.result
        )

        req_data = get_dummy_webhook_request_for_google(action="choose_color")

        resp = client.post("/webhook", json=req_data)

        assert resp.get_json() == self.result
        mock_choose_color.assert_called_with(req_data)

    def test_webhook_two_squares(self, client, mocker):
        mock_two_squares = mocker.patch(
            "chess_server.routes.two_squares", return_value=self.result
        )

        req_data = get_dummy_webhook_request_for_google(action="two_squares")

        resp = client.post("/webhook", json=req_data)

        assert resp.get_json() == self.result
        mock_two_squares.assert_called_with(req_data)

    def test_webhook_castle(self, client, mocker):
        mock_castle = mocker.patch(
            "chess_server.routes.castle", return_value=self.result
        )

        req_data = get_dummy_webhook_request_for_google(action="castle")

        resp = client.post("/webhook", json=req_data)

        assert resp.get_json() == self.result
        mock_castle.assert_called_with(req_data)

    def test_webhook_resign(self, client, mocker):
        mock_resign = mocker.patch(
            "chess_server.routes.resign", return_value=self.result
        )

        req_data = get_dummy_webhook_request_for_google(action="resign")

        resp = client.post("/webhook", json=req_data)

        assert resp.get_json() == self.result
        mock_resign.assert_called_with(req_data)

    def test_webhook_unknown_intent(self, client, mocker):
        req_data = get_dummy_webhook_request_for_google(action="unknown")

        resp = client.post("/webhook", json=req_data)

        assert resp.status_code == 400
        assert "Unknown intent action: unknown" in str(resp.get_data())


@pytest.mark.usefixtures('client_class')
class TestPNGImage:
    def setup_method(self):
        self.session_id = get_random_session_id()
        self.file_content = b'file content'

    def test_png_image_success(self, client, config, mocker):
        url = url_for('webhook_bp.png_image', session_id=self.session_id)

        imgpath = os.path.join(config["IMG_DIR"], f"{self.session_id}.png")

        with open(imgpath, 'wb') as fw:
            fw.write(self.file_content)

        r = client.get(url)

        assert r.get_data() == self.file_content

    def test_png_image_file_not_found(self, client, config, mocker):
        url = url_for('webhook_bp.png_image', session_id=self.session_id)

        imgpath = os.path.join(config["IMG_DIR"], f"{self.session_id}.png")

        r = client.get(url)

        assert r.status_code == 404
