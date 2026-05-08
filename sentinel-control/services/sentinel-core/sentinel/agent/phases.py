from enum import StrEnum


class AgentPhase(StrEnum):
    CREATED = "created"
    INITIALIZED = "initialized"
    CONTEXT_BUILDING = "context_building"
    ORIENTING = "orienting"
    METHOD_SELECTING = "method_selecting"
    CAPABILITY_SELECTING = "capability_selecting"
    TOOL_SELECTING = "tool_selecting"
    HYPOTHESIS_VERIFYING = "hypothesis_verifying"
    ACTION_SCORING = "action_scoring"
    EFFORT_ROUTING = "effort_routing"
    PLANNING = "planning"
    PLAN_REVIEWING = "plan_reviewing"
    EXECUTING = "executing"
    ARTIFACT_REVIEWING = "artifact_reviewing"
    REPAIRING = "repairing"
    SUCCESS_EVALUATING = "success_evaluating"
    LEARNING_PROPOSING = "learning_proposing"
    COMPLETED = "completed"
    ESCALATED = "escalated"
    PAUSED = "paused"
    STOPPED = "stopped"
    REVOKED = "revoked"
    BLOCKED = "blocked"
    FAILED = "failed"


ALLOWED_PHASE_TRANSITIONS: dict[AgentPhase, frozenset[AgentPhase]] = {
    AgentPhase.CREATED: frozenset({AgentPhase.INITIALIZED, AgentPhase.STOPPED, AgentPhase.BLOCKED}),
    AgentPhase.INITIALIZED: frozenset({AgentPhase.CONTEXT_BUILDING, AgentPhase.REVOKED, AgentPhase.STOPPED, AgentPhase.BLOCKED, AgentPhase.FAILED}),
    AgentPhase.CONTEXT_BUILDING: frozenset({AgentPhase.ORIENTING, AgentPhase.REVOKED, AgentPhase.STOPPED, AgentPhase.BLOCKED, AgentPhase.FAILED}),
    AgentPhase.ORIENTING: frozenset({AgentPhase.METHOD_SELECTING, AgentPhase.PAUSED, AgentPhase.STOPPED, AgentPhase.BLOCKED, AgentPhase.FAILED}),
    AgentPhase.METHOD_SELECTING: frozenset({AgentPhase.CAPABILITY_SELECTING, AgentPhase.PAUSED, AgentPhase.STOPPED, AgentPhase.BLOCKED, AgentPhase.FAILED}),
    AgentPhase.CAPABILITY_SELECTING: frozenset({AgentPhase.TOOL_SELECTING, AgentPhase.PAUSED, AgentPhase.STOPPED, AgentPhase.BLOCKED, AgentPhase.FAILED}),
    AgentPhase.TOOL_SELECTING: frozenset({AgentPhase.HYPOTHESIS_VERIFYING, AgentPhase.LEARNING_PROPOSING, AgentPhase.PAUSED, AgentPhase.STOPPED, AgentPhase.BLOCKED, AgentPhase.FAILED}),
    AgentPhase.HYPOTHESIS_VERIFYING: frozenset({AgentPhase.ACTION_SCORING, AgentPhase.LEARNING_PROPOSING, AgentPhase.PAUSED, AgentPhase.STOPPED, AgentPhase.BLOCKED, AgentPhase.FAILED}),
    AgentPhase.ACTION_SCORING: frozenset({AgentPhase.EFFORT_ROUTING, AgentPhase.LEARNING_PROPOSING, AgentPhase.PAUSED, AgentPhase.STOPPED, AgentPhase.BLOCKED, AgentPhase.FAILED}),
    AgentPhase.EFFORT_ROUTING: frozenset({AgentPhase.PLANNING, AgentPhase.LEARNING_PROPOSING, AgentPhase.PAUSED, AgentPhase.STOPPED, AgentPhase.BLOCKED, AgentPhase.FAILED}),
    AgentPhase.PLANNING: frozenset({AgentPhase.PLAN_REVIEWING, AgentPhase.LEARNING_PROPOSING, AgentPhase.PAUSED, AgentPhase.STOPPED, AgentPhase.BLOCKED, AgentPhase.FAILED}),
    AgentPhase.PLAN_REVIEWING: frozenset({AgentPhase.EXECUTING, AgentPhase.LEARNING_PROPOSING, AgentPhase.PAUSED, AgentPhase.STOPPED, AgentPhase.BLOCKED, AgentPhase.FAILED}),
    AgentPhase.EXECUTING: frozenset({AgentPhase.ARTIFACT_REVIEWING, AgentPhase.LEARNING_PROPOSING, AgentPhase.ESCALATED, AgentPhase.PAUSED, AgentPhase.STOPPED, AgentPhase.BLOCKED, AgentPhase.FAILED}),
    AgentPhase.ARTIFACT_REVIEWING: frozenset({AgentPhase.SUCCESS_EVALUATING, AgentPhase.REPAIRING, AgentPhase.ESCALATED, AgentPhase.PAUSED, AgentPhase.STOPPED, AgentPhase.BLOCKED, AgentPhase.FAILED}),
    AgentPhase.REPAIRING: frozenset({AgentPhase.EXECUTING, AgentPhase.SUCCESS_EVALUATING, AgentPhase.PAUSED, AgentPhase.STOPPED, AgentPhase.BLOCKED, AgentPhase.FAILED}),
    AgentPhase.SUCCESS_EVALUATING: frozenset({AgentPhase.LEARNING_PROPOSING, AgentPhase.REPAIRING, AgentPhase.PAUSED, AgentPhase.STOPPED, AgentPhase.BLOCKED, AgentPhase.FAILED}),
    AgentPhase.LEARNING_PROPOSING: frozenset({AgentPhase.COMPLETED, AgentPhase.ESCALATED, AgentPhase.STOPPED, AgentPhase.BLOCKED, AgentPhase.FAILED}),
}


ABSORBING_PHASES = {
    AgentPhase.COMPLETED,
    AgentPhase.ESCALATED,
    AgentPhase.PAUSED,
    AgentPhase.STOPPED,
    AgentPhase.REVOKED,
    AgentPhase.BLOCKED,
    AgentPhase.FAILED,
}


def can_transition(phase: AgentPhase, next_phase: AgentPhase) -> bool:
    if phase == next_phase:
        return True
    if phase in ABSORBING_PHASES:
        return False
    return next_phase in ALLOWED_PHASE_TRANSITIONS.get(phase, frozenset())
