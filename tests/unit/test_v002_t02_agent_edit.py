"""Regression coverage for V002-T02 full Qt agent editing."""
import os
import pytest


def test_agent_edit_persists_all_fields_and_cancel_is_safe(tmp_path, monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QComboBox, QCheckBox, QTextEdit
    from multagent.desktop.views.window import MainWindow, WORKSPACE

    app = QApplication.instance() or QApplication([])
    window = MainWindow(tmp_path)
    window.agent_name.setText("Original")
    window.agent_model.setText("model-a")
    window.add_agent()
    window.agent_table.selectRow(0)
    agent_id = window.agent_table.item(0, 0).text()
    before = window.registry.get(WORKSPACE, agent_id)
    assert before.name == "Original"

    def fill_and_accept(dialog):
        edits = dialog.findChildren(QLineEdit)
        assert len(edits) >= 3
        edits[0].setText("Alterado")
        edits[1].setText("supervisor")
        edits[2].setText("model-b")
        providers = dialog.findChildren(QComboBox)
        providers[0].setCurrentText("grok")
        dialog.findChild(QCheckBox).setChecked(False)
        dialog.findChild(QTextEdit).setPlainText("Instruções revisadas")
        return QDialog.DialogCode.Accepted

    monkeypatch.setattr(QDialog, "exec", fill_and_accept)
    window.edit_agent()
    saved = window.registry.get(WORKSPACE, agent_id)
    assert (saved.id, saved.name, saved.role, saved.provider, saved.model) == (
        agent_id, "Alterado", "supervisor", "grok", "model-b")
    assert saved.enabled is False
    assert saved.instructions == "Instruções revisadas"
    assert window.agent_table.currentRow() == 0

    window.close()
    reopened = MainWindow(tmp_path)
    assert reopened.registry.get(WORKSPACE, agent_id).instructions == "Instruções revisadas"
    reopened.agent_table.selectRow(0)
    monkeypatch.setattr(QDialog, "exec", lambda dialog: QDialog.DialogCode.Rejected)
    reopened.edit_agent()
    assert reopened.registry.get(WORKSPACE, agent_id).name == "Alterado"
    reopened.close()
    assert app is not None


def test_invalid_edit_does_not_overwrite_saved_agent(tmp_path, monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QMessageBox
    from multagent.desktop.views.window import MainWindow, WORKSPACE

    app = QApplication.instance() or QApplication([])
    window = MainWindow(tmp_path)
    window.agent_name.setText("Preservado")
    window.agent_model.setText("model-a")
    window.add_agent()
    window.agent_table.selectRow(0)
    agent_id = window.agent_table.item(0, 0).text()

    def invalid(dialog):
        dialog.findChildren(QLineEdit)[0].clear()
        return QDialog.DialogCode.Accepted

    monkeypatch.setattr(QDialog, "exec", invalid)
    monkeypatch.setattr(QMessageBox, "warning", lambda *args: QMessageBox.StandardButton.Ok)
    window.edit_agent()
    assert window.registry.get(WORKSPACE, agent_id).name == "Preservado"
    window.close()
    assert app is not None
