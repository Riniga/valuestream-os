from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path


def _normalize_artifact_id(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_only.lower()
    cleaned = re.sub(r"[^a-z0-9]+", "_", lowered).strip("_")
    return cleaned


def _parse_artifact_section(lines: list[str], heading: str) -> list[str]:
    marker = f"## {heading}"
    start_index = -1
    for index, line in enumerate(lines):
        if line.strip() == marker:
            start_index = index + 1
            break

    if start_index == -1:
        return []

    items: list[str] = []
    for line in lines[start_index:]:
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        if not stripped.startswith("- "):
            continue
        artifact_name = stripped[2:].strip()
        if artifact_name:
            items.append(artifact_name)

    return items


def _parse_context_value(lines: list[str], label: str) -> str | None:
    marker = "## 2. Kontext"
    start_index = -1
    for index, line in enumerate(lines):
        if line.strip() == marker:
            start_index = index + 1
            break

    if start_index == -1:
        return None

    for line in lines[start_index:]:
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        match = re.match(rf"-\s*{re.escape(label)}\s*:\s*(.+)$", stripped)
        if match:
            return match.group(1).strip()

    return None


@dataclass(frozen=True)
class KravstallningStep:
    step_id: str
    sop_path: Path
    input_artifact_ids: tuple[str, ...]
    output_artifact_ids: tuple[str, ...]


@dataclass(frozen=True)
class OutputArtifactTarget:
    artifact_id: str
    work_path: Path
    output_path: Path


class ArtifactRegistry:
    """Maps Kravstallning SOP inputs/outputs to file-backed artifact IDs."""

    def __init__(self, steps: list[KravstallningStep]) -> None:
        self._steps = steps

    @classmethod
    def from_repo_root(cls, repo_root: Path) -> "ArtifactRegistry":
        docs_root = repo_root / "docs"
        steps = cls._load_kravstallning_steps(docs_root=docs_root)
        return cls(steps=steps)

    @staticmethod
    def _load_kravstallning_steps(docs_root: Path) -> list[KravstallningStep]:
        steps: list[KravstallningStep] = []
        sop_root = docs_root / "SOP"
        for sop_path in sorted(sop_root.glob("**/*.md")):
            if sop_path.name == "sop-conventions-discovery.md":
                continue

            lines = sop_path.read_text(encoding="utf-8").splitlines()
            process_step = _parse_context_value(lines, "Processteg")
            if process_step != "Kravställning":
                continue

            input_names = _parse_artifact_section(lines, "3. Input")
            output_names = _parse_artifact_section(lines, "4. Output")
            delprocess = _parse_context_value(lines, "Delprocess")

            input_ids = tuple(sorted({_normalize_artifact_id(name) for name in input_names if name}))
            output_ids = tuple(
                sorted({_normalize_artifact_id(name) for name in output_names if name})
            )
            step_id = _normalize_artifact_id(delprocess or sop_path.stem)

            steps.append(
                KravstallningStep(
                    step_id=step_id,
                    sop_path=sop_path,
                    input_artifact_ids=input_ids,
                    output_artifact_ids=output_ids,
                )
            )

        return steps

    @property
    def steps(self) -> tuple[KravstallningStep, ...]:
        return tuple(self._steps)

    def discover_input_artifact_ids(self, input_path: Path) -> set[str]:
        discovered: set[str] = set()
        for path in sorted(input_path.glob("*.md")):
            discovered.add(_normalize_artifact_id(path.stem))
        return discovered

    def resolve_next_outputs(
        self, *, input_path: Path, work_path: Path, output_path: Path
    ) -> list[OutputArtifactTarget]:
        available_ids = self.discover_input_artifact_ids(input_path)
        available_ids.update(self._discover_existing_artifact_ids(work_path))
        available_ids.update(self._discover_existing_artifact_ids(output_path))

        targets: list[OutputArtifactTarget] = []
        seen_output_ids: set[str] = set()
        for step in self._steps:
            if not set(step.input_artifact_ids).issubset(available_ids):
                continue
            for artifact_id in step.output_artifact_ids:
                if artifact_id in available_ids or artifact_id in seen_output_ids:
                    continue
                seen_output_ids.add(artifact_id)
                targets.append(
                    OutputArtifactTarget(
                        artifact_id=artifact_id,
                        work_path=work_path / f"{artifact_id}.md",
                        output_path=output_path / f"{artifact_id}.md",
                    )
                )

        return targets

    @staticmethod
    def _discover_existing_artifact_ids(path: Path) -> set[str]:
        if not path.exists():
            return set()
        return {_normalize_artifact_id(file_path.stem) for file_path in path.glob("*.md")}
