from datetime import datetime
import pytest
from multagent.core.domain import (Agent, DomainError, IntegrationInstance, PermissionGrant, Run, Task, TaskState, Team)
from multagent.core.services import AgentService, RunService, WorkflowService, WorkspaceService


def test_entities_and_states():
    agent = Agent("a1", "ws1", "Planner", "deepseek", "model-id")
    assert agent.enabled
    assert Task("t1", "ws1", "wf1", "a1", "Plan task").state == TaskState.PENDING
    assert Run("r1", "ws1", "wf1").state.value == "pending"
    assert Team("team1", "ws1", "Equipe", ["a1"]).agent_ids == ["a1"]


@pytest.mark.parametrize("factory", [
    lambda: Agent("a1", "ws1", "Bad", "unknown", "model"),
    lambda: Agent("a1", "ws1", "Self", "grok", "model", supervisor_id="a1"),
    lambda: Team("t", "ws", "Team", ["x", "x"]),
    lambda: Task("a", "w", "f", "ag", "prompt", depends_on=["a"]),
    lambda: PermissionGrant("g", "w", "a", "r", "read", datetime(2025, 1, 1)),
    lambda: IntegrationInstance("i", "w", "deepseek", "plaintext-secret"),
])
def test_invalid_state_rejected(factory):
    with pytest.raises(DomainError):
        factory()


def test_contracts_are_protocols():
    assert hasattr(AgentService, "save")
    assert hasattr(RunService, "create")
    assert hasattr(WorkflowService, "tasks")
    assert hasattr(WorkspaceService, "get")
