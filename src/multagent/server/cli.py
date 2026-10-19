"""Headless CLI; configuration is explicit, never opens a browser or Qt."""
from __future__ import annotations

import argparse
import getpass
from pathlib import Path
import os
import sys
from multagent import __version__
from multagent.server.config import config_path, initialize, load


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="multagent-server")
    parser.add_argument("command", choices=["init", "start", "status", "doctor", "version"])
    parser.add_argument("--config", type=Path, default=config_path())
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--tls-cert")
    parser.add_argument("--tls-key")\n    parser.add_argument("--allowed-host", action="append", default=[], help="Explicit TLS hostname/IP allowed for remote clients")
    args = parser.parse_args(argv)
    if args.command == "version":
        print(__version__)
        return 0
    if args.command == "init":
        if args.config.exists():
            print("Already initialized; refusing overwrite", file=sys.stderr)
            return 1
        password = getpass.getpass("Administrator password (min. 12 characters): ")
        repeat = getpass.getpass("Confirm password: ")
        if password != repeat:
            print("Passwords do not match", file=sys.stderr)
            return 1
        try:
            initialize(args.config, password, args.port, args.bind,
                       tls_cert=args.tls_cert, tls_key=args.tls_key, allowed_hosts=tuple(args.allowed_host))
        except (ValueError, OSError) as exc:
            print("Initialization rejected:", type(exc).__name__, file=sys.stderr)
            return 1
        print("Initialized server config:", args.config)
        return 0
    try:
        config = load(args.config)
    except (ValueError, OSError) as exc:
        print("Server not initialized or configuration invalid", file=sys.stderr)
        return 1
    if args.command in ("doctor", "status"):
        print(f"Configured for {config['bind']}:{config['port']} (not proof of running)")
        print("TLS:", bool(config.get("tls_cert")))
        return 0
    try:
        import uvicorn
        from multagent.server.api import create_app
        config["frontend_dir"] = os.environ.get("MULTAGENT_SERVER_UI", str(Path(__file__).resolve().parents[3] / "frontend-server" / "dist"))
        app = create_app(config)
        uvicorn.run(app, host=config["bind"], port=config["port"],
                    ssl_certfile=config.get("tls_cert"), ssl_keyfile=config.get("tls_key"),
                    access_log=False)
        return 0
    except (OSError, ImportError) as exc:
        print("Server startup failed:", type(exc).__name__, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
