"""Authenticated local IPC using OS pipes/sockets, distinct from signed admin tickets.

This is a transport building block, not an auto-installed elevated service.
Separate randomly generated transport auth key from the ticket signing key.
"""
from __future__ import annotations

from dataclasses import asdict
import json
from multiprocessing.connection import Listener, Client
import os
from pathlib import Path
import stat
from typing import Any

from .broker import BrokerTicket, PrivilegeBroker


class BrokerIPC:
    def __init__(self, broker: PrivilegeBroker, address: str, transport_key: bytes):
        if len(transport_key) < 32:
            raise ValueError("IPC transport key must be 256 bits")
        self.broker = broker
        self.address = address
        self.key = transport_key
        self.family = "AF_PIPE" if os.name == "nt" else "AF_UNIX"
        if self.family == "AF_UNIX":
            parent = Path(address).parent.resolve(strict=True)
            if not parent.is_dir() or parent.stat().st_mode & (stat.S_IRWXG | stat.S_IRWXO):
                raise PermissionError("Unix socket parent must be private (0700)")
            if Path(address).exists() or Path(address).is_symlink():
                raise FileExistsError("IPC endpoint must not already exist")
        elif not address.startswith("\\\\.\\pipe\\MultAgent-"):
            raise ValueError("Windows IPC endpoint must be a private MultAgent pipe name")

    def serve_once(self) -> None:
        """An authorized host service may call this from its own isolated process."""
        with Listener(self.address, family=self.family, authkey=self.key) as listener:
            if self.family == "AF_UNIX":
                os.chmod(self.address, 0o600)
            try:
                with listener.accept() as connection:
                    try:
                        payload: dict[str, Any] = json.loads(connection.recv_bytes(8192))
                        if set(payload) != set(BrokerTicket.__dataclass_fields__):
                            raise ValueError("Unexpected IPC fields")
                        self.broker.execute(BrokerTicket(**payload))
                        connection.send_bytes(b'{"ok":true}')
                    except (ValueError, TypeError, KeyError, PermissionError):
                        connection.send_bytes(b'{"ok":false}')
            finally:
                if self.family == "AF_UNIX":
                    Path(self.address).unlink(missing_ok=True)

    def submit(self, ticket: BrokerTicket) -> bool:
        """The transport key proves IPC client membership; signed ticket proves approval."""
        with Client(self.address, family=self.family, authkey=self.key) as connection:
            connection.send_bytes(json.dumps(asdict(ticket)).encode("utf-8"))
            return bool(json.loads(connection.recv_bytes(8192)).get("ok"))
