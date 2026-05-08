from __future__ import annotations

from sentinel.agent.event_bus import EventBus
from sentinel.agent.events import AgentEventType
from sentinel.capabilities.models import CapabilityManifest, CapabilityManifestStatus, CapabilityPolicyDecision, ToolInvocation
from sentinel.capabilities.policy import CapabilityPolicy
from sentinel.mission.models import MissionAuthorityEnvelope


class ToolRegistry:
    def __init__(self, *, policy: CapabilityPolicy | None = None) -> None:
        self._manifests: dict[str, CapabilityManifest | None] = {}
        self.policy = policy or CapabilityPolicy()

    def register(self, manifest: CapabilityManifest) -> None:
        if not manifest.id.strip() or manifest.id != manifest.id.strip():
            raise ValueError("Tool id must be non-empty and must not contain leading or trailing whitespace.")
        if manifest.id in self._manifests:
            raise ValueError(f"Tool `{manifest.id}` is already registered.")
        self._manifests[manifest.id] = self._clone_manifest(manifest)

    def register_unmanifested(self, tool_id: str) -> None:
        if not tool_id.strip() or tool_id != tool_id.strip():
            raise ValueError("Tool id must be non-empty and must not contain leading or trailing whitespace.")
        if tool_id in self._manifests:
            raise ValueError(f"Tool `{tool_id}` is already registered.")
        self._manifests[tool_id] = None

    def get(self, tool_id: str) -> CapabilityManifest:
        manifest = self._manifests.get(tool_id)
        if manifest is None:
            raise KeyError(f"Tool `{tool_id}` has no manifest.")
        return self._clone_manifest(manifest)

    def maybe_get(self, tool_id: str) -> CapabilityManifest | None:
        manifest = self._manifests.get(tool_id)
        if manifest is None:
            return None
        return self._clone_manifest(manifest)

    def list_tools(self) -> list[str]:
        return sorted(self._manifests)

    def manifests(self) -> list[CapabilityManifest]:
        return [self._clone_manifest(manifest) for manifest in self._manifests.values() if manifest is not None]

    def manifests_for_capability(self, capability: str, mission_type: str | None = None) -> list[CapabilityManifest]:
        matches: list[CapabilityManifest] = []
        for manifest in self.manifests():
            if capability not in manifest.capabilities:
                continue
            if mission_type is not None and manifest.mission_scopes_allowed and mission_type not in manifest.mission_scopes_allowed:
                continue
            matches.append(manifest)
        return sorted(matches, key=lambda manifest: manifest.id)

    def has_capability(
        self,
        capability: str,
        mission_type: str,
        *,
        approved_only: bool = False,
        allowed_tool_ids: set[str] | None = None,
    ) -> bool:
        for manifest in self.manifests():
            if allowed_tool_ids is not None and manifest.id not in allowed_tool_ids:
                continue
            if capability not in manifest.capabilities:
                continue
            if manifest.mission_scopes_allowed and mission_type not in manifest.mission_scopes_allowed:
                continue
            if approved_only and manifest.status != CapabilityManifestStatus.APPROVED:
                continue
            return True
        return False

    def decide(
        self,
        invocation: ToolInvocation,
        envelope: MissionAuthorityEnvelope,
        *,
        event_bus: EventBus,
    ) -> CapabilityPolicyDecision:
        if event_bus.mission_id != envelope.id:
            raise ValueError("Tool registry decision trace mission_id must match the mission authority envelope.")
        manifest = self.maybe_get(invocation.tool_id)
        decision = self.policy.decide(manifest, invocation, envelope)
        event = event_bus.append(
            AgentEventType.TOOL_POLICY_DECIDED,
            "Capability registry policy decision recorded.",
            payload={
                "tool_id": decision.tool_id,
                "action": decision.action,
                "status": decision.status,
                "allowed": decision.allowed,
                "reason": decision.reason,
                "risk_class": decision.risk_class,
                "manifest_status": decision.manifest_status,
                "requested_side_effects": invocation.requested_side_effects,
                "capability": invocation.capability,
            },
        )
        decision = decision.model_copy(update={"trace_event_id": event.id})
        return decision

    def export_json(self) -> list[dict]:
        return [manifest.model_dump(mode="json") for manifest in self.manifests()]

    @staticmethod
    def _clone_manifest(manifest: CapabilityManifest) -> CapabilityManifest:
        return manifest.model_copy(deep=True)
