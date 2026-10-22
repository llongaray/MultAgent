"""Native Qt sidebar and dashboard presentation components.

Pure presentation: no routing, credential, or persistence operations.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

SECTIONS = (
    ("Início", "⌂"),
    ("Funcionários", "♙"),
    ("Integrações", "⚡"),
    ("Permissões", "◇"),
    ("Execuções", "▷"),
    ("Logs", "▤"),
)


def sidebar(on_navigate) -> tuple[QFrame, list[QPushButton]]:
    panel = QFrame()
    panel.setObjectName("sidebar")
    panel.setFixedWidth(232)
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(14, 22, 14, 16)
    layout.setSpacing(7)

    brand = QLabel("◢  MultAgent")
    brand.setObjectName("sidebarBrand")
    layout.addWidget(brand)
    version = QLabel("      Desktop local")
    version.setObjectName("sidebarHint")
    layout.addWidget(version)
    layout.addSpacing(25)

    buttons = []
    for index, (name, symbol) in enumerate(SECTIONS):
        button = QPushButton(f"  {symbol}    {name}")
        button.setObjectName("sidebarNavigation")
        button.setCheckable(True)
        button.setAccessibleName("Abrir " + name)
        button.clicked.connect(lambda _checked=False, i=index: on_navigate(i))
        layout.addWidget(button)
        buttons.append(button)
    layout.addStretch()

    footer_line = QFrame()
    footer_line.setFrameShape(QFrame.Shape.HLine)
    footer_line.setObjectName("sidebarDivider")
    layout.addWidget(footer_line)
    footer = QLabel("◢  Aray")
    footer.setObjectName("sidebarBrand")
    layout.addWidget(footer)
    tagline = QLabel("Inteligência que trabalha com você.")
    tagline.setWordWrap(True)
    tagline.setObjectName("sidebarHint")
    layout.addWidget(tagline)
    return panel, buttons


def card(title: str, subtitle: str = "") -> tuple[QFrame, QVBoxLayout]:
    panel = QFrame()
    panel.setObjectName("dashboardCard")
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(12)
    heading = QLabel(title)
    heading.setObjectName("cardHeading")
    layout.addWidget(heading)
    if subtitle:
        note = QLabel(subtitle)
        note.setObjectName("cardNote")
        note.setWordWrap(True)
        layout.addWidget(note)
    return panel, layout


def status_row(title: str, description: str, state: str) -> QFrame:
    panel = QFrame()
    panel.setObjectName("statusRow")
    layout = QHBoxLayout(panel)
    layout.setContentsMargins(12, 10, 12, 10)
    content = QVBoxLayout()
    name = QLabel(title)
    name.setObjectName("statusTitle")
    content.addWidget(name)
    detail = QLabel(description)
    detail.setWordWrap(True)
    detail.setObjectName("cardNote")
    content.addWidget(detail)
    layout.addLayout(content, 1)
    badge = QLabel(state)
    badge.setObjectName("statusBadge")
    badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(badge)
    return panel


def dashboard_scroller() -> tuple[QScrollArea, QVBoxLayout]:
    scroll = QScrollArea()
    scroll.setObjectName("dashboardScroll")
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    inner = QWidget()
    inner.setObjectName("dashboardContent")
    layout = QVBoxLayout(inner)
    layout.setContentsMargins(18, 18, 18, 18)
    layout.setSpacing(16)
    scroll.setWidget(inner)
    return scroll, layout
