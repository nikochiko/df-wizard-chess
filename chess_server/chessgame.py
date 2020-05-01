import logging
from typing import List, Optional

import chess.engine

from chess_server.config import ENGINE_PATH
from chess_server.utils import get_user, update_user

logger = logging.getLogger(__name__)
logger.setLevel("WARNING")

pieces = {
    "K": "King",
    "Q": "Queen",
    "R": "Rook",
    "N": "Knight",
    "B": "Bishop",
}

pieces_symbols = {
    "king": "k",
    "queen": "q",
    "rook": "r",
    "knight": "n",
    "bishop": "b",
}


def lan_to_speech(lan: str) -> str:
    """Convert LAN move to a more spoken form

    Such as:
    Ng1-f3 -> Knight from g1 to f3
    Bc4xf7+ -> Bishop from c4 captures f7 check
    e7-e8Q -> Pawn from e7 to e8 queen
    h7xg8Q -> Pawn from h7 captures g8 queen
    """

    # Setting up boolean flag is_check
    if lan[-1] == "+" or lan[-1] == "#":
        is_check = True
        lan = lan[:-1]  # Exclude the last element
    else:
        is_check = False

    # Return early for castling moves
    if lan.startswith("O-O"):
        prefix = "Long " if lan == "O-O-O" else "Short "
        return f"{prefix}castle{' check' if is_check else ''}"

    output_string = ""

    # Add piece to output_string
    if lan[0] in pieces.keys():
        output_string += pieces[lan[0]]
        lan = lan[1:]
    else:
        output_string += "Pawn"

    # The from square will now be indicated by first two positions
    output_string += f" from {lan[:2]}"

    # Add destination square to output_string
    output_string += f"{' captures' if lan[2] == 'x' else ' to'} {lan[3:5]}"

    # If it is a promotion move (a7-a8=Q)
    if lan[-1] in pieces.keys():
        output_string += f" {pieces[lan[-1]]}"

    # Add check to output string if required
    output_string += " check" if is_check else ""

    return output_string


def two_squares_and_piece_to_lan(
    board: chess.Board, squares: List[str], piece: Optional[str] = None,
) -> str:
    """Get the LAN notation of the move from two squares and a piece"""

    # Squares should strictly have only 2 elements
    initial_square, destination_square = squares

    # First get the uci notation of move
    uci = f"{initial_square}{destination_square}"
    move = chess.Move.from_uci(uci)

    # Return LAN if move is legal without including the piece
    if board.is_legal(move):
        return board.lan(move)

    # Move could be promotion, try adding theat to uci and see if that works
    if piece:
        uci = f"{uci}{pieces_symbols[piece]}"
        move = chess.Move.from_uci(uci)

        if board.is_legal(move):
            return board.lan(move)

    return "illegal move"


def process_castle_by_querytext(board: chess.Board, queryText: str) -> str:
    """
    Process queryText to determine whether castle is legal and which side
    it should be done.
    Returns the LAN notation of the castling move (O-O or O-O-O with + or
    # suffix if required)

    Defaults to short castle (O-O) when the side is not explicitly mentioned
    """
    queryText = queryText.lower()

    # Check which castling is legal
    short_castle = None
    try:
        short_castle = board.parse_san("O-O")
    except ValueError:  # Illegal move
        pass

    long_castle = None
    try:
        long_castle = board.parse_san("O-O-O")
    except ValueError:
        pass

    # Check if the query suggests to short castle
    go_short = False
    for word in ["short", "kingside", "king's side"]:
        if word in queryText:
            go_short = True
            break

    # Similarly for long
    go_long = False
    for word in ["long", "queenside", "queen's side"]:
        if word in queryText:
            go_long = True
            break

    # Return LAN notation of long castle if move is legal
    # First priority to short castle
    if go_short:
        result = board.lan(short_castle) if short_castle else "illegal move"
    elif go_long:
        result = board.lan(long_castle) if long_castle else "illegal move"
    elif short_castle:
        result = board.lan(short_castle)
    elif long_castle:
        result = board.lan(long_castle)
    else:
        result = "illegal move"

    return result


class Mediator:
    def activate_engine(self, engine_path: Optional[str] = None):

        # If engine path is not given, check if it is mentioned in config file
        if not engine_path:
            # See: config.py
            engine_path = ENGINE_PATH

        try:
            # Load engine
            self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        except Exception as exc:
            # Log and throw error
            print(
                f"Error while trying to set up engine from path {engine_path}."
                " See logs for more details."
            )
            logger.error(
                f"Error while initializing engine from {engine_path}:\n{exc}"
            )
            raise

    def play_engine_move_and_get_speech(self, session_id: str) -> str:
        """Play engine's move and return the speech conversion of the move"""

        user = get_user(session_id)

        # Doesn't actually play the move
        result = self.engine.play(user.board, chess.engine.Limit(time=0.100))

        # Store LAN notation and push
        lan = user.board.lan(result.move)
        user.board.push(result.move)

        # Update DB
        update_user(session_id, user.board)

        return lan_to_speech(lan)

    def play_lan(self, session_id: str, lan: str) -> bool:
        """Play move and return bool showing if move was successful"""

        user = get_user(session_id)

        try:
            user.board.push_san(lan)
            update_user(session_id)
            return True
        except ValueError:  # Illegal, invalid or ambiguous move
            return False
