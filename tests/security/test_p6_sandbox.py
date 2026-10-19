from pathlib import Path
import pytest
from multagent.core.domain import PermissionGrant, Resource
from multagent.resources import ResourceManager
from multagent.resources.workspaces import GitWorkspace, WorkspaceBoundaryError
from multagent.storage.sqlite import SQLiteStore
from multagent.tools.shell import SandboxRunner, SandboxUnavailable, ShellDenied


def test_boundary_and_explicit_grants(tmp_path, monkeypatch):
    root=tmp_path/"root"; root.mkdir()
    repository=root/"project"; repository.mkdir()
    other=tmp_path/"escape"; other.mkdir()
    m=ResourceManager(SQLiteStore(tmp_path/"data.db"))
    m.register(Resource("g","ws","git",str(repository)))
    m.register(Resource("d","ws","directory",str(repository)))
    m.grant(PermissionGrant("read","ws","actor","g","read"))
    m.grant(PermissionGrant("execute","ws","actor","d","execute"))
    g=GitWorkspace(m,root)
    with pytest.raises(WorkspaceBoundaryError):g._within(other)
    with pytest.raises(PermissionError):g.worktree("ws","actor","g",root,"HEAD")
    with pytest.raises(PermissionError):g.status("other","actor","g")
    s=SandboxRunner(m)
    with pytest.raises(ShellDenied):s.run("ws","actor","d","python-version")
    with pytest.raises(ShellDenied):s.run("ws","actor","d","rm -rf",approved=True)
    import platform
    monkeypatch.setattr(platform,"system",lambda:"Windows")
    with pytest.raises(SandboxUnavailable):s.run("ws","actor","d","python-version",approved=True)


def test_symlink_escape(tmp_path):
    root=tmp_path/"allowed";root.mkdir();outside=tmp_path/"outside";outside.mkdir()
    link=root/"link"
    try:link.symlink_to(outside,target_is_directory=True)
    except OSError:pytest.skip("Symlinks unavailable")
    m=ResourceManager(SQLiteStore(tmp_path/"d.db"))
    with pytest.raises(WorkspaceBoundaryError):GitWorkspace(m,root)._within(link)
