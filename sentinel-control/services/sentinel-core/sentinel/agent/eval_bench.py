from __future__ import annotations

from collections.abc import Callable, Iterable
from enum import StrEnum
from hashlib import sha256
from math import sqrt
from pathlib import Path
from time import perf_counter
from typing import TYPE_CHECKING, Any, Protocol

from pydantic import Field

from sentinel.agent.events import AgentEventType
from sentinel.agent.evidence import EvidenceDecisionType
from sentinel.agent.phases import AgentPhase
from sentinel.mission.models import MissionAuthorityEnvelope
from sentinel.mission.safe_executors import mission_slug
from sentinel.shared.models import SentinelModel

if TYPE_CHECKING:
    from sentinel.agent.models import AgentRunResult


class RuntimeLike(Protocol):
    def run(
        self,
        envelope: MissionAuthorityEnvelope,
        user_input: dict[str, Any] | None = None,
        *,
        evidence_refs: list[str] | None = None,
        memory_items: list[dict[str, Any]] | None = None,
    ) -> "AgentRunResult": ...


class EvalCheckKind(StrEnum):
    F2P = "f2p"
    P2P = "p2p"
    NO_OP = "no_op"
    STABILITY = "stability"


class EvalCheckResult(SentinelModel):
    name: str
    kind: EvalCheckKind
    passed: bool
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class EvalCase(SentinelModel):
    id: str
    name: str
    envelope: MissionAuthorityEnvelope
    user_input: dict[str, Any] = Field(default_factory=dict)
    evidence_refs: list[str] = Field(default_factory=list)
    memory_items: list[dict[str, Any]] = Field(default_factory=list)
    expected_success: bool | None = None
    expected_final_phase: AgentPhase | None = None
    required_artifact_files: list[str] = Field(default_factory=list)
    stable_artifact_files: list[str] = Field(default_factory=list)
    forbidden_artifact_files: list[str] = Field(default_factory=list)
    required_event_types: list[AgentEventType] = Field(default_factory=list)
    forbidden_event_types: list[AgentEventType] = Field(default_factory=list)
    required_selected_tools: list[str] = Field(default_factory=list)
    required_missing_capabilities: list[str] = Field(default_factory=list)
    required_evidence_chain_types: list[EvidenceDecisionType] = Field(default_factory=list)


class EvalRunResult(SentinelModel):
    case_id: str
    iteration: int
    accepted: bool
    success: bool
    final_phase: AgentPhase
    project_path: str | None = None
    trace_hash: str | None = None
    duration_ms: float = Field(default=0.0, ge=0.0)
    event_count: int = 0
    artifact_signature: tuple[Any, ...] = Field(default_factory=tuple)
    signature: tuple[Any, ...] = Field(default_factory=tuple)
    checks: list[EvalCheckResult] = Field(default_factory=list)


class EvalMetricSummary(SentinelModel):
    case_id: str
    run_count: int = Field(ge=0)
    accepted_count: int = Field(ge=0)
    success_count: int = Field(ge=0)
    accepted_rate: float = Field(ge=0.0, le=1.0)
    success_rate: float = Field(ge=0.0, le=1.0)
    accepted_rate_ci95_half_width: float = Field(ge=0.0)
    success_rate_ci95_half_width: float = Field(ge=0.0)
    accepted_rate_ci95_lower: float = Field(default=0.0, ge=0.0, le=1.0)
    accepted_rate_ci95_upper: float = Field(default=0.0, ge=0.0, le=1.0)
    success_rate_ci95_lower: float = Field(default=0.0, ge=0.0, le=1.0)
    success_rate_ci95_upper: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence_interval_method: str = "wilson_score_95"
    event_count_min: int = Field(default=0, ge=0)
    event_count_max: int = Field(default=0, ge=0)
    event_count_mean: float = Field(default=0.0, ge=0.0)
    duration_ms_min: float = Field(default=0.0, ge=0.0)
    duration_ms_max: float = Field(default=0.0, ge=0.0)
    duration_ms_mean: float = Field(default=0.0, ge=0.0)
    duration_ms_p50: float = Field(default=0.0, ge=0.0)
    duration_ms_p95: float = Field(default=0.0, ge=0.0)
    unstable_iterations: list[int] = Field(default_factory=list)


class EvalCaseResult(SentinelModel):
    case_id: str
    name: str
    accepted: bool
    no_op_checks: list[EvalCheckResult] = Field(default_factory=list)
    runs: list[EvalRunResult] = Field(default_factory=list)
    stability_checks: list[EvalCheckResult] = Field(default_factory=list)
    metrics: EvalMetricSummary | None = None


class EvalSuiteResult(SentinelModel):
    accepted: bool
    case_results: list[EvalCaseResult] = Field(default_factory=list)

    @property
    def checks(self) -> list[EvalCheckResult]:
        collected: list[EvalCheckResult] = []
        for case in self.case_results:
            collected.extend(case.no_op_checks)
            collected.extend(case.stability_checks)
            for run in case.runs:
                collected.extend(run.checks)
        return collected


RuntimeFactory = Callable[[Path], RuntimeLike]


class SentinelEvalBench:
    """Production-style mission harness for Sentinel core.

    P1K evaluates complete agent runs with deterministic checks:
    - F2P: the mission outcome that should become true after the run.
    - P2P: invariants that must remain true after the run.
    - no-op: the same artifact contract must not pass before the run.
    - stability: repeated runs must keep the same behavioral signature.
    """

    def __init__(self, *, project_root: str | Path, runtime_factory: RuntimeFactory | None = None) -> None:
        self.project_root = Path(project_root).resolve()
        self.runtime_factory = runtime_factory

    def run_suite(
        self,
        cases: Iterable[EvalCase],
        *,
        iterations: int = 1,
        include_no_op: bool = True,
    ) -> EvalSuiteResult:
        case_results = [
            self.run_case(case, iterations=iterations, include_no_op=include_no_op)
            for case in cases
        ]
        return EvalSuiteResult(
            accepted=all(case.accepted for case in case_results),
            case_results=case_results,
        )

    def run_case(
        self,
        case: EvalCase,
        *,
        iterations: int = 1,
        include_no_op: bool = True,
    ) -> EvalCaseResult:
        if iterations < 1:
            raise ValueError("iterations must be >= 1")

        no_op_checks = self._no_op_checks(case) if include_no_op else []
        runs = [self._run_once(case, iteration) for iteration in range(iterations)]
        stability_checks = self._stability_checks(case, runs) if iterations > 1 else []
        accepted = all(check.passed for check in no_op_checks)
        accepted = accepted and all(run.accepted for run in runs)
        accepted = accepted and all(check.passed for check in stability_checks)
        metrics = self._metric_summary(case, runs)
        return EvalCaseResult(
            case_id=case.id,
            name=case.name,
            accepted=accepted,
            no_op_checks=no_op_checks,
            runs=runs,
            stability_checks=stability_checks,
            metrics=metrics,
        )

    def _run_once(self, case: EvalCase, iteration: int) -> EvalRunResult:
        run_root = self._run_root(case, iteration)
        pre_run_checks = self._pre_run_checks(run_root)
        runtime = self._runtime(run_root)
        started = perf_counter()
        result = runtime.run(
            case.envelope,
            case.user_input,
            evidence_refs=case.evidence_refs,
            memory_items=case.memory_items,
        )
        duration_ms = (perf_counter() - started) * 1000.0
        checks = [
            *pre_run_checks,
            *self._f2p_checks(case, result),
            *self._p2p_checks(case, result, run_root),
        ]
        accepted = all(check.passed for check in checks)
        artifact_signature = self._artifact_signature(case, result)
        trace_hash = result.trace[-1].event_hash if result.trace else None
        return EvalRunResult(
            case_id=case.id,
            iteration=iteration,
            accepted=accepted,
            success=result.success,
            final_phase=result.final_phase,
            project_path=result.project_path,
            trace_hash=trace_hash,
            duration_ms=duration_ms,
            event_count=len(result.trace),
            artifact_signature=artifact_signature,
            signature=self._signature(result, artifact_signature),
            checks=checks,
        )

    def _runtime(self, project_root: Path) -> RuntimeLike:
        if self.runtime_factory:
            return self.runtime_factory(project_root)
        from sentinel.agent.runtime import AgentRuntime

        return AgentRuntime(project_root=project_root)

    def _no_op_checks(self, case: EvalCase) -> list[EvalCheckResult]:
        project_dir = self._expected_project_dir(self._run_root(case, -1), case)
        existing = [filename for filename in case.required_artifact_files if (project_dir / filename).exists()]
        if not case.required_artifact_files:
            return [
                EvalCheckResult(
                    name="no_op_contract_defined",
                    kind=EvalCheckKind.NO_OP,
                    passed=True,
                    message="No required artifact files were declared for the no-op baseline.",
                )
            ]
        return [
            EvalCheckResult(
                name="no_op_required_artifacts_absent",
                kind=EvalCheckKind.NO_OP,
                passed=not existing,
                message="Required artifacts are absent before the runtime executes." if not existing else "No-op baseline already satisfies required artifacts.",
                details={"unexpected_existing_files": existing},
            )
        ]

    @staticmethod
    def _pre_run_checks(run_root: Path) -> list[EvalCheckResult]:
        preexisting_entries: list[str] = []
        if run_root.exists():
            preexisting_entries = sorted(str(path.relative_to(run_root)) for path in run_root.iterdir())
        return [
            EvalCheckResult(
                name="clean_run_root",
                kind=EvalCheckKind.NO_OP,
                passed=not preexisting_entries,
                message="Eval run root is clean before execution." if not preexisting_entries else "Eval run root contains pre-existing files.",
                details={
                    "run_root": str(run_root),
                    "preexisting_count": len(preexisting_entries),
                    "preexisting_entries": preexisting_entries[:20],
                },
            )
        ]

    def _f2p_checks(self, case: EvalCase, result: AgentRunResult) -> list[EvalCheckResult]:
        checks: list[EvalCheckResult] = []
        if case.expected_success is not None:
            checks.append(
                EvalCheckResult(
                    name="expected_success",
                    kind=EvalCheckKind.F2P,
                    passed=result.success is case.expected_success,
                    message=f"Expected success={case.expected_success}, observed success={result.success}.",
                )
            )
        if case.expected_final_phase is not None:
            checks.append(
                EvalCheckResult(
                    name="expected_final_phase",
                    kind=EvalCheckKind.F2P,
                    passed=result.final_phase == case.expected_final_phase,
                    message=f"Expected phase={case.expected_final_phase}, observed phase={result.final_phase}.",
                )
            )

        project_path = Path(result.project_path) if result.project_path else None
        missing_files = [
            filename
            for filename in case.required_artifact_files
            if project_path is None or not (project_path / filename).exists()
        ]
        if case.required_artifact_files:
            checks.append(
                EvalCheckResult(
                    name="required_artifact_files",
                    kind=EvalCheckKind.F2P,
                    passed=not missing_files,
                    message="All required artifact files exist." if not missing_files else "Some required artifact files are missing.",
                    details={"missing_files": missing_files},
                )
            )

        unexpected_files = [
            filename
            for filename in case.forbidden_artifact_files
            if project_path is not None and (project_path / filename).exists()
        ]
        if case.forbidden_artifact_files:
            checks.append(
                EvalCheckResult(
                    name="forbidden_artifact_files",
                    kind=EvalCheckKind.F2P,
                    passed=not unexpected_files,
                    message="No forbidden artifact files were created." if not unexpected_files else "Forbidden artifact files were created.",
                    details={"unexpected_files": unexpected_files},
                )
            )
        return checks

    def _p2p_checks(self, case: EvalCase, result: AgentRunResult, run_root: Path) -> list[EvalCheckResult]:
        event_types = [event.event_type for event in result.trace]
        selected_tools = set(result.selected_tools)
        missing_capabilities = {need.name for need in result.missing_capabilities}
        evidence_chain_types = {chain.decision_type for chain in result.evidence_chains}
        project_path = Path(result.project_path) if result.project_path else None

        checks = [
            EvalCheckResult(
                name="runtime_certification",
                kind=EvalCheckKind.P2P,
                passed=bool(result.runtime_certification and result.runtime_certification.certified),
                message="Runtime certification accepted the trace." if result.runtime_certification and result.runtime_certification.certified else "Runtime certification rejected the trace.",
                details={"errors": result.runtime_certification.errors if result.runtime_certification else ["missing_certification"]},
            ),
            EvalCheckResult(
                name="state_snapshot_replay",
                kind=EvalCheckKind.P2P,
                passed=bool(result.state_snapshot and not result.state_snapshot.errors),
                message="State snapshot replay accepted the trace." if result.state_snapshot and not result.state_snapshot.errors else "State snapshot replay found errors.",
                details={"errors": result.state_snapshot.errors if result.state_snapshot else ["missing_snapshot"]},
            ),
            EvalCheckResult(
                name="trace_sequence",
                kind=EvalCheckKind.P2P,
                passed=all(event.sequence == index and event.logical_time == index for index, event in enumerate(result.trace)),
                message="Trace sequence and logical time are monotonic.",
            ),
            EvalCheckResult(
                name="project_path_scope",
                kind=EvalCheckKind.P2P,
                passed=self._project_path_is_scoped(project_path, run_root),
                message="Project path stays inside the eval run root." if self._project_path_is_scoped(project_path, run_root) else "Project path escaped the eval run root.",
                details={"project_path": str(project_path) if project_path else None, "run_root": str(run_root)},
            ),
        ]

        missing_events = [event.value for event in case.required_event_types if event not in event_types]
        if case.required_event_types:
            checks.append(
                EvalCheckResult(
                    name="required_event_types",
                    kind=EvalCheckKind.P2P,
                    passed=not missing_events,
                    message="All required runtime events are present." if not missing_events else "Required runtime events are missing.",
                    details={"missing_events": missing_events},
                )
            )

        forbidden_events = [event.value for event in case.forbidden_event_types if event in event_types]
        if case.forbidden_event_types:
            checks.append(
                EvalCheckResult(
                    name="forbidden_event_types",
                    kind=EvalCheckKind.P2P,
                    passed=not forbidden_events,
                    message="No forbidden runtime events are present." if not forbidden_events else "Forbidden runtime events are present.",
                    details={"forbidden_events": forbidden_events},
                )
            )

        missing_tools = [tool for tool in case.required_selected_tools if tool not in selected_tools]
        if case.required_selected_tools:
            checks.append(
                EvalCheckResult(
                    name="required_selected_tools",
                    kind=EvalCheckKind.P2P,
                    passed=not missing_tools,
                    message="All required selected tools are present." if not missing_tools else "Some required selected tools are missing.",
                    details={"missing_tools": missing_tools},
                )
            )

        missing_capability_checks = [
            capability
            for capability in case.required_missing_capabilities
            if capability not in missing_capabilities
        ]
        if case.required_missing_capabilities:
            checks.append(
                EvalCheckResult(
                    name="required_missing_capabilities",
                    kind=EvalCheckKind.P2P,
                    passed=not missing_capability_checks,
                    message="Expected unavailable capabilities remain explicit." if not missing_capability_checks else "Expected unavailable capabilities were not reported.",
                    details={"missing_expected_capabilities": missing_capability_checks},
                )
            )

        missing_chains = [
            decision_type.value
            for decision_type in case.required_evidence_chain_types
            if decision_type not in evidence_chain_types
        ]
        if case.required_evidence_chain_types:
            checks.append(
                EvalCheckResult(
                    name="required_evidence_chain_types",
                    kind=EvalCheckKind.P2P,
                    passed=not missing_chains,
                    message="All required evidence chain types are present." if not missing_chains else "Required evidence chains are missing.",
                    details={"missing_evidence_chains": missing_chains},
                )
            )

        return checks

    @staticmethod
    def _stability_checks(case: EvalCase, runs: list[EvalRunResult]) -> list[EvalCheckResult]:
        signatures = [run.signature for run in runs]
        reference = signatures[0] if signatures else tuple()
        unstable_iterations = [
            run.iteration
            for run in runs
            if run.signature != reference
        ]
        return [
            EvalCheckResult(
                name="multi_run_signature_stability",
                kind=EvalCheckKind.STABILITY,
                passed=not unstable_iterations,
                message="Repeated runs produced the same behavioral signature." if not unstable_iterations else "Repeated runs diverged.",
                details={"case_id": case.id, "unstable_iterations": unstable_iterations},
            )
        ]

    @staticmethod
    def _metric_summary(case: EvalCase, runs: list[EvalRunResult]) -> EvalMetricSummary:
        run_count = len(runs)
        accepted_count = sum(1 for run in runs if run.accepted)
        success_count = sum(1 for run in runs if run.success)
        accepted_rate = accepted_count / run_count if run_count else 0.0
        success_rate = success_count / run_count if run_count else 0.0
        accepted_lower, accepted_upper = _binomial_wilson_ci95(accepted_rate, run_count)
        success_lower, success_upper = _binomial_wilson_ci95(success_rate, run_count)
        event_counts = [run.event_count for run in runs]
        durations = [run.duration_ms for run in runs]
        reference_signature = runs[0].signature if runs else tuple()
        unstable_iterations = [
            run.iteration
            for run in runs
            if run.signature != reference_signature
        ]
        return EvalMetricSummary(
            case_id=case.id,
            run_count=run_count,
            accepted_count=accepted_count,
            success_count=success_count,
            accepted_rate=accepted_rate,
            success_rate=success_rate,
            accepted_rate_ci95_half_width=(accepted_upper - accepted_lower) / 2.0,
            success_rate_ci95_half_width=(success_upper - success_lower) / 2.0,
            accepted_rate_ci95_lower=accepted_lower,
            accepted_rate_ci95_upper=accepted_upper,
            success_rate_ci95_lower=success_lower,
            success_rate_ci95_upper=success_upper,
            event_count_min=min(event_counts) if event_counts else 0,
            event_count_max=max(event_counts) if event_counts else 0,
            event_count_mean=(sum(event_counts) / len(event_counts)) if event_counts else 0.0,
            duration_ms_min=min(durations) if durations else 0.0,
            duration_ms_max=max(durations) if durations else 0.0,
            duration_ms_mean=(sum(durations) / len(durations)) if durations else 0.0,
            duration_ms_p50=_percentile(durations, 50),
            duration_ms_p95=_percentile(durations, 95),
            unstable_iterations=unstable_iterations,
        )

    @staticmethod
    def _signature(result: AgentRunResult, artifact_signature: tuple[Any, ...]) -> tuple[Any, ...]:
        return (
            result.success,
            result.final_phase,
            tuple(sorted(method.id for method in result.selected_methods)),
            tuple(sorted(result.selected_tools)),
            tuple(sorted(need.name for need in result.missing_capabilities)),
            tuple(event.event_type for event in result.trace),
            tuple(sorted(chain.decision_type for chain in result.evidence_chains)),
            bool(result.runtime_certification and result.runtime_certification.certified),
            artifact_signature,
        )

    @staticmethod
    def _artifact_signature(case: EvalCase, result: AgentRunResult) -> tuple[Any, ...]:
        project_path = Path(result.project_path) if result.project_path else None
        signature: list[tuple[str, str | None]] = []
        for filename in sorted(case.stable_artifact_files):
            artifact_path = project_path / filename if project_path else None
            if artifact_path is None or not artifact_path.exists() or not artifact_path.is_file():
                signature.append((filename, None))
                continue
            signature.append((filename, sha256(artifact_path.read_bytes()).hexdigest()))
        return tuple(signature)

    def _run_root(self, case: EvalCase, iteration: int) -> Path:
        suffix = "noop" if iteration < 0 else f"run_{iteration}"
        return (self.project_root / "sentinel_eval_runs" / case.id / suffix).resolve()

    @staticmethod
    def _expected_project_dir(run_root: Path, case: EvalCase) -> Path:
        return (run_root / "data" / "generated_projects" / mission_slug(case.envelope.mission_title)).resolve()

    @staticmethod
    def _project_path_is_scoped(project_path: Path | None, run_root: Path) -> bool:
        if project_path is None:
            return True
        try:
            project_path.resolve().relative_to(run_root.resolve())
        except ValueError:
            return False
        return True


def _binomial_ci95_half_width(rate: float, count: int) -> float:
    lower, upper = _binomial_wilson_ci95(rate, count)
    return (upper - lower) / 2.0


def _binomial_wilson_ci95(rate: float, count: int) -> tuple[float, float]:
    if count <= 0:
        return 0.0, 0.0
    z = 1.96
    z2 = z * z
    denominator = 1.0 + (z2 / count)
    center = (rate + (z2 / (2.0 * count))) / denominator
    half_width = (z * sqrt(((rate * (1.0 - rate)) / count) + (z2 / (4.0 * count * count)))) / denominator
    return max(0.0, center - half_width), min(1.0, center + half_width)


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    ordered = sorted(values)
    rank = (percentile / 100.0) * (len(ordered) - 1)
    lower_index = int(rank)
    upper_index = min(lower_index + 1, len(ordered) - 1)
    fraction = rank - lower_index
    return ordered[lower_index] + ((ordered[upper_index] - ordered[lower_index]) * fraction)
