"""Native sidebar and home dashboard regression checks."""
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QFrame, QPushButton

from multagent.desktop.views.shell import SECTIONS
from multagent.desktop.views.window import MainWindow, WORKSPACE


def test_sidebar_preserves_six_pages_and_navigation(tmp_path):
    app = QApplication.instance() or QApplication([])
    window = MainWindow(tmp_path)
    assert window.tabs.count() == 6
    assert window.tabs.tabBar().isHidden()
    assert tuple(window.tabs.tabText(i) for i in range(6)) == tuple(
        label for label, _symbol in SECTIONS
    )
    assert len(window.nav_buttons) == 6
    assert window.nav_buttons[0].isChecked()
    for index in range(6):
        window.nav_buttons[index].click()
        assert window.tabs.currentIndex() == index
        assert window.nav_buttons[index].isChecked()
        assert sum(button.isChecked() for button in window.nav_buttons) == 1
    window.close()
    assert app is not None


def test_dashboard_preserves_settings_and_has_cards(tmp_path):
    app = QApplication.instance() or QApplication([])
    window = MainWindow(tmp_path)
    assert window.findChild(QFrame, "dashboardHero") is not None
    assert len(window.findChildren(QFrame, "dashboardCard")) >= 5
    assert window.findChild(QPushButton, "primaryAction") is not None
    assert window.theme_combo.currentData() == "light"
    window.theme_combo.setCurrentIndex(window.theme_combo.findData("dark"))
    assert window.store.get("settings", WORKSPACE, "appearance")["theme"] == "dark"
    window.mode_combo.setCurrentIndex(0)
    window.save_mode()
    assert window.store.get("settings", WORKSPACE, "routing")["mode"] == (
        window.mode_combo.currentData().value
    )
    window.close()
    assert app is not None
