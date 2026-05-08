from __future__ import annotations

import json
from pathlib import Path


def test_browser_fluency_mission_catalog_is_complete_and_unique():
    path = Path(__file__).with_name("browser_fluency_missions.json")
    catalog = json.loads(path.read_text(encoding="utf-8"))

    missions = [mission for group in catalog["groups"] for mission in group["missions"]]
    mission_ids = [mission["id"] for mission in missions]

    assert catalog["schema_version"] == "browser_fluency_missions.v1"
    assert catalog["mission_count"] == 72
    assert len(catalog["groups"]) == 12
    assert len(missions) == catalog["mission_count"]
    assert len(mission_ids) == len(set(mission_ids))
    assert all(mission["expected_proof"] for mission in missions)
    assert {mission["level"] for mission in missions} <= {"F0", "F1", "F2", "F3", "F4", "F5"}


def test_browser_fluency_mission_catalog_covers_browser_fluency_surfaces():
    path = Path(__file__).with_name("browser_fluency_missions.json")
    catalog = json.loads(path.read_text(encoding="utf-8"))
    capabilities = {mission["capability"] for group in catalog["groups"] for mission in group["missions"]}

    required = {
        "allowed_url_navigation",
        "viewport_screenshot",
        "image_ocr",
        "safe_form_submit",
        "private_session",
        "redacted_storage_summary",
        "download_quarantine",
        "upload_artifact",
        "har_redaction",
        "js_network_rejection",
        "multi_tab_compare",
        "hard_to_find_info",
        "prompt_injection_detection",
        "loop_detector",
        "llm_draft_boundary",
    }

    assert required <= capabilities
