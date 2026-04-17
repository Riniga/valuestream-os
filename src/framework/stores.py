"""
File-based state stores for the Agent Orchestration Framework.

All state is kept as transparent, human-readable JSON files under runs/<run-id>/
so that runs are easy to inspect, debug, and replay.

Files written:
  runs/<run-id>/run_state.json          — overall run progress
  runs/<run-id>/artifact_state.json     — status of each artifact
  runs/<run-id>/agent_memory_<id>.json  — per-agent working memory
  runs/<run-id>/consultation_requests.json  — consultation requests per artifact/step
  runs/<run-id>/consultation_responses.json — consultation responses per artifact/step
  runs/<run-id>/approval_decisions.json     — approval decisions and requested changes
  runs/<run-id>/informed_role_briefs.json   — role-specific informing briefs
  runs/<run-id>/expert_context.json         — run-scoped expert context per agent/artifact
  runs/<run-id>/run_log.json            — chronological event log
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.framework.models import (
    ApprovalDecision,
    AgentMemory,
    ActorKind,
    ConsultationRequest,
    ConsultationResponse,
    ArtifactRecord,
    ArtifactState,
    ArtifactStatus,
    ExpertContext,
    HumanTask,
    HumanTaskStatus,
    InformedRoleBrief,
    RunState,
    RunStatus,
    StepStatus,
)


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _read_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# RunStateStore
# ---------------------------------------------------------------------------

class RunStateStore:
    """Persists and loads the RunState for a given run."""

    _FILENAME = "run_state.json"

    def __init__(self, run_dir: Path) -> None:
        self._path = run_dir / self._FILENAME

    def load(self) -> RunState | None:
        data = _read_json(self._path)
        if data is None:
            return None
        return RunState(
            run_id=data["run_id"],
            flow_id=data["flow_id"],
            process_file=data.get("process_file", ""),
            status=RunStatus(data["status"]),
            current_step_id=data.get("current_step_id"),
            current_phase=data.get("current_phase"),
            pending_human_task_id=data.get("pending_human_task_id"),
            step_statuses=data.get("step_statuses", {}),
        )

    def save(self, state: RunState) -> None:
        _write_json(
            self._path,
            {
                "run_id": state.run_id,
                "flow_id": state.flow_id,
                "process_file": state.process_file,
                "status": state.status.value,
                "current_step_id": state.current_step_id,
                "current_phase": state.current_phase,
                "pending_human_task_id": state.pending_human_task_id,
                "step_statuses": state.step_statuses,
                "updated_at": _now_iso(),
            },
        )

    def initialize(self, run_id: str, flow_id: str, step_ids: list[str], process_file: str = "") -> RunState:
        state = RunState(
            run_id=run_id,
            flow_id=flow_id,
            process_file=process_file,
            status=RunStatus.running,
            step_statuses={s: StepStatus.pending.value for s in step_ids},
        )
        self.save(state)
        return state


# ---------------------------------------------------------------------------
# ArtifactStateStore
# ---------------------------------------------------------------------------

class ArtifactStateStore:
    """Persists and loads the ArtifactState for a given run."""

    _FILENAME = "artifact_state.json"

    def __init__(self, run_dir: Path) -> None:
        self._path = run_dir / self._FILENAME

    def load(self) -> ArtifactState | None:
        data = _read_json(self._path)
        if data is None:
            return None
        artifacts = {
            filename: ArtifactRecord(
                name=rec["name"],
                filename=rec["filename"],
                producer_step_id=rec["producer_step_id"],
                status=ArtifactStatus(rec["status"]),
                agent_actor_kind=ActorKind(rec.get("agent_actor_kind", ActorKind.automated.value)),
                consult_agent_ids=rec.get("consult_agent_ids", []),
                consult_actor_kinds={
                    agent_id: ActorKind(kind)
                    for agent_id, kind in rec.get("consult_actor_kinds", {}).items()
                },
                approver_agent_id=rec.get("approver_agent_id"),
                approver_actor_kind=(
                    ActorKind(rec["approver_actor_kind"])
                    if rec.get("approver_actor_kind") is not None
                    else None
                ),
                informed_agent_ids=rec.get("informed_agent_ids", []),
                informed_actor_kinds={
                    agent_id: ActorKind(kind)
                    for agent_id, kind in rec.get("informed_actor_kinds", {}).items()
                },
                latest_phase=rec.get("latest_phase"),
                approval_decision=rec.get("approval_decision"),
                pending_human_task_id=rec.get("pending_human_task_id"),
                pending_human_phase=rec.get("pending_human_phase"),
            )
            for filename, rec in data.get("artifacts", {}).items()
        }
        return ArtifactState(run_id=data["run_id"], artifacts=artifacts)

    def save(self, state: ArtifactState) -> None:
        _write_json(
            self._path,
            {
                "run_id": state.run_id,
                "artifacts": {
                    filename: {
                        "name": rec.name,
                        "filename": rec.filename,
                        "producer_step_id": rec.producer_step_id,
                        "status": rec.status.value,
                        "agent_actor_kind": rec.agent_actor_kind.value,
                        "consult_agent_ids": rec.consult_agent_ids,
                        "consult_actor_kinds": {
                            agent_id: kind.value for agent_id, kind in rec.consult_actor_kinds.items()
                        },
                        "approver_agent_id": rec.approver_agent_id,
                        "approver_actor_kind": (
                            rec.approver_actor_kind.value if rec.approver_actor_kind is not None else None
                        ),
                        "informed_agent_ids": rec.informed_agent_ids,
                        "informed_actor_kinds": {
                            agent_id: kind.value for agent_id, kind in rec.informed_actor_kinds.items()
                        },
                        "latest_phase": rec.latest_phase,
                        "approval_decision": rec.approval_decision,
                        "pending_human_task_id": rec.pending_human_task_id,
                        "pending_human_phase": rec.pending_human_phase,
                    }
                    for filename, rec in state.artifacts.items()
                },
                "updated_at": _now_iso(),
            },
        )

    def initialize(self, run_id: str) -> ArtifactState:
        state = ArtifactState(run_id=run_id)
        self.save(state)
        return state

    def record_produced(
        self, state: ArtifactState, filename: str, name: str, step_id: str
    ) -> ArtifactState:
        return self.record_status(state, filename, name, step_id, ArtifactStatus.produced)

    def record_failed(
        self, state: ArtifactState, filename: str, name: str, step_id: str
    ) -> ArtifactState:
        return self.record_status(state, filename, name, step_id, ArtifactStatus.failed)

    def record_status(
        self,
        state: ArtifactState,
        filename: str,
        name: str,
        step_id: str,
        status: ArtifactStatus,
        *,
        agent_actor_kind: ActorKind | None = None,
        consult_agent_ids: list[str] | None = None,
        consult_actor_kinds: dict[str, ActorKind] | None = None,
        approver_agent_id: str | None = None,
        approver_actor_kind: ActorKind | None = None,
        informed_agent_ids: list[str] | None = None,
        informed_actor_kinds: dict[str, ActorKind] | None = None,
        latest_phase: str | None = None,
        approval_decision: str | None = None,
        pending_human_task_id: str | None = None,
        pending_human_phase: str | None = None,
    ) -> ArtifactState:
        existing = state.artifacts.get(filename)
        state.artifacts[filename] = ArtifactRecord(
            name=name,
            filename=filename,
            producer_step_id=step_id,
            status=status,
            agent_actor_kind=agent_actor_kind if agent_actor_kind is not None else (
                existing.agent_actor_kind if existing else ActorKind.automated
            ),
            consult_agent_ids=consult_agent_ids if consult_agent_ids is not None else (
                existing.consult_agent_ids if existing else []
            ),
            consult_actor_kinds=consult_actor_kinds if consult_actor_kinds is not None else (
                existing.consult_actor_kinds if existing else {}
            ),
            approver_agent_id=approver_agent_id if approver_agent_id is not None else (
                existing.approver_agent_id if existing else None
            ),
            approver_actor_kind=approver_actor_kind if approver_actor_kind is not None else (
                existing.approver_actor_kind if existing else None
            ),
            informed_agent_ids=informed_agent_ids if informed_agent_ids is not None else (
                existing.informed_agent_ids if existing else []
            ),
            informed_actor_kinds=informed_actor_kinds if informed_actor_kinds is not None else (
                existing.informed_actor_kinds if existing else {}
            ),
            latest_phase=latest_phase if latest_phase is not None else (
                existing.latest_phase if existing else None
            ),
            approval_decision=approval_decision if approval_decision is not None else (
                existing.approval_decision if existing else None
            ),
            pending_human_task_id=pending_human_task_id if pending_human_task_id is not None else (
                existing.pending_human_task_id if existing else None
            ),
            pending_human_phase=pending_human_phase if pending_human_phase is not None else (
                existing.pending_human_phase if existing else None
            ),
        )
        self.save(state)
        return state


# ---------------------------------------------------------------------------
# AgentMemoryStore
# ---------------------------------------------------------------------------

class AgentMemoryStore:
    """Persists and loads per-agent working memory for a run."""

    def __init__(self, run_dir: Path) -> None:
        self._run_dir = run_dir

    def _path(self, agent_id: str) -> Path:
        safe = agent_id.replace("/", "_").replace(" ", "_")
        return self._run_dir / f"agent_memory_{safe}.json"

    def load(self, agent_id: str, run_id: str) -> AgentMemory:
        data = _read_json(self._path(agent_id))
        if data is None:
            return AgentMemory(agent_id=agent_id, run_id=run_id)
        return AgentMemory(
            agent_id=data["agent_id"],
            run_id=data["run_id"],
            entries=data.get("entries", {}),
        )

    def save(self, memory: AgentMemory) -> None:
        _write_json(
            self._path(memory.agent_id),
            {
                "agent_id": memory.agent_id,
                "run_id": memory.run_id,
                "entries": memory.entries,
                "updated_at": _now_iso(),
            },
        )

    def set_entry(self, memory: AgentMemory, key: str, value: Any) -> AgentMemory:
        memory.entries[key] = value
        self.save(memory)
        return memory


# ---------------------------------------------------------------------------
# ConsultationStore
# ---------------------------------------------------------------------------

class ConsultationStore:
    """Persists consultation requests and responses for a run."""

    _REQUESTS_FILENAME = "consultation_requests.json"
    _RESPONSES_FILENAME = "consultation_responses.json"

    def __init__(self, run_dir: Path) -> None:
        self._requests_path = run_dir / self._REQUESTS_FILENAME
        self._responses_path = run_dir / self._RESPONSES_FILENAME

    def append_request(self, request: ConsultationRequest) -> None:
        items: list[dict[str, Any]] = _read_json(self._requests_path) or []
        items.append(
            {
                "request_id": request.request_id,
                "step_id": request.step_id,
                "artifact_name": request.artifact_name,
                "artifact_filename": request.artifact_filename,
                "requester_agent_id": request.requester_agent_id,
                "consultant_agent_ids": request.consultant_agent_ids,
                "questions": request.questions,
                "draft_summary": request.draft_summary,
                "created_at": _now_iso(),
            }
        )
        _write_json(self._requests_path, items)

    def append_response(self, response: ConsultationResponse) -> None:
        items: list[dict[str, Any]] = _read_json(self._responses_path) or []
        items.append(
            {
                "request_id": response.request_id,
                "step_id": response.step_id,
                "artifact_name": response.artifact_name,
                "consultant_agent_id": response.consultant_agent_id,
                "response_text": response.response_text,
                "summary": response.summary,
                "created_at": _now_iso(),
            }
        )
        _write_json(self._responses_path, items)

    def load_requests(self) -> list[ConsultationRequest]:
        items = _read_json(self._requests_path) or []
        return [
            ConsultationRequest(
                request_id=item["request_id"],
                step_id=item["step_id"],
                artifact_name=item["artifact_name"],
                artifact_filename=item["artifact_filename"],
                requester_agent_id=item["requester_agent_id"],
                consultant_agent_ids=item.get("consultant_agent_ids", []),
                questions=item.get("questions", []),
                draft_summary=item.get("draft_summary", ""),
            )
            for item in items
        ]

    def load_responses(self) -> list[ConsultationResponse]:
        items = _read_json(self._responses_path) or []
        return [
            ConsultationResponse(
                request_id=item["request_id"],
                step_id=item["step_id"],
                artifact_name=item["artifact_name"],
                consultant_agent_id=item["consultant_agent_id"],
                response_text=item["response_text"],
                summary=item.get("summary", ""),
            )
            for item in items
        ]

    def load_responses_for_step(self, step_id: str) -> list[ConsultationResponse]:
        return [item for item in self.load_responses() if item.step_id == step_id]


# ---------------------------------------------------------------------------
# ApprovalStore
# ---------------------------------------------------------------------------

class ApprovalStore:
    """Persists approval decisions for a run."""

    _FILENAME = "approval_decisions.json"

    def __init__(self, run_dir: Path) -> None:
        self._path = run_dir / self._FILENAME

    def append(self, decision: ApprovalDecision) -> None:
        items: list[dict[str, Any]] = _read_json(self._path) or []
        items.append(
            {
                "step_id": decision.step_id,
                "artifact_name": decision.artifact_name,
                "artifact_filename": decision.artifact_filename,
                "approver_agent_id": decision.approver_agent_id,
                "decision": decision.decision,
                "actor_kind": decision.actor_kind.value,
                "summary": decision.summary,
                "rationale": decision.rationale,
                "changes_requested": decision.changes_requested,
                "created_at": _now_iso(),
            }
        )
        _write_json(self._path, items)

    def load(self) -> list[ApprovalDecision]:
        items = _read_json(self._path) or []
        return [
            ApprovalDecision(
                step_id=item["step_id"],
                artifact_name=item["artifact_name"],
                artifact_filename=item["artifact_filename"],
                approver_agent_id=item["approver_agent_id"],
                decision=item["decision"],
                actor_kind=ActorKind(item.get("actor_kind", ActorKind.automated.value)),
                summary=item.get("summary", ""),
                rationale=item.get("rationale", ""),
                changes_requested=item.get("changes_requested", []),
            )
            for item in items
        ]

    def load_for_step(self, step_id: str) -> ApprovalDecision | None:
        decisions = [item for item in self.load() if item.step_id == step_id]
        return decisions[-1] if decisions else None


# ---------------------------------------------------------------------------
# InformedRoleBriefStore
# ---------------------------------------------------------------------------

class InformedRoleBriefStore:
    """Persists role-specific briefs for informed roles."""

    _FILENAME = "informed_role_briefs.json"

    def __init__(self, run_dir: Path) -> None:
        self._path = run_dir / self._FILENAME

    def append(self, brief: InformedRoleBrief) -> None:
        items: list[dict[str, Any]] = _read_json(self._path) or []
        items.append(
            {
                "step_id": brief.step_id,
                "artifact_name": brief.artifact_name,
                "artifact_filename": brief.artifact_filename,
                "role_agent_id": brief.role_agent_id,
                "brief_text": brief.brief_text,
                "actor_kind": brief.actor_kind.value,
                "relevance": brief.relevance,
                "created_at": _now_iso(),
            }
        )
        _write_json(self._path, items)

    def load(self) -> list[InformedRoleBrief]:
        items = _read_json(self._path) or []
        return [
            InformedRoleBrief(
                step_id=item["step_id"],
                artifact_name=item["artifact_name"],
                artifact_filename=item["artifact_filename"],
                role_agent_id=item["role_agent_id"],
                brief_text=item["brief_text"],
                actor_kind=ActorKind(item.get("actor_kind", ActorKind.automated.value)),
                relevance=item.get("relevance", ""),
            )
            for item in items
        ]

    def load_for_step(self, step_id: str) -> list[InformedRoleBrief]:
        return [item for item in self.load() if item.step_id == step_id]


# ---------------------------------------------------------------------------
# ExpertContextStore
# ---------------------------------------------------------------------------

class ExpertContextStore:
    """Persists run-scoped context for consultation agents."""

    _FILENAME = "expert_context.json"

    def __init__(self, run_dir: Path) -> None:
        self._path = run_dir / self._FILENAME

    def save(self, context: ExpertContext) -> None:
        items: dict[str, dict[str, Any]] = _read_json(self._path) or {}
        key = self._build_key(context.agent_id, context.artifact_name)
        items[key] = {
            "agent_id": context.agent_id,
            "run_id": context.run_id,
            "artifact_name": context.artifact_name,
            "context_text": context.context_text,
            "source_filenames": context.source_filenames,
            "updated_at": _now_iso(),
        }
        _write_json(self._path, items)

    def load(self, agent_id: str, run_id: str, artifact_name: str) -> ExpertContext | None:
        items: dict[str, dict[str, Any]] = _read_json(self._path) or {}
        item = items.get(self._build_key(agent_id, artifact_name))
        if item is None:
            return None
        return ExpertContext(
            agent_id=item["agent_id"],
            run_id=item.get("run_id", run_id),
            artifact_name=item["artifact_name"],
            context_text=item.get("context_text", ""),
            source_filenames=item.get("source_filenames", []),
        )

    @staticmethod
    def _build_key(agent_id: str, artifact_name: str) -> str:
        safe_artifact = artifact_name.replace("/", "_")
        return f"{agent_id}::{safe_artifact}"


# ---------------------------------------------------------------------------
# HumanTaskStore
# ---------------------------------------------------------------------------

class HumanTaskStore:
    """Persists human handoff tasks as individual JSON files."""

    _DIRNAME = "human_tasks"

    def __init__(self, run_dir: Path) -> None:
        self._dir = run_dir / self._DIRNAME

    def _path(self, task_id: str) -> Path:
        safe = task_id.replace("/", "_").replace(" ", "_")
        return self._dir / f"{safe}.json"

    def path_for(self, task_id: str) -> Path:
        return self._path(task_id)

    def save(self, task: HumanTask) -> Path:
        path = self._path(task.task_id)
        _write_json(
            path,
            {
                "task_id": task.task_id,
                "step_id": task.step_id,
                "artifact_name": task.artifact_name,
                "artifact_filename": task.artifact_filename,
                "agent_id": task.agent_id,
                "role_name": task.role_name,
                "phase": task.phase,
                "task_kind": task.task_kind,
                "action_required": task.action_required,
                "next_step_hint": task.next_step_hint,
                "status": task.status.value,
                "request_payload": task.request_payload,
                "response_payload": task.response_payload,
                "completion_summary": task.completion_summary,
                "updated_at": _now_iso(),
            },
        )
        return path

    def load(self, task_id: str) -> HumanTask | None:
        data = _read_json(self._path(task_id))
        if data is None:
            return None
        return HumanTask(
            task_id=data["task_id"],
            step_id=data["step_id"],
            artifact_name=data["artifact_name"],
            artifact_filename=data["artifact_filename"],
            agent_id=data["agent_id"],
            role_name=data["role_name"],
            phase=data["phase"],
            task_kind=data.get("task_kind", ""),
            action_required=data.get("action_required", ""),
            next_step_hint=data.get("next_step_hint", ""),
            status=HumanTaskStatus(data.get("status", HumanTaskStatus.pending.value)),
            request_payload=data.get("request_payload", {}),
            response_payload=data.get("response_payload", {}),
            completion_summary=data.get("completion_summary", ""),
        )

    def load_all(self) -> list[HumanTask]:
        if not self._dir.exists():
            return []
        tasks: list[HumanTask] = []
        for path in sorted(self._dir.glob("*.json")):
            data = _read_json(path)
            if data is None:
                continue
            tasks.append(
                HumanTask(
                    task_id=data["task_id"],
                    step_id=data["step_id"],
                    artifact_name=data["artifact_name"],
                    artifact_filename=data["artifact_filename"],
                    agent_id=data["agent_id"],
                    role_name=data["role_name"],
                    phase=data["phase"],
                    task_kind=data.get("task_kind", ""),
                    action_required=data.get("action_required", ""),
                    next_step_hint=data.get("next_step_hint", ""),
                    status=HumanTaskStatus(data.get("status", HumanTaskStatus.pending.value)),
                    request_payload=data.get("request_payload", {}),
                    response_payload=data.get("response_payload", {}),
                    completion_summary=data.get("completion_summary", ""),
                )
            )
        return tasks

    def load_pending(self) -> list[HumanTask]:
        return [task for task in self.load_all() if task.status == HumanTaskStatus.pending]

    def load_for_step_and_phase(self, step_id: str, phase: str, agent_id: str) -> HumanTask | None:
        candidates = [
            task
            for task in self.load_all()
            if task.step_id == step_id and task.phase == phase and task.agent_id == agent_id
        ]
        return candidates[-1] if candidates else None


# ---------------------------------------------------------------------------
# RunLog
# ---------------------------------------------------------------------------

class RunLog:
    """Appends structured log entries to runs/<run-id>/run_log.json."""

    _FILENAME = "run_log.json"

    def __init__(self, run_dir: Path) -> None:
        self._path = run_dir / self._FILENAME

    def append(self, entry: dict[str, Any]) -> None:
        entries: list[dict[str, Any]] = _read_json(self._path) or []
        entries.append({"timestamp": _now_iso(), **entry})
        _write_json(self._path, entries)

    def load(self) -> list[dict[str, Any]]:
        return _read_json(self._path) or []
