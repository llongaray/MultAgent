import os
import pytest


def test_gui_is_native_without_http_or_browser(tmp_path, monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication
    from multagent.desktop.views.window import MainWindow
    app = QApplication.instance() or QApplication([])
    def forbidden(*args, **kwargs):
        raise AssertionError("No HTTP bind or webbrowser in Desktop initialization")
    import socket
    import webbrowser
    monkeypatch.setattr(socket.socket, "bind", forbidden)
    monkeypatch.setattr(webbrowser, "open", forbidden)
    window = MainWindow(tmp_path)
    assert window.tabs.count() == 6
    window.agent_name.setText("Engenheiro")
    window.agent_model.setText("model-test")
    window.add_agent()
    assert window.agent_table.rowCount() == 1
    assert "Sem servidor" not in window.windowTitle()
    window.close()
    assert app is not None


def test_cli_diagnostics_are_headless(capsys, tmp_path, monkeypatch):
    from multagent.desktop.cli import main
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    assert main(["doctor"]) == 0
    assert "no HTTP server" in capsys.readouterr().out
