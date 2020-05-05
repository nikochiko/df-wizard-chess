import logging
import os
import sqlite3
from typing import Any, Dict, List, NamedTuple, Optional, Union

import chess
import chess.svg
from cairosvg import svg2png
from flask import g, current_app

logger = logging.getLogger(__name__)


class User(NamedTuple):
    """Simple structure to store game and user data

    Initialize with
    ```python
    user = User(board=chess.Board(), color=chess.WHITE)  # For white pieces
    ```
    """

    board: chess.Board
    color: chess.Color


class Image(NamedTuple):
    url: str
    accessibilityText: str
    width: Optional[int] = None
    height: Optional[int] = None

    def make_image(self) -> Dict[str, Any]:
        image = {}

        image["url"] = self.url
        image["accessibilityText"] = self.accessibilityText

        if self.width:
            image["width"] = self.width

        if self.height:
            image["height"] = self.height


class BasicCard(NamedTuple):
    """Basic card for response.

    Note: At least one of image and formattedText is required.
    """
    # One is required:
    image: Optional[Image] = None
    formattedText: Optional[str] = None

    # All optional:
    title: Optional[str] = None
    subtitle: Optional[str] = None

    def make_card(self) -> Dict[str, Any]:
        card = {}

        if self.image:
            card["image"] = self.image.make_image()

        if self.formattedText:
            card["formattedText"] = self.formattedText

        if self.title is not None:
            card["title"] = self.title

        if self.subtitle is not None:
            card["subtitle"] = self.subtitle

        return card


def get_session_by_req(req: Dict[str, Any]) -> str:
    """Get Session ID by DialogFlow request"""
    return req.get("session").split("/")[-1]


def get_params_by_req(req: Dict[str, Any]) -> Dict[str, str]:
    """Get parameters by DialogFlow request"""
    return req.get("queryResult").get("parameters")


def get_response_template_for_google(
    options: Optional[bool] = False,
) -> Dict[str, Any]:
    """Return template for response for Google Assistant"""

    template = {
        "payload": {
            "google": {
                "expectUserResponse": True,
                "richResponse": {
                    "items": [{"simpleResponse": {"textToSpeech": ""}}],
                },
            }
        }
    }

    if options:
        template["payload"]["google"]["systemIntent"] = {
            "intent": "actions.intent.OPTION",
            "data": {
                "@type": "type.googleapis.com/"
                "google.actions.v2.OptionValueSpec",
                "listSelect": {"items": []},
            },
        }

    return template


def get_response_for_google(
    textToSpeech: str,
    expectUserResponse: Optional[bool] = True,
    basicCard: Optional[BasicCard] = None,
    options: Optional[List[Dict[str, Union[str, Dict[str, str]]]]] = None,
) -> Dict[str, Any]:
    """
    Generate response from given data.


    For example,
    ```python
    generate_response_for_google_assistant(
        textToSpeech='This is a simple response')
    ```
    would return:


    ```json
    {
        "payload": {
            "google": {
                "expectUserResponse": true,
                    "richResponse": {
                        "items": [
                        {
                            "simpleResponse": {
                                "textToSpeech": "this is a simple response"
                            }
                        }
                    ]
                }
            }
        }
    }
    ```

    And, for a more complex example:
    ```python
    options = [
        {
            'optionInfo': {'key': 'first title key'},
            'description': 'first description',
            'image': {
                'url': '/assistant/images/badges/img.png',
                'accessibilityText': 'first alt',
            },
            'title': 'first title',
        },
        {
            'optionInfo': {'key': 'second'},
            'description': 'second description',
            'image': {
                'url': 'https://test-url/image2.png',
                'accessibilityText': 'second alt',
            },
            'title': 'second title',
        },
    ]

    generate_response_for_google_assistant(
        textToSpeech='Choose a item',
        options=options)
    ```

    should give:

    ```json
    {
      "payload": {
        "google": {
          "expectUserResponse": true,
          "richResponse": {
            "items": [
              {
                "simpleResponse": {
                  "textToSpeech": "Choose a item"
                }
              }
            ]
          },
          "systemIntent": {
            "intent": "actions.intent.OPTION",
            "data": {
              "@type": "type.googleapis.com/google.actions.v2.OptionValueSpec",
              "listSelect": {
                "title": "Hello",
                "items": [
                  {
                    "optionInfo": {
                      "key": "first title key"
                    },
                    "description": "first description",
                    "image": {
                      "url": "/assistant/images/badges/img.png",
                      "accessibilityText": "first alt"
                    },
                    "title": "first title"
                  },
                  {
                    "optionInfo": {
                      "key": "second"
                    },
                    "description": "second description",
                    "image": {
                      "url": "https://test-url/image2.png",
                      "accessibilityText": "second alt"
                    },
                    "title": "second title"
                  }
                ]
              }
            }
          }
        }
      }
    }
    ```

    Note: Setting the `expectUserResponse` param to False will mark the end of
    conversation
    """

    # Get template for response
    template = get_response_template_for_google(options=bool(options))

    # Modify the dict as per the arguments
    template["payload"]["google"]["expectUserResponse"] = expectUserResponse
    template["payload"]["google"]["richResponse"]["items"][0][
        "simpleResponse"
    ]["textToSpeech"] = textToSpeech

    # If options List is given
    if options:
        print(template)
        template["payload"]["google"]["systemIntent"]["data"]["listSelect"][
            "items"
        ] = options

    # If basicCard is given
    if basicCard:
        card = basicCard.make_card()
        template["payload"]["google"]["richResponse"]["items"].append(card)

    # Return DICT
    return template


def exists_in_db(session_id: str) -> bool:
    """Returns boolean indicating whether the entry exists in db"""

    c = g.db.cursor()

    res = c.execute("SELECT * FROM users WHERE session_id=?", (session_id,))

    # res.fetchone() is None if entry does not exist
    return res.fetchone() is not None


def create_user(session_id: str, board: chess.Board, color: chess.Color):
    """Creates a new entry in table with given data"""

    if "db" not in g:
        raise Exception("Database not found.")

    c = g.db.cursor()

    fen = board.fen()

    try:
        c.execute(
            "INSERT INTO users (session_id, fen, color) VALUES (?,?,?)",
            (session_id, fen, color),
        )
    except sqlite3.IntegrityError:
        if exists_in_db(session_id):
            raise Exception(f"Entry with key {session_id} already exists.")

        raise

    g.db.commit()


def get_user(session_id: str) -> User:
    """Gets the required user from database when its session id is given"""
    if "db" not in g:
        raise Exception("Database not found.")

    # Get cursor on the database
    c = g.db.cursor()

    # Find user by session_id
    res = c.execute("SELECT * FROM users WHERE session_id=?", (session_id,))

    # Get first (and only) result
    res = res.fetchone()

    if res is None:
        # When entry does not exist
        raise Exception("Entry not found.")

    board = chess.Board(res["fen"])
    color = chess.WHITE if res["color"] else chess.BLACK

    return User(board=board, color=color)


def update_user(session_id: str, board: chess.Board):
    """Updates an existing entry for user with session id session_id"""
    if "db" not in g:
        raise Exception("Database not found.")

    c = g.db.cursor()

    fen = board.fen()

    if exists_in_db(session_id):
        c.execute(
            "UPDATE users SET fen=? WHERE session_id=?", (fen, session_id)
        )

    else:
        # Throw entry not found exception
        raise Exception("Entry not found.")

    g.db.commit()


def delete_user(session_id: str):
    """Deletes a user entry from db"""
    if "db" not in g:
        raise Exception("Database not found.")

    c = g.db.cursor()

    c.execute("DELETE FROM users WHERE session_id=?", (session_id,))

    g.db.commit()


def save_board_as_png(imgkey: str, board: chess.Board) -> str:
    """Render the PNG of a board, save it on disk and return the location.

    imgkey argument should be the identifier for the image like session id.
    """
    img_dir = current_app.config["IMG_DIR"]

    try:
        # Get last move on the board
        lastmove = board.peek()
    except IndexError:
        # This is the first move
        lastmove = None

    # Render SVG
    svg = str(chess.svg.board(board, lastmove=lastmove))

    # Path to png
    pngfile = os.path.join(img_dir, f"{imgkey}.png")

    # Perform conversion
    try:
        svg2png(bytestring=svg, write_to=pngfile)
        return pngfile
    except Exception as exc:
        # Log error and raise
        logger.error(
            f"Unable to process image. Failed with error:\n{str(exc)}")
        raise
