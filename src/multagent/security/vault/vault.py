"""OS keyring and explicit password-unlocked AES-GCM server vaults."""
from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import secrets
from typing import Protocol


class VaultUnavailable(RuntimeError):
    """Required secure credential backend is unavailable; fail closed."""


def vault_ref(name: str) -> str:
    if not name or any(c in name for c in ":/\\"):
        raise ValueError("Use a simple non-empty credential name")
    return "vault:" + name


class CredentialVault(Protocol):
    def put(self, name: str, secret: str) -> str: ...
    def get(self, reference: str) -> str: ...
    def delete(self, reference: str) -> None: ...


def _parse_ref(reference: str) -> str:
    if not reference.startswith("vault:"):
        raise ValueError("Only vault references are accepted")
    name = reference[6:]
    if vault_ref(name) != reference:
        raise ValueError("Malformed credential reference")
    return name


class KeyringVault:
    """Windows Credential Manager / macOS Keychain / Linux Secret Service when available."""

    def __init__(self, service: str = "MultAgent") -> None:
        try:
            import keyring
            from keyring.backends.fail import Keyring as FailKeyring
            from keyring.backends.null import Keyring as NullKeyring
        except ImportError as exc:
            raise VaultUnavailable("Install the optional keyring dependency") from exc
        backend = keyring.get_keyring()
        if isinstance(backend, (FailKeyring, NullKeyring)) or backend.priority <= 0:
            raise VaultUnavailable("No secure OS credential store is available")
        self._ring = keyring
        self._service = service

    def put(self, name: str, secret: str) -> str:
        reference = vault_ref(name)
        if not isinstance(secret, str) or not secret:
            raise ValueError("Secret may not be blank")
        self._ring.set_password(self._service, name, secret)
        return reference

    def get(self, reference: str) -> str:
        secret = self._ring.get_password(self._service, _parse_ref(reference))
        if secret is None:
            raise KeyError("Credential not present")
        return str(secret)

    def delete(self, reference: str) -> None:
        self._ring.delete_password(self._service, _parse_ref(reference))


class EncryptedFileVault:
    """AES-256-GCM vault with scrypt password KDF; no stored plaintext or password."""

    def __init__(self, path: str | Path, password: str) -> None:
        if not isinstance(password, str) or len(password) < 12:
            raise ValueError("Vault unlock password must have at least 12 characters")
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            from cryptography.exceptions import InvalidTag
        except ImportError as exc:
            raise VaultUnavailable("Install the optional cryptography dependency") from exc
        self._aes = AESGCM
        self._invalid_tag = InvalidTag
        self.path = Path(path)
        self._password = password.encode("utf-8")
        self._values: dict[str, str] = {}
        if self.path.exists():
            self._values = self._read()

    def _key(self, salt: bytes) -> bytes:
        return hashlib.scrypt(self._password, salt=salt, n=2**14, r=8, p=1, dklen=32)

    def _read(self) -> dict[str, str]:
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        if raw.get("version") != 1:
            raise VaultUnavailable("Unsupported vault format")
        try:
            salt, nonce, ciphertext = (base64.b64decode(raw[k], validate=True) for k in ("salt", "nonce", "data"))
            values: dict[str, str] = json.loads(self._aes(self._key(salt)).decrypt(nonce, ciphertext, b"multagent:v1"))
        except (ValueError, KeyError, TypeError, self._invalid_tag) as exc:
            raise VaultUnavailable("Vault could not be unlocked (wrong password or corrupted)") from exc
        return values

    def _write(self) -> None:
        salt, nonce = secrets.token_bytes(16), secrets.token_bytes(12)
        ciphertext = self._aes(self._key(salt)).encrypt(nonce, json.dumps(self._values).encode(), b"multagent:v1")
        values = {"version": 1, "salt": base64.b64encode(salt).decode(),
                  "nonce": base64.b64encode(nonce).decode(), "data": base64.b64encode(ciphertext).decode()}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_name(self.path.name + "." + secrets.token_hex(6) + ".tmp")
        try:
            descriptor = os.open(tmp, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                json.dump(values, stream)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(tmp, self.path)
        finally:
            if tmp.exists():
                tmp.unlink()

    def put(self, name: str, secret: str) -> str:
        reference = vault_ref(name)
        if not secret:
            raise ValueError("Secret may not be blank")
        self._values[name] = secret
        self._write()
        return reference

    def get(self, reference: str) -> str:
        return self._values[_parse_ref(reference)]

    def delete(self, reference: str) -> None:
        name = _parse_ref(reference)
        del self._values[name]
        self._write()
