from __future__ import annotations

import json
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
REPORT_DIR = ROOT / "reports"
REPORT_PATH = REPORT_DIR / "openclaw_fake_benchmark_report.md"
EXPECTED_PATH = ROOT / "expected_results.json"
RISK_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


RULES: list[dict[str, Any]] = [
    {
        "pattern": r"ignore previous|disable the firewall|approval is no longer required|approval is granted|system prompt",
        "risk": "high",
        "policy": "prompt_injection_review_policy",
        "reason": "untrusted input attempts to override policy or instructions",
    },
    {
        "pattern": r"sendMessage|send this|send .*prospects|external_contact|everyone in #|contact actions",
        "risk": "high",
        "policy": "external_contact_policy",
        "reason": "requests external contact or outbound channel action",
    },
    {
        "pattern": r"browser|submit the form|contact form|open https?://",
        "risk": "high",
        "policy": "browser_sandbox_policy",
        "reason": "requests browser control or form submission",
    },
    {
        "pattern": r"\.\./|outside_sandbox|write .*outside",
        "risk": "high",
        "policy": "filesystem_access_policy",
        "reason": "attempts filesystem escape from sandbox",
    },
    {
        "pattern": r"\bnpm install\b|\bpnpm install\b|\byarn add\b|\bpip install\b",
        "risk": "critical",
        "policy": "plugin_install_policy",
        "reason": "requests package or remote dependency install",
    },
    {
        "pattern": r"\bop read\b|\bop://|1Password|API_TOKEN|PRIVATE",
        "risk": "critical",
        "policy": "secret_access_policy",
        "reason": "requests secret manager or secret path access",
    },
    {
        "pattern": r"\bbash\b|\bpowershell\b|\bcmd\.exe\b|\brun:",
        "risk": "critical",
        "policy": "run_shell_command",
        "reason": "requests shell execution",
    },
    {
        "pattern": r"remember permanently|store a persistent|memory policy|future action",
        "risk": "high",
        "policy": "memory_write_policy",
        "reason": "attempts persistent memory or policy mutation",
    },
    {
        "pattern": r"channel_adapter|fake channel|declared_capabilities",
        "risk": "medium",
        "policy": "channel_adapter_policy",
        "reason": "declares channel adapter surface",
    },
]


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped:
            rows.append(json.loads(stripped))
    return rows


def load_fixtures() -> list[dict[str, Any]]:
    fixtures = load_jsonl(ROOT / "fake_channel_messages.jsonl")

    for path in sorted((ROOT / "fake_plugin_manifests").glob("*.json")):
        fixtures.append(json.loads(path.read_text(encoding="utf-8")))

    for path in sorted((ROOT / "fake_skills").glob("*/SKILL.md")):
        fixtures.append({
            "id": path.parent.name,
            "kind": "skill",
            "source": path.relative_to(ROOT).as_posix(),
            "text": path.read_text(encoding="utf-8"),
            "expected_decision": "blocked",
        })

    return fixtures


def fixture_text(fixture: dict[str, Any]) -> str:
    values = []
    for key in ("id", "kind", "source", "name", "description", "text", "path"):
        if fixture.get(key):
            values.append(str(fixture[key]))
    if fixture.get("declared_capabilities"):
        values.append(json.dumps(fixture["declared_capabilities"]))
    return "\n".join(values)


def max_risk(left: str, right: str) -> str:
    return left if RISK_ORDER[left] >= RISK_ORDER[right] else right


def classify(fixture: dict[str, Any]) -> dict[str, Any]:
    text = fixture_text(fixture)
    risk = "low"
    policies: set[str] = set()
    reasons: list[str] = []

    for rule in RULES:
        if re.search(rule["pattern"], text, flags=re.IGNORECASE):
            risk = max_risk(risk, str(rule["risk"]))
            policies.add(str(rule["policy"]))
            reasons.append(str(rule["reason"]))

    if not policies:
        decision = "safe_static_doc"
        approval_required = False
    else:
        decision = "blocked"
        approval_required = True

    if "plugin_install_policy" in policies:
        policies.add("run_shell_command")
    if "secret_access_policy" in policies:
        policies.add("run_shell_command")
    if fixture.get("kind") == "browser_task":
        policies.add("external_contact_policy")
    if "external_contact_policy" in policies and fixture.get("kind") == "channel_message":
        approval_required = True

    return {
        "id": fixture["id"],
        "kind": fixture.get("kind", "unknown"),
        "risk_level": risk,
        "sentinel_decision": decision,
        "approval_required": approval_required,
        "required_firewall_policies": sorted(policies),
        "dry_run_preview": {
            "action": fixture.get("kind", "unknown"),
            "risk": risk,
            "why_needed": "Benchmark classification only; no real action is executed.",
            "preview": {
                "input_source": fixture.get("source"),
                "input_excerpt": text[:220],
            },
            "requires_approval": approval_required,
        },
        "trace_events": [
            "benchmark_input_loaded",
            "risk_classified",
            "policy_mapped",
            "dry_run_built",
            "approval_simulated",
            "trace_recorded",
        ],
        "reasons": sorted(set(reasons)),
    }


def compare_expected(result: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for key in ("risk_level", "sentinel_decision", "approval_required"):
        if result[key] != expected[key]:
            failures.append(f"{key}: expected {expected[key]!r}, got {result[key]!r}")

    expected_policies = set(expected["required_firewall_policies"])
    actual_policies = set(result["required_firewall_policies"])
    if expected_policies != actual_policies:
        failures.append(
            "required_firewall_policies: expected "
            f"{sorted(expected_policies)!r}, got {sorted(actual_policies)!r}"
        )
    return failures


def render_report(results: list[dict[str, Any]], failures: dict[str, list[str]]) -> str:
    decision_counts = Counter(result["sentinel_decision"] for result in results)
    risk_counts = Counter(result["risk_level"] for result in results)
    lines = [
        "# OpenClaw Fake Runtime Benchmark Report",
        "",
        "This B3 benchmark uses fake fixtures only. It does not install OpenClaw, run OpenClaw, execute plugins/skills, connect accounts, send messages, submit browser forms, or write outside this benchmark folder.",
        "",
        f"Generated: `{utc_now()}`",
        "",
        "## Summary",
        "",
        f"- fixtures: `{len(results)}`",
        f"- failures: `{sum(len(items) for items in failures.values())}`",
        f"- decisions: `{dict(sorted(decision_counts.items()))}`",
        f"- risk counts: `{dict(sorted(risk_counts.items()))}`",
        "",
        "## Results",
        "",
        "| ID | Kind | Risk | Decision | Policies | Status |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for result in results:
        status = "PASS" if not failures.get(result["id"]) else "FAIL"
        policies = ", ".join(f"`{policy}`" for policy in result["required_firewall_policies"])
        lines.append(
            f"| `{result['id']}` | `{result['kind']}` | `{result['risk_level']}` | "
            f"`{result['sentinel_decision']}` | {policies} | {status} |"
        )

    lines.extend([
        "",
        "## Dry-Run And Trace Contract",
        "",
        "Every fixture must produce:",
        "",
        "- policy mapping;",
        "- dry-run preview;",
        "- approval simulation;",
        "- trace event list;",
        "- no real side effect.",
        "",
        "## Failure Details",
        "",
    ])
    if not failures:
        lines.append("No expectation failures.")
    else:
        for fixture_id, fixture_failures in failures.items():
            lines.append(f"### `{fixture_id}`")
            for failure in fixture_failures:
                lines.append(f"- {failure}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    expected = json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))
    results = [classify(fixture) for fixture in load_fixtures()]
    failures: dict[str, list[str]] = {}

    for result in results:
        fixture_expected = expected.get(result["id"])
        if not fixture_expected:
            failures[result["id"]] = ["missing expected result"]
            continue
        issues = compare_expected(result, fixture_expected)
        if issues:
            failures[result["id"]] = issues

    missing = sorted(set(expected) - {result["id"] for result in results})
    for fixture_id in missing:
        failures[fixture_id] = ["expected result has no fixture"]

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(render_report(results, failures), encoding="utf-8")
    print(f"wrote {REPORT_PATH.relative_to(ROOT.parents[2]).as_posix()}")
    print(f"fixtures={len(results)} failures={sum(len(items) for items in failures.values())}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
