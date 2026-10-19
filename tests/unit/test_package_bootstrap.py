"""Testes do bootstrap P0-01: instalação e importação sem side effects."""

import subprocess
import sys
import tomllib
from pathlib import Path

import multagent

ROOT = Path(__file__).resolve().parents[2]


def test_import_exposes_pre_release_version() -> None:
    assert multagent.__version__ == "0.0.1.dev0"


def test_version_matches_package_metadata() -> None:
    with (ROOT / "pyproject.toml").open("rb") as stream:
        metadata = tomllib.load(stream)
    assert metadata["project"]["version"] == multagent.__version__
    assert metadata["project"]["dependencies"] == []
    assert metadata["project"]["requires-python"] == ">=3.11"


def test_import_does_not_initialize_ui_or_http_server() -> None:
    snippet = (
        "import sys; import multagent; "
        "assert not {'PySide6', 'fastapi', 'uvicorn'} "
        "& {name.split('.')[0] for name in sys.modules}; "
        "assert multagent.__version__"
    )
    result = subprocess.run(
        [sys.executable, "-c", snippet],
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
        cwd=ROOT / "src",
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_package_is_typed() -> None:
    assert (ROOT / "src" / "multagent" / "py.typed").is_file()
