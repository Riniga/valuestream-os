"""
Business Analyst agent.

Delegates LLM execution to the shared MAF adapter (src.framework.maf_adapter).
The existing BusinessAnalystFlow and CLI continue to work unchanged — this class
is still instantiated with the same interface as before.
"""
from __future__ import annotations

from src.framework.maf_adapter import AgentRunner


class BusinessAnalystAgent:

    def __init__(self, instructions: str, model: str | None = None) -> None:
        self._runner = AgentRunner(name="BusinessAnalyst", instructions=instructions)

    def run(self, prompt: str) -> str:
        return self._runner.run(prompt)

    @property
    def backend(self) -> str:
        return "maf"
