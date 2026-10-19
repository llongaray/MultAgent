"""Topological task execution, trace capture and strict approvals."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable
from multagent.core.domain import DomainError, Run, RunState, Task, TaskState, Workflow
from multagent.storage.sqlite import SQLiteStore


class CancelledRun(RuntimeError):
    pass


class WorkflowExecutionError(RuntimeError):
    pass


@dataclass(slots=True)
class ExecutionTrace:
    task_id: str
    agent_id: str
    status: str
    message: str = ""


class WorkflowEngine:
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    @staticmethod
    def validate(workflow: Workflow, tasks: list[Task]) -> list[Task]:
        if len(set(t.id for t in tasks)) != len(tasks):
            raise DomainError("Duplicate task IDs")
        by_id = {t.id: t for t in tasks}
        if set(workflow.task_ids) != set(by_id):
            raise DomainError("Workflow tasks do not match task set")
        if any(t.workspace_id != workflow.workspace_id or t.workflow_id != workflow.id for t in tasks):
            raise DomainError("Cross-workspace task is not allowed")
        pending = set(by_id)
        visited: set[str] = set()
        result: list[Task] = []
        while pending:
            ready = sorted(tid for tid in pending if set(by_id[tid].depends_on).issubset(visited))
            if not ready:
                raise DomainError("Cyclic or missing task dependencies")
            for tid in ready:
                pending.remove(tid)
                visited.add(tid)
                result.append(by_id[tid])
        return result

    def save(self, workflow: Workflow, tasks: list[Task]) -> None:
        self.validate(workflow, tasks)
        self.store.put("workflow", workflow.workspace_id, workflow.id,
                       {"id": workflow.id, "workspace_id": workflow.workspace_id, "name": workflow.name, "task_ids": workflow.task_ids})
        for task in tasks:
            self.store.put("task", task.workspace_id, task.id, self._task_record(task))

    @staticmethod
    def _task_record(task: Task) -> dict[str, object]:
        return {"id": task.id, "workspace_id": task.workspace_id, "workflow_id": task.workflow_id,
                "agent_id": task.agent_id, "prompt": task.prompt, "depends_on": task.depends_on,
                "state": task.state.value, "result": task.result, "requires_approval": task.requires_approval}

    def execute(self, run: Run, workflow: Workflow, tasks: list[Task],
                dispatch: Callable[[Task], str], *, approved_task_ids: set[str] | None = None,
                cancelled: Callable[[], bool] | None = None) -> list[ExecutionTrace]:
        if run.workspace_id != workflow.workspace_id or run.workflow_id != workflow.id:
            raise DomainError("Run/workflow partition mismatch")
        ordered = self.validate(workflow, tasks)
        approved = approved_task_ids or set()
        traces: list[ExecutionTrace] = []
        run.state = RunState.RUNNING
        self.store.put("run", run.workspace_id, run.id,
                       {"id": run.id, "workspace_id": run.workspace_id, "workflow_id": run.workflow_id, "state": run.state.value})
        try:
            for task in ordered:
                if cancelled and cancelled():
                    task.state = TaskState.CANCELLED
                    raise CancelledRun("Execution cancelled by operator")
                if task.requires_approval and task.id not in approved:
                    task.state = TaskState.WAITING_APPROVAL
                    self.store.put("task", task.workspace_id, task.id, self._task_record(task))
                    raise WorkflowExecutionError("Approval required before executing task")
                task.state = TaskState.RUNNING
                self.store.put("task", task.workspace_id, task.id, self._task_record(task))
                try:
                    result = dispatch(task)  # caller injects permission-checked dispatcher
                    if not isinstance(result, str):
                        raise TypeError("Task dispatcher must return a string")
                    task.result = result
                    task.state = TaskState.SUCCEEDED
                    traces.append(ExecutionTrace(task.id, task.agent_id, "succeeded"))
                except Exception:
                    task.state = TaskState.FAILED
                    traces.append(ExecutionTrace(task.id, task.agent_id, "failed"))
                    raise
                finally:
                    self.store.put("task", task.workspace_id, task.id, self._task_record(task))
            run.state = RunState.SUCCEEDED
            return traces
        except CancelledRun:
            run.state = RunState.CANCELLED
            raise
        except Exception:
            run.state = RunState.FAILED
            raise
        finally:
            self.store.put("run", run.workspace_id, run.id,
                           {"id": run.id, "workspace_id": run.workspace_id, "workflow_id": run.workflow_id,
                            "state": run.state.value, "results": {t.id: t.result for t in tasks if t.result is not None}})
