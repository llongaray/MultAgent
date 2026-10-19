"""Concurrency limits, approval checkpoints, idempotency and audit events."""
from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from multagent.storage.sqlite import SQLiteStore


class SchedulerError(RuntimeError):
    pass


@dataclass(slots=True)
class ScheduledRun:
    id: str
    workspace_id: str
    budget_usd: float
    approval_required: bool
    approved: bool = False
    status: str = "queued"


class Scheduler:
    def __init__(self, store: SQLiteStore, *, max_concurrent: int = 2, maximum_budget_usd: float = 1.0) -> None:
        if max_concurrent < 1 or maximum_budget_usd < 0:
            raise ValueError("Invalid scheduling limits")
        self.store, self.max_concurrent, self.maximum_budget_usd = store, max_concurrent, maximum_budget_usd
        self._lock = RLock()
        self._jobs: dict[tuple[str, str], ScheduledRun] = {}

    def _get(self, workspace_id: str, run_id: str) -> ScheduledRun:
        key = (workspace_id, run_id)
        if key not in self._jobs:
            record = self.store.get("run", workspace_id, run_id)
            if "budget_usd" not in record:
                raise SchedulerError("Record does not belong to scheduler")
            self._jobs[key] = ScheduledRun(run_id, workspace_id, record["budget_usd"],
                record["approval_required"], record["approved"], record["state"])
        return self._jobs[key]

    def enqueue(self, *, workspace_id: str, run_id: str, budget_usd: float, approval_required: bool = False) -> ScheduledRun:
        if not workspace_id or not run_id or budget_usd < 0 or budget_usd > self.maximum_budget_usd:
            raise SchedulerError("Invalid run identity or over budget")
        with self._lock:
            key = workspace_id, run_id
            if key not in self._jobs:
                try:
                    return self._get(workspace_id, run_id)
                except KeyError:
                    pass
                job = ScheduledRun(run_id, workspace_id, budget_usd, approval_required)
                self._jobs[key] = job
                self._save(job)
            return self._jobs[key]

    def approve(self, workspace_id: str, run_id: str, principal_id: str) -> None:
        if not principal_id.strip():
            raise SchedulerError("Explicit approval identity required")
        with self._lock:
            job = self._get(workspace_id, run_id)
            if job.status != "queued":
                raise SchedulerError("Only queued runs may be approved")
            job.approved = True
            self._save(job)
            self.store.record_audit(workspace_id, principal_id, run_id, "approve-run")

    def start(self, workspace_id: str, run_id: str) -> bool:
        with self._lock:
            job = self._get(workspace_id, run_id)
            if job.status != "queued":
                return False  # idempotency / no double effects
            if job.approval_required and not job.approved:
                return False
            if sum(j.status == "running" for j in self._jobs.values()) >= self.max_concurrent:
                return False
            job.status = "running"
            self._save(job)
            return True

    def finish(self, workspace_id: str, run_id: str, *, success: bool) -> None:
        with self._lock:
            job = self._get(workspace_id, run_id)
            if job.status != "running":
                raise SchedulerError("Run is not active")
            job.status = "succeeded" if success else "failed"
            self._save(job)

    def cancel(self, workspace_id: str, run_id: str) -> None:
        with self._lock:
            job = self._get(workspace_id, run_id)
            if job.status in ("succeeded", "failed"):
                raise SchedulerError("Completed run cannot be cancelled")
            job.status = "cancelled"
            self._save(job)

    def _save(self, job: ScheduledRun) -> None:
        self.store.put("run", job.workspace_id, job.id,
            {"id": job.id, "workspace_id": job.workspace_id, "budget_usd": job.budget_usd,
             "approval_required": job.approval_required, "approved": job.approved, "state": job.status})
