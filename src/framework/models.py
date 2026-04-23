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
    paused = "paused"
    completed = "completed"
    skipped = "skipped"
    failed = "failed"


class ArtifactStatus(str, Enum):
    pending = "pending"
    draft = "draft"
    in_consultation = "in_consultation"
    revision_requested = "revision_requested"
    awaiting_approval = "awaiting_approval"
    awaiting_human_input = "awaiting_human_input"
    approved = "approved"
    approved_with_notes = "approved_with_notes"
    rejected = "rejected"
    published_to_informed_roles = "published_to_informed_roles"
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

class ActorKind(str, Enum):
    automated = "automated"
    human = "human"


class HumanTaskStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"

@dataclass(frozen=True)
class AgentDefinition:
    """Static description of one agent role in the framework."""
    agent_id: str
    agent_file: str        # relative to framework/{variant}/agents/, e.g. "business-analyst.md"
    raci_role_id: str      # role identifier as it appears in SOP RACI, e.g. "Business Analyst"
    actor_kind: ActorKind = ActorKind.automated
    display_name: str = ""


@dataclass(frozen=True)
class FlowStep:
    """One step in a multi-agent flow."""
    step_id: str
    agent_id: str          # must match an AgentDefinition.agent_id
    sop_filename: str      # e.g. "01_vision_och_malbild.md"
    artifact_name: str     # human-readable artifact name, e.g. "Vision & målbild"
    output_filename: str   # output file name, e.g. "vision_och_malbild.md"
    input_filenames: list[str]  # required input files for this step
    optional_input_filenames: list[str] = field(default_factory=list)
    delprocess_title: str = ""  # subprocess display name, e.g. "Affärsmål och värdebild"
    agent_actor_kind: ActorKind = ActorKind.automated
    consult_agent_ids: list[str] = field(default_factory=list)
    consult_actor_kinds: dict[str, ActorKind] = field(default_factory=dict)
    approver_agent_id: str | None = None
    approver_actor_kind: ActorKind | None = None
    informed_agent_ids: list[str] = field(default_factory=list)
    informed_actor_kinds: dict[str, ActorKind] = field(default_factory=dict)
    use_raci_workflow: bool = False


@dataclass(frozen=True)
class ProcessFlow:
    """A process-driven flow resolved from the configured framework directory."""
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
    agent_actor_kind: ActorKind = ActorKind.automated
    consult_agent_ids: list[str] = field(default_factory=list)
    consult_actor_kinds: dict[str, ActorKind] = field(default_factory=dict)
    approver_agent_id: str | None = None
    approver_actor_kind: ActorKind | None = None
    informed_agent_ids: list[str] = field(default_factory=list)
    informed_actor_kinds: dict[str, ActorKind] = field(default_factory=dict)
    latest_phase: str | None = None
    approval_decision: str | None = None
    pending_human_task_id: str | None = None
    pending_human_phase: str | None = None


@dataclass
class RunState:
    """Tracks the overall state of an orchestrator run."""
    run_id: str
    flow_id: str
    process_file: str = ""
    status: RunStatus = RunStatus.running
    current_step_id: str | None = None
    current_phase: str | None = None
    pending_human_task_id: str | None = None
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


@dataclass
class ConsultationRequest:
    """Structured request sent from a producing role to consultation roles."""
    request_id: str
    step_id: str
    artifact_name: str
    artifact_filename: str
    requester_agent_id: str
    consultant_agent_ids: list[str] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)
    draft_summary: str = ""


@dataclass
class ConsultationResponse:
    """Structured response from one consultation role."""
    request_id: str
    step_id: str
    artifact_name: str
    consultant_agent_id: str
    response_text: str
    summary: str = ""


@dataclass
class ApprovalDecision:
    """Structured decision made by the accountable role."""
    step_id: str
    artifact_name: str
    artifact_filename: str
    approver_agent_id: str
    decision: str
    actor_kind: ActorKind = ActorKind.automated
    summary: str = ""
    rationale: str = ""
    changes_requested: list[str] = field(default_factory=list)


@dataclass
class InformedRoleBrief:
    """Role-specific summary sent to informed roles."""
    step_id: str
    artifact_name: str
    artifact_filename: str
    role_agent_id: str
    brief_text: str
    actor_kind: ActorKind = ActorKind.automated
    relevance: str = ""


@dataclass
class ExpertContext:
    """Run-scoped context used by consultation agents."""
    agent_id: str
    run_id: str
    artifact_name: str
    context_text: str
    source_filenames: list[str] = field(default_factory=list)


@dataclass
class HumanTask:
    """A file-backed handoff for work that must be completed by a human role."""
    task_id: str
    step_id: str
    artifact_name: str
    artifact_filename: str
    agent_id: str
    role_name: str
    phase: str
    task_kind: str = ""
    action_required: str = ""
    next_step_hint: str = ""
    status: HumanTaskStatus = HumanTaskStatus.pending
    request_payload: dict[str, Any] = field(default_factory=dict)
    response_payload: dict[str, Any] = field(default_factory=dict)
    completion_summary: str = ""


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
    phase: str | None = None
    approval_decision: str | None = None
    human_task_id: str | None = None
    human_task_path: Path | None = None
