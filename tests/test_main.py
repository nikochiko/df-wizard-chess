import random
from unittest import TestCase, mock

import chess

from chess_server.main import (
    RESPONSES,
    welcome,
    castle,
    choose_color,
    two_squares,
    piece_and_square,
    resign,
    show_board,
    simply_san,
    get_result_comment,
    start_game_and_get_response,
)
from chess_server.utils import User, Image, BasicCard
from tests.utils import (
    GoogleOptionsList,
    get_dummy_webhook_request_for_google,
    get_random_session_id,
)


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
                "r1bq2k1/ppp2Bp1/2np1n1p/b3p3/3PP3/B1P5/P4PPP/RN1Q1RK1 b - - "
                "0 11"
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
            board=chess.Board("7K/7P/7k/8/6q1/8/8/8 w - - 0 1"),
            color=chess.WHITE,
        )
        result = get_result_comment(user=user)

        self.assertEqual(result, expected)

        # As black
        user = User(
            board=chess.Board("7K/7P/7k/8/6q1/8/8/8 w - - 0 1"),
            color=chess.BLACK,
        )
        result = get_result_comment(user=user)

        self.assertEqual(result, expected)

    def test_get_result_comment_drawn_by_insufficient_material(self):

        expected = RESPONSES["result_draw"].format(
            reason="insufficient material"
        )

        # As white
        user = User(
            board=chess.Board("4k3/8/8/8/8/5B2/8/4K3 w - - 0 1"),
            color=chess.WHITE,
        )
        result = get_result_comment(user=user)

        self.assertEqual(result, expected)

        # As black
        user = User(
            board=chess.Board("4k3/8/8/8/8/5B2/8/4K3 w - - 0 1"),
            color=chess.BLACK,
        )
        result = get_result_comment(user=user)

        self.assertEqual(result, expected)

    def test_get_result_comment_drawn_by_fifty_move_rule(self):

        expected = RESPONSES["result_draw"].format(reason="fifty move rule")

        # As white
        user = User(
            board=chess.Board("4k3/8/6r1/8/8/8/2R5/4K3 w - - 120 1"),
            color=chess.WHITE,
        )
        result = get_result_comment(user=user)

        self.assertEqual(result, expected)

        # As black
        user = User(
            board=chess.Board("4k3/8/6r1/8/8/8/2R5/4K3 w - - 120 1"),
            color=chess.BLACK,
        )
        result = get_result_comment(user=user)

        self.assertEqual(result, expected)

    def test_get_result_comment_drawn_by_threefold_repetition(self):

        expected = RESPONSES["result_draw"].format(
            reason="threefold repetition"
        )

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
            "chess_server.main.get_response_for_google",
            return_value=self.result,
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
            "chess_server.main.get_response_for_google",
            return_value=self.result,
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
        assert (
            self.engine_reply in mock_get_response.call_args[1]["textToSpeech"]
        )
        assert value == self.result

    def test_start_game_random(self, mocker):

        mock_create_user = mocker.patch("chess_server.main.create_user")
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google",
            return_value=self.result,
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
        mock_random.assert_any_call([chess.WHITE, chess.BLACK])
        mock_get_response.assert_called_once()

        # Assert that color was announced
        kwarg_tts = mock_get_response.call_args[1]["textToSpeech"]
        assert "white" in kwarg_tts or "black" in kwarg_tts
        assert value == self.result


class TestWelcome:
    def setup_method(self):
        self.session_id = get_random_session_id()
        self.result = {"foo": "bar"}

    def test_welcome_color_is_given(self, context, mocker):
        mock_start_game = mocker.patch(
            "chess_server.main.start_game_and_get_response",
            return_value=self.result,
        )
        color = "white"

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id,
            action="welcome",
            parameters={"color": color},
        )
        value = welcome(req_data)

        assert value == self.result
        mock_start_game.assert_called_once_with(self.session_id, color)

    def test_welcome_color_is_not_given(self, context, mocker):
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google",
            return_value=self.result,
        )

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id,
            action="welcome",
            parameters={"color": ""},
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
            "chess_server.main.start_game_and_get_response",
            return_value=self.result,
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
        self.engine_reply = "spam ham and eggs"

        self.image = Image(
            url="http://testserver/img.png", accessibilityText="Hello World"
        )
        self.card = BasicCard(
            image=self.image, formattedText="spam ham and eggs"
        )

        self.result_unfinished = None
        self.result_win = RESPONSES["result_win"]
        self.result_lose = RESPONSES["result_lose"]
        self.result_draw = RESPONSES["result_draw"]

    def test_two_squares_illegal_move(self, mocker):
        user = User(board=chess.Board(), color=chess.WHITE)
        params = {"squares": ["a1", "b5"], "piece": "rook"}

        mock_get_user = mocker.patch(
            "chess_server.main.get_user", return_value=user
        )
        mock_two_squares_to_lan = mocker.patch(
            "chess_server.main.two_squares_and_piece_to_lan",
            return_value="illegal move",
        )
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google",
            return_value=self.result,
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

        mock_get_user = mocker.patch(
            "chess_server.main.get_user", return_value=user
        )
        mock_del_user = mocker.patch("chess_server.main.delete_user")
        mock_two_squares_to_lan = mocker.patch(
            "chess_server.main.two_squares_and_piece_to_lan",
            return_value=move_lan,
        )
        mock_get_result = mocker.patch(
            "chess_server.main.get_result_comment",
            return_value=self.result_unfinished,
        )
        mock_play_lan = mocker.patch("chess_server.main.Mediator.play_lan")
        mock_play_engine = mocker.patch(
            "chess_server.main.Mediator.play_engine_move_and_get_speech",
            return_value=self.engine_reply,
        )
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google",
            return_value=self.result,
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
        mock_play_lan.assert_called_with(
            session_id=self.session_id, lan=move_lan
        )
        mock_play_engine.assert_called_with(self.session_id)
        assert mock_get_response.call_args[1]["textToSpeech"].startswith(
            self.engine_reply
        )

    def test_two_squares_game_ends_after_user_move(self, mocker):
        user = User(board=chess.Board(), color=chess.BLACK)
        squares = ["f6", "e7"]
        piece = "queen"
        move_lan = "Qf6-e7#"
        params = {"squares": squares, "piece": piece}

        mock_get_user = mocker.patch(
            "chess_server.main.get_user", return_value=user
        )
        mock_del_user = mocker.patch("chess_server.main.delete_user")
        mock_two_squares_to_lan = mocker.patch(
            "chess_server.main.two_squares_and_piece_to_lan",
            return_value=move_lan,
        )
        mock_get_result = mocker.patch(
            "chess_server.main.get_result_comment",
            return_value=self.result_win,
        )
        mock_play_lan = mocker.patch("chess_server.main.Mediator.play_lan")
        mock_play_engine = mocker.patch(
            "chess_server.main.Mediator.play_engine_move_and_get_speech",
            return_value=self.engine_reply,
        )
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google",
            return_value=self.result,
        )
        mock_save_board_image = mocker.patch(
            "chess_server.main.save_board_as_png_and_get_image_card",
            return_value=self.card,
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
        mock_play_lan.assert_called_with(
            session_id=self.session_id, lan=move_lan
        )
        mock_play_engine.assert_not_called()
        mock_save_board_image.assert_called_with(self.session_id)
        mock_get_response.assert_called_with(
            textToSpeech=self.result_win,
            expectUserResponse=False,
            basicCard=self.card,
        )

    def test_two_squares_game_ends_after_engine_move(self, mocker):
        user = User(board=chess.Board(), color=chess.BLACK)
        squares = ["f6", "e7"]
        piece = "queen"
        move_lan = "Qf6-e7#"
        params = {"squares": squares, "piece": piece}

        mock_get_user = mocker.patch(
            "chess_server.main.get_user", return_value=user
        )
        mock_del_user = mocker.patch("chess_server.main.delete_user")
        mock_two_squares_to_lan = mocker.patch(
            "chess_server.main.two_squares_and_piece_to_lan",
            return_value=move_lan,
        )
        mock_get_result = mocker.patch(
            "chess_server.main.get_result_comment",
            side_effect=[self.result_unfinished, self.result_lose],
        )
        mock_play_lan = mocker.patch("chess_server.main.Mediator.play_lan")
        mock_play_engine = mocker.patch(
            "chess_server.main.Mediator.play_engine_move_and_get_speech",
            return_value=self.engine_reply,
        )
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google",
            return_value=self.result,
        )
        mock_save_board_image = mocker.patch(
            "chess_server.main.save_board_as_png_and_get_image_card",
            return_value=self.card,
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
        mock_play_lan.assert_called_with(
            session_id=self.session_id, lan=move_lan
        )
        mock_play_engine.assert_called_with(self.session_id)
        mock_save_board_image.assert_called_with(self.session_id)
        mock_get_response.assert_called_with(
            textToSpeech=f"spam ham and eggs. {self.result_lose}",
            expectUserResponse=False,
            basicCard=self.card,
        )

    def test_two_squares_uppercase(self, mocker):
        user = User(board=chess.Board(), color=chess.WHITE)
        squares = ["D2", "D4"]
        actual_squares = ["d2", "d4"]
        piece = ""
        move_lan = "d2-d4"
        params = {"squares": squares, "piece": piece}

        mock_get_user = mocker.patch(
            "chess_server.main.get_user", return_value=user
        )
        mock_del_user = mocker.patch("chess_server.main.delete_user")
        mock_two_squares_to_lan = mocker.patch(
            "chess_server.main.two_squares_and_piece_to_lan",
            return_value=move_lan,
        )
        mock_get_result = mocker.patch(
            "chess_server.main.get_result_comment",
            return_value=self.result_unfinished,
        )
        mock_play_lan = mocker.patch("chess_server.main.Mediator.play_lan")
        mock_play_engine = mocker.patch(
            "chess_server.main.Mediator.play_engine_move_and_get_speech",
            return_value=self.engine_reply,
        )
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google",
            return_value=self.result,
        )

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id,
            action="two_squares",
            intent="two_squares",
            queryText="Pawn from D2 to D4",
            parameters=params,
        )
        value = two_squares(req_data)

        assert value == self.result
        mock_get_user.assert_called_with(self.session_id)
        mock_del_user.assert_not_called()
        mock_two_squares_to_lan.assert_called_with(
            board=user.board, squares=actual_squares, piece=piece
        )
        mock_get_result.assert_called()
        mock_play_lan.assert_called_with(
            session_id=self.session_id, lan=move_lan
        )
        mock_play_engine.assert_called_with(self.session_id)
        assert mock_get_response.call_args[1]["textToSpeech"].startswith(
            self.engine_reply
        )


class TestCastle:
    def setup_method(self):
        self.session_id = get_random_session_id()
        self.result = {"foo": "bar"}
        self.engine_reply = "spam ham and eggs"

        self.image = Image(
            url="http://testserver/img.png", accessibilityText="Hello World"
        )
        self.card = BasicCard(
            image=self.image, formattedText="spam ham and eggs"
        )

        self.result_unfinished = None
        self.result_win = RESPONSES["result_win"]
        self.result_lose = RESPONSES["result_lose"]
        self.result_draw = RESPONSES["result_draw"]

    def test_castle_illegal_move(self, mocker):
        user = User(board=chess.Board(), color=chess.WHITE)
        queryText = "Castle short"

        mock_get_user = mocker.patch(
            "chess_server.main.get_user", return_value=user
        )
        mock_process_castle = mocker.patch(
            "chess_server.main.process_castle_by_querytext",
            return_value="illegal move",
        )
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google",
            return_value=self.result,
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
        mock_process_castle.assert_called_with(
            board=user.board, queryText=queryText
        )
        mock_get_response.assert_called_with(
            textToSpeech=RESPONSES["illegal_move"]
        )

    def test_castle_game_does_not_end(self, mocker):
        user = User(board=chess.Board(), color=chess.BLACK)
        queryText = "Castle short"
        move_lan = "O-O"

        mock_get_user = mocker.patch(
            "chess_server.main.get_user", return_value=user
        )
        mock_del_user = mocker.patch("chess_server.main.delete_user")
        mock_process_castle = mocker.patch(
            "chess_server.main.process_castle_by_querytext",
            return_value=move_lan,
        )
        mock_get_result = mocker.patch(
            "chess_server.main.get_result_comment",
            return_value=self.result_unfinished,
        )
        mock_play_lan = mocker.patch("chess_server.main.Mediator.play_lan")
        mock_play_engine = mocker.patch(
            "chess_server.main.Mediator.play_engine_move_and_get_speech",
            return_value=self.engine_reply,
        )
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google",
            return_value=self.result,
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
        mock_del_user.assert_not_called()
        mock_process_castle.assert_called_with(
            board=user.board, queryText=queryText
        )
        mock_get_result.assert_called()
        mock_play_lan.assert_called_with(
            session_id=self.session_id, lan=move_lan
        )
        mock_play_engine.assert_called_with(self.session_id)
        assert mock_get_response.call_args[1]["textToSpeech"].startswith(
            self.engine_reply
        )

    def test_castle_game_ends_after_user_move(self, mocker):
        user = User(board=chess.Board(), color=chess.BLACK)
        queryText = "long castle check"
        move_lan = "O-O-O#"

        mock_get_user = mocker.patch(
            "chess_server.main.get_user", return_value=user
        )
        mock_del_user = mocker.patch("chess_server.main.delete_user")
        mock_process_castle = mocker.patch(
            "chess_server.main.process_castle_by_querytext",
            return_value=move_lan,
        )
        mock_get_result = mocker.patch(
            "chess_server.main.get_result_comment",
            return_value=self.result_win,
        )
        mock_play_lan = mocker.patch("chess_server.main.Mediator.play_lan")
        mock_play_engine = mocker.patch(
            "chess_server.main.Mediator.play_engine_move_and_get_speech",
            return_value=self.engine_reply,
        )
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google",
            return_value=self.result,
        )
        mock_save_board_image = mocker.patch(
            "chess_server.main.save_board_as_png_and_get_image_card",
            return_value=self.card,
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
        mock_process_castle.assert_called_with(
            board=user.board, queryText=queryText
        )
        mock_get_result.assert_called_with(user=user)
        mock_play_lan.assert_called_with(
            session_id=self.session_id, lan=move_lan
        )
        mock_play_engine.assert_not_called()
        mock_save_board_image.assert_called_with(self.session_id)
        mock_get_response.assert_called_with(
            textToSpeech=self.result_win,
            expectUserResponse=False,
            basicCard=self.card,
        )

    def test_castle_game_ends_after_engine_move(self, mocker):
        user = User(board=chess.Board(), color=chess.BLACK)
        queryText = "castle"
        move_lan = "O-O"

        mock_get_user = mocker.patch(
            "chess_server.main.get_user", return_value=user
        )
        mock_del_user = mocker.patch("chess_server.main.delete_user")
        mock_process_castle = mocker.patch(
            "chess_server.main.process_castle_by_querytext",
            return_value=move_lan,
        )
        mock_get_result = mocker.patch(
            "chess_server.main.get_result_comment",
            side_effect=[self.result_unfinished, self.result_lose],
        )
        mock_play_lan = mocker.patch("chess_server.main.Mediator.play_lan")
        mock_play_engine = mocker.patch(
            "chess_server.main.Mediator.play_engine_move_and_get_speech",
            return_value=self.engine_reply,
        )
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google",
            return_value=self.result,
        )
        mock_save_board_image = mocker.patch(
            "chess_server.main.save_board_as_png_and_get_image_card",
            return_value=self.card,
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
        mock_process_castle.assert_called_with(
            board=user.board, queryText=queryText
        )
        mock_get_result.assert_called_with(user=user)
        mock_play_lan.assert_called_with(
            session_id=self.session_id, lan=move_lan
        )
        mock_play_engine.assert_called_with(self.session_id)
        mock_save_board_image.assert_called_with(self.session_id)
        mock_get_response.assert_called_with(
            textToSpeech=f"spam ham and eggs. {self.result_lose}",
            expectUserResponse=False,
            basicCard=self.card,
        )


class TestSimplySAN:
    def setup_method(self):
        self.session_id = get_random_session_id()
        self.result = {"spam": "eggs"}
        self.engine_reply = "engine reply"

    def test_simply_san_ambiguous_move(self, mocker):
        fen = (
            "rnbqk2r/pp2bppp/4pn2/1N1p4/2Pp4/4PN2/PP3PPP/R1BQKB1R w KQkq - 0 1"
        )
        user = User(board=chess.Board(fen), color=chess.WHITE)
        san = "Nxd4"

        mocker.patch("chess_server.main.get_user", return_value=user)
        mock_play_lan = mocker.patch("chess_server.main.Mediator.play_lan")
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google",
            return_value=self.result,
        )

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id,
            action="simply_san",
            intent="simply_san",
            queryText=san,
            parameters={"san": san},
        )
        value = simply_san(req_data)

        assert value == self.result
        assert "ambiguous" in mock_get_response.call_args[1]["textToSpeech"]
        mock_play_lan.assert_not_called()

    def test_simply_san_illegal_move(self, mocker):
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        user = User(board=chess.Board(fen), color=chess.WHITE)
        san = "Ng3"

        mocker.patch("chess_server.main.get_user", return_value=user)
        mock_play_lan = mocker.patch("chess_server.main.Mediator.play_lan")
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google",
            return_value=self.result,
        )

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id,
            action="simply_san",
            intent="simply_san",
            queryText=san,
            parameters={"san": san},
        )
        value = simply_san(req_data)

        assert value == self.result
        assert "not legal" in mock_get_response.call_args[1]["textToSpeech"]
        mock_play_lan.assert_not_called()

    def test_simply_san_invalid_move(self, mocker):
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        user = User(board=chess.Board(fen), color=chess.WHITE)
        san = "Ki4+"

        mocker.patch("chess_server.main.get_user", return_value=user)
        mock_play_lan = mocker.patch("chess_server.main.Mediator.play_lan")
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google",
            return_value=self.result,
        )

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id,
            action="simply_san",
            intent="simply_san",
            queryText=san,
            parameters={"san": san},
        )
        value = simply_san(req_data)

        assert value == self.result
        assert "not valid" in mock_get_response.call_args[1]["textToSpeech"]
        mock_play_lan.assert_not_called()

    def test_simply_san_legal_move(self, mocker):
        fen = (
            "rnbqk2r/pp2bppp/2p2n2/3p2B1/3P4/2NBP3/PP3PPP/R2QK1NR b KQkq - 0 1"
        )
        user = User(board=chess.Board(fen), color=chess.BLACK)
        san = "O-O"

        mocker.patch("chess_server.main.get_user", return_value=user)
        mock_play_lan = mocker.patch("chess_server.main.Mediator.play_lan")
        mock_play_engine = mocker.patch(
            "chess_server.main.Mediator.play_engine_move_and_get_speech",
            return_value=self.engine_reply,
        )
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google",
            return_value=self.result,
        )

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id,
            action="simply_san",
            intent="simply_san",
            queryText=san,
            parameters={"san": san},
        )
        value = simply_san(req_data)

        assert value == self.result
        assert mock_get_response.call_args[1]["textToSpeech"].startswith(
            self.engine_reply
        )
        mock_play_lan.assert_called_with(self.session_id, san)
        mock_play_engine.assert_called_with(self.session_id)

    def test_simply_san_uppercase(self, mocker):
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        user = User(board=chess.Board(fen), color=chess.WHITE)
        san = "E4"
        lan = "e2-e4"

        mocker.patch("chess_server.main.get_user", return_value=user)
        mock_play_lan = mocker.patch("chess_server.main.Mediator.play_lan")
        mock_play_engine = mocker.patch(
            "chess_server.main.Mediator.play_engine_move_and_get_speech",
            return_value=self.engine_reply,
        )
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google",
            return_value=self.result,
        )

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id,
            action="simply_san",
            intent="simply_san",
            queryText=san,
            parameters={"san": san},
        )
        value = simply_san(req_data)

        assert value == self.result
        assert mock_get_response.call_args[1]["textToSpeech"].startswith(
            self.engine_reply
        )
        mock_play_lan.assert_called_with(self.session_id, lan)
        mock_play_engine.assert_called_with(self.session_id)


class TestPieceAndSquare:
    def setup_method(self):
        self.session_id = get_random_session_id()
        self.result = {"spam": "eggs"}
        self.engine_reply = "engine reply"

    def test_piece_and_square_ambiguous_move(self, mocker):
        fen = (
            "rnbqk2r/pp2bppp/4pn2/1N1p4/2Pp4/4PN2/PP3PPP/R1BQKB1R w KQkq - 0 1"
        )
        user = User(board=chess.Board(fen), color=chess.WHITE)
        querytext = "knight takes D4"
        params = {"pawn": "", "piece": "knight", "square": "D4"}

        mocker.patch("chess_server.main.get_user", return_value=user)
        mock_play_lan = mocker.patch("chess_server.main.Mediator.play_lan")
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google",
            return_value=self.result,
        )

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id,
            action="piece_and_square",
            intent="piece_and_square",
            queryText=querytext,
            parameters=params,
        )
        value = piece_and_square(req_data)

        assert value == self.result
        assert "ambiguous" in mock_get_response.call_args[1]["textToSpeech"]
        mock_play_lan.assert_not_called()

    def test_piece_and_square_illegal_move(self, mocker):
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        user = User(board=chess.Board(fen), color=chess.WHITE)
        querytext = "pawn to g5"
        params = {"piece": "", "pawn": "pawn", "square": "g5"}

        mocker.patch("chess_server.main.get_user", return_value=user)
        mock_play_lan = mocker.patch("chess_server.main.Mediator.play_lan")
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google",
            return_value=self.result,
        )

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id,
            action="piece_and_square",
            intent="piece_and_square",
            queryText=querytext,
            parameters=params,
        )
        value = piece_and_square(req_data)

        assert value == self.result
        assert "not legal" in mock_get_response.call_args[1]["textToSpeech"]
        mock_play_lan.assert_not_called()

    def test_piece_and_square_legal_move(self, mocker):
        fen = (
            "rnbqk2r/pp2bppp/2p2n2/3p2B1/3P4/2NBP3/PP3PPP/R2QK1NR b KQkq - 0 1"
        )
        user = User(board=chess.Board(fen), color=chess.BLACK)
        params = {"piece": "", "pawn": "Pawn", "square": "h6"}
        querytext = "Pawn h6"
        lan = "h7-h6"

        mocker.patch("chess_server.main.get_user", return_value=user)
        mock_play_lan = mocker.patch("chess_server.main.Mediator.play_lan")
        mock_play_engine = mocker.patch(
            "chess_server.main.Mediator.play_engine_move_and_get_speech",
            return_value=self.engine_reply,
        )
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google",
            return_value=self.result,
        )

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id,
            action="piece_and_square",
            intent="piece_and_square",
            queryText=querytext,
            parameters=params,
        )
        value = piece_and_square(req_data)

        assert value == self.result
        assert mock_get_response.call_args[1]["textToSpeech"].startswith(
            self.engine_reply
        )
        mock_play_lan.assert_called_with(self.session_id, lan)
        mock_play_engine.assert_called_with(self.session_id)

    def test_piece_and_square_legal_move_promotion(self, mocker):
        fen = "2b5/3P1kp1/5p2/8/3p3p/8/r7/2K5 w - - 1 39"
        user = User(board=chess.Board(fen), color=chess.BLACK)
        params = {"piece": "queen", "pawn": "Pawn", "square": "d8"}
        querytext = "Pawn to d8 queen"
        lan = "d7-d8=Q"

        mocker.patch("chess_server.main.get_user", return_value=user)
        mock_play_lan = mocker.patch("chess_server.main.Mediator.play_lan")
        mock_play_engine = mocker.patch(
            "chess_server.main.Mediator.play_engine_move_and_get_speech",
            return_value=self.engine_reply,
        )
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google",
            return_value=self.result,
        )

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id,
            action="piece_and_square",
            intent="piece_and_square",
            queryText=querytext,
            parameters=params,
        )
        value = piece_and_square(req_data)

        assert value == self.result
        assert mock_get_response.call_args[1]["textToSpeech"]
        mock_play_lan.assert_called_with(self.session_id, lan)
        mock_play_engine.assert_called_with(self.session_id)

    def test_piece_and_square_legal_move_promotion_to_knight_check(
        self, mocker
    ):
        fen = "2b5/3P1kp1/5p2/8/3p3p/8/r7/2K5 w - - 1 39"
        user = User(board=chess.Board(fen), color=chess.BLACK)
        params = {"piece": "Knight", "pawn": "Pawn", "square": "D8"}
        querytext = "Pawn to D8 Knight check"
        lan = "d7-d8=N+"

        mocker.patch("chess_server.main.get_user", return_value=user)
        mock_play_lan = mocker.patch("chess_server.main.Mediator.play_lan")
        mock_play_engine = mocker.patch(
            "chess_server.main.Mediator.play_engine_move_and_get_speech",
            return_value=self.engine_reply,
        )
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google",
            return_value=self.result,
        )

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id,
            action="piece_and_square",
            intent="piece_and_square",
            queryText=querytext,
            parameters=params,
        )
        value = piece_and_square(req_data)

        assert value == self.result
        assert mock_get_response.call_args[1]["textToSpeech"].startswith(
            self.engine_reply
        )
        mock_play_lan.assert_called_with(self.session_id, lan)
        mock_play_engine.assert_called_with(self.session_id)

    def test_piece_and_square_unexpected(self, mocker):
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        user = User(board=chess.Board(fen), color=chess.BLACK)
        querytext = "Gibberish and then e4"
        params = {"piece": "", "pawn": "", "square": "e4"}

        mocker.patch("chess_server.main.get_user", return_value=user)
        mock_handle_san = mocker.patch(
            "chess_server.main.handle_san_and_get_response_kwargs"
        )
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google",
            return_value=self.result,
        )

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id,
            action="piece_and_square",
            intent="piece_and_square",
            queryText=querytext,
            parameters=params,
        )
        value = piece_and_square(req_data)

        assert value == self.result
        assert (
            mock_get_response.call_args[1]["textToSpeech"]
            == "Sorry, can you say that again?"
        )
        mock_handle_san.assert_not_called()


class TestResign:
    def setup_method(self):
        self.session_id = get_random_session_id()
        self.user = User(board=chess.Board(), color=chess.WHITE)
        self.result = {"foo": "bar"}

        self.image = Image(
            url="http://testserver/img.png", accessibilityText="Hello World"
        )
        self.card = BasicCard(
            image=self.image, formattedText="spam ham and eggs"
        )

    def test_resign(self, context, mocker):
        mock_del_user = mocker.patch("chess_server.main.delete_user")
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google",
            return_value=self.result,
        )
        mocker.patch("chess_server.main.get_user", return_value=self.user)
        mock_save_board_image = mocker.patch(
            "chess_server.main.save_board_as_png_and_get_image_card",
            return_value=self.card,
        )

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id, action="resign", intent="resign"
        )
        value = resign(req_data)

        assert value == self.result
        mock_del_user.assert_called_with(self.session_id)
        mock_save_board_image.assert_called_with(self.session_id)
        mock_get_response.assert_called_with(
            textToSpeech=mocker.ANY,
            expectUserResponse=False,
            basicCard=self.card,
        )


class TestShowBoard:
    def setup_method(self):
        self.session_id = get_random_session_id()
        self.image = Image(
            url="http://testserver/img.png", accessibilityText="Hello World"
        )
        self.card = BasicCard(
            image=self.image, formattedText="spam ham and eggs"
        )
        self.result = {"spam": "eggs"}

    def test_show_board_success(self, client, config, mocker):
        mock_save_board_and_get_card = mocker.patch(
            "chess_server.main.save_board_as_png_and_get_image_card",
            return_value=self.card,
        )
        mock_get_response = mocker.patch(
            "chess_server.main.get_response_for_google",
            return_value=self.result,
        )

        req_data = get_dummy_webhook_request_for_google(
            session_id=self.session_id, action="show_board"
        )
        value = show_board(req_data)

        assert value == self.result
        mock_save_board_and_get_card.assert_called_with(self.session_id)
        assert mock_get_response.call_args[1]["basicCard"] == self.card
