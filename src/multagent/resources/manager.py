"""Access checks at resource boundary; neither UI nor agent may bypass policy."""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from multagent.core.domain import PermissionGrant, Resource
from multagent.security.permissions import PolicyEngine
from multagent.storage.sqlite import SQLiteStore


class ResourceManager:
    def __init__(self, storage: SQLiteStore) -> None:
        self.storage = storage

    def register(self, resource: Resource) -> None:
        self.storage.put("resource", resource.workspace_id, resource.id, asdict(resource))

    def get(self, workspace_id: str, resource_id: str) -> Resource:
        return Resource(**self.storage.get("resource", workspace_id, resource_id))

    def grant(self, grant: PermissionGrant) -> None:
        self.get(grant.workspace_id, grant.resource_id)  # Cross-workspace denial
        data = asdict(grant)
        data["expires_at"] = grant.expires_at.isoformat() if grant.expires_at else None
        self.storage.put("grant", grant.workspace_id, grant.id, data)
        self.storage.record_audit(grant.workspace_id, grant.principal_id, grant.resource_id, "grant:" + grant.action)

    def revoke(self, workspace_id: str, grant_id: str) -> None:
        payload = self.storage.get("grant", workspace_id, grant_id)
        payload["revoked"] = True
        self.storage.put("grant", workspace_id, grant_id, payload)
        self.storage.record_audit(workspace_id, payload["principal_id"], payload["resource_id"], "revoke:" + payload["action"])

    def policy(self, workspace_id: str) -> PolicyEngine:
        grants = []
        for record in self.storage.list("grant", workspace_id):
            if record.get("expires_at"):
                record["expires_at"] = datetime.fromisoformat(record["expires_at"])
            grants.append(PermissionGrant(**record))
        return PolicyEngine(grants)

    def require(self, *, workspace_id: str, principal_id: str, resource_id: str, action: str) -> Resource:
        resource = self.get(workspace_id, resource_id)
        self.policy(workspace_id).require(workspace_id=workspace_id, principal_id=principal_id,
                                          resource=resource, action=action)
        self.storage.record_audit(workspace_id, principal_id, resource_id, "access:" + action)
        return resource
