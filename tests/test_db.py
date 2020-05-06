import sqlite3
from typing import Any, List, Tuple

import chess
import pytest
from flask import current_app as app
from flask import g

from chess_server.utils import (
    User,
    create_user,
    get_user,
    update_user,
    delete_user,
    exists_in_db,
)
from tests.utils import get_random_session_id


def get_all_entries_from_db() -> List[Tuple[Any]]:
    """Fetches all entries from table users from the database"""
    conn = sqlite3.connect(app.config["DATABASE"])
    cur = conn.cursor()

    # Run query
    res = cur.execute(f"SELECT * FROM users")

    # Convert to list
    res = res.fetchall()

    # Close connection before returning
    conn.close()

    return res


def test_setup(client):
    assert "DATABASE" in app.config
    assert app.config["TESTING"] is True
    assert "db" in g


def test_create_user(client):
    # Creating a random session id of length 36
    session_id = get_random_session_id()

    # Generate arguments for create_user
    board = chess.Board()
    color = chess.WHITE

    create_user(session_id, board, color)

    # Read from database
    data = get_all_entries_from_db()

    # Only one user was created
    assert len(data) == 1

    # Check parameters
    assert data[0] == (session_id, board.fen(), color)


def test_create_user_multiple_entries(client):
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

    data = get_all_entries_from_db()

    # Only one entry should be present
    assert len(data) == 1
    assert data[0] == (session_id1, board1.fen(), color1)

    # Insert second entry
    create_user(session_id2, board2, color2)

    data = get_all_entries_from_db()

    assert len(data) == 2
    assert (session_id1, board1.fen(), color1) in data
    assert (session_id2, board2.fen(), color2) in data


def test_create_user_when_entry_with_key_already_exists(client):
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


def test_create_user_db_does_not_exist():
    # Not using context fixture so db does not exist prior to this test

    session_id = get_random_session_id()
    board = chess.Board()
    color = chess.BLACK

    # Play some random moves
    board.push_san("Nf3")
    board.push_san("Nf6")

    with pytest.raises(Exception, match="Database not found."):
        with app.test_request_context():
            create_user(session_id, board, color)


def test_get_user(client):
    session_id = get_random_session_id()
    board = chess.Board()
    color = chess.BLACK

    create_user(session_id, board, color)

    assert get_user(session_id) == User(board, color)


def test_get_user_when_multiple_entries_exist(client):
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


def test_get_user_db_does_not_exist():
    session_id = get_random_session_id()

    with pytest.raises(Exception, match="Database not found."):
        with app.test_request_context():
            get_user(session_id)


def test_get_user_entry_does_not_exist(client):
    session_id = get_random_session_id()

    # Skipping create_user() step
    with pytest.raises(Exception, match="Entry not found."):
        get_user(session_id)


def test_update_user(client):
    session_id = get_random_session_id()
    board = chess.Board()
    color = chess.BLACK

    create_user(session_id, board, color)

    # Now update it with some moves
    board.push_san("Nf3")
    board.push_san("d5")

    update_user(session_id, board)

    assert get_user(session_id) == User(board, color)


def test_update_user_multiple_entries(client):
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


def test_update_user_db_does_not_exist():
    session_id = get_random_session_id()
    board = chess.Board()

    with pytest.raises(Exception, match="Database not found."):
        with app.test_request_context():
            update_user(session_id, board)


def test_update_user_entry_does_not_exist(client):
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


def test_delete_user(client):
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
    data = get_all_entries_from_db()
    assert len(data) == 0


def test_delete_user_multiple_entries(client):
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
    assert len(get_all_entries_from_db()) == 1
    assert get_user(session_id2) == User(board2, color2)


def test_delete_user_db_does_not_exist():
    session_id = get_random_session_id()

    with pytest.raises(Exception, match="Database not found."):
        with app.test_request_context():
            delete_user(session_id)
