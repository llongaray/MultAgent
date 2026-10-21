"""Centralized Qt palette and QSS with readable light/dark contrast."""
from __future__ import annotations

from PySide6.QtWidgets import QApplication

THEMES = {
    "light": {
        "bg": "#f5f7fb", "surface": "#ffffff", "text": "#17243b",
        "muted": "#506079", "border": "#9eacc0", "accent": "#175cbe",
        "on_accent": "#ffffff", "selection": "#d7e8ff",
    },
    "dark": {
        "bg": "#141b29", "surface": "#202c3e", "text": "#f1f5fb",
        "muted": "#c5d0e2", "border": "#657790", "accent": "#82b8ff",
        "on_accent": "#07182d", "selection": "#35557e",
    },
}


def stylesheet(theme: str) -> str:
    if theme not in THEMES:
        raise ValueError("Invalid Qt theme")
    c = THEMES[theme]
    return f"""
    QWidget {{ background-color: {c['bg']}; color: {c['text']}; font-size: 13px; }}
    QMainWindow, QTabWidget::pane {{ background-color: {c['bg']}; }}
    QLabel {{ background: transparent; }}
    QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QDoubleSpinBox,
    QTableWidget {{ background-color: {c['surface']}; color: {c['text']};
      border: 1px solid {c['border']}; border-radius: 6px; padding: 6px; }}
    QPushButton {{ background-color: {c['surface']}; color: {c['text']};
      border: 1px solid {c['border']}; border-radius: 6px; padding: 8px; }}
    QPushButton:hover {{ border: 2px solid {c['accent']}; }}
    QPushButton:focus, QLineEdit:focus, QComboBox:focus,
    QTextEdit:focus, QPlainTextEdit:focus {{
      border: 2px solid {c['accent']}; }}
    QPushButton:disabled {{ color: {c['muted']}; }}
    QTabBar::tab {{ background-color: {c['surface']}; color: {c['text']};
      padding: 10px 16px; margin-right: 2px; }}
    QTabBar::tab:selected {{ border-bottom: 3px solid {c['accent']}; }}
    QTableWidget::item:selected {{ background-color: {c['selection']}; color: {c['text']}; }}
    QHeaderView::section {{ background-color: {c['surface']}; color: {c['text']};
      border: 1px solid {c['border']}; padding: 7px; }}
    """


def apply_theme(app: QApplication, theme: str) -> None:
    app.setStyleSheet(stylesheet(theme))
