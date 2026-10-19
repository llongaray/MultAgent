"""Terminal diagnostics for the GUI edition (no HTTP listener)."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
from multagent import __version__


def data_directory() -> Path:
    import os
    if os.name == "nt":
        root = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
        return root / "MultAgent"
    return Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "multagent"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="multagent-cli", description="MultAgent diagnostic commands")
    parser.add_argument("command", choices=["version", "doctor", "logs"], help="diagnostic operation")
    args = parser.parse_args(argv)
    if args.command == "version":
        print(__version__)
    elif args.command == "doctor":
        directory = data_directory()
        print("Version:", __version__)
        print("Data directory:", directory)
        print("Database:", "present" if (directory / "state.db").exists() else "not initialized")
        print("Desktop: no HTTP server used")
    elif args.command == "logs":
        log = data_directory() / "multagent.log"
        if log.exists():
            print(log.read_text(encoding="utf-8")[-20000:])
        else:
            print("No local log file available")
    return 0


if __name__ == "__main__":
    sys.exit(main())
