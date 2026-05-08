from __future__ import annotations

from collections.abc import Iterable

from sentinel.agent.capability_selector import ACTION_TO_CAPABILITY
from sentinel.agent.event_bus import EventBus
from sentinel.agent.events import AgentEventType
from sentinel.agent.models import AgentContext, CapabilityNeed, ToolSelectionDecision, ToolSelectionResult, ToolSelectionStatus
from sentinel.capabilities.models import CapabilityManifest, ToolInvocation
from sentinel.capabilities.registry import ToolRegistry
from sentinel.capabilities.risk import ToolExecutionStatus, ToolRiskClass, ToolSideEffect


CAPABILITY_TO_ACTIONS: dict[str, list[str]] = {}
for action, capability in ACTION_TO_CAPABILITY.items():
    CAPABILITY_TO_ACTIONS.setdefault(capability, []).append(action)


SAFE_WORKER_SIDE_EFFECTS = {
    ToolSideEffect.FILESYSTEM_WRITE,
    ToolSideEffect.LOCAL_DRAFT_WRITE,
    ToolSideEffect.NONE,
}


class ToolSelector:
    """Maps declared capability needs to registry-governed tool decisions.

    P1C is a cognitive selection phase only. This selector never executes a
    tool; it classifies candidates and records the policy trace before planning.
    """

    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def select(
        self,
        context: AgentContext,
        capabilities: list[CapabilityNeed],
        *,
        event_bus: EventBus,
    ) -> ToolSelectionResult:
        decisions: list[ToolSelectionDecision] = []
        trace_refs: list[str] = []
        missing_capabilities: set[str] = set()
        unavailable_capabilities: set[str] = set()

        mission_type = context.mission.mission_type.value if hasattr(context.mission.mission_type, "value") else str(context.mission.mission_type)
        for need in capabilities:
            manifests = self.registry.manifests_for_capability(need.name, mission_type=mission_type)
            if not manifests:
                decisions.append(
                    ToolSelectionDecision(
                        mission_id=context.mission.id,
                        capability_name=need.name,
                        decision=ToolSelectionStatus.UNAVAILABLE,
                        reason="No manifest maps to this capability.",
                        authority_allowed=need.available,
                    )
                )
                unavailable_capabilities.add(need.name)
                if need.required:
                    missing_capabilities.add(need.name)
                continue

            need_has_selectable_tool = False
            for manifest in manifests:
                requested_action = self._requested_action(need.name, manifest)
                policy_decision = self.registry.decide(
                    ToolInvocation(
                        tool_id=manifest.id,
                        action=requested_action,
                        requested_side_effects=manifest.side_effects,
                        capability=need.name,
                    ),
                    context.mission,
                    event_bus=event_bus,
                )
                if policy_decision.trace_event_id:
                    trace_refs.append(policy_decision.trace_event_id)

                status = self._selection_status(manifest, policy_decision.status, policy_decision.allowed, policy_decision.reason)
                if status in {ToolSelectionStatus.ELIGIBLE_FOR_SAFE_WORKER, ToolSelectionStatus.ELIGIBLE_FOR_DRY_RUN}:
                    need_has_selectable_tool = True

                decisions.append(
                    ToolSelectionDecision(
                        mission_id=context.mission.id,
                        capability_name=need.name,
                        requested_action=requested_action,
                        candidate_tool_id=manifest.id,
                        decision=status,
                        reason=policy_decision.reason,
                        manifest_status=manifest.status,
                        risk_class=policy_decision.risk_class,
                        side_effects=manifest.side_effects,
                        authority_allowed=policy_decision.allowed,
                        registry_policy_result=policy_decision.status,
                        trace_id=policy_decision.trace_event_id,
                    )
                )

            if not need_has_selectable_tool:
                unavailable_capabilities.add(need.name)
                if need.required:
                    missing_capabilities.add(need.name)

        result = ToolSelectionResult(
            decisions=decisions,
            selected_tools=self._unique(
                decision.candidate_tool_id
                for decision in decisions
                if decision.candidate_tool_id
                and decision.decision in {ToolSelectionStatus.ELIGIBLE_FOR_SAFE_WORKER, ToolSelectionStatus.ELIGIBLE_FOR_DRY_RUN}
            ),
            candidate_tools=self._unique(
                decision.candidate_tool_id
                for decision in decisions
                if decision.candidate_tool_id and decision.decision == ToolSelectionStatus.CANDIDATE
            ),
            blocked_tools=self._unique(
                decision.candidate_tool_id
                for decision in decisions
                if decision.candidate_tool_id and decision.decision == ToolSelectionStatus.BLOCKED
            ),
            unavailable_capabilities=sorted(unavailable_capabilities),
            missing_capabilities=sorted(missing_capabilities),
            trace_refs=trace_refs,
        )
        aggregate_event = event_bus.append(
            AgentEventType.TOOLS_SELECTED,
            "Agent selected registry-governed tool candidates without executing them.",
            payload={
                "selected_tools": result.selected_tools,
                "candidate_tools": result.candidate_tools,
                "blocked_tools": result.blocked_tools,
                "unavailable_capabilities": result.unavailable_capabilities,
                "missing_capabilities": result.missing_capabilities,
                "decision_count": len(result.decisions),
            },
            trace_refs=trace_refs,
        )
        result.trace_refs.append(aggregate_event.id)
        return result

    @staticmethod
    def _requested_action(capability: str, manifest: CapabilityManifest) -> str:
        for action in CAPABILITY_TO_ACTIONS.get(capability, ()):
            if action in manifest.allowed_actions:
                return action
        if manifest.allowed_actions:
            return manifest.allowed_actions[0]
        return f"capability:{capability}"

    @staticmethod
    def _selection_status(
        manifest: CapabilityManifest,
        registry_status: ToolExecutionStatus,
        allowed: bool,
        reason: str,
    ) -> ToolSelectionStatus:
        if allowed:
            if ToolSelector._is_safe_worker_manifest(manifest):
                return ToolSelectionStatus.ELIGIBLE_FOR_SAFE_WORKER
            return ToolSelectionStatus.ELIGIBLE_FOR_DRY_RUN
        if registry_status == ToolExecutionStatus.CANDIDATE_ONLY:
            return ToolSelectionStatus.CANDIDATE
        if reason in {
            "tool_not_granted_by_mission_authority",
            "action_not_granted_by_mission_authority",
            "mission_scope_not_allowed",
        }:
            return ToolSelectionStatus.UNAVAILABLE
        return ToolSelectionStatus.BLOCKED

    @staticmethod
    def _is_safe_worker_manifest(manifest: CapabilityManifest) -> bool:
        return (
            manifest.provider == "sentinel"
            and manifest.risk_class == ToolRiskClass.DRAFT_ONLY_WRITE
            and set(manifest.side_effects).issubset(SAFE_WORKER_SIDE_EFFECTS)
        )

    @staticmethod
    def _unique(values: Iterable[str | None]) -> list[str]:
        return sorted({value for value in values if value})
