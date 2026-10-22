"""Centralized Qt palette and QSS with readable light/dark contrast."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QApplication

THEMES = {
    "light": {
        "bg": "#f5f7fb", "surface": "#ffffff", "text": "#17243b",
        "muted": "#506079", "border": "#68788e", "accent": "#175cbe",
        "on_accent": "#ffffff", "selection": "#d7e8ff",
    },
    "dark": {
        "bg": "#141b29", "surface": "#202c3e", "text": "#f1f5fb",
        "muted": "#c5d0e2", "border": "#8497b0", "accent": "#82b8ff",
        "on_accent": "#07182d", "selection": "#35557e",
    },
}


def stylesheet(theme: str) -> str:
    if theme not in THEMES:
        raise ValueError("Invalid Qt theme")
    c = THEMES[theme]
    check_icon = (Path(__file__).parent / "assets" / f"check-{theme}.svg").as_posix()
    return f"""
    QWidget {{ background-color: {c['bg']}; color: {c['text']}; font-size: 13px; }}
    #applicationShell, #dashboardContent, #dashboardScroll {{
      background-color: {c['bg']}; }}
    #sidebar {{ background-color: #061D40; border: none; }}
    #sidebarBrand {{ background: transparent; color: #f2f7ff;
      font-size: 22px; font-weight: 800; }}
    #sidebarHint {{ background: transparent; color: #9dbce9;
      font-size: 12px; }}
    #sidebarDivider {{ background-color: #42628a; border: none; max-height: 1px; }}
    QPushButton#sidebarNavigation {{ background: transparent; color: #d7e6fc;
      text-align: left; border: none; padding: 13px 12px;
      font-size: 14px; border-radius: 8px; }}
    QPushButton#sidebarNavigation:hover {{ background-color: #103c75; }}
    QPushButton#sidebarNavigation:checked {{ background-color: #0869EF;
      color: #ffffff; border-left: 4px solid #64d3ff; font-weight: 700; }}
    QPushButton#sidebarNavigation:focus {{ border: 2px solid #FFC340; }}
    #dashboardHero {{ background-color: #061D40; border: 1px solid #17539c;
      border-radius: 14px; min-height: 190px; }}
    #heroKicker {{ color: #FFC340; background: transparent;
      font-size: 12px; font-weight: 700; }}
    #heroTitle {{ color: #ffffff; background: transparent;
      font-size: 42px; font-weight: 800; }}
    #heroSubtitle {{ color: #ffffff; background: transparent; font-size: 18px; }}
    #heroNote {{ color: #b9cff0; background: transparent; font-size: 13px; }}
    #dashboardCard {{ background-color: {c['surface']}; border: 1px solid {c['border']};
      border-radius: 12px; }}
    #cardHeading {{ background: transparent; color: {c['text']};
      font-size: 19px; font-weight: 700; }}
    #cardNote {{ background: transparent; color: {c['muted']}; font-size: 12px; }}
    #statusRow {{ background-color: {c['bg']}; border-radius: 9px; }}
    #statusTitle {{ background: transparent; font-weight: 700; }}
    #statusBadge {{ background-color: #c9f2db; color: #074b31;
      border-radius: 12px; padding: 5px 11px; font-weight: 700; }}
    QPushButton#primaryAction {{ background-color: #0869EF; color: #ffffff;
      border: 2px solid #0869EF; font-size: 15px; font-weight: 700;
      min-height: 36px; }}
    QPushButton#primaryAction:hover {{ background-color: #0758ca; }}
    QPushButton#primaryAction:focus {{ border: 3px solid #FFC340; }}
    QMainWindow, QTabWidget::pane {{ background-color: {c['bg']}; }}
    QLabel {{ background: transparent; }}
    QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QDoubleSpinBox,
    QTableWidget {{ background-color: {c['surface']}; color: {c['text']};
      border: 1px solid {c['border']}; border-radius: 6px; padding: 6px; }}
    QPushButton {{ background-color: {c['surface']}; color: {c['text']};
      border: 1px solid {c['border']}; border-radius: 6px; padding: 8px; }}
    QPushButton:hover {{ border: 2px solid {c['accent']}; }}
    QPushButton:focus, QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus,
    QTableWidget:focus, QCheckBox:focus,
    QTextEdit:focus, QPlainTextEdit:focus {{
      border: 2px solid {c['accent']}; }}
    QPushButton:disabled {{ color: {c['muted']}; }}
    QCheckBox {{ background-color: transparent; spacing: 7px; }}
    QCheckBox::indicator {{ width: 17px; height: 17px;
      background-color: {c['surface']}; border: 2px solid {c['border']};
      border-radius: 4px; }}
    QCheckBox::indicator:checked {{ background-color: {c['accent']};
      border-color: {c['accent']}; image: url({check_icon}); }}
    QCheckBox::indicator:focus {{ border: 2px solid {c['accent']}; }}
    QTableCornerButton::section {{ background-color: {c['surface']};
      border: 1px solid {c['border']}; }}
    QTabBar::tab {{ background-color: {c['surface']}; color: {c['text']};
      padding: 10px 16px; margin-right: 2px; }}
    QTabBar::tab:selected {{ border-bottom: 3px solid {c['accent']}; }}
    QTableWidget::item:selected {{ background-color: {c['selection']}; color: {c['text']}; }}
    QHeaderView::section {{ background-color: {c['surface']}; color: {c['text']};
      border: 1px solid {c['border']}; padding: 7px; }}
    """


def apply_theme(app: QApplication, theme: str) -> None:
    app.setStyleSheet(stylesheet(theme))
