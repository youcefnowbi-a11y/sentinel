from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import Field, model_validator

from sentinel.agent.event_bus import EventBus
from sentinel.agent.events import AgentEventType
from sentinel.mission.models import MissionAuthorityEnvelope
from sentinel.shared.models import SentinelModel


def _stable_id(prefix: str, payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return f"{prefix}_{hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:16]}"


class ProcedurePrecondition(SentinelModel):
    id: str = ""
    name: str
    required: bool = True
    satisfied: bool = False
    evidence_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate(self) -> ProcedurePrecondition:
        if not self.id:
            self.id = _stable_id("pre", {"name": self.name, "required": self.required, "evidence_refs": self.evidence_refs})
        return self


class RequiredAuthority(SentinelModel):
    allowed_tools: list[str] = Field(default_factory=list)
    allowed_actions: list[str] = Field(default_factory=list)
    allowed_paths: list[str] = Field(default_factory=list)
    allowed_domains: list[str] = Field(default_factory=list)

    def missing_from(self, envelope: MissionAuthorityEnvelope) -> list[str]:
        missing = []
        missing.extend(f"tool:{tool}" for tool in self.allowed_tools if tool not in envelope.allowed_tools)
        missing.extend(f"action:{action}" for action in self.allowed_actions if action not in envelope.allowed_actions)
        missing.extend(f"path:{path}" for path in self.allowed_paths if path not in envelope.allowed_paths)
        missing.extend(f"domain:{domain}" for domain in self.allowed_domains if domain not in envelope.allowed_domains)
        return missing


class CanonicalStep(SentinelModel):
    id: str = ""
    order: int = Field(ge=1)
    action: str
    tool: str
    description: str
    evidence_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate(self) -> CanonicalStep:
        if not self.id:
            self.id = _stable_id("cstep", {"order": self.order, "action": self.action, "tool": self.tool, "evidence_refs": self.evidence_refs})
        return self


class SuccessProof(SentinelModel):
    id: str = ""
    name: str
    evidence_refs: list[str]

    @model_validator(mode="after")
    def _validate(self) -> SuccessProof:
        if not self.evidence_refs:
            raise ValueError("SuccessProof requires evidence refs.")
        if not self.id:
            self.id = _stable_id("sproof", {"name": self.name, "evidence_refs": self.evidence_refs})
        return self


class KnownFailureMode(SentinelModel):
    id: str = ""
    code: str
    mitigation: str
    evidence_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate(self) -> KnownFailureMode:
        if not self.id:
            self.id = _stable_id("kfail", {"code": self.code, "mitigation": self.mitigation, "evidence_refs": self.evidence_refs})
        return self


class SkillProcedure(SentinelModel):
    id: str = ""
    name: str
    objective_keywords: list[str] = Field(default_factory=list)
    capability_names: list[str] = Field(default_factory=list)
    preconditions: list[ProcedurePrecondition] = Field(default_factory=list)
    required_authority: RequiredAuthority = Field(default_factory=RequiredAuthority)
    canonical_steps: list[CanonicalStep] = Field(default_factory=list)
    success_proofs: list[SuccessProof] = Field(default_factory=list)
    known_failure_modes: list[KnownFailureMode] = Field(default_factory=list)
    stale: bool = False
    recommended_only: bool = True
    authority_expansion: bool = False

    @model_validator(mode="after")
    def _validate(self) -> SkillProcedure:
        if not self.id:
            self.id = _stable_id("skillproc", {"name": self.name, "objective_keywords": sorted(self.objective_keywords), "capability_names": sorted(self.capability_names)})
        return self


class SkillProcedureMatch(SentinelModel):
    id: str = ""
    mission_id: str
    procedure_id: str
    procedure_name: str
    score: float = Field(ge=0.0, le=1.0)
    matched_objective_terms: list[str] = Field(default_factory=list)
    matched_capabilities: list[str] = Field(default_factory=list)
    missing_authority: list[str] = Field(default_factory=list)
    blocked_execution_recommendation: bool = False
    stale_warning: bool = False
    preconditions: list[ProcedurePrecondition] = Field(default_factory=list)
    required_authority: RequiredAuthority = Field(default_factory=RequiredAuthority)
    canonical_steps: list[CanonicalStep] = Field(default_factory=list)
    success_proofs: list[SuccessProof] = Field(default_factory=list)
    known_failure_modes: list[KnownFailureMode] = Field(default_factory=list)
    recommended_only: bool = True
    authority_expansion: bool = False
    trace_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate(self) -> SkillProcedureMatch:
        if not self.id:
            self.id = _stable_id(
                "spmatch",
                {
                    "mission_id": self.mission_id,
                    "procedure_id": self.procedure_id,
                    "score": self.score,
                    "matched_objective_terms": self.matched_objective_terms,
                    "matched_capabilities": self.matched_capabilities,
                    "missing_authority": self.missing_authority,
                },
            )
        return self


class SkillProcedureGraph(SentinelModel):
    procedures: list[SkillProcedure] = Field(default_factory=list)
    advisory_only: bool = True
    authority_expansion: bool = False

    def match(
        self,
        envelope: MissionAuthorityEnvelope,
        *,
        objective: str,
        capability_names: list[str] | None = None,
        event_bus: EventBus | None = None,
    ) -> SkillProcedureMatch:
        if not self.procedures:
            raise ValueError("SkillProcedureGraph has no procedures.")
        objective_tokens = set(objective.lower().split())
        capabilities = set(capability_names or [])
        matches = [self._score(procedure, objective_tokens, capabilities) for procedure in self.procedures]
        procedure, score, matched_terms, matched_capabilities = max(matches, key=lambda item: item[1])
        missing_authority = procedure.required_authority.missing_from(envelope)
        match = SkillProcedureMatch(
            mission_id=envelope.id,
            procedure_id=procedure.id,
            procedure_name=procedure.name,
            score=score,
            matched_objective_terms=matched_terms,
            matched_capabilities=matched_capabilities,
            missing_authority=missing_authority,
            blocked_execution_recommendation=bool(missing_authority),
            stale_warning=procedure.stale,
            preconditions=procedure.preconditions,
            required_authority=procedure.required_authority,
            canonical_steps=sorted(procedure.canonical_steps, key=lambda step: step.order),
            success_proofs=procedure.success_proofs,
            known_failure_modes=procedure.known_failure_modes,
        )
        return self._record(match, event_bus)

    @staticmethod
    def _score(
        procedure: SkillProcedure,
        objective_tokens: set[str],
        capabilities: set[str],
    ) -> tuple[SkillProcedure, float, list[str], list[str]]:
        keyword_set = {keyword.lower() for keyword in procedure.objective_keywords}
        matched_terms = sorted(keyword for keyword in keyword_set if keyword in objective_tokens)
        matched_capabilities = sorted(capability for capability in procedure.capability_names if capability in capabilities)
        denominator = max(1, len(procedure.objective_keywords) + len(procedure.capability_names))
        score = round(min(1.0, (len(matched_terms) + len(matched_capabilities)) / denominator), 6)
        return procedure, score, matched_terms, matched_capabilities

    @staticmethod
    def _record(match: SkillProcedureMatch, event_bus: EventBus | None) -> SkillProcedureMatch:
        if event_bus is None:
            return match
        event = event_bus.append(
            AgentEventType.SKILL_PROCEDURE_MATCHED,
            "Skill procedure matched advisably without granting authority.",
            payload={
                "match_id": match.id,
                "procedure_id": match.procedure_id,
                "procedure_name": match.procedure_name,
                "score": match.score,
                "missing_authority": match.missing_authority,
                "blocked_execution_recommendation": match.blocked_execution_recommendation,
                "stale_warning": match.stale_warning,
                "recommended_only": True,
                "authority_expansion": False,
            },
        )
        return match.model_copy(update={"trace_refs": [event.id]})
