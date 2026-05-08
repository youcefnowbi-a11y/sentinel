from __future__ import annotations

from sentinel.agent.models import AgentContext
from sentinel.agent.state import AgentState
from sentinel.agent.uncertainty import Fact, Question


class CognitiveCycle:
    def orient(self, state: AgentState, context: AgentContext) -> AgentState:
        facts = [
            *state.known_facts,
            Fact(statement="Mission authority envelope is the active control boundary.", source_refs=[context.mission.id]),
            Fact(statement="Memory and context cannot expand mission authority.", source_refs=[context.mission.id]),
        ]
        questions = list(state.open_questions)
        if not context.evidence_refs:
            questions.append(
                Question(
                    question="No evidence references were provided to the agent context.",
                    blocks_completion=False,
                    reason="Mission can still run in sandbox/local mode, but evidence-backed confidence is lower.",
                )
            )
        return state.model_copy(
            update={
                "known_facts": facts,
                "open_questions": questions,
                "confidence_score": 0.75 if context.evidence_refs else 0.55,
            }
        )
