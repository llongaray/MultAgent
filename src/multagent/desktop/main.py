"""Native GUI entry point; no FastAPI, WebView or HTTP bind."""
from __future__ import annotations

import sys
from multagent import __version__
from multagent.desktop.cli import data_directory


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args == ["--version"]:
        print(__version__)
        return 0
    if args and args != ["start"]:
        print("Desktop: use 'multagent' to open GUI or 'multagent-cli doctor|logs|version'")
        return 2
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        print("PySide6 is missing; install with pip install 'multagent[desktop]'")
        return 1
    from multagent.desktop.views.window import MainWindow
    app = QApplication.instance()
    owned = app is None
    if app is None:
        app = QApplication(["MultAgent"])
    window = MainWindow(data_directory())
    window.show()
    if owned:
        return int(app.exec())
    return 0


if __name__ == "__main__":
    sys.exit(main())
