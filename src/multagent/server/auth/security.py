"""Scrypt passwords, short-lived opaque sessions and CSRF for cookie-auth APIs."""
from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from dataclasses import dataclass


def hash_password(password: str, salt: bytes | None = None) -> str:
    if len(password) < 12:
        raise ValueError("Administrator password must have at least 12 characters")
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return salt.hex() + ":" + digest.hex()


def verify_password(password: str, encoded: str) -> bool:
    try:
        salt_hex, target = encoded.split(":", 1)
        salt = bytes.fromhex(salt_hex)
        actual = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
        return hmac.compare_digest(actual, bytes.fromhex(target))
    except (ValueError, TypeError):
        return False


@dataclass(frozen=True)
class Session:
    csrf_token: str
    expires_at: float


class SessionStore:
    def __init__(self, ttl_seconds: int = 3600) -> None:
        self._ttl = ttl_seconds
        self._sessions: dict[str, Session] = {}

    def create(self) -> tuple[str, Session]:
        token = secrets.token_urlsafe(32)
        session = Session(secrets.token_urlsafe(24), time.time() + self._ttl)
        self._sessions[hashlib.sha256(token.encode()).hexdigest()] = session
        return token, session

    def lookup(self, token: str | None) -> Session | None:
        if not token:
            return None
        fingerprint = hashlib.sha256(token.encode()).hexdigest()
        record = self._sessions.get(fingerprint)
        if record is None:
            return None
        if record.expires_at <= time.time():
            self._sessions.pop(fingerprint, None)
            return None
        return record

    def revoke(self, token: str | None) -> None:
        if token:
            self._sessions.pop(hashlib.sha256(token.encode()).hexdigest(), None)
