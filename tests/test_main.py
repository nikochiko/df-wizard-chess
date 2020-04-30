from unittest import TestCase

import chess

from chess_server import main
from chess_server.main import RESPONSES
from chess_server.utils import User


class TestGetResultComment(TestCase):
    def test_get_result_comment_game_is_not_over_as_white(self):

        user = User(board=chess.Board(), color=chess.WHITE)

        expected = None
        result = main.get_result_comment(user)

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
        result = main.get_result_comment(user)

        self.assertEqual(result, expected)

    def test_get_result_comment_user_wins_as_white(self):

        user = User(
            board=chess.Board("4N3/ppp3Qk/2p5/7p/3P3P/8/P4P2/5K2 b - - 0 36"),
            color=chess.WHITE,
        )

        expected = RESPONSES["result_win"]
        result = main.get_result_comment(user)

        self.assertEqual(result, expected)

    def test_get_result_comment_user_wins_as_black(self):

        user = User(
            board=chess.Board(
                "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"
            ),
            color=chess.BLACK,
        )

        expected = RESPONSES["result_win"]
        result = main.get_result_comment(user=user)

        self.assertEqual(result, expected)

    def test_get_result_comment_drawn_by_stalemate(self):

        expected = RESPONSES["result_draw"].format(reason="stalemate")

        # As white
        user = User(
            board=chess.Board("7K/7P/7k/8/6q1/8/8/8 w - - 0 1"),
            color=chess.WHITE,
        )
        result = main.get_result_comment(user=user)

        self.assertEqual(result, expected)

        # As black
        user = User(
            board=chess.Board("7K/7P/7k/8/6q1/8/8/8 w - - 0 1"),
            color=chess.BLACK,
        )
        result = main.get_result_comment(user=user)

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
        result = main.get_result_comment(user=user)

        self.assertEqual(result, expected)

        # As black
        user = User(
            board=chess.Board("4k3/8/8/8/8/5B2/8/4K3 w - - 0 1"),
            color=chess.BLACK,
        )
        result = main.get_result_comment(user=user)

        self.assertEqual(result, expected)

    def test_get_result_comment_drawn_by_fifty_move_rule(self):

        expected = RESPONSES["result_draw"].format(reason="fifty move rule")

        # As white
        user = User(
            board=chess.Board("4k3/8/6r1/8/8/8/2R5/4K3 w - - 120 1"),
            color=chess.WHITE,
        )
        result = main.get_result_comment(user=user)

        self.assertEqual(result, expected)

        # As black
        user = User(
            board=chess.Board("4k3/8/6r1/8/8/8/2R5/4K3 w - - 120 1"),
            color=chess.BLACK,
        )
        result = main.get_result_comment(user=user)

        self.assertEqual(result, expected)

    def test_get_result_comment_drawn_by_threefold_repetition(self):

        expected = RESPONSES["result_draw"].format(
            reason="threefold repetition"
        )

        # As white
        board = chess.Board()
        user = User(board=board, color=chess.WHITE)

        self.assertEqual(main.get_result_comment(user=user), None)
        board.push_san("Nf3")
        board.push_san("Nf6")
        self.assertEqual(main.get_result_comment(user=user), None)
        board.push_san("Ng1")
        board.push_san("Ng8")
        self.assertEqual(main.get_result_comment(user=user), None)
        board.push_san("Nf3")
        board.push_san("Nf6")
        self.assertEqual(main.get_result_comment(user=user), None)
        board.push_san("Ng1")

        result = main.get_result_comment(user=user)

        self.assertEqual(result, expected)

        # As black
        board = chess.Board()
        user = User(board=board, color=chess.BLACK)

        board.push_san("Nf3")
        self.assertEqual(main.get_result_comment(user=user), None)
        board.push_san("Nf6")
        board.push_san("Ng1")
        self.assertEqual(main.get_result_comment(user=user), None)
        board.push_san("Ng8")
        board.push_san("Nf3")
        self.assertEqual(main.get_result_comment(user=user), None)
        board.push_san("Nf6")
        board.push_san("Ng1")

        result = main.get_result_comment(user=user)

        self.assertEqual(result, expected)
