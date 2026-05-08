from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from sentinel.agent import AgentEventType, AgentRuntime, CoreFinalGate, EventBus
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
from sentinel.shared.enums import ConfidenceLevel, ExternalityLevel, MissionMode, MissionStatus, MissionType, ReversibilityLevel, SensitivityLevel


SAFE_GTM_ACTIONS = [
    "create_project_folder",
    "generate_gtm_pack",
    "generate_landing_copy",
    "generate_outreach_drafts_without_sending",
    "create_watchlist",
    "generate_research_questions",
]
PNG_BYTES = b"\x89PNG\r\n\x1a\nfake"


@dataclass(frozen=True)
class MiniCorpusCase:
    case_id: str
    html: str
    text: str
    submit_name: str
    final_title: str
    final_text: str
    expected_effect: str
    notes: str
    planned_step_count: int = 2
    final_url_after: str = "https://example.com/form/thanks"

    @property
    def context_pack_id(self) -> str:
        return f"cpk_p4h_af_{self.case_id}"


MINI_CORPUS = [
    MiniCorpusCase(
        case_id="messy_duplicate_context_submit",
        html="""
        <html><body>
          <main>
            <section aria-label="Archive">
              <h2>Old request</h2>
              <input placeholder="Archived email" />
              <button>Send request</button>
            </section>
            <section aria-label="Current">
              <h2>Current request</h2>
              <input placeholder="Work email" />
              <button>Send enterprise request</button>
            </section>
          </main>
        </body></html>
        """,
        text="Old request Archived email Send request Current request Work email Send enterprise request",
        submit_name="Send enterprise request",
        final_title="Enterprise Request Submitted",
        final_text="Enterprise confirmation text appears.",
        expected_effect="enterprise confirmation text appears",
        notes="messy duplicate controls still bind by runtime ref",
    ),
    MiniCorpusCase(
        case_id="weak_dom_ax_visual_bound_action",
        html="""
        <html><body>
          <main>
            <h1>Low semantics form</h1>
            <input placeholder="Email" />
            <button aria-label="Continue validation"></button>
          </main>
        </body></html>
        """,
        text="Low semantics form Email Continue validation",
        submit_name="Continue validation",
        final_title="Validation Continued",
        final_text="Validation confirmation text appears.",
        expected_effect="validation confirmation text appears",
        notes="weak visible label still produces an authorized runtime ref",
    ),
    MiniCorpusCase(
        case_id="dynamic_state_after_action_verify",
        html="""
        <html><body>
          <main>
            <h1>Dynamic state</h1>
            <input placeholder="Email" />
            <button>Start dynamic check</button>
          </main>
        </body></html>
        """,
        text="Dynamic state Email Start dynamic check",
        submit_name="Start dynamic check",
        final_title="Dynamic State Changed",
        final_text="State changed after submit and confirmation text appears.",
        expected_effect="dynamic confirmation text appears",
        notes="post-action state differs from pre-action state",
    ),
    MiniCorpusCase(
        case_id="redirect_revalidate_submit",
        html="""
        <html><body>
          <main>
            <h1>Redirect flow</h1>
            <input placeholder="Email" />
            <button>Submit and revalidate</button>
          </main>
        </body></html>
        """,
        text="Redirect flow Email Submit and revalidate",
        submit_name="Submit and revalidate",
        final_title="Redirect Revalidated",
        final_text="Same-origin redirect revalidated before confirmation.",
        expected_effect="same-origin redirect remains authorized",
        notes="same-origin final URL change is receipt-bound",
        final_url_after="https://example.com/form/revalidated",
    ),
    MiniCorpusCase(
        case_id="deep_scroll_budget_pressure",
        html="""
        <html><body>
          <main>
            <h1>Long document</h1>
            <section><h2>Intro</h2><p>Lots of content.</p></section>
            <section><h2>Middle</h2><p>More content.</p></section>
            <section><h2>More</h2><p>Even more content.</p></section>
            <section><h2>Target area</h2><input placeholder="Email" /><button>Send deep request</button></section>
          </main>
        </body></html>
        """,
        text="Long document Intro Lots of content Middle More content More Even more content Target area Email Send deep request",
        submit_name="Send deep request",
        final_title="Deep Request Submitted",
        final_text="Deep scroll target confirmation text appears.",
        expected_effect="deep scroll confirmation text appears",
        notes="deeper target still stays inside action budget",
        planned_step_count=5,
    ),
]


class MiniCorpusFormSubmitBackend:
    def __init__(self, cases: list[MiniCorpusCase]) -> None:
        self.cases_by_context = {case.context_pack_id: case for case in cases}
        self.snapshots_by_context = {case.context_pack_id: snapshot_for_case(case) for case in cases}
        self.calls: list[str] = []

    def __call__(self, request: BrowserFormSubmitRequest) -> BrowserFormSubmitBackendResult:
        case = self.cases_by_context[request.context_pack_id]
        self.calls.append(case.case_id)
        return BrowserFormSubmitBackendResult(
            before_snapshot=self.snapshots_by_context[request.context_pack_id],
            after_page=BrowserRenderedPage(
                final_url=case.final_url_after,
                status_code=200,
                title=case.final_title,
                text=case.final_text,
                links=[],
                html=f"<html><body><main><h1>{case.final_title}</h1><p>{case.final_text}</p></main></body></html>",
                screenshot_png=PNG_BYTES,
            ),
            final_url_before=request.final_url,
            final_url_after=case.final_url_after,
            submitted=True,
            submitted_ref_ids=[request.form_ref_id, request.submit_ref_id],
        )


def grant(max_uses: int = 20) -> BrowserV3AuthorityGrant:
    return BrowserV3AuthorityGrant(
        id="grant_browser_form_submit",
        authority_class=BrowserV3AuthorityClass.FORM_SUBMIT,
        allowed_domains=["example.com"],
        max_uses=max_uses,
    )


def envelope(mission_id: str, **overrides) -> MissionAuthorityEnvelope:
    data = {
        "id": mission_id,
        "user_id": "user_p4h_af",
        "mission_type": MissionType.RESEARCH_SUMMARY,
        "mission_title": "P4H-AF Runtime Integrated Browser Review",
        "mission_objective": "Run a mini-corpus of governed browser operator routes through runtime.",
        "success_criteria": ["Mini-corpus browser routes execute with receipts and FinalGate proof."],
        "mode": MissionMode.POWER,
        "allowed_systems": ["local_workspace", "public_web"],
        "allowed_tools": ["safe_file_writer", "browser_public_form_submit"],
        "allowed_actions": [*SAFE_GTM_ACTIONS, "browser_operator_route", "browser_form_submit", "create_markdown_file"],
        "forbidden_actions": ["payment", "credential_access"],
        "allowed_paths": ["data/generated_projects"],
        "allowed_domains": ["example.com"],
        "browser_v3_authority_grants": [grant().model_dump(mode="json")],
        "risk_appetite_score": 90,
        "max_actions": 40,
        "max_duration_minutes": 10,
        "max_cost_usd": 1.0,
    }
    data.update(overrides)
    return MissionAuthorityEnvelope(**data)


def snapshot_for_case(case: MiniCorpusCase):
    return BrowserAccessibilitySnapshotBuilder().build(html=case.html, text=case.text)


def snapshot_event(bus: EventBus, snap) -> str:
    event = bus.append(
        AgentEventType.BROWSER_SNAPSHOT_CAPTURED,
        "Rendered browser snapshot captured for P4H-AF mini-corpus setup.",
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


def ref_by_role(snap, role: str) -> str:
    for ref_id, ref in snap.refs.items():
        if ref.role == role:
            return ref_id
    raise AssertionError(f"missing ref for role {role}")


def ref_by_role_name(snap, role: str, name: str) -> str:
    for ref_id, ref in snap.refs.items():
        if ref.role == role and ref.name == name:
            return ref_id
    raise AssertionError(f"missing ref for role={role} name={name}. refs={snap.refs!r}")


def tool_call_for_case(mission_id: str, case: MiniCorpusCase, *, target_ref_override: str | None = None, actions_already_used: int = 0) -> dict:
    snap = snapshot_for_case(case)
    bus = EventBus(mission_id)
    snap_trace = snapshot_event(bus, snap)
    textbox = ref_by_role(snap, "textbox")
    button = ref_by_role_name(snap, "button", case.submit_name)
    target_ref = target_ref_override or button
    result = BrowserInteractionDryRunPlanner().create_plan(
        mission_id=mission_id,
        snapshot=snap,
        steps=[
            BrowserInteractionStep(
                intent=BrowserInteractionIntent.FILL_PLAN,
                target=BrowserInteractionTarget(ref=textbox),
                text="operator@example.com",
                reason=f"Fill public fixture field for {case.case_id}.",
            ),
            BrowserInteractionStep(
                intent=BrowserInteractionIntent.CLICK_PLAN,
                target=BrowserInteractionTarget(ref=button),
                reason=f"Submit fixture form for {case.case_id}.",
            ),
        ],
        event_bus=bus,
        final_url="https://example.com/form",
        snapshot_trace_id=snap_trace,
    )
    assert result.accepted is True
    assert result.plan is not None
    assert result.trace_event_id is not None
    arguments = {
        "ui_observation_set": BrowserUIObservationBuilder().from_accessibility_snapshot(
            mission_id=mission_id,
            url="https://example.com/form",
            snapshot=snap,
        ).model_dump(mode="json"),
        "target_ref_id": target_ref,
        "ref_id": target_ref,
        "plan": result.plan.model_dump(mode="json"),
        "authority_grant_id": "grant_browser_form_submit",
        "context_pack_id": case.context_pack_id,
        "operator_intent": f"P4H-AF mini-corpus case: {case.notes}.",
        "plan_trace_event_id": result.trace_event_id,
        "before_snapshot_trace_event_id": snap_trace,
        "final_url": "https://example.com/form",
        "form_ref_id": textbox,
        "submit_ref_id": button,
        "expected_effect": case.expected_effect,
        "allowed_domains": ["example.com"],
        "capture_screenshot": True,
        "planned_step_count": case.planned_step_count,
        "actions_already_used": actions_already_used,
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


def canonical_tool_call_payload(call: dict) -> dict:
    return {
        **call,
        "canonical_hash": hashlib.sha256(
            json.dumps(call, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
    }


def route_action(env: MissionAuthorityEnvelope, case: MiniCorpusCase, *, project_path: str = "data/generated_projects/p4h-af-runtime-minicorpus") -> MissionAction:
    raw = canonical_tool_call_payload(tool_call_for_case(env.id, case))
    return MissionAction(
        id=f"mact_{case.case_id}",
        mission_id=env.id,
        action_type="browser_operator_route",
        tool="browser_public_form_submit",
        intent=f"Execute P4H-AF mini-corpus browser route `{case.case_id}`.",
        target=project_path,
        input={"tool_call": raw},
        expected_output=f"{case.case_id} browser route executed.",
        reversibility=ReversibilityLevel.STATE_MUTATING_RECOVERABLE,
        externality=ExternalityLevel.INTERNAL_LOCAL,
        sensitivity=SensitivityLevel.INTERNAL,
        confidence=ConfidenceLevel.HIGH,
        evidence_refs=["ev_p4h_af_runtime"],
    )


def summary_action(env: MissionAuthorityEnvelope, *, project_path: str = "data/generated_projects/p4h-af-runtime-minicorpus") -> MissionAction:
    return MissionAction(
        mission_id=env.id,
        action_type="create_markdown_file",
        tool="safe_file_writer",
        intent="Write bounded P4H-AF mini-corpus summary after browser routes.",
        target=project_path,
        input={
            "filename": "RESEARCH_SUMMARY.md",
            "artifact_type": "research_summary",
            "content": "# P4H-AF Runtime Mini-Corpus\n\nEvidence refs\n\n- ev_p4h_af_runtime\n",
        },
        expected_output="P4H-AF mini-corpus summary exists.",
        reversibility=ReversibilityLevel.LOCAL_WRITE_REVERSIBLE,
        externality=ExternalityLevel.INTERNAL_LOCAL,
        sensitivity=SensitivityLevel.INTERNAL,
        confidence=ConfidenceLevel.HIGH,
        evidence_refs=["ev_p4h_af_runtime"],
    )


def mini_corpus_plan(env: MissionAuthorityEnvelope, cases: list[MiniCorpusCase]) -> MissionPlan:
    steps: list[MissionPlanStep] = []
    previous_id = ""
    for case in cases:
        step_id = f"route_{case.case_id}"
        steps.append(
            MissionPlanStep(
                id=step_id,
                depends_on=[previous_id] if previous_id else [],
                action=route_action(env, case),
            )
        )
        previous_id = step_id
    steps.append(
        MissionPlanStep(
            id="write_summary",
            depends_on=[previous_id],
            action=summary_action(env),
            expected_artifact="RESEARCH_SUMMARY.md",
        )
    )
    return MissionPlan(mission_id=env.id, steps=steps)


def operator_route(tmp_path: Path, cases: list[MiniCorpusCase]) -> BrowserOperatorRuntimeRoute:
    return BrowserOperatorRuntimeRoute(
        registry=default_tool_registry(),
        capture_root=tmp_path / "captures",
        form_submit_backend=MiniCorpusFormSubmitBackend(cases),
    )


def runtime_with_plan(tmp_path: Path, plan: MissionPlan, route: BrowserOperatorRuntimeRoute) -> AgentRuntime:
    runtime = AgentRuntime(project_root=tmp_path, browser_operator_route=route)

    def create_plan(*args, **kwargs):
        return runtime.planner_bridge._attach_verified_hypotheses(plan, kwargs.get("verified_hypotheses") or [])

    runtime.planner_bridge.create_plan = create_plan
    return runtime


def test_mission_runner_executes_runtime_integrated_browser_mini_corpus(tmp_path):
    cases = MINI_CORPUS
    env = envelope("mission_p4h_af_mission_runner")
    plan = mini_corpus_plan(env, cases)
    result = MissionRunner(project_root=tmp_path, browser_operator_route=operator_route(tmp_path, cases)).run_mission(
        env,
        evidence_refs=["ev_p4h_af_runtime"],
        plan=plan,
    )

    executed_routes = [
        event
        for event in result.trace_events
        if event.result.get("type") == "browser_operator_route"
    ]
    receipt_ids = [event.result.get("receipt_id") for event in executed_routes]

    assert result.success is True
    assert result.state.status == MissionStatus.COMPLETED
    assert result.state.action_count == len(cases) + 1
    assert len(executed_routes) == len(cases)
    assert all(event.result["accepted"] is True for event in executed_routes)
    assert all(event.result["operator_trace_certified"] is True for event in executed_routes)
    assert len(set(receipt_ids)) == len(cases)


def test_agent_runtime_worker_executes_browser_mini_corpus_and_finalgate_accepts(tmp_path):
    cases = MINI_CORPUS[:4]
    env = envelope("mission_p4h_af_agent_runtime_worker")
    plan = mini_corpus_plan(env, cases)
    result = runtime_with_plan(tmp_path, plan, operator_route(tmp_path, cases)).run(
        env,
        {"idea": "P4H-AF runtime-integrated browser review"},
        evidence_refs=["ev_p4h_af_runtime"],
    )

    assert result.success is True
    assert result.mission_result is not None
    assert result.mission_result.state.action_count == len(cases) + 1

    gate = CoreFinalGate().evaluate(result, allowed_project_root=tmp_path)
    assert gate.accepted is True
    assert gate.errors == []


def test_agent_runtime_direct_tool_calls_execute_browser_mini_corpus_with_unique_receipts(tmp_path):
    cases = MINI_CORPUS[:3]
    env = envelope(
        "mission_p4h_af_direct_tool_calls",
        mission_type=MissionType.GTM,
        mission_title="P4H-AF Direct Browser Runtime Mini-Corpus",
    )
    result = AgentRuntime(project_root=tmp_path, browser_operator_route=operator_route(tmp_path, cases)).run(
        env,
        {
            "idea": "P4H-AF direct controlled browser mini-corpus",
            "tool_calls": [tool_call_for_case(env.id, case) for case in cases],
        },
        evidence_refs=["ev_p4h_af_runtime"],
    )

    accepted = [item for item in result.controlled_capability_results if item.get("accepted") is True]
    event_types = [event.event_type for event in result.trace]

    assert result.success is True
    assert len(accepted) == len(cases)
    assert event_types.count(AgentEventType.BROWSER_OPERATOR_ROUTE_COMPLETED) == len(cases)
    assert len({item["receipt_id"] for item in accepted}) == len(cases)

    gate = CoreFinalGate().evaluate(result, allowed_project_root=tmp_path)
    assert gate.accepted is True


def test_runtime_mini_corpus_rejects_fabricated_ref_before_browser_execution(tmp_path):
    case = MINI_CORPUS[0]
    env = envelope(
        "mission_p4h_af_fabricated_ref",
        mission_type=MissionType.GTM,
        mission_title="P4H-AF Fabricated Ref Guard",
    )
    result = AgentRuntime(project_root=tmp_path, browser_operator_route=operator_route(tmp_path, [case])).run(
        env,
        {
            "idea": "P4H-AF fabricated browser ref rejection",
            "tool_calls": [tool_call_for_case(env.id, case, target_ref_override="fabricated-ref")],
        },
        evidence_refs=["ev_p4h_af_runtime"],
    )

    rejected = result.controlled_capability_results[0]
    event_types = [event.event_type for event in result.trace]

    assert rejected["accepted"] is False
    assert rejected["operator_route"]["status"] == "rejected"
    assert rejected["reason"] == "browser_operator_target_ref_not_observed"
    assert AgentEventType.BROWSER_FORM_SUBMIT_EXECUTED not in event_types


def test_runtime_mini_corpus_blocks_action_budget_exhaustion_before_browser_execution(tmp_path):
    case = MINI_CORPUS[-1]
    env = envelope(
        "mission_p4h_af_action_budget_guard",
        mission_type=MissionType.GTM,
        mission_title="P4H-AF Action Budget Guard",
        max_actions=40,
    )
    result = AgentRuntime(project_root=tmp_path, browser_operator_route=operator_route(tmp_path, [case])).run(
        env,
        {
            "idea": "P4H-AF browser action budget guard",
            "tool_calls": [tool_call_for_case(env.id, case, actions_already_used=env.max_actions)],
        },
        evidence_refs=["ev_p4h_af_runtime"],
    )

    rejected = result.controlled_capability_results[0]
    event_types = [event.event_type for event in result.trace]

    assert rejected["accepted"] is False
    assert rejected["operator_route"]["status"] == "rejected"
    assert rejected["reason"].startswith("browser_operator_prepare_failed")
    assert "action_budget_exceeded" in rejected["errors"]
    assert AgentEventType.BROWSER_FORM_SUBMIT_EXECUTED not in event_types
