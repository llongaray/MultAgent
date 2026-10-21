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
    assert window.theme_combo.currentText() == "Claro"
    window.theme_combo.setCurrentIndex(window.theme_combo.findData("dark"))
    assert THEMES["dark"]["bg"] in app.styleSheet()
    assert window.store.get("settings", WORKSPACE, "appearance")["theme"] == "dark"
    window.close()
    reopened = MainWindow(tmp_path)
    assert reopened.theme_combo.currentText() == "Escuro"
    reopened.theme_combo.setCurrentIndex(reopened.theme_combo.findData("light"))
    assert THEMES["light"]["bg"] in app.styleSheet()
    reopened.close()


def _luminance(hex_color):
    channels = [int(hex_color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in channels]
    return sum(a * b for a, b in zip(linear, (0.2126, 0.7152, 0.0722)))


def test_control_boundary_contrast_and_focus_styles():
    for theme in THEMES.values():
        surface, border = sorted((_luminance(theme["surface"]), _luminance(theme["border"])))
        assert (border + 0.05) / (surface + 0.05) >= 3.0
    for token in (
        "QTableCornerButton::section", "QCheckBox::indicator", "QDoubleSpinBox:focus",
        "QTableWidget:focus", "QCheckBox:focus",
    ):
        assert token in stylesheet("dark")
        assert token in stylesheet("light")
