import sqlite3
from typing import Any, Dict, List, NamedTuple, Optional, Union

import chess
from flask import g


class User(NamedTuple):
    """Simple structure to store game and user data

    Initialize with
    ```python
    user = User(board=chess.Board(), color=chess.WHITE)  # For white pieces
    ```
    """

    board: chess.Board
    color: chess.Color


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
