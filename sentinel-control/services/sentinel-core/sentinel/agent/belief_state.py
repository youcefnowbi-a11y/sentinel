from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import Field, model_validator

from sentinel.agent.event_bus import EventBus
from sentinel.agent.events import AgentEventType
from sentinel.shared.models import SentinelModel


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


def _round(value: float) -> float:
    return round(_clamp01(value), 6)


def _stable_id(prefix: str, payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return f"{prefix}_{hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:16]}"


class EvidenceSupport(SentinelModel):
    id: str = ""
    evidence_ref: str
    summary: str = ""
    weight: float = Field(default=0.5, ge=0.0, le=1.0)
    reliability: float = Field(default=0.5, ge=0.0, le=1.0)
    trace_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate(self) -> EvidenceSupport:
        if not self.id:
            self.id = _stable_id(
                "bsup",
                {
                    "evidence_ref": self.evidence_ref,
                    "summary": self.summary,
                    "weight": self.weight,
                    "reliability": self.reliability,
                },
            )
        return self

    @property
    def score(self) -> float:
        return _round(self.weight * self.reliability)


class ContradictionSupport(SentinelModel):
    id: str = ""
    evidence_ref: str
    summary: str = ""
    severity: float = Field(default=0.5, ge=0.0, le=1.0)
    reliability: float = Field(default=0.5, ge=0.0, le=1.0)
    trace_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate(self) -> ContradictionSupport:
        if not self.id:
            self.id = _stable_id(
                "bcon",
                {
                    "evidence_ref": self.evidence_ref,
                    "summary": self.summary,
                    "severity": self.severity,
                    "reliability": self.reliability,
                },
            )
        return self

    @property
    def score(self) -> float:
        return _round(self.severity * self.reliability)


class Belief(SentinelModel):
    id: str = ""
    mission_id: str
    hypothesis_id: str
    statement: str
    belief_probability: float = Field(default=0.5, ge=0.0, le=1.0)
    belief_variance: float = Field(default=0.5, ge=0.0, le=1.0)
    supporting_evidence: list[EvidenceSupport] = Field(default_factory=list)
    contradiction_support: list[ContradictionSupport] = Field(default_factory=list)
    posterior_update_reason: str = "prior"
    advisory_only: bool = True
    authority_expansion: bool = False
    trace_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate(self) -> Belief:
        if not self.id:
            self.id = _stable_id(
                "belief",
                {
                    "mission_id": self.mission_id,
                    "hypothesis_id": self.hypothesis_id,
                    "statement": self.statement.strip().lower(),
                },
            )
        return self

    @property
    def compatibility_status(self) -> str:
        if self.belief_probability >= 0.75 and self.belief_variance <= 0.30:
            return "verified"
        if self.belief_probability <= 0.25 and self.belief_variance <= 0.45:
            return "rejected"
        return "uncertain"


class BeliefUpdate(SentinelModel):
    id: str = ""
    mission_id: str
    belief_id: str
    prior_probability: float = Field(ge=0.0, le=1.0)
    prior_variance: float = Field(ge=0.0, le=1.0)
    posterior_probability: float = Field(ge=0.0, le=1.0)
    posterior_variance: float = Field(ge=0.0, le=1.0)
    evidence_support: list[EvidenceSupport] = Field(default_factory=list)
    contradiction_support: list[ContradictionSupport] = Field(default_factory=list)
    posterior_update_reason: str
    rejected: bool = False
    errors: list[str] = Field(default_factory=list)
    advisory_only: bool = True
    authority_expansion: bool = False
    trace_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate(self) -> BeliefUpdate:
        if not self.id:
            self.id = _stable_id(
                "bupd",
                {
                    "mission_id": self.mission_id,
                    "belief_id": self.belief_id,
                    "prior_probability": self.prior_probability,
                    "prior_variance": self.prior_variance,
                    "posterior_probability": self.posterior_probability,
                    "posterior_variance": self.posterior_variance,
                    "evidence_support": [item.id for item in self.evidence_support],
                    "contradiction_support": [item.id for item in self.contradiction_support],
                    "posterior_update_reason": self.posterior_update_reason,
                },
            )
        return self


class BayesianBeliefState(SentinelModel):
    mission_id: str
    beliefs: list[Belief] = Field(default_factory=list)
    updates: list[BeliefUpdate] = Field(default_factory=list)
    advisory_only: bool = True
    authority_expansion: bool = False

    @classmethod
    def create(cls, mission_id: str, beliefs: list[Belief] | None = None) -> BayesianBeliefState:
        for belief in beliefs or []:
            if belief.mission_id != mission_id:
                raise ValueError("Belief mission_id must match BayesianBeliefState mission_id.")
        return cls(mission_id=mission_id, beliefs=beliefs or [])

    def add_belief(self, belief: Belief) -> BayesianBeliefState:
        if belief.mission_id != self.mission_id:
            raise ValueError("Belief mission_id must match BayesianBeliefState mission_id.")
        return self.model_copy(update={"beliefs": [*self.beliefs, belief]})

    def update_belief(
        self,
        belief_id: str,
        *,
        evidence_support: list[EvidenceSupport] | None = None,
        contradiction_support: list[ContradictionSupport] | None = None,
        proposed_posterior_probability: float | None = None,
        proposed_posterior_variance: float | None = None,
        event_bus: EventBus | None = None,
    ) -> tuple[BayesianBeliefState, BeliefUpdate]:
        belief = self._belief(belief_id)
        supports = evidence_support or []
        contradictions = contradiction_support or []
        computed_probability, computed_variance, reason = self._posterior(belief, supports, contradictions)
        posterior_probability = computed_probability if proposed_posterior_probability is None else _round(proposed_posterior_probability)
        posterior_variance = computed_variance if proposed_posterior_variance is None else _round(proposed_posterior_variance)

        errors: list[str] = []
        if proposed_posterior_probability is not None and abs(posterior_probability - belief.belief_probability) > 0.35 and not supports and not contradictions:
            errors.append("unsupported_posterior_jump")
        if proposed_posterior_variance is not None and abs(posterior_variance - belief.belief_variance) > 0.35 and not supports and not contradictions:
            errors.append("unsupported_variance_jump")
        if errors:
            update = BeliefUpdate(
                mission_id=self.mission_id,
                belief_id=belief.id,
                prior_probability=belief.belief_probability,
                prior_variance=belief.belief_variance,
                posterior_probability=belief.belief_probability,
                posterior_variance=belief.belief_variance,
                evidence_support=supports,
                contradiction_support=contradictions,
                posterior_update_reason="rejected_unsupported_jump",
                rejected=True,
                errors=errors,
            )
            return self._record_update(update, event_bus, belief)

        updated_belief = belief.model_copy(
            update={
                "belief_probability": posterior_probability,
                "belief_variance": posterior_variance,
                "supporting_evidence": [*belief.supporting_evidence, *supports],
                "contradiction_support": [*belief.contradiction_support, *contradictions],
                "posterior_update_reason": reason,
            }
        )
        update = BeliefUpdate(
            mission_id=self.mission_id,
            belief_id=belief.id,
            prior_probability=belief.belief_probability,
            prior_variance=belief.belief_variance,
            posterior_probability=posterior_probability,
            posterior_variance=posterior_variance,
            evidence_support=supports,
            contradiction_support=contradictions,
            posterior_update_reason=reason,
        )
        next_beliefs = [updated_belief if item.id == belief.id else item for item in self.beliefs]
        next_state = self.model_copy(update={"beliefs": next_beliefs, "updates": [*self.updates, update]})
        return next_state._record_update(update, event_bus, updated_belief)

    def compatibility_view(self) -> dict[str, list[str]]:
        return {
            "verified": [belief.hypothesis_id for belief in self.beliefs if belief.compatibility_status == "verified"],
            "rejected": [belief.hypothesis_id for belief in self.beliefs if belief.compatibility_status == "rejected"],
            "uncertain": [belief.hypothesis_id for belief in self.beliefs if belief.compatibility_status == "uncertain"],
        }

    def _belief(self, belief_id: str) -> Belief:
        for belief in self.beliefs:
            if belief.id == belief_id or belief.hypothesis_id == belief_id:
                return belief
        raise ValueError("Unknown belief_id.")

    @staticmethod
    def _posterior(
        belief: Belief,
        supports: list[EvidenceSupport],
        contradictions: list[ContradictionSupport],
    ) -> tuple[float, float, str]:
        support_score = min(1.0, sum(item.score for item in supports))
        contradiction_score = min(1.0, sum(item.score for item in contradictions))
        delta = (0.35 * support_score) - (0.35 * contradiction_score)
        posterior_probability = _round(belief.belief_probability + delta)
        if contradictions and supports:
            posterior_variance = _round(belief.belief_variance + (0.20 * contradiction_score) - (0.08 * support_score))
            reason = "mixed_support_and_contradiction"
        elif contradictions:
            posterior_variance = _round(belief.belief_variance + (0.25 * contradiction_score))
            reason = "contradiction_widened_variance"
        elif supports:
            posterior_variance = _round(belief.belief_variance - (0.25 * support_score))
            reason = "supporting_evidence_narrowed_variance"
        else:
            posterior_variance = belief.belief_variance
            reason = "no_new_evidence"
        return posterior_probability, posterior_variance, reason

    def _record_update(
        self,
        update: BeliefUpdate,
        event_bus: EventBus | None,
        belief: Belief,
    ) -> tuple[BayesianBeliefState, BeliefUpdate]:
        if update not in self.updates:
            state = self.model_copy(update={"updates": [*self.updates, update]})
        else:
            state = self
        if event_bus is None:
            return state, update
        event = event_bus.append(
            AgentEventType.BELIEF_STATE_UPDATED,
            "Bayesian belief state updated advisably without changing authority.",
            payload={
                "belief_id": belief.id,
                "hypothesis_id": belief.hypothesis_id,
                "prior_probability": update.prior_probability,
                "prior_variance": update.prior_variance,
                "posterior_probability": update.posterior_probability,
                "posterior_variance": update.posterior_variance,
                "posterior_update_reason": update.posterior_update_reason,
                "compatibility_status": belief.compatibility_status,
                "rejected": update.rejected,
                "errors": update.errors,
                "advisory_only": True,
                "authority_expansion": False,
            },
            trace_refs=[*update.trace_refs, *belief.trace_refs],
        )
        traced_update = update.model_copy(update={"trace_refs": [event.id]})
        traced_beliefs = [belief.model_copy(update={"trace_refs": [*belief.trace_refs, event.id]}) if item.id == belief.id else item for item in state.beliefs]
        traced_updates = [traced_update if item.id == update.id else item for item in state.updates]
        return state.model_copy(update={"beliefs": traced_beliefs, "updates": traced_updates}), traced_update
