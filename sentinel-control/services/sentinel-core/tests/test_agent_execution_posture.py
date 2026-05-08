from __future__ import annotations

from pathlib import Path

from sentinel.agent import AgentEventType, AgentRuntime, ExecutionPostureLevel, ExecutionPosturePolicy
from sentinel.mission import MissionAuthorityEnvelope
from sentinel.shared.enums import MissionMode, MissionType


SAFE_ACTIONS = [
    "create_project_folder",
    "create_markdown_file",
    "export_json",
    "generate_gtm_pack",
    "generate_landing_copy",
    "generate_outreach_drafts_without_sending",
    "create_watchlist",
    "generate_research_questions",
    "write_trace",
]


def envelope(**overrides) -> MissionAuthorityEnvelope:
    data = {
        "user_id": "user_001",
        "mission_type": MissionType.GTM,
        "mission_title": "P2E execution posture",
        "mission_objective": "Tune execution aggressiveness without expanding authority.",
        "success_criteria": ["Execution posture is traced"],
        "mode": MissionMode.POWER,
        "allowed_systems": ["local_workspace"],
        "allowed_tools": ["safe_file_writer"],
        "allowed_actions": SAFE_ACTIONS,
        "forbidden_actions": ["send_email", "run_shell_command", "browser_submit_form", "credential_access"],
        "allowed_paths": ["data/generated_projects"],
        "max_actions": 20,
        "max_cost_usd": 1.0,
    }
    data.update(overrides)
    return MissionAuthorityEnvelope(**data)


def test_execution_posture_policy_keeps_safe_mode_conservative():
    env = envelope(mode=MissionMode.SAFE, max_actions=10, risk_appetite_score=10)

    posture = ExecutionPosturePolicy().select(env, reserved_plan_actions=6)

    assert posture.level == ExecutionPostureLevel.CAUTIOUS
    assert posture.max_repair_cycles == 0
    assert posture.direct_tool_call_budget == 0
    assert "authority_unchanged=true" in posture.reason


def test_execution_posture_policy_makes_power_mode_aggressive_inside_remaining_budget():
    env = envelope(mode=MissionMode.POWER, max_actions=12, risk_appetite_score=80)

    posture = ExecutionPosturePolicy().select(env, reserved_plan_actions=7)

    assert posture.level == ExecutionPostureLevel.POWER
    assert posture.max_repair_cycles == 3
    assert posture.direct_tool_call_budget == 5
    assert posture.local_reversible_bias == 1.0


def test_safe_mode_rejects_direct_tool_call_but_still_solves_with_mission_worker(tmp_path: Path):
    env = envelope(
        mode=MissionMode.SAFE,
        allowed_tools=["safe_file_writer", "safe_local_markdown_tool"],
        risk_appetite_score=10,
    )

    result = AgentRuntime(project_root=tmp_path).run(
        env,
        {
            "idea": "Safe posture",
            "tool_calls": [
                {
                    "tool_id": "safe_local_markdown_tool",
                    "action": "create_markdown_file",
                    "capability": "local_markdown_write",
                    "arguments": {"path": "runtime/safe.md", "content": "safe should not direct-write"},
                }
            ],
        },
        evidence_refs=["ev_wtp"],
    )
    project_path = Path(result.project_path or "")

    assert result.success is True
    assert result.execution_posture is not None
    assert result.execution_posture.level == ExecutionPostureLevel.CAUTIOUS
    assert result.controlled_capability_results[0]["accepted"] is False
    assert result.controlled_capability_results[0]["reason"] == "direct_tool_call_budget_exhausted"
    assert not (project_path / "runtime" / "safe.md").exists()
    assert AgentEventType.EXECUTION_POSTURE_SELECTED in [event.event_type for event in result.trace]


def test_power_mode_executes_direct_local_call_when_authority_grants_it(tmp_path: Path):
    env = envelope(
        mode=MissionMode.POWER,
        allowed_tools=["safe_file_writer", "safe_local_markdown_tool"],
        risk_appetite_score=80,
    )

    result = AgentRuntime(project_root=tmp_path).run(
        env,
        {
            "idea": "Power posture",
            "tool_calls": [
                {
                    "tool_id": "safe_local_markdown_tool",
                    "action": "create_markdown_file",
                    "capability": "local_markdown_write",
                    "arguments": {"path": "runtime/power.md", "content": "power direct write"},
                }
            ],
        },
        evidence_refs=["ev_wtp"],
    )
    project_path = Path(result.project_path or "")

    assert result.success is True
    assert result.execution_posture is not None
    assert result.execution_posture.level == ExecutionPostureLevel.POWER
    assert result.controlled_capability_results[0]["accepted"] is True
    assert (project_path / "runtime" / "power.md").exists()
