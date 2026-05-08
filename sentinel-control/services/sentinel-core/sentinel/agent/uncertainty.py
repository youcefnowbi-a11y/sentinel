from __future__ import annotations

from pydantic import Field

from sentinel.shared.models import SentinelModel, new_id


class Fact(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("fact"))
    statement: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source_refs: list[str] = Field(default_factory=list)


class Assumption(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("asm"))
    statement: str
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    reason: str | None = None


class Hypothesis(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("hyp"))
    statement: str
    confidence: float = Field(default=0.25, ge=0.0, le=1.0)
    test_needed: str | None = None


class Question(SentinelModel):
    id: str = Field(default_factory=lambda: new_id("q"))
    question: str
    blocks_completion: bool = False
    reason: str | None = None


class UncertaintyState(SentinelModel):
    known: list[Fact] = Field(default_factory=list)
    assumed: list[Assumption] = Field(default_factory=list)
    suspected: list[Hypothesis] = Field(default_factory=list)
    unknown: list[Question] = Field(default_factory=list)

    def has_blocking_questions(self) -> bool:
        return any(question.blocks_completion for question in self.unknown)
