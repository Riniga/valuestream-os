"""
UX agent.

Uses the same AgentRunner (MAF adapter) and AgentContextLoader as Business Analyst.
No agent-specific logic lives here — the generalized framework handles everything.
This module exists so the UX agent can be referenced, tested, and extended
independently from the Business Analyst if needed.
"""
from __future__ import annotations

from src.framework.maf_adapter import AgentRunner


class UXAgent:

    def __init__(self, instructions: str) -> None:
        self._runner = AgentRunner(name="UX", instructions=instructions)

    def run(self, prompt: str) -> str:
        return self._runner.run(prompt)

    @property
    def backend(self) -> str:
        return "maf"
