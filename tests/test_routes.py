from tests.utils import get_dummy_webhook_request_for_google


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
