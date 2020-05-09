import os

import chess
import chess.svg
import pytest
from chess_server.utils import (get_params_by_req, get_response_for_google,
                                get_response_template_for_google,
                                get_session_by_req, save_board_as_png)
from flask import current_app
from tests import data
from tests.utils import get_random_session_id


def test_get_session_by_req():

    result = get_session_by_req(data.sample_request)
    assert result == data.sample_request_sessionid


def test_get_params_by_req():

    result = get_params_by_req(data.sample_request)
    assert result == data.sample_request_params


def test_get_response_for_google():

    result = get_response_for_google(
        textToSpeech=data.sample_textToSpeech, options=data.sample_options,
    )
    assert result == data.sample_response_for_google_assistant


def test_get_response_template_for_google():

    result = get_response_template_for_google()
    assert result == data.sample_google_response_template


def test_get_response_template_for_google_with_options():

    result = get_response_template_for_google(options=True)
    assert result == data.sample_google_response_template_with_options


class TestRenderPNG:
    def setup_method(self):
        self.session_id = get_random_session_id()

    def test_save_board_as_png_success(self, mocker, context):
        mock_svg2png = mocker.patch("chess_server.utils.svg2png")

        expected_pngfile = os.path.join(
            current_app.config["IMG_DIR"], f"{self.session_id}.png"
        )

        # With an empty board (lastmove=None)
        board = chess.Board()
        svg = str(chess.svg.board(board))

        value = save_board_as_png(self.session_id, board)

        assert value == expected_pngfile
        mock_svg2png.assert_called_with(bytestring=str(svg), write_to=expected_pngfile)

    def test_save_board_as_png_success_lastmove(self, mocker, context):
        mock_svg2png = mocker.patch("chess_server.utils.svg2png")

        expected_pngfile = os.path.join(
            current_app.config["IMG_DIR"], f"{self.session_id}.png"
        )

        # With a move played (lastmove must be highlighted on board)
        board = chess.Board()
        board.push_san("e4")
        lastmove = chess.Move.from_uci("e2e4")
        svg = str(chess.svg.board(board, lastmove=lastmove))

        value = save_board_as_png(self.session_id, board)

        assert value == expected_pngfile
        mock_svg2png.assert_called_with(bytestring=str(svg), write_to=expected_pngfile)

    def test_save_board_as_png_error(self, mocker, context):
        mock_logger = mocker.patch("chess_server.utils.logger.error")
        mock_svg2png = mocker.patch(
            "chess_server.utils.svg2png", side_effect=Exception("Example error")
        )

        board = chess.Board()
        svg = str(chess.svg.board(board))

        with pytest.raises(Exception, match="Example error"):
            value = save_board_as_png(self.session_id, board)

        mock_svg2png.assert_called()
        mock_logger.assert_called_with(
            f"Unable to process image. Failed with error:\nExample error"
        )
