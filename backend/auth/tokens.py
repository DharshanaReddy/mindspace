"""
Anonymous session token management using JWT.
Users get a persistent anonymous identity without creating an account.
"""

import secrets
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from ..config import get_settings

settings = get_settings()


def generate_session_token() -> str:
    """Generate a cryptographically secure random session token."""
    return secrets.token_hex(32)


def create_jwt(session_token: str) -> str:
    payload = {
        "sub": session_token,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expire_hours),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_jwt(token: str) -> str | None:
    """Decode JWT and return session token, or None if invalid."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload.get("sub")
    except JWTError:
        return None
