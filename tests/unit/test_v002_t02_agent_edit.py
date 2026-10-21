"""Qt agent editor regression tests for V002-T02."""
import os
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDialog, QDialogButtonBox, QLineEdit,
    QMessageBox, QTextEdit,
)
from multagent.core.domain import Agent
from multagent.desktop.views.window import MainWindow, WORKSPACE


@pytest.fixture
def window(tmp_path):
    app = QApplication.instance() or QApplication([])
    widget = MainWindow(tmp_path)
    yield widget
    widget.close()
    assert app is not None


def add_agent(window, name):
    window.agent_name.setText(name)
    window.agent_model.setText("model-a")
    window.add_agent()
    return next(agent for agent in window.registry.list(WORKSPACE) if agent.name == name)


def field(dialog, name, cls):
    widget = dialog.findChild(cls, name)
    assert widget is not None, name
    return widget


def save(dialog):
    controls = dialog.findChild(QDialogButtonBox)
    assert controls is not None
    controls.button(QDialogButtonBox.StandardButton.Save).click()


def test_edit_persistence_supervisor_and_disabled_state(window, tmp_path, monkeypatch):
    manager = add_agent(window, "Gestor")
    worker = add_agent(window, "Original")
    window.refresh_agents()
    for row in range(window.agent_table.rowCount()):
        if window.agent_table.item(row, 0).text() == worker.id:
            window.agent_table.selectRow(row)
            break

    def edit(dialog):
        field(dialog, "edit_agent_name", QLineEdit).setText("Alterado")
        field(dialog, "edit_agent_role", QLineEdit).setText("analyst")
        field(dialog, "edit_agent_model", QLineEdit).setText("model-b")
        field(dialog, "edit_agent_provider", QComboBox).setCurrentText("grok")
        selector = field(dialog, "edit_agent_supervisor", QComboBox)
        selector.setCurrentIndex(selector.findData(manager.id))
        field(dialog, "edit_agent_enabled", QCheckBox).setChecked(False)
        field(dialog, "edit_agent_instructions", QTextEdit).setPlainText("Revisadas")
        save(dialog)
        return dialog.result()

    monkeypatch.setattr(QDialog, "exec", edit)
    window.edit_agent()
    saved = window.registry.get(WORKSPACE, worker.id)
    assert (saved.name, saved.role, saved.provider, saved.model) == (
        "Alterado", "analyst", "grok", "model-b"
    )
    assert saved.supervisor_id == manager.id
    assert saved.enabled is False and saved.instructions == "Revisadas"
    assert any(
        window.agent_table.item(i, 4).text() == "Desativado"
        for i in range(window.agent_table.rowCount())
        if window.agent_table.item(i, 0).text() == worker.id
    )
    assert "Desativado" in window.run_agent.itemText(
        window.run_agent.findData(worker.id)
    )
    reopened = MainWindow(tmp_path)
    assert reopened.registry.get(WORKSPACE, worker.id).supervisor_id == manager.id
    reopened.close()


def test_invalid_fields_keep_dialog_open_and_preserve_data(window, monkeypatch):
    worker = add_agent(window, "Original")
    window.agent_table.selectRow(0)
    warnings = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *args: warnings.append(args[2]))

    def invalid_then_cancel(dialog):
        name = field(dialog, "edit_agent_name", QLineEdit)
        name.clear()
        save(dialog)
        assert dialog.result() != QDialog.DialogCode.Accepted
        assert name.text() == ""
        assert warnings
        name.setText("Ainda editando")
        return QDialog.DialogCode.Rejected

    monkeypatch.setattr(QDialog, "exec", invalid_then_cancel)
    window.edit_agent()
    assert window.registry.get(WORKSPACE, worker.id).name == "Original"


def test_cycle_rejected_without_closing_editor(window, monkeypatch):
    parent = add_agent(window, "Parent")
    child = add_agent(window, "Child")
    # Simulate stale persisted data created by external/manual mutation.
    record = window.store.get("agent", WORKSPACE, worker.id)
    record["supervisor_id"] = "missing-supervisor"
    window.store.put("agent", WORKSPACE, worker.id, record)
    window.refresh_agents()
    window.agent_table.selectRow(0)
    alerts = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *args: alerts.append(args[2]))
    window.edit_agent()
    assert alerts and "supervisor" in alerts[0].lower()
    assert window.registry.get(WORKSPACE, worker.id).supervisor_id == "missing-supervisor"


def test_cancel_does_not_save(window, monkeypatch):
    worker = add_agent(window, "Intacto")
    window.agent_table.selectRow(0)

    def cancel(dialog):
        field(dialog, "edit_agent_name", QLineEdit).setText("Descartado")
        return QDialog.DialogCode.Rejected

    monkeypatch.setattr(QDialog, "exec", cancel)
    window.edit_agent()
    assert window.registry.get(WORKSPACE, worker.id).name == "Intacto"
