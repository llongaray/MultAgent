"""V002-T04: DeepSeek/Grok keys stay in the OS vault and out of the UI."""
from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QMessageBox

from multagent.desktop.views.window import WORKSPACE, MainWindow
from multagent.security.credentials import CredentialRejected, validate_api_key
from multagent.storage.sqlite import StoredRecordNotFound

SECRET = "sk-test-secret-value"


class MemoryVault:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    def put(self, name: str, secret: str) -> str:
        if not secret:
            raise ValueError("Secret may not be blank")
        self.values[name] = secret
        return "vault:" + name

    def get(self, reference: str) -> str:
        name = reference.removeprefix("vault:")
        if name not in self.values:
            raise KeyError("Credential not present")
        return self.values[name]

    def contains(self, reference: str) -> bool:
        return reference.removeprefix("vault:") in self.values

    def delete(self, reference: str) -> None:
        self.values.pop(reference.removeprefix("vault:"), None)


class ProbeClient:
    def __init__(self, status: int = 200, payload: dict | None = None) -> None:
        self.status = status
        self.payload = payload if payload is not None else {"data": [{"id": "demo-model"}]}
        self.headers: list[dict[str, str]] = []

    def __enter__(self) -> ProbeClient:
        return self

    def __exit__(self, *_args: object) -> bool:
        return False

    def request(self, method: str, url: str, headers: dict[str, str] | None = None, json: object = None) -> object:
        del method, url, json
        self.headers.append(dict(headers or {}))

        class Response:
            def __init__(self, status: int, payload: dict) -> None:
                self.status_code = status
                self._payload = payload

            def json(self) -> dict:
                return self._payload

        return Response(self.status, self.payload)


def test_api_key_rejects_blank_space_and_short_values() -> None:
    for secret in ("", "   ", "sk secret", "short"):
        with pytest.raises(CredentialRejected):
            validate_api_key(secret)
    assert validate_api_key(SECRET) == SECRET


@pytest.fixture
def desktop(tmp_path, monkeypatch):
    vault = MemoryVault()
    monkeypatch.setattr("multagent.desktop.views.window.KeyringVault", lambda: vault)
    app = QApplication.instance() or QApplication([])
    window = MainWindow(tmp_path)
    window._credential_client_factory = lambda timeout=30: ProbeClient()
    yield window, vault
    window.close()
    assert app is not None


def _secret_leaked(window: MainWindow, tmp_path) -> bool:
    database = (tmp_path / "state.db").read_bytes().decode("utf-8", "ignore")
    visible = " ".join((
        window.credential_status.text(),
        window.key_input.text(),
        window.statusBar().currentMessage() or "",
        database,
    ))
    return SECRET in visible


def test_save_stores_reference_without_showing_secret(desktop, tmp_path, monkeypatch):
    window, vault = desktop
    warnings: list[str] = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *args: warnings.append(args[2]))
    window.key_input.setText(SECRET)
    window.save_credential()
    assert warnings == []
    assert vault.get("vault:deepseek") == SECRET
    assert window.key_input.text() == ""
    assert window.credential_status.text() == "Configurada no cofre do sistema"
    record = window.store.get("integration", WORKSPACE, "deepseek")
    assert record["credential_ref"] == "vault:deepseek"
    assert SECRET not in record.values()
    assert not _secret_leaked(window, tmp_path)


def test_invalid_key_is_not_stored(desktop, monkeypatch):
    window, vault = desktop
    warnings: list[str] = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *args: warnings.append(args[2]))
    window.key_input.setText("bad key")
    window.save_credential()
    assert warnings
    assert SECRET not in warnings[-1]
    assert vault.values == {}
    assert window.credential_status.text() == "Não configurada"


def test_switching_provider_clears_the_field_and_status(desktop):
    window, _vault = desktop
    window.key_input.setText(SECRET)
    window.key_provider.setCurrentIndex(window.key_provider.findData("grok"))
    assert window.key_input.text() == ""
    assert window.credential_status.text() == "Não configurada"
    assert window.key_provider.currentData() == "grok"


def test_probe_confirms_stored_key_without_displaying_it(desktop, tmp_path, monkeypatch):
    window, _vault = desktop
    client = ProbeClient()
    window._credential_client_factory = lambda timeout=30: client
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.StandardButton.Yes)
    window.key_input.setText(SECRET)
    window.save_credential()
    window.test_credential()
    assert client.headers
    assert client.headers[0].get("Authorization") == "Bearer " + SECRET
    assert window.statusBar().currentMessage() == "Credencial aceita pelo provedor. A chave não é exibida."
    assert not _secret_leaked(window, tmp_path)


def test_rejected_probe_hides_the_provider_error_body(desktop, monkeypatch):
    window, _vault = desktop
    window._credential_client_factory = lambda timeout=30: ProbeClient(status=401, payload={"error": SECRET})
    warnings: list[str] = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *args: warnings.append(str(args[2])))
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.StandardButton.Yes)
    window.key_input.setText(SECRET)
    window.save_credential()
    window.test_credential()
    assert warnings
    assert "HTTP 401" in warnings[-1]
    assert SECRET not in warnings[-1]


def test_unexpected_probe_failure_does_not_reveal_the_secret(desktop, monkeypatch):
    window, _vault = desktop

    class LeakyClient(ProbeClient):
        def request(self, method: str, url: str, headers: dict[str, str] | None = None, json: object = None) -> object:
            del method, url, headers, json
            raise RuntimeError("Authorization: Bearer " + SECRET)

    window._credential_client_factory = lambda timeout=30: LeakyClient()
    warnings: list[str] = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *args: warnings.append(str(args[2])))
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.StandardButton.Yes)
    window.key_input.setText(SECRET)
    window.save_credential()
    window.test_credential()
    assert warnings == ["Falha ao validar a credencial"]
    assert SECRET not in warnings[-1]


def test_remove_deletes_vault_entry_and_reference(desktop, tmp_path, monkeypatch):
    window, vault = desktop
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.StandardButton.Yes)
    window.key_input.setText(SECRET)
    window.save_credential()
    window.remove_credential()
    assert "deepseek" not in vault.values
    with pytest.raises(StoredRecordNotFound):
        window.store.get("integration", WORKSPACE, "deepseek")
    assert window.credential_status.text() == "Não configurada"
    assert not _secret_leaked(window, tmp_path)
