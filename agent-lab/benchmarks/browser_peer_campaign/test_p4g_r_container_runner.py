from __future__ import annotations

import json
from pathlib import Path

from p4g_r_container_runner import main


def test_p4g_r_container_runner_blocks_without_container_runtime(tmp_path: Path, monkeypatch):
    out_dir = tmp_path / "reports"
    monkeypatch.setattr(
        "sys.argv",
        [
            "p4g_r_container_runner.py",
            "--iterations",
            "3",
            "--container-runtime",
            "definitely-missing-container-runtime",
            "--out-dir",
            str(out_dir),
        ],
    )

    assert main() == 0

    rows = [
        json.loads(line)
        for line in (out_dir / "p4g_r_openclaw_container_results.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    summary = json.loads((out_dir / "p4g_r_container_summary.json").read_text(encoding="utf-8"))

    assert len(rows) == 13
    assert summary["final_decision"] == "D_campaign_inconclusive"
    assert summary["peer_real_runtime_executed"] is False
    assert summary["host_dependency_install"] is False
    assert summary["product_vendor_runtime_imported"] is False
    assert summary["fake_env_only"] is True
    assert summary["container_runtime"] is None
    assert all(row["execution_status"] == "blocked_no_container_runtime" for row in rows)
    assert all(row["run_count"] == 0 for row in rows)
    assert all(row["host_dependency_install"] is False for row in rows)
    assert all(row["product_vendor_runtime_imported"] is False for row in rows)
