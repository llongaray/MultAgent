"""Import only pinned GitHub/GitLab public Markdown skills into quarantine."""
from __future__ import annotations
import hashlib
from pathlib import Path
import re
from urllib.parse import quote
from typing import Any
from multagent.resources import ResourceManager

class SkillDenied(PermissionError):pass

class SkillImporter:
    def __init__(self,resources:ResourceManager,quarantine_dir:Path,http_factory:Any=None)->None:
        self.resources=resources
        self.root=Path(quarantine_dir)
        self.http_factory=http_factory

    def import_skill(self, *, ws:str,actor:str,rid:str,provider:str,revision:str,path:str,
                     sha256:str,approved_network:bool=False)->Path:
        if not approved_network:raise SkillDenied("Network import needs authorization")
        resource=self.resources.require(workspace_id=ws,principal_id=actor,resource_id=rid,action="read")
        if resource.kind!="git":raise SkillDenied("Git repository grant required")
        match=re.fullmatch(r"https://(github.com|gitlab.com)/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)",resource.locator)
        if not match or provider not in ("github","gitlab") or match.group(1)!=(provider+".com"):
            raise SkillDenied("Untrusted skill repository origin")
        if not re.fullmatch(r"[0-9a-f]{40}",revision) or not re.fullmatch(r"[a-zA-Z0-9_./-]{1,150}",path) or ".." in Path(path).parts or not path.endswith(".md"):
            raise SkillDenied("Skill revision or path is not immutable and safe")
        if not re.fullmatch("[0-9a-fA-F]{64}",sha256):raise ValueError("Missing pinned content checksum")
        owner,repo=match.group(2),match.group(3)
        url=(f"https://raw.githubusercontent.com/{owner}/{repo}/{revision}/{quote(path)}" if provider=="github"
             else f"https://gitlab.com/{owner}/{repo}/-/raw/{revision}/{quote(path)}")
        if self.http_factory:client=self.http_factory(timeout=20)
        else:
            try:import httpx
            except ImportError as exc:raise RuntimeError("Install multagent[forges]") from exc
            client=httpx.Client(timeout=20,follow_redirects=False)
        with client as session:
            reply=session.get(url)
            if reply.status_code!=200 or len(reply.content)>1_000_000:
                raise SkillDenied("Source not accessible within download limits")
            data=reply.content
        if hashlib.sha256(data).hexdigest().lower()!=sha256.lower():
            raise SkillDenied("Skill checksum mismatch")
        target=self.root/ws/(provider+"-"+owner+"-"+repo)/(revision+"-"+sha256.lower()+".md")
        target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists():target.write_bytes(data)
        # No imported skill is executed or given tools automatically.
        return target
