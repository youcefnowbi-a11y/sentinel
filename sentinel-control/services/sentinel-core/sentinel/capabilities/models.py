from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import Field, model_validator

from sentinel.capabilities.risk import ToolAuthType, ToolExecutionStatus, ToolRiskClass, ToolSideEffect
from sentinel.shared.models import SentinelModel


def utc_now() -> datetime:
    return datetime.now(UTC)


class CapabilityManifestStatus(StrEnum):
    CANDIDATE = "candidate"
    APPROVED = "approved"
    DISABLED = "disabled"
    BLOCKED = "blocked"


class CapabilityManifest(SentinelModel):
    id: str
    name: str
    version: str = "0.1"
    category: str
    provider: str
    description: str
    capabilities: list[str] = Field(default_factory=list)
    auth_type: ToolAuthType = ToolAuthType.NONE
    required_credentials: list[str] = Field(default_factory=list)
    allowed_actions: list[str] = Field(default_factory=list)
    forbidden_actions: list[str] = Field(default_factory=list)
    side_effects: list[ToolSideEffect] = Field(default_factory=list)
    data_access: list[str] = Field(default_factory=list)
    network_domains: list[str] = Field(default_factory=list)
    filesystem_roots: list[str] = Field(default_factory=list)
    externality: str = "internal_local"
    reversibility: str = "read_only"
    sensitivity: str = "public"
    risk_class: ToolRiskClass = ToolRiskClass.STATIC_REFERENCE
    cost_model: str = "none"
    rate_limit: str = "none"
    mission_scopes_allowed: list[str] = Field(default_factory=list)
    trace_events: list[str] = Field(default_factory=list)
    policy_refs: list[str] = Field(default_factory=list)
    eval_refs: list[str] = Field(default_factory=list)
    status: CapabilityManifestStatus = CapabilityManifestStatus.CANDIDATE
    created_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def side_effects_must_be_explicit(self) -> "CapabilityManifest":
        if not self.side_effects:
            raise ValueError("CapabilityManifest.side_effects must be explicit, even for static/no-op tools.")
        if ToolSideEffect.NONE in self.side_effects and len(set(self.side_effects)) > 1:
            raise ValueError("CapabilityManifest.side_effects cannot mix `none` with real side effects.")
        return self


class ToolInvocation(SentinelModel):
    tool_id: str
    action: str
    requested_side_effects: list[ToolSideEffect] = Field(default_factory=list)
    capability: str | None = None
    target: str | None = None


class CapabilityPolicyDecision(SentinelModel):
    tool_id: str
    action: str
    status: ToolExecutionStatus
    allowed: bool = False
    reason: str
    risk_class: ToolRiskClass = ToolRiskClass.STATIC_REFERENCE
    manifest_status: CapabilityManifestStatus | None = None
    policy_refs: list[str] = Field(default_factory=list)
    trace_event_id: str | None = None
