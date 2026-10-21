"""V002-T03: visual selectors for workspace-scoped permissions."""
import os
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
from multagent.desktop.views.window import MainWindow, WORKSPACE


def test_permission_agent_selector_and_directory_picker(tmp_path, monkeypatch):
    app = QApplication.instance() or QApplication([])
    window = MainWindow(tmp_path)
    window.agent_name.setText("Analista")
    window.agent_model.setText("model-test")
    window.add_agent()
    agent = window.registry.list(WORKSPACE)[0]
    index = window.principal_agent.findData(agent.id)
    assert index > 0
    window.principal_agent.setCurrentIndex(index)
    window.resource_kind.setCurrentText("directory")
    assert window.resource_picker.isEnabled()
    monkeypatch.setattr(
        QFileDialog, "getExistingDirectory",
        lambda *args, **kwargs: str(tmp_path),
    )
    window.choose_permission_directory()
    assert window.resource_locator.text() == str(tmp_path)
    window.permission_action.setCurrentText("read")
    window.grant_permission()
    records = window.store.list("grant", WORKSPACE)
    assert len(records) == 1
    assert records[0]["principal_id"] == agent.id
    window.resource_kind.setCurrentText("ssh")
    assert not window.resource_picker.isEnabled()
    window.close()
    assert app is not None


def test_permission_requires_selected_agent(tmp_path, monkeypatch):
    app = QApplication.instance() or QApplication([])
    window = MainWindow(tmp_path)
    messages = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *args: messages.append(args[2]))
    window.resource_locator.setText(str(tmp_path))
    window.grant_permission()
    assert messages and "Selecione um funcionário" in messages[-1]
    assert window.store.list("grant", WORKSPACE) == []
    window.close()
    assert app is not None
