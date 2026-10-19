"""Headless authenticated Server API: no Qt imports and no automatic paid requests."""
from __future__ import annotations

import hmac
from pathlib import Path
from uuid import uuid4\nfrom urllib.parse import urlsplit
from typing import Any

from fastapi import Cookie, Depends, FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from multagent.agents import AgentRegistry
from multagent.core.domain import Agent, DomainError
from multagent.core.router import Mode, Router, RoutingConfig
from multagent.server.auth.security import Session, SessionStore, verify_password
from multagent.storage.sqlite import SQLiteStore, StoredRecordNotFound

WORKSPACE = "server-default"


class LoginBody(BaseModel):
    password: str = Field(min_length=1, max_length=1024)


class AgentBody(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    role: str = Field(default="worker", max_length=120)
    provider: str
    model: str = Field(min_length=1, max_length=120)
    supervisor_id: str | None = None


class ModeBody(BaseModel):
    mode: Mode


def create_app(config: dict[str, Any], store: SQLiteStore | None = None) -> FastAPI:
    """Construct app with scoped services. Auth required even on loopback for private routes."""
    if not config.get("password_hash"):
        raise ValueError("Server must be initialized before startup")
    database = store or SQLiteStore(Path(config["data_dir"]) / "state.db")
    session_store = SessionStore()
    router = Router(RoutingConfig(Mode.DEEPSEEK_ONLY, {"deepseek"}))
    agents = AgentRegistry(database, router)
    app = FastAPI(title="MultAgent Server", docs_url=None, redoc_url=None, openapi_url=None)

    @app.middleware("http")
    async def security_headers(request: Request, call_next: Any) -> Response:
        host = request.headers.get("host", "")
        host_name = host.split(":")[0].strip("[]").lower()
        allowed = {str(config.get("bind", "127.0.0.1")).strip("[]").lower(), "127.0.0.1", "localhost", "::1", "testserver"}\n        allowed.update(str(h).lower() for h in config.get("allowed_hosts", []))
        if host_name not in allowed:
            return Response("Unrecognized host", status_code=400)
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = "default-src 'self'; object-src 'none'; frame-ancestors 'none'"
        return response

    def signed_in(session: str | None = Cookie(default=None, alias="multagent_session"),
                  csrf: str | None = Header(default=None, alias="X-CSRF-Token"),
                  request: Request = None) -> Session:
        record = session_store.lookup(session)
        if record is None:
            raise HTTPException(status_code=401, detail="Authentication required")
        if request is not None and request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            if not csrf or not hmac.compare_digest(csrf, record.csrf_token):
                raise HTTPException(status_code=403, detail="CSRF token required")
            origin = request.headers.get("origin")
            if origin and origin.rstrip("/") != str(request.base_url).rstrip("/"):
                raise HTTPException(status_code=403, detail="Invalid Origin")
        return record

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "healthy"}

    @app.post("/api/login")
    def login(body: LoginBody, response: Response) -> dict[str, str]:
        if not verify_password(body.password, str(config["password_hash"])):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token, created = session_store.create()
        secure = bool(config.get("tls_cert"))
        response.set_cookie("multagent_session", token, httponly=True, secure=secure,
                            samesite="strict", max_age=3600, path="/")
        return {"csrf_token": created.csrf_token}

    @app.post("/api/logout", dependencies=[Depends(signed_in)])
    def logout(response: Response, session: str | None = Cookie(default=None, alias="multagent_session")) -> dict[str, bool]:
        session_store.revoke(session)
        response.delete_cookie("multagent_session", path="/")
        return {"ok": True}

    @app.get("/api/me", dependencies=[Depends(signed_in)])
    def me() -> dict[str, str]:
        return {"role": "administrator", "workspace_id": WORKSPACE}

    @app.get("/api/agents", dependencies=[Depends(signed_in)])
    def list_agents() -> list[dict[str, Any]]:
        from dataclasses import asdict
        return [asdict(x) for x in agents.list(WORKSPACE)]

    @app.post("/api/agents", dependencies=[Depends(signed_in)], status_code=201)
    def create_agent(body: AgentBody) -> dict[str, str]:
        try:
            a = Agent(str(uuid4()), WORKSPACE, body.name, body.provider, body.model,
                      role=body.role, supervisor_id=body.supervisor_id)
            agents.save(a)
            return {"id": a.id}
        except (DomainError, StoredRecordNotFound) as exc:
            raise HTTPException(status_code=422, detail="Invalid agent or supervisor") from exc

    @app.delete("/api/agents/{agent_id}", dependencies=[Depends(signed_in)])
    def delete_agent(agent_id: str) -> dict[str, bool]:
        try:
            agents.get(WORKSPACE, agent_id)
            agents.delete(WORKSPACE, agent_id)
            return {"ok": True}
        except (DomainError, StoredRecordNotFound) as exc:
            raise HTTPException(status_code=404, detail="Agent not found or referenced") from exc

    @app.post("/api/mode", dependencies=[Depends(signed_in)])
    def set_mode(body: ModeBody) -> dict[str, str]:
        mode = body.mode
        router.config.mode = mode
        router.config.enabled = ({"deepseek"} if mode == Mode.DEEPSEEK_ONLY else
                                 {"grok"} if mode == Mode.GROK_ONLY else {"deepseek", "grok"})
        database.put("settings", WORKSPACE, "mode", {"id": "mode", "mode": mode.value})
        return {"mode": mode.value}

    @app.get("/api/mode", dependencies=[Depends(signed_in)])
    def get_mode() -> dict[str, str]:
        return {"mode": router.config.mode.value}

    @app.get("/api/runs", dependencies=[Depends(signed_in)])
    def list_runs() -> list[dict[str, Any]]:
        # Only recorded execution states; no model prompts or results.
        return database.list("run", WORKSPACE)

    @app.get("/api/audit", dependencies=[Depends(signed_in)])
    def list_audit() -> list[dict[str, Any]]:
        return database.audit_log(WORKSPACE)

    @app.get("/assets/{filename:path}")
    def static_asset(filename: str) -> Any:
        directory = Path(str(config.get("frontend_dir") or "")) / "assets"
        if not filename or ".." in Path(filename).parts:
            raise HTTPException(status_code=404)
        asset = (directory / filename).resolve()
        if not config.get("frontend_dir") or not asset.is_relative_to(directory.resolve()) or not asset.is_file():
            raise HTTPException(status_code=404)
        return FileResponse(asset)

    @app.get("/")
    def frontend(request: Request) -> Any:
        index = Path(str(config.get("frontend_dir", ""))) / "index.html"
        if index.is_file() and config.get("frontend_dir"):
            return FileResponse(index)
        return {"edition": "server", "status": "frontend-not-built",
                "hint": "Build frontend-server with npm run build"}

    return app
