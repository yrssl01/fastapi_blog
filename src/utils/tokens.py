from datetime import timedelta, timezone, datetime
import jwt
from jwt import InvalidTokenError
from src.core.config import settings
from src.schemas.auth import TokenType


def generate_token(email: str, token_type: TokenType) -> str:
    delta = timedelta(minutes=token_type.expiry_minutes)
    now = datetime.now(timezone.utc)
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email, "type": token_type.value},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_user_token(token: str, expected_type: TokenType) -> str | None:
    try:
        decoded_token = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        if decoded_token.get("type") != expected_type.value:
            raise ValueError("Invalid token type")
        return str(decoded_token["sub"])
    except InvalidTokenError:
        return None