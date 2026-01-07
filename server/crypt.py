from __future__ import annotations

import time
from typing import Optional

import jwt

from .config import JWT_EXPIRATION_SECONDS, JWT_SECRET_KEY


__all__ = ("encode_jwt", "decode_jwt")


def encode_jwt(body: str) -> str:
    payload = {
        "sub": body,
        "iat": int(time.time()),
        "exp": int(time.time()) + JWT_EXPIRATION_SECONDS,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="ES256")


def decode_jwt(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["ES256"])
        return payload["sub"]
    except jwt.PyJWTError:
        return None
