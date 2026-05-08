from __future__ import annotations

import hashlib
import json
from pathlib import Path

from sentinel.agent import AgentEventType, AgentRuntime, CoreFinalGate, EventBus, RepairDecisionType
from sentinel.agent.browser import (
    BrowserAccessibilitySnapshotBuilder,
    BrowserFormSubmitBackendResult,
    BrowserFormSubmitRequest,
    BrowserInteractionDryRunPlanner,
    BrowserInteractionIntent,
    BrowserInteractionStep,
    BrowserInteractionTarget,
    BrowserOperatorRuntimeRoute,
    BrowserRenderedPage,
    BrowserUIObservationBuilder,
    BrowserV3AuthorityClass,
    BrowserV3AuthorityGrant,
)
from sentinel.agent.phases import AgentPhase
from sentinel.capabilities import default_tool_registry
from sentinel.mission import MissionAction, MissionAuthorityEnvelope, MissionPlan, MissionPlanStep, MissionRunner
from sentinel.mission.models import utc_now
from sentinel.shared.enums import ConfidenceLevel, ExternalityLevel, MissionMode, MissionStatus, MissionType, ReversibilityLevel, SensitivityLevel


MISSION_ID = "mission_p4h_ae_browser_runtime_integration"
SAFE_GTM_ACTIONS = [
    "create_project_folder",
    "generate_gtm_pack",
    "generate_landing_copy",
    "generate_outreach_drafts_without_sending",
    "create_watchlist",
    "generate_research_questions",
]
PNG_BYTES = b"\x89PNG\r\n\x1a\nfake"


def grant() -> BrowserV3AuthorityGrant:
    return BrowserV3AuthorityGrant(
        id="grant_browser_form_submit",
        authority_class=BrowserV3AuthorityClass.FORM_SUBMIT,
        allowed_domains=["example.com"],
        max_uses=5,
    )


def envelope(**overrides) -> MissionAuthorityEnvelope:
    data = {
        "id": MISSION_ID,
        "user_id": "user_p4h_ae",
        "mission_type": MissionType.GTM,
        "mission_title": "P4H-AE Browser Runtime Integration",
        "mission_objective": "Route a Browser V3 action through the runtime operator path.",
        "success_criteria": ["Runtime operator route executes with receipt and FinalGate proof."],
        "mode": MissionMode.POWER,
        "allowed_systems": ["local_workspace", "public_web"],
        "allowed_tools": ["safe_file_writer", "browser_public_form_submit"],
        "allowed_actions": [*SAFE_GTM_ACTIONS, "browser_form_submit"],
        "forbidden_actions": ["payment", "credential_access"],
        "allowed_paths": ["data/generated_projects"],
        "allowed_domains": ["example.com"],
        "browser_v3_authority_grants": [grant().model_dump(mode="json")],
        "risk_appetite_score": 90,
        "max_actions": 30,
        "max_duration_minutes": 10,
        "max_cost_usd": 1.0,
    }
    data.update(overrides)
    return MissionAuthorityEnvelope(**data)


def snapshot():
    return BrowserAccessibilitySnapshotBuilder().build(
        html="""
        <html><body>
          <main>
            <h1>Contact</h1>
            <input type="text" placeholder="Email" />
            <button>Send request</button>
          </main>
        </body></html>
        """,
        text="Contact Email Send request",
    )


def first_ref(snap, role: str) -> str:
    for ref_id, ref in snap.refs.items():
        if ref.role == role:
            return ref_id
    raise AssertionError(f"missing ref for role {role}")


def snapshot_event(bus: EventBus, snap) -> str:
    event = bus.append(
        AgentEventType.BROWSER_SNAPSHOT_CAPTURED,
        "Rendered browser snapshot captured for test setup.",
        phase_before=AgentPhase.EXECUTING,
        phase_after=AgentPhase.EXECUTING,
        payload={
            "receipt_id": "receipt_snapshot",
            "snapshot_artifact_id": "artifact_snapshot",
            "snapshot_artifact_sha256": "a" * 64,
            "accessibility_snapshot_sha256": snap.snapshot_sha256,
            "accessibility_page_sha256": snap.page_sha256,
            "accessibility_ref_count": snap.stats.refs,
            "accessibility_interactive_count": snap.stats.interactive,
            "accessibility_ref_ids": sorted(snap.refs),
        },
    )
    return event.id


def form_plan(snap):
    bus = EventBus(MISSION_ID)
    snap_trace = snapshot_event(bus, snap)
    textbox = first_ref(snap, "textbox")
    button = first_ref(snap, "button")
    result = BrowserInteractionDryRunPlanner().create_plan(
        mission_id=MISSION_ID,
        snapshot=snap,
        steps=[
            BrowserInteractionStep(
                intent=BrowserInteractionIntent.FILL_PLAN,
                target=BrowserInteractionTarget(ref=textbox),
                text="operator@example.com",
                reason="Fill public fixture field.",
            ),
            BrowserInteractionStep(
                intent=BrowserInteractionIntent.CLICK_PLAN,
                target=BrowserInteractionTarget(ref=button),
                reason="Submit fixture form.",
            ),
        ],
        event_bus=bus,
        final_url="https://example.com/form",
        snapshot_trace_id=snap_trace,
    )
    assert result.accepted is True
    assert result.plan is not None
    assert result.trace_event_id is not None
    return result.plan, result.trace_event_id, snap_trace, textbox, button


def ui_observation_set(snap):
    return BrowserUIObservationBuilder().from_accessibility_snapshot(
        mission_id=MISSION_ID,
        url="https://example.com/form",
        snapshot=snap,
    )


def browser_tool_call() -> dict:
    snap = snapshot()
    plan, plan_trace, snap_trace, textbox, button = form_plan(snap)
    arguments = {
        "ui_observation_set": ui_observation_set(snap).model_dump(mode="json"),
        "target_ref_id": button,
        "ref_id": button,
        "plan": plan.model_dump(mode="json"),
        "authority_grant_id": "grant_browser_form_submit",
        "context_pack_id": "cpk_p4h_ae_runtime",
        "plan_trace_event_id": plan_trace,
        "before_snapshot_trace_event_id": snap_trace,
        "final_url": "https://example.com/form",
        "form_ref_id": textbox,
        "submit_ref_id": button,
        "expected_effect": "confirmation text appears",
        "allowed_domains": ["example.com"],
        "capture_screenshot": True,
    }
    return {
        "tool_id": "browser_public_form_submit",
        "action": "browser_form_submit",
        "capability": "public_web_form_submit",
        "target": "https://example.com/form",
        "requested_side_effects": [
            "network_read",
            "network_write",
            "browser_read",
            "browser_submit",
            "filesystem_write",
            "local_draft_write",
        ],
        "arguments": arguments,
    }


class FakeFormSubmitBackend:
    def __init__(self, before_snapshot) -> None:
        self.before_snapshot = before_snapshot

    def __call__(self, request: BrowserFormSubmitRequest) -> BrowserFormSubmitBackendResult:
        return BrowserFormSubmitBackendResult(
            before_snapshot=self.before_snapshot,
            after_page=BrowserRenderedPage(
                final_url="https://example.com/form",
                status_code=200,
                title="Submitted",
                text="Thanks, confirmation text appears.",
                links=[],
                html="<html><body><main><h1>Thanks, confirmation text appears.</h1></main></body></html>",
                screenshot_png=PNG_BYTES,
            ),
            final_url_before=request.final_url,
            final_url_after="https://example.com/form",
            submitted=True,
            submitted_ref_ids=[request.form_ref_id, request.submit_ref_id],
        )


class SequenceFormSubmitBackend:
    def __init__(self, before_snapshot, submitted_sequence: list[bool]) -> None:
        self.before_snapshot = before_snapshot
        self.submitted_sequence = submitted_sequence
        self.calls = 0

    def __call__(self, request: BrowserFormSubmitRequest) -> BrowserFormSubmitBackendResult:
        submitted = self.submitted_sequence[min(self.calls, len(self.submitted_sequence) - 1)]
        self.calls += 1
        return BrowserFormSubmitBackendResult(
            before_snapshot=self.before_snapshot,
            after_page=BrowserRenderedPage(
                final_url="https://example.com/form",
                status_code=200,
                title="Submitted" if submitted else "Still editing",
                text="Thanks, confirmation text appears." if submitted else "The form is still open.",
                links=[],
                html=(
                    "<html><body><main><h1>Thanks, confirmation text appears.</h1></main></body></html>"
                    if submitted
                    else "<html><body><main><h1>The form is still open.</h1></main></body></html>"
                ),
                screenshot_png=PNG_BYTES,
            ),
            final_url_before=request.final_url,
            final_url_after="https://example.com/form",
            submitted=submitted,
            submitted_ref_ids=[request.form_ref_id, request.submit_ref_id] if submitted else [],
        )


def operator_route(tmp_path: Path, form_submit_backend=None) -> BrowserOperatorRuntimeRoute:
    return BrowserOperatorRuntimeRoute(
        registry=default_tool_registry(),
        capture_root=tmp_path / "captures",
        form_submit_backend=form_submit_backend or FakeFormSubmitBackend(snapshot()),
    )


def browser_route_action(env: MissionAuthorityEnvelope, project_path: str = "data/generated_projects/p4h-ae-mission-runner") -> MissionAction:
    call = browser_tool_call()
    raw = {
        **call,
        "canonical_hash": hashlib.sha256(
            json.dumps(call, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
    }
    return MissionAction(
        mission_id=env.id,
        action_type="browser_operator_route",
        tool="browser_public_form_submit",
        intent="Invoke the compiled browser operator route from MissionRunner.",
        target=project_path,
        input={"tool_call": raw},
        expected_output="Browser operator route executed.",
        reversibility=ReversibilityLevel.STATE_MUTATING_RECOVERABLE,
        externality=ExternalityLevel.INTERNAL_LOCAL,
        sensitivity=SensitivityLevel.INTERNAL,
        confidence=ConfidenceLevel.HIGH,
    )


def research_summary_action(
    env: MissionAuthorityEnvelope,
    *,
    project_path: str = "data/generated_projects/p4h-ae-mission-runner",
    filename: str = "RESEARCH_SUMMARY.md",
    content: str = "# Research Summary\n\nEvidence refs\n\n- ev_runtime_route\n",
) -> MissionAction:
    return MissionAction(
        mission_id=env.id,
        action_type="create_markdown_file",
        tool="safe_file_writer",
        intent=f"Write bounded research summary artifact `{filename}` after browser route.",
        target=project_path,
        input={
            "filename": filename,
            "artifact_type": "research_summary",
            "content": content,
        },
        expected_output=f"{filename} exists.",
        reversibility=ReversibilityLevel.LOCAL_WRITE_REVERSIBLE,
        externality=ExternalityLevel.INTERNAL_LOCAL,
        sensitivity=SensitivityLevel.INTERNAL,
        confidence=ConfidenceLevel.HIGH,
        evidence_refs=["ev_runtime_route"],
    )


def browser_route_plan(
    env: MissionAuthorityEnvelope,
    *,
    include_third_step: bool = False,
    summary_content: str = "# Research Summary\n\nEvidence refs\n\n- ev_runtime_route\n",
) -> MissionPlan:
    route_action = browser_route_action(env)
    summary_action = research_summary_action(env, content=summary_content)
    steps = [
        MissionPlanStep(id="browser_operator_route", action=route_action),
        MissionPlanStep(
            id="write_summary",
            depends_on=["browser_operator_route"],
            action=summary_action,
            expected_artifact="RESEARCH_SUMMARY.md",
        ),
    ]
    if include_third_step:
        steps.append(
            MissionPlanStep(
                id="write_extra_summary",
                depends_on=["write_summary"],
                action=research_summary_action(
                    env,
                    filename="RESEARCH_SUMMARY_EXTRA.md",
                    content="# Extra Summary\n\nEvidence refs\n\n- ev_runtime_route\n",
                ),
                expected_artifact="RESEARCH_SUMMARY_EXTRA.md",
            )
        )
    return MissionPlan(mission_id=env.id, steps=steps)


def runtime_with_plan(tmp_path: Path, env: MissionAuthorityEnvelope, plan: MissionPlan, route: BrowserOperatorRuntimeRoute) -> AgentRuntime:
    runtime = AgentRuntime(project_root=tmp_path, browser_operator_route=route)

    def create_plan(*args, **kwargs):
        return runtime.planner_bridge._attach_verified_hypotheses(plan, kwargs.get("verified_hypotheses") or [])

    runtime.planner_bridge.create_plan = create_plan
    return runtime


def test_agent_runtime_routes_browser_v3_action_through_action_engine_and_finalgate(tmp_path):
    env = envelope()
    result = AgentRuntime(project_root=tmp_path, browser_operator_route=operator_route(tmp_path)).run(
        env,
        {"idea": "P4H-AE runtime route", "tool_calls": [browser_tool_call()]},
        evidence_refs=["ev_runtime_route"],
    )

    event_types = [event.event_type for event in result.trace]
    assert AgentEventType.BROWSER_OPERATOR_ROUTE_STARTED in event_types
    assert AgentEventType.BROWSER_OPERATOR_ROUTE_PREPARED in event_types
    assert AgentEventType.BROWSER_OPERATOR_ROUTE_COMPLETED in event_types
    assert AgentEventType.BROWSER_FORM_SUBMIT_EXECUTED in event_types
    assert result.controlled_capability_results[0]["accepted"] is True
    assert result.controlled_capability_results[0]["operator_route"]["status"] == "executed"

    gate = CoreFinalGate().evaluate(result, allowed_project_root=tmp_path)
    assert gate.accepted is True


def test_agent_runtime_rejects_operator_route_without_compiled_policy_authority(tmp_path):
    env = envelope(allowed_actions=[*SAFE_GTM_ACTIONS], browser_v3_authority_grants=[])
    result = AgentRuntime(project_root=tmp_path, browser_operator_route=operator_route(tmp_path)).run(
        env,
        {"idea": "P4H-AE rejected route", "tool_calls": [browser_tool_call()]},
        evidence_refs=["ev_runtime_route"],
    )

    rejected = result.controlled_capability_results[0]
    assert rejected["accepted"] is False
    assert rejected["operator_route"]["status"] == "rejected"
    assert rejected["reason"].startswith("browser_operator_prepare_failed")
    assert "action_class_out_of_scope" in rejected["errors"]
    assert AgentEventType.BROWSER_FORM_SUBMIT_EXECUTED not in [event.event_type for event in result.trace]


def test_mission_runner_can_invoke_browser_operator_route_as_compiled_mission_action(tmp_path):
    call = browser_tool_call()
    raw = {
        **call,
        "canonical_hash": hashlib.sha256(
            json.dumps(call, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
    }
    env = envelope(
        mission_type=MissionType.RESEARCH_SUMMARY,
        allowed_actions=[*SAFE_GTM_ACTIONS, "browser_operator_route", "browser_form_submit", "create_markdown_file"],
        allowed_tools=["browser_public_form_submit", "safe_file_writer"],
    )
    project_path = "data/generated_projects/p4h-ae-mission-runner"
    route_action = MissionAction(
        mission_id=env.id,
        action_type="browser_operator_route",
        tool="browser_public_form_submit",
        intent="Invoke the compiled browser operator route from MissionRunner.",
        target=project_path,
        input={"tool_call": raw},
        expected_output="Browser operator route executed.",
        reversibility=ReversibilityLevel.STATE_MUTATING_RECOVERABLE,
        externality=ExternalityLevel.INTERNAL_LOCAL,
        sensitivity=SensitivityLevel.INTERNAL,
        confidence=ConfidenceLevel.HIGH,
    )
    summary_action = MissionAction(
        mission_id=env.id,
        action_type="create_markdown_file",
        tool="safe_file_writer",
        intent="Write bounded research summary after browser route.",
        target=project_path,
        input={
            "filename": "RESEARCH_SUMMARY.md",
            "artifact_type": "research_summary",
            "content": "# Research Summary\n\nEvidence refs\n\n- ev_runtime_route\n",
        },
        expected_output="Research summary exists.",
        reversibility=ReversibilityLevel.LOCAL_WRITE_REVERSIBLE,
        externality=ExternalityLevel.INTERNAL_LOCAL,
        sensitivity=SensitivityLevel.INTERNAL,
        confidence=ConfidenceLevel.HIGH,
        evidence_refs=["ev_runtime_route"],
    )
    plan = MissionPlan(
        mission_id=env.id,
        steps=[
            MissionPlanStep(id="browser_operator_route", action=route_action),
            MissionPlanStep(id="write_summary", depends_on=["browser_operator_route"], action=summary_action, expected_artifact="RESEARCH_SUMMARY.md"),
        ],
    )

    result = MissionRunner(project_root=tmp_path, browser_operator_route=operator_route(tmp_path)).run_mission(
        env,
        evidence_refs=["ev_runtime_route"],
        plan=plan,
    )

    assert result.success is True
    assert result.state.status == MissionStatus.COMPLETED
    executed_route = next(event for event in result.trace_events if event.action_id == route_action.id and event.result.get("type") == "browser_operator_route")
    assert executed_route.result["accepted"] is True
    assert executed_route.result["operator_trace_certified"] is True


def test_repair_loop_recovers_after_browser_failure_then_succeeds(tmp_path):
    env = envelope(
        mission_type=MissionType.RESEARCH_SUMMARY,
        allowed_actions=[*SAFE_GTM_ACTIONS, "browser_operator_route", "browser_form_submit", "create_markdown_file"],
        allowed_tools=["browser_public_form_submit", "safe_file_writer"],
    )
    plan = browser_route_plan(env)
    backend = SequenceFormSubmitBackend(snapshot(), [False, True])
    result = runtime_with_plan(tmp_path, env, plan, operator_route(tmp_path, backend)).run(
        env,
        {"idea": "P4H-AE repair path"},
        evidence_refs=["ev_runtime_route"],
    )

    event_types = [event.event_type for event in result.trace]
    assert result.success is True
    assert result.repair_decision is not None
    assert result.repair_decision.decision == RepairDecisionType.REPAIR_ALLOWED
    assert AgentEventType.REPAIR_DECIDED in event_types
    assert AgentEventType.REPAIR_EXECUTED in event_types
    assert len(result.mission_results) == 2
    assert result.mission_results[0].success is False
    assert result.mission_results[1].success is True
    assert backend.calls == 2


def test_budget_blocks_browser_action_when_max_actions_exhausted(tmp_path):
    env = envelope(
        mission_type=MissionType.RESEARCH_SUMMARY,
        allowed_actions=[*SAFE_GTM_ACTIONS, "browser_operator_route", "browser_form_submit", "create_markdown_file"],
        allowed_tools=["browser_public_form_submit", "safe_file_writer"],
        max_actions=2,
    )
    plan = browser_route_plan(env, include_third_step=True)

    result = MissionRunner(project_root=tmp_path, browser_operator_route=operator_route(tmp_path)).run_mission(
        env,
        evidence_refs=["ev_runtime_route"],
        plan=plan,
    )

    assert result.success is False
    assert result.state.action_count <= 2
    assert result.escalations or result.blocked_actions
    assert not any(
        event.action_id == plan.steps[2].action.id and event.event_type.value == "action_executed"
        for event in result.trace_events
    )


def test_budget_blocks_repair_when_projected_overflow(tmp_path):
    env = envelope(
        mission_type=MissionType.RESEARCH_SUMMARY,
        allowed_actions=[*SAFE_GTM_ACTIONS, "browser_operator_route", "browser_form_submit", "create_markdown_file"],
        allowed_tools=["browser_public_form_submit", "safe_file_writer"],
        max_actions=3,
    )
    plan = browser_route_plan(env, summary_content="# Research Summary\n\nThis intentionally lacks evidence markers.\n")
    backend = SequenceFormSubmitBackend(snapshot(), [True, True])
    result = runtime_with_plan(tmp_path, env, plan, operator_route(tmp_path, backend)).run(
        env,
        {"idea": "P4H-AE budget repair overflow", "tool_calls": [browser_tool_call()]},
        evidence_refs=["ev_runtime_route"],
    )

    assert result.success is False
    assert result.repair_decision is not None
    assert result.repair_decision.decision == RepairDecisionType.REPAIR_BLOCKED
    assert "repair_blocked_by_global_action_budget" in result.repair_decision.reasons
    assert result.mission_result is not None
    assert result.mission_result.state.action_count == 2
    assert len([item for item in result.controlled_capability_results if item.get("accepted") is True]) == 1


def test_finalgate_validates_browser_receipts_and_artifacts_in_result(tmp_path):
    env = envelope()
    result = AgentRuntime(project_root=tmp_path, browser_operator_route=operator_route(tmp_path)).run(
        env,
        {"idea": "P4H-AE receipt chain", "tool_calls": [browser_tool_call()]},
        evidence_refs=["ev_runtime_route"],
    )

    controlled = result.controlled_capability_results[0]
    route = controlled["operator_route"]
    assert controlled["receipt_id"]
    assert controlled["artifact_ids"]
    assert route["perception_frame_id"]
    assert route["compiled_policy_id"]
    assert route["action_envelope_id"]

    gate = CoreFinalGate().evaluate(result, allowed_project_root=tmp_path)
    assert gate.accepted is True
    assert gate.errors == []


def test_revoked_envelope_blocks_browser_route_immediately(tmp_path):
    env = envelope(revoked_at=utc_now())
    result = AgentRuntime(project_root=tmp_path, browser_operator_route=operator_route(tmp_path)).run(
        env,
        {"idea": "P4H-AE revoked route", "tool_calls": [browser_tool_call()]},
        evidence_refs=["ev_runtime_route"],
    )

    assert result.success is False
    assert result.final_phase == AgentPhase.REVOKED
    assert AgentEventType.BROWSER_OPERATOR_ROUTE_STARTED not in [event.event_type for event in result.trace]
