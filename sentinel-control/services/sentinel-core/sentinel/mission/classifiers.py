from __future__ import annotations

from sentinel.shared.enums import ConfidenceLevel, ExternalityLevel, ReversibilityLevel, SensitivityLevel


class ReversibilityClassifier:
    def classify(self, action_type: str, payload: dict | None = None) -> ReversibilityLevel:
        action = action_type.lower()
        if action in {"read_file", "research", "generate_research_questions"}:
            return ReversibilityLevel.READ_ONLY
        if "draft" in action or action in {"generate_outreach_drafts_without_sending", "prepare_email_draft"}:
            return ReversibilityLevel.DRAFT
        if action in {
            "create_project_folder",
            "create_markdown_file",
            "export_json",
            "generate_gtm_pack",
            "generate_landing_copy",
            "create_watchlist",
            "write_trace",
        }:
            return ReversibilityLevel.LOCAL_WRITE_REVERSIBLE
        if action in {"update_crm_record", "update_watchlist"}:
            return ReversibilityLevel.STATE_MUTATING_RECOVERABLE
        return ReversibilityLevel.IRREVERSIBLE


class ExternalityClassifier:
    def classify(self, action_type: str, payload: dict | None = None) -> ExternalityLevel:
        action = action_type.lower()
        if action in {
            "create_project_folder",
            "create_markdown_file",
            "export_json",
            "generate_gtm_pack",
            "generate_landing_copy",
            "generate_outreach_drafts_without_sending",
            "create_watchlist",
            "generate_research_questions",
            "write_trace",
        }:
            return ExternalityLevel.INTERNAL_LOCAL
        if action in {"cueidea_import", "read_public_web"}:
            return ExternalityLevel.INTERNAL_CONNECTED_SYSTEM
        if action in {"send_email", "external_channel_send"}:
            return ExternalityLevel.EXTERNAL_PRIVATE
        if action in {"publish_content", "browser_submit_form"}:
            return ExternalityLevel.EXTERNAL_PUBLIC
        return ExternalityLevel.EXTERNAL_PRIVATE


class SensitivityClassifier:
    def classify(self, action_type: str, payload: dict | None = None) -> SensitivityLevel:
        action = action_type.lower()
        text = str(payload or {}).lower()
        if action in {"credential_access", "use_api_key"} or any(token in text for token in ("api_key", "password", "token", "secret")):
            return SensitivityLevel.SECRET
        if action in {"payment", "spend_money"}:
            return SensitivityLevel.FINANCIAL
        if action in {"identity_access", "desktop_control"}:
            return SensitivityLevel.IDENTITY
        if action in {"send_email", "external_channel_send"}:
            return SensitivityLevel.PERSONAL
        if action in {"generate_research_questions", "generate_gtm_pack", "create_markdown_file"}:
            return SensitivityLevel.INTERNAL
        return SensitivityLevel.INTERNAL


class ConfidenceClassifier:
    def classify(self, action_type: str, payload: dict | None = None) -> ConfidenceLevel:
        payload = payload or {}
        confidence = payload.get("confidence")
        if isinstance(confidence, (int, float)):
            if confidence >= 0.75:
                return ConfidenceLevel.HIGH
            if confidence >= 0.5:
                return ConfidenceLevel.MEDIUM
            return ConfidenceLevel.LOW
        if action_type in {"unknown", "external_channel_send", "browser_submit_form"}:
            return ConfidenceLevel.UNKNOWN
        return ConfidenceLevel.HIGH
