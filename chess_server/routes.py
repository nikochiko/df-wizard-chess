import os

from flask import current_app as app
from flask import Blueprint, make_response, jsonify, request, send_file
from werkzeug.exceptions import BadRequest, NotFound

from chess_server.main import (
    welcome,
    choose_color,
    two_squares,
    castle,
    resign,
)


webhook_bp = Blueprint("webhook_bp", __name__)

log = app.logger


@webhook_bp.route("/webhook", methods=["POST"])
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


@webhook_bp.route("/webhook/images/boards/<session_id>", methods=["GET"])
def png_image(session_id):

    img_path = os.path.join(app.config["IMG_DIR"], f"{session_id}.png")

    if os.path.exists(img_path):
        return send_file(img_path, mimetype="images/png")
    else:
        return NotFound()