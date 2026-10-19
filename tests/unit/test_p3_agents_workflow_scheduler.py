import pytest
from multagent.agents import AgentRegistry
from multagent.core.domain import Agent, DomainError, Run, RunState, Task, Team, Workflow
from multagent.core.orchestrator import CancelledRun, WorkflowEngine, WorkflowExecutionError
from multagent.core.scheduler import Scheduler, SchedulerError
from multagent.storage.sqlite import SQLiteStore, StoredRecordNotFound


def test_agent_crud_teams_and_supervisor_cycles(tmp_path):
    registry = AgentRegistry(SQLiteStore(tmp_path / "agents.db"))
    registry.save(Agent("a", "ws", "Supervisor", "deepseek", "model"))
    registry.save(Agent("b", "ws", "Coder", "grok", "model", supervisor_id="a"))
    registry.add_team(Team("team", "ws", "Team", ["a", "b"]))
    assert len(registry.teams("ws")) == 1
    with pytest.raises(DomainError):
        registry.save(Agent("a", "ws", "Supervisor", "deepseek", "model", supervisor_id="b"))
    with pytest.raises(DomainError):
        registry.delete("ws", "a")
    with pytest.raises(StoredRecordNotFound):
        registry.get("other", "b")


def test_workflow_dag_executes_and_records(tmp_path):
    engine = WorkflowEngine(SQLiteStore(tmp_path / "dag.db"))
    wf = Workflow("wf", "ws", "Engineering", ["1", "2", "3"])
    tasks = [Task("1", "ws", "wf", "planner", "plan"), Task("2", "ws", "wf", "coder", "code", depends_on=["1"]),
             Task("3", "ws", "wf", "reviewer", "review", depends_on=["2"])]
    engine.save(wf, tasks)
    called = []
    run = Run("run", "ws", "wf")
    result = engine.execute(run, wf, tasks, lambda task: (called.append(task.id) or "ok"))
    assert called == ["1", "2", "3"]
    assert len(result) == 3 and run.state == RunState.SUCCEEDED
    assert engine.store.get("run", "ws", "run")["state"] == "succeeded"
    tasks[0].depends_on = ["2"]
    with pytest.raises(DomainError):
        engine.validate(wf, tasks)


def test_cancel_and_human_approval(tmp_path):
    engine = WorkflowEngine(SQLiteStore(tmp_path / "approval.db"))
    wf = Workflow("wf", "ws", "Risky", ["1"])
    task = Task("1", "ws", "wf", "a", "delete production", requires_approval=True)
    with pytest.raises(WorkflowExecutionError):
        engine.execute(Run("r1", "ws", "wf"), wf, [task], lambda _: "should-not-run")
    with pytest.raises(CancelledRun):
        engine.execute(Run("r2", "ws", "wf"), wf, [task], lambda _: "no", approved_task_ids={"1"}, cancelled=lambda: True)
    assert engine.execute(Run("r3", "ws", "wf"), wf, [task], lambda _: "approved", approved_task_ids={"1"})[0].status == "succeeded"


def test_scheduler_limit_approval_and_idempotence(tmp_path):
    scheduler = Scheduler(SQLiteStore(tmp_path / "sched.db"), max_concurrent=1)
    a = scheduler.enqueue(workspace_id="ws", run_id="a", budget_usd=0.5, approval_required=True)
    assert scheduler.enqueue(workspace_id="ws", run_id="a", budget_usd=0.5) is a
    assert not scheduler.start("ws", "a")
    scheduler.approve("ws", "a", "human-user")
    assert scheduler.start("ws", "a")
    assert not scheduler.start("ws", "a")
    scheduler.enqueue(workspace_id="ws", run_id="b", budget_usd=0.5)
    assert not scheduler.start("ws", "b")
    scheduler.finish("ws", "a", success=True)
    assert scheduler.start("ws", "b")
    with pytest.raises(SchedulerError):
        scheduler.enqueue(workspace_id="ws", run_id="c", budget_usd=5.0)
