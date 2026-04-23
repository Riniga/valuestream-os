from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from src.capabilities.run_workspace import RunWorkspace
from src.framework.models import RunState
from src.framework.repo_layout import get_framework_root
from src.orchestration.process_loader import ProcessFlowLoader


@dataclass(frozen=True)
class PhaseArtifact:
    artifact_name: str
    filename: str
    delprocess_title: str


@dataclass(frozen=True)
class PhaseCatalog:
    process_file: str
    process_title: str
    artifacts: list[PhaseArtifact]


ROOT_METADATA_FILES: dict[str, str] = {
    "run_state.json": "Övergripande status för runnen och senaste körda process.",
    "artifact_state.json": "Status för huvudartefakter som har producerats i runnen.",
    "run_log.json": "Kronologisk logg över vad som har hänt under körningen.",
    "approval_decisions.json": "Samlad logg över godkännanden och beslut.",
    "consultation_requests.json": "Frågor som skickats ut i konsultationsfasen.",
    "consultation_responses.json": "Svar från konsulterande roller.",
    "expert_context.json": "Run-specifik expertkontext som byggts upp under körningen.",
    "informed_role_briefs.json": "Briefs som skickats till informerade roller.",
}


def publish_output_index(
    *,
    repo_root: Path,
    workspace: RunWorkspace,
    run_state: RunState | None,
) -> Path:
    content = build_output_index_content(
        repo_root=repo_root,
        workspace=workspace,
        run_state=run_state,
    )
    return workspace.write_output("INDEX.md", content)


def build_output_index_content(
    *,
    repo_root: Path,
    workspace: RunWorkspace,
    run_state: RunState | None,
) -> str:
    output_files = sorted(path for path in workspace.output_dir.glob("*") if path.is_file())
    output_names = {path.name for path in output_files}
    phase_catalog = _build_phase_catalog(repo_root)
    primary_filenames = {
        artifact.filename
        for phase in phase_catalog
        for artifact in phase.artifacts
    }
    primary_output_files = sorted(name for name in output_names if name in primary_filenames)
    support_counts = _count_support_files(output_names)
    metadata_lines = _build_metadata_lines(workspace)
    phase_sections = [
        _render_phase_section(phase=phase, output_names=output_names)
        for phase in phase_catalog
    ]
    ungrouped_files = sorted(
        name
        for name in output_names
        if name not in primary_filenames
        and name != "INDEX.md"
        and _classify_support_file(name) == "other"
    )

    run_status = run_state.status.value if run_state is not None else "unknown"
    process_file = run_state.process_file if run_state is not None else ""

    lines = [
        f"# Output Index: {workspace.run_id}",
        "",
        "Denna fil sammanfattar det som har genererats i runnen.",
        "Huvudartefakter publiceras i `output/` och kopieras normalt vidare till `input/` när de ska kunna användas i nästa processsteg.",
        "",
        "## Runsammanfattning",
        "| Fält | Värde |",
        "|------|-------|",
        f"| Run ID | {workspace.run_id} |",
        f"| Status | {run_status} |",
        f"| Senast körd process | {process_file or '-'} |",
        f"| Huvudartefakter i output | {len(primary_output_files)} |",
        f"| Approval-filer | {support_counts['approval']} |",
        f"| Consultation-filer | {support_counts['consultation']} |",
        f"| Brief-filer | {support_counts['brief']} |",
        f"| Övriga output-filer | {len(ungrouped_files)} |",
        "",
        "## Run-metadata",
        *metadata_lines,
        "",
        "## Genererat innehåll per processsteg",
        "",
        *phase_sections,
    ]

    if ungrouped_files:
        lines.extend(
            [
                "## Övriga filer i output",
                "Filer som inte är huvudartefakter eller standardiserade approval/consultation/brief-filer.",
                "",
            ]
        )
        lines.extend(f"- [`{name}`](./{name})" for name in ungrouped_files)
        lines.append("")

    lines.extend(
        [
            "## Att läsa först",
            "- Börja med huvudartefakterna för respektive processsteg.",
            "- Använd metadatafilerna i run-roten när du vill förstå status, beslut och körhistorik.",
            "- Gå till approval-, consultation- och brief-filer först när du behöver fördjupad spårbarhet.",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def _build_phase_catalog(repo_root: Path) -> list[PhaseCatalog]:
    framework_root = get_framework_root(repo_root)
    process_paths = sorted(
        path
        for path in (framework_root / "processes").glob("*.md")
        if re.match(r"^\d+\.\s+.+\.md$", path.name)
    )
    loader = ProcessFlowLoader(repo_root)
    catalogs: list[PhaseCatalog] = []
    for process_path in process_paths:
        flow = loader.load(process_path.name)
        artifacts: list[PhaseArtifact] = []
        seen: set[str] = set()
        for step in flow.steps:
            if step.output_filename in seen:
                continue
            seen.add(step.output_filename)
            artifacts.append(
                PhaseArtifact(
                    artifact_name=step.artifact_name,
                    filename=step.output_filename,
                    delprocess_title=step.delprocess_title,
                )
            )
        catalogs.append(
            PhaseCatalog(
                process_file=flow.process_file,
                process_title=Path(flow.process_file).stem,
                artifacts=artifacts,
            )
        )
    return catalogs


def _build_metadata_lines(workspace: RunWorkspace) -> list[str]:
    lines: list[str] = []
    for filename, description in ROOT_METADATA_FILES.items():
        path = workspace.run_dir / filename
        if path.exists():
            lines.append(f"- [`../{filename}`](../{filename}) - {description}")
    human_tasks_dir = workspace.human_tasks_dir
    if human_tasks_dir.exists():
        lines.append("- [`../human_tasks/`](../human_tasks/) - Mänskliga uppgifter och handoffs för runnen.")
    if not lines:
        lines.append("- Inga metadatafiler har publicerats ännu.")
    return lines


def _render_phase_section(*, phase: PhaseCatalog, output_names: set[str]) -> str:
    present_artifacts = [artifact for artifact in phase.artifacts if artifact.filename in output_names]
    support_counts = _count_phase_support_files(present_artifacts=present_artifacts, output_names=output_names)

    lines = [f"### {phase.process_title}"]
    if not present_artifacts:
        lines.append("_Inga huvudartefakter publicerade för detta processsteg i denna run ännu._")
        lines.append("")
        return "\n".join(lines)

    lines.extend(
        [
            "",
            "**Huvudartefakter**",
        ]
    )
    for artifact in present_artifacts:
        lines.append(
            f"- [`{artifact.filename}`](./{artifact.filename}) - {artifact.artifact_name} "
            f"({artifact.delprocess_title})"
        )

    if any(support_counts.values()):
        lines.extend(
            [
                "",
                "**Kompletterande filer**",
                f"- Approval-filer: {support_counts['approval']}",
                f"- Consultation-filer: {support_counts['consultation']}",
                f"- Brief-filer: {support_counts['brief']}",
            ]
        )

    lines.append("")
    return "\n".join(lines)


def _count_phase_support_files(
    *,
    present_artifacts: list[PhaseArtifact],
    output_names: set[str],
) -> dict[str, int]:
    stems = {Path(artifact.filename).stem for artifact in present_artifacts}
    counts = {"approval": 0, "consultation": 0, "brief": 0}
    for name in output_names:
        base_stem = _extract_base_stem(name)
        if base_stem not in stems:
            continue
        file_type = _classify_support_file(name)
        if file_type in counts:
            counts[file_type] += 1
    return counts


def _count_support_files(output_names: set[str]) -> dict[str, int]:
    counts = {"approval": 0, "consultation": 0, "brief": 0}
    for name in output_names:
        file_type = _classify_support_file(name)
        if file_type in counts:
            counts[file_type] += 1
    return counts


def _extract_base_stem(filename: str) -> str:
    stem = Path(filename).stem
    for marker in ("_approval_", "_consultation_", "_brief_"):
        if marker in stem:
            return stem.split(marker, 1)[0]
    return stem


def _classify_support_file(filename: str) -> str:
    stem = Path(filename).stem
    if "_approval_" in stem:
        return "approval"
    if "_consultation_" in stem:
        return "consultation"
    if "_brief_" in stem:
        return "brief"
    return "other"
