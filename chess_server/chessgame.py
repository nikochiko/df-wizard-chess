import logging
from typing import Optional

import chess.engine
from flask import current_app

from chess_server.utils import get_user, update_user, lan_to_speech

logger = logging.getLogger(__name__)


class Mediator:
    def activate_engine(self, engine_path: Optional[str] = None):

        # If engine path is not given, check if it is mentioned in config file
        if not engine_path:
            engine_path = current_app.config["ENGINE_PATH"]

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
            update_user(session_id, user.board)
            return True
        except ValueError:  # Illegal, invalid or ambiguous move
            return False
