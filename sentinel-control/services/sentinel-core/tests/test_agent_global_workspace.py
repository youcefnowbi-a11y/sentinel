from __future__ import annotations

import pytest

from sentinel.agent import (
    AgentEventType,
    BroadcastSlice,
    EventBus,
    MissionGlobalWorkspace,
    WorkspaceAgentOutput,
    WorkspaceDelta,
    WorkspaceFact,
    WorkspaceOpenQuestion,
    WorkspaceRejectedClaim,
    WorkspaceSignal,
)
from sentinel.mission import MissionAuthorityEnvelope
from sentinel.shared.enums import MissionMode, MissionType


SAFE_ACTIONS = ["create_markdown_file", "export_json", "write_trace"]


def envelope(**overrides) -> MissionAuthorityEnvelope:
    data = {
        "user_id": "user_p5e",
        "mission_type": MissionType.RESEARCH_SUMMARY,
        "mission_title": "P5E workspace fixture",
        "mission_objective": "Maintain shared mission cognition without changing authority.",
        "success_criteria": ["Workspace exists", "Broadcast stays bounded"],
        "mode": MissionMode.POWER,
        "allowed_systems": ["local_workspace"],
        "allowed_tools": ["safe_file_writer"],
        "allowed_actions": SAFE_ACTIONS,
        "forbidden_actions": ["send_email", "run_shell_command", "credential_access", "payment", "spend_money"],
        "allowed_paths": ["data/generated_projects"],
        "allowed_domains": [],
        "allowed_accounts": [],
        "max_actions": 40,
        "max_cost_usd": 1.0,
    }
    data.update(overrides)
    return MissionAuthorityEnvelope(**data)


def workspace(env: MissionAuthorityEnvelope | None = None, **kwargs) -> MissionGlobalWorkspace:
    return MissionGlobalWorkspace.create(env or envelope(), **kwargs)


def delta(env: MissionAuthorityEnvelope, base_version: int, **kwargs) -> WorkspaceDelta:
    return WorkspaceDelta(mission_id=env.id, base_version=base_version, **kwargs)


def test_initial_snapshot_is_deterministic_and_emits_trace():
    env = envelope()
    bus = EventBus(env.id)

    one = workspace(env, open_questions=["What proof is missing?"])
    two = workspace(env, open_questions=["What proof is missing?"])
    traced = workspace(env, open_questions=["What proof is missing?"], event_bus=bus)

    assert one.snapshot.id == two.snapshot.id
    assert one.snapshot.model_dump(exclude={"trace_refs"}) == two.snapshot.model_dump(exclude={"trace_refs"})
    assert traced.snapshot.version == 0
    assert traced.snapshot.trace_refs
    assert bus.events()[0].event_type == AgentEventType.WORKSPACE_SNAPSHOT_CREATED


def test_delta_increments_workspace_version_and_emits_trace():
    env = envelope()
    base = workspace(env)
    bus = EventBus(env.id)
    change = delta(
        env,
        0,
        accepted_facts=[WorkspaceFact(text="The mission needs a compact broadcast.", evidence_refs=["ev_workspace"])],
    )

    result = base.apply_delta(change, event_bus=bus)

    assert result.snapshot.version == 1
    assert result.deltas == [change]
    assert result.snapshot.trace_refs
    assert bus.events()[0].event_type == AgentEventType.WORKSPACE_DELTA_APPLIED


def test_accepted_fact_requires_evidence_ref():
    with pytest.raises(ValueError, match="requires at least one evidence ref"):
        WorkspaceFact(text="Unsupported accepted fact.", evidence_refs=[])


def test_rejected_claim_cannot_be_reintroduced_as_accepted_fact():
    env = envelope()
    base = workspace(env)
    rejected = base.apply_delta(
        delta(
            env,
            0,
            rejected_claims=[WorkspaceRejectedClaim(text="This unsupported claim is true.", reason="No evidence.")],
        )
    )

    with pytest.raises(ValueError, match="Rejected claim cannot be reintroduced"):
        rejected.apply_delta(
            delta(
                env,
                1,
                accepted_facts=[WorkspaceFact(text="This unsupported claim is true.", evidence_refs=["ev_late"])],
            )
        )


def test_broadcast_slice_minimizes_context_by_role_and_purpose():
    env = envelope()
    base = workspace(env, open_questions=["Which source should research inspect?", "Which claim should verifier test?"])
    many_facts = [
        WorkspaceFact(text=f"Research branch {index} has evidence.", evidence_refs=[f"ev_{index}"], tags=["research"])
        for index in range(6)
    ]
    updated = base.apply_delta(
        delta(
            env,
            0,
            accepted_facts=many_facts,
            open_questions=[
                WorkspaceOpenQuestion(question="Research-only question.", role_relevance=["research_agent"]),
                WorkspaceOpenQuestion(question="Verifier-only question.", role_relevance=["verifier_agent"]),
            ],
            rejected_claims=[WorkspaceRejectedClaim(text="Bad claim.", reason="Contradicted.")],
        )
    )

    broadcast = updated.prepare_broadcast("research_agent", purpose=["exploration"], max_items=3)

    assert isinstance(broadcast, BroadcastSlice)
    assert broadcast.minimized_context is True
    assert len(broadcast.accepted_facts) < len(updated.snapshot.accepted_facts)
    assert all("verifier" not in question.role_relevance for question in broadcast.open_questions)
    assert broadcast.rejected_claims == []


def test_broadcast_preserves_authority_summary_without_expansion():
    env = envelope(allowed_tools=["safe_file_writer"], allowed_actions=["create_markdown_file"], max_cost_usd=2.0)
    before = env.model_dump(mode="json")
    base = workspace(env)
    bus = EventBus(env.id)

    broadcast = base.prepare_broadcast("aggregator_agent", purpose=["aggregation"], event_bus=bus)

    assert env.model_dump(mode="json") == before
    assert broadcast.authority_expansion is False
    assert broadcast.authority_summary["allowed_tools"] == ["safe_file_writer"]
    assert broadcast.authority_summary["allowed_actions"] == ["create_markdown_file"]
    assert "payment_send" not in broadcast.authority_summary["allowed_actions"]
    assert bus.events()[0].event_type == AgentEventType.WORKSPACE_BROADCAST_PREPARED


def test_signal_entries_are_stored_as_observations_only():
    env = envelope()
    base = workspace(env)
    signal = WorkspaceSignal(
        signal_type="roi",
        summary="Prospect reply rate improved.",
        value={"reply_rate": 0.18},
        evidence_refs=["ev_signal"],
    )

    result = base.apply_delta(delta(env, 0, signals=[signal]))

    stored = result.snapshot.signals[0]
    assert stored.observation_only is True
    assert stored.spend_runtime is False
    assert stored.authority_expansion is False


def test_agent_output_can_be_stored_without_execution():
    env = envelope()
    base = workspace(env)
    output = WorkspaceAgentOutput(
        role="verifier_agent",
        summary="Verifier found one supported claim.",
        claims=["Supported claim"],
        evidence_refs=["ev_supported"],
    )

    result = base.apply_delta(delta(env, 0, agent_outputs=[output]))

    stored = result.snapshot.agent_outputs[0]
    assert stored.execution_seen is False
    assert stored.agent_spawning is False
    assert stored.runtime_multi_agent_execution is False
    assert stored.authority_expansion is False


def test_stale_delta_is_rejected():
    env = envelope()
    base = workspace(env)
    current = base.apply_delta(delta(env, 0, accepted_facts=[WorkspaceFact(text="Fresh fact.", evidence_refs=["ev_fresh"])]))

    with pytest.raises(ValueError, match="base_version is stale"):
        current.apply_delta(delta(env, 0, accepted_facts=[WorkspaceFact(text="Stale fact.", evidence_refs=["ev_stale"])]))


def test_workspace_replay_from_deltas_is_deterministic():
    env = envelope()
    base = workspace(env)
    d1 = delta(env, 0, accepted_facts=[WorkspaceFact(text="Fact one.", evidence_refs=["ev_one"])])
    d2 = delta(env, 1, signals=[WorkspaceSignal(signal_type="risk", summary="Risk lowered.", value={"risk": "low"})])

    direct = base.apply_delta(d1).apply_delta(d2)
    replayed = MissionGlobalWorkspace.replay(base.snapshot, [d1, d2])

    assert replayed.snapshot.id == direct.snapshot.id
    assert replayed.snapshot.model_dump(exclude={"trace_refs"}) == direct.snapshot.model_dump(exclude={"trace_refs"})


def test_workspace_never_expands_authority():
    env = envelope(
        allowed_tools=["safe_file_writer"],
        allowed_actions=["create_markdown_file"],
        allowed_paths=["data/generated_projects"],
    )
    before = env.model_dump(mode="json")
    result = workspace(env).apply_delta(
        delta(
            env,
            0,
            signals=[WorkspaceSignal(signal_type="budget", summary="Budget remains available.", value={"remaining": 1.0})],
            agent_outputs=[WorkspaceAgentOutput(role="planner_agent", summary="Plan only.", evidence_refs=["ev_plan"])],
        )
    )

    assert env.model_dump(mode="json") == before
    assert result.authority_expansion is False
    assert result.payment_runtime is False
    assert result.trading_runtime is False
    assert result.account_creation_runtime is False
    assert result.snapshot.authority_summary["allowed_tools"] == ["safe_file_writer"]
    assert result.snapshot.authority_summary["allowed_actions"] == ["create_markdown_file"]
