from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from src.framework.context_loader import AgentContextLoader
from src.framework.models import AgentDefinition, FlowStep, ProcessFlow
from src.orchestration.agent_registry import AGENT_DEFINITIONS


DEFAULT_PROCESS_FILE = "1. Kravställning.md"


@dataclass(frozen=True)
class ProcessSection:
    index: int
    title: str
    sop_filename: str


class ProcessFlowLoader:
    """Builds executable flow steps from docs/processes/ documentation."""

    def __init__(
        self,
        repo_root: Path,
        agent_definitions: dict[str, AgentDefinition] | None = None,
    ) -> None:
        self._repo_root = repo_root
        self._docs_root = repo_root / "docs"
        self._processes_root = self._docs_root / "processes"
        self._agent_definitions = agent_definitions or AGENT_DEFINITIONS
        sample_agent = next(iter(self._agent_definitions.values()))
        self._artifact_loader = AgentContextLoader(
            repo_root=repo_root,
            agent_file=sample_agent.agent_file,
            raci_role_id=sample_agent.raci_role_id,
        )

    def load(self, process_file: str = DEFAULT_PROCESS_FILE) -> ProcessFlow:
        path = self._processes_root / process_file
        content = path.read_text(encoding="utf-8")
        sections = self._parse_sections(content)
        steps: list[FlowStep] = []

        for section in sections:

            sop = self._artifact_loader.load_sop(section.sop_filename)
            agent_id = self._resolve_agent_id(sop.content)
            input_filenames = self._resolve_input_filenames(sop.inputs)
            seen_outputs: set[str] = set()

            for output_name in sop.outputs:

                template_path = self._artifact_loader.find_template_path(output_name)
                # print(f"Template path: {template_path}")
                if template_path is None:
                    continue
                if template_path.name in seen_outputs:
                    continue
                seen_outputs.add(template_path.name)

                steps.append(
                    FlowStep(
                        step_id=self._build_step_id(
                            process_file=process_file,
                            section_index=section.index,
                            output_filename=template_path.name,
                        ),
                        agent_id=agent_id,
                        sop_filename=section.sop_filename,
                        artifact_name=output_name,
                        output_filename=template_path.name,
                        input_filenames=input_filenames,
                        delprocess_title=section.title,
                    )
                )

        return ProcessFlow(
            flow_id=self._build_flow_id(process_file),
            process_file=process_file,
            process_title=self._extract_process_title(content, Path(process_file).stem),
            steps=steps,
        )

    def _parse_sections(self, content: str) -> list[ProcessSection]:
        matches = list(
            re.finditer(
                r"^##\s+Delprocess\s+(\d+):\s+(.+?)$",
                content,
                flags=re.MULTILINE,
            )
        )
        sections: list[ProcessSection] = []
        for i, match in enumerate(matches):
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            block = content[start:end]
            sop_match = re.search(
                r"\.\./SOP/[^)/]+/(?P<filename>[^)]+\.md)",
                block,
            )
            if not sop_match:
                continue
            sections.append(
                ProcessSection(
                    index=int(match.group(1)),
                    title=match.group(2).strip(),
                    sop_filename=sop_match.group("filename"),
                )
            )
        return sections

    def _resolve_agent_id(self, sop_content: str) -> str:
        responsible_role = self._extract_responsible_role(sop_content)
        for agent_id, agent_def in self._agent_definitions.items():
            if agent_def.raci_role_id.lower() in responsible_role.lower():
                return agent_id
        raise ValueError(f"Ingen registrerad agent hittades för RACI-roll: {responsible_role}")

    def _resolve_input_filenames(self, input_names: list[str]) -> list[str]:
        filenames: list[str] = []
        seen: set[str] = set()
        for input_name in input_names:
            template_path = self._artifact_loader.find_template_path(input_name)
            if template_path is None:
                continue
            if template_path.name in seen:
                continue
            seen.add(template_path.name)
            filenames.append(template_path.name)
        return filenames

    @staticmethod
    def _extract_responsible_role(sop_content: str) -> str:
        raci_match = re.search(
            r"^-\s*R\s*:\s*(.+)$",
            sop_content,
            flags=re.MULTILINE,
        )
        if not raci_match:
            raise ValueError("SOP saknar RACI-rad för ansvarig roll")
        return raci_match.group(1).strip()

    @staticmethod
    def _extract_process_title(content: str, fallback: str) -> str:
        for line in content.splitlines():
            if line.startswith("# "):
                return line.lstrip("# ").strip()
        return fallback

    @staticmethod
    def _build_flow_id(process_file: str) -> str:
        return ProcessFlowLoader._slugify(Path(process_file).stem)

    @staticmethod
    def _build_step_id(process_file: str, section_index: int, output_filename: str) -> str:
        process_slug = ProcessFlowLoader._slugify(Path(process_file).stem)
        output_slug = ProcessFlowLoader._slugify(Path(output_filename).stem)
        return f"{process_slug}-{section_index:02d}-{output_slug}"

    @staticmethod
    def _slugify(value: str) -> str:
        ascii_value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
        ascii_value = ascii_value.lower()
        ascii_value = re.sub(r"[^a-z0-9]+", "-", ascii_value)
        return ascii_value.strip("-")
