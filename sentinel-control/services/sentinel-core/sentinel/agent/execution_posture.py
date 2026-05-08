from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from sentinel.agent.events import AgentEventType
from sentinel.agent.phases import AgentPhase
from sentinel.mission.models import MissionAuthorityEnvelope
from sentinel.shared.enums import MissionMode
from sentinel.shared.models import SentinelModel, new_id

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sentinel.agent.event_bus import EventBus


class ExecutionPostureLevel(StrEnum):
    CAUTIOUS = "cautious"
    BALANCED = "balanced"
    ASSERTIVE = "assertive"
    POWER = "power"


class ExecutionPosture(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("posture"))
    mission_id: str
    level: ExecutionPostureLevel
    mode: MissionMode
    max_repair_cycles: int = Field(ge=0)
    direct_tool_call_budget: int = Field(ge=0)
    local_reversible_bias: float = Field(ge=0.0, le=1.0)
    escalation_bias: float = Field(ge=0.0, le=1.0)
    reason: str
    trace_refs: list[str] = Field(default_factory=list)


class ExecutionPosturePolicy:
    """Selects how hard the agent may push inside already-granted authority.

    This policy never grants tools, actions, paths, credentials, or network
    access. It only decides how much effort to spend on reversible local work.
    """

    def select(
        self,
        envelope: MissionAuthorityEnvelope,
        *,
        reserved_plan_actions: int = 0,
        phase: AgentPhase = AgentPhase.INITIALIZED,
        event_bus: EventBus | None = None,
    ) -> ExecutionPosture:
        remaining_actions = max(0, envelope.max_actions - max(0, reserved_plan_actions))
        risk_appetite = envelope.risk_appetite_score
        mode = envelope.mode

        if mode == MissionMode.SAFE:
            level = ExecutionPostureLevel.CAUTIOUS
            max_repair_cycles = 0
            direct_tool_call_budget = 0
            local_reversible_bias = 0.15
            escalation_bias = 0.85
        elif mode == MissionMode.OPERATOR:
            level = ExecutionPostureLevel.BALANCED
            max_repair_cycles = 1
            direct_tool_call_budget = min(1, remaining_actions)
            local_reversible_bias = 0.45
            escalation_bias = 0.55
        elif mode == MissionMode.POWER:
            level = ExecutionPostureLevel.POWER if risk_appetite >= 50 else ExecutionPostureLevel.ASSERTIVE
            max_repair_cycles = 2
            direct_tool_call_budget = remaining_actions
            local_reversible_bias = 0.90
            escalation_bias = 0.20
        else:
            level = ExecutionPostureLevel.ASSERTIVE
            max_repair_cycles = 1
            direct_tool_call_budget = min(2, remaining_actions)
            local_reversible_bias = 0.65
            escalation_bias = 0.35

        if risk_appetite < 20:
            direct_tool_call_budget = min(direct_tool_call_budget, 1)
            max_repair_cycles = min(max_repair_cycles, 1)
            escalation_bias = max(escalation_bias, 0.75)
        elif risk_appetite >= 75 and mode == MissionMode.POWER:
            max_repair_cycles = max(max_repair_cycles, 3)
            local_reversible_bias = 1.0

        posture = ExecutionPosture(
            mission_id=envelope.id,
            level=level,
            mode=mode,
            max_repair_cycles=max_repair_cycles,
            direct_tool_call_budget=direct_tool_call_budget,
            local_reversible_bias=local_reversible_bias,
            escalation_bias=escalation_bias,
            reason=(
                f"mode={mode.value}; risk_appetite={risk_appetite}; "
                f"remaining_actions={remaining_actions}; authority_unchanged=true"
            ),
        )
        if event_bus is None:
            return posture

        event = event_bus.append(
            AgentEventType.EXECUTION_POSTURE_SELECTED,
            "Execution posture selected without expanding mission authority.",
            phase_before=phase,
            phase_after=phase,
            payload={
                "posture_id": posture.id,
                "level": posture.level,
                "mode": posture.mode,
                "max_repair_cycles": posture.max_repair_cycles,
                "direct_tool_call_budget": posture.direct_tool_call_budget,
                "local_reversible_bias": posture.local_reversible_bias,
                "escalation_bias": posture.escalation_bias,
                "reason": posture.reason,
            },
        )
        return posture.model_copy(update={"trace_refs": [event.id]})
