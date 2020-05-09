import os
import random
import tempfile
from unittest import mock
from unittest import TestCase

import chess
import pytest
from flask import current_app
from flask import url_for
from werkzeug.exceptions import NotFound

from chess_server import main
from chess_server.main import castle
from chess_server.main import choose_color
from chess_server.main import get_result_comment
from chess_server.main import resign
from chess_server.main import RESPONSES
from chess_server.main import show_board
from chess_server.main import start_game_and_get_response
from chess_server.main import two_squares
from chess_server.main import welcome
from chess_server.utils import User
from tests.utils import get_dummy_webhook_request_for_google
from tests.utils import get_random_session_id
from tests.utils import GoogleOptionsList


class TestGetResultComment(TestCase):
    def test_get_result_comment_game_is_not_over_as_white(self):

        user = User(board=chess.Board(), color=chess.WHITE)

        expected = None
        result = get_result_comment(user=user)

        self.assertEqual(result, expected)

    def test_get_result_comment_game_is_not_over_as_black(self):

        # Reference game: Morphy-Maurian, 1869

        user = User(
            board=chess.Board(
                "r1bq2k1/ppp2Bp1/2np1n1p/b3p3/3PP3/B1P5/P4PPP/RN1Q1RK1 b - - " "0 11"
            ),
            color=chess.BLACK,
        )

        expected = None
        result = get_result_comment(user=user)

        self.assertEqual(result, expected)

    def test_get_result_comment_user_wins_as_white(self):

        user = User(
            board=chess.Board("4N3/ppp3Qk/2p5/7p/3P3P/8/P4P2/5K2 b - - 0 36"),
            color=chess.WHITE,
        )

        expected = RESPONSES["result_win"]
        result = get_result_comment(user=user)

        self.assertEqual(result, expected)

    def test_get_result_comment_user_wins_as_black(self):

        user = User(
            board=chess.Board(
                "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"
            ),
            color=chess.BLACK,
        )

        expected = RESPONSES["result_win"]
        result = get_result_comment(user=user)

        self.assertEqual(result, expected)

    def test_get_result_comment_drawn_by_stalemate(self):

        expected = RESPONSES["result_draw"].format(reason="stalemate")

        # As white
        user = User(
            board=chess.Board("7K/7P/7k/8/6q1/8/8/8 w - - 0 1"), color=chess.WHITE,
        )
        result = get_result_comment(user=user)

        self.assertEqual(result, expected)

        # As black
        user = User(
            board=chess.Board("7K/7P/7k/8/6q1/8/8/8 w - - 0 1"), color=chess.BLACK,
        )
        result = get_result_comment(user=user)

        self.assertEqual(result, expected)

    def test_get_result_comment_drawn_by_insufficient_material(self):

        expected = RESPONSES["result_draw"].format(reason="insufficient material")

        # As white
        user = User(
            board=chess.Board("4k3/8/8/8/8/5B2/8/4K3 w - - 0 1"), color=chess.WHITE,
        )
        result = get_result_comment(user=user)

        self.assertEqual(result, expected)

        # As black
        user = User(
            board=chess.Board("4k3/8/8/8/8/5B2/8/4K3 w - - 0 1"), color=chess.BLACK,
        )
        result = get_result_comment(user=user)

        self.assertEqual(result, expected)

    def test_get_result_comment_drawn_by_fifty_move_rule(self):

        expected = RESPONSES["result_draw"].format(reason="fifty move rule")

        # As white
        user = User(
            board=chess.Board("4k3/8/6r1/8/8/8/2R5/4K3 w - - 120 1"), color=chess.WHITE,
        )
        result = get_result_comment(user=user)

        self.assertEqual(result, expected)

        # As black
        user = User(
            board=chess.Board("4k3/8/6r1/8/8/8/2R5/4K3 w - - 120 1"), color=chess.BLACK,
        )
        result = get_result_comment(user=user)

        self.assertEqual(result, expected)

    def test_get_result_comment_drawn_by_threefold_repetition(self):

        expected = RESPONSES["result_draw"].format(reason="threefold repetition")

        # As white
        board = chess.Board()
        user = User(board=board, color=chess.WHITE)

        self.assertEqual(get_result_comment(user=user), None)
        board.push_san("Nf3")
        board.push_san("Nf6")
        self.assertEqual(get_result_comment(user=user), None)
        board.push_san("Ng1")
        board.push_san("Ng8")
        self.assertEqual(get_result_comment(user=user), None)
        board.push_san("Nf3")
        board.push_san("Nf6")
        self.assertEqual(get_result_comment(user=user), None)
        board.push_san("Ng1")

        result = get_result_comment(user=user)

        self.assertEqual(result, expected)

        # As black
        board = chess.Board()
        user = User(board=board, color=chess.BLACK)

        board.push_san("Nf3")
        self.assertEqual(get_result_comment(user=user), None)
        board.push_san("Nf6")
        board.push_san("Ng1")
        self.assertEqual(get_result_comment(user=user), None)
        board.push_san("Ng8")
        board.push_san("Nf3")
        self.assertEqual(get_result_comment(user=user), None)
        board.push_san("Nf6")
        board.push_san("Ng1")

        result = get_result_comment(user=user)

        self.assertEqual(result, expected)


class TestStartGame:
    def setup_method(self):
        self.result = {"ham": "eggs"}
        self.engine_reply = "engine's move"

    def test_start_game_white(self, mocker):

        mock_create_user = mocker.patch("chess_server.main.create_user")
        mock_play_engine = mocker.patch(
            "chess_server.main.Mediator.play_engine_move_and_get_speech",
            return_value=self.engine_reply,
        )
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google", return_value=self.result,
        )

        session_id = get_random_session_id()
        color = "white"

        value = start_game_and_get_response(session_id, color)

        mock_create_user.assert_called_with(
            session_id, board=chess.Board(), color=chess.WHITE
        )
        mock_play_engine.assert_not_called()
        mock_get_response.assert_called_once()

        # Assert that color was announced
        assert color in mock_get_response.call_args[1]["textToSpeech"]
        assert value == self.result

    def test_start_game_black(self, mocker):
        mock_create_user = mocker.patch("chess_server.main.create_user")
        mock_play_engine = mocker.patch(
            "chess_server.main.Mediator.play_engine_move_and_get_speech",
            return_value=self.engine_reply,
        )
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google", return_value=self.result,
        )

        session_id = get_random_session_id()
        color = "black"

        value = start_game_and_get_response(session_id, color)

        mock_create_user.assert_called_with(
            session_id, board=chess.Board(), color=chess.BLACK
        )
        mock_play_engine.assert_called_once_with(session_id=session_id)
        mock_get_response.assert_called_once()

        # Assert that color and engine's move were announced
        assert color in mock_get_response.call_args[1]["textToSpeech"]
        assert self.engine_reply in mock_get_response.call_args[1]["textToSpeech"]
        assert value == self.result

    def test_start_game_random(self, mocker):

        mock_create_user = mocker.patch("chess_server.main.create_user")
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google", return_value=self.result,
        )
        mock_random = mocker.patch(
            "chess_server.main.random.choice", side_effect=random.choice
        )
        mocker.patch(
            "chess_server.main.Mediator.play_engine_move_and_get_speech",
            return_value=self.engine_reply,
        )

        session_id = get_random_session_id()
        color = "random"

        value = start_game_and_get_response(session_id, color)

        mock_create_user.assert_called_with(
            session_id, board=chess.Board(), color=mock.ANY
        )
        mock_random.assert_called_with([chess.WHITE, chess.BLACK])
        mock_get_response.assert_called_once()

        # Assert that color was announced
        kwarg_tts = mock_get_response.call_args[1]["textToSpeech"]
        assert "white" in kwarg_tts or "black" in kwarg_tts
        assert value == self.result


class TestWebhookForGoogle:
    def setup_method(self):
        self.result = {"spam": "eggs"}

    def test_webhook_welcome(self, client, mocker):
        mock_welcome = mocker.patch(
            "chess_server.main.welcome", return_value=self.result
        )

        req_data = get_dummy_webhook_request_for_google(action="welcome")

        resp = client.post("/webhook", json=req_data)

        assert resp.get_json() == self.result
        mock_welcome.assert_called_with(req_data)

    def test_webhook_choose_color(self, client, mocker):
        mock_choose_color = mocker.patch(
            "chess_server.main.choose_color", return_value=self.result
        )

        req_data = get_dummy_webhook_request_for_google(action="choose_color")

        resp = client.post("/webhook", json=req_data)

        assert resp.get_json() == self.result
        mock_choose_color.assert_called_with(req_data)

    def test_webhook_two_squares(self, client, mocker):
        mock_two_squares = mocker.patch(
            "chess_server.main.two_squares", return_value=self.result
        )

        req_data = get_dummy_webhook_request_for_google(action="two_squares")

        resp = client.post("/webhook", json=req_data)

        assert resp.get_json() == self.result
        mock_two_squares.assert_called_with(req_data)

    def test_webhook_castle(self, client, mocker):
        mock_castle = mocker.patch("chess_server.main.castle", return_value=self.result)

        req_data = get_dummy_webhook_request_for_google(action="castle")

        resp = client.post("/webhook", json=req_data)

        assert resp.get_json() == self.result
        mock_castle.assert_called_with(req_data)

    def test_webhook_resign(self, client, mocker):
        mock_resign = mocker.patch("chess_server.main.resign", return_value=self.result)

        req_data = get_dummy_webhook_request_for_google(action="resign")

        resp = client.post("/webhook", json=req_data)

        assert resp.get_json() == self.result
        mock_resign.assert_called_with(req_data)

    def test_webhook_show_board(self, client, mocker):
        mock_show_board = mocker.patch(
            "chess_server.main.show_board", return_value=self.result
        )

        req_data = get_dummy_webhook_request_for_google(action="show_board")

        resp = client.post("/webhook", json=req_data)

        assert resp.get_json() == self.result
        mock_show_board.assert_called_with(req_data)

    def test_webhook_unknown_intent(self, client, mocker):
        req_data = get_dummy_webhook_request_for_google(action="unknown")

        resp = client.post("/webhook", json=req_data)

        assert resp.status_code == 400
        assert "Unknown intent action: unknown" in str(resp.get_data())


class TestWelcome:
    def setup_method(self):
        self.session_id = get_random_session_id()
        self.result = {"foo": "bar"}

    def test_welcome_color_is_given(self, context, mocker):
        mock_start_game = mocker.patch(
            "chess_server.main.start_game_and_get_response", return_value=self.result,
        )
        color = "white"

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id, action="welcome", parameters={"color": color},
        )
        value = welcome(req_data)

        assert value == self.result
        mock_start_game.assert_called_once_with(self.session_id, color)

    def test_welcome_color_is_not_given(self, context, mocker):
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google", return_value=self.result,
        )

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id, action="welcome", parameters={"color": ""},
        )
        value = welcome(req_data)

        assert value == self.result
        mock_get_response.assert_called()

        options = GoogleOptionsList(mock_get_response.call_args[1]["options"])
        for key in ("white", "black", "random"):
            assert hasattr(options, key)


class TestChooseColor:
    def setup_method(self):
        self.session_id = get_random_session_id()
        self.result = {"foo": "bar"}

    def test_choose_color(self, mocker):
        mock_start_game = mocker.patch(
            "chess_server.main.start_game_and_get_response", return_value=self.result,
        )
        chosen_key = "chosen_key"

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id,
            action="choose_color",
            intent="choose_color",
            queryText="actions_intent_OPTION",
            option=("chosen_key", "title of that key"),
        )
        value = choose_color(req_data)

        assert value == self.result
        mock_start_game.assert_called_with(self.session_id, chosen_key)


class TestTwoSquares:
    def setup_method(self):
        self.session_id = get_random_session_id()
        self.result = {"foo": "bar"}

        self.result_unfinished = None
        self.result_win = RESPONSES["result_win"]
        self.result_lose = RESPONSES["result_lose"]
        self.result_draw = RESPONSES["result_draw"]

    def test_two_squares_illegal_move(self, mocker):
        user = User(board=chess.Board(), color=chess.WHITE)
        params = {"squares": ["a1", "b5"], "piece": "rook"}

        mock_get_user = mocker.patch("chess_server.main.get_user", return_value=user)
        mock_two_squares_to_lan = mocker.patch(
            "chess_server.main.two_squares_and_piece_to_lan",
            return_value="illegal move",
        )
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google", return_value=self.result,
        )

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id,
            action="two_squares",
            intent="two_squares",
            queryText="rook from a1 to b5",
            parameters=params,
        )
        value = two_squares(req_data)

        assert value == self.result
        mock_get_user.assert_called_with(self.session_id)
        mock_two_squares_to_lan.assert_called_with(
            board=user.board, squares=params["squares"], piece=params["piece"]
        )
        mock_get_response.assert_called()

    def test_two_squares_game_does_not_end(self, mocker):
        user = User(board=chess.Board(), color=chess.BLACK)
        squares = ["e2", "e4"]
        piece = ""
        move_lan = "e2-e4"
        params = {"squares": squares, "piece": piece}

        mock_get_user = mocker.patch("chess_server.main.get_user", return_value=user)
        mock_del_user = mocker.patch("chess_server.main.delete_user")
        mock_two_squares_to_lan = mocker.patch(
            "chess_server.main.two_squares_and_piece_to_lan", return_value=move_lan,
        )
        mock_get_result = mocker.patch(
            "chess_server.main.get_result_comment", return_value=self.result_unfinished,
        )
        mock_play_lan = mocker.patch("chess_server.main.Mediator.play_lan")
        mock_play_engine = mocker.patch(
            "chess_server.main.Mediator.play_engine_move_and_get_speech",
            return_value="spam ham and eggs",
        )
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google", return_value=self.result,
        )

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id,
            action="two_squares",
            intent="two_squares",
            queryText="Pawn from e2 to e4",
            parameters=params,
        )
        value = two_squares(req_data)

        assert value == self.result
        mock_get_user.assert_called_with(self.session_id)
        mock_del_user.assert_not_called()
        mock_two_squares_to_lan.assert_called_with(
            board=user.board, squares=squares, piece=piece
        )
        mock_get_result.assert_called()
        mock_play_lan.assert_called_with(session_id=self.session_id, lan=move_lan)
        mock_play_engine.assert_called_with(session_id=self.session_id)
        mock_get_response.assert_called_with(textToSpeech="spam ham and eggs")

    def test_two_squares_game_ends_after_user_move(self, mocker):
        user = User(board=chess.Board(), color=chess.BLACK)
        squares = ["f6", "e7"]
        piece = "queen"
        move_lan = "Qf6-e7#"
        params = {"squares": squares, "piece": piece}

        mock_get_user = mocker.patch("chess_server.main.get_user", return_value=user)
        mock_del_user = mocker.patch("chess_server.main.delete_user")
        mock_two_squares_to_lan = mocker.patch(
            "chess_server.main.two_squares_and_piece_to_lan", return_value=move_lan,
        )
        mock_get_result = mocker.patch(
            "chess_server.main.get_result_comment", return_value=self.result_win,
        )
        mock_play_lan = mocker.patch("chess_server.main.Mediator.play_lan")
        mock_play_engine = mocker.patch(
            "chess_server.main.Mediator.play_engine_move_and_get_speech",
            return_value="spam ham and eggs",
        )
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google", return_value=self.result,
        )

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id,
            action="two_squares",
            intent="two_squares",
            queryText="Pawn from e2 to e4",
            parameters=params,
        )
        value = two_squares(req_data)

        assert value == self.result
        mock_get_user.assert_called_with(self.session_id)
        mock_del_user.assert_called_with(self.session_id)
        mock_two_squares_to_lan.assert_called_with(
            board=user.board, squares=squares, piece=piece
        )
        mock_get_result.assert_called_with(user=user)
        mock_play_lan.assert_called_with(session_id=self.session_id, lan=move_lan)
        mock_play_engine.assert_not_called()
        mock_get_response.assert_called_with(
            textToSpeech=self.result_win, expectUserResponse=False
        )

    def test_two_squares_game_ends_after_engine_move(self, mocker):
        user = User(board=chess.Board(), color=chess.BLACK)
        squares = ["f6", "e7"]
        piece = "queen"
        move_lan = "Qf6-e7#"
        params = {"squares": squares, "piece": piece}

        mock_get_user = mocker.patch("chess_server.main.get_user", return_value=user)
        mock_del_user = mocker.patch("chess_server.main.delete_user")
        mock_two_squares_to_lan = mocker.patch(
            "chess_server.main.two_squares_and_piece_to_lan", return_value=move_lan,
        )
        mock_get_result = mocker.patch(
            "chess_server.main.get_result_comment",
            side_effect=[self.result_unfinished, self.result_lose],
        )
        mock_play_lan = mocker.patch("chess_server.main.Mediator.play_lan")
        mock_play_engine = mocker.patch(
            "chess_server.main.Mediator.play_engine_move_and_get_speech",
            return_value="spam ham and eggs",
        )
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google", return_value=self.result,
        )

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id,
            action="two_squares",
            intent="two_squares",
            queryText="Pawn from e2 to e4",
            parameters=params,
        )
        value = two_squares(req_data)

        assert value == self.result
        mock_get_user.assert_called_with(self.session_id)
        mock_del_user.assert_called_with(self.session_id)
        mock_two_squares_to_lan.assert_called_with(
            board=user.board, squares=squares, piece=piece
        )
        mock_get_result.assert_called_with(user=user)
        mock_play_lan.assert_called_with(session_id=self.session_id, lan=move_lan)
        mock_play_engine.assert_called_with(session_id=self.session_id)
        mock_get_response.assert_called_with(
            textToSpeech=f"spam ham and eggs. {self.result_lose}",
            expectUserResponse=False,
        )


class TestCastle:
    def setup_method(self):
        self.session_id = get_random_session_id()
        self.result = {"foo": "bar"}

        self.result_unfinished = None
        self.result_win = RESPONSES["result_win"]
        self.result_lose = RESPONSES["result_lose"]
        self.result_draw = RESPONSES["result_draw"]

    def test_castle_illegal_move(self, mocker):
        user = User(board=chess.Board(), color=chess.WHITE)
        queryText = "Castle short"

        mock_get_user = mocker.patch("chess_server.main.get_user", return_value=user)
        mock_process_castle = mocker.patch(
            "chess_server.main.process_castle_by_querytext",
            return_value="illegal move",
        )
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google", return_value=self.result,
        )

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id,
            action="castle",
            intent="castle",
            queryText=queryText,
            parameters={},
        )
        value = castle(req_data)

        assert value == self.result
        mock_get_user.assert_called_with(self.session_id)
        mock_process_castle.assert_called_with(board=user.board, queryText=queryText)
        mock_get_response.assert_called_with(textToSpeech=RESPONSES["illegal_move"])

    def test_castle_game_ends_after_user_move(self, mocker):
        user = User(board=chess.Board(), color=chess.BLACK)
        queryText = "long castle check"
        move_lan = "O-O-O#"

        mock_get_user = mocker.patch("chess_server.main.get_user", return_value=user)
        mock_del_user = mocker.patch("chess_server.main.delete_user")
        mock_process_castle = mocker.patch(
            "chess_server.main.process_castle_by_querytext", return_value=move_lan,
        )
        mock_get_result = mocker.patch(
            "chess_server.main.get_result_comment", return_value=self.result_win,
        )
        mock_play_lan = mocker.patch("chess_server.main.Mediator.play_lan")
        mock_play_engine = mocker.patch(
            "chess_server.main.Mediator.play_engine_move_and_get_speech",
            return_value="spam ham and eggs",
        )
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google", return_value=self.result,
        )

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id,
            action="castle",
            intent="castle",
            queryText=queryText,
            parameters={},
        )
        value = castle(req_data)

        assert value == self.result
        mock_get_user.assert_called_with(self.session_id)
        mock_del_user.assert_called_with(self.session_id)
        mock_process_castle.assert_called_with(board=user.board, queryText=queryText)
        mock_get_result.assert_called_with(user=user)
        mock_play_lan.assert_called_with(session_id=self.session_id, lan=move_lan)
        mock_play_engine.assert_not_called()
        mock_get_response.assert_called_with(
            textToSpeech=self.result_win, expectUserResponse=False
        )

    def test_castle_game_ends_after_engine_move(self, mocker):
        user = User(board=chess.Board(), color=chess.BLACK)
        queryText = "castle"
        move_lan = "O-O"

        mock_get_user = mocker.patch("chess_server.main.get_user", return_value=user)
        mock_del_user = mocker.patch("chess_server.main.delete_user")
        mock_process_castle = mocker.patch(
            "chess_server.main.process_castle_by_querytext", return_value=move_lan,
        )
        mock_get_result = mocker.patch(
            "chess_server.main.get_result_comment",
            side_effect=[self.result_unfinished, self.result_lose],
        )
        mock_play_lan = mocker.patch("chess_server.main.Mediator.play_lan")
        mock_play_engine = mocker.patch(
            "chess_server.main.Mediator.play_engine_move_and_get_speech",
            return_value="spam ham and eggs",
        )
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google", return_value=self.result,
        )

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id,
            action="castle",
            intent="castle",
            queryText=queryText,
            parameters={},
        )
        value = castle(req_data)

        assert value == self.result
        mock_get_user.assert_called_with(self.session_id)
        mock_del_user.assert_called_with(self.session_id)
        mock_process_castle.assert_called_with(board=user.board, queryText=queryText)
        mock_get_result.assert_called_with(user=user)
        mock_play_lan.assert_called_with(session_id=self.session_id, lan=move_lan)
        mock_play_engine.assert_called_with(session_id=self.session_id)
        mock_get_response.assert_called_with(
            textToSpeech=f"spam ham and eggs. {self.result_lose}",
            expectUserResponse=False,
        )


class TestResign:
    def setup_method(self):
        self.session_id = get_random_session_id()
        self.result = {"foo": "bar"}

    def test_resign(self, mocker):
        mock_del_user = mocker.patch("chess_server.main.delete_user")
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google", return_value=self.result,
        )
        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id, action="resign", intent="resign"
        )
        value = resign(req_data)

        assert value == self.result
        mock_del_user.assert_called_with(self.session_id)
        mock_get_response.assert_called_with(
            textToSpeech=mocker.ANY, expectUserResponse=False
        )


class TestShowBoard:
    def setup_method(self):
        self.session_id = get_random_session_id()
        self.user = User(chess.Board(), color=chess.BLACK)
        self.result = {"spam": "eggs"}

    def test_show_board_success(self, client, mocker):
        mock_get_user = mocker.patch(
            "chess_server.main.get_user", return_value=self.user
        )
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google", return_value=self.result
        )

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id, action="show_board"
        )
        with main.app.app_context():
            value = show_board(req_data)

        assert value == self.result
        mock_get_user.assert_called_with(self.session_id)
        mock_get_response.assert_called()

        imgpath = os.path.join(current_app.config["IMG_DIR"], f"{self.session_id}.png")
        assert os.path.exists(imgpath)


class TestPNGImage:
    def setup_method(self):
        self.session_id = get_random_session_id()
        self.imgpath = os.path.join(
            main.app.config["IMG_DIR"], f"{self.session_id}.png"
        )
        self.file_content = b"file content"
        self.url = f"/webhook/images/boards/{self.session_id}"

    def test_png_image_success(self, client, mocker):
        with open(self.imgpath, "w") as fw:
            fw.write(self.file_content)

        r = client.get(self.url)

        assert r.get_data() == self.file_content

    def test_png_image_file_not_found(self, client, mocker):
        with pytest.raises(NotFound):
            r = client.get(self.url)
