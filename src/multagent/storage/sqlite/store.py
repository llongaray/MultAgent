"""Transactional per-workspace records with schema versioning and backups."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sqlite3
from threading import RLock
from typing import Any


class StoredRecordNotFound(KeyError):
    """No object exists inside the requested workspace."""


class SQLiteStore:
    SCHEMA_VERSION = 1
    KINDS = frozenset({"workspace", "agent", "team", "workflow", "task", "run", "resource", "grant", "integration"})

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        if str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        self.migrate()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.path), timeout=10, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=10000")
        conn.execute("PRAGMA foreign_keys=ON")
        if str(self.path) != ":memory:":
            conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def migrate(self) -> None:
        with self._lock, self._connect() as c:
            version = c.execute("PRAGMA user_version").fetchone()[0]
            if version > self.SCHEMA_VERSION:
                raise RuntimeError("Database schema is newer than this application")
            if version == 0:
                c.execute("BEGIN IMMEDIATE")
                try:
                    c.execute("""CREATE TABLE IF NOT EXISTS objects (
                        workspace_id TEXT NOT NULL,
                        kind TEXT NOT NULL,
                        id TEXT NOT NULL,
                        payload TEXT NOT NULL,
                        revision INTEGER NOT NULL DEFAULT 1,
                        PRIMARY KEY (workspace_id, kind, id))""")
                    c.execute("""CREATE INDEX IF NOT EXISTS ix_objects_workspace_kind
                        ON objects(workspace_id, kind)""")
                    c.execute("""CREATE TABLE IF NOT EXISTS audit (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        workspace_id TEXT NOT NULL,
                        principal_id TEXT NOT NULL,
                        resource_id TEXT NOT NULL,
                        action TEXT NOT NULL,
                        occurred_at TEXT NOT NULL DEFAULT (datetime('now')))""")
                    c.execute(f"PRAGMA user_version={self.SCHEMA_VERSION}")
                    c.execute("COMMIT")
                except Exception:
                    c.execute("ROLLBACK")
                    raise

    @staticmethod
    def _validate(kind: str, workspace_id: str, object_id: str) -> None:
        if kind not in SQLiteStore.KINDS or not workspace_id.strip() or not object_id.strip():
            raise ValueError("Invalid record kind or identifier")

    def put(self, kind: str, workspace_id: str, object_id: str, data: dict[str, Any]) -> None:
        self._validate(kind, workspace_id, object_id)
        if data.get("workspace_id") not in (None, workspace_id) or data.get("id") not in (None, object_id):
            raise ValueError("Record identity disagrees with the storage partition")
        payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        with self._lock, self._connect() as c:
            c.execute("BEGIN IMMEDIATE")
            try:
                c.execute("""INSERT INTO objects(workspace_id,kind,id,payload) VALUES(?,?,?,?)
                    ON CONFLICT(workspace_id,kind,id) DO UPDATE SET
                    payload=excluded.payload, revision=revision+1""",
                    (workspace_id, kind, object_id, payload))
                c.execute("COMMIT")
            except Exception:
                c.execute("ROLLBACK")
                raise

    def get(self, kind: str, workspace_id: str, object_id: str) -> dict[str, Any]:
        self._validate(kind, workspace_id, object_id)
        with self._connect() as c:
            row = c.execute("SELECT payload FROM objects WHERE workspace_id=? AND kind=? AND id=?",
                (workspace_id, kind, object_id)).fetchone()
        if row is None:
            raise StoredRecordNotFound(object_id)
        result: dict[str, Any] = json.loads(row["payload"])
        return result

    def list(self, kind: str, workspace_id: str) -> list[dict[str, Any]]:
        self._validate(kind, workspace_id, "_")
        with self._connect() as c:
            rows = c.execute("SELECT payload FROM objects WHERE workspace_id=? AND kind=? ORDER BY id",
                (workspace_id, kind)).fetchall()
        return [json.loads(row["payload"]) for row in rows]

    def delete(self, kind: str, workspace_id: str, object_id: str) -> bool:
        self._validate(kind, workspace_id, object_id)
        with self._lock, self._connect() as c:
            c.execute("BEGIN IMMEDIATE")
            try:
                count = c.execute("DELETE FROM objects WHERE workspace_id=? AND kind=? AND id=?",
                    (workspace_id, kind, object_id)).rowcount
                c.execute("COMMIT")
                return bool(count)
            except Exception:
                c.execute("ROLLBACK")
                raise

    def record_audit(self, workspace_id: str, principal_id: str, resource_id: str, action: str) -> None:
        if not all(isinstance(x, str) and x.strip() for x in (workspace_id, principal_id, resource_id, action)):
            raise ValueError("Audit fields must not be blank")
        with self._lock, self._connect() as c:
            c.execute("INSERT INTO audit(workspace_id,principal_id,resource_id,action) VALUES(?,?,?,?)",
                (workspace_id, principal_id, resource_id, action))

    def audit_log(self, workspace_id: str) -> list[dict[str, Any]]:
        with self._connect() as c:
            rows = c.execute("SELECT principal_id,resource_id,action,occurred_at FROM audit WHERE workspace_id=? ORDER BY id", (workspace_id,)).fetchall()
        return [dict(row) for row in rows]

    def backup(self, destination: str | Path) -> None:
        target = Path(destination)
        if target.resolve() == self.path.resolve():
            raise ValueError("Backup cannot overwrite active database")
        target.parent.mkdir(parents=True, exist_ok=True)
        with self._lock, self._connect() as source, sqlite3.connect(str(target)) as dest:
            source.backup(dest)
            if dest.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise RuntimeError("Backup integrity check failed")

    def schema_version(self) -> int:
        with self._connect() as c:
            return int(c.execute("PRAGMA user_version").fetchone()[0])
