import random
import re
from typing import Any, Dict, Optional

import chess

from chess_server.chessgame import Mediator
from chess_server.utils import (
    User,
    create_user,
    delete_user,
    get_user,
    get_session_by_req,
    get_params_by_req,
    get_piece_symbol,
    get_prompt_phrase,
    get_response_for_google,
    get_san_description,
    process_castle_by_querytext,
    save_board_as_png_and_get_image_card,
    two_squares_and_piece_to_lan,
    undo_users_last_move,
)

RESPONSES = {
    "result_win": "Congratulations! You have won the game."
    " Thanks for playing.",
    "result_lose": "Oops, you were checkmated. Thanks for playing.",
    "result_draw": "The game has been drawn due to {reason}. "
    "Thanks for playing.",
    "illegal_move": "The move is not legal, please try once again."
    " Just an FYI, you can say Show Board to see the"
    " current position on the board.",
}

mediator = Mediator()


def welcome(req: Dict[str, Any]) -> Dict[str, Any]:

    session_id = get_session_by_req(req)
    color = get_params_by_req(req)["color"]

    if color:
        return start_game_and_get_response(session_id, color)

    response_text = "Howdy! Which color would you like to choose?"
    options = [
        {
            "optionInfo": {"key": "white"},
            "description": "I like white!",
            "title": "White",
        },
        {
            "optionInfo": {"key": "black"},
            "description": "I'll choose black.",
            "title": "Black",
        },
        {
            "optionInfo": {"key": "random"},
            "description": "Choose randomly",
            "title": "Anything works!",
        },
    ]

    return get_response_for_google(textToSpeech=response_text, options=options)


def choose_color(req: Dict[str, Any]) -> Dict[str, Any]:
    """Assign board and color to user"""

    # Get session id to store user data by key
    session_id = get_session_by_req(req)

    # Extract the key of chosen list item
    arguments = req["originalDetectIntentRequest"]["payload"][
        "inputs"
    ]  # Is a list

    for each in arguments:
        if each["intent"] == "actions.intent.OPTION":
            arguments = each["arguments"]
            break

    # Look for chosen key
    for each in arguments:
        if each.get("name") == "OPTION":
            color = each["textValue"]
            break

    return start_game_and_get_response(session_id, color)


def two_squares(req: Dict[str, Any]) -> Dict[str, Any]:
    """Given two squares and a piece, play a move"""
    params = get_params_by_req(req)

    # Extract params and take the lowercase of the square
    squares = [square.lower() for square in params["squares"]]
    piece = params["piece"]

    if len(squares) == 1:
        return piece_and_square(req)

    # Extract board
    session_id = get_session_by_req(req)

    # TODO: Handle case when `session_id not found' when migrating to db
    # Get user
    user = get_user(session_id)

    # Get LAN move
    lan = two_squares_and_piece_to_lan(
        board=user.board, squares=squares, piece=piece
    )

    # TODO: Store this reply somewhere
    if lan == "illegal move":
        return get_response_for_google(textToSpeech=RESPONSES["illegal_move"])

    # Play move on board
    mediator.play_lan(session_id=session_id, lan=lan)

    kwargs = get_response_kwargs(session_id)
    return get_response_for_google(**kwargs)


def castle(req: Dict[str, Any]) -> Dict[str, Any]:
    """When asked to castle, try playing the castles move"""

    session_id = get_session_by_req(req)
    user = get_user(session_id)

    queryText = req["queryResult"]["queryText"]

    # Get lan of move
    lan = process_castle_by_querytext(board=user.board, queryText=queryText)

    if lan == "illegal move":
        return get_response_for_google(textToSpeech=RESPONSES["illegal_move"])

    mediator.play_lan(session_id=session_id, lan=lan)

    kwargs = get_response_kwargs(session_id)
    return get_response_for_google(**kwargs)


def simply_san(req: Dict[str, Any]) -> Dict[str, Any]:
    """Intent handler for simply SAN moves

    Note: Accepts overspecified SAN (including LAN)
    """
    session_id = get_session_by_req(req)
    san = get_params_by_req(req)["san"]

    # Convert pawn moves like E4, D5 to lowercase i.e. e4, d5
    if re.match(r"^[A-Z][1-8]$", san):
        san = san.lower()

    user = get_user(session_id)
    board = user.board

    kwargs = handle_san_and_get_response_kwargs(session_id, board, san)

    return get_response_for_google(**kwargs)


def piece_and_square(req: Dict[str, Any]) -> Dict[str, Any]:
    """Intent handler for when only one piece and one square are given"""
    session_id = get_session_by_req(req)
    params = get_params_by_req(req)

    piece = params["piece"].lower()
    pawn = params["pawn"].lower()
    square = params["square"].lower()

    board = get_user(session_id).board

    if pawn:
        san = square

        if piece and (square[-1] == "1" or square[-1] == "8"):
            # Promotion move
            san = f"{square}={get_piece_symbol(piece, upper=True)}"

        kwargs = handle_san_and_get_response_kwargs(session_id, board, san)

    elif piece:
        san = f"{get_piece_symbol(piece, upper=True)}{square}"
        kwargs = handle_san_and_get_response_kwargs(session_id, board, san)

    else:
        kwargs = {"textToSpeech": "Sorry, can you say that again?"}

    return get_response_for_google(**kwargs)


def resign(req: Dict[str, Any]) -> Dict[str, Any]:
    """Delete the player from the database and return a conclusion response"""
    session_id = get_session_by_req(req)
    card = save_board_as_png_and_get_image_card(session_id)
    delete_user(session_id)

    output = "GG! Thanks for playing."

    return get_response_for_google(
        textToSpeech=output, expectUserResponse=False, basicCard=card
    )


def show_board(req: Dict[str, Any]) -> Dict[str, Any]:
    """Show the board to player as a PNG image"""
    session_id = get_session_by_req(req)

    # Save board to <IMG_DIR>/<session_id>.png
    card = save_board_as_png_and_get_image_card(session_id)

    resp = get_response_for_google(
        textToSpeech="OK! Here it is. What's your next move?", basicCard=card
    )

    return resp


def undo(req: Dict[str, Any]) -> Dict[str, Any]:
    """Undo the last move of the user"""
    session_id = get_session_by_req(req)

    undone = undo_users_last_move(session_id)

    if undone:
        if len(undone) == 1:
            resp = f"OK! Undid the move {undone[0]}."

        else:
            engine_move, user_move = undone
            resp = (
                f"Alright! The moves {user_move} and {engine_move} have been "
                "undone."
            )

    else:
        resp = "Nothing to undo!"

    text_to_speech = f"{resp} {get_prompt_phrase()}"

    return get_response_for_google(
        textToSpeech=text_to_speech, displayText=resp
    )


def start_game_and_get_response(session_id: str, color: str):
    """Initializes game given session and color"""

    if color == "white":
        create_user(session_id, board=chess.Board(), color=chess.WHITE)

    elif color == "black":
        create_user(session_id, board=chess.Board(), color=chess.BLACK)

    else:
        chosen = random.choice([chess.WHITE, chess.BLACK])
        color = "white" if chosen else "black"
        create_user(session_id, board=chess.Board(), color=chosen)

    output = f"Okay! You are playing with the {color} pieces."

    if color == "white":
        output += " Your turn."

    else:
        # Play engine's move and append that move's speech to output
        speech = mediator.play_engine_move_and_get_speech(
            session_id=session_id
        )
        output += f" My move is {speech}. {get_prompt_phrase()}"

    return get_response_for_google(textToSpeech=output)


def get_result_comment(user: User) -> str:
    """Return a response provided that the game has ended

    result is a str: valid values are '1-0', '0-1' or '1/2-1/2'
    """
    # Get result
    result = user.board.result(claim_draw=True)

    # Return None if game has not ended
    if result == "*":
        return None

    if result[-1] == "2":  # Only happens for draw
        # Find out reason for draw
        if user.board.is_stalemate():
            reason = "stalemate"

        elif user.board.is_insufficient_material():
            reason = "insufficient material"

        elif user.board.can_claim_fifty_moves():
            reason = "fifty move rule"

        elif user.board.can_claim_threefold_repetition():
            reason = "threefold repetition"

        else:
            reason = "unknown reason"

        output = RESPONSES["result_draw"].format(reason=reason)

    # When user wins
    elif (result[-1] == "0") == user.color:
        # User.color is True when it is chess.WHITE,
        # white is winner when result[-1] = '0'
        # If both are False, then player was black and black won
        # In the other case player lost

        output = RESPONSES["result_win"]

    # When user loses
    else:
        output = RESPONSES["result_lose"]

    return output


def get_response_kwargs(session_id: str, lastmove_lan: Optional[str] = None):
    """
    Gets the appropriate args for generating response from result and
    engine's move

    Note: Also plays engine's move on the board
    """
    user = get_user(session_id)

    kwargs = {}

    game_result = get_result_comment(user=user)

    if game_result:
        card = save_board_as_png_and_get_image_card(session_id)
        # TODO: Archive the game instead of deleting
        delete_user(session_id)
        kwargs.update(
            textToSpeech=game_result, expectUserResponse=False, basicCard=card
        )

    else:
        # Play engine's move
        output = mediator.play_engine_move_and_get_speech(session_id)

        user = get_user(session_id)

        game_result = get_result_comment(user=user)
        if game_result:
            output = f"{output}. {game_result}"
            card = save_board_as_png_and_get_image_card(session_id)
            delete_user(session_id)
            kwargs.update(
                textToSpeech=output, expectUserResponse=False, basicCard=card
            )

        else:
            output = f"{output}. {get_prompt_phrase()}"
            kwargs["textToSpeech"] = output

    if lastmove_lan:
        kwargs[
            "displayText"
        ] = f"Your last move was {lastmove_lan}.\n {output}"

    return kwargs


def handle_san_and_get_response_kwargs(
    session_id: str, board: chess.Board, san: str
) -> Dict[str, Any]:
    """Process a SAN move and get response kwargs"""

    status = get_san_description(board, san)

    if status == "legal":
        # Convert SAN to LAN
        move = board.parse_san(san)
        lan = board.lan(move)

        mediator.play_lan(session_id, lan)
        kwargs = get_response_kwargs(session_id, lastmove_lan=lan)

    elif status == "ambiguous":
        kwargs = {
            "textToSpeech": f"The move {san} is ambiguous. Please clarify by"
            " giving more details about the move."
        }

    elif status == "illegal":
        kwargs = {
            "textToSpeech": f"The move {san} is not legal. Please try again."
            " You can always ask me to 'show the board' if you feel lost."
        }

    elif status == "invalid":
        kwargs = {"textToSpeech": f"The move {san} is not valid."}

    return kwargs
