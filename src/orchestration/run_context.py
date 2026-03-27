from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class RunContext:
    """File-backed context for one orchestration run."""

    run_id: str
    runs_root: Path

    @classmethod
    def from_repo_root(cls, run_id: str, repo_root: Path) -> "RunContext":
        return cls(run_id=run_id, runs_root=repo_root / "runs")

    @property
    def run_path(self) -> Path:
        return self.runs_root / self.run_id

    @property
    def input_path(self) -> Path:
        return self.run_path / "input"

    @property
    def work_path(self) -> Path:
        return self.run_path / "work"

    @property
    def output_path(self) -> Path:
        return self.run_path / "output"

    @property
    def logs_path(self) -> Path:
        return self.run_path / "logs"

    @property
    def state_path(self) -> Path:
        return self.work_path / "state.json"

    @property
    def lineage_path(self) -> Path:
        return self.work_path / "lineage.json"

    def initialize(self) -> dict[str, Any]:
        """Ensure folder contract exists and initialize state file."""
        self.input_path.mkdir(parents=True, exist_ok=True)
        self.work_path.mkdir(parents=True, exist_ok=True)
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)

        if self.state_path.exists():
            return self.load_state()

        initial_state = self._build_initial_state()
        self.save_state(initial_state)
        return initial_state

    def _build_initial_state(self) -> dict[str, Any]:
        timestamp = _utc_timestamp()
        return {
            "run_id": self.run_id,
            "status": "initialized",
            "created_at": timestamp,
            "updated_at": timestamp,
        }

    def load_state(self) -> dict[str, Any]:
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def save_state(self, state: dict[str, Any]) -> None:
        state_to_save = dict(state)
        state_to_save["run_id"] = self.run_id
        state_to_save["updated_at"] = _utc_timestamp()
        if "created_at" not in state_to_save:
            state_to_save["created_at"] = state_to_save["updated_at"]

        serialized = json.dumps(state_to_save, indent=2, sort_keys=True)
        self.state_path.write_text(f"{serialized}\n", encoding="utf-8")

    def load_lineage(self) -> dict[str, Any]:
        if not self.lineage_path.exists():
            return {}
        return json.loads(self.lineage_path.read_text(encoding="utf-8"))

    def save_lineage(self, lineage: dict[str, Any]) -> None:
        serialized = json.dumps(lineage, indent=2, sort_keys=True)
        self.lineage_path.write_text(f"{serialized}\n", encoding="utf-8")

    def record_lineage(
        self,
        *,
        artifact_id: str,
        artifact_path: Path,
        source_files: tuple[Path, ...],
        produced_by: str,
    ) -> None:
        lineage = self.load_lineage()
        normalized_source_files = sorted(
            {self._to_run_relative_path(source_file) for source_file in source_files}
        )
        lineage[artifact_id] = {
            "artifact_id": artifact_id,
            "artifact_path": self._to_run_relative_path(artifact_path),
            "source_files": normalized_source_files,
            "produced_by": produced_by,
            "review_status": str(lineage.get(artifact_id, {}).get("review_status", "pending")),
            "timestamp": _utc_timestamp(),
        }
        self.save_lineage(lineage)

    def update_lineage_review_status(self, *, artifact_id: str, review_status: str) -> None:
        lineage = self.load_lineage()
        if artifact_id not in lineage:
            return
        lineage_entry = dict(lineage[artifact_id])
        lineage_entry["review_status"] = review_status
        lineage_entry["timestamp"] = _utc_timestamp()
        lineage[artifact_id] = lineage_entry
        self.save_lineage(lineage)

    def _to_run_relative_path(self, path: Path) -> str:
        try:
            return path.relative_to(self.run_path).as_posix()
        except ValueError:
            return path.as_posix()

