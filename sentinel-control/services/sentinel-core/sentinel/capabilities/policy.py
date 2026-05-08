from __future__ import annotations

from pathlib import PurePosixPath

from sentinel.capabilities.models import CapabilityManifest, CapabilityManifestStatus, CapabilityPolicyDecision, ToolInvocation
from sentinel.capabilities.risk import BLACK_ZONE_SIDE_EFFECTS, ToolAuthType, ToolExecutionStatus, ToolRiskClass, ToolSideEffect, risk_class_covers, risk_for_side_effects
from sentinel.mission.models import MissionAuthorityEnvelope


class CapabilityPolicy:
    def decide(
        self,
        manifest: CapabilityManifest | None,
        invocation: ToolInvocation,
        envelope: MissionAuthorityEnvelope,
    ) -> CapabilityPolicyDecision:
        if manifest is None:
            return CapabilityPolicyDecision(
                tool_id=invocation.tool_id,
                action=invocation.action,
                status=ToolExecutionStatus.BLOCKED,
                reason="tool_without_manifest",
                risk_class=risk_for_side_effects(invocation.requested_side_effects),
                policy_refs=["P1B_unknown_tools_blocked"],
            )

        requested_effects = set(invocation.requested_side_effects)
        if not requested_effects:
            return self._blocked(
                manifest,
                invocation,
                "requested_side_effects_missing",
                risk_for_side_effects(manifest.side_effects),
            )
        if ToolSideEffect.NONE in requested_effects and len(requested_effects) > 1:
            return self._blocked(
                manifest,
                invocation,
                "ambiguous_none_side_effect",
                risk_for_side_effects(list(requested_effects)),
            )
        declared_effects = set(manifest.side_effects)
        undeclared_effects = requested_effects - declared_effects
        if undeclared_effects:
            return self._blocked(
                manifest,
                invocation,
                "undeclared_side_effect",
                risk_for_side_effects(list(requested_effects)),
            )

        authorized_black_effects = self._authorized_browser_v3_black_zone_effects(invocation, envelope)
        non_authorized_requested_black = (requested_effects & BLACK_ZONE_SIDE_EFFECTS) - authorized_black_effects
        non_authorized_manifest_black = (set(manifest.side_effects) & BLACK_ZONE_SIDE_EFFECTS) - authorized_black_effects
        if non_authorized_requested_black or non_authorized_manifest_black:
            return self._blocked(
                manifest,
                invocation,
                "black_zone_side_effect",
                ToolRiskClass.CRITICAL_BLOCKED,
            )

        if manifest.auth_type == ToolAuthType.LEAKED_KEY:
            return self._blocked(manifest, invocation, "leaked_key_source", ToolRiskClass.CRITICAL_BLOCKED)

        if manifest.status == CapabilityManifestStatus.BLOCKED:
            return self._blocked(manifest, invocation, "manifest_blocked", manifest.risk_class)

        if manifest.status == CapabilityManifestStatus.DISABLED:
            return CapabilityPolicyDecision(
                tool_id=invocation.tool_id,
                action=invocation.action,
                status=ToolExecutionStatus.DISABLED,
                reason="manifest_disabled",
                risk_class=manifest.risk_class,
                manifest_status=manifest.status,
                policy_refs=[*manifest.policy_refs, "P1B_disabled_tools_do_not_execute"],
            )

        if invocation.action in manifest.forbidden_actions or invocation.action not in manifest.allowed_actions:
            return self._blocked(manifest, invocation, "action_not_allowed_by_manifest", manifest.risk_class)

        mission_type = envelope.mission_type.value if hasattr(envelope.mission_type, "value") else str(envelope.mission_type)
        if manifest.mission_scopes_allowed and mission_type not in manifest.mission_scopes_allowed:
            return self._blocked(manifest, invocation, "mission_scope_not_allowed", manifest.risk_class)

        if manifest.status == CapabilityManifestStatus.CANDIDATE:
            return CapabilityPolicyDecision(
                tool_id=invocation.tool_id,
                action=invocation.action,
                status=ToolExecutionStatus.CANDIDATE_ONLY,
                reason="candidate_tool_cannot_execute",
                risk_class=manifest.risk_class,
                manifest_status=manifest.status,
                policy_refs=[*manifest.policy_refs, "P1B_candidate_tools_are_catalog_only"],
            )

        if invocation.tool_id not in envelope.allowed_tools:
            return self._blocked(manifest, invocation, "tool_not_granted_by_mission_authority", manifest.risk_class)

        if invocation.action not in envelope.allowed_actions:
            return self._blocked(manifest, invocation, "action_not_granted_by_mission_authority", manifest.risk_class)

        if not self._filesystem_roots_are_scoped(manifest, envelope):
            return self._blocked(manifest, invocation, "filesystem_root_outside_mission_scope", ToolRiskClass.HOST_MUTATION)

        risk_effects = [effect for effect in manifest.side_effects if effect not in authorized_black_effects]
        actual_risk = risk_for_side_effects(risk_effects)
        if not risk_class_covers(manifest.risk_class, actual_risk):
            return self._blocked(manifest, invocation, "risk_class_understates_side_effects", actual_risk)

        return CapabilityPolicyDecision(
            tool_id=invocation.tool_id,
            action=invocation.action,
            status=ToolExecutionStatus.ALLOWED,
            allowed=True,
            reason="approved_tool_granted_by_mission_authority",
            risk_class=manifest.risk_class,
            manifest_status=manifest.status,
            policy_refs=[*manifest.policy_refs, "P1B_approved_tools_require_mission_authority"],
        )

    @staticmethod
    def _filesystem_roots_are_scoped(manifest: CapabilityManifest, envelope: MissionAuthorityEnvelope) -> bool:
        if ToolSideEffect.FILESYSTEM_WRITE not in manifest.side_effects and ToolSideEffect.LOCAL_DRAFT_WRITE not in manifest.side_effects:
            return True
        allowed_paths = set(envelope.allowed_paths)
        roots = set(manifest.filesystem_roots)
        if not roots or "*" in roots or "*" in allowed_paths:
            return False
        if any(CapabilityPolicy._has_path_escape(path) for path in roots | allowed_paths):
            return False
        return roots.issubset(allowed_paths)

    @staticmethod
    def _authorized_browser_v3_black_zone_effects(
        invocation: ToolInvocation,
        envelope: MissionAuthorityEnvelope,
    ) -> set[ToolSideEffect]:
        if invocation.action not in {"browser_form_submit", "browser_login_authority"}:
            return set()
        expected_class = {
            "browser_form_submit": "browser_form_submit",
            "browser_login_authority": "browser_login_authority",
        }.get(invocation.action)
        has_grant = any(
            str(grant.get("authority_class") or "") == expected_class
            for grant in envelope.browser_v3_authority_grants
            if isinstance(grant, dict)
        )
        if not has_grant:
            return set()
        if invocation.action == "browser_form_submit":
            return {ToolSideEffect.BROWSER_SUBMIT}
        if invocation.action == "browser_login_authority":
            return {ToolSideEffect.CREDENTIAL_ACCESS}
        return set()

    @staticmethod
    def _has_path_escape(path: str) -> bool:
        return not path or ".." in PurePosixPath(path.replace("\\", "/")).parts

    @staticmethod
    def _blocked(
        manifest: CapabilityManifest,
        invocation: ToolInvocation,
        reason: str,
        risk_class: ToolRiskClass,
    ) -> CapabilityPolicyDecision:
        return CapabilityPolicyDecision(
            tool_id=invocation.tool_id,
            action=invocation.action,
            status=ToolExecutionStatus.BLOCKED,
            reason=reason,
            risk_class=risk_class,
            manifest_status=manifest.status,
            policy_refs=[*manifest.policy_refs, "P1B_policy_block"],
        )
