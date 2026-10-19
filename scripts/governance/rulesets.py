"""Plan, apply and verify repository branch rulesets/labels using a separately supplied admin PAT.

Never called by CI automatically. --apply must be explicit, and only after manual review.
The GitHub connector used to commit this code cannot grant itself admin mutation rights.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from typing import Any

OWNER = "llongaray"
REPO = "MultAgent"
BASE = f"https://api.github.com/repos/{OWNER}/{REPO}"
LABELS = {**{f"P{i}": f"{i:02x}6699" for i in range(10)},
          "docs": "1d76db", "security": "b60205", "bug": "d73a4a", "feature": "a2eeef"}
CI_CONTEXTS = [
    "promotion-gate", "unit (ubuntu-latest, 3.11)", "unit (ubuntu-latest, 3.13)",
    "unit (windows-latest, 3.11)", "unit (windows-latest, 3.13)",
    "qt (ubuntu-latest, 3.11)", "qt (windows-latest, 3.11)", "react",
]


def planned_ruleset(branch: str) -> dict[str, Any]:
    if branch not in ("dev", "hml", "main"):
        raise ValueError("Not a governed branch")
    rules = [
        {"type": "deletion"},
        {"type": "non_fast_forward"},
        {"type": "pull_request", "parameters": {
            "dismiss_stale_reviews_on_push": True,
            "require_code_owner_review": False,
            "require_last_push_approval": False,
            "required_approving_review_count": 1 if branch == "main" else 0,
            "required_review_thread_resolution": branch == "main",
        }},
        {"type": "required_status_checks", "parameters": {
            "strict_required_status_checks_policy": True,
            "do_not_enforce_on_create": False,
            "required_status_checks": [{"context": context} for context in CI_CONTEXTS],
        }},
    ]
    return {
        "name": f"MultAgent guarded {branch} (managed)",
        "target": "branch",
        "enforcement": "active",
        "conditions": {"ref_name": {"include": [f"refs/heads/{branch}"], "exclude": []}},
        "bypass_actors": [],
        "rules": rules,
    }


def request(method: str, path: str, token: str, payload: dict[str, Any] | None = None) -> Any:
    data = json.dumps(payload).encode() if payload is not None else None
    req = Request(BASE + path, data=data, method=method,
                  headers={"Accept": "application/vnd.github+json",
                           "X-GitHub-Api-Version": "2022-11-28",
                           "Authorization": "Bearer " + token,
                           "User-Agent": "MultAgent-Governance-CLI",
                           **({"Content-Type": "application/json"} if data is not None else {})})
    with urlopen(req, timeout=20) as response:
        raw = response.read()
        return json.loads(raw) if raw else {}


def apply(token: str) -> None:
    existing = request("GET", "/rulesets?per_page=100", token)
    for branch in ("dev", "hml", "main"):
        desired = planned_ruleset(branch)
        matched = next((r for r in existing if r.get("name") == desired["name"]), None)
        if matched:
            request("PUT", f"/rulesets/{matched['id']}", token, desired)
        else:
            request("POST", "/rulesets", token, desired)
        print(f"Applied {branch} ruleset")
    current_labels = {x["name"] for x in request("GET", "/labels?per_page=100", token)}
    for name, color in LABELS.items():
        if name not in current_labels:
            request("POST", "/labels", token, {"name": name, "color": color})
            print(f"Created label {name}")


def verify(token: str) -> bool:
    listed = request("GET", "/rulesets?per_page=100", token)
    found = {r["name"]: r for r in listed if r.get("enforcement") == "active"}
    for branch in ("dev", "hml", "main"):
        desired = planned_ruleset(branch)
        summary = found.get(desired["name"])
        if not summary:
            print(f"MISSING active ruleset for {branch}")
            return False
        detail = request("GET", f"/rulesets/{summary['id']}", token)
        kinds = {r.get("type") for r in detail.get("rules", [])}
        if not {"deletion", "non_fast_forward", "pull_request", "required_status_checks"}.issubset(kinds):
            print(f"INCOMPLETE branch rules for {branch}")
            return False
    labels = {x["name"] for x in request("GET", "/labels?per_page=100", token)}
    missing = set(LABELS) - labels
    if missing:
        print(f"MISSING labels: {', '.join(sorted(missing))}")
        return False
    print("Verified active rulesets, prevention of force pushes and expected labels")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MultAgent GitHub governance administration")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--plan", action="store_true")
    group.add_argument("--apply", action="store_true")
    group.add_argument("--verify", action="store_true")
    args = parser.parse_args(argv)
    if args.plan:
        print(json.dumps({"rulesets": [planned_ruleset(b) for b in ("dev", "hml", "main")],
                          "labels": LABELS}, indent=2))
        return 0
    token = os.environ.get("GH_ADMIN_TOKEN", "")
    if not token:
        print("GH_ADMIN_TOKEN required from an authorized administrator", file=sys.stderr)
        return 2
    try:
        if args.apply:
            apply(token)
        return 0 if verify(token) else 1
    except (HTTPError, URLError, OSError, ValueError, KeyError) as exc:
        print(f"GitHub governance operation failed: {type(exc).__name__}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
