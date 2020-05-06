from flask import request, make_response, jsonify
from flask import current_app as app
from werkzeug.exceptions import BadRequest

from chess_server.main import (
    welcome,
    choose_color,
    two_squares,
    castle,
    resign,
)

log = app.logger


@app.route("/webhook", methods=["POST"])
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
        raise BadRequest(f"Unknown intent action: {action}")

    return make_response(jsonify(res))
