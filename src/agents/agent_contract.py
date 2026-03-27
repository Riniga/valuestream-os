from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Protocol

from src.orchestration.run_context import RunContext


@dataclass(frozen=True)
class AgentArtifactOutput:
    """Metadata for one producer artifact written by an agent."""

    artifact_id: str
    artifact_path: Path
    produced_by: str
    source_artifact_ids: tuple[str, ...]
    required_headings: tuple[str, ...]


class ProducerAgent(Protocol):
    """Minimal contract for deterministic SOP-step producers."""

    producer_name: str

    def produce(
        self,
        input_artifacts: Mapping[str, Path],
        context: RunContext,
    ) -> AgentArtifactOutput:
        """Read input artifacts and write one output artifact to work/."""
