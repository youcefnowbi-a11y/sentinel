from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from sentinel.agent.agent_count import AgentCountRoute
from sentinel.agent.event_bus import EventBus
from sentinel.agent.events import AgentEventType
from sentinel.agent.mission_entropy import MissionEntropyEstimate
from sentinel.mission.models import MissionAuthorityEnvelope
from sentinel.shared.models import SentinelModel, new_id


class AgentRolePurpose(StrEnum):
    EXPLORATION = "exploration"
    VERIFICATION = "verification"
    AGGREGATION = "aggregation"
    CONTRADICTION = "contradiction"
    COST_CONTROL = "cost_control"
    CONTEXT_COMPRESSION = "context_compression"
    AUTHORITY_BOUND_FALLBACK = "authority_bound_fallback"


class AgentSocietyPlanStatus(StrEnum):
    PLANNED = "planned"
    REJECTED = "rejected"


class AgentOutputContract(SentinelModel):
    format: str = "structured_markdown"
    required_sections: list[str] = Field(default_factory=list)
    evidence_refs_required: bool = True
    prohibited_outputs: list[str] = Field(default_factory=lambda: ["new_authority", "runtime_execution", "agent_spawn"])


class AgentRoleAssignment(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("arole"))
    role: str
    mission_id: str
    scope: str
    first_principles_purpose: list[AgentRolePurpose]
    allowed_tools: list[str] = Field(default_factory=list)
    allowed_actions: list[str] = Field(default_factory=list)
    context_budget: int = Field(ge=0)
    output_contract: AgentOutputContract
    evidence_required: bool = True
    timeout: int = Field(ge=1)
    authority_level: str = "mission_envelope_subset"
    trace_refs: list[str] = Field(default_factory=list)


class AgentSocietyPlan(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("asoc"))
    mission_id: str
    status: AgentSocietyPlanStatus
    agent_count: int = Field(ge=0)
    max_parallel_agents: int = Field(ge=0)
    roles: list[AgentRoleAssignment] = Field(default_factory=list)
    advisory_only: bool = True
    authority_expansion: bool = False
    agent_spawning: bool = False
    runtime_multi_agent_execution: bool = False
    errors: list[str] = Field(default_factory=list)
    trace_refs: list[str] = Field(default_factory=list)


class AgentSocietyManager:
    """Creates advisory role plans without spawning or executing agents."""

    BASE_SEQUENCE = [
        ("planner_agent", [AgentRolePurpose.EXPLORATION]),
        ("research_agent", [AgentRolePurpose.EXPLORATION]),
        ("verifier_agent", [AgentRolePurpose.VERIFICATION]),
        ("skeptic_agent", [AgentRolePurpose.CONTRADICTION]),
        ("aggregator_agent", [AgentRolePurpose.AGGREGATION, AgentRolePurpose.CONTEXT_COMPRESSION]),
        ("cost_control_agent", [AgentRolePurpose.COST_CONTROL]),
        ("context_compression_agent", [AgentRolePurpose.CONTEXT_COMPRESSION]),
        ("resourcefulness_agent", [AgentRolePurpose.AUTHORITY_BOUND_FALLBACK]),
    ]

    def plan(
        self,
        envelope: MissionAuthorityEnvelope,
        route: AgentCountRoute,
        estimate: MissionEntropyEstimate,
        *,
        event_bus: EventBus | None = None,
        blocked_tools: list[str] | None = None,
        unavailable_capabilities: list[str] | None = None,
        uncertain_path_detected: bool = False,
    ) -> AgentSocietyPlan:
        if route.mission_id != envelope.id or estimate.mission_id != envelope.id:
            raise ValueError("AgentSocietyManager route/estimate mission_id must match the envelope.")
        if route.recommended_agent_count <= 0 or route.extreme_swarm_blocked:
            plan = AgentSocietyPlan(
                mission_id=envelope.id,
                status=AgentSocietyPlanStatus.REJECTED,
                agent_count=0,
                max_parallel_agents=0,
                errors=["agent_count_route_not_plannable"],
            )
            return self._record_plan(plan, route, event_bus)

        target_count = min(route.recommended_agent_count, route.max_parallel_agents)
        role_specs = self._role_specs(target_count, route, estimate, blocked_tools or [], unavailable_capabilities or [], uncertain_path_detected)
        roles = [
            self._role(envelope, role_name, purposes, target_count=target_count, index=index)
            for index, (role_name, purposes) in enumerate(role_specs[:target_count])
        ]
        plan = AgentSocietyPlan(
            mission_id=envelope.id,
            status=AgentSocietyPlanStatus.PLANNED,
            agent_count=len(roles),
            max_parallel_agents=route.max_parallel_agents,
            roles=roles,
        )
        plan = self.validate_plan(plan)
        return self._record_plan(plan, route, event_bus)

    def validate_plan(self, plan: AgentSocietyPlan) -> AgentSocietyPlan:
        errors = list(plan.errors)
        if len(plan.roles) > 1 and not any(role.role == "aggregator_agent" for role in plan.roles):
            errors.append("multi_role_plan_missing_aggregator")
        for role in plan.roles:
            if not role.first_principles_purpose:
                errors.append(f"role_missing_first_principles_purpose:{role.role}")
        status = AgentSocietyPlanStatus.REJECTED if errors else plan.status
        return plan.model_copy(update={"status": status, "errors": errors})

    def _role_specs(
        self,
        target_count: int,
        route: AgentCountRoute,
        estimate: MissionEntropyEstimate,
        blocked_tools: list[str],
        unavailable_capabilities: list[str],
        uncertain_path_detected: bool,
    ) -> list[tuple[str, list[AgentRolePurpose]]]:
        if target_count == 1:
            return [self.BASE_SEQUENCE[0]]

        specs = [
            ("planner_agent", [AgentRolePurpose.EXPLORATION]),
            ("research_agent", [AgentRolePurpose.EXPLORATION]),
            ("aggregator_agent", [AgentRolePurpose.AGGREGATION, AgentRolePurpose.CONTEXT_COMPRESSION]),
        ]
        if route.entropy_band in {"high", "very_high"}:
            specs.extend(
                [
                    ("verifier_agent", [AgentRolePurpose.VERIFICATION]),
                    ("skeptic_agent", [AgentRolePurpose.CONTRADICTION]),
                ]
            )
        if estimate.budget_pressure >= 0.60:
            specs.append(("cost_control_agent", [AgentRolePurpose.COST_CONTROL]))
        if target_count >= 8:
            specs.append(("context_compression_agent", [AgentRolePurpose.CONTEXT_COMPRESSION]))
        if uncertain_path_detected or blocked_tools or unavailable_capabilities or estimate.tool_uncertainty >= 0.50:
            specs.append(("resourcefulness_agent", [AgentRolePurpose.AUTHORITY_BOUND_FALLBACK]))

        shard_index = 1
        while len(specs) < target_count:
            specs.append((f"exploration_shard_{shard_index}", [AgentRolePurpose.EXPLORATION]))
            shard_index += 1
        return specs

    def _role(
        self,
        envelope: MissionAuthorityEnvelope,
        role_name: str,
        purposes: list[AgentRolePurpose],
        *,
        target_count: int,
        index: int,
    ) -> AgentRoleAssignment:
        allowed_tools = self._tool_subset(envelope, role_name)
        allowed_actions = self._action_subset(envelope, role_name)
        return AgentRoleAssignment(
            role=role_name,
            mission_id=envelope.id,
            scope=self._scope(role_name),
            first_principles_purpose=purposes,
            allowed_tools=allowed_tools,
            allowed_actions=allowed_actions,
            context_budget=max(800, round(12000 / max(1, target_count))),
            output_contract=self._output_contract(role_name),
            evidence_required=role_name not in {"cost_control_agent", "context_compression_agent"},
            timeout=max(60, 300 - (index * 5)),
        )

    @staticmethod
    def _tool_subset(envelope: MissionAuthorityEnvelope, role_name: str) -> list[str]:
        tools = list(dict.fromkeys(envelope.allowed_tools))
        if role_name in {"aggregator_agent", "cost_control_agent", "context_compression_agent"}:
            return tools[:1]
        return tools

    @staticmethod
    def _action_subset(envelope: MissionAuthorityEnvelope, role_name: str) -> list[str]:
        forbidden = set(envelope.forbidden_actions)
        actions = [action for action in dict.fromkeys(envelope.allowed_actions) if action not in forbidden]
        if role_name in {"aggregator_agent", "cost_control_agent", "context_compression_agent"}:
            preferred = [action for action in actions if action in {"create_markdown_file", "export_json", "write_trace"}]
            return preferred or actions[:1]
        return actions

    @staticmethod
    def _scope(role_name: str) -> str:
        return {
            "planner_agent": "Propose bounded mission strategy from accepted context.",
            "research_agent": "Explore evidence needs and open questions inside authority.",
            "verifier_agent": "Verify claims against available evidence.",
            "skeptic_agent": "Find contradictions, unsupported claims, and risk blind spots.",
            "aggregator_agent": "Aggregate role outputs and compress context.",
            "cost_control_agent": "Track cognitive budget and avoid waste.",
            "context_compression_agent": "Prepare compact workspace summaries.",
            "resourcefulness_agent": "Find authorized fallback routes when blocked.",
        }.get(role_name, "Explore one bounded mission branch inside authority.")

    @staticmethod
    def _output_contract(role_name: str) -> AgentOutputContract:
        base = ["summary", "evidence_refs", "residual_uncertainty"]
        if role_name == "aggregator_agent":
            base = ["accepted_claims", "rejected_claims", "open_questions", "evidence_refs"]
        elif role_name == "cost_control_agent":
            base = ["cost_risks", "budget_recommendation"]
        elif role_name == "resourcefulness_agent":
            base = ["allowed_fallbacks", "blocked_authority", "partial_success_option"]
        return AgentOutputContract(required_sections=base)

    def _record_plan(
        self,
        plan: AgentSocietyPlan,
        route: AgentCountRoute,
        event_bus: EventBus | None,
    ) -> AgentSocietyPlan:
        if event_bus is None:
            return plan
        role_events = []
        roles = []
        for role in plan.roles:
            event = event_bus.append(
                AgentEventType.AGENT_ROLE_ASSIGNED,
                "Advisory agent role assigned without spawning or executing an agent.",
                payload={
                    "plan_id": plan.id,
                    "role_id": role.id,
                    "role": role.role,
                    "first_principles_purpose": [purpose.value for purpose in role.first_principles_purpose],
                    "allowed_tools": role.allowed_tools,
                    "allowed_actions": role.allowed_actions,
                    "context_budget": role.context_budget,
                    "advisory_only": True,
                    "agent_spawning": False,
                    "runtime_multi_agent_execution": False,
                    "authority_expansion": False,
                },
                trace_refs=list(route.trace_refs),
            )
            role_events.append(event.id)
            roles.append(role.model_copy(update={"trace_refs": [event.id]}))
        plan_event = event_bus.append(
            AgentEventType.AGENT_SOCIETY_PLANNED,
            "Advisory agent society plan created without spawning or execution.",
            payload={
                "plan_id": plan.id,
                "status": plan.status.value,
                "agent_count": len(roles),
                "max_parallel_agents": plan.max_parallel_agents,
                "role_ids": [role.id for role in roles],
                "roles": [role.role for role in roles],
                "errors": plan.errors,
                "advisory_only": True,
                "agent_spawning": False,
                "runtime_multi_agent_execution": False,
                "authority_expansion": False,
            },
            trace_refs=[*route.trace_refs, *role_events],
        )
        return plan.model_copy(update={"roles": roles, "trace_refs": [plan_event.id], "agent_count": len(roles)})
