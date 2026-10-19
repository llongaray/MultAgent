"""Validated entities shared by Desktop and Server; no framework dependency."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class DomainError(ValueError):
    """Invalid domain state or cross-workspace operation."""


def required(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DomainError(f"{name} must not be blank")
    return value.strip()


class TaskState(str, Enum):
    PENDING = "pending"
    WAITING_APPROVAL = "waiting_approval"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RunState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class Workspace:
    id: str
    name: str

    def __post_init__(self) -> None:
        required(self.id, "workspace.id")
        required(self.name, "workspace.name")


@dataclass(slots=True)
class Agent:
    id: str
    workspace_id: str
    name: str
    provider: str
    model: str
    role: str = "worker"
    supervisor_id: str | None = None
    enabled: bool = True
    instructions: str = ""

    def __post_init__(self) -> None:
        for key in ("id", "workspace_id", "name", "provider", "model", "role"):
            required(getattr(self, key), f"agent.{key}")
        if self.provider not in {"deepseek", "grok"}:
            raise DomainError("Unsupported provider")
        if self.supervisor_id == self.id:
            raise DomainError("Agent cannot supervise itself")


@dataclass(slots=True)
class Team:
    id: str
    workspace_id: str
    name: str
    agent_ids: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        required(self.id, "team.id")
        required(self.workspace_id, "team.workspace_id")
        required(self.name, "team.name")
        if len(set(self.agent_ids)) != len(self.agent_ids):
            raise DomainError("Team has duplicate agents")


@dataclass(slots=True)
class Workflow:
    id: str
    workspace_id: str
    name: str
    task_ids: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        required(self.id, "workflow.id")
        required(self.workspace_id, "workflow.workspace_id")
        required(self.name, "workflow.name")
        if len(set(self.task_ids)) != len(self.task_ids):
            raise DomainError("Duplicate tasks in workflow")


@dataclass(slots=True)
class Task:
    id: str
    workspace_id: str
    workflow_id: str
    agent_id: str
    prompt: str
    depends_on: list[str] = field(default_factory=list)
    state: TaskState = TaskState.PENDING
    result: str | None = None
    requires_approval: bool = False

    def __post_init__(self) -> None:
        for key in ("id", "workspace_id", "workflow_id", "agent_id", "prompt"):
            required(getattr(self, key), f"task.{key}")
        if self.id in self.depends_on or len(set(self.depends_on)) != len(self.depends_on):
            raise DomainError("Invalid task dependencies")


@dataclass(slots=True)
class Resource:
    id: str
    workspace_id: str
    kind: str
    locator: str

    def __post_init__(self) -> None:
        for key in ("id", "workspace_id", "kind", "locator"):
            required(getattr(self, key), f"resource.{key}")
        if self.kind not in {"directory", "git", "ssh", "app", "tool"}:
            raise DomainError("Invalid resource kind")


@dataclass(slots=True)
class PermissionGrant:
    id: str
    workspace_id: str
    principal_id: str
    resource_id: str
    action: str
    expires_at: datetime | None = None
    revoked: bool = False

    def __post_init__(self) -> None:
        for key in ("id", "workspace_id", "principal_id", "resource_id", "action"):
            required(getattr(self, key), f"grant.{key}")
        if self.expires_at is not None and (
            self.expires_at.tzinfo is None or self.expires_at.utcoffset() is None
        ):
            raise DomainError("Expiration must be timezone aware")

    def is_active(self, now: datetime | None = None) -> bool:
        timestamp = now or datetime.now(timezone.utc)
        return not self.revoked and (self.expires_at is None or timestamp < self.expires_at)


@dataclass(slots=True)
class IntegrationInstance:
    id: str
    workspace_id: str
    provider: str
    credential_ref: str  # Vault reference; NEVER API key itself
    enabled: bool = True

    def __post_init__(self) -> None:
        for key in ("id", "workspace_id", "provider", "credential_ref"):
            required(getattr(self, key), f"integration.{key}")
        if self.provider not in {"deepseek", "grok"}:
            raise DomainError("Unsupported provider")
        if not self.credential_ref.startswith("vault:"):
            raise DomainError("credential_ref must be a vault reference, not a secret")


@dataclass(slots=True)
class Run:
    id: str
    workspace_id: str
    workflow_id: str
    state: RunState = RunState.PENDING
    results: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        required(self.id, "run.id")
        required(self.workspace_id, "run.workspace_id")
        required(self.workflow_id, "run.workflow_id")
