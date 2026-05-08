from __future__ import annotations

from collections.abc import Iterable
from math import isclose
from typing import Any

from sentinel.agent.audit import RuntimeCertificationGate
from sentinel.agent.events import AgentEventType
from sentinel.agent.evidence import EvidenceDecisionType
from sentinel.agent.models import AgentEvent, AgentReplayResult, AgentStateSnapshot


class AgentTraceReplayer:
    """Reconstructs an audit snapshot from EventBus records.

    Replay is intentionally read-only. It derives state from event payloads and
    certification results; it never calls workers, tools, registries, or files.
    """

    def replay(self, events: Iterable[AgentEvent]) -> AgentReplayResult:
        trace = tuple(events)
        certification = RuntimeCertificationGate().certify(trace)
        errors = list(certification.errors)
        snapshot = self._snapshot(trace)
        errors.extend(snapshot.errors)
        snapshot = snapshot.model_copy(update={"errors": errors})
        return AgentReplayResult(
            accepted=certification.certified and not errors,
            snapshot=snapshot,
            certification=certification,
            errors=errors,
        )

    def _snapshot(self, trace: tuple[AgentEvent, ...]) -> AgentStateSnapshot:
        if not trace:
            return AgentStateSnapshot(errors=["empty_trace"])

        state: dict[str, Any] = {
            "mission_id": trace[0].mission_id,
            "event_count": len(trace),
            "final_phase": trace[-1].phase_after,
            "last_event_id": trace[-1].id,
            "trace_hash": trace[-1].event_hash,
        }
        errors: list[str] = []
        objective_selected_action_id: str | None = None
        objective_selected_action_name: str | None = None
        effort_level: str | None = None
        effort_score: float | None = None
        tools_selected: list[str] = []
        evidence_chain_ids: list[str] = []
        evidence_chain_types: list[EvidenceDecisionType] = []

        for event in trace:
            payload = event.payload
            if event.event_type == AgentEventType.METHODS_SELECTED:
                state["selected_methods"] = self._strings(payload.get("methods"))
            elif event.event_type == AgentEventType.EXECUTION_POSTURE_SELECTED:
                state["execution_posture"] = self._optional_string(payload.get("level"))
                state["direct_tool_call_budget"] = self._optional_int(
                    payload.get("direct_tool_call_budget", 0),
                    errors,
                    "invalid_execution_posture_direct_tool_call_budget",
                )
                state["max_repair_cycles"] = self._optional_int(
                    payload.get("max_repair_cycles", 0),
                    errors,
                    "invalid_execution_posture_max_repair_cycles",
                )
            elif event.event_type == AgentEventType.CAPABILITIES_SELECTED:
                state["needed_capabilities"] = self._strings(payload.get("needed"))
                state["missing_capabilities"] = self._strings(payload.get("missing"))
            elif event.event_type == AgentEventType.TOOLS_SELECTED:
                tools_selected = self._strings(payload.get("selected_tools"))
                state["selected_tools"] = tools_selected
                state["candidate_tools"] = self._strings(payload.get("candidate_tools"))
                state["blocked_tools"] = self._strings(payload.get("blocked_tools"))
                state["unavailable_capabilities"] = self._strings(payload.get("unavailable_capabilities"))
            elif event.event_type == AgentEventType.HYPOTHESES_REVIEWED:
                state["verified_hypotheses"] = self._strings(payload.get("verified"))
                state["rejected_hypotheses"] = self._strings(payload.get("rejected"))
            elif event.event_type == AgentEventType.OBJECTIVE_SCORED:
                objective_selected_action_id = self._optional_string(payload.get("selected_action_id"))
                objective_selected_action_name = self._optional_string(payload.get("selected_action_name"))
                state["selected_action_id"] = objective_selected_action_id
                state["selected_action_name"] = objective_selected_action_name
            elif event.event_type == AgentEventType.EFFORT_ROUTED:
                effort_level = self._optional_string(payload.get("level"))
                effort_score = self._optional_float(payload.get("score"))
                state["effort_level"] = effort_level
                state["effort_score"] = effort_score
            elif event.event_type == AgentEventType.PLAN_CREATED:
                self._check_plan_payload(payload, tools_selected, objective_selected_action_id, objective_selected_action_name, effort_level, effort_score, errors)
                state["selected_tools"] = self._strings(payload.get("selected_tools")) or state.get("selected_tools", [])
                state["verified_hypotheses"] = self._strings(payload.get("verified_hypotheses")) or state.get("verified_hypotheses", [])
                state["selected_action_id"] = self._optional_string(payload.get("selected_action_id")) or state.get("selected_action_id")
                state["selected_action_name"] = self._optional_string(payload.get("selected_action_name")) or state.get("selected_action_name")
                state["effort_level"] = self._optional_string(payload.get("effort_level")) or state.get("effort_level")
                plan_effort_score = self._optional_float(payload.get("effort_score"))
                state["effort_score"] = plan_effort_score if plan_effort_score is not None else state.get("effort_score")
            elif event.event_type == AgentEventType.WORKER_STARTED:
                state["worker_started"] = True
            elif event.event_type == AgentEventType.WORKER_COMPLETED:
                state["worker_completed"] = True
                state["project_path"] = self._optional_string(payload.get("project_path"))
            elif event.event_type == AgentEventType.CONTROLLED_CAPABILITY_EXECUTED:
                state["controlled_capability_executed_count"] = int(state.get("controlled_capability_executed_count", 0)) + 1
            elif event.event_type == AgentEventType.CONTROLLED_CAPABILITY_REJECTED:
                state["controlled_capability_rejected_count"] = int(state.get("controlled_capability_rejected_count", 0)) + 1
            elif event.event_type == AgentEventType.REPAIR_DECIDED:
                state["repair_decision"] = self._optional_string(payload.get("decision"))
                state["repair_pressure"] = self._optional_float(payload.get("repair_pressure"))
                state["repair_cycles"] = self._optional_int(
                    payload.get("current_repair_cycles", 0),
                    errors,
                    "invalid_repair_decided_current_repair_cycles",
                )
                state["max_repair_cycles"] = self._optional_int(
                    payload.get("max_repair_cycles", 0),
                    errors,
                    "invalid_repair_decided_max_repair_cycles",
                )
            elif event.event_type == AgentEventType.REPAIR_EXECUTED:
                state["repair_cycles"] = self._optional_int(
                    payload.get("repair_cycles", state.get("repair_cycles", 0)),
                    errors,
                    "invalid_repair_executed_repair_cycles",
                    default=int(state.get("repair_cycles", 0)),
                )
                state["max_repair_cycles"] = self._optional_int(
                    payload.get("max_repair_cycles", state.get("max_repair_cycles", 0)),
                    errors,
                    "invalid_repair_executed_max_repair_cycles",
                    default=int(state.get("max_repair_cycles", 0)),
                )
            elif event.event_type == AgentEventType.SUCCESS_EVALUATED:
                success = payload.get("success")
                state["success"] = success if isinstance(success, bool) else None
            elif event.event_type == AgentEventType.LEARNING_PROPOSED:
                proposal_count = payload.get("proposal_count", 0)
                state["learning_proposal_count"] = int(proposal_count) if isinstance(proposal_count, int) else 0
            elif event.event_type == AgentEventType.EVIDENCE_CHAIN_BUILT:
                chain_id = self._optional_string(payload.get("chain_id"))
                if chain_id:
                    evidence_chain_ids.append(chain_id)
                decision_type = self._optional_evidence_decision_type(payload.get("decision_type"))
                if decision_type:
                    evidence_chain_types.append(decision_type)
            elif event.event_type == AgentEventType.AGENT_COMPLETED:
                if state.get("success") is False:
                    errors.append("completed_event_conflicts_with_failed_success_evaluation")
            elif event.event_type == AgentEventType.AGENT_FAILED:
                if state.get("success") is True:
                    errors.append("failed_event_conflicts_with_success_evaluation")

        return AgentStateSnapshot(
            **state,
            evidence_chain_ids=list(dict.fromkeys(evidence_chain_ids)),
            evidence_chain_types=list(dict.fromkeys(evidence_chain_types)),
            errors=errors,
        )

    @staticmethod
    def _check_plan_payload(
        payload: dict[str, Any],
        tools_selected: list[str],
        objective_selected_action_id: str | None,
        objective_selected_action_name: str | None,
        effort_level: str | None,
        effort_score: float | None,
        errors: list[str],
    ) -> None:
        plan_tools = AgentTraceReplayer._strings(payload.get("selected_tools"))
        if plan_tools != tools_selected:
            errors.append("plan_selected_tools_mismatch")
        plan_action_id = AgentTraceReplayer._optional_string(payload.get("selected_action_id"))
        if plan_action_id != objective_selected_action_id:
            errors.append("plan_selected_action_id_mismatch")
        plan_action_name = AgentTraceReplayer._optional_string(payload.get("selected_action_name"))
        if plan_action_name != objective_selected_action_name:
            errors.append("plan_selected_action_name_mismatch")
        plan_effort_level = AgentTraceReplayer._optional_string(payload.get("effort_level"))
        if plan_effort_level != effort_level:
            errors.append("plan_effort_level_mismatch")
        plan_effort_score = AgentTraceReplayer._optional_float(payload.get("effort_score"))
        if (effort_score is None) != (plan_effort_score is None):
            errors.append("plan_effort_score_mismatch")
        elif effort_score is not None and plan_effort_score is not None and not isclose(plan_effort_score, effort_score, abs_tol=0.000001):
            errors.append("plan_effort_score_mismatch")

    @staticmethod
    def _strings(value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item) for item in value]

    @staticmethod
    def _optional_string(value: Any) -> str | None:
        if value is None:
            return None
        return str(value)

    @staticmethod
    def _optional_float(value: Any) -> float | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, int | float):
            return float(value)
        return None

    @staticmethod
    def _optional_int(value: Any, errors: list[str], error_code: str, *, default: int = 0) -> int:
        if isinstance(value, bool):
            errors.append(error_code)
            return default
        if isinstance(value, int):
            return value
        if value is None:
            return default
        errors.append(error_code)
        return default

    @staticmethod
    def _optional_evidence_decision_type(value: Any) -> EvidenceDecisionType | None:
        if value is None:
            return None
        try:
            return EvidenceDecisionType(value)
        except (TypeError, ValueError):
            return None


def replay_agent_trace(events: Iterable[AgentEvent]) -> AgentReplayResult:
    return AgentTraceReplayer().replay(events)
