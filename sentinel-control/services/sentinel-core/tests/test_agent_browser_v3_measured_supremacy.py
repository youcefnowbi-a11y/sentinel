from __future__ import annotations

import pytest

from sentinel.agent.browser import BrowserV3MeasuredMissionGroup, BrowserV3MeasuredSupremacyGate


def test_p4c_s_cases_cover_required_browser_v3_groups(tmp_path):
    gate = BrowserV3MeasuredSupremacyGate(project_root=tmp_path, iterations=1, use_live_harness=True)

    groups = {case.user_input["mission_group"] for case in gate.cases()}

    assert groups == {group.value for group in BrowserV3MeasuredMissionGroup}
    assert len(gate.cases()) == 9


def test_p4c_s_measured_supremacy_gate_runs_multi_run_corpus(tmp_path):
    pytest.importorskip("playwright.sync_api")

    report = BrowserV3MeasuredSupremacyGate(project_root=tmp_path, iterations=2, use_live_harness=True).run()

    assert report.suite_accepted is True
    assert report.case_count == 9
    assert report.iterations == 2
    assert report.verdict == "browser_v3_ready_for_next_organ"
    assert report.measured_success_rate == 1.0
    assert report.measured_acceptance_rate == 1.0
    assert {score.mission_group for score in report.scores} == set(BrowserV3MeasuredMissionGroup)
    for score in report.scores:
        assert score.run_count == 2
        assert score.accepted_rate == 1.0
        assert score.success_rate == 1.0
        assert score.unstable_iterations == []
        assert score.trace_quality == 1.0
        assert score.proof_completeness == 1.0
        assert score.side_effect_containment == 1.0
