from __future__ import annotations

from typing import Any

from sentinel.agent.capability_selector import capabilities_from_actions
from sentinel.agent.models import AgentContext
from sentinel.mission.models import MissionAuthorityEnvelope


class ContextBuilder:
    def build(
        self,
        envelope: MissionAuthorityEnvelope,
        *,
        user_input: dict[str, Any] | None = None,
        evidence_refs: list[str] | None = None,
        memory_items: list[dict[str, Any]] | None = None,
    ) -> AgentContext:
        constraints = [
            f"mission_type={envelope.mission_type.value if hasattr(envelope.mission_type, 'value') else envelope.mission_type}",
            f"max_actions={envelope.max_actions}",
            f"max_cost_usd={envelope.max_cost_usd}",
            "memory_is_context_not_authority",
            "unknown_capabilities_must_be_reported_not_executed",
        ]
        summary = f"{envelope.mission_title}: {envelope.mission_objective}"
        return AgentContext(
            mission=envelope,
            user_input=user_input or {},
            evidence_refs=evidence_refs or [],
            memory_items=memory_items or [],
            constraints=constraints,
            available_capabilities=capabilities_from_actions(list(envelope.allowed_actions)),
            available_tools=list(envelope.allowed_tools),
            world_model_refs=["mission_authority", "local_filesystem_boundary", "memory_not_authority"],
            summary=summary,
        )
