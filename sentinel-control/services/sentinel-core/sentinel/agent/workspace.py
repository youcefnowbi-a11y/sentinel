from __future__ import annotations

import hashlib
import json
from typing import Any
from typing import TypeVar

from pydantic import Field, model_validator

from sentinel.agent.event_bus import EventBus
from sentinel.agent.events import AgentEventType
from sentinel.mission.models import MissionAuthorityEnvelope
from sentinel.shared.models import SentinelModel


T = TypeVar("T", bound=SentinelModel)


def _normalize_text(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _stable_id(prefix: str, payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return f"{prefix}_{hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:16]}"


def _dedupe_by_id(items: list[T]) -> list[T]:
    seen: set[str] = set()
    result: list[T] = []
    for item in items:
        item_id = str(getattr(item, "id"))
        if item_id not in seen:
            seen.add(item_id)
            result.append(item)
    return result


class WorkspaceFact(SentinelModel):
    id: str = ""
    text: str
    evidence_refs: list[str]
    tags: list[str] = Field(default_factory=list)
    source: str = "workspace_delta"
    trace_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate(self) -> WorkspaceFact:
        if not self.evidence_refs:
            raise ValueError("WorkspaceFact requires at least one evidence ref.")
        if "unverified" in _normalize_text(self.source) or any("unverified" in _normalize_text(tag) for tag in self.tags):
            raise ValueError("Unverified workspace claims cannot be accepted as facts.")
        if not self.id:
            self.id = _stable_id("wfact", {"text": _normalize_text(self.text), "evidence_refs": self.evidence_refs})
        return self

    @property
    def normalized_text(self) -> str:
        return _normalize_text(self.text)


class WorkspaceClaim(SentinelModel):
    id: str = ""
    text: str
    evidence_refs: list[str] = Field(default_factory=list)
    status: str = "candidate"
    trace_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate(self) -> WorkspaceClaim:
        if not self.id:
            self.id = _stable_id("wclaim", {"text": _normalize_text(self.text), "status": self.status, "evidence_refs": self.evidence_refs})
        return self

    @property
    def normalized_text(self) -> str:
        return _normalize_text(self.text)


class WorkspaceSignal(SentinelModel):
    id: str = ""
    signal_type: str
    summary: str
    value: dict[str, Any] = Field(default_factory=dict)
    evidence_refs: list[str] = Field(default_factory=list)
    observation_only: bool = True
    authority_expansion: bool = False
    spend_runtime: bool = False
    trace_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate(self) -> WorkspaceSignal:
        dynamic_spend_signal_types = {"dynamic_spend", "budget_reallocation", "spend_policy", "transaction_limit_change"}
        if self.signal_type in dynamic_spend_signal_types and not self.evidence_refs:
            raise ValueError("Dynamic spend signals require signal evidence refs.")
        if not self.id:
            self.id = _stable_id(
                "wsig",
                {
                    "signal_type": self.signal_type,
                    "summary": _normalize_text(self.summary),
                    "value": self.value,
                    "evidence_refs": self.evidence_refs,
                },
            )
        return self


class WorkspaceAgentOutput(SentinelModel):
    id: str = ""
    role: str
    summary: str
    claims: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    execution_seen: bool = False
    agent_spawning: bool = False
    runtime_multi_agent_execution: bool = False
    authority_expansion: bool = False
    trace_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate(self) -> WorkspaceAgentOutput:
        if not self.id:
            self.id = _stable_id(
                "wout",
                {
                    "role": self.role,
                    "summary": _normalize_text(self.summary),
                    "claims": sorted(_normalize_text(claim) for claim in self.claims),
                    "evidence_refs": self.evidence_refs,
                },
            )
        return self


class WorkspaceOpenQuestion(SentinelModel):
    id: str = ""
    question: str
    role_relevance: list[str] = Field(default_factory=list)
    trace_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate(self) -> WorkspaceOpenQuestion:
        if not self.id:
            self.id = _stable_id(
                "wq",
                {"question": _normalize_text(self.question), "role_relevance": sorted(self.role_relevance)},
            )
        return self

    @property
    def normalized_text(self) -> str:
        return _normalize_text(self.question)


class WorkspaceRejectedClaim(SentinelModel):
    id: str = ""
    text: str
    reason: str
    evidence_refs: list[str] = Field(default_factory=list)
    normalized_text: str = ""
    trace_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate(self) -> WorkspaceRejectedClaim:
        if not self.normalized_text:
            self.normalized_text = _normalize_text(self.text)
        if not self.id:
            self.id = _stable_id("wrej", {"text": self.normalized_text, "reason": self.reason, "evidence_refs": self.evidence_refs})
        return self


class WorkspaceSnapshot(SentinelModel):
    id: str = ""
    mission_id: str
    version: int = Field(ge=0)
    mission_title: str
    mission_objective: str
    authority_summary: dict[str, Any] = Field(default_factory=dict)
    accepted_facts: list[WorkspaceFact] = Field(default_factory=list)
    claims: list[WorkspaceClaim] = Field(default_factory=list)
    open_questions: list[WorkspaceOpenQuestion] = Field(default_factory=list)
    rejected_claims: list[WorkspaceRejectedClaim] = Field(default_factory=list)
    signals: list[WorkspaceSignal] = Field(default_factory=list)
    agent_outputs: list[WorkspaceAgentOutput] = Field(default_factory=list)
    authority_expansion: bool = False
    trace_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate(self) -> WorkspaceSnapshot:
        if not self.id:
            self.id = _stable_id(
                "wsnap",
                {
                    "mission_id": self.mission_id,
                    "version": self.version,
                    "accepted_facts": [fact.id for fact in self.accepted_facts],
                    "claims": [claim.id for claim in self.claims],
                    "open_questions": [question.id for question in self.open_questions],
                    "rejected_claims": [claim.id for claim in self.rejected_claims],
                    "signals": [signal.id for signal in self.signals],
                    "agent_outputs": [output.id for output in self.agent_outputs],
                },
            )
        return self


class WorkspaceDelta(SentinelModel):
    id: str = ""
    mission_id: str
    base_version: int = Field(ge=0)
    accepted_facts: list[WorkspaceFact] = Field(default_factory=list)
    claims: list[WorkspaceClaim] = Field(default_factory=list)
    open_questions: list[WorkspaceOpenQuestion] = Field(default_factory=list)
    rejected_claims: list[WorkspaceRejectedClaim] = Field(default_factory=list)
    signals: list[WorkspaceSignal] = Field(default_factory=list)
    agent_outputs: list[WorkspaceAgentOutput] = Field(default_factory=list)
    trace_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate(self) -> WorkspaceDelta:
        if not self.id:
            self.id = _stable_id(
                "wdelta",
                {
                    "mission_id": self.mission_id,
                    "base_version": self.base_version,
                    "accepted_facts": [fact.id for fact in self.accepted_facts],
                    "claims": [claim.id for claim in self.claims],
                    "open_questions": [question.id for question in self.open_questions],
                    "rejected_claims": [claim.id for claim in self.rejected_claims],
                    "signals": [signal.id for signal in self.signals],
                    "agent_outputs": [output.id for output in self.agent_outputs],
                },
            )
        return self


class BroadcastSlice(SentinelModel):
    id: str = ""
    mission_id: str
    workspace_version: int = Field(ge=0)
    role: str
    purpose: list[str] = Field(default_factory=list)
    authority_summary: dict[str, Any] = Field(default_factory=dict)
    accepted_facts: list[WorkspaceFact] = Field(default_factory=list)
    open_questions: list[WorkspaceOpenQuestion] = Field(default_factory=list)
    rejected_claims: list[WorkspaceRejectedClaim] = Field(default_factory=list)
    signals: list[WorkspaceSignal] = Field(default_factory=list)
    agent_outputs: list[WorkspaceAgentOutput] = Field(default_factory=list)
    minimized_context: bool = True
    authority_expansion: bool = False
    trace_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate(self) -> BroadcastSlice:
        if not self.id:
            self.id = _stable_id(
                "wcast",
                {
                    "mission_id": self.mission_id,
                    "workspace_version": self.workspace_version,
                    "role": self.role,
                    "purpose": sorted(self.purpose),
                    "accepted_facts": [fact.id for fact in self.accepted_facts],
                    "open_questions": [question.id for question in self.open_questions],
                    "rejected_claims": [claim.id for claim in self.rejected_claims],
                    "signals": [signal.id for signal in self.signals],
                    "agent_outputs": [output.id for output in self.agent_outputs],
                },
            )
        return self


class MissionGlobalWorkspace(SentinelModel):
    snapshot: WorkspaceSnapshot
    deltas: list[WorkspaceDelta] = Field(default_factory=list)
    advisory_only: bool = True
    authority_expansion: bool = False
    runtime_multi_agent_execution: bool = False
    payment_runtime: bool = False
    trading_runtime: bool = False
    account_creation_runtime: bool = False

    @classmethod
    def create(
        cls,
        envelope: MissionAuthorityEnvelope,
        *,
        open_questions: list[str] | None = None,
        evidence_refs: list[str] | None = None,
        event_bus: EventBus | None = None,
    ) -> MissionGlobalWorkspace:
        refs = evidence_refs or ["mission_context"]
        facts = [
            WorkspaceFact(text=f"Mission title: {envelope.mission_title}", evidence_refs=refs, tags=["mission_context"], source="mission_context"),
            WorkspaceFact(text=f"Mission objective: {envelope.mission_objective}", evidence_refs=refs, tags=["mission_context"], source="mission_context"),
        ]
        if envelope.success_criteria:
            facts.append(
                WorkspaceFact(
                    text=f"Success criteria: {'; '.join(envelope.success_criteria)}",
                    evidence_refs=refs,
                    tags=["mission_context", "success_criteria"],
                    source="mission_context",
                )
            )
        questions = [
            WorkspaceOpenQuestion(question=question, role_relevance=["planner_agent", "research_agent", "verifier_agent"])
            for question in sorted(open_questions or [])
        ]
        snapshot = WorkspaceSnapshot(
            mission_id=envelope.id,
            version=0,
            mission_title=envelope.mission_title,
            mission_objective=envelope.mission_objective,
            authority_summary=cls._authority_summary(envelope),
            accepted_facts=facts,
            open_questions=questions,
        )
        workspace = cls(snapshot=snapshot)
        if event_bus is None:
            return workspace
        event = event_bus.append(
            AgentEventType.WORKSPACE_SNAPSHOT_CREATED,
            "Mission global workspace snapshot created without changing authority.",
            payload={
                "snapshot_id": snapshot.id,
                "workspace_version": snapshot.version,
                "accepted_fact_count": len(snapshot.accepted_facts),
                "open_question_count": len(snapshot.open_questions),
                "advisory_only": True,
                "authority_expansion": False,
            },
        )
        traced_snapshot = snapshot.model_copy(update={"trace_refs": [event.id]})
        return cls(snapshot=traced_snapshot)

    def apply_delta(self, delta: WorkspaceDelta, *, event_bus: EventBus | None = None) -> MissionGlobalWorkspace:
        if delta.mission_id != self.snapshot.mission_id:
            raise ValueError("WorkspaceDelta mission_id must match the workspace mission.")
        if delta.base_version != self.snapshot.version:
            raise ValueError("WorkspaceDelta base_version is stale.")
        rejected_norms = {claim.normalized_text for claim in [*self.snapshot.rejected_claims, *delta.rejected_claims]}
        for fact in delta.accepted_facts:
            if fact.normalized_text in rejected_norms:
                raise ValueError("Rejected claim cannot be reintroduced as an accepted fact.")

        next_snapshot = WorkspaceSnapshot(
            mission_id=self.snapshot.mission_id,
            version=self.snapshot.version + 1,
            mission_title=self.snapshot.mission_title,
            mission_objective=self.snapshot.mission_objective,
            authority_summary=dict(self.snapshot.authority_summary),
            accepted_facts=_dedupe_by_id([*self.snapshot.accepted_facts, *delta.accepted_facts]),
            claims=_dedupe_by_id([*self.snapshot.claims, *delta.claims]),
            open_questions=_dedupe_by_id([*self.snapshot.open_questions, *delta.open_questions]),
            rejected_claims=_dedupe_by_id([*self.snapshot.rejected_claims, *delta.rejected_claims]),
            signals=_dedupe_by_id([*self.snapshot.signals, *delta.signals]),
            agent_outputs=_dedupe_by_id([*self.snapshot.agent_outputs, *delta.agent_outputs]),
            trace_refs=[*self.snapshot.trace_refs, *delta.trace_refs],
        )
        deltas = [*self.deltas, delta]
        next_workspace = self.model_copy(update={"snapshot": next_snapshot, "deltas": deltas})
        if event_bus is None:
            return next_workspace
        event = event_bus.append(
            AgentEventType.WORKSPACE_DELTA_APPLIED,
            "Mission global workspace delta applied without changing authority.",
            payload={
                "snapshot_id": next_snapshot.id,
                "delta_id": delta.id,
                "base_version": delta.base_version,
                "workspace_version": next_snapshot.version,
                "accepted_fact_count": len(next_snapshot.accepted_facts),
                "rejected_claim_count": len(next_snapshot.rejected_claims),
                "signal_count": len(next_snapshot.signals),
                "agent_output_count": len(next_snapshot.agent_outputs),
                "advisory_only": True,
                "authority_expansion": False,
            },
            trace_refs=list(delta.trace_refs),
        )
        return next_workspace.model_copy(update={"snapshot": next_snapshot.model_copy(update={"trace_refs": [*next_snapshot.trace_refs, event.id]})})

    def prepare_broadcast(
        self,
        role: str,
        *,
        purpose: list[str] | None = None,
        max_items: int = 3,
        event_bus: EventBus | None = None,
    ) -> BroadcastSlice:
        role_key = role.lower()
        purpose_values = [str(item.value if hasattr(item, "value") else item) for item in (purpose or [])]
        facts = self._facts_for_role(role_key, max_items)
        questions = self._questions_for_role(role_key, purpose_values, max_items)
        rejected = self._rejected_for_role(role_key, max_items)
        signals = self._signals_for_role(role_key, max_items)
        outputs = self._outputs_for_role(role_key, max_items)
        broadcast = BroadcastSlice(
            mission_id=self.snapshot.mission_id,
            workspace_version=self.snapshot.version,
            role=role,
            purpose=purpose_values,
            authority_summary=self.snapshot.authority_summary,
            accepted_facts=facts,
            open_questions=questions,
            rejected_claims=rejected,
            signals=signals,
            agent_outputs=outputs,
        )
        if event_bus is None:
            return broadcast
        event = event_bus.append(
            AgentEventType.WORKSPACE_BROADCAST_PREPARED,
            "Role-specific workspace broadcast prepared with minimized context.",
            payload={
                "broadcast_id": broadcast.id,
                "workspace_version": self.snapshot.version,
                "role": role,
                "purpose": purpose_values,
                "accepted_fact_count": len(broadcast.accepted_facts),
                "open_question_count": len(broadcast.open_questions),
                "rejected_claim_count": len(broadcast.rejected_claims),
                "signal_count": len(broadcast.signals),
                "agent_output_count": len(broadcast.agent_outputs),
                "minimized_context": True,
                "authority_expansion": False,
            },
            trace_refs=list(self.snapshot.trace_refs),
        )
        return broadcast.model_copy(update={"trace_refs": [event.id]})

    @classmethod
    def replay(cls, initial_snapshot: WorkspaceSnapshot, deltas: list[WorkspaceDelta]) -> MissionGlobalWorkspace:
        workspace = cls(snapshot=initial_snapshot)
        for delta in deltas:
            workspace = workspace.apply_delta(delta)
        return workspace

    def _facts_for_role(self, role_key: str, max_items: int) -> list[WorkspaceFact]:
        mission_facts = [fact for fact in self.snapshot.accepted_facts if "mission_context" in fact.tags]
        if "aggregator" in role_key or "verifier" in role_key or "skeptic" in role_key:
            return self.snapshot.accepted_facts[:max_items]
        if "cost" in role_key or "treasurer" in role_key:
            cost_facts = [fact for fact in self.snapshot.accepted_facts if "budget" in fact.tags or "cost" in fact.tags]
            return _dedupe_by_id([*mission_facts, *cost_facts])[:max_items]
        return mission_facts[:max_items]

    def _questions_for_role(self, role_key: str, purpose: list[str], max_items: int) -> list[WorkspaceOpenQuestion]:
        relevant = [
            question
            for question in self.snapshot.open_questions
            if role_key in question.role_relevance or any(item in question.role_relevance for item in purpose)
        ]
        return (relevant or self.snapshot.open_questions)[:max_items]

    def _rejected_for_role(self, role_key: str, max_items: int) -> list[WorkspaceRejectedClaim]:
        if "verifier" in role_key or "skeptic" in role_key or "aggregator" in role_key:
            return self.snapshot.rejected_claims[:max_items]
        return []

    def _signals_for_role(self, role_key: str, max_items: int) -> list[WorkspaceSignal]:
        if "cost" in role_key or "treasurer" in role_key:
            keywords = {"budget", "cost", "spend", "risk", "roi"}
            return [signal for signal in self.snapshot.signals if signal.signal_type in keywords][:max_items]
        if "aggregator" in role_key:
            return self.snapshot.signals[:max_items]
        return self.snapshot.signals[:1]

    def _outputs_for_role(self, role_key: str, max_items: int) -> list[WorkspaceAgentOutput]:
        if "aggregator" in role_key:
            return self.snapshot.agent_outputs[:max_items]
        return [output for output in self.snapshot.agent_outputs if output.role.lower() == role_key][:max_items]

    @staticmethod
    def _authority_summary(envelope: MissionAuthorityEnvelope) -> dict[str, Any]:
        return {
            "mission_id": envelope.id,
            "mode": envelope.mode.value if hasattr(envelope.mode, "value") else str(envelope.mode),
            "allowed_systems": list(envelope.allowed_systems),
            "allowed_tools": list(envelope.allowed_tools),
            "allowed_actions": list(envelope.allowed_actions),
            "forbidden_actions": list(envelope.forbidden_actions),
            "allowed_paths": list(envelope.allowed_paths),
            "allowed_domains": list(envelope.allowed_domains),
            "allowed_accounts": list(envelope.allowed_accounts),
            "max_actions": envelope.max_actions,
            "max_cost_usd": envelope.max_cost_usd,
            "max_recipients": envelope.max_recipients,
            "max_duration_minutes": envelope.max_duration_minutes,
            "risk_appetite_score": envelope.risk_appetite_score,
            "emergency_stop_enabled": envelope.emergency_stop_enabled,
            "authority_expansion": False,
        }
