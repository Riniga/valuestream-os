from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from src.framework.context_loader import AgentContextLoader
from src.framework.models import AgentDefinition, FlowStep, ProcessFlow
from src.framework.repo_layout import get_framework_root
from src.orchestration.agent_registry import (
    build_raci_role_index,
    load_agent_definitions,
    normalize_raci_role,
)


DEFAULT_PROCESS_FILE = "1. Kravställning.md"


@dataclass(frozen=True)
class ProcessSection:
    index: int
    title: str
    sop_filename: str


class ProcessFlowLoader:
    """Build executable flow steps from the configured framework."""

    def __init__(
        self,
        repo_root: Path,
        agent_definitions: dict[str, AgentDefinition] | None = None,
    ) -> None:
        self._repo_root = repo_root
        self._framework_root = get_framework_root(repo_root)
        self._processes_root = self._framework_root / "processes"
        self._agent_definitions = agent_definitions or load_agent_definitions(repo_root)
        if not self._agent_definitions:
            raise ValueError("Inga agentdefinitioner kunde laddas från frameworket")
        self._raci_role_index = build_raci_role_index(self._agent_definitions)
        sample_agent = next(iter(self._agent_definitions.values()))
        self._context_loader = AgentContextLoader(
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
            sop = self._context_loader.load_sop(section.sop_filename)
            agent_id = self._resolve_required_agent_id(
                self._extract_raci_roles(sop.content, "R"),
                key="R",
                sop_filename=section.sop_filename,
            )
            consult_agent_ids = self._resolve_agent_ids(
                self._extract_raci_roles(sop.content, "C"),
                sop_filename=section.sop_filename,
            )
            approver_agent_id = self._resolve_optional_agent_id(
                self._extract_raci_roles(sop.content, "A"),
                sop_filename=section.sop_filename,
            )
            informed_agent_ids = self._resolve_agent_ids(
                self._extract_raci_roles(sop.content, "I"),
                sop_filename=section.sop_filename,
            )
            input_filenames = self._resolve_input_filenames(
                sop.inputs,
                sop_filename=section.sop_filename,
            )
            seen_outputs: set[str] = set()
            responsible_def = self._agent_definitions[agent_id]
            consult_actor_kinds = {
                role_agent_id: self._agent_definitions[role_agent_id].actor_kind
                for role_agent_id in consult_agent_ids
            }
            approver_actor_kind = (
                self._agent_definitions[approver_agent_id].actor_kind
                if approver_agent_id is not None
                else None
            )
            informed_actor_kinds = {
                role_agent_id: self._agent_definitions[role_agent_id].actor_kind
                for role_agent_id in informed_agent_ids
            }

            for output_name in sop.outputs:
                template_path = self._require_template_path(output_name, section.sop_filename)
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
                        agent_actor_kind=responsible_def.actor_kind,
                        consult_agent_ids=consult_agent_ids,
                        consult_actor_kinds=consult_actor_kinds,
                        approver_agent_id=approver_agent_id,
                        approver_actor_kind=approver_actor_kind,
                        informed_agent_ids=informed_agent_ids,
                        informed_actor_kinds=informed_actor_kinds,
                        use_raci_workflow=self._should_use_raci_workflow(
                            consult_agent_ids=consult_agent_ids,
                            approver_agent_id=approver_agent_id,
                            informed_agent_ids=informed_agent_ids,
                        ),
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

    def _resolve_required_agent_id(self, roles: list[str], *, key: str, sop_filename: str) -> str:
        if not roles:
            raise ValueError(f"SOP '{sop_filename}' saknar RACI-rad för {key}")
        return self._resolve_agent_id(roles[0], sop_filename=sop_filename)

    def _resolve_agent_id(self, role: str, *, sop_filename: str) -> str:
        normalized_role = normalize_raci_role(role)
        agent_id = self._raci_role_index.get(normalized_role)
        if agent_id is None:
            raise ValueError(
                f"Ingen registrerad agent hittades för RACI-roll '{role}' i SOP '{sop_filename}'"
            )
        return agent_id

    def _resolve_optional_agent_id(self, roles: list[str], *, sop_filename: str) -> str | None:
        if not roles:
            return None
        return self._resolve_agent_id(roles[0], sop_filename=sop_filename)

    def _resolve_agent_ids(self, roles: list[str], *, sop_filename: str) -> list[str]:
        resolved: list[str] = []
        seen: set[str] = set()
        for role in roles:
            agent_id = self._resolve_agent_id(role, sop_filename=sop_filename)
            if agent_id in seen:
                continue
            seen.add(agent_id)
            resolved.append(agent_id)
        return resolved

    def _resolve_input_filenames(self, input_names: list[str], *, sop_filename: str) -> list[str]:
        filenames: list[str] = []
        seen: set[str] = set()
        for input_name in input_names:
            template_path = self._require_template_path(input_name, sop_filename)
            resolved_name = template_path.name
            if resolved_name in seen:
                continue
            seen.add(resolved_name)
            filenames.append(resolved_name)
        return filenames

    @staticmethod
    def _should_use_raci_workflow(
        consult_agent_ids: list[str],
        approver_agent_id: str | None,
        informed_agent_ids: list[str],
    ) -> bool:
        return bool(consult_agent_ids or approver_agent_id or informed_agent_ids)

    @staticmethod
    def _extract_raci_roles(sop_content: str, key: str) -> list[str]:
        raci_match = re.search(
            rf"^-\s*{re.escape(key)}\s*:\s*(.+)$",
            sop_content,
            flags=re.MULTILINE,
        )
        if not raci_match:
            return []
        raw = raci_match.group(1).strip()
        return [part.strip() for part in raw.split(",") if part.strip()]

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

    def _require_template_path(self, artifact_name: str, sop_filename: str) -> Path:
        template_path = self._context_loader.find_template_path(artifact_name)
        if template_path is None:
            raise FileNotFoundError(
                f"Artefaktmall saknas för '{artifact_name}' som refereras i SOP '{sop_filename}'"
            )
        return template_path

    @staticmethod
    def _fallback_input_filename(artifact_name: str) -> str:
        ascii_value = (
            unicodedata.normalize("NFKD", artifact_name)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
        ascii_value = ascii_value.lower()
        ascii_value = re.sub(r"[^a-z0-9]+", "_", ascii_value)
        return f"{ascii_value.strip('_')}.md"

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
