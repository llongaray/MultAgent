"""Unit tests for actual GitHub ruleset payloads and promotion policy."""
from scripts.governance.promotion_gate import validate
from scripts.governance.rulesets import CI_CONTEXTS, LABELS, planned_ruleset


def event(base: str, head: str, repo: str = "llongaray/MultAgent") -> dict:
    return {"pull_request": {"draft": False,
            "base": {"ref": base, "repo": {"full_name": "llongaray/MultAgent"}},
            "head": {"ref": head, "repo": {"full_name": repo}}}}


def test_branch_gate_allowlist():
    for base, head in (("dev", "feat/p9-desktop"), ("dev", "ops/protections"),
                       ("hml", "dev"), ("main", "hml")):
        assert validate(event(base, head))[0]
    for base, head in (("dev", "main"), ("dev", "hml"), ("hml", "feat/foo"),
                       ("main", "dev"), ("main", "feat/foo"), ("main", "main")):
        assert not validate(event(base, head))[0]
    assert not validate(event("main", "hml", "other/fork"))[0]
    assert not validate({})[0]
    draft = event("main", "hml")
    draft["pull_request"]["draft"] = True
    assert not validate(draft)[0]


def test_protection_payload():
    for name in ("dev", "hml", "main"):
        ruleset = planned_ruleset(name)
        assert ruleset["enforcement"] == "active"
        assert ruleset["conditions"]["ref_name"]["include"] == [f"refs/heads/{name}"]
        kinds = {x["type"]: x for x in ruleset["rules"]}
        assert "non_fast_forward" in kinds and "deletion" in kinds
        contexts = kinds["required_status_checks"]["parameters"]["required_status_checks"]
        assert {x["context"] for x in contexts} == set(CI_CONTEXTS)
        reviews = kinds["pull_request"]["parameters"]["required_approving_review_count"]
        assert reviews == (1 if name == "main" else 0)
    assert set(f"P{i}" for i in range(10)).issubset(LABELS)
