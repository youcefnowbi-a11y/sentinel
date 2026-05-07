from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import Field, model_validator

from sentinel.agent.belief_state import BayesianBeliefState
from sentinel.agent.event_bus import EventBus
from sentinel.agent.events import AgentEventType
from sentinel.agent.mission_entropy import MissionEntropyEstimate
from sentinel.shared.models import SentinelModel


def _stable_id(prefix: str, payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return f"{prefix}_{hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:16]}"


class DebateRolePlan(SentinelModel):
    id: str = ""
    role: str
    purpose: str
    scope: str
    input_refs: list[str] = Field(default_factory=list)
    output_contract: list[str] = Field(default_factory=list)
    runtime_agent_execution: bool = False
    authority_expansion: bool = False

    @model_validator(mode="after")
    def _validate(self) -> DebateRolePlan:
        if not self.id:
            self.id = _stable_id("drole", {"role": self.role, "purpose": self.purpose, "scope": self.scope, "input_refs": self.input_refs})
        return self


class SparseMoAPlan(SentinelModel):
    id: str = ""
    layers: int = Field(ge=0)
    fan_in_limit: int = Field(ge=0)
    max_layers: int = Field(ge=0)
    max_debate_rounds: int = Field(ge=0)
    layer_role_ids: list[list[str]] = Field(default_factory=list)
    sparse_edges: list[tuple[str, str]] = Field(default_factory=list)
    planned_only: bool = True
    runtime_agent_execution: bool = False
    authority_expansion: bool = False

    @model_validator(mode="after")
    def _validate(self) -> SparseMoAPlan:
        if not self.id:
            self.id = _stable_id(
                "smoa",
                {
                    "layers": self.layers,
                    "fan_in_limit": self.fan_in_limit,
                    "max_layers": self.max_layers,
                    "max_debate_rounds": self.max_debate_rounds,
                    "layer_role_ids": self.layer_role_ids,
                    "sparse_edges": self.sparse_edges,
                },
            )
        return self


class DebateAggregationPlan(SentinelModel):
    id: str = ""
    aggregator_role: str = "aggregator_agent"
    synthesis_strategy: str = "preserve_disputes_and_merge_supported_claims"
    input_role_ids: list[str] = Field(default_factory=list)
    unresolved_disputes: list[str] = Field(default_factory=list)
    planned_only: bool = True
    runtime_agent_execution: bool = False
    authority_expansion: bool = False

    @model_validator(mode="after")
    def _validate(self) -> DebateAggregationPlan:
        if not self.id:
            self.id = _stable_id(
                "dagg",
                {
                    "aggregator_role": self.aggregator_role,
                    "synthesis_strategy": self.synthesis_strategy,
                    "input_role_ids": self.input_role_ids,
                    "unresolved_disputes": self.unresolved_disputes,
                },
            )
        return self


class DebateRoute(SentinelModel):
    id: str = ""
    mission_id: str
    debate_needed: bool
    reason: str
    debate_roles: list[DebateRolePlan] = Field(default_factory=list)
    sparse_moa_plan: SparseMoAPlan | None = None
    aggregation_plan: DebateAggregationPlan | None = None
    unresolved_disputes: list[str] = Field(default_factory=list)
    fan_in_limit: int = Field(ge=0)
    max_layers: int = Field(ge=0)
    max_debate_rounds: int = Field(ge=0)
    advisory_only: bool = True
    runtime_agent_execution: bool = False
    runtime_multi_agent_execution: bool = False
    authority_expansion: bool = False
    trace_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate(self) -> DebateRoute:
        if not self.id:
            self.id = _stable_id(
                "droute",
                {
                    "mission_id": self.mission_id,
                    "debate_needed": self.debate_needed,
                    "reason": self.reason,
                    "debate_roles": [role.id for role in self.debate_roles],
                    "unresolved_disputes": self.unresolved_disputes,
                    "fan_in_limit": self.fan_in_limit,
                    "max_layers": self.max_layers,
                    "max_debate_rounds": self.max_debate_rounds,
                },
            )
        return self


class AdaptiveDebateRouter:
    """Plans debate and Sparse MoA routing without executing agents."""

    HARD_MAX_LAYERS = 3
    HARD_MAX_ROUNDS = 3
    HARD_FAN_IN_LIMIT = 5

    def route(
        self,
        mission_id: str,
        *,
        estimate: MissionEntropyEstimate | None = None,
        belief_state: BayesianBeliefState | None = None,
        unresolved_disputes: list[str] | None = None,
        impact_level: float | None = None,
        max_layers: int = 2,
        max_debate_rounds: int = 2,
        fan_in_limit: int = 3,
        event_bus: EventBus | None = None,
    ) -> DebateRoute:
        disputes = list(unresolved_disputes or [])
        contradiction_count = 0
        high_variance = False
        if belief_state is not None:
            if belief_state.mission_id != mission_id:
                raise ValueError("Belief state mission_id must match debate mission_id.")
            contradiction_count = sum(len(belief.contradiction_support) for belief in belief_state.beliefs)
            high_variance = any(belief.belief_variance >= 0.55 for belief in belief_state.beliefs)
            disputes.extend(
                f"{belief.hypothesis_id}: contradiction present"
                for belief in belief_state.beliefs
                if belief.contradiction_support
            )
        entropy = estimate.mission_entropy if estimate is not None else 0.0
        impact = impact_level if impact_level is not None else (estimate.impact_level if estimate is not None else 0.0)
        debate_needed = bool(disputes or contradiction_count or high_variance or entropy >= 0.55 or impact >= 0.65)
        reason = self._reason(debate_needed, entropy, impact, contradiction_count, high_variance, disputes)
        bounded_layers = min(max_layers, self.HARD_MAX_LAYERS)
        bounded_rounds = min(max_debate_rounds, self.HARD_MAX_ROUNDS)
        bounded_fan_in = min(fan_in_limit, self.HARD_FAN_IN_LIMIT)

        roles = self._roles(debate_needed, disputes, contradiction_count, high_variance)
        sparse_plan = self._sparse_plan(roles, bounded_layers, bounded_rounds, bounded_fan_in) if debate_needed else None
        aggregation_plan = (
            DebateAggregationPlan(
                input_role_ids=[role.id for role in roles[:bounded_fan_in]],
                unresolved_disputes=disputes,
            )
            if debate_needed
            else None
        )
        route = DebateRoute(
            mission_id=mission_id,
            debate_needed=debate_needed,
            reason=reason,
            debate_roles=roles,
            sparse_moa_plan=sparse_plan,
            aggregation_plan=aggregation_plan,
            unresolved_disputes=disputes,
            fan_in_limit=bounded_fan_in,
            max_layers=bounded_layers,
            max_debate_rounds=bounded_rounds,
        )
        return self._record(route, event_bus)

    @staticmethod
    def _reason(
        debate_needed: bool,
        entropy: float,
        impact: float,
        contradiction_count: int,
        high_variance: bool,
        disputes: list[str],
    ) -> str:
        if not debate_needed:
            return "debate_off_low_uncertainty"
        parts = []
        if entropy >= 0.55:
            parts.append("high_entropy")
        if impact >= 0.65:
            parts.append("high_impact")
        if contradiction_count:
            parts.append("contradiction")
        if high_variance:
            parts.append("high_variance")
        if disputes:
            parts.append("unresolved_disputes")
        return ";".join(parts)

    @staticmethod
    def _roles(
        debate_needed: bool,
        disputes: list[str],
        contradiction_count: int,
        high_variance: bool,
    ) -> list[DebateRolePlan]:
        if not debate_needed:
            return []
        roles = [
            DebateRolePlan(role="proposer_agent", purpose="exploration", scope="Produce the strongest supported answer.", output_contract=["claims", "evidence_refs"]),
            DebateRolePlan(role="verifier_agent", purpose="verification", scope="Verify claims against evidence.", output_contract=["verified_claims", "evidence_refs"]),
            DebateRolePlan(role="skeptic_agent", purpose="contradiction", scope="Find contradictions and unsupported assumptions.", output_contract=["contradictions", "risk_notes"]),
            DebateRolePlan(role="aggregator_agent", purpose="aggregation", scope="Synthesize without hiding disputes.", output_contract=["accepted_claims", "unresolved_disputes"]),
        ]
        if disputes or contradiction_count or high_variance:
            roles.append(
                DebateRolePlan(
                    role="dispute_keeper_agent",
                    purpose="preserve_unresolved_disputes",
                    scope="Keep unresolved disputes visible for FinalGate.",
                    output_contract=["unresolved_disputes", "blocking_questions"],
                )
            )
        return roles

    @staticmethod
    def _sparse_plan(
        roles: list[DebateRolePlan],
        max_layers: int,
        max_debate_rounds: int,
        fan_in_limit: int,
    ) -> SparseMoAPlan:
        source_ids = [role.id for role in roles if role.role != "aggregator_agent"]
        layer_one = source_ids[:fan_in_limit]
        layer_two = [role.id for role in roles if role.role == "aggregator_agent"][:1]
        layer_role_ids = [layer_one]
        if max_layers > 1 and layer_two:
            layer_role_ids.append(layer_two)
        edges = [(source, target) for source in layer_one[:fan_in_limit] for target in layer_two]
        return SparseMoAPlan(
            layers=len(layer_role_ids),
            fan_in_limit=fan_in_limit,
            max_layers=max_layers,
            max_debate_rounds=max_debate_rounds,
            layer_role_ids=layer_role_ids,
            sparse_edges=edges,
        )

    def _record(self, route: DebateRoute, event_bus: EventBus | None) -> DebateRoute:
        if event_bus is None:
            return route
        route_event = event_bus.append(
            AgentEventType.DEBATE_ROUTED,
            "Adaptive debate routed advisably without executing agents.",
            payload={
                "route_id": route.id,
                "debate_needed": route.debate_needed,
                "reason": route.reason,
                "fan_in_limit": route.fan_in_limit,
                "max_layers": route.max_layers,
                "max_debate_rounds": route.max_debate_rounds,
                "role_count": len(route.debate_roles),
                "advisory_only": True,
                "runtime_agent_execution": False,
                "authority_expansion": False,
            },
        )
        trace_refs = [route_event.id]
        if route.sparse_moa_plan is not None:
            for layer_index, role_ids in enumerate(route.sparse_moa_plan.layer_role_ids):
                event = event_bus.append(
                    AgentEventType.MOA_LAYER_COMPLETED,
                    "Sparse MoA layer planned and marked complete without agent execution.",
                    payload={
                        "route_id": route.id,
                        "sparse_moa_plan_id": route.sparse_moa_plan.id,
                        "layer_index": layer_index,
                        "role_ids": role_ids,
                        "planned_only": True,
                        "runtime_agent_execution": False,
                        "authority_expansion": False,
                    },
                    trace_refs=trace_refs,
                )
                trace_refs.append(event.id)
        if route.aggregation_plan is not None:
            event = event_bus.append(
                AgentEventType.DEBATE_AGGREGATED,
                "Debate aggregation planned without hiding unresolved disputes.",
                payload={
                    "route_id": route.id,
                    "aggregation_plan_id": route.aggregation_plan.id,
                    "unresolved_disputes": route.unresolved_disputes,
                    "planned_only": True,
                    "runtime_agent_execution": False,
                    "authority_expansion": False,
                },
                trace_refs=trace_refs,
            )
            trace_refs.append(event.id)
        return route.model_copy(update={"trace_refs": trace_refs})
