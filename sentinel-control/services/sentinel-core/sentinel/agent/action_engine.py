from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from typing import Protocol
from urllib.parse import urlparse

from pydantic import Field

from sentinel.agent.browser.models import (
    BrowserControlledCapabilityResult,
    BrowserControlledCapabilityStatus,
    BrowserInteractionExecutionReceipt,
    BrowserRenderedSnapshotResult,
)
from sentinel.agent.browser.verifier import BrowserPostActionVerifier, BrowserVerificationResult
from sentinel.agent.event_bus import EventBus
from sentinel.agent.perception import PerceptionFrame, PerceptionSourceType, PerceptionTarget
from sentinel.agent.tool_call_protocol import CanonicalToolCall
from sentinel.mission.models import MissionAuthorityEnvelope
from sentinel.shared.models import SentinelModel, new_id


class CompiledMissionDecision(StrEnum):
    GRANTED = "granted"
    OUT_OF_SCOPE = "out_of_scope"
    HIGHER_AUTHORITY = "higher_authority"
    INVALID = "invalid"


class ActionEngineStatus(StrEnum):
    PREPARED = "prepared"
    EXECUTED = "executed"
    REJECTED = "rejected"
    NEEDS_REPAIR = "needs_repair"


class CompiledMissionPolicy(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("cmp"))
    mission_id: str
    source_envelope_hash: str
    policy_hash: str
    allowed_action_classes: list[str] = Field(default_factory=list)
    allowed_tools: list[str] = Field(default_factory=list)
    allowed_domains: list[str] = Field(default_factory=list)
    allowed_paths: list[str] = Field(default_factory=list)
    allowed_backend_kinds: list[str] = Field(default_factory=lambda: ["browser"])
    impact_budget: float = Field(default=0.0, ge=0.0, le=100.0)
    action_budget: int = Field(default=1, ge=1)
    max_steps: int = Field(default=1, ge=1)
    max_repair_attempts: int = Field(default=2, ge=0)
    max_wall_clock_ms: int = Field(default=60_000, ge=1)
    confirmation_boundaries: list[str] = Field(default_factory=list)
    forbidden_zones: list[str] = Field(default_factory=list)
    required_receipt_types: list[str] = Field(default_factory=list)
    required_verifier_types: list[str] = Field(default_factory=list)
    credentialed_state_rules: list[str] = Field(default_factory=list)
    externality_rules: list[str] = Field(default_factory=list)
    trace_refs: list[str] = Field(default_factory=list)


class CompiledMissionPolicyCompiler:
    """Compiles mission authority into a fast lookup policy without expanding it."""

    def compile(self, envelope: MissionAuthorityEnvelope, *, trace_refs: list[str] | None = None) -> CompiledMissionPolicy:
        source_hash = _hash_payload(envelope.model_dump(mode="json"))
        allowed_action_classes = sorted(set(envelope.allowed_actions))
        allowed_backend_kinds = ["browser"] if any(action.startswith("browser_") for action in allowed_action_classes) else []
        policy_payload = {
            "mission_id": envelope.id,
            "source_envelope_hash": source_hash,
            "allowed_action_classes": allowed_action_classes,
            "allowed_tools": sorted(set(envelope.allowed_tools)),
            "allowed_domains": sorted(set(envelope.allowed_domains)),
            "allowed_paths": sorted(set(envelope.allowed_paths)),
            "allowed_backend_kinds": allowed_backend_kinds,
            "impact_budget": envelope.risk_appetite_score,
            "action_budget": envelope.max_actions,
            "max_steps": envelope.max_actions,
            "max_repair_attempts": 2,
            "max_wall_clock_ms": envelope.max_duration_minutes * 60_000,
            "confirmation_boundaries": sorted(set(envelope.escalation_triggers)),
            "forbidden_zones": sorted(set(envelope.forbidden_actions)),
            "required_receipt_types": self._required_receipts(envelope.allowed_actions),
            "required_verifier_types": self._required_verifiers(envelope.allowed_actions),
            "credentialed_state_rules": self._credentialed_rules(envelope),
            "externality_rules": self._externality_rules(envelope.allowed_actions),
            "trace_refs": list(trace_refs or []),
        }
        return CompiledMissionPolicy(**policy_payload, policy_hash=_hash_payload(policy_payload))

    @staticmethod
    def _required_receipts(actions: list[str]) -> list[str]:
        receipts = []
        for action in actions:
            if action.startswith("browser_"):
                receipts.append("browser_receipt")
            if action in {"browser_interaction_limited", "browser_form_submit", "browser_login_authority"}:
                receipts.append("browser_interaction_receipt")
        return sorted(set(receipts))

    @staticmethod
    def _required_verifiers(actions: list[str]) -> list[str]:
        if any(action.startswith("browser_") for action in actions):
            return ["browser_post_action_verifier"]
        return []

    @staticmethod
    def _credentialed_rules(envelope: MissionAuthorityEnvelope) -> list[str]:
        if not envelope.allowed_accounts:
            return ["no_credentialed_state"]
        return ["account_id_only", "no_raw_credentials_in_context_or_trace"]

    @staticmethod
    def _externality_rules(actions: list[str]) -> list[str]:
        rules = ["verify_after_impact"]
        if any(action in {"browser_form_submit", "browser_upload_authorized"} for action in actions):
            rules.append("external_write_requires_receipt")
        return sorted(set(rules))


class SceneActionCandidate(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("sact"))
    mission_id: str
    perception_frame_id: str
    source_type: PerceptionSourceType
    target_id: str
    runtime_ref_id: str | None = None
    action_class: str
    tool_id: str
    intent: str
    expected_effect: str
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    required_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    planned_step_count: int = Field(default=1, ge=1)
    actions_already_used: int = Field(default=0, ge=0)
    repair_attempt_count: int = Field(default=0, ge=0)
    arguments: dict[str, object] = Field(default_factory=dict)
    evidence_refs: list[str] = Field(default_factory=list)


class PerceptionActionLink(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("palink"))
    mission_id: str
    perception_frame_id: str
    target_id: str
    runtime_ref_id: str
    action_class: str
    visible: bool
    understood: bool
    actionable: bool
    authorized: bool
    decision: CompiledMissionDecision
    reasons: list[str] = Field(default_factory=list)


class VisualActuationPlan(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("vap"))
    mission_id: str
    candidate_id: str
    action_class: str
    runtime_ref_id: str
    expected_effect: str
    verifier_type: str = "browser_post_action_verifier"
    steps: list[str] = Field(default_factory=list)


class ActionEnvelope(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("aenv"))
    mission_id: str
    compiled_policy_id: str
    compiled_policy_hash: str
    candidate_id: str
    perception_frame_id: str
    target_id: str
    runtime_ref_id: str
    source_type: PerceptionSourceType
    tool_id: str
    action_class: str
    expected_effect: str
    canonical_call: CanonicalToolCall
    call_hash: str
    required_receipt_types: list[str] = Field(default_factory=list)
    required_verifier_types: list[str] = Field(default_factory=list)
    visual_actuation_plan: VisualActuationPlan
    trace_refs: list[str] = Field(default_factory=list)


class ActionPreparationResult(SentinelModel):
    accepted: bool
    status: ActionEngineStatus
    decision: CompiledMissionDecision
    reason: str
    envelope: ActionEnvelope | None = None
    link: PerceptionActionLink | None = None
    errors: list[str] = Field(default_factory=list)


class ActionExecutionResult(SentinelModel):
    accepted: bool
    status: ActionEngineStatus
    reason: str
    envelope_id: str
    controlled_result: BrowserControlledCapabilityResult | None = None
    verifier_result: BrowserVerificationResult | None = None
    errors: list[str] = Field(default_factory=list)


class BrowserRunnerProtocol(Protocol):
    def run(
        self,
        call: CanonicalToolCall,
        envelope: MissionAuthorityEnvelope,
        *,
        event_bus: EventBus,
    ) -> BrowserControlledCapabilityResult:
        ...


class ActionEngine:
    """Prepares and dispatches action envelopes through governed runners."""

    def prepare_browser_action(
        self,
        *,
        frame: PerceptionFrame,
        candidate: SceneActionCandidate,
        policy: CompiledMissionPolicy,
        canonical_call: CanonicalToolCall,
    ) -> ActionPreparationResult:
        errors: list[str] = []
        if frame.mission_id != candidate.mission_id or policy.mission_id != candidate.mission_id:
            errors.append("mission_mismatch")
        if frame.source_type != PerceptionSourceType.BROWSER or candidate.source_type != PerceptionSourceType.BROWSER:
            errors.append("backend_not_active")
        if "browser" not in policy.allowed_backend_kinds:
            errors.append("browser_backend_not_granted")
        if candidate.actions_already_used >= policy.action_budget:
            errors.append("action_budget_exceeded")
        if candidate.planned_step_count > policy.max_steps:
            errors.append("max_steps_exceeded")
        if candidate.repair_attempt_count >= policy.max_repair_attempts:
            errors.append("repair_budget_exceeded")
        if candidate.required_confidence and candidate.confidence_score < candidate.required_confidence:
            errors.append("candidate_confidence_below_threshold")
        target = frame.target_by_id(candidate.target_id)
        if target is None:
            errors.append("perception_target_not_found")
        else:
            errors.extend(self._target_errors(candidate, target))
        if candidate.action_class not in policy.allowed_action_classes:
            errors.append("action_class_out_of_scope")
        if candidate.action_class in policy.forbidden_zones:
            errors.append("action_class_forbidden")
        if candidate.tool_id not in policy.allowed_tools:
            errors.append("tool_out_of_scope")
        if canonical_call.action != candidate.action_class:
            errors.append("canonical_call_action_mismatch")
        if canonical_call.tool_id != candidate.tool_id:
            errors.append("canonical_call_tool_mismatch")
        if canonical_call.arguments.get("ref_id") and canonical_call.arguments.get("ref_id") != candidate.runtime_ref_id:
            errors.append("canonical_call_ref_mismatch")
        if not self._target_domain_allowed(canonical_call.target, policy.allowed_domains):
            errors.append("target_domain_out_of_scope")

        decision = self._decision(errors)
        link = PerceptionActionLink(
            mission_id=candidate.mission_id,
            perception_frame_id=frame.id,
            target_id=candidate.target_id,
            runtime_ref_id=candidate.runtime_ref_id or "",
            action_class=candidate.action_class,
            visible=bool(target.visible) if target is not None else False,
            understood=bool(target.understood) if target is not None else False,
            actionable=bool(target.actionable) if target is not None else False,
            authorized=decision == CompiledMissionDecision.GRANTED,
            decision=decision,
            reasons=list(errors) or ["compiled_policy_granted"],
        )
        if errors:
            return ActionPreparationResult(
                accepted=False,
                status=ActionEngineStatus.REJECTED,
                decision=decision,
                reason=errors[0],
                link=link,
                errors=errors,
            )

        runtime_ref_id = candidate.runtime_ref_id or ""
        plan = VisualActuationPlan(
            mission_id=candidate.mission_id,
            candidate_id=candidate.id,
            action_class=candidate.action_class,
            runtime_ref_id=runtime_ref_id,
            expected_effect=candidate.expected_effect,
            steps=[
                "bind_runtime_ref",
                "dispatch_existing_browser_runner",
                "verify_post_action_evidence",
            ],
        )
        action_envelope = ActionEnvelope(
            mission_id=candidate.mission_id,
            compiled_policy_id=policy.id,
            compiled_policy_hash=policy.policy_hash,
            candidate_id=candidate.id,
            perception_frame_id=frame.id,
            target_id=candidate.target_id,
            runtime_ref_id=runtime_ref_id,
            source_type=PerceptionSourceType.BROWSER,
            tool_id=candidate.tool_id,
            action_class=candidate.action_class,
            expected_effect=candidate.expected_effect,
            canonical_call=canonical_call,
            call_hash=canonical_call.canonical_hash,
            required_receipt_types=list(policy.required_receipt_types),
            required_verifier_types=list(policy.required_verifier_types),
            visual_actuation_plan=plan,
            trace_refs=list(frame.trace_refs),
        )
        return ActionPreparationResult(
            accepted=True,
            status=ActionEngineStatus.PREPARED,
            decision=CompiledMissionDecision.GRANTED,
            reason="compiled_policy_granted",
            envelope=action_envelope,
            link=link,
        )

    def execute_browser_action(
        self,
        *,
        action_envelope: ActionEnvelope,
        mission_envelope: MissionAuthorityEnvelope,
        runner: BrowserRunnerProtocol,
        event_bus: EventBus,
    ) -> ActionExecutionResult:
        if action_envelope.source_type != PerceptionSourceType.BROWSER:
            return ActionExecutionResult(
                accepted=False,
                status=ActionEngineStatus.REJECTED,
                reason="backend_not_active",
                envelope_id=action_envelope.id,
                errors=["backend_not_active"],
            )
        result = runner.run(action_envelope.canonical_call, mission_envelope, event_bus=event_bus)
        if not result.accepted:
            return ActionExecutionResult(
                accepted=False,
                status=ActionEngineStatus.REJECTED,
                reason=result.reason,
                envelope_id=action_envelope.id,
                controlled_result=result,
                errors=list(result.errors),
            )
        return ActionExecutionResult(
            accepted=True,
            status=ActionEngineStatus.EXECUTED,
            reason="existing_browser_runner_executed",
            envelope_id=action_envelope.id,
            controlled_result=result,
        )

    def verify_browser_post_action(
        self,
        *,
        mission_id: str,
        receipt: BrowserInteractionExecutionReceipt,
        after_snapshot: BrowserRenderedSnapshotResult,
        event_bus: EventBus,
        expected_text: str | None = None,
        expected_url: str | None = None,
    ) -> BrowserVerificationResult:
        return BrowserPostActionVerifier().verify(
            mission_id=mission_id,
            receipt=receipt,
            after_snapshot=after_snapshot,
            expected_text=expected_text,
            expected_url=expected_url,
            event_bus=event_bus,
        )

    @staticmethod
    def _target_errors(candidate: SceneActionCandidate, target: PerceptionTarget) -> list[str]:
        errors: list[str] = []
        if not target.visible:
            errors.append("target_not_visible")
        if not target.understood:
            errors.append("target_not_understood")
        if not target.actionable:
            errors.append("target_not_actionable")
        if not target.runtime_ref_id:
            errors.append("target_runtime_ref_missing")
        if candidate.runtime_ref_id and candidate.runtime_ref_id != target.runtime_ref_id:
            errors.append("candidate_ref_mismatch")
        if candidate.action_class not in target.action_classes:
            errors.append("target_action_class_not_supported")
        return errors

    @staticmethod
    def _target_domain_allowed(target_url: str | None, allowed_domains: list[str]) -> bool:
        if not target_url or not allowed_domains:
            return True
        host = (urlparse(target_url).hostname or "").lower()
        return any(host == domain.lower() or host.endswith(f".{domain.lower()}") for domain in allowed_domains)

    @staticmethod
    def _decision(errors: list[str]) -> CompiledMissionDecision:
        if not errors:
            return CompiledMissionDecision.GRANTED
        if any(error.endswith("_out_of_scope") or error == "action_class_forbidden" for error in errors):
            return CompiledMissionDecision.OUT_OF_SCOPE
        if any(error in {"action_budget_exceeded", "max_steps_exceeded", "repair_budget_exceeded"} for error in errors):
            return CompiledMissionDecision.OUT_OF_SCOPE
        if any(error.startswith("target_") or error.endswith("_mismatch") for error in errors):
            return CompiledMissionDecision.INVALID
        if "candidate_confidence_below_threshold" in errors:
            return CompiledMissionDecision.INVALID
        return CompiledMissionDecision.HIGHER_AUTHORITY


def _hash_payload(payload: dict[str, object]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
