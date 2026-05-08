from __future__ import annotations

from pathlib import Path

from sentinel.mission.models import MissionAction, MissionAuthorityEnvelope


BLACK_ZONE_ACTIONS = {
    "run_shell_command",
    "shell",
    "exec",
    "eval",
    "browser_submit_form",
    "browser_submit",
    "real_browser_submit",
    "desktop_control",
    "sidecar_runtime",
    "payment",
    "payment_send",
    "spend_money",
    "dependency_install",
    "install_dependency",
    "credential_access",
    "read_credentials",
    "use_api_key",
    "network_mutation",
    "network_write",
    "send_email",
    "email_send",
    "external_channel_send",
    "production_mutation",
    "modify_code",
}


PATH_SCOPED_LOCAL_ACTIONS = {
    "create_project_folder",
    "create_markdown_file",
    "export_json",
    "generate_gtm_pack",
    "generate_landing_copy",
    "generate_outreach_drafts_without_sending",
    "create_watchlist",
    "generate_research_questions",
    "write_trace",
}


class MissionScopeChecker:
    def __init__(self, project_root: str | Path | None = None) -> None:
        self.project_root = Path(project_root or Path.cwd()).resolve()

    def is_black_zone(self, action: MissionAction) -> bool:
        return action.action_type.lower() in BLACK_ZONE_ACTIONS or action.tool.lower() in BLACK_ZONE_ACTIONS

    def is_forbidden(self, envelope: MissionAuthorityEnvelope, action: MissionAction) -> bool:
        forbidden = {item.lower() for item in envelope.forbidden_actions}
        return action.action_type.lower() in forbidden or action.tool.lower() in forbidden or self.is_black_zone(action)

    def is_in_scope(self, envelope: MissionAuthorityEnvelope, action: MissionAction) -> bool:
        if action.action_type not in envelope.allowed_actions:
            return False
        if action.tool not in envelope.allowed_tools:
            return False
        return self.is_path_in_scope(envelope, action)

    def is_path_in_scope(self, envelope: MissionAuthorityEnvelope, action: MissionAction) -> bool:
        raw = self._path_from(action)
        if raw is None:
            return action.action_type not in PATH_SCOPED_LOCAL_ACTIONS

        candidate = Path(raw)
        if not candidate.is_absolute():
            candidate = self.project_root / candidate
        candidate = candidate.resolve()

        for allowed in envelope.allowed_paths:
            allowed_path = Path(allowed)
            if not allowed_path.is_absolute():
                allowed_path = self.project_root / allowed_path
            allowed_path = allowed_path.resolve()
            if candidate == allowed_path or allowed_path in candidate.parents:
                return True
        return False

    @staticmethod
    def _path_from(action: MissionAction) -> str | None:
        for key in ("path", "file_path", "folder_path", "output_path"):
            value = action.input.get(key)
            if value:
                return str(value)
        return action.target
