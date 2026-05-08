from __future__ import annotations

import json
import re
from pathlib import Path

from sentinel.cueidea_bridge import normalize_validation_response
from sentinel.decision.debate import DebateOrchestrator
from sentinel.decision.research_enrichment import enrich_research
from sentinel.execution import GTMPackGenerator
from sentinel.execution.gtm_quality import evaluate_gtm_pack_quality, input_from_gtm_pack


FIXTURE_ROOT = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "cueidea_reports"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))


def build_pack(name: str):
    payload = load_fixture(name)
    result = normalize_validation_response(payload, idea=payload["idea_text"])
    enrichment = enrich_research(result.evidence)
    debate = DebateOrchestrator().debate(result.idea, result.evidence)
    pack = GTMPackGenerator().generate(result.idea, debate, result.evidence, enrichment=enrichment)
    quality = evaluate_gtm_pack_quality(input_from_gtm_pack(pack))
    return result, enrichment, pack, quality


def section(pack, filename: str):
    return next(item for item in pack.sections if item.filename == filename)


def test_vague_icp_triggers_needs_revision() -> None:
    _, enrichment, pack, quality = build_pack("vague_icp_report.json")

    assert "icp" in enrichment.evidence_gaps
    assert "EVIDENCE_GAP: icp" in section(pack, "02_ICP.md").content
    assert quality.status == "needs_revision"
    assert any("icp" in blocker.lower() for blocker in quality.blockers)


def test_strong_community_evidence_improves_pack_specificity() -> None:
    _, enrichment, pack, quality = build_pack("strong_icp_community_report.json")
    prospect_sources = section(pack, "10_PROSPECT_SOURCES.md")

    assert "communities" not in enrichment.evidence_gaps
    assert any("r/freelance" in signal.label.lower() or "designer hangout" in signal.label.lower() for signal in enrichment.communities)
    assert "r/freelance" in prospect_sources.content or "Designer Hangout" in prospect_sources.content
    assert quality.status == "ready"


def test_missing_competitor_gap_creates_evidence_gap() -> None:
    _, enrichment, pack, quality = build_pack("noisy_low_evidence_report.json")

    assert "competitor_gap" in enrichment.evidence_gaps
    assert "EVIDENCE_GAP: competitor_gap" in section(pack, "03_COMPETITOR_GAPS.md").content
    assert quality.status == "needs_revision"


def test_strong_wtp_direct_pain_and_competitor_weakness_can_be_ready() -> None:
    _, enrichment, pack, quality = build_pack("strong_competitor_gap_report.json")

    assert "wtp" not in enrichment.evidence_gaps
    assert "competitor_gap" not in enrichment.evidence_gaps
    assert any(signal.label == "Asana" for signal in enrichment.competitors)
    assert quality.status == "ready"
    assert quality.blockers == []
    assert "Asana" in section(pack, "03_COMPETITOR_GAPS.md").content


def test_roadmap_actions_are_measurable() -> None:
    _, _, pack, _ = build_pack("strong_icp_community_report.json")
    roadmap = section(pack, "07_7_DAY_ROADMAP.md").content.lower()

    assert all(token in roadmap for token in ("day 1", "day 2", "day 3", "day 7"))
    assert re.search(r"\b10 prospects\b", roadmap)
    assert re.search(r"\b5\b.*interview|interview\s+5", roadmap)
    assert re.search(r"\b3 alternatives\b", roadmap)
    assert re.search(r"\b2 landing headlines\b", roadmap)


def test_outreach_includes_evidence_refs_and_pain_trigger() -> None:
    _, enrichment, pack, _ = build_pack("strong_objection_report.json")
    outreach = section(pack, "05_OUTREACH_MESSAGES.md")

    assert outreach.evidence_refs
    assert "post-call follow-up" in outreach.content.lower() or "privacy" in outreach.content.lower()
    assert "Reply stop if not relevant" in outreach.content
    assert enrichment.objections
