import random
import string
from typing import Optional


def get_random_session_id(length: Optional[int] = 36) -> str:
    """Returns a randomly generated session id of given length (default 36)"""
    return "".join(
        random.choice(string.ascii_letters + string.digits) for i in range(36)
    )
