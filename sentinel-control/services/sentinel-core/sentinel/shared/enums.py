from enum import StrEnum


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Verdict(StrEnum):
    BUILD = "build"
    PIVOT = "pivot"
    NICHE_DOWN = "niche_down"
    KILL = "kill"
    RESEARCH_MORE = "research_more"


class EvidenceType(StrEnum):
    PAIN = "pain"
    WTP = "wtp"
    COMPETITOR_COMPLAINT = "competitor_complaint"
    TREND = "trend"
    PRICING = "pricing"
    COMMUNITY_SIGNAL = "community_signal"
    DIRECT_PROOF = "direct_proof"
    ADJACENT_PROOF = "adjacent_proof"


class ApprovalStatus(StrEnum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    BLOCKED = "blocked"


class TraceEventType(StrEnum):
    RUN_STARTED = "run_started"
    CUEIDEA_IMPORTED = "cueidea_imported"
    EVIDENCE_RECORDED = "evidence_recorded"
    DECISION_CREATED = "decision_created"
    PACK_GENERATED = "pack_generated"
    ACTION_PROPOSED = "action_proposed"
    FIREWALL_REVIEWED = "firewall_reviewed"
    APPROVAL_RECORDED = "approval_recorded"
    ACTION_EXECUTED = "action_executed"
    ASSET_GENERATED = "asset_generated"
    RUN_COMPLETED = "run_completed"
    RUN_FAILED = "run_failed"


class MissionMode(StrEnum):
    SAFE = "safe"
    OPERATOR = "operator"
    POWER = "power"
    AUTONOMOUS = "autonomous"


class MissionType(StrEnum):
    GTM = "gtm"
    RESEARCH_SUMMARY = "research_summary"


class MissionStatus(StrEnum):
    PLANNED = "planned"
    RUNNING = "running"
    PAUSED = "paused"
    ESCALATED = "escalated"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"
    REVOKED = "revoked"


class MissionActionRoute(StrEnum):
    AUTO_EXECUTE = "auto_execute"
    LOG_AND_CONTINUE = "log_and_continue"
    ESCALATE = "escalate"
    BLOCK = "block"


class ReversibilityLevel(StrEnum):
    READ_ONLY = "read_only"
    DRAFT = "draft"
    LOCAL_WRITE_REVERSIBLE = "local_write_reversible"
    STATE_MUTATING_RECOVERABLE = "state_mutating_recoverable"
    IRREVERSIBLE = "irreversible"


class ExternalityLevel(StrEnum):
    INTERNAL_LOCAL = "internal_local"
    INTERNAL_CONNECTED_SYSTEM = "internal_connected_system"
    EXTERNAL_PRIVATE = "external_private"
    EXTERNAL_PUBLIC = "external_public"


class SensitivityLevel(StrEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    PERSONAL = "personal"
    SECRET = "secret"
    FINANCIAL = "financial"
    IDENTITY = "identity"


class ConfidenceLevel(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class EscalationOption(StrEnum):
    APPROVE_ONCE = "approve_once"
    ALLOW_FOR_MISSION = "allow_for_this_mission"
    DENY = "deny"
    TAKE_OVER = "take_over"


class MissionTraceEventType(StrEnum):
    MISSION_CREATED = "mission_created"
    MISSION_STARTED = "mission_started"
    MISSION_PAUSED = "mission_paused"
    MISSION_RESUMED = "mission_resumed"
    MISSION_STOPPED = "mission_stopped"
    MISSION_REVOKED = "mission_revoked"
    MISSION_COMPLETED = "mission_completed"
    MISSION_FAILED = "mission_failed"
    ACTION_PLANNED = "action_planned"
    ACTION_ROUTED = "action_routed"
    RISK_ROUTE_DECIDED = "risk_route_decided"
    ACTION_EXECUTED = "action_executed"
    ACTION_RECEIPT_RECORDED = "action_receipt_recorded"
    ACTION_ESCALATED = "action_escalated"
    ACTION_BLOCKED = "action_blocked"
    USER_APPROVED_ONCE = "user_approved_once"
    USER_ALLOWED_FOR_MISSION = "user_allowed_for_mission"
    USER_DENIED = "user_denied"
    USER_TAKEOVER = "user_takeover"
    BUDGET_WARNING = "budget_warning"
    BUDGET_EXCEEDED = "budget_exceeded"
    ROLLBACK_AVAILABLE = "rollback_available"
    ROLLBACK_EXECUTED = "rollback_executed"
    REVIEW_EXECUTED = "review_executed"
    ARTIFACT_INDEX_WRITTEN = "artifact_index_written"

