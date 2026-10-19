"""Short-lived, signed one-shot requests for strictly enumerated admin operations.

Only a trusted human-facing local host should call issue(). Agents never receive
the signing secret or a direct privilege escalation path.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import hmac
import json
import secrets
import subprocess
import os
from pathlib import Path
import platform
from threading import RLock
import time
from typing import Callable

from multagent.resources import ResourceManager


class BrokerDenied(PermissionError):
    """Privilege approval absent, invalid, expired or already consumed."""


@dataclass(frozen=True, slots=True)
class BrokerTicket:
    workspace_id: str
    principal_id: str
    resource_id: str
    operation: str
    target: str
    nonce: str
    expires_at: int
    mac: str


# Deliberately fixed argument vectors: caller cannot supply executable or flags.
OPERATIONS: dict[tuple[str, str], dict[str, tuple[str, ...]]] = {
    ("restart-service", "multagent-server"): {
        "Linux": ("/usr/bin/systemctl", "restart", "multagent-server.service"),
        "Windows": ("sc.exe", "stop", "MultAgentServer"),
    },
}


def _canonical(fields: dict[str, object]) -> bytes:
    return json.dumps(fields, sort_keys=True, separators=(",", ":")).encode("utf-8")


def os_elevated() -> bool:
    if platform.system() == "Linux":
        return hasattr(os, "geteuid") and os.geteuid() == 0
    if platform.system() == "Windows":
        try:
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except (AttributeError, OSError):
            return False
    return False


def execute_admin_operation(operation: str, target: str) -> None:
    """Only usable by an administrator-owned helper, never by the unprivileged LLM."""
    try:
        command = OPERATIONS[(operation, target)][platform.system()]
    except KeyError as exc:
        raise BrokerDenied("This administrative action is not allowlisted on this OS") from exc
    if not os_elevated():
        raise BrokerDenied("Run the helper under a separately approved OS-admin account")
    if platform.system() == "Windows":
        # Resolve sc.exe through the kernel, never from a potentially modified PATH.
        import ctypes
        destination = ctypes.create_unicode_buffer(32768)
        if not ctypes.windll.kernel32.GetSystemDirectoryW(destination, 32768):
            raise BrokerDenied("Cannot verify Windows system directory")
        system_sc = str(Path(destination.value) / "sc.exe")
        command_sequence = [(system_sc, "stop", "MultAgentServer"),
                            (system_sc, "start", "MultAgentServer")]
    else:
        command_sequence = [command]
    for args in command_sequence:
        try:
            result = subprocess.run(args, shell=False, timeout=30, capture_output=True,
                                    check=False, cwd=str(Path.home()))
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise BrokerDenied("Administrative helper failed") from exc
        if result.returncode:
            raise BrokerDenied("Administrative action failed; inspect host OS service logs")


class PrivilegeBroker:
    """Verifies MAC, TTL, single use and the exact allowlisted operation."""

    def __init__(self, resources: ResourceManager, signing_key: bytes,
                 *, executor: Callable[[str, str], None] = execute_admin_operation,
                 clock: Callable[[], float] = time.time):
        if len(signing_key) < 32:
            raise ValueError("Broker signing key must be at least 256 bits")
        self._key = signing_key
        self._used: set[str] = set()
        self._lock = RLock()
        self._clock = clock
        self._executor = executor
        self.resources = resources

    def _signature(self, fields: dict[str, object]) -> str:
        return hmac.new(self._key, _canonical(fields), hashlib.sha256).hexdigest()

    def issue(self, *, workspace_id: str, principal_id: str, resource_id: str,
              operation: str, target: str, human_confirmed: bool = False,
              ttl_seconds: int = 30) -> BrokerTicket:
        if not human_confirmed:
            raise BrokerDenied("Explicit human confirmation is required for every request")
        if not 1 <= ttl_seconds <= 60:
            raise BrokerDenied("Tickets must expire within 60 seconds")
        if (operation, target) not in OPERATIONS:
            raise BrokerDenied("Administrative action or target not allowlisted")
        resource = self.resources.require(workspace_id=workspace_id, principal_id=principal_id,
                                          resource_id=resource_id, action="execute")
        if resource.kind != "tool" or resource.locator != f"admin://{operation}/{target}":
            raise BrokerDenied("Administrator resource is not explicitly granted")
        fields: dict[str, object] = dict(workspace_id=workspace_id, principal_id=principal_id,
                resource_id=resource_id, operation=operation, target=target,
                nonce=secrets.token_hex(24), expires_at=int(self._clock()) + ttl_seconds)
        ticket = BrokerTicket(**fields, mac=self._signature(fields))
        self.resources.storage.record_audit(workspace_id, principal_id, resource_id, "admin-approved")
        return ticket

    def execute(self, ticket: BrokerTicket) -> None:
        fields = asdict(ticket)
        provided = fields.pop("mac")
        signature = self._signature(fields)
        if not hmac.compare_digest(provided, signature):
            raise BrokerDenied("Invalid authenticated broker ticket")
        if not int(self._clock()) < ticket.expires_at:
            raise BrokerDenied("Broker ticket expired")
        if (ticket.operation, ticket.target) not in OPERATIONS:
            raise BrokerDenied("Administrative operation not allowlisted")
        # Recheck persisted grant: revoking it invalidates even freshly signed tickets.
        resource = self.resources.require(workspace_id=ticket.workspace_id,
                principal_id=ticket.principal_id, resource_id=ticket.resource_id, action="execute")
        if resource.kind != "tool" or resource.locator != f"admin://{ticket.operation}/{ticket.target}":
            raise BrokerDenied("Administrative resource no longer authorized")
        with self._lock:
            key = "privilege-broker:" + ticket.nonce
            if ticket.nonce in self._used:
                raise BrokerDenied("Replay of one-time broker ticket")
            try:
                self.resources.storage.get("run", ticket.workspace_id, key)
            except KeyError:
                pass
            else:
                raise BrokerDenied("Ticket previously consumed in another broker session")
            # Persist before executing: a service restart must not resurrect this ticket.
            self.resources.storage.put("run", ticket.workspace_id, key,
                {"id": key, "workspace_id": ticket.workspace_id, "state": "consumed"})
            self._used.add(ticket.nonce)
        self.resources.storage.record_audit(ticket.workspace_id, ticket.principal_id,
                                             ticket.resource_id, "admin-attempt")
        try:
            self._executor(ticket.operation, ticket.target)
        except Exception:
            self.resources.storage.record_audit(ticket.workspace_id, ticket.principal_id,
                                                 ticket.resource_id, "admin-failed")
            raise
        self.resources.storage.record_audit(ticket.workspace_id, ticket.principal_id,
                                             ticket.resource_id, "admin-succeeded")
