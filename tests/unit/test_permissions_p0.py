from datetime import datetime, timedelta, timezone
import pytest
from multagent.core.domain import PermissionGrant, Resource
from multagent.security.permissions import AccessDenied, PolicyEngine


def test_deny_by_default_and_workspace_isolation():
    engine = PolicyEngine()
    a = Resource("file1", "w1", "directory", "/tmp/a")
    assert not engine.allows(workspace_id="w1", principal_id="worker", resource=a, action="read")
    engine.add_grant(PermissionGrant("g1", "w1", "worker", "file1", "read"))
    assert engine.allows(workspace_id="w1", principal_id="worker", resource=a, action="read")
    assert not engine.allows(workspace_id="w2", principal_id="worker", resource=a, action="read")
    assert not engine.allows(workspace_id="w1", principal_id="other", resource=a, action="read")
    assert not engine.allows(workspace_id="w1", principal_id="worker", resource=a, action="write")
    with pytest.raises(AccessDenied):
        engine.require(workspace_id="w1", principal_id="other", resource=a, action="read")
    engine.revoke("g1")
    assert not engine.allows(workspace_id="w1", principal_id="worker", resource=a, action="read")


def test_expiration_and_no_supervisor_escalation():
    a = Resource("r1", "ws", "tool", "search")
    old = datetime.now(timezone.utc) - timedelta(seconds=1)
    engine = PolicyEngine([
        PermissionGrant("a", "ws", "boss", "r1", "execute"),
        PermissionGrant("b", "ws", "worker", "r1", "execute", expires_at=old),
    ])
    assert engine.delegation_intersection(workspace_id="ws", supervisor_id="boss", agent_id="worker", resources=[a], actions=["execute"]) == set()
    engine.add_grant(PermissionGrant("c", "ws", "worker", "r1", "execute"))
    assert engine.delegation_intersection(workspace_id="ws", supervisor_id="boss", agent_id="worker", resources=[a], actions=["execute"]) == {("r1", "execute")}
