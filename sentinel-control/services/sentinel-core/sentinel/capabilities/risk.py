from __future__ import annotations

from enum import StrEnum


class ToolRiskClass(StrEnum):
    STATIC_REFERENCE = "static_reference"
    READ_ONLY_PUBLIC = "read_only_public"
    READ_ONLY_AUTH = "read_only_auth"
    PRIVATE_DATA_READ = "private_data_read"
    DRAFT_ONLY_WRITE = "draft_only_write"
    EXTERNAL_MUTATION = "external_mutation"
    HOST_MUTATION = "host_mutation"
    CRITICAL_BLOCKED = "critical_blocked"


class ToolAuthType(StrEnum):
    NONE = "none"
    API_KEY = "api_key"
    OAUTH = "oauth"
    USER_PROVIDED = "user_provided"
    SANDBOX = "sandbox"
    UNKNOWN = "unknown"
    LEAKED_KEY = "leaked_key"


class ToolSideEffect(StrEnum):
    NONE = "none"
    NETWORK_READ = "network_read"
    NETWORK_WRITE = "network_write"
    FILESYSTEM_READ = "filesystem_read"
    FILESYSTEM_WRITE = "filesystem_write"
    LOCAL_DRAFT_WRITE = "local_draft_write"
    EXTERNAL_SEND = "external_send"
    BROWSER_READ = "browser_read"
    BROWSER_SUBMIT = "browser_submit"
    SHELL_EXECUTION = "shell_execution"
    DESKTOP_CONTROL = "desktop_control"
    PAYMENT = "payment"
    CREDENTIAL_ACCESS = "credential_access"
    SECRET_READ = "secret_read"
    MEDIA_GENERATION = "media_generation"


class ToolExecutionStatus(StrEnum):
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    CANDIDATE_ONLY = "candidate_only"
    DISABLED = "disabled"
    ESCALATE = "escalate"


RISK_CLASS_RANK = {
    ToolRiskClass.STATIC_REFERENCE: 0,
    ToolRiskClass.READ_ONLY_PUBLIC: 1,
    ToolRiskClass.READ_ONLY_AUTH: 2,
    ToolRiskClass.PRIVATE_DATA_READ: 3,
    ToolRiskClass.DRAFT_ONLY_WRITE: 4,
    ToolRiskClass.EXTERNAL_MUTATION: 5,
    ToolRiskClass.HOST_MUTATION: 6,
    ToolRiskClass.CRITICAL_BLOCKED: 7,
}


BLACK_ZONE_SIDE_EFFECTS = frozenset(
    {
        ToolSideEffect.EXTERNAL_SEND,
        ToolSideEffect.BROWSER_SUBMIT,
        ToolSideEffect.SHELL_EXECUTION,
        ToolSideEffect.DESKTOP_CONTROL,
        ToolSideEffect.PAYMENT,
        ToolSideEffect.CREDENTIAL_ACCESS,
        ToolSideEffect.SECRET_READ,
    }
)


def risk_for_side_effects(side_effects: list[ToolSideEffect]) -> ToolRiskClass:
    effects = set(side_effects)
    if effects & BLACK_ZONE_SIDE_EFFECTS:
        return ToolRiskClass.CRITICAL_BLOCKED
    if ToolSideEffect.NETWORK_WRITE in effects:
        return ToolRiskClass.EXTERNAL_MUTATION
    if ToolSideEffect.FILESYSTEM_WRITE in effects and ToolSideEffect.LOCAL_DRAFT_WRITE in effects:
        return ToolRiskClass.DRAFT_ONLY_WRITE
    if ToolSideEffect.FILESYSTEM_WRITE in effects:
        return ToolRiskClass.HOST_MUTATION
    if ToolSideEffect.LOCAL_DRAFT_WRITE in effects:
        return ToolRiskClass.DRAFT_ONLY_WRITE
    if ToolSideEffect.NETWORK_READ in effects or ToolSideEffect.BROWSER_READ in effects:
        return ToolRiskClass.READ_ONLY_PUBLIC
    return ToolRiskClass.STATIC_REFERENCE


def risk_class_covers(declared: ToolRiskClass, actual: ToolRiskClass) -> bool:
    return RISK_CLASS_RANK[declared] >= RISK_CLASS_RANK[actual]
