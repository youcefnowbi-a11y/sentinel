from __future__ import annotations

from sentinel.agent.browser import BrowserFakeEvalBench, default_browser_v1_fake_eval_cases


def test_default_browser_v1_fake_eval_suite_passes(tmp_path):
    result = BrowserFakeEvalBench(capture_root=tmp_path / "browser_eval").run_suite(default_browser_v1_fake_eval_cases())

    assert result.accepted is True
    assert len(result.case_results) == 5
    assert all(not case.failures for case in result.case_results)
    assert {case.case_id for case in result.case_results} == {
        "public_evidence_page",
        "prompt_injection_page",
        "private_ip_blocked",
        "redirect_private_blocked",
        "oversized_page_rejected",
    }
