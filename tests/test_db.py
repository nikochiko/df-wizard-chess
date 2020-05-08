import chess
import pytest

from chess_server.models import UserModel
from chess_server.utils import (
    User,
    create_user,
    get_user,
    update_user,
    delete_user,
    exists_in_db,
)
from tests.utils import get_random_session_id


def test_create_user(context):
    # Creating a random session id of length 36
    session_id = get_random_session_id()

    # Generate arguments for create_user
    board = chess.Board()
    color = chess.WHITE

    create_user(session_id, board, color)

    # Only one user was created
    assert UserModel.query.count() == 1
    assert UserModel.query.get(session_id) is not None


def test_create_user_multiple_entries(context):
    session_id1 = get_random_session_id()
    board1 = chess.Board()
    board1.push_san("Nf3")
    color1 = chess.BLACK

    session_id2 = get_random_session_id()
    board2 = chess.Board()
    board2.push_san("e4")
    board2.push_san("e5")
    color2 = chess.WHITE

    # Inserting one at a time
    create_user(session_id1, board1, color1)

    # Only one entry should be present
    assert UserModel.query.count() == 1
    assert UserModel.query.get(session_id1) is not None

    # Insert second entry
    create_user(session_id2, board2, color2)

    assert UserModel.query.count() == 2
    assert UserModel.query.get(session_id1) is not None
    assert UserModel.query.get(session_id2) is not None


def test_create_user_when_entry_with_key_already_exists(context):
    session_id = get_random_session_id()
    board = chess.Board()
    color = chess.WHITE

    create_user(session_id, board, color)

    board.push_san("Nf3")
    board.push_san("c6")

    # Now trying to create another entry with same session_id
    with pytest.raises(
        Exception, match=f"Entry with key {session_id} already exists."
    ):
        create_user(session_id, board, color)


def test_get_user(context):
    session_id = get_random_session_id()
    board = chess.Board()
    color = chess.BLACK

    create_user(session_id, board, color)

    assert get_user(session_id) == User(board, color)


def test_get_user_when_multiple_entries_exist(context):
    session_id = get_random_session_id()
    board = chess.Board()
    color = chess.WHITE

    # Make some moves
    board.push_san("Nc3")
    board.push_san("d5")
    board.push_san("d4")

    create_user(session_id, board, color)

    # Another entry
    session_id2 = get_random_session_id()
    board2 = chess.Board()
    color2 = chess.WHITE

    create_user(session_id2, board2, color2)

    assert get_user(session_id) == User(board, color)


def test_get_user_entry_does_not_exist(context):
    session_id = get_random_session_id()

    # Skipping create_user() step
    with pytest.raises(Exception, match="Entry not found."):
        get_user(session_id)


def test_update_user(context):
    session_id = get_random_session_id()
    board = chess.Board()
    color = chess.BLACK

    create_user(session_id, board, color)

    # Now update it with some moves
    board.push_san("Nf3")
    board.push_san("d5")

    update_user(session_id, board)

    assert get_user(session_id) == User(board, color)


def test_update_user_multiple_entries(context):
    session_id = get_random_session_id()
    board = chess.Board()
    color = chess.WHITE

    create_user(session_id, board, color)

    # Create second user
    session_id2 = get_random_session_id()
    board2 = chess.Board()
    color2 = chess.BLACK

    board2.push_san("e4")
    board2.push_san("e5")

    create_user(session_id2, board2, color2)

    board.push_san("g4")
    update_user(session_id, board)

    assert get_user(session_id) == User(board, color)
    # Ensure that other entry has not been modified
    assert get_user(session_id2) == User(board2, color2)


def test_update_user_entry_does_not_exist(context):
    session_id = get_random_session_id()
    board = chess.Board()

    board.push_san("e4")
    board.push_san("e5")

    # Create another random entry
    session_id2 = get_random_session_id()
    board2 = chess.Board()
    color2 = chess.BLACK

    create_user(session_id2, board2, color2)

    with pytest.raises(Exception, match="Entry not found."):
        update_user(session_id, board)


def test_delete_user(context):
    session_id = get_random_session_id()
    board = chess.Board()
    color = chess.BLACK

    create_user(session_id, board, color)

    # Verify that the user has been created
    assert get_user(session_id) == User(board, color)

    delete_user(session_id)

    # Verify that deletion is successful
    assert exists_in_db(session_id) is False

    # Verify that no other operation has been performed
    assert UserModel.query.count() == 0


def test_delete_user_multiple_entries(context):
    session_id = get_random_session_id()
    board = chess.Board()
    color = chess.WHITE

    create_user(session_id, board, color)

    # Create another user
    session_id2 = get_random_session_id()
    board2 = chess.Board()
    color2 = chess.BLACK

    board2.push_san("e4")
    board2.push_san("d5")

    create_user(session_id2, board2, color2)

    # Delete first user
    delete_user(session_id)

    assert exists_in_db(session_id) is False

    # Verify that no other changes were made
    assert UserModel.query.count() == 1
    assert get_user(session_id2) == User(board2, color2)
