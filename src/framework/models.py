"""
Core data models for the Agent Orchestration Framework.

These models are shared across all agents, the orchestrator, and the CLI.
They intentionally contain no framework-specific logic — only data contracts.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Status enumerations
# ---------------------------------------------------------------------------

class StepStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    skipped = "skipped"
    failed = "failed"


class ArtifactStatus(str, Enum):
    pending = "pending"
    produced = "produced"
    failed = "failed"


class RunStatus(str, Enum):
    running = "running"
    completed = "completed"
    failed = "failed"
    paused = "paused"


# ---------------------------------------------------------------------------
# Flow definition
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AgentDefinition:
    """Static description of one agent role in the framework."""
    agent_id: str
    agent_file: str        # relative to docs/agents/, e.g. "business-analyst.md"
    raci_role_id: str      # role identifier as it appears in SOP RACI, e.g. "Business Analyst"


@dataclass(frozen=True)
class FlowStep:
    """One step in a multi-agent flow."""
    step_id: str
    agent_id: str          # must match an AgentDefinition.agent_id
    sop_filename: str      # e.g. "01_vision_och_malbild.md"
    artifact_name: str     # human-readable artifact name, e.g. "Vision & målbild"
    output_filename: str   # output file name, e.g. "vision_och_malbild.md"
    input_filenames: list[str]  # required input files for this step
    delprocess_title: str = ""  # subprocess display name, e.g. "Affärsmål och värdebild"


@dataclass(frozen=True)
class ProcessFlow:
    """A process-driven flow resolved from docs/processes/."""
    flow_id: str
    process_file: str
    process_title: str
    steps: list[FlowStep]


# ---------------------------------------------------------------------------
# Runtime state
# ---------------------------------------------------------------------------

@dataclass
class ArtifactRecord:
    """Tracks one artifact's status within a run."""
    name: str
    filename: str
    producer_step_id: str
    status: ArtifactStatus = ArtifactStatus.pending


@dataclass
class RunState:
    """Tracks the overall state of an orchestrator run."""
    run_id: str
    flow_id: str
    status: RunStatus = RunStatus.running
    current_step_id: str | None = None
    step_statuses: dict[str, str] = field(default_factory=dict)  # step_id -> StepStatus.value


@dataclass
class ArtifactState:
    """Tracks all artifact records for a run."""
    run_id: str
    artifacts: dict[str, ArtifactRecord] = field(default_factory=dict)  # filename -> record


@dataclass
class AgentMemory:
    """Lightweight per-agent, per-run working memory."""
    agent_id: str
    run_id: str
    entries: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Step execution result
# ---------------------------------------------------------------------------

@dataclass
class StepResult:
    """Result of running one orchestrator step."""
    step_id: str
    agent_id: str
    artifact_name: str
    status: StepStatus
    output_path: Path | None = None
    skipped_reason: str | None = None
    error: str | None = None
    delprocess_title: str = ""
