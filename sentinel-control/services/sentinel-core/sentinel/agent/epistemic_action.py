from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import Field, model_validator

from sentinel.agent.event_bus import EventBus
from sentinel.agent.events import AgentEventType
from sentinel.mission.models import MissionAction, MissionAuthorityEnvelope
from sentinel.shared.enums import ExternalityLevel, ReversibilityLevel, SensitivityLevel
from sentinel.shared.models import SentinelModel


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


def _round(value: float) -> float:
    return round(_clamp01(value), 6)


def _stable_id(prefix: str, payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return f"{prefix}_{hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:16]}"


class EpistemicActionScore(SentinelModel):
    id: str = ""
    mission_id: str
    action_id: str
    action_type: str
    tool: str
    expected_progress: float = Field(ge=0.0, le=1.0)
    expected_information_gain: float = Field(ge=0.0, le=1.0)
    risk_penalty: float = Field(ge=0.0, le=1.0)
    cost_penalty: float = Field(ge=0.0, le=1.0)
    authority_impact: float = Field(ge=0.0, le=1.0)
    total_action_value: float
    authority_allowed: bool = False
    curiosity_loop_blocked: bool = False
    action_executed: bool = False
    advisory_only: bool = True
    authority_expansion: bool = False
    trace_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate(self) -> EpistemicActionScore:
        if not self.id:
            self.id = _stable_id(
                "eascore",
                {
                    "mission_id": self.mission_id,
                    "action_id": self.action_id,
                    "expected_progress": self.expected_progress,
                    "expected_information_gain": self.expected_information_gain,
                    "risk_penalty": self.risk_penalty,
                    "cost_penalty": self.cost_penalty,
                    "authority_impact": self.authority_impact,
                    "total_action_value": self.total_action_value,
                },
            )
        return self


class EpistemicActionEvaluator:
    """Scores actions by progress and information gain without executing them."""

    def score(
        self,
        envelope: MissionAuthorityEnvelope,
        action: MissionAction,
        *,
        mission_entropy: float = 0.5,
        expected_progress: float | None = None,
        expected_information_gain: float | None = None,
        event_bus: EventBus | None = None,
    ) -> EpistemicActionScore:
        if action.mission_id != envelope.id:
            raise ValueError("MissionAction mission_id must match MissionAuthorityEnvelope id.")
        authority_allowed = self._authority_allowed(envelope, action)
        progress = _round(expected_progress if expected_progress is not None else self._progress(action, mission_entropy))
        info_gain = _round(expected_information_gain if expected_information_gain is not None else self._information_gain(action, mission_entropy))
        curiosity_loop_blocked = False
        if info_gain >= 0.75 and progress <= 0.20:
            curiosity_loop_blocked = True
            info_gain = min(info_gain, 0.25)
        risk_penalty = self._risk_penalty(action)
        cost_penalty = self._cost_penalty(envelope, action)
        authority_impact = self._authority_impact(envelope, action, authority_allowed)
        total = round(progress + info_gain - risk_penalty - cost_penalty - authority_impact, 6)
        score = EpistemicActionScore(
            mission_id=envelope.id,
            action_id=action.id,
            action_type=action.action_type,
            tool=action.tool,
            expected_progress=progress,
            expected_information_gain=info_gain,
            risk_penalty=risk_penalty,
            cost_penalty=cost_penalty,
            authority_impact=authority_impact,
            total_action_value=total,
            authority_allowed=authority_allowed,
            curiosity_loop_blocked=curiosity_loop_blocked,
        )
        return self._record(score, event_bus)

    def rank(
        self,
        envelope: MissionAuthorityEnvelope,
        actions: list[MissionAction],
        *,
        mission_entropy: float = 0.5,
    ) -> list[EpistemicActionScore]:
        scores = [self.score(envelope, action, mission_entropy=mission_entropy) for action in actions]
        return sorted(scores, key=lambda item: item.total_action_value, reverse=True)

    @staticmethod
    def _authority_allowed(envelope: MissionAuthorityEnvelope, action: MissionAction) -> bool:
        forbidden = {item.lower() for item in envelope.forbidden_actions}
        return (
            action.action_type in envelope.allowed_actions
            and action.tool in envelope.allowed_tools
            and action.action_type.lower() not in forbidden
            and action.tool.lower() not in forbidden
        )

    @staticmethod
    def _progress(action: MissionAction, mission_entropy: float) -> float:
        base = 0.45
        if mission_entropy < 0.25:
            base += 0.25
        if action.evidence_refs:
            base += 0.10
        if action.confidence.value == "high":
            base += 0.10
        return _round(base)

    @staticmethod
    def _information_gain(action: MissionAction, mission_entropy: float) -> float:
        exploratory = any(token in action.intent.lower() for token in ("learn", "research", "probe", "validate", "compare", "test"))
        gain = mission_entropy * 0.65
        if exploratory:
            gain += 0.25
        if mission_entropy < 0.25 and exploratory:
            gain *= 0.15
        if action.evidence_refs:
            gain -= 0.10
        return _round(gain)

    @staticmethod
    def _risk_penalty(action: MissionAction) -> float:
        penalty = action.risk_score / 100.0
        if action.externality in {ExternalityLevel.EXTERNAL_PRIVATE, ExternalityLevel.EXTERNAL_PUBLIC}:
            penalty += 0.20
        if action.reversibility == ReversibilityLevel.IRREVERSIBLE:
            penalty += 0.20
        if action.sensitivity in {SensitivityLevel.FINANCIAL, SensitivityLevel.SECRET, SensitivityLevel.IDENTITY, SensitivityLevel.PERSONAL}:
            penalty += 0.15
        return _round(penalty)

    @staticmethod
    def _cost_penalty(envelope: MissionAuthorityEnvelope, action: MissionAction) -> float:
        if envelope.max_cost_usd <= 0:
            return 0.0
        return _round((action.estimated_cost / envelope.max_cost_usd) * 0.50)

    @staticmethod
    def _authority_impact(envelope: MissionAuthorityEnvelope, action: MissionAction, authority_allowed: bool) -> float:
        if not authority_allowed:
            return 1.0
        if action.action_type in {"payment", "spend_money", "payment_send", "credential_access", "send_email"}:
            return 0.85
        if action.externality in {ExternalityLevel.EXTERNAL_PRIVATE, ExternalityLevel.EXTERNAL_PUBLIC}:
            return 0.25
        return 0.0

    @staticmethod
    def _record(score: EpistemicActionScore, event_bus: EventBus | None) -> EpistemicActionScore:
        if event_bus is None:
            return score
        event = event_bus.append(
            AgentEventType.EPISTEMIC_ACTION_SCORED,
            "Epistemic action scored advisably without execution or authority expansion.",
            payload={
                "score_id": score.id,
                "action_id": score.action_id,
                "expected_progress": score.expected_progress,
                "expected_information_gain": score.expected_information_gain,
                "risk_penalty": score.risk_penalty,
                "cost_penalty": score.cost_penalty,
                "authority_impact": score.authority_impact,
                "total_action_value": score.total_action_value,
                "authority_allowed": score.authority_allowed,
                "curiosity_loop_blocked": score.curiosity_loop_blocked,
                "action_executed": False,
                "advisory_only": True,
                "authority_expansion": False,
            },
            trace_refs=list(score.trace_refs),
        )
        return score.model_copy(update={"trace_refs": [event.id]})
