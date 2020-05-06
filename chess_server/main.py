import random
from typing import Any, Dict

import chess
from flask import url_for

from chess_server.chessgame import Mediator
from chess_server.utils import (
    User,
    BasicCard,
    Image,
    create_user,
    delete_user,
    get_user,
    get_session_by_req,
    get_params_by_req,
    get_response_for_google,
    process_castle_by_querytext,
    save_board_as_png,
    two_squares_and_piece_to_lan,
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

    if get_params_by_req(req)["color"]:
        color = get_params_by_req(req)["color"]
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

    # Extract params
    squares = params["squares"]
    piece = params["piece"]

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

    game_result = get_result_comment(user=user)
    if game_result:
        # TODO: Display image of board when game is over
        # image = get_image(board)
        delete_user(session_id)  # Free up memory
        return get_response_for_google(
            textToSpeech=game_result, expectUserResponse=False
        )

    # Play engine's move
    output = mediator.play_engine_move_and_get_speech(session_id=session_id)

    game_result = get_result_comment(user=user)
    if game_result:
        output = f"{output}. {game_result}"
        delete_user(session_id)  # Free up memory
        return get_response_for_google(
            textToSpeech=output, expectUserResponse=False
        )

    return get_response_for_google(textToSpeech=output)


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

    game_result = get_result_comment(user=user)
    if game_result:
        # TODO: Display image of board when game is over
        # image = get_image(board)
        delete_user(session_id)
        return get_response_for_google(
            textToSpeech=game_result, expectUserResponse=False
        )

    # Play engine's move
    output = mediator.play_engine_move_and_get_speech(session_id=session_id)

    game_result = get_result_comment(user=user)
    if game_result:
        output = f"{output}. {game_result}"
        delete_user(session_id)
        return get_response_for_google(
            textToSpeech=output, expectUserResponse=False
        )

    return get_response_for_google(textToSpeech=output)


def resign(req: Dict[str, Any]) -> Dict[str, Any]:
    """Delete the player from the database and return a conclusion response"""
    session_id = get_session_by_req(req)
    board = get_user(session_id).board

    # Saves board to disk
    save_board_as_png(session_id, board)

    url = url_for("webhook_bp.png_image", session_id=session_id)
    alt = str(board)

    image = Image(url=url, accessibilityText=alt)
    formattedText = f"**Moves played: {board.fullmove_number}**"
    card = BasicCard(image=image, formattedText=formattedText)

    delete_user(session_id)

    output = "GG! Thanks for playing."

    return get_response_for_google(
        textToSpeech=output, expectUserResponse=False, basicCard=card
    )


def show_board(req: Dict[str, Any]) -> Dict[str, Any]:
    """Show the board to player as a PNG image"""
    session_id = get_session_by_req(req)
    board = get_user(session_id).board

    # Save board to <IMG_DIR>/<session_id>.png
    save_board_as_png(session_id, board)

    url = url_for("webhook_bp.png_image", session_id=session_id)
    alt = str(board)

    image = Image(url=url, accessibilityText=alt)
    formatted_text = f"**Moves played: {board.fullmove_number}**"
    card = BasicCard(image=image, formattedText=formatted_text)

    resp = get_response_for_google(
        textToSpeech="Cool! Here's the board for you.", basicCard=card
    )

    return resp


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
        output += f" My move is {speech}."

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
