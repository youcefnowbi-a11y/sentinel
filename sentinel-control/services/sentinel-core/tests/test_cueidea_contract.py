from __future__ import annotations

import json
from pathlib import Path

from sentinel.cueidea_bridge import normalize_validation_response
from sentinel.decision.debate import DebateOrchestrator
from sentinel.execution import ActionRunner, GTMPackGenerator
from sentinel.execution.gtm_quality import evaluate_gtm_pack_quality, input_from_gtm_pack
from sentinel.firewall import review_action
from sentinel.learning import TraceLedger
from sentinel.shared.db import InMemoryTraceRepository
from sentinel.shared.enums import ApprovalStatus, EvidenceType, TraceEventType, Verdict
from sentinel.shared.models import DecisionPlan


FIXTURE_ROOT = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "cueidea_reports"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))


def normalize_fixture(name: str):
    payload = load_fixture(name)
    return normalize_validation_response(payload, idea=payload["idea_text"])


def test_cueidea_report_import_preserves_critical_fields() -> None:
    result = normalize_fixture("strong_wtp_report.json")

    assert result.validation_id == "cue_val_strong_wtp_001"
    assert result.idea == "Tone-aware invoice follow-up assistant for freelance designers"
    assert result.verdict == "build"
    assert result.confidence == 0.84
    assert "Freelance designers" in result.summary
    assert len(result.evidence) >= 7
    assert any(item.url for item in result.evidence)
    assert any(item.quote for item in result.evidence)
    assert all(item.source for item in result.evidence)
    assert all(item.metadata.get("raw") for item in result.evidence)


def test_direct_adjacent_wtp_and_competitor_evidence_survive_import() -> None:
    result = normalize_fixture("strong_wtp_report.json")
    proof_tiers = {item.metadata.get("proof_tier") for item in result.evidence}
    evidence_types = {item.evidence_type for item in result.evidence}

    assert {"direct", "adjacent", "supporting"}.issubset(proof_tiers)
    assert result.direct_evidence_count >= 4
    assert result.adjacent_evidence_count >= 1
    assert result.wtp_signal_count == 2
    assert EvidenceType.WTP in evidence_types
    assert EvidenceType.COMPETITOR_COMPLAINT in evidence_types
    assert result.competitors[0].name == "InvoiceTool"
    assert result.competitors[0].evidence_refs == ["strong_comp_001"]
    assert result.trends[0].keyword == "late invoice reminders"


def test_missing_wtp_blocks_build_and_ready_quality() -> None:
    for fixture_name in ("weak_wtp_report.json", "noisy_low_evidence_report.json"):
        result = normalize_fixture(fixture_name)
        debate = DebateOrchestrator().debate(result.idea, result.evidence)
        pack = GTMPackGenerator().generate(result.idea, debate, result.evidence)
        quality_input = input_from_gtm_pack(pack)
        quality = evaluate_gtm_pack_quality(quality_input)

        assert result.wtp_signal_count == 0
        assert debate.decision != Verdict.BUILD
        assert quality.status == "needs_revision"
        assert "wtp" in quality_input.evidence_gaps
        assert any("wtp" in blocker.lower() for blocker in quality.blockers)


def test_noisy_evidence_is_downgraded_not_hidden() -> None:
    result = normalize_fixture("noisy_low_evidence_report.json")

    assert len(result.evidence) == 3
    assert result.direct_evidence_count == 0
    assert result.adjacent_evidence_count == 1
    assert result.wtp_signal_count == 0
    assert all(item.metadata.get("proof_tier") != "direct" for item in result.evidence)
    assert max(item.confidence for item in result.evidence) <= 0.35
    assert {item.source for item in result.evidence} >= {
        "scrape_batch_anon_42",
        "trend_scrape_anon_17",
        "forum_batch_anon_03",
    }


def test_competitor_gap_fixture_preserves_competitor_signals() -> None:
    result = normalize_fixture("competitor_gap_report.json")
    competitor_items = [item for item in result.evidence if item.evidence_type == EvidenceType.COMPETITOR_COMPLAINT]

    assert len(competitor_items) == 3
    assert len(result.competitors) == 2
    assert all(item.url for item in competitor_items)
    assert any("client-side onboarding accountability" in item.summary for item in competitor_items)


def test_end_to_end_cueidea_to_gtm_pack_trace_and_safe_execution(tmp_path) -> None:
    result = normalize_fixture("strong_wtp_report.json")
    debate = DebateOrchestrator().debate(result.idea, result.evidence)
    pack_generator = GTMPackGenerator()
    pack = pack_generator.generate(result.idea, debate, result.evidence)
    quality = evaluate_gtm_pack_quality(input_from_gtm_pack(pack))

    assert debate.decision == Verdict.BUILD
    assert quality.status == "ready"
    assert all(section.evidence_refs for section in pack.sections)

    repository = InMemoryTraceRepository()
    ledger = TraceLedger(repository)
    user_id = "test_user"
    run = ledger.create_run(
        user_id=user_id,
        input_idea=result.idea,
        metadata={"mode": "evidence_backed", "validation_id": result.validation_id},
    )
    ledger.record_trace(
        user_id=user_id,
        run_id=run.id,
        event_type=TraceEventType.CUEIDEA_IMPORTED,
        input_snapshot={"validation_id": result.validation_id, "source": "cueidea_fixture"},
        output_snapshot={"evidence_count": len(result.evidence)},
    )

    for evidence in result.evidence:
        ledger.record_evidence(user_id=user_id, run_id=run.id, evidence=evidence)

    actions = pack_generator.actions_for_pack(pack)
    plan = DecisionPlan(
        goal="Create evidence-backed GTM pack from CueIdea validation",
        evidence=result.evidence,
        reasoning_summary=debate.skeptical_challenge,
        proposed_actions=actions,
        confidence=debate.confidence,
        risk_score=34,
        verdict=debate.decision,
    )
    ledger.record_decision_plan(user_id=user_id, run_id=run.id, plan=plan)
    ledger.record_trace(
        user_id=user_id,
        run_id=run.id,
        event_type=TraceEventType.PACK_GENERATED,
        decision_snapshot={"decision": debate.decision.value, "confidence": debate.confidence},
        output_snapshot={"slug": pack.slug, "quality_status": quality.status, "quality_score": quality.score},
    )

    for section in pack.sections:
        ledger.record_generated_asset(
            user_id=user_id,
            run_id=run.id,
            asset_type=section.filename.removesuffix(".md").lower(),
            title=section.title,
            content=section.content,
            file_path=f"data/generated_projects/{pack.slug}/{section.filename}",
            evidence_refs=section.evidence_refs,
        )

    runner = ActionRunner(project_root=tmp_path)
    allowed_root = (tmp_path / "data/generated_projects").resolve()
    created_files: list[Path] = []
    disabled_tools = {"send_email", "browser_submit_form", "run_shell_command", "modify_code"}

    assert not any(action.tool in disabled_tools for action in actions)

    for action in actions:
        pending_review = review_action(action, evidence=result.evidence, project_root=tmp_path)
        ledger.record_action_proposal(
            user_id=user_id,
            run_id=run.id,
            action=action,
            dry_run_json=pending_review.dry_run.model_dump(mode="json") if pending_review.dry_run else {},
        )
        ledger.record_trace(
            user_id=user_id,
            run_id=run.id,
            event_type=TraceEventType.FIREWALL_REVIEWED,
            action_snapshot=pending_review.model_dump(mode="json"),
        )

        if action.tool == "prepare_email_draft":
            assert pending_review.allowed is False
            assert pending_review.requires_approval is True
            ledger.record_trace(
                user_id=user_id,
                run_id=run.id,
                event_type=TraceEventType.APPROVAL_RECORDED,
                action_snapshot={"action_id": action.id, "approval_status": ApprovalStatus.APPROVED.value},
            )
            review, output = runner.run(action, evidence=result.evidence, approval_status=ApprovalStatus.APPROVED)
            assert output["status"] == "draft_created"
            assert output["sent"] == "false"
        else:
            review, output = runner.run(action, evidence=result.evidence)
            assert review.allowed is True
            if action.tool == "create_file":
                output_path = Path(output["path"]).resolve()
                created_files.append(output_path)
                assert output_path == allowed_root or allowed_root in output_path.parents

        ledger.record_trace(
            user_id=user_id,
            run_id=run.id,
            event_type=TraceEventType.ACTION_EXECUTED,
            action_snapshot=review.model_dump(mode="json"),
            output_snapshot=output,
        )

    assert len(created_files) == len(pack.sections)
    assert all(path.exists() for path in created_files)
    assert all("## Evidence refs" in path.read_text(encoding="utf-8") for path in created_files)
    assert all(asset["evidence_refs"] for asset in repository.list("generated_assets"))

    events = [row["event_type"] for row in repository.list("trace_records")]
    for required in (
        TraceEventType.RUN_STARTED.value,
        TraceEventType.CUEIDEA_IMPORTED.value,
        TraceEventType.EVIDENCE_RECORDED.value,
        TraceEventType.DECISION_CREATED.value,
        TraceEventType.PACK_GENERATED.value,
        TraceEventType.ASSET_GENERATED.value,
        TraceEventType.ACTION_PROPOSED.value,
        TraceEventType.FIREWALL_REVIEWED.value,
        TraceEventType.APPROVAL_RECORDED.value,
        TraceEventType.ACTION_EXECUTED.value,
    ):
        assert required in events
