from __future__ import annotations

import json
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any

from sentinel.agent.audit import RuntimeCertificationGate
from sentinel.agent.browser import (
    BrowserControlledCapabilityRunner,
    BrowserEvidenceInterpreter,
    BrowserFetcher,
    BrowserInteractionBackend,
    BrowserOperatorRouteProtocol,
    BrowserRenderer,
    DnsResolver,
)
from sentinel.agent.capability_selector import CapabilitySelector
from sentinel.agent.cognitive_cycle import CognitiveCycle
from sentinel.agent.controlled_capability import LocalControlledCapabilityRunner
from sentinel.agent.context_builder import ContextBuilder
from sentinel.agent.context_compressor import ContextCompressor
from sentinel.agent.event_bus import EventBus
from sentinel.agent.effort_router import EffortRouter
from sentinel.agent.events import AgentEventType
from sentinel.agent.evidence import EvidenceChainBuilder
from sentinel.agent.exceptions import AgentBlockedError, MissionRevokedError
from sentinel.agent.execution_posture import ExecutionPosturePolicy
from sentinel.agent.hypothesis import HypothesisVerifier
from sentinel.agent.identity import AgentIdentity, default_agent_identity
from sentinel.agent.invariants import InvariantViolation
from sentinel.agent.learning_loop import LearningLoop
from sentinel.agent.method_selector import MethodSelector
from sentinel.agent.models import AgentRunResult
from sentinel.agent.phases import AgentPhase, can_transition
from sentinel.agent.planner_bridge import PlannerBridge
from sentinel.agent.repair_loop import CognitiveRepairLoop, RepairDecisionType
from sentinel.agent.replay import AgentTraceReplayer
from sentinel.agent.review_loop import ReviewLoop
from sentinel.agent.state import AgentState
from sentinel.agent.supervisor import Supervisor
from sentinel.agent.tool_call_protocol import ToolCallProtocol
from sentinel.agent.tool_selector import ToolSelector
from sentinel.agent.worker_coordinator import WorkerCoordinator
from sentinel.agent.world_model import ActionEvaluator
from sentinel.capabilities import ToolRegistry, default_tool_registry
from sentinel.mission.models import MissionAuthorityEnvelope
from sentinel.mission.runner import MissionRunner
from sentinel.mission.safe_executors import mission_slug


class AgentRuntime:
    def __init__(
        self,
        *,
        identity: AgentIdentity | None = None,
        project_root: str | Path | None = None,
        tool_registry: ToolRegistry | None = None,
        browser_renderer: BrowserRenderer | None = None,
        browser_fetcher: BrowserFetcher | None = None,
        browser_interaction_backend: BrowserInteractionBackend | None = None,
        browser_resolver: DnsResolver | None = None,
        browser_operator_route: BrowserOperatorRouteProtocol | None = None,
    ) -> None:
        self.identity = identity or default_agent_identity()
        self.project_root = Path(project_root or Path.cwd()).resolve()
        self.tool_registry = tool_registry or default_tool_registry()
        self.context_builder = ContextBuilder()
        self.context_compressor = ContextCompressor()
        self.cognitive_cycle = CognitiveCycle()
        self.method_selector = MethodSelector()
        self.capability_selector = CapabilitySelector(registry=self.tool_registry)
        self.tool_selector = ToolSelector(self.tool_registry)
        self.tool_call_protocol = ToolCallProtocol()
        self.hypothesis_verifier = HypothesisVerifier()
        self.action_evaluator = ActionEvaluator()
        self.effort_router = EffortRouter()
        self.execution_posture_policy = ExecutionPosturePolicy()
        self.evidence_chain_builder = EvidenceChainBuilder()
        self.browser_evidence_interpreter = BrowserEvidenceInterpreter()
        self.planner_bridge = PlannerBridge(project_root=str(self.project_root))
        self.browser_operator_route = browser_operator_route
        mission_runner = MissionRunner(project_root=self.project_root, browser_operator_route=browser_operator_route) if browser_operator_route is not None else None
        self.worker_coordinator = WorkerCoordinator(project_root=self.project_root, runner=mission_runner)
        self.review_loop = ReviewLoop()
        self.repair_loop = CognitiveRepairLoop()
        self.learning_loop = LearningLoop()
        self.supervisor = Supervisor()
        self.certification_gate = RuntimeCertificationGate()
        self.trace_replayer = AgentTraceReplayer()
        self.browser_renderer = browser_renderer
        self.browser_fetcher = browser_fetcher
        self.browser_interaction_backend = browser_interaction_backend
        self.browser_resolver = browser_resolver

    def run(
        self,
        envelope: MissionAuthorityEnvelope,
        user_input: dict[str, Any] | None = None,
        *,
        evidence_refs: list[str] | None = None,
        memory_items: list[dict[str, Any]] | None = None,
    ) -> AgentRunResult:
        event_bus = EventBus(envelope.id)
        evidence_chains = []
        controlled_capability_results: list[dict[str, Any]] = []
        mission_results = []
        execution_posture = None
        context = None
        state = AgentState(mission_id=envelope.id).transition(AgentPhase.INITIALIZED)
        event_bus.append(
            AgentEventType.AGENT_INITIALIZED,
            "Agent runtime initialized.",
            phase_before=AgentPhase.CREATED,
            phase_after=AgentPhase.INITIALIZED,
            payload={"agent_id": self.identity.id, "doctrine": self.identity.doctrine},
        )

        try:
            state = state.transition(AgentPhase.CONTEXT_BUILDING)
            context = self.context_builder.build(
                envelope,
                user_input=user_input or {},
                evidence_refs=evidence_refs,
                memory_items=memory_items,
            )
            self.supervisor.assert_mission_can_run(context)
            self.supervisor.assert_context_did_not_expand_authority(context)
            event_bus.append(
                AgentEventType.CONTEXT_BUILT,
                "Agent context built from mission authority and input.",
                phase_before=AgentPhase.INITIALIZED,
                phase_after=AgentPhase.CONTEXT_BUILDING,
                payload={"summary": context.summary, "constraints": context.constraints},
            )

            context = self.context_compressor.compress(context)
            event_bus.append(
                AgentEventType.CONTEXT_COMPRESSED,
                "Agent context compressed while preserving authority and references.",
                phase_before=AgentPhase.CONTEXT_BUILDING,
                phase_after=AgentPhase.CONTEXT_BUILDING,
                payload={"summary": context.summary, "evidence_refs": context.evidence_refs},
            )

            state = state.transition(AgentPhase.ORIENTING)
            state = self.cognitive_cycle.orient(state, context)
            event_bus.append(
                AgentEventType.ORIENTATION_COMPLETED,
                "Agent orientation completed.",
                phase_before=AgentPhase.CONTEXT_BUILDING,
                phase_after=AgentPhase.ORIENTING,
                payload={"known_facts": len(state.known_facts), "open_questions": len(state.open_questions)},
            )

            state = state.transition(AgentPhase.METHOD_SELECTING)
            methods = self.method_selector.select(context)
            state = state.model_copy(update={"selected_methods": methods})
            event_bus.append(
                AgentEventType.METHODS_SELECTED,
                "Agent selected deterministic work methods.",
                phase_before=AgentPhase.ORIENTING,
                phase_after=AgentPhase.METHOD_SELECTING,
                payload={"methods": [method.id for method in methods]},
            )

            state = state.transition(AgentPhase.CAPABILITY_SELECTING)
            capabilities = self.capability_selector.select(context, methods)
            missing_capabilities = [need for need in capabilities if not need.available]
            self.supervisor.assert_capabilities_are_declared(capabilities)
            state = state.model_copy(update={"needed_capabilities": capabilities, "missing_capabilities": missing_capabilities})
            event_bus.append(
                AgentEventType.CAPABILITIES_SELECTED,
                "Agent declared capability needs.",
                phase_before=AgentPhase.METHOD_SELECTING,
                phase_after=AgentPhase.CAPABILITY_SELECTING,
                payload={"needed": [need.name for need in capabilities], "missing": [need.name for need in missing_capabilities]},
            )

            state = state.transition(AgentPhase.TOOL_SELECTING)
            tool_selection = self.tool_selector.select(context, capabilities, event_bus=event_bus)
            state = state.model_copy(
                update={
                    "tool_selection_decisions": tool_selection.decisions,
                    "selected_tools": tool_selection.selected_tools,
                    "candidate_tools": tool_selection.candidate_tools,
                    "blocked_tools": tool_selection.blocked_tools,
                    "unavailable_capabilities": tool_selection.unavailable_capabilities,
                }
            )
            tool_selection_findings = self.review_loop.review_tool_selection(capabilities, tool_selection)
            evidence_chains.append(
                self.evidence_chain_builder.build_tool_selection(
                    context,
                    tool_selection,
                    tool_selection_findings,
                    event_bus=event_bus,
                )
            )
            state = state.model_copy(update={"review_findings": tool_selection_findings})
            critical_tool_selection_findings = [
                finding for finding in tool_selection_findings if finding.severity == "critical"
            ]
            if critical_tool_selection_findings:
                state = state.transition(AgentPhase.LEARNING_PROPOSING)
                learning_proposals = self.learning_loop.propose(
                    review_findings=tool_selection_findings,
                    missing_capabilities=[need for need in capabilities if need.name in tool_selection.missing_capabilities],
                    mission_failed=True,
                )
                self.supervisor.assert_learning_is_safe(learning_proposals)
                event_bus.append(
                    AgentEventType.LEARNING_PROPOSED,
                    "Agent created learning proposals after tool selection review.",
                    phase_before=AgentPhase.TOOL_SELECTING,
                    phase_after=AgentPhase.LEARNING_PROPOSING,
                    payload={"proposal_count": len(learning_proposals)},
                )
                evidence_chains.append(
                    self.evidence_chain_builder.build_learning_proposal(
                        context,
                        learning_proposals,
                        tool_selection_findings,
                        [need for need in capabilities if need.name in tool_selection.missing_capabilities],
                        event_bus=event_bus,
                    )
                )
                state = state.transition(AgentPhase.BLOCKED)
                event_bus.append(
                    AgentEventType.AGENT_BLOCKED,
                    "Agent blocked execution because required tools were unavailable.",
                    phase_before=AgentPhase.LEARNING_PROPOSING,
                    phase_after=AgentPhase.BLOCKED,
                    payload={"findings": [finding.code for finding in critical_tool_selection_findings]},
                )
                self.supervisor.assert_trace_integrity(event_bus)
                return AgentRunResult(
                    mission_id=envelope.id,
                    final_phase=AgentPhase.BLOCKED,
                    success=False,
                    selected_methods=methods,
                    needed_capabilities=capabilities,
                    missing_capabilities=missing_capabilities,
                    tool_selection_decisions=tool_selection.decisions,
                    selected_tools=tool_selection.selected_tools,
                    candidate_tools=tool_selection.candidate_tools,
                    blocked_tools=tool_selection.blocked_tools,
                    unavailable_capabilities=tool_selection.unavailable_capabilities,
                    known_facts=state.known_facts,
                    assumptions=state.assumptions,
                    suspected=state.suspected,
                    open_questions=state.open_questions,
                    review_findings=tool_selection_findings,
                    learning_proposals=learning_proposals,
                    evidence_chains=evidence_chains,
                    trace=list(event_bus.events()),
                    runtime_certification=self._certify_trace(event_bus),
                    state_snapshot=self._snapshot_trace(event_bus),
                    escalation_reason="Tool selection produced critical findings.",
                )

            state = state.transition(AgentPhase.HYPOTHESIS_VERIFYING)
            hypothesis_result = self.hypothesis_verifier.run(context, event_bus=event_bus)
            state = state.model_copy(
                update={
                    "hypotheses": hypothesis_result.hypotheses,
                    "verified_hypotheses": hypothesis_result.verified_hypotheses,
                    "verification_tests": hypothesis_result.verification_tests,
                    "adversarial_findings": hypothesis_result.adversarial_findings,
                }
            )
            hypothesis_findings = self.review_loop.review_hypotheses(hypothesis_result)
            evidence_chains.append(
                self.evidence_chain_builder.build_hypothesis_verdict(
                    context,
                    hypothesis_result,
                    hypothesis_findings,
                    event_bus=event_bus,
                )
            )
            critical_hypothesis_findings = [finding for finding in hypothesis_findings if finding.severity == "critical"]
            if critical_hypothesis_findings:
                state = state.model_copy(update={"review_findings": hypothesis_findings})
                state = state.transition(AgentPhase.LEARNING_PROPOSING)
                learning_proposals = self.learning_loop.propose(
                    review_findings=hypothesis_findings,
                    missing_capabilities=[],
                    mission_failed=True,
                )
                self.supervisor.assert_learning_is_safe(learning_proposals)
                event_bus.append(
                    AgentEventType.LEARNING_PROPOSED,
                    "Agent created learning proposals after hypothesis verification review.",
                    phase_before=AgentPhase.HYPOTHESIS_VERIFYING,
                    phase_after=AgentPhase.LEARNING_PROPOSING,
                    payload={"proposal_count": len(learning_proposals)},
                )
                evidence_chains.append(
                    self.evidence_chain_builder.build_learning_proposal(
                        context,
                        learning_proposals,
                        hypothesis_findings,
                        [],
                        event_bus=event_bus,
                    )
                )
                state = state.transition(AgentPhase.BLOCKED)
                event_bus.append(
                    AgentEventType.AGENT_BLOCKED,
                    "Agent blocked execution because hypothesis verification violated invariants.",
                    phase_before=AgentPhase.LEARNING_PROPOSING,
                    phase_after=AgentPhase.BLOCKED,
                    payload={"findings": [finding.code for finding in critical_hypothesis_findings]},
                )
                self.supervisor.assert_trace_integrity(event_bus)
                return AgentRunResult(
                    mission_id=envelope.id,
                    final_phase=AgentPhase.BLOCKED,
                    success=False,
                    selected_methods=methods,
                    needed_capabilities=capabilities,
                    missing_capabilities=missing_capabilities,
                    tool_selection_decisions=tool_selection.decisions,
                    selected_tools=tool_selection.selected_tools,
                    candidate_tools=tool_selection.candidate_tools,
                    blocked_tools=tool_selection.blocked_tools,
                    unavailable_capabilities=tool_selection.unavailable_capabilities,
                    hypotheses=hypothesis_result.hypotheses,
                    verified_hypotheses=hypothesis_result.verified_hypotheses,
                    verification_tests=hypothesis_result.verification_tests,
                    adversarial_findings=hypothesis_result.adversarial_findings,
                    known_facts=state.known_facts,
                    assumptions=state.assumptions,
                    suspected=state.suspected,
                    open_questions=state.open_questions,
                    review_findings=hypothesis_findings,
                    learning_proposals=learning_proposals,
                    evidence_chains=evidence_chains,
                    trace=list(event_bus.events()),
                    runtime_certification=self._certify_trace(event_bus),
                    state_snapshot=self._snapshot_trace(event_bus),
                    escalation_reason="Hypothesis verification produced critical findings.",
                )

            state = state.transition(AgentPhase.ACTION_SCORING)
            action_result = self.action_evaluator.evaluate(
                context,
                state,
                tool_selection,
                hypothesis_result,
                event_bus=event_bus,
            )
            state = state.model_copy(
                update={
                    "cognitive_actions": action_result.actions,
                    "world_model_predictions": action_result.predictions,
                    "objective_scores": action_result.scores,
                    "action_evaluations": action_result.evaluations,
                    "selected_action_id": action_result.selected_action_id,
                    "selected_action_name": action_result.selected_action_name,
                }
            )

            state = state.transition(AgentPhase.EFFORT_ROUTING)
            effort_route = self.effort_router.route(
                context,
                state,
                tool_selection,
                hypothesis_result,
                action_result,
                event_bus=event_bus,
            )
            state = state.model_copy(update={"effort_route": effort_route})

            state = state.transition(AgentPhase.PLANNING)
            plan = self.planner_bridge.create_plan(
                context,
                methods,
                capabilities,
                tool_selection=tool_selection,
                verified_hypotheses=hypothesis_result.verified_hypotheses,
            )
            state = state.model_copy(update={"plan_id": plan.mission_id})
            event_bus.append(
                AgentEventType.PLAN_CREATED,
                "Mission plan created through MissionRegistry.",
                phase_before=AgentPhase.EFFORT_ROUTING,
                phase_after=AgentPhase.PLANNING,
                payload={
                    "steps": [step.id for step in plan.steps],
                    "selected_tools": tool_selection.selected_tools,
                    "verified_hypotheses": [hypothesis.id for hypothesis in hypothesis_result.verified_hypotheses],
                    "selected_action_id": action_result.selected_action_id,
                    "selected_action_name": action_result.selected_action_name,
                    "effort_level": effort_route.level,
                    "effort_score": effort_route.score,
                },
            )
            execution_posture = self.execution_posture_policy.select(
                envelope,
                reserved_plan_actions=len(plan.steps),
                phase=AgentPhase.PLANNING,
                event_bus=event_bus,
            )
            state = state.model_copy(
                update={
                    "execution_posture": execution_posture,
                    "max_repair_cycles": execution_posture.max_repair_cycles,
                }
            )

            state = state.transition(AgentPhase.PLAN_REVIEWING)
            review_findings = [
                *hypothesis_findings,
                *self.review_loop.review_plan(
                    context,
                    plan,
                    capabilities,
                    tool_selection=tool_selection,
                    verified_hypotheses=hypothesis_result.verified_hypotheses,
                ),
            ]
            state = state.model_copy(update={"review_findings": review_findings})
            event_bus.append(
                AgentEventType.PLAN_REVIEWED,
                "Agent reviewed plan before execution.",
                phase_before=AgentPhase.PLANNING,
                phase_after=AgentPhase.PLAN_REVIEWING,
                payload={"findings": [finding.code for finding in review_findings]},
            )
            evidence_chains.append(
                self.evidence_chain_builder.build_plan_creation(
                    context,
                    plan,
                    tool_selection,
                    hypothesis_result.verified_hypotheses,
                    review_findings,
                    event_bus=event_bus,
                )
            )
            critical_plan_findings = [finding for finding in review_findings if finding.severity == "critical"]
            if critical_plan_findings:
                state = state.transition(AgentPhase.LEARNING_PROPOSING)
                learning_proposals = self.learning_loop.propose(
                    review_findings=review_findings,
                    missing_capabilities=[need for need in missing_capabilities if need.required],
                    mission_failed=True,
                )
                self.supervisor.assert_learning_is_safe(learning_proposals)
                event_bus.append(
                    AgentEventType.LEARNING_PROPOSED,
                    "Agent created learning proposals after critical plan review.",
                    phase_before=AgentPhase.PLAN_REVIEWING,
                    phase_after=AgentPhase.LEARNING_PROPOSING,
                    payload={"proposal_count": len(learning_proposals)},
                )
                evidence_chains.append(
                    self.evidence_chain_builder.build_learning_proposal(
                        context,
                        learning_proposals,
                        review_findings,
                        [need for need in missing_capabilities if need.required],
                        event_bus=event_bus,
                    )
                )
                state = state.transition(AgentPhase.BLOCKED)
                event_bus.append(
                    AgentEventType.AGENT_BLOCKED,
                    "Agent blocked execution because plan review found critical issues.",
                    phase_before=AgentPhase.LEARNING_PROPOSING,
                    phase_after=AgentPhase.BLOCKED,
                    payload={"findings": [finding.code for finding in critical_plan_findings]},
                )
                self.supervisor.assert_trace_integrity(event_bus)
                return AgentRunResult(
                    mission_id=envelope.id,
                    final_phase=AgentPhase.BLOCKED,
                    success=False,
                    selected_methods=methods,
                    needed_capabilities=capabilities,
                    missing_capabilities=missing_capabilities,
                    tool_selection_decisions=tool_selection.decisions,
                    selected_tools=tool_selection.selected_tools,
                    candidate_tools=tool_selection.candidate_tools,
                    blocked_tools=tool_selection.blocked_tools,
                    unavailable_capabilities=tool_selection.unavailable_capabilities,
                    known_facts=state.known_facts,
                    assumptions=state.assumptions,
                    suspected=state.suspected,
                    open_questions=state.open_questions,
                    hypotheses=hypothesis_result.hypotheses,
                    verified_hypotheses=hypothesis_result.verified_hypotheses,
                    verification_tests=hypothesis_result.verification_tests,
                    adversarial_findings=hypothesis_result.adversarial_findings,
                    cognitive_actions=action_result.actions,
                    world_model_predictions=action_result.predictions,
                    objective_scores=action_result.scores,
                    action_evaluations=action_result.evaluations,
                    selected_action_id=action_result.selected_action_id,
                    selected_action_name=action_result.selected_action_name,
                    controlled_capability_results=controlled_capability_results,
                    effort_route=effort_route,
                    execution_posture=execution_posture,
                    review_findings=review_findings,
                    learning_proposals=learning_proposals,
                    evidence_chains=evidence_chains,
                    trace=list(event_bus.events()),
                    runtime_certification=self._certify_trace(event_bus),
                    state_snapshot=self._snapshot_trace(event_bus),
                    escalation_reason="Plan review produced critical findings.",
                    active_plan=plan,
                )

            state = state.transition(AgentPhase.EXECUTING)
            controlled_capability_results = self._execute_controlled_tool_calls(
                envelope,
                user_input or {},
                event_bus,
                max_calls=execution_posture.direct_tool_call_budget if execution_posture is not None else max(0, envelope.max_actions - len(plan.steps)),
            )
            state = state.model_copy(update={"controlled_capability_results": controlled_capability_results})
            browser_cortex = self.browser_evidence_interpreter.interpret(
                context,
                event_bus.events(),
                hypotheses=hypothesis_result.hypotheses,
                event_bus=event_bus,
            )
            browser_cortex_findings = browser_cortex.review_findings if browser_cortex.browser_signal_count else []
            if browser_cortex.evidence_chain is not None:
                evidence_chains.append(browser_cortex.evidence_chain)
            worker_result = self.worker_coordinator.run_mission_worker(context, event_bus, plan=plan)

            state = state.transition(AgentPhase.ARTIFACT_REVIEWING)
            artifact_findings = self.review_loop.review_worker_result(worker_result)
            control_findings = list(state.review_findings)
            all_findings = [*control_findings, *artifact_findings, *browser_cortex_findings]
            state = state.model_copy(update={"review_findings": all_findings})
            event_bus.append(
                AgentEventType.ARTIFACTS_REVIEWED,
                "Agent reviewed worker artifacts.",
                phase_before=AgentPhase.EXECUTING,
                phase_after=AgentPhase.ARTIFACT_REVIEWING,
                payload={"findings": [finding.code for finding in artifact_findings]},
            )

            mission_result = worker_result.mission_result
            if mission_result is not None:
                mission_results.append(mission_result)
            repair_decision = self.repair_loop.decide(
                context,
                state,
                review_findings=all_findings,
                adversarial_findings=hypothesis_result.adversarial_findings,
                objective_scores=action_result.scores,
                effort_route=effort_route,
                event_bus=event_bus,
            )
            repair_decision = self._block_repair_if_action_budget_would_overflow(
                envelope,
                state,
                repair_decision,
                controlled_capability_results,
                mission_result,
                plan_step_count=len(plan.steps),
                event_bus=event_bus,
            )
            state = state.model_copy(update={"repair_decision": repair_decision})
            evidence_chains.append(
                self.evidence_chain_builder.build_repair_decision(
                    context,
                    repair_decision,
                    all_findings,
                    hypothesis_result.adversarial_findings,
                    event_bus=event_bus,
                )
            )
            if repair_decision.decision == RepairDecisionType.ESCALATE:
                state = state.transition(AgentPhase.ESCALATED)
                event_bus.append(
                    AgentEventType.AGENT_ESCALATED,
                    "Agent escalated after bounded repair certification.",
                    phase_before=AgentPhase.ARTIFACT_REVIEWING,
                    phase_after=AgentPhase.ESCALATED,
                    payload={"repair_pressure": repair_decision.repair_pressure},
                    trace_refs=repair_decision.trace_refs,
                )
                self.supervisor.assert_trace_integrity(event_bus)
                return AgentRunResult(
                    mission_id=envelope.id,
                    final_phase=AgentPhase.ESCALATED,
                    success=False,
                    project_path=mission_result.project_path if mission_result else None,
                    artifacts=mission_result.artifacts if mission_result else [],
                    selected_methods=methods,
                    needed_capabilities=capabilities,
                    missing_capabilities=missing_capabilities,
                    tool_selection_decisions=tool_selection.decisions,
                    selected_tools=tool_selection.selected_tools,
                    candidate_tools=tool_selection.candidate_tools,
                    blocked_tools=tool_selection.blocked_tools,
                    unavailable_capabilities=tool_selection.unavailable_capabilities,
                    hypotheses=hypothesis_result.hypotheses,
                    verified_hypotheses=hypothesis_result.verified_hypotheses,
                    verification_tests=hypothesis_result.verification_tests,
                    adversarial_findings=hypothesis_result.adversarial_findings,
                    cognitive_actions=action_result.actions,
                    world_model_predictions=action_result.predictions,
                    objective_scores=action_result.scores,
                    action_evaluations=action_result.evaluations,
                    selected_action_id=action_result.selected_action_id,
                    selected_action_name=action_result.selected_action_name,
                    controlled_capability_results=controlled_capability_results,
                    effort_route=effort_route,
                    execution_posture=execution_posture,
                    repair_decision=repair_decision,
                    known_facts=state.known_facts,
                    assumptions=state.assumptions,
                    suspected=state.suspected,
                    open_questions=state.open_questions,
                    review_findings=all_findings,
                    evidence_chains=evidence_chains,
                    trace=list(event_bus.events()),
                    runtime_certification=self._certify_trace(event_bus),
                    state_snapshot=self._snapshot_trace(event_bus),
                    mission_result=mission_result,
                    mission_results=mission_results,
                    escalation_reason="Repair pressure exceeded escalation threshold.",
                    active_plan=plan,
                )
            if repair_decision.decision == RepairDecisionType.REPAIR_ALLOWED:
                state = state.transition(AgentPhase.REPAIRING)
                state = state.model_copy(update={"repair_cycles": state.repair_cycles + 1})
                self.supervisor.assert_state_bounds(state)
                repair_execution_phase_before = state.phase
                state = state.transition(AgentPhase.EXECUTING)
                event_bus.append(
                    AgentEventType.REPAIR_EXECUTED,
                    "Agent executed one bounded internal repair pass through the existing mission worker.",
                    phase_before=repair_execution_phase_before,
                    phase_after=AgentPhase.EXECUTING,
                    payload={
                        "repair_decision_id": repair_decision.id,
                        "repair_cycles": state.repair_cycles,
                        "max_repair_cycles": state.max_repair_cycles,
                        "instruction_count": len(repair_decision.instructions),
                    },
                    trace_refs=repair_decision.trace_refs,
                )
                repair_worker_result = self.worker_coordinator.run_mission_worker(context, event_bus, plan=plan)
                state = state.transition(AgentPhase.ARTIFACT_REVIEWING)
                repair_artifact_findings = self.review_loop.review_worker_result(repair_worker_result)
                all_findings = [*control_findings, *repair_artifact_findings]
                state = state.model_copy(update={"review_findings": all_findings})
                event_bus.append(
                    AgentEventType.ARTIFACTS_REVIEWED,
                    "Agent reviewed worker artifacts after bounded repair pass.",
                    phase_before=AgentPhase.EXECUTING,
                    phase_after=AgentPhase.ARTIFACT_REVIEWING,
                    payload={
                        "repair_decision_id": repair_decision.id,
                        "findings": [finding.code for finding in repair_artifact_findings],
                    },
                    trace_refs=repair_decision.trace_refs,
                )
                repair_mission_result = repair_worker_result.mission_result
                if repair_mission_result is not None:
                    mission_results.append(repair_mission_result)
                mission_result = repair_mission_result or mission_result

            success_phase_before = state.phase
            state = state.transition(AgentPhase.SUCCESS_EVALUATING)
            mission_success = bool(mission_result and mission_result.success and not [finding for finding in all_findings if finding.severity == "critical"])
            event_bus.append(
                AgentEventType.SUCCESS_EVALUATED,
                "Agent evaluated mission success.",
                phase_before=success_phase_before,
                phase_after=AgentPhase.SUCCESS_EVALUATING,
                payload={"success": mission_success},
            )
            evidence_chains.append(
                self.evidence_chain_builder.build_success_evaluation(
                    context,
                    mission_success=mission_success,
                    mission_result=mission_result,
                    review_findings=all_findings,
                    repair_decision=repair_decision,
                    event_bus=event_bus,
                )
            )

            state = state.transition(AgentPhase.LEARNING_PROPOSING)
            learning_proposals = self.learning_loop.propose(
                review_findings=all_findings,
                missing_capabilities=[need for need in missing_capabilities if need.required],
                mission_failed=not mission_success,
            )
            self.supervisor.assert_learning_is_safe(learning_proposals)
            event_bus.append(
                AgentEventType.LEARNING_PROPOSED,
                "Agent created safe learning proposals.",
                phase_before=AgentPhase.SUCCESS_EVALUATING,
                phase_after=AgentPhase.LEARNING_PROPOSING,
                payload={"proposal_count": len(learning_proposals)},
            )
            evidence_chains.append(
                self.evidence_chain_builder.build_learning_proposal(
                    context,
                    learning_proposals,
                    all_findings,
                    [need for need in missing_capabilities if need.required],
                    event_bus=event_bus,
                )
            )

            final_phase = AgentPhase.COMPLETED if mission_success else AgentPhase.FAILED
            state = state.transition(final_phase)
            if final_phase == AgentPhase.COMPLETED:
                self.supervisor.assert_completion(state, mission_result)
            event_bus.append(
                AgentEventType.AGENT_COMPLETED if mission_success else AgentEventType.AGENT_FAILED,
                "Agent run finalized.",
                phase_before=AgentPhase.LEARNING_PROPOSING,
                phase_after=final_phase,
                payload={"success": mission_success},
            )
            self.supervisor.assert_trace_integrity(event_bus)

            return AgentRunResult(
                mission_id=envelope.id,
                final_phase=final_phase,
                success=mission_success,
                project_path=mission_result.project_path if mission_result else None,
                artifacts=mission_result.artifacts if mission_result else [],
                selected_methods=methods,
                needed_capabilities=capabilities,
                missing_capabilities=missing_capabilities,
                tool_selection_decisions=tool_selection.decisions,
                selected_tools=tool_selection.selected_tools,
                candidate_tools=tool_selection.candidate_tools,
                blocked_tools=tool_selection.blocked_tools,
                unavailable_capabilities=tool_selection.unavailable_capabilities,
                hypotheses=hypothesis_result.hypotheses,
                verified_hypotheses=hypothesis_result.verified_hypotheses,
                verification_tests=hypothesis_result.verification_tests,
                adversarial_findings=hypothesis_result.adversarial_findings,
                cognitive_actions=action_result.actions,
                world_model_predictions=action_result.predictions,
                objective_scores=action_result.scores,
                action_evaluations=action_result.evaluations,
                selected_action_id=action_result.selected_action_id,
                selected_action_name=action_result.selected_action_name,
                controlled_capability_results=controlled_capability_results,
                effort_route=effort_route,
                execution_posture=execution_posture,
                repair_decision=repair_decision,
                known_facts=state.known_facts,
                assumptions=state.assumptions,
                suspected=state.suspected,
                open_questions=state.open_questions,
                review_findings=all_findings,
                learning_proposals=learning_proposals,
                evidence_chains=evidence_chains,
                trace=list(event_bus.events()),
                runtime_certification=self._certify_trace(event_bus),
                state_snapshot=self._snapshot_trace(event_bus),
                mission_result=mission_result,
                mission_results=mission_results,
                active_plan=plan,
            )
        except Exception as exc:
            final_phase = AgentPhase.FAILED
            event_type = AgentEventType.AGENT_FAILED
            if isinstance(exc, MissionRevokedError):
                final_phase = AgentPhase.REVOKED
                event_type = AgentEventType.AGENT_REVOKED
            elif isinstance(exc, (AgentBlockedError, InvariantViolation)):
                final_phase = AgentPhase.BLOCKED
                event_type = AgentEventType.AGENT_BLOCKED
            learning_proposals = []
            if context is not None and can_transition(state.phase, AgentPhase.LEARNING_PROPOSING):
                learning_phase_before = state.phase
                state = state.transition(AgentPhase.LEARNING_PROPOSING)
                learning_proposals = self.learning_loop.propose(
                    review_findings=[],
                    missing_capabilities=[],
                    mission_failed=True,
                )
                self.supervisor.assert_learning_is_safe(learning_proposals)
                event_bus.append(
                    AgentEventType.LEARNING_PROPOSED,
                    "Agent created safe learning proposals after a runtime exception.",
                    phase_before=learning_phase_before,
                    phase_after=AgentPhase.LEARNING_PROPOSING,
                    payload={"proposal_count": len(learning_proposals)},
                )
                evidence_chains.append(
                    self.evidence_chain_builder.build_learning_proposal(
                        context,
                        learning_proposals,
                        [],
                        [],
                        event_bus=event_bus,
                    )
                )
            event_bus.append(
                event_type,
                "Agent run failed before completion.",
                phase_before=state.phase,
                phase_after=final_phase,
                payload={"error": str(exc)},
            )
            self.supervisor.assert_trace_integrity(event_bus)
            return AgentRunResult(
                mission_id=envelope.id,
                final_phase=final_phase,
                success=False,
                review_findings=[],
                learning_proposals=learning_proposals,
                evidence_chains=evidence_chains,
                controlled_capability_results=controlled_capability_results,
                execution_posture=execution_posture,
                trace=list(event_bus.events()),
                runtime_certification=self._certify_trace(event_bus),
                state_snapshot=self._snapshot_trace(event_bus),
                mission_results=mission_results,
                escalation_reason=str(exc),
            )

    def _execute_controlled_tool_calls(
        self,
        envelope: MissionAuthorityEnvelope,
        user_input: dict[str, Any],
        event_bus: EventBus,
        *,
        max_calls: int,
    ) -> list[dict[str, Any]]:
        raw_calls, requested_count = self._raw_tool_call_payloads(user_input, limit=max_calls)
        if requested_count == 0:
            return []
        if max_calls <= 0:
            event = event_bus.append(
                AgentEventType.CONTROLLED_CAPABILITY_REJECTED,
                "Controlled local capability requests skipped because the direct-call budget is exhausted.",
                phase_before=AgentPhase.EXECUTING,
                phase_after=AgentPhase.EXECUTING,
                payload={
                    "reason": "direct_tool_call_budget_exhausted",
                    "requested_count": requested_count,
                    "max_calls": max_calls,
                },
            )
            return [
                {
                    "accepted": False,
                    "status": "rejected",
                    "reason": "direct_tool_call_budget_exhausted",
                    "requested_count": requested_count,
                    "trace_event_id": event.id,
                }
            ]

        runner = LocalControlledCapabilityRunner(
            registry=self.tool_registry,
            capture_root=self._controlled_capture_root(envelope),
        )
        browser_runner = BrowserControlledCapabilityRunner(
            registry=self.tool_registry,
            capture_root=self._controlled_capture_root(envelope),
            renderer=self.browser_renderer,
            fetcher=self.browser_fetcher,
            interaction_backend=self.browser_interaction_backend,
            resolver=self.browser_resolver,
        )
        results: list[dict[str, Any]] = []
        for raw_call in raw_calls:
            canonicalization = self.tool_call_protocol.canonicalize(
                raw_call,
                event_bus=event_bus,
                phase=AgentPhase.EXECUTING,
            )
            if not canonicalization.accepted or canonicalization.call is None:
                event = event_bus.append(
                    AgentEventType.CONTROLLED_CAPABILITY_REJECTED,
                    "Controlled local capability request rejected because the tool call was not canonical.",
                    phase_before=AgentPhase.EXECUTING,
                    phase_after=AgentPhase.EXECUTING,
                    payload={
                        "reason": "tool_call_not_canonical",
                        "canonicalization_trace_id": canonicalization.trace_event_id,
                        "errors": canonicalization.errors,
                    },
                    trace_refs=[canonicalization.trace_event_id] if canonicalization.trace_event_id else [],
                )
                results.append(
                    {
                        "accepted": False,
                        "status": "rejected",
                        "reason": "tool_call_not_canonical",
                        "errors": canonicalization.errors,
                        "canonicalization_trace_id": canonicalization.trace_event_id,
                        "trace_event_id": event.id,
                    }
                )
                continue

            if canonicalization.call.action in BrowserControlledCapabilityRunner.SUPPORTED_ACTIONS:
                if self.browser_operator_route is not None:
                    route_result = self.browser_operator_route.run(
                        canonicalization.call,
                        envelope,
                        event_bus=event_bus,
                        capture_root=self._controlled_capture_root(envelope),
                    )
                    result = route_result.controlled_result
                    payload = result.model_dump(mode="json")
                    payload["operator_route"] = route_result.model_dump(mode="json", exclude={"controlled_result"})
                    results.append(payload)
                    continue
                result = browser_runner.run(canonicalization.call, envelope, event_bus=event_bus)
            else:
                result = runner.run(canonicalization.call, envelope, event_bus=event_bus)
            results.append(result.model_dump(mode="json"))
        overflow_count = requested_count - len(raw_calls)
        if overflow_count > 0:
            event = event_bus.append(
                AgentEventType.CONTROLLED_CAPABILITY_REJECTED,
                "Extra controlled local capability requests skipped after exhausting the direct-call budget.",
                phase_before=AgentPhase.EXECUTING,
                phase_after=AgentPhase.EXECUTING,
                payload={
                    "reason": "direct_tool_call_budget_exhausted",
                    "requested_count": requested_count,
                    "executed_or_evaluated_count": len(raw_calls),
                    "skipped_count": overflow_count,
                },
            )
            results.append(
                {
                    "accepted": False,
                    "status": "rejected",
                    "reason": "direct_tool_call_budget_exhausted",
                    "skipped_count": overflow_count,
                    "trace_event_id": event.id,
                }
            )
        return results

    def _block_repair_if_action_budget_would_overflow(
        self,
        envelope: MissionAuthorityEnvelope,
        state: AgentState,
        repair_decision,
        controlled_capability_results: list[dict[str, Any]],
        mission_result,
        *,
        plan_step_count: int,
        event_bus: EventBus,
    ):
        if repair_decision.decision != RepairDecisionType.REPAIR_ALLOWED:
            return repair_decision

        controlled_executed = self._accepted_controlled_capability_count(controlled_capability_results)
        mission_actions_used = mission_result.state.action_count if mission_result is not None else 0
        projected_total = controlled_executed + mission_actions_used + max(0, plan_step_count)
        if projected_total <= envelope.max_actions:
            return repair_decision

        reasons = [
            *repair_decision.reasons,
            "repair_blocked_by_global_action_budget",
        ]
        event = event_bus.append(
            AgentEventType.REPAIR_DECIDED,
            "Bounded repair was blocked because the projected run action budget would overflow.",
            phase_before=state.phase,
            phase_after=state.phase,
            payload={
                "decision": RepairDecisionType.REPAIR_BLOCKED,
                "repair_pressure": repair_decision.repair_pressure,
                "reasons": reasons,
                "findings_used": repair_decision.findings_used,
                "current_repair_cycles": state.repair_cycles,
                "max_repair_cycles": state.max_repair_cycles,
                "controlled_executed": controlled_executed,
                "mission_actions_used": mission_actions_used,
                "projected_repair_actions": max(0, plan_step_count),
                "projected_total_actions": projected_total,
                "max_actions": envelope.max_actions,
            },
            trace_refs=repair_decision.trace_refs,
        )
        return repair_decision.model_copy(
            update={
                "decision": RepairDecisionType.REPAIR_BLOCKED,
                "reasons": reasons,
                "can_continue": False,
                "instructions": [],
                "trace_refs": [*repair_decision.trace_refs, event.id],
            }
        )

    @staticmethod
    def _accepted_controlled_capability_count(results: list[dict[str, Any]]) -> int:
        return sum(1 for item in results if item.get("accepted") is True)

    @staticmethod
    def _raw_tool_call_payloads(user_input: dict[str, Any], *, limit: int) -> tuple[list[str], int]:
        raw_value = user_input.get("tool_calls", user_input.get("tool_call"))
        if raw_value is None:
            return [], 0
        items = raw_value if isinstance(raw_value, list) else [raw_value]
        requested_count = len(items)
        payloads: list[str] = []
        for item in items[: max(0, limit)]:
            if isinstance(item, str):
                payloads.append(item)
            elif isinstance(item, dict):
                payloads.append(json.dumps(item, sort_keys=True, default=str, separators=(",", ":")))
            else:
                payloads.append(str(item))
        return payloads, requested_count

    def _controlled_capture_root(self, envelope: MissionAuthorityEnvelope) -> Path:
        for allowed_root in envelope.allowed_paths or []:
            normalized = PurePosixPath(str(allowed_root).replace("\\", "/"))
            if normalized.is_absolute() or ".." in normalized.parts or "*" in normalized.parts:
                continue
            if normalized.as_posix().rstrip("/") == "data/generated_projects":
                capture_root = (self.project_root / normalized / mission_slug(envelope.mission_title)).resolve()
                capture_root.relative_to(self.project_root)
                return capture_root
        raise ValueError("Controlled local capability capture requires data/generated_projects in mission allowed_paths.")

    def _certify_trace(self, event_bus: EventBus):
        return self.certification_gate.certify(event_bus.events())

    def _snapshot_trace(self, event_bus: EventBus):
        return self.trace_replayer.replay(event_bus.events()).snapshot
