"""Workspace-scoped agent CRUD with cycle detection and provider policy checks."""
from __future__ import annotations

from dataclasses import asdict
from multagent.core.domain import Agent, DomainError, Team
from multagent.core.router import Router
from multagent.storage.sqlite import SQLiteStore, StoredRecordNotFound


class AgentRegistry:
    def __init__(self, store: SQLiteStore, router: Router | None = None) -> None:
        self.store = store
        self.router = router

    def get(self, workspace_id: str, agent_id: str) -> Agent:
        return Agent(**self.store.get("agent", workspace_id, agent_id))

    def list(self, workspace_id: str) -> list[Agent]:
        return [Agent(**record) for record in self.store.list("agent", workspace_id)]

    def save(self, agent: Agent) -> None:
        if agent.supervisor_id:
            ancestors: set[str] = {agent.id}
            current = agent.supervisor_id
            while current:
                if current in ancestors:
                    raise DomainError("Supervisor graph contains a cycle")
                ancestors.add(current)
                try:
                    supervisor = self.get(agent.workspace_id, current)
                except StoredRecordNotFound as exc:
                    raise DomainError("Supervisor must exist in the same workspace") from exc
                current = supervisor.supervisor_id
        self.store.put("agent", agent.workspace_id, agent.id, asdict(agent))

    def delete(self, workspace_id: str, agent_id: str) -> None:
        if any(a.supervisor_id == agent_id for a in self.list(workspace_id)):
            raise DomainError("Reassign employees before deleting their supervisor")
        self.store.delete("agent", workspace_id, agent_id)

    def add_team(self, team: Team) -> None:
        for agent_id in team.agent_ids:
            self.get(team.workspace_id, agent_id)  # validates workspace membership
        self.store.put("team", team.workspace_id, team.id, asdict(team))

    def teams(self, workspace_id: str) -> list[Team]:
        return [Team(**record) for record in self.store.list("team", workspace_id)]

    def can_run(self, workspace_id: str, agent_id: str) -> bool:
        if self.router is None:
            return False  # fail closed until policy configured
        return self.router.permitted(self.get(workspace_id, agent_id))
