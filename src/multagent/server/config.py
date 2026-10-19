"""Safe, persistent server configuration; no plaintext administrator secret."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any
from multagent.server.auth.security import hash_password


def config_path() -> Path:
    return Path(os.environ.get("MULTAGENT_SERVER_CONFIG") or
        (Path.home() / ".config" / "multagent" / "server.json"))


def initialize(path: Path, password: str, port: int = 8765, bind: str = "127.0.0.1", *,
               tls_cert: str | None = None, tls_key: str | None = None,
               allowed_hosts: tuple[str, ...] = ()) -> None:
    if not 1024 <= port <= 65535:
        raise ValueError("Unprivileged port required: 1024..65535")
    if bind not in ("127.0.0.1", "::1") and not (tls_cert and tls_key and allowed_hosts):
        raise ValueError("External bind requires TLS certificate/key and allowed hosts")
    if any(not re.fullmatch(r"[A-Za-z0-9.:-]{1,253}", host) for host in allowed_hosts):
        raise ValueError("Invalid Host allowlist entry")
    if (tls_cert is None) != (tls_key is None):
        raise ValueError("Both TLS certificate and key are required")
    if path.exists():
        raise FileExistsError("Server already initialized; config will not be overwritten")
    payload: dict[str, Any] = {
        "version": 1, "bind": bind, "port": port, "password_hash": hash_password(password),
        "tls_cert": tls_cert, "tls_key": tls_key, "allowed_hosts": list(allowed_hosts),
        "data_dir": str(path.parent / "data"),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        path.unlink(missing_ok=True)
        raise


def load(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("version") != 1 or not raw.get("password_hash"):
        raise ValueError("Unrecognized or invalid server configuration")
    bind = str(raw.get("bind", ""))
    port = int(raw.get("port", 0))
    if bind not in ("127.0.0.1", "::1") and not (raw.get("tls_cert") and raw.get("tls_key") and raw.get("allowed_hosts")):
        raise ValueError("Refusing to expose Server HTTP without TLS")
    if not 1024 <= port <= 65535:
        raise ValueError("Invalid port")
    return raw
