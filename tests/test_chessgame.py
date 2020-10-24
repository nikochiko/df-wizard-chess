
import chess
import chess.engine
import pytest
from flask import current_app
from pytest_mock import mocker

from chess_server.chessgame import Mediator
from chess_server.utils import User
from tests.utils import get_random_session_id


@pytest.mark.usefixtures("context")
class TestMediator():
    def setUp(self):
        self.mock_engine_path = "engine_path"
        self.mock_engine = mocker.MagicMock()

        self.board = chess.Board()
        self.color = chess.WHITE
        self.user = User(self.board, self.color)

        self.mediator = Mediator()

        # Mock the popen_uci method to return our mock engine
        self.patcher = mocker.patch(
            "chess.engine.SimpleEngine.popen_uci",
            return_value=self.mock_engine,
        )
        self.mock_popen_uci = self.patcher.start()

    def test_activate_engine_with_arg_successful(self):

        # Call the function with mocks in place
        self.mediator.activate_engine(self.mock_engine_path)

        # Verify that the engine was initialized
        self.mock_popen_uci.assert_called_with(self.mock_engine_path)
        self.assertEqual(self.mediator.engine, self.mock_engine)

    @mocker.patch("chess_server.chessgame.logger.error")
    def test_activate_engine_with_arg_error(self, mock_logger):

        # popen_uci method will raise exception when run
        self.mock_popen_uci.side_effect = Exception("Example error")

        log = (
            f"Error while initializing engine from {self.mock_engine_path}"
            ":\nExample error"
        )

        # Should raise exception
        with self.assertRaises(Exception, msg="Example error"):
            self.mediator.activate_engine(self.mock_engine_path)
            mock_logger.assert_called_with(log)

    def test_activate_engine_from_config(self):

        # Edit the engine path in config
        current_app.config["ENGINE_PATH"] = self.mock_engine_path
        self.mediator.activate_engine()

        self.mock_popen_uci.assert_called_with(self.mock_engine_path)
        self.assertEqual(self.mediator.engine, self.mock_engine)

    @mocker.patch("chess_server.chessgame.lan_to_speech")
    @mocker.patch("chess_server.chessgame.update_user")
    @mocker.patch("chess_server.chessgame.get_user")
    def test_play_engine_move_and_get_speech(
        self, mock_get_user, mock_update_user, mock_lts
    ):

        self.mediator.engine = self.mock_engine

        session_id = get_random_session_id()
        move = self.board.parse_san("e4")
        lan = self.board.lan(move)

        mock_get_user.return_value = self.user
        mock_lts.return_value = "test reply"
        self.mock_engine.play.return_value = chess.engine.PlayResult(
            move=move, ponder=None
        )

        with mocker.patch.object(self.board, "push") as mock_push:
            with mocker.patch.object(self.board, "lan", return_value=lan):
                value = self.mediator.play_engine_move_and_get_speech(
                    session_id
                )

        mock_get_user.assert_called_with(
            session_id
        )  # User object was retrieved
        self.mock_engine.play.assert_called()  # Engine was used
        mock_push.assert_called_with(move)  # Move was played
        mock_update_user.assert_called_with(
            session_id, self.board
        )  # DB was updated
        self.assertEqual(value, "test reply")  # Correctly reply was given

    @mocker.patch("chess_server.chessgame.update_user")
    @mocker.patch("chess_server.chessgame.get_user")
    def test_play_lan_success(self, mock_get_user, mock_update_user):

        session_id = get_random_session_id()
        move = self.board.parse_san("Nf3")
        lan = self.board.lan(move)

        mock_get_user.return_value = self.user

        with mocker.patch.object(self.board, "push") as mock_push:
            # The board method which finally makes the move is `Board.push`
            # even though the method being called directly is `Board.push_san`
            value = self.mediator.play_lan(session_id, lan)

        mock_get_user.assert_called_with(session_id)  # User object retrieved
        mock_push.assert_called_with(move)  # Move played
        mock_update_user.assert_called_with(
            session_id, self.board
        )  # DB updated
        self.assertTrue(value)  # Correct value returned

    @mocker.patch("chess_server.chessgame.update_user")
    @mocker.patch("chess_server.chessgame.get_user")
    def test_play_lan_illegal_move(self, mock_get_user, mock_update_user):

        session_id = get_random_session_id()
        lan = "e2xe1"  # Illegal move

        mock_get_user.return_value = self.user

        value = self.mediator.play_lan(session_id, lan)

        mock_get_user.assert_called_with(session_id)  # User object retrieved
        mock_update_user.asert_not_called()  # DB not updated
        self.assertFalse(value)  # Correct value returned

    def tearDown(self):
        self.patcher.stop()
