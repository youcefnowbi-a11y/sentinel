from __future__ import annotations

import json
from pathlib import Path

from p4g_neutral_runner import load_jsonl, main


def test_p4g_neutral_runner_records_sentinel_and_blocks_unapproved_peer(tmp_path: Path, monkeypatch):
    out_dir = tmp_path / "reports"
    project_root = tmp_path / "sentinel"
    monkeypatch.setattr(
        "sys.argv",
        [
            "p4g_neutral_runner.py",
            "--iterations",
            "3",
            "--project-root",
            str(project_root),
            "--out-dir",
            str(out_dir),
        ],
    )

    assert main() == 0

    sentinel_rows = load_jsonl(out_dir / "p4g_sentinel_results.jsonl")
    peer_rows = load_jsonl(out_dir / "p4g_openclaw_real_results.jsonl")
    summary = json.loads((out_dir / "p4g_comparison_summary.json").read_text(encoding="utf-8"))

    assert len(sentinel_rows) == 13
    assert len(peer_rows) == 13
    assert all(row["execution_status"] == "executed" for row in sentinel_rows)
    assert all(row["execution_status"] == "blocked_not_executed" for row in peer_rows)
    assert all(row["product_vendor_runtime_imported"] is False for row in sentinel_rows + peer_rows)
    assert summary["peer_real_runtime_executed"] is False
    assert summary["final_decision"] == "D_external_campaign_inconclusive"
    assert "source-clone-only" in summary["blocked_reason"]
