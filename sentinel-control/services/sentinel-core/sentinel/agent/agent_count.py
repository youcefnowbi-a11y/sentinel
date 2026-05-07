from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from sentinel.agent.event_bus import EventBus
from sentinel.agent.events import AgentEventType
from sentinel.agent.mission_entropy import MissionEntropyEstimate
from sentinel.mission.models import MissionAuthorityEnvelope
from sentinel.shared.models import SentinelModel, new_id


class BrainMode(StrEnum):
    FAST_BRAIN = "fast_brain"
    SMALL_SOCIETY = "small_society_advisory"
    SLOW_BRAIN = "slow_brain_advisory"
    VERY_HIGH_SOCIETY = "very_high_society_advisory"
    EXTREME_SWARM_BLOCKED = "extreme_swarm_blocked"


class AgentCountRoute(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("acroute"))
    mission_id: str
    entropy_estimate_id: str
    recommended_agent_count: int = Field(ge=0)
    brain_mode: BrainMode
    max_parallel_agents: int = Field(ge=0)
    agent_budget: int = Field(ge=0)
    reason: str
    entropy_band: str
    extreme_swarm_blocked: bool = False
    advisory_only: bool = True
    authority_expansion: bool = False
    agent_spawning: bool = False
    runtime_multi_agent_execution: bool = False
    trace_refs: list[str] = Field(default_factory=list)


class AgentCountController:
    """Routes advisory agent-count allocation without spawning agents."""

    def route(
        self,
        envelope: MissionAuthorityEnvelope,
        estimate: MissionEntropyEstimate,
        *,
        event_bus: EventBus | None = None,
        extreme_swarm_enabled: bool = False,
    ) -> AgentCountRoute:
        if estimate.mission_id != envelope.id:
            raise ValueError("AgentCountController estimate mission_id must match the envelope.")

        extreme_candidate = estimate.mission_entropy >= 0.90 and estimate.parallelizability >= 0.80
        if extreme_candidate and not extreme_swarm_enabled:
            route = AgentCountRoute(
                mission_id=envelope.id,
                entropy_estimate_id=estimate.id,
                recommended_agent_count=0,
                brain_mode=BrainMode.EXTREME_SWARM_BLOCKED,
                max_parallel_agents=0,
                agent_budget=0,
                reason="extreme_swarm_disabled_by_default",
                entropy_band=estimate.entropy_band,
                extreme_swarm_blocked=True,
            )
            return self._record(route, estimate, event_bus)

        floor, ceiling, mode = self._band_policy(estimate)
        desired = self._desired_count(estimate, floor, ceiling)
        recommended = self._apply_budget_pressure(desired, floor, estimate.budget_pressure)
        route = AgentCountRoute(
            mission_id=envelope.id,
            entropy_estimate_id=estimate.id,
            recommended_agent_count=recommended,
            brain_mode=mode,
            max_parallel_agents=recommended,
            agent_budget=recommended,
            reason=self._reason(estimate, recommended, floor, ceiling),
            entropy_band=estimate.entropy_band,
        )
        return self._record(route, estimate, event_bus)

    @staticmethod
    def _band_policy(estimate: MissionEntropyEstimate) -> tuple[int, int, BrainMode]:
        band = estimate.entropy_band
        if band == "low":
            return 1, 1, BrainMode.FAST_BRAIN
        if band == "medium":
            return 3, 5, BrainMode.SMALL_SOCIETY
        if band == "high":
            return 8, 20, BrainMode.SLOW_BRAIN
        return 20, 100, BrainMode.VERY_HIGH_SOCIETY

    @staticmethod
    def _desired_count(estimate: MissionEntropyEstimate, floor: int, ceiling: int) -> int:
        if floor == ceiling:
            return floor
        pressure = max(estimate.mission_entropy, estimate.parallelizability)
        scaled = floor + round((ceiling - floor) * pressure)
        return min(ceiling, max(floor, scaled))

    @staticmethod
    def _apply_budget_pressure(desired: int, floor: int, budget_pressure: float) -> int:
        if desired <= floor:
            return desired
        if budget_pressure >= 0.85:
            factor = 0.35
        elif budget_pressure >= 0.60:
            factor = 0.55
        elif budget_pressure >= 0.30:
            factor = 0.75
        else:
            factor = 1.0
        return max(floor, round(desired * factor))

    @staticmethod
    def _reason(estimate: MissionEntropyEstimate, recommended: int, floor: int, ceiling: int) -> str:
        parts = [f"entropy_band={estimate.entropy_band}", f"agent_count={recommended}"]
        if estimate.budget_pressure >= 0.60:
            parts.append("budget_pressure_reduced_count")
        if recommended == floor:
            parts.append("floor_count")
        if recommended == ceiling:
            parts.append("ceiling_count")
        return ";".join(parts)

    @staticmethod
    def _record(
        route: AgentCountRoute,
        estimate: MissionEntropyEstimate,
        event_bus: EventBus | None,
    ) -> AgentCountRoute:
        if event_bus is None:
            return route
        event = event_bus.append(
            AgentEventType.AGENT_COUNT_ROUTED,
            "Agent count routed advisably without spawning or executing agents.",
            payload={
                "route_id": route.id,
                "entropy_estimate_id": estimate.id,
                "recommended_agent_count": route.recommended_agent_count,
                "brain_mode": route.brain_mode.value,
                "max_parallel_agents": route.max_parallel_agents,
                "agent_budget": route.agent_budget,
                "reason": route.reason,
                "entropy_band": route.entropy_band,
                "extreme_swarm_blocked": route.extreme_swarm_blocked,
                "advisory_only": True,
                "authority_expansion": False,
                "agent_spawning": False,
                "runtime_multi_agent_execution": False,
            },
            trace_refs=list(estimate.trace_refs),
        )
        return route.model_copy(update={"trace_refs": [event.id]})
