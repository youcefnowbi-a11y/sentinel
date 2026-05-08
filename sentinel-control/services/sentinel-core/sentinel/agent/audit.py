from __future__ import annotations

from collections.abc import Iterable

from pydantic import Field

from sentinel.agent.event_bus import EventBus
from sentinel.agent.events import AgentEventType
from sentinel.agent.evidence import EvidenceChainReviewer
from sentinel.agent.models import AgentEvent, RuntimeCertificationResult
from sentinel.agent.phases import ABSORBING_PHASES, AgentPhase, can_transition
from sentinel.shared.models import SentinelModel


TERMINAL_EVENT_PHASES = {
    AgentEventType.AGENT_COMPLETED: AgentPhase.COMPLETED,
    AgentEventType.AGENT_FAILED: AgentPhase.FAILED,
    AgentEventType.AGENT_BLOCKED: AgentPhase.BLOCKED,
    AgentEventType.AGENT_ESCALATED: AgentPhase.ESCALATED,
    AgentEventType.AGENT_REVOKED: AgentPhase.REVOKED,
}


class AgentTraceAuditResult(SentinelModel):
    mission_id: str | None = None
    event_count: int = 0
    integrity_ok: bool = False
    final_event_type: AgentEventType | None = None
    final_phase: AgentPhase | None = None
    phase_path: list[AgentPhase] = Field(default_factory=list)
    event_types: list[AgentEventType] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

    @property
    def accepted(self) -> bool:
        return self.integrity_ok and not self.errors


class AgentTraceAuditor:
    def audit(self, events: Iterable[AgentEvent]) -> AgentTraceAuditResult:
        trace = tuple(events)
        if not trace:
            return AgentTraceAuditResult(errors=["empty_trace"])

        errors: list[str] = []
        mission_ids = {event.mission_id for event in trace}
        if len(mission_ids) != 1:
            errors.append("mixed_mission_ids")
        event_ids = [event.id for event in trace]
        if len(event_ids) != len(set(event_ids)):
            errors.append("duplicate_event_ids")

        integrity_ok = EventBus.verify_events(trace)
        if not integrity_ok:
            errors.append("hash_chain_invalid")

        phase_path = self._phase_path(trace)
        errors.extend(self._phase_transition_errors(trace))
        final_event_type = trace[-1].event_type
        final_phase = trace[-1].phase_after
        expected_phase = TERMINAL_EVENT_PHASES.get(final_event_type)

        if final_phase not in ABSORBING_PHASES:
            errors.append("trace_not_terminal")
        if expected_phase is None:
            errors.append("terminal_event_missing")
        elif final_phase != expected_phase:
            errors.append("terminal_event_phase_mismatch")

        return AgentTraceAuditResult(
            mission_id=trace[0].mission_id if len(mission_ids) == 1 else None,
            event_count=len(trace),
            integrity_ok=integrity_ok,
            final_event_type=final_event_type,
            final_phase=final_phase,
            phase_path=phase_path,
            event_types=[event.event_type for event in trace],
            errors=errors,
        )

    @staticmethod
    def _phase_path(trace: tuple[AgentEvent, ...]) -> list[AgentPhase]:
        path: list[AgentPhase] = []
        for event in trace:
            if event.phase_before is not None and not path:
                path.append(event.phase_before)
            if event.phase_after is not None and (not path or path[-1] != event.phase_after):
                path.append(event.phase_after)
        return path

    @staticmethod
    def _phase_transition_errors(trace: tuple[AgentEvent, ...]) -> list[str]:
        errors: list[str] = []
        for index, event in enumerate(trace):
            if event.phase_before is None or event.phase_after is None:
                continue
            if not can_transition(event.phase_before, event.phase_after):
                errors.append(
                    f"invalid_phase_transition_{event.phase_before.value}_to_{event.phase_after.value}_at_{index}"
                )
        return errors


def audit_agent_trace(events: Iterable[AgentEvent]) -> AgentTraceAuditResult:
    return AgentTraceAuditor().audit(events)


class RuntimeCertificationGate:
    """Certifies that runtime traces respect the mandatory cognitive order.

    The gate does not execute anything and does not mutate the trace. It rejects
    traces where worker execution appears before the cognitive control phases.
    """

    PLANNING_PREREQUISITES = (
        AgentEventType.TOOLS_SELECTED,
        AgentEventType.HYPOTHESES_REVIEWED,
        AgentEventType.WORLD_MODEL_SIMULATED,
        AgentEventType.OBJECTIVE_SCORED,
        AgentEventType.EFFORT_ROUTED,
    )
    EXECUTION_PREREQUISITES = (
        *PLANNING_PREREQUISITES,
        AgentEventType.PLAN_CREATED,
        AgentEventType.PLAN_REVIEWED,
    )
    CONTROLLED_EXECUTION_EVENTS = (
        AgentEventType.CONTROLLED_CAPABILITY_EXECUTED,
        AgentEventType.CONTROLLED_CAPABILITY_REJECTED,
    )

    def certify(self, events: Iterable[AgentEvent]) -> RuntimeCertificationResult:
        trace = tuple(events)
        audit = AgentTraceAuditor().audit(trace)
        errors = list(audit.errors)
        evidence_review = EvidenceChainReviewer().review_events(trace)
        errors.extend(evidence_review.errors)
        errors.extend(self._controlled_execution_payload_errors(trace))
        errors.extend(self._worker_lifecycle_errors(trace))
        errors.extend(self._terminal_outcome_errors(trace))
        positions = self._positions(trace)
        indices = self._indices(trace)
        planning_seen = AgentEventType.PLAN_CREATED in positions
        execution_seen = AgentEventType.WORKER_STARTED in positions or AgentEventType.CONTROLLED_CAPABILITY_EXECUTED in positions

        if planning_seen:
            for prerequisite in self.PLANNING_PREREQUISITES:
                self._require_before_each(indices, positions, prerequisite, AgentEventType.PLAN_CREATED, errors)
        if AgentEventType.PLAN_REVIEWED in positions:
            self._require_before_each(indices, positions, AgentEventType.PLAN_CREATED, AgentEventType.PLAN_REVIEWED, errors)
        if execution_seen:
            for prerequisite in self.EXECUTION_PREREQUISITES:
                if AgentEventType.WORKER_STARTED in positions:
                    self._require_before_each(indices, positions, prerequisite, AgentEventType.WORKER_STARTED, errors)
        for controlled_event in self.CONTROLLED_EXECUTION_EVENTS:
            if controlled_event in positions:
                for prerequisite in self.EXECUTION_PREREQUISITES:
                    self._require_before_each(indices, positions, prerequisite, controlled_event, errors)
        if AgentEventType.WORKER_COMPLETED in positions:
            self._require_before_each(indices, positions, AgentEventType.WORKER_STARTED, AgentEventType.WORKER_COMPLETED, errors)
        if AgentEventType.ARTIFACTS_REVIEWED in positions:
            self._require_before_each(indices, positions, AgentEventType.WORKER_COMPLETED, AgentEventType.ARTIFACTS_REVIEWED, errors)
        if AgentEventType.SUCCESS_EVALUATED in positions:
            if execution_seen:
                self._require_before_each(indices, positions, AgentEventType.ARTIFACTS_REVIEWED, AgentEventType.SUCCESS_EVALUATED, errors)
            if AgentEventType.ARTIFACTS_REVIEWED in positions:
                self._require_before_each(indices, positions, AgentEventType.REPAIR_DECIDED, AgentEventType.SUCCESS_EVALUATED, errors)
        if AgentEventType.REPAIR_EXECUTED in positions:
            self._require_before_each(indices, positions, AgentEventType.REPAIR_DECIDED, AgentEventType.REPAIR_EXECUTED, errors)
        if AgentEventType.LEARNING_PROPOSED in positions and AgentEventType.SUCCESS_EVALUATED in positions:
            self._require_before_each(indices, positions, AgentEventType.SUCCESS_EVALUATED, AgentEventType.LEARNING_PROPOSED, errors)

        terminal_ok = audit.final_phase in ABSORBING_PHASES and "terminal_event_missing" not in errors and "terminal_event_phase_mismatch" not in errors
        return RuntimeCertificationResult(
            mission_id=audit.mission_id,
            event_count=audit.event_count,
            certified=audit.integrity_ok and terminal_ok and not errors,
            integrity_ok=audit.integrity_ok,
            terminal_ok=terminal_ok,
            execution_seen=execution_seen,
            planning_seen=planning_seen,
            evidence_ok=evidence_review.accepted,
            evidence_chain_types=evidence_review.present_decision_types,
            event_types=audit.event_types,
            errors=errors,
        )

    @staticmethod
    def _positions(trace: tuple[AgentEvent, ...]) -> dict[AgentEventType, int]:
        positions: dict[AgentEventType, int] = {}
        for index, event in enumerate(trace):
            positions.setdefault(event.event_type, index)
        return positions

    @staticmethod
    def _indices(trace: tuple[AgentEvent, ...]) -> dict[AgentEventType, list[int]]:
        indices: dict[AgentEventType, list[int]] = {}
        for index, event in enumerate(trace):
            indices.setdefault(event.event_type, []).append(index)
        return indices

    @staticmethod
    def _controlled_execution_payload_errors(trace: tuple[AgentEvent, ...]) -> list[str]:
        errors: list[str] = []
        for index, event in enumerate(trace):
            payload = event.payload
            if event.event_type == AgentEventType.CONTROLLED_CAPABILITY_EXECUTED:
                required = (
                    "tool_id",
                    "tool_call_id",
                    "canonical_call_hash",
                    "action",
                    "policy_trace_id",
                    "capture_trace_id",
                    "receipt_id",
                    "artifact_id",
                    "artifact_path",
                    "artifact_sha256",
                    "rollback_strategy",
                )
                if any(not payload.get(key) for key in required):
                    errors.append(f"malformed_controlled_capability_executed_{index}")
            elif event.event_type == AgentEventType.CONTROLLED_CAPABILITY_REJECTED:
                if not payload.get("reason"):
                    errors.append(f"malformed_controlled_capability_rejected_{index}")
        return errors

    @staticmethod
    def _worker_lifecycle_errors(trace: tuple[AgentEvent, ...]) -> list[str]:
        errors: list[str] = []
        running_workers = 0
        completed_waiting_for_review = 0
        for index, event in enumerate(trace):
            if event.event_type == AgentEventType.WORKER_STARTED:
                running_workers += 1
            elif event.event_type == AgentEventType.WORKER_COMPLETED:
                if running_workers <= 0:
                    errors.append(f"worker_completed_without_worker_started_at_{index}")
                else:
                    running_workers -= 1
                completed_waiting_for_review += 1
            elif event.event_type == AgentEventType.ARTIFACTS_REVIEWED:
                if completed_waiting_for_review <= 0:
                    errors.append(f"artifacts_reviewed_without_worker_completed_at_{index}")
                else:
                    completed_waiting_for_review -= 1
        if running_workers:
            errors.append("worker_started_without_worker_completed")
        return errors

    @staticmethod
    def _terminal_outcome_errors(trace: tuple[AgentEvent, ...]) -> list[str]:
        errors: list[str] = []
        success_seen: bool | None = None
        learning_seen = False
        for index, event in enumerate(trace):
            if event.event_type == AgentEventType.SUCCESS_EVALUATED:
                success = event.payload.get("success")
                success_seen = success if isinstance(success, bool) else None
                if success_seen is None:
                    errors.append(f"success_evaluated_missing_boolean_success_at_{index}")
            elif event.event_type == AgentEventType.LEARNING_PROPOSED:
                learning_seen = True
            elif event.event_type == AgentEventType.AGENT_COMPLETED:
                if success_seen is not True:
                    errors.append("agent_completed_without_success_evaluation_true")
                if not learning_seen:
                    errors.append("agent_completed_without_learning_proposed")
            elif event.event_type == AgentEventType.AGENT_FAILED and success_seen is True:
                errors.append("agent_failed_after_success_evaluation_true")

            if event.event_type in TERMINAL_EVENT_PHASES and index != len(trace) - 1:
                errors.append(f"terminal_event_before_end_{event.event_type.value}_at_{index}")
        return errors

    @staticmethod
    def _require_before(
        positions: dict[AgentEventType, int],
        prerequisite: AgentEventType,
        later: AgentEventType,
        errors: list[str],
    ) -> None:
        if later not in positions:
            return
        if prerequisite not in positions:
            errors.append(f"missing_{prerequisite.value}_before_{later.value}")
            return
        if positions[prerequisite] > positions[later]:
            errors.append(f"{prerequisite.value}_after_{later.value}")

    @staticmethod
    def _require_before_each(
        indices: dict[AgentEventType, list[int]],
        positions: dict[AgentEventType, int],
        prerequisite: AgentEventType,
        later: AgentEventType,
        errors: list[str],
    ) -> None:
        if later not in indices:
            return
        if prerequisite not in positions:
            errors.append(f"missing_{prerequisite.value}_before_{later.value}")
            return
        prerequisite_indices = indices[prerequisite]
        for later_index in indices[later]:
            if not any(prerequisite_index < later_index for prerequisite_index in prerequisite_indices):
                errors.append(f"{prerequisite.value}_after_{later.value}_at_{later_index}")


def certify_runtime_trace(events: Iterable[AgentEvent]) -> RuntimeCertificationResult:
    return RuntimeCertificationGate().certify(events)
