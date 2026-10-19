import os
import pytest
from multagent.server.auth.security import hash_password, verify_password
from multagent.server.config import initialize, load
from multagent.storage.sqlite import SQLiteStore


def test_password_hash_and_safe_server_configuration(tmp_path):
    hashed = hash_password("very long test password 123")
    assert verify_password("very long test password 123", hashed)
    assert not verify_password("wrong", hashed)
    config = tmp_path / "config.json"
    with pytest.raises(ValueError):
        initialize(config, "very long test password", bind="0.0.0.0")
    initialize(config, "very long test password", 8989)
    assert load(config)["port"] == 8989
    assert "very long test password" not in config.read_text()
    with pytest.raises(ValueError):
        initialize(tmp_path / "remote.json", "very long test password", bind="0.0.0.0",
                   tls_cert="server.crt", tls_key="server.key")
    initialize(tmp_path / "remote.json", "very long test password", bind="0.0.0.0",
               tls_cert="server.crt", tls_key="server.key", allowed_hosts=("server.example",))
    assert load(tmp_path / "remote.json")["allowed_hosts"] == ["server.example"]
    with pytest.raises(FileExistsError):
        initialize(config, "another long password 123")


def test_server_auth_csrf_and_workspace(tmp_path):
    fastapi = pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient
    from multagent.server.api import create_app
    config = {"password_hash": hash_password("correct-test-password"), "bind": "127.0.0.1",
              "port": 8765, "data_dir": str(tmp_path)}
    client = TestClient(create_app(config, SQLiteStore(tmp_path / "db.sqlite")))
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/agents").status_code == 401
    assert client.post("/api/login", json={"password": "bad"}).status_code == 401
    csrf = client.post("/api/login", json={"password": "correct-test-password"}).json()["csrf_token"]
    assert client.get("/api/me").json()["role"] == "administrator"
    assert client.post("/api/agents", json={"name": "Coder", "provider": "grok", "model": "model"}).status_code == 403
    result = client.post("/api/agents", headers={"X-CSRF-Token": csrf},
        json={"name": "Coder", "provider": "grok", "model": "model"})
    assert result.status_code == 201, result.text
    assert len(client.get("/api/agents").json()) == 1
    assert client.post("/api/mode", headers={"X-CSRF-Token": csrf}, json={"mode": "hybrid"}).status_code == 200
    assert client.get("/api/mode").json()["mode"] == "hybrid"
    assert client.post("/api/logout", headers={"X-CSRF-Token": csrf}).status_code == 200
    assert client.get("/api/me").status_code == 401
    assert client.get("/api/agents", headers={"Host": "evil.invalid"}).status_code == 400


def test_server_does_not_import_gui():
    import sys
    from multagent.server.api import create_app
    assert "PySide6" not in sys.modules
