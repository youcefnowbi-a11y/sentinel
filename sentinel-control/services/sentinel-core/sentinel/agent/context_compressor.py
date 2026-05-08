from __future__ import annotations

from sentinel.agent.models import AgentContext


class ContextCompressor:
    def compress(self, context: AgentContext) -> AgentContext:
        summary = context.summary
        if len(summary) > 500:
            summary = f"{summary[:497]}..."
        return context.model_copy(update={"summary": summary})
