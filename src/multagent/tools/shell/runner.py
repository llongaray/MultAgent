"""OS sandboxed read-only command allowlist; no host shell fallback."""
from __future__ import annotations
import os
from pathlib import Path
import platform
import shutil
import subprocess
from dataclasses import dataclass
from multagent.resources import ResourceManager

class ShellDenied(PermissionError):
    pass

class SandboxUnavailable(RuntimeError):
    pass

@dataclass(frozen=True)
class RunResult:
    code: int
    stdout: str
    stderr: str

class SandboxRunner:
    COMMANDS = {"git-version": ("/usr/bin/git", "--version"), "python-version": ("/usr/bin/python3", "--version")}

    def __init__(self, manager: ResourceManager, timeout: int = 10) -> None:
        if not 1 <= timeout <= 60:
            raise ValueError("Invalid runtime limit")
        self.manager, self.timeout = manager, timeout

    def run(self, workspace_id: str, principal_id: str, resource_id: str,
            command: str, *, approved: bool = False) -> RunResult:
        if not approved or command not in self.COMMANDS:
            raise ShellDenied("Command not explicitly authorized and allowlisted")
        resource = self.manager.require(workspace_id=workspace_id, principal_id=principal_id,
                                        resource_id=resource_id, action="execute")
        if resource.kind != "directory":
            raise ShellDenied("Directory grant required")
        path = Path(resource.locator).resolve(strict=True)
        if not path.is_dir():
            raise ShellDenied("Invalid working directory")
        if platform.system() != "Linux" or shutil.which("bwrap") is None:
            raise SandboxUnavailable("OS sandbox unavailable; refused host execution")
        mounts: list[str] = []
        for entry in ("/usr", "/bin", "/lib", "/lib64", "/etc"):
            if Path(entry).exists():
                mounts.extend(["--ro-bind", entry, entry])
        args = ["bwrap", "--unshare-all", "--die-with-parent", "--new-session",
                "--clearenv", "--setenv", "HOME", "/tmp", "--setenv", "PATH", "/usr/bin:/bin",
                *mounts, "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
                "--ro-bind", str(path), "/work", "--chdir", "/work", "--", *self.COMMANDS[command]]
        try:
            process = subprocess.run(args, capture_output=True, text=True, timeout=self.timeout,
                                     env={"PATH": os.environ.get("PATH", "")}, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise SandboxUnavailable("Sandbox execution failed or timed out") from exc
        return RunResult(process.returncode, process.stdout[:50000], process.stderr[:50000])
