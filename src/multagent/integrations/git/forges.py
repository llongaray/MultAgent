"""GitHub/GitLab/Bitbucket REST adapters without arbitrary URLs or writes."""
from __future__ import annotations
import re
import base64
from urllib.parse import quote
from typing import Any
from multagent.resources import ResourceManager

class ForgeDenied(PermissionError):
    pass

class RemoteForge:
    ENDPOINTS={"github":("github.com","https://api.github.com"),
      "gitlab":("gitlab.com","https://gitlab.com/api/v4"),
      "bitbucket":("bitbucket.org","https://api.bitbucket.org/2.0")}

    def __init__(self, kind: str, resources: ResourceManager, vault: Any, credential_ref: str,
                 *, http_factory: Any=None) -> None:
        if kind not in self.ENDPOINTS or not credential_ref.startswith("vault:"):
            raise ValueError("Invalid forge or vault credential")
        self.kind,self.resources,self.vault,self.credential_ref,self.http_factory=kind,resources,vault,credential_ref,http_factory

    def _resource(self, ws: str, principal: str, rid: str, action: str) -> str:
        r=self.resources.require(workspace_id=ws,principal_id=principal,resource_id=rid,action=action)
        host=self.ENDPOINTS[self.kind][0]
        if r.kind!="git":
            raise ForgeDenied("Git repository grant required")
        match=re.fullmatch(r"https://"+re.escape(host)+r"/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?",r.locator)
        if not match:
            raise ForgeDenied("Repository host/path not authorized")
        return match.group(1)+"/"+match.group(2)

    def _request(self, verb: str, route: str, payload: dict[str,Any]|None=None)->Any:
        key=self.vault.get(self.credential_ref)
        if not key:
            raise ForgeDenied("Missing credential")
        if self.http_factory:
            client=self.http_factory(timeout=20)
        else:
            try:
                import httpx
            except ImportError as exc:
                raise RuntimeError("Install multagent[forges]") from exc
            client=httpx.Client(timeout=20,follow_redirects=False)
        headers={"Accept":"application/json"}
        if self.kind=="gitlab":
            headers["PRIVATE-TOKEN"]=key
        else:
            headers["Authorization"]="Bearer "+key
        with client as session:
            reply=session.request(verb,self.ENDPOINTS[self.kind][1]+route,headers=headers,json=payload)
            if reply.status_code>=400:
                raise RuntimeError("Forge returned HTTP "+str(reply.status_code))
            return reply.json()

    def branches(self, ws: str, principal: str, rid: str, *, approved_network: bool=False)->Any:
        if not approved_network:
            raise ForgeDenied("Remote read not approved")
        repo=self._resource(ws,principal,rid,"read")
        route=("/repos/"+repo+"/branches" if self.kind=="github" else
              "/projects/"+quote(repo,safe="")+"/repository/branches" if self.kind=="gitlab" else
              "/repositories/"+repo+"/refs/branches")
        return self._request("GET",route)

    def create_pr(self, ws: str, principal: str, rid: str, title: str, head: str, base: str,
                  *, approved_write: bool=False)->Any:
        if not approved_write:
            raise ForgeDenied("Write requires explicit user approval")
        repo=self._resource(ws,principal,rid,"write")
        if not title.strip() or len(title)>200:
            raise ValueError("Invalid PR title")
        for value in (head,base):
            if not re.fullmatch(r"[A-Za-z0-9._/-]{1,128}",value) or ".." in value or value.startswith("-"):
                raise ValueError("Invalid branch")
        if self.kind=="github":
            return self._request("POST","/repos/"+repo+"/pulls",{"title":title,"head":head,"base":base})
        if self.kind=="gitlab":
            return self._request("POST","/projects/"+quote(repo,safe="")+"/merge_requests",
                                 {"title":title,"source_branch":head,"target_branch":base})
        return self._request("POST","/repositories/"+repo+"/pullrequests",
                             {"title":title,"source":{"branch":{"name":head}},
                              "destination":{"branch":{"name":base}}})

    def issues(self, ws: str, principal: str, rid: str, *, approved_network: bool = False) -> Any:
        """Fetch only issues visible within the explicitly scoped repository."""
        if not approved_network:
            raise ForgeDenied("Network read requires approval")
        repo = self._resource(ws, principal, rid, "read")
        if self.kind == "github":
            endpoint = "/repos/" + repo + "/issues"
        elif self.kind == "gitlab":
            endpoint = "/projects/" + quote(repo, safe="") + "/issues"
        else:
            endpoint = "/repositories/" + repo + "/issues"
        return self._request("GET", endpoint)

    def create_branch(self, ws: str, principal: str, rid: str, branch: str,
                      from_branch: str = "main", *, approved_write: bool = False) -> Any:
        if not approved_write:
            raise ForgeDenied("Explicit approval required to create branches")
        if self.kind != "github":
            raise NotImplementedError("Branch mutation is currently only implemented for GitHub")
        repo = self._resource(ws, principal, rid, "write")
        for value in (branch, from_branch):
            if not re.fullmatch(r"[A-Za-z0-9._/-]{1,128}", value) or value.startswith("-") or ".." in value:
                raise ValueError("Invalid branch name")
        base = self._request("GET", "/repos/" + repo + "/git/ref/heads/" + quote(from_branch, safe=""))
        sha = base["object"]["sha"]
        if not re.fullmatch("[a-fA-F0-9]{40}", sha):
            raise ValueError("Untrusted base SHA")
        return self._request("POST", "/repos/" + repo + "/git/refs",
                             {"ref": "refs/heads/" + branch, "sha": sha})

    def commit_file(self, ws: str, principal: str, rid: str, path: str,
                    content: bytes, branch: str, message: str, *,
                    expected_blob_sha: str | None = None, approved_write: bool = False) -> Any:
        """GitHub Contents API, no force pushes, explicit branch + optional blob lease."""
        if not approved_write:
            raise ForgeDenied("File commits require explicit approval")
        if self.kind != "github":
            raise NotImplementedError("Commit mutation is currently only implemented for GitHub")
        repo = self._resource(ws, principal, rid, "write")
        if (not re.fullmatch(r"[A-Za-z0-9._/-]{1,256}", path) or
            ".." in path.split("/") or path.startswith("/") or
            not re.fullmatch(r"[A-Za-z0-9._/-]{1,128}", branch) or ".." in branch):
            raise ValueError("Unsafe repository path or branch")
        if len(content) > 1_000_000 or not message.strip():
            raise ValueError("Commit content/description outside accepted bounds")
        if expected_blob_sha and not re.fullmatch("[a-fA-F0-9]{40}", expected_blob_sha):
            raise ValueError("Invalid optimistic concurrency SHA")
        payload: dict[str, Any] = {
            "message": message, "branch": branch,
            "content": base64.b64encode(content).decode("ascii")
        }
        if expected_blob_sha:
            payload["sha"] = expected_blob_sha
        return self._request("PUT", "/repos/" + repo + "/contents/" + quote(path, safe="/"), payload)
