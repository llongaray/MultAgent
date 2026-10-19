"""Permission-scoped local Git operations without arbitrary shell execution."""
from __future__ import annotations
import os
from pathlib import Path
import re
import subprocess
from uuid import uuid4
from multagent.resources import ResourceManager

class WorkspaceBoundaryError(PermissionError):
    pass

class GitWorkspace:
    def __init__(self, manager: ResourceManager, allowed_root: Path) -> None:
        self.manager, self.root = manager, Path(allowed_root).resolve(strict=True)
        if not self.root.is_dir():
            raise ValueError("Expected existing directory")

    def _within(self, path: str | Path) -> Path:
        real = Path(path).resolve(strict=True)
        if not real.is_relative_to(self.root):
            raise WorkspaceBoundaryError("Git path escapes authorized boundary")
        return real

    def _repo(self, ws: str, actor: str, resource: str, action: str) -> Path:
        grant = self.manager.require(workspace_id=ws, principal_id=actor,resource_id=resource,action=action)
        if grant.kind != "git":
            raise WorkspaceBoundaryError("A Git resource grant is required")
        repo = self._within(grant.locator)
        if not repo.is_dir() or not (repo / ".git").exists():
            raise ValueError("Not an initialized local repository")
        return repo

    @staticmethod
    def _run(repo: Path, *args: str) -> str:
        env = {"PATH": os.environ.get("PATH", ""), "GIT_CONFIG_NOSYSTEM": "1",
               "GIT_CONFIG_GLOBAL": os.devnull, "GIT_TERMINAL_PROMPT": "0",
               "GIT_NO_REPLACE_OBJECTS": "1", "GIT_OPTIONAL_LOCKS": "0", "GIT_PAGER": "cat"}
        try:
            r = subprocess.run(["git", "-c", "core.hooksPath="+os.devnull,
                 "-c", "diff.external=", "-C", str(repo), *args], capture_output=True,
                 text=True, check=False, timeout=30, env=env)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise RuntimeError("Git operation unavailable") from exc
        if r.returncode or len(r.stdout) > 1_000_000:
            raise RuntimeError("Git operation rejected")
        return r.stdout

    def status(self, workspace_id: str, principal_id: str, resource_id: str) -> str:
        repo = self._repo(workspace_id, principal_id, resource_id, "read")
        return self._run(repo, "status", "--porcelain=v1", "--untracked-files=no")

    def diff(self, workspace_id: str, principal_id: str, resource_id: str) -> str:
        repo = self._repo(workspace_id, principal_id, resource_id, "read")
        return self._run(repo, "diff", "--no-ext-diff", "--no-textconv", "--")

    def worktree(self, workspace_id: str, principal_id: str, resource_id: str,
                 target_dir: Path, ref: str, *, approved: bool = False) -> Path:
        if not approved:
            raise PermissionError("Human write approval required")
        repo = self._repo(workspace_id, principal_id, resource_id, "write")
        target = self._within(target_dir)
        if not target.is_dir() or not re.fullmatch("[A-Za-z0-9._/-]{1,120}",ref) or ".." in ref or ref.startswith("-"):
            raise ValueError("Invalid target or ref")
        sha = self._run(repo, "rev-parse", "--verify", ref+"^{commit}").strip()
        if not re.fullmatch("[0-9a-f]{40,64}", sha):
            raise ValueError("Untrusted revision")
        destination = target / ("ma-"+uuid4().hex)
        self._run(repo, "worktree", "add", "--detach", str(destination), sha)
        return destination
