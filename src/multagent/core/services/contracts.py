"""Dependency-inversion contracts. Adapters can use SQLite, mocks or another DB."""
from __future__ import annotations

from typing import Protocol
from multagent.core.domain import Agent, Run, Task, Workflow, Workspace


class ServiceError(Exception):
    """Service/application-level error (do not expose secrets in messages)."""


class NotFoundError(ServiceError):
    """Item not found within the authorized workspace."""


class ConflictError(ServiceError):
    """Attempt to overwrite conflicting state."""


class WorkspaceService(Protocol):
    def create(self, workspace: Workspace) -> None: ...
    def get(self, workspace_id: str) -> Workspace: ...


class AgentService(Protocol):
    def save(self, agent: Agent) -> None: ...
    def get(self, workspace_id: str, agent_id: str) -> Agent: ...
    def list(self, workspace_id: str) -> list[Agent]: ...
    def delete(self, workspace_id: str, agent_id: str) -> None: ...


class WorkflowService(Protocol):
    def save(self, workflow: Workflow, tasks: list[Task]) -> None: ...
    def get(self, workspace_id: str, workflow_id: str) -> Workflow: ...
    def tasks(self, workspace_id: str, workflow_id: str) -> list[Task]: ...


class RunService(Protocol):
    def create(self, run: Run) -> None: ...
    def get(self, workspace_id: str, run_id: str) -> Run: ...
    def save(self, run: Run) -> None: ...
