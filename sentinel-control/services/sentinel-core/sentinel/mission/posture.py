from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from sentinel.mission.models import MissionAuthorityEnvelope
from sentinel.shared.enums import MissionMode
from sentinel.shared.models import SentinelModel


class MissionExecutionPostureLevel(StrEnum):
    CAUTIOUS = "cautious"
    BALANCED = "balanced"
    ASSERTIVE = "assertive"
    POWER = "power"


class MissionExecutionPosture(SentinelModel):
    mission_id: str
    mode: MissionMode
    level: MissionExecutionPostureLevel
    auto_execute_threshold: float = Field(ge=0.0, le=100.0)
    log_and_continue_threshold: float = Field(ge=0.0, le=100.0)
    escalate_threshold: float = Field(ge=0.0, le=100.0)
    block_threshold: float = Field(ge=0.0, le=100.0)
    uncertainty_escalates: bool = False
    require_receipt_for_auto_execute: bool = True
    reason: str


class MissionExecutionPosturePolicy:
    def select(self, envelope: MissionAuthorityEnvelope) -> MissionExecutionPosture:
        if envelope.mode == MissionMode.SAFE:
            return MissionExecutionPosture(
                mission_id=envelope.id,
                mode=envelope.mode,
                level=MissionExecutionPostureLevel.CAUTIOUS,
                auto_execute_threshold=9.0,
                log_and_continue_threshold=30.0,
                escalate_threshold=60.0,
                block_threshold=81.0,
                uncertainty_escalates=True,
                reason="SAFE mode keeps uncertain actions behind escalation.",
            )
        if envelope.mode == MissionMode.OPERATOR:
            return MissionExecutionPosture(
                mission_id=envelope.id,
                mode=envelope.mode,
                level=MissionExecutionPostureLevel.BALANCED,
                auto_execute_threshold=30.0,
                log_and_continue_threshold=60.0,
                escalate_threshold=75.0,
                block_threshold=81.0,
                reason="OPERATOR mode auto-executes ordinary local reversible actions.",
            )
        if envelope.mode == MissionMode.AUTONOMOUS:
            return MissionExecutionPosture(
                mission_id=envelope.id,
                mode=envelope.mode,
                level=MissionExecutionPostureLevel.ASSERTIVE,
                auto_execute_threshold=40.0,
                log_and_continue_threshold=65.0,
                escalate_threshold=75.0,
                block_threshold=81.0,
                reason="AUTONOMOUS mode stays bounded while continuing local recoverable work.",
            )
        return MissionExecutionPosture(
            mission_id=envelope.id,
            mode=envelope.mode,
            level=MissionExecutionPostureLevel.POWER,
            auto_execute_threshold=50.0,
            log_and_continue_threshold=70.0,
            escalate_threshold=78.0,
            block_threshold=81.0,
            reason="POWER mode pushes hard on authorized local reversible work only.",
        )
