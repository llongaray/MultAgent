"""V002-T01 theme switch and persistence smoke coverage."""
import os
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication
from multagent.desktop.theme import THEMES, stylesheet
from multagent.desktop.views.window import MainWindow, WORKSPACE


def test_theme_tokens_are_valid_and_distinct():
    assert set(THEMES) == {"light", "dark"}
    assert stylesheet("light") != stylesheet("dark")
    with pytest.raises(ValueError):
        stylesheet("unknown")


def test_theme_is_applied_and_restored(tmp_path):
    app = QApplication.instance() or QApplication([])
    window = MainWindow(tmp_path)
    assert window.theme_combo.currentText() == "light"
    window.theme_combo.setCurrentText("dark")
    assert THEMES["dark"]["bg"] in app.styleSheet()
    assert window.store.get("settings", WORKSPACE, "appearance")["theme"] == "dark"
    window.close()
    reopened = MainWindow(tmp_path)
    assert reopened.theme_combo.currentText() == "dark"
    reopened.theme_combo.setCurrentText("light")
    assert THEMES["light"]["bg"] in app.styleSheet()
    reopened.close()
