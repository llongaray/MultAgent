from pathlib import Path
import pytest
from multagent.core.domain import PermissionGrant, Resource
from multagent.resources import ResourceManager
from multagent.security.permissions import AccessDenied
from multagent.storage.sqlite import SQLiteStore, StoredRecordNotFound


def test_migrations_storage_partition_backup(tmp_path: Path):
    db = SQLiteStore(tmp_path / "a.db")
    assert db.schema_version() == 1
    db.migrate()
    db.put("agent", "w1", "x", {"id": "x", "workspace_id": "w1", "name": "Alpha"})
    db.put("agent", "w2", "x", {"id": "x", "workspace_id": "w2", "name": "Beta"})
    assert db.get("agent", "w1", "x")["name"] == "Alpha"
    assert db.get("agent", "w2", "x")["name"] == "Beta"
    with pytest.raises(StoredRecordNotFound):
        db.get("agent", "w3", "x")
    with pytest.raises(ValueError):
        db.put("agent", "w1", "x", {"workspace_id": "w2"})
    db.backup(tmp_path / "copy.db")
    copy = SQLiteStore(tmp_path / "copy.db")
    assert copy.get("agent", "w1", "x")["name"] == "Alpha"
    assert db.delete("agent", "w1", "x")
    assert db.list("agent", "w1") == []


def test_grant_persistence_revoke_isolation(tmp_path: Path):
    mgr = ResourceManager(SQLiteStore(tmp_path / "resources.db"))
    mgr.register(Resource("repo", "tenant-a", "git", "https://example.test/repo"))
    mgr.grant(PermissionGrant("g", "tenant-a", "worker", "repo", "read"))
    assert mgr.require(workspace_id="tenant-a", principal_id="worker", resource_id="repo", action="read").id == "repo"
    with pytest.raises((AccessDenied, StoredRecordNotFound)):
        mgr.require(workspace_id="tenant-b", principal_id="worker", resource_id="repo", action="read")
    with pytest.raises(AccessDenied):
        mgr.require(workspace_id="tenant-a", principal_id="worker", resource_id="repo", action="write")
    mgr.revoke("tenant-a", "g")
    with pytest.raises(AccessDenied):
        mgr.require(workspace_id="tenant-a", principal_id="worker", resource_id="repo", action="read")
    assert [x["action"] for x in mgr.storage.audit_log("tenant-a")] == ["grant:read", "access:read", "revoke:read"]
