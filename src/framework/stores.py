"""
File-based state stores for the Agent Orchestration Framework.

All state is kept as transparent, human-readable JSON files under runs/<run-id>/
so that runs are easy to inspect, debug, and replay.

Files written:
  runs/<run-id>/run_state.json          — overall run progress
  runs/<run-id>/artifact_state.json     — status of each artifact
  runs/<run-id>/agent_memory_<id>.json  — per-agent working memory
  runs/<run-id>/run_log.json            — chronological event log
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.framework.models import (
    AgentMemory,
    ArtifactRecord,
    ArtifactState,
    ArtifactStatus,
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
            status=RunStatus(data["status"]),
            current_step_id=data.get("current_step_id"),
            step_statuses=data.get("step_statuses", {}),
        )

    def save(self, state: RunState) -> None:
        _write_json(
            self._path,
            {
                "run_id": state.run_id,
                "flow_id": state.flow_id,
                "status": state.status.value,
                "current_step_id": state.current_step_id,
                "step_statuses": state.step_statuses,
                "updated_at": _now_iso(),
            },
        )

    def initialize(self, run_id: str, flow_id: str, step_ids: list[str]) -> RunState:
        state = RunState(
            run_id=run_id,
            flow_id=flow_id,
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
        state.artifacts[filename] = ArtifactRecord(
            name=name,
            filename=filename,
            producer_step_id=step_id,
            status=ArtifactStatus.produced,
        )
        self.save(state)
        return state

    def record_failed(
        self, state: ArtifactState, filename: str, name: str, step_id: str
    ) -> ArtifactState:
        state.artifacts[filename] = ArtifactRecord(
            name=name,
            filename=filename,
            producer_step_id=step_id,
            status=ArtifactStatus.failed,
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
