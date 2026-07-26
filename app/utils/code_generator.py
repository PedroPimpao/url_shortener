import secrets
import string

BASE62 = string.digits + string.ascii_uppercase + string.ascii_lowercase

def generate_short_code(length: int = 8) -> str:
    return "".join(secrets.choice(BASE62) for _ in range(length))