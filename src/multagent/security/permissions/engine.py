"""Minimal privilege by default; no supervisor privilege inheritance."""
from __future__ import annotations

from datetime import datetime, timezone
from multagent.core.domain import PermissionGrant, Resource


class AccessDenied(PermissionError):
    """Access denied. Does not disclose confidential resource details."""


class PolicyEngine:
    def __init__(self, grants: list[PermissionGrant] | None = None) -> None:
        self._grants: dict[str, PermissionGrant] = {g.id: g for g in (grants or [])}

    def add_grant(self, grant: PermissionGrant) -> None:
        self._grants[grant.id] = grant

    def revoke(self, grant_id: str) -> None:
        grant = self._grants.get(grant_id)
        if grant is not None:
            grant.revoked = True

    def allows(
        self, *, workspace_id: str, principal_id: str, resource: Resource,
        action: str, now: datetime | None = None,
    ) -> bool:
        if resource.workspace_id != workspace_id:
            return False
        timestamp = now or datetime.now(timezone.utc)
        return any(
            g.workspace_id == workspace_id
            and g.principal_id == principal_id
            and g.resource_id == resource.id
            and g.action == action
            and g.is_active(timestamp)
            for g in self._grants.values()
        )

    def require(self, *, workspace_id: str, principal_id: str, resource: Resource, action: str) -> None:
        if not self.allows(workspace_id=workspace_id, principal_id=principal_id, resource=resource, action=action):
            raise AccessDenied("Permission denied")

    def delegation_intersection(
        self, *, workspace_id: str, supervisor_id: str, agent_id: str,
        resources: list[Resource], actions: list[str],
    ) -> set[tuple[str, str]]:
        """Only permissions possessed by BOTH supervisor and worker can be delegated."""
        return {
            (resource.id, action)
            for resource in resources
            for action in actions
            if self.allows(workspace_id=workspace_id, principal_id=supervisor_id, resource=resource, action=action)
            and self.allows(workspace_id=workspace_id, principal_id=agent_id, resource=resource, action=action)
        }
