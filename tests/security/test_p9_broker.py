"""Broker tests prove denial on missing grants, forgery, expiry and replay."""
from dataclasses import replace
import pytest
from multagent.core.domain import Resource, PermissionGrant
from multagent.resources import ResourceManager
from multagent.storage.sqlite import SQLiteStore
from multagent.security.privilege_broker import BrokerDenied, PrivilegeBroker


def test_admin_tickets_require_real_grant_and_one_time_hmac(tmp_path):
    resources = ResourceManager(SQLiteStore(tmp_path / "audit.db"))
    resources.register(Resource("service", "ws", "tool",
                                "admin://restart-service/multagent-server"))
    actions = []
    now = [100]
    broker = PrivilegeBroker(resources, b"X" * 32,
                             executor=lambda operation, target: actions.append((operation, target)),
                             clock=lambda: now[0])
    with pytest.raises(BrokerDenied):
        broker.issue(workspace_id="ws", principal_id="worker", resource_id="service",
                     operation="restart-service", target="multagent-server")
    with pytest.raises((PermissionError, KeyError)):
        broker.issue(workspace_id="ws", principal_id="worker", resource_id="service",
                     operation="restart-service", target="multagent-server", human_confirmed=True)
    resources.grant(PermissionGrant("g1", "ws", "worker", "service", "execute"))
    ticket = broker.issue(workspace_id="ws", principal_id="worker", resource_id="service",
                          operation="restart-service", target="multagent-server", human_confirmed=True)
    with pytest.raises(BrokerDenied):
        broker.execute(replace(ticket, target="other"))
    broker.execute(ticket)
    assert actions == [("restart-service", "multagent-server")]
    with pytest.raises(BrokerDenied):
        broker.execute(ticket)
    expired = broker.issue(workspace_id="ws", principal_id="worker", resource_id="service",
                           operation="restart-service", target="multagent-server",
                           human_confirmed=True, ttl_seconds=1)
    now[0] = 102
    with pytest.raises(BrokerDenied):
        broker.execute(expired)
    log = resources.storage.audit_log("ws")
    assert any(entry["action"] == "admin-succeeded" for entry in log)
    assert not any("secret" in str(entry) for entry in log)


def test_no_generic_root_command_or_unsafe_key(tmp_path):
    resources = ResourceManager(SQLiteStore(tmp_path / "audit.db"))
    with pytest.raises(ValueError):
        PrivilegeBroker(resources, b"short")
    broker = PrivilegeBroker(resources, b"Y" * 32, executor=lambda a, b: None)
    with pytest.raises(BrokerDenied):
        broker.issue(workspace_id="ws", principal_id="worker", resource_id="unknown",
                     operation="shell", target="rm -rf /", human_confirmed=True)


def test_ipc_requires_private_socket_parent(tmp_path):
    from multagent.security.privilege_broker import BrokerIPC
    resources = ResourceManager(SQLiteStore(tmp_path / "audit.db"))
    broker = PrivilegeBroker(resources, b"Y" * 32, executor=lambda a, b: None)
    with pytest.raises(ValueError):
        BrokerIPC(broker, str(tmp_path / "endpoint.sock"), b"x")
    if __import__("os").name != "nt":
        # Pytest temporary dir permissions vary by host; explicitly make it public.
        exposed = tmp_path / "public"
        exposed.mkdir(mode=0o777)
        exposed.chmod(0o777)
        with pytest.raises(PermissionError):
            BrokerIPC(broker, str(exposed / "endpoint.sock"), b"Z" * 32)
