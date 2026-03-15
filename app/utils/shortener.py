import random
import string

ALPHABET = string.ascii_letters + string.digits


def generate_short_code(length: int = 6) -> str:
    return "".join(random.choice(ALPHABET) for _ in range(length))
