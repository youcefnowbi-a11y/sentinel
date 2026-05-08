from __future__ import annotations

from typing import TYPE_CHECKING

from sentinel.agent.models import AgentContext, CapabilityNeed, MethodRef
from sentinel.shared.enums import MissionType

if TYPE_CHECKING:
    from sentinel.capabilities.registry import ToolRegistry


ACTION_TO_CAPABILITY = {
    "create_project_folder": "local_workspace_write",
    "create_markdown_file": "local_markdown_write",
    "export_json": "local_json_export",
    "generate_gtm_pack": "gtm_pack_generation",
    "generate_landing_copy": "landing_copy_generation",
    "generate_outreach_drafts_without_sending": "outreach_draft_generation",
    "create_watchlist": "watchlist_generation",
    "generate_research_questions": "roadmap_generation",
    "write_trace": "trace_write",
    "browser_read_public_page": "browser_research",
    "browser_render_public_page": "browser_research",
    "browser_form_submit": "public_web_form_submit",
}


def capabilities_from_actions(actions: list[str]) -> list[str]:
    return sorted({ACTION_TO_CAPABILITY[action] for action in actions if action in ACTION_TO_CAPABILITY})


class CapabilitySelector:
    def __init__(self, registry: ToolRegistry | None = None) -> None:
        self.registry = registry

    def select(self, context: AgentContext, methods: list[MethodRef]) -> list[CapabilityNeed]:
        available = set(context.available_capabilities)
        needs: list[CapabilityNeed] = []
        mission_type = context.mission.mission_type.value if hasattr(context.mission.mission_type, "value") else str(context.mission.mission_type)
        allowed_tool_ids = set(context.mission.allowed_tools)

        def add(name: str, reason: str, required: bool = True) -> None:
            granted_by_authority = name in available
            if self.registry is None:
                has_approved_manifest = True
            else:
                has_approved_manifest = self.registry.has_capability(
                    name,
                    mission_type,
                    approved_only=True,
                    allowed_tool_ids=allowed_tool_ids,
                )
            is_available = granted_by_authority and has_approved_manifest
            missing_reason = (
                self._missing_reason(name, mission_type, granted_by_authority, allowed_tool_ids)
                if not is_available
                else None
            )
            needs.append(
                CapabilityNeed(
                    name=name,
                    reason=reason,
                    required=required,
                    available=is_available,
                    missing_reason=missing_reason,
                )
            )

        if context.mission.mission_type == MissionType.GTM:
            add("local_workspace_write", "GTM mission needs a local workspace.")
            add("gtm_pack_generation", "GTM mission needs core pack generation.")
            add("landing_copy_generation", "GTM mission needs landing copy artifact.")
            add("outreach_draft_generation", "GTM mission needs draft-only outreach.")
            add("watchlist_generation", "GTM mission needs a watchlist artifact.")
            add("browser_research", "Future launch-quality GTM would benefit from browser research.", required=False)
            add("image_generation", "Future launch-quality GTM would benefit from visual assets.", required=False)
        elif context.mission.mission_type == MissionType.RESEARCH_SUMMARY:
            add("local_workspace_write", "Research mission needs a local workspace.")
            add("local_markdown_write", "Research mission needs markdown export.")
            if "browser_form_submit" in set(context.mission.allowed_actions):
                add("public_web_form_submit", "Research mission grants a governed Browser V3 public form submit route.")
            add("browser_research", "Future research quality would benefit from read-only browser evidence.", required=False)
        else:
            add("mission_decomposition", "Unknown mission type needs conservative decomposition.", required=False)

        return needs

    def _missing_reason(
        self,
        capability: str,
        mission_type: str,
        granted_by_authority: bool,
        allowed_tool_ids: set[str],
    ) -> str:
        if not granted_by_authority:
            if self.registry is not None and self.registry.has_capability(capability, mission_type, approved_only=True):
                return "Capability is not granted by mission authority, although an approved manifest exists."
            if self.registry is not None and self.registry.has_capability(capability, mission_type, approved_only=False):
                return "Capability is not granted by mission authority and only has a candidate manifest."
            return "Capability is not present in the mission authority envelope."
        if self.registry is None:
            return "Capability is not present in the mission authority envelope."
        if self.registry.has_capability(capability, mission_type, approved_only=True, allowed_tool_ids=allowed_tool_ids):
            return "Capability is present and approved, but was not granted by mission authority."
        if self.registry.has_capability(capability, mission_type, approved_only=True):
            return "Capability has an approved manifest, but mission authority does not grant an approved tool."
        if self.registry.has_capability(capability, mission_type, approved_only=False):
            return "Capability has a candidate manifest, but is not approved for execution."
        return "Capability has no manifest in the registry."
