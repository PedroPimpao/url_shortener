import hashlib
import hmac
import secrets
import string

from ..config import settings


def generate_otp() -> str:
    return "".join(secrets.choice(string.digits) for _ in range(6))


def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)


def hash_otp(otp: str) -> str:
    return hmac.new(
        settings.SECRET_KEY.encode(),
        otp.encode(),
        hashlib.sha256,
    ).hexdigest()


def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def otp_matches(otp: str, expected_hash: str) -> bool:
    return hmac.compare_digest(hash_otp(otp), expected_hash)
