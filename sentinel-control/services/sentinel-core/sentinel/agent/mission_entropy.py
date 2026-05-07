from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from pydantic import Field

from sentinel.agent.event_bus import EventBus
from sentinel.agent.events import AgentEventType
from sentinel.mission.models import MissionAuthorityEnvelope
from sentinel.shared.models import SentinelModel, new_id


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


def _round(value: float) -> float:
    return round(_clamp01(value), 6)


class MissionEntropyEstimate(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("ment"))
    mission_id: str
    mission_entropy: float = Field(ge=0.0, le=1.0)
    domain_breadth: float = Field(ge=0.0, le=1.0)
    evidence_gap: float = Field(ge=0.0, le=1.0)
    parallelizability: float = Field(ge=0.0, le=1.0)
    impact_level: float = Field(ge=0.0, le=1.0)
    tool_uncertainty: float = Field(ge=0.0, le=1.0)
    budget_pressure: float = Field(ge=0.0, le=1.0)
    entropy_band: str
    advisory_only: bool = True
    authority_expansion: bool = False
    reasons: list[str] = Field(default_factory=list)
    trace_refs: list[str] = Field(default_factory=list)


class MissionEntropyEstimator:
    """Deterministically estimates mission uncertainty without granting authority."""

    DOMAIN_KEYWORDS = {
        "browser",
        "code",
        "security",
        "math",
        "research",
        "market",
        "competitor",
        "customer",
        "legal",
        "finance",
        "data",
        "production",
        "email",
        "channel",
        "desktop",
    }
    EVIDENCE_KEYWORDS = {"prove", "validate", "verify", "unknown", "missing", "research", "compare", "audit"}
    PARALLEL_KEYWORDS = {"compare", "multiple", "many", "list", "across", "each", "sources", "competitors", "scan", "batch"}
    IMPACT_KEYWORDS = {"send", "payment", "credential", "production", "account", "desktop", "deploy", "delete", "external"}

    def estimate(
        self,
        envelope: MissionAuthorityEnvelope,
        *,
        user_input: dict[str, Any] | None = None,
        evidence_refs: list[str] | None = None,
        open_questions: list[str] | None = None,
        selected_tools: list[str] | None = None,
        blocked_tools: list[str] | None = None,
        unavailable_capabilities: list[str] | None = None,
        event_bus: EventBus | None = None,
    ) -> MissionEntropyEstimate:
        text = self._mission_text(envelope, user_input)
        domain_breadth = self._domain_breadth(envelope, text)
        evidence_gap = self._evidence_gap(envelope, text, evidence_refs or [], open_questions or [])
        parallelizability = self._parallelizability(envelope, text)
        impact_level = self._impact_level(envelope, text)
        tool_uncertainty = self._tool_uncertainty(envelope, selected_tools or [], blocked_tools or [], unavailable_capabilities or [])
        budget_pressure = self._budget_pressure(envelope)
        mission_entropy = _round(
            (0.22 * domain_breadth)
            + (0.28 * evidence_gap)
            + (0.18 * parallelizability)
            + (0.16 * impact_level)
            + (0.10 * tool_uncertainty)
            + (0.06 * budget_pressure)
        )
        estimate = MissionEntropyEstimate(
            mission_id=envelope.id,
            mission_entropy=mission_entropy,
            domain_breadth=domain_breadth,
            evidence_gap=evidence_gap,
            parallelizability=parallelizability,
            impact_level=impact_level,
            tool_uncertainty=tool_uncertainty,
            budget_pressure=budget_pressure,
            entropy_band=self._band(mission_entropy),
            reasons=self._reasons(
                domain_breadth,
                evidence_gap,
                parallelizability,
                impact_level,
                tool_uncertainty,
                budget_pressure,
            ),
        )
        if event_bus is None:
            return estimate
        event = event_bus.append(
            AgentEventType.MISSION_ENTROPY_ESTIMATED,
            "Mission entropy estimated deterministically without changing authority.",
            payload={
                "estimate_id": estimate.id,
                "mission_entropy": estimate.mission_entropy,
                "domain_breadth": estimate.domain_breadth,
                "evidence_gap": estimate.evidence_gap,
                "parallelizability": estimate.parallelizability,
                "impact_level": estimate.impact_level,
                "tool_uncertainty": estimate.tool_uncertainty,
                "budget_pressure": estimate.budget_pressure,
                "entropy_band": estimate.entropy_band,
                "advisory_only": True,
                "authority_expansion": False,
                "reasons": estimate.reasons,
            },
        )
        return estimate.model_copy(update={"trace_refs": [event.id]})

    @classmethod
    def _mission_text(cls, envelope: MissionAuthorityEnvelope, user_input: dict[str, Any] | None) -> str:
        parts = [
            envelope.mission_title,
            envelope.mission_objective,
            " ".join(envelope.success_criteria),
            " ".join(envelope.allowed_systems),
            " ".join(envelope.allowed_tools),
            " ".join(envelope.allowed_actions),
        ]
        if user_input:
            parts.extend(str(value) for value in user_input.values() if isinstance(value, (str, int, float)))
        return " ".join(parts).lower()

    @classmethod
    def _keyword_score(cls, text: str, keywords: Iterable[str], weight: float) -> float:
        return min(1.0, sum(1 for keyword in keywords if keyword in text) * weight)

    @classmethod
    def _domain_breadth(cls, envelope: MissionAuthorityEnvelope, text: str) -> float:
        score = cls._keyword_score(text, cls.DOMAIN_KEYWORDS, 0.075)
        score += max(0, len(envelope.allowed_systems) - 1) * 0.12
        score += max(0, len(envelope.allowed_tools) - 1) * 0.08
        score += max(0, len(envelope.allowed_actions) - 3) * 0.025
        return _round(score)

    @classmethod
    def _evidence_gap(
        cls,
        envelope: MissionAuthorityEnvelope,
        text: str,
        evidence_refs: list[str],
        open_questions: list[str],
    ) -> float:
        required = max(1, len(envelope.success_criteria))
        score = 1.0 - min(1.0, len(evidence_refs) / required)
        score += cls._keyword_score(text, cls.EVIDENCE_KEYWORDS, 0.045)
        score += min(0.35, len(open_questions) * 0.12)
        if evidence_refs and "provided" in text:
            score -= 0.12
        return _round(score)

    @classmethod
    def _parallelizability(cls, envelope: MissionAuthorityEnvelope, text: str) -> float:
        score = cls._keyword_score(text, cls.PARALLEL_KEYWORDS, 0.10)
        score += max(0, len(envelope.success_criteria) - 1) * 0.08
        if any(char.isdigit() for char in text):
            score += 0.12
        return _round(score)

    @classmethod
    def _impact_level(cls, envelope: MissionAuthorityEnvelope, text: str) -> float:
        score = cls._keyword_score(text, cls.IMPACT_KEYWORDS, 0.11)
        if "public_web" in envelope.allowed_systems:
            score += 0.18
        if envelope.allowed_domains:
            score += 0.10
        if envelope.allowed_accounts:
            score += 0.18
        if envelope.browser_v3_authority_grants:
            score += 0.16
        if envelope.max_recipients:
            score += 0.12
        if str(envelope.mode.value if hasattr(envelope.mode, "value") else envelope.mode) == "power":
            score += 0.08
        if envelope.risk_appetite_score >= 70:
            score += 0.10
        return _round(score)

    @staticmethod
    def _tool_uncertainty(
        envelope: MissionAuthorityEnvelope,
        selected_tools: list[str],
        blocked_tools: list[str],
        unavailable_capabilities: list[str],
    ) -> float:
        score = len(blocked_tools) * 0.12
        score += len(unavailable_capabilities) * 0.14
        unselected = set(envelope.allowed_tools) - set(selected_tools)
        score += max(0, len(unselected) - 1) * 0.05
        if not envelope.allowed_tools:
            score += 0.35
        return _round(score)

    @staticmethod
    def _budget_pressure(envelope: MissionAuthorityEnvelope) -> float:
        if envelope.max_actions <= 5:
            pressure = 0.85
        elif envelope.max_actions <= 10:
            pressure = 0.60
        elif envelope.max_actions <= 20:
            pressure = 0.30
        else:
            pressure = 0.15
        if 0.0 < envelope.max_cost_usd < 0.25:
            pressure = max(pressure, 0.85)
        elif 0.0 < envelope.max_cost_usd < 1.0:
            pressure = max(pressure, 0.55)
        return _round(pressure)

    @staticmethod
    def _band(mission_entropy: float) -> str:
        if mission_entropy < 0.25:
            return "low"
        if mission_entropy < 0.50:
            return "medium"
        if mission_entropy < 0.75:
            return "high"
        return "very_high"

    @staticmethod
    def _reasons(*scores: float) -> list[str]:
        names = [
            "domain_breadth",
            "evidence_gap",
            "parallelizability",
            "impact_level",
            "tool_uncertainty",
            "budget_pressure",
        ]
        reasons = [f"{name}_high" for name, score in zip(names, scores, strict=True) if score >= 0.60]
        return reasons or ["bounded_low_uncertainty_path"]
