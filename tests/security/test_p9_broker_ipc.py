"""Run a real authenticated Unix socket test without privileged subprocesses."""
import os
import threading
import time

import pytest

from multagent.core.domain import PermissionGrant, Resource
from multagent.resources import ResourceManager
from multagent.storage.sqlite import SQLiteStore
from multagent.security.privilege_broker import BrokerDenied, BrokerIPC, PrivilegeBroker


@pytest.mark.skipif(os.name == "nt", reason="AF_UNIX test uses POSIX socket permissions")
def test_authenticated_socket_executes_once(tmp_path):
    private = tmp_path / "private"
    private.mkdir(mode=0o700)
    private.chmod(0o700)
    resources = ResourceManager(SQLiteStore(tmp_path / "audit.db"))
    resources.register(Resource("srv", "ws", "tool", "admin://restart-service/multagent-server"))
    resources.grant(PermissionGrant("g", "ws", "human", "srv", "execute"))
    called = []
    broker = PrivilegeBroker(resources, b"A" * 32,
                             executor=lambda op, target: called.append((op, target)))
    ticket = broker.issue(workspace_id="ws", principal_id="human", resource_id="srv",
                          operation="restart-service", target="multagent-server",
                          human_confirmed=True)
    address = str(private / "broker.sock")
    ipc = BrokerIPC(broker, address, b"B" * 32)
    server = threading.Thread(target=ipc.serve_once, daemon=True)
    server.start()
    for _ in range(200):
        if os.path.exists(address):
            break
        time.sleep(0.01)
    assert os.path.exists(address), "IPC listener did not start"
    assert ipc.submit(ticket) is True
    server.join(timeout=5)
    assert not server.is_alive()
    assert called == [("restart-service", "multagent-server")]
    # A restarted broker must not accept a signed one-time ticket already consumed.
    restarted = PrivilegeBroker(resources, b"A" * 32,
                                 executor=lambda op, target: called.append((op, target)))
    with pytest.raises(BrokerDenied):
        restarted.execute(ticket)


def test_grant_revoke_invalidates_signed_ticket(tmp_path):
    resources = ResourceManager(SQLiteStore(tmp_path / "audit.db"))
    resources.register(Resource("srv", "ws", "tool", "admin://restart-service/multagent-server"))
    resources.grant(PermissionGrant("g", "ws", "human", "srv", "execute"))
    broker = PrivilegeBroker(resources, b"C" * 32, executor=lambda a, b: None)
    ticket = broker.issue(workspace_id="ws", principal_id="human", resource_id="srv",
                          operation="restart-service", target="multagent-server",
                          human_confirmed=True)
    resources.revoke("ws", "g")
    with pytest.raises(PermissionError):
        broker.execute(ticket)
