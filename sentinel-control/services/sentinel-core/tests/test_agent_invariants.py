from __future__ import annotations

import pytest

from sentinel.agent import AgentState, CapabilityNeed, InvariantChecker, InvariantViolation, LearningProposal
from sentinel.agent.phases import AgentPhase
from sentinel.mission import MissionAction, MissionAuthorityEnvelope
from sentinel.shared.enums import ConfidenceLevel, ExternalityLevel, MissionMode, MissionType, ReversibilityLevel, SensitivityLevel


SAFE_ACTIONS = ["create_project_folder", "generate_gtm_pack"]


def envelope(**overrides) -> MissionAuthorityEnvelope:
    data = {
        "user_id": "user_001",
        "mission_type": MissionType.GTM,
        "mission_title": "Agent core test",
        "mission_objective": "Test agent core.",
        "mode": MissionMode.SAFE,
        "allowed_tools": ["safe_file_writer"],
        "allowed_actions": SAFE_ACTIONS,
        "forbidden_actions": ["run_shell_command"],
    }
    data.update(overrides)
    return MissionAuthorityEnvelope(**data)


def action(env: MissionAuthorityEnvelope, action_type: str = "create_project_folder", tool: str = "safe_file_writer") -> MissionAction:
    return MissionAction(
        mission_id=env.id,
        action_type=action_type,
        tool=tool,
        intent="test",
        expected_output="done",
        reversibility=ReversibilityLevel.LOCAL_WRITE_REVERSIBLE,
        externality=ExternalityLevel.INTERNAL_LOCAL,
        sensitivity=SensitivityLevel.INTERNAL,
        confidence=ConfidenceLevel.HIGH,
    )


def test_authority_invariant_allows_in_scope_action():
    env = envelope()

    InvariantChecker().check_authority(env, action(env))


def test_authority_invariant_rejects_out_of_scope_action():
    env = envelope()

    with pytest.raises(InvariantViolation):
        InvariantChecker().check_authority(env, action(env, "run_shell_command", "shell"))


def test_memory_context_cannot_expand_authority():
    env = envelope()

    with pytest.raises(InvariantViolation):
        InvariantChecker().check_memory_not_authority(env, ["create_project_folder", "send_email"])


def test_context_capabilities_must_derive_from_allowed_actions():
    env = envelope()

    InvariantChecker().check_capabilities_derive_from_authority(
        env,
        ["local_workspace_write", "gtm_pack_generation"],
    )

    with pytest.raises(InvariantViolation):
        InvariantChecker().check_capabilities_derive_from_authority(
            env,
            ["local_workspace_write", "browser_research"],
        )


def test_missing_capability_must_explain_absence():
    need = CapabilityNeed(name="browser_research", reason="future", available=False)

    with pytest.raises(InvariantViolation):
        InvariantChecker().check_capability_declarations([need])


def test_learning_proposal_must_require_human_approval():
    proposal = LearningProposal(
        observed_failure="test",
        proposed_change="unsafe auto change",
        requires_human_approval=False,
    )

    with pytest.raises(InvariantViolation):
        InvariantChecker().check_learning_proposals([proposal])


def test_bounded_repair_invariant_blocks_overrun():
    state = AgentState(mission_id="mission_001", repair_cycles=2, max_repair_cycles=1)

    with pytest.raises(InvariantViolation):
        InvariantChecker().check_bounded_repair(state)


def test_completion_invariant_requires_successful_mission_result():
    state = AgentState(mission_id="mission_001", phase=AgentPhase.COMPLETED)

    with pytest.raises(InvariantViolation):
        InvariantChecker().check_completion(state, None)
