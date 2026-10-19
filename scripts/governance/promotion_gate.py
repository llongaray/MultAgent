"""Fail-closed PR promotion policy, enforced only when a ruleset requires this CI job."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
from typing import Any

FEATURE_RE = re.compile(r"^(feat|fix|docs|security|build|test|ops|chore)/[a-zA-Z0-9][a-zA-Z0-9._/-]*$")
ALLOWED_SOURCE = {"dev": None, "hml": "dev", "main": "hml"}


def validate(event: dict[str, Any]) -> tuple[bool, str]:
    pr = event.get("pull_request")
    if not isinstance(pr, dict):
        return False, "Only pull_request events can pass the promotion gate"
    base, head = pr.get("base", {}), pr.get("head", {})
    if not isinstance(base, dict) or not isinstance(head, dict):
        return False, "Invalid pull request metadata"
    target, source = base.get("ref"), head.get("ref")
    target_repo = (base.get("repo") or {}).get("full_name")
    source_repo = (head.get("repo") or {}).get("full_name")
    if target not in ALLOWED_SOURCE or not source:
        return False, "Unknown target or source branch"
    if not target_repo or source_repo != target_repo:
        return False, "Fork promotions are not permitted"
    if target == "dev":
        if source in ("main", "hml", "dev") or not FEATURE_RE.fullmatch(source) or ".." in source:
            return False, "dev accepts only named feature/fix/docs/security/build/test/ops/chore PRs"
    elif source != ALLOWED_SOURCE[target]:
        return False, f"{target} accepts promotions only from {ALLOWED_SOURCE[target]}"
    if pr.get("draft"):
        return False, "Draft pull requests are not eligible for promotion"
    return True, f"Permitted promotion: {source} -> {target}"


def main() -> int:
    path = os.environ.get("GITHUB_EVENT_PATH")
    if not path:
        print("Missing GITHUB_EVENT_PATH: cannot prove a valid pull request", file=sys.stderr)
        return 1
    try:
        event = json.loads(Path(path).read_text(encoding="utf-8"))
        result, message = validate(event)
    except (OSError, ValueError, TypeError) as exc:
        print(f"Invalid event input: {type(exc).__name__}", file=sys.stderr)
        return 1
    print(message)
    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())
