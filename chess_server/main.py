import random
from typing import Any, Dict

import chess
from flask import Flask, jsonify, make_response, request

from chess_server.chessgame import (
    Mediator,
    User,
    lan_to_speech,
    process_castle_by_querytext,
    two_squares_and_piece_to_lan,
)
from chess_server.utils import (
    get_session_by_req,
    get_params_by_req,
    generate_response_for_google_assistant,
)


app = Flask(__name__)
log = app.logger


# TODO: Add tests!!!

# Flow >
# > user says hi to dialogflow
# > we reply using a pun
# > we ask for color as a option
# > we start game according to color chosen
# > if it is engine's move, engine move is played and replied
# > else user is asked for input
# > action can be 'castle' or 'two_squares'
# > after each move, check if game has ended
# > if it has, return an output string for that, and ask for another game with options

RESPONSES = {
    "result_win": "Congratulations! You have won the game. Thanks for playing.",
    "result_lose": "Oops, you were checkmated. Thanks for playing.",
    "result_draw": "The game has been drawn due to {reason}. Thanks for playing.",
}

mediator = Mediator()
PLAYERS = {}


@app.route("/", methods=["POST"])
def webhook():

    req = request.get_json()

    action = req["queryResult"].get("action")

    if action == "welcome":
        res = welcome(req)

    elif action == "choose_color":
        res = choose_color(req)

    elif action == "two_squares":
        res = two_squares(req)

    elif action == "castle":
        res = castle(req)

    elif action == "resign":
        res = resign(req)

    else:
        log.error(f"Bad request:\n{str(req)}")
        res = "bad request"

    return make_response(jsonify(res))


def welcome(req: Dict[str, Any]) -> Dict[str, Any]:

    session_id = get_session_by_req(req)

    if get_params_by_req(req)["color"]:
        color = get_params_by_req(req)["color"]
        return initialize_game_by_session_and_color(session_id, color)

    response_text = "Howdy! Which color would you like to choose?"
    options = [
        {
            "optionInfo": {"key": "white",},
            "description": "I like white!",
            "title": "White",
        },
        {
            "optionInfo": {"key": "black",},
            "description": "I'll choose black.",
            "title": "Black",
        },
        {
            "optionInfo": {"key": "random",},
            "description": "Choose randomly",
            "title": "Anything works!",
        },
    ]

    return generate_response_for_google_assistant(
        textToSpeech=response_text, options=options
    )


def choose_color(req: Dict[str, Any]) -> Dict[str, Any]:
    """Assign board and color to user"""

    # Get session id to store user data by key
    session_id = get_session_by_req(req)

    # Extract the key of chosen list item
    arguments = req["originalDetectIntentRequest"]["payload"]["inputs"]  # Is a list

    for each in arguments:
        if each["intent"] == "actions.intent.OPTION":
            arguments = each["arguments"]
            break

    # Look for chosen key
    for each in arguments:
        if each.get("name") == "OPTION":
            color = each["textValue"]
            break

    return initialize_game_by_session_and_color(session_id, color)


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
    player = PLAYERS[session_id]

    # Get LAN move
    lan = two_squares_and_piece_to_lan(board=player.board, squares=squares, piece=piece)

    # TODO: Store this reply somewhere
    if lan == "illegal move":
        return generate_response_for_google_assistant(
            textToSpeech=f"The move is not legal, please try once again. Just an FYI, you can say Show Board to see the current position on the board."
        )

    # Maybe recite the user's move back for confirmation?
    #
    # # Return speech form
    # speech = lan_to_speech(lan)

    # output = f'The move {speech} has been played.'

    # Play move on board
    mediator.play_lan(player, lan)

    game_result = get_result_comment(user=player)
    if game_result:
        # TODO: Display image of board when game is over
        # image = get_image(board)
        del PLAYERS[sessoin_id]  # Free up memory
        return generate_response_for_google_assistant(
            textToSpeech=game_result, expectUserResponse=False
        )

    # Play engine's move
    output = mediator.play_engine_move_and_get_speech(user=player)

    game_result = get_result_comment(user=player)
    if game_result:
        output = f"{output}. {game_result}"
        del PLAYERS[session_id]  # Free up memory
        return generate_response_for_google_assistant(
            textToSpeech=output, expectUserResponse=False
        )

    return generate_response_for_google_assistant(textToSpeech=output)


def castle(req: Dict[str, Any]) -> Dict[str, Any]:
    """When asked to castle, try playing the castles move"""

    session_id = get_session_by_req(req)
    user = PLAYERS[session_id]

    queryText = req["queryResult"]["queryText"]

    # Get lan of move
    lan = process_castle_by_querytext(board=user.board, queryText=queryText)

    if lan == "illegal move":
        return generate_response_for_google_assistant(
            textToSpeech=f"The move you are trying to play is not legal, please try once again. Just an FYI, you can say Show Board to see the current position on the board."
        )

    mediator.play_lan(user=user, lan=lan)

    game_result = get_result_comment(user=user)
    if game_result:
        # TODO: Display image of board when game is over
        # image = get_image(board)
        del PLAYERS[session_id]
        return generate_response_for_google_assistant(
            textToSpeech=game_result, expectUserResponse=False
        )

    # Play engine's move
    output = mediator.play_engine_move_and_get_speech(user=user)

    game_result = get_result_comment(user=user)
    if game_result:
        output = f"{output}. {game_result}"
        del PLAYERS[session_id]
        return generate_response_for_google_assistant(
            textToSpeech=output, expectUserResponse=False
        )

    return generate_response_for_google_assistant(textToSpeech=output)


def resign(req: Dict[str, Any]) -> Dict[str, Any]:
    """Delete the player from the database and return a conclusion response"""
    session_id = get_session_by_req(req)
    del PLAYERS[session_id]

    output = "GG! Thanks for playing."
    return generate_response_for_google_assistant(textToSpeech=output)


def initialize_game_by_session_and_color(session_id: str, color: str):
    """Initializes game given session and color"""
    # TODO: Store the PLAYERS data in a DB (sqlite for now, postgres later) instead of using a dict

    if color == "white":
        PLAYERS[session_id] = User(board=chess.Board(), color=chess.WHITE)

    elif color == "black":
        PLAYERS[session_id] = User(board=chess.Board(), color=chess.BLACK)

    else:
        chosen = random.choice([chess.WHITE, chess.BLACK])
        color = "white" if chosen else "black"
        PLAYERS[session_id] = User(board=chess.Board(), color=chosen)

    output = f"Okay! You are playing with the {color} pieces."

    # If player has white pieces
    if PLAYERS[session_id].color:
        output += " Your turn."

    else:
        # Play engine's move and append that move's speech to output
        speech = mediator.play_engine_move_and_get_speech(user=PLAYERS[session_id])
        output += f" My move is {speech}."

    return generate_response_for_google_assistant(textToSpeech=output)


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
        # User.color is True when it is chess.WHITE, and white is winner when result[-1] = '0'
        # If both are False, then player was black and black won
        # In the other case player lost

        output = RESPONSES["result_win"]

    # When user loses
    else:
        output = RESPONSES["result_lose"]

    return output


def main():

    PLAYERS = {}
    mediator = Mediator()

    app.run(host="0.0.0.0")


if __name__ == "__main__":
    main()
