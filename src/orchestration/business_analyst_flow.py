from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from src.agents.business_analyst.agent import BusinessAnalystAgent
from src.agents.business_analyst.artifact_registry import (
    ArtifactDefinition,
    build_artifact_registry,
    get_artifact,
)
from src.agents.business_analyst.context_loader import FrameworkContextLoader, SopEntry
from src.agents.business_analyst.prompt_builder import PromptBuilder
from src.capabilities.run_workspace import RunWorkspace


class BusinessAnalystFlow:

    def __init__(self, workspace: RunWorkspace, repo_root: Path) -> None:
        self.workspace = workspace
        self.repo_root = repo_root
        self.loader = FrameworkContextLoader(repo_root)
        self.prompt_builder = PromptBuilder()
        self._registry = build_artifact_registry(self.loader)

    def get_info(self) -> dict:
        agent_file = self.repo_root / "docs" / "agents" / FrameworkContextLoader.AGENT_FILE
        purpose = self.loader.load_agent_purpose()

        artifacts = []
        seen: set[str] = set()
        for sop_entry in self.loader.load_sops_for_role():
            for output_name in sop_entry.outputs:
                if output_name in seen:
                    continue
                seen.add(output_name)

                desc_path = self.loader.find_description_path(output_name)
                tmpl_path = self.loader.find_template_path(output_name)
                artifact_def = next(
                    (a for a in self._registry if a.name == output_name), None
                )
                artifacts.append(
                    {
                        "name": output_name,
                        "sop_name": sop_entry.name,
                        "sop_path": sop_entry.path,
                        "sop_ok": sop_entry.path.exists(),
                        "description_path": desc_path,
                        "description_ok": desc_path is not None,
                        "template_path": tmpl_path,
                        "template_ok": tmpl_path is not None,
                        "input_files": artifact_def.input_filenames if artifact_def else [],
                        "output_file": artifact_def.output_filename if artifact_def else None,
                    }
                )

        return {
            "role_name": self.loader.role_name,
            "agent_file": agent_file,
            "agent_file_ok": agent_file.exists(),
            "purpose": purpose,
            "artifacts": artifacts,
        }

    def list_responsibilities(self) -> list[dict]:
        sops = self.loader.load_sops_for_role()
        results = []
        for sop in sops:
            for output_name in sop.outputs:
                artifact_def = next(
                    (a for a in self._registry if a.name == output_name), None
                )
                results.append(
                    {
                        "sop": sop.name,
                        "artifact": output_name,
                        "registered": artifact_def is not None,
                        "output_filename": artifact_def.output_filename if artifact_def else None,
                        "input_required": artifact_def.input_filenames if artifact_def else [],
                    }
                )
        return results

    def run_all(self, dry_run: bool = False) -> list[dict]:
        results: list[dict] = []

        for artifact_def in self._registry:
            missing = self.workspace.validate_input(artifact_def.input_filenames)
            if missing:
                results.append(
                    {
                        "artifact": artifact_def.name,
                        "status": "skipped",
                        "missing_inputs": missing,
                    }
                )
                continue

            try:
                if dry_run:
                    output_path = self.generate_dry_run(artifact_def.output_filename)
                    results.append(
                        {"artifact": artifact_def.name, "status": "dry-run", "path": output_path}
                    )
                else:
                    output_path = self.update(artifact_def.output_filename)
                    # Make the generated output available as input for downstream artifacts.
                    dest = self.workspace.input_dir / artifact_def.output_filename
                    shutil.copy(output_path, dest)
                    results.append(
                        {"artifact": artifact_def.name, "status": "ok", "path": output_path}
                    )
            except Exception as exc:  # noqa: BLE001
                results.append(
                    {
                        "artifact": artifact_def.name,
                        "status": "error",
                        "reason": f"{type(exc).__name__}: {exc}",
                    }
                )

        return results

    def update(self, artifact_filename: str = "vision_och_malbild.md") -> Path:
        artifact_def = get_artifact(self._registry, artifact_filename)
        if artifact_def is None:
            raise ValueError(
                f"Artifact '{artifact_filename}' is not registered.\n"
                f"Registered artifacts: {[a.output_filename for a in self._registry]}"
            )

        self._validate_inputs(artifact_def)
        role_text, sop, description, template, input_content = self._load_context(artifact_def)

        if self.workspace.output_exists(artifact_filename):
            existing_content = self.workspace.read_output(artifact_filename)
            prompt = self.prompt_builder.build_update_prompt(
                role_text=role_text,
                sop_text=sop.content,
                artifact_description=description,
                artifact_template=template,
                input_content=input_content,
                existing_content=existing_content,
            )
            action = "update"
        else:
            prompt = self.prompt_builder.build_generate_prompt(
                role_text=role_text,
                sop_text=sop.content,
                artifact_description=description,
                artifact_template=template,
                input_content=input_content,
            )
            action = "generate"

        instructions = self.loader.load_agent_instructions()
        agent = BusinessAnalystAgent(instructions=instructions)
        content = agent.run(prompt)

        output_path = self.workspace.write_output(artifact_filename, content)
        self._write_log(artifact_def, sop, action=action)

        return output_path

    def generate_dry_run(self, artifact_filename: str = "vision_och_malbild.md") -> Path:
        artifact_def = get_artifact(self._registry, artifact_filename)
        if artifact_def is None:
            raise ValueError(
                f"Artifact '{artifact_filename}' is not registered.\n"
                f"Registered artifacts: {[a.output_filename for a in self._registry]}"
            )

        self._validate_inputs(artifact_def)
        role_text, sop, description, template, input_content = self._load_context(artifact_def)

        prompt = self.prompt_builder.build_generate_prompt(
            role_text=role_text,
            sop_text=sop.content,
            artifact_description=description,
            artifact_template=template,
            input_content=input_content,
        )

        dry_run_filename = artifact_filename.replace(".md", "_prompt_dry_run.txt")
        return self.workspace.write_output(dry_run_filename, prompt)

    def _load_context(
        self, artifact_def: ArtifactDefinition
    ) -> tuple[str, SopEntry, str, str, dict[str, str]]:
        role_text = self.loader.load_role()
        sop = self.loader.load_sop(artifact_def.sop_filename)
        description = self.loader.load_artifact_description(artifact_def.name)
        template = self.loader.load_artifact_template(artifact_def.template_filename)
        input_content = self._read_inputs(artifact_def)
        return role_text, sop, description, template, input_content

    def _validate_inputs(self, artifact_def: ArtifactDefinition) -> None:
        missing = self.workspace.validate_input(artifact_def.input_filenames)
        if missing:
            raise FileNotFoundError(
                f"Missing required input files for '{artifact_def.name}':\n"
                + "\n".join(f"  - input/{f}" for f in missing)
            )

    def _read_inputs(self, artifact_def: ArtifactDefinition) -> dict[str, str]:
        return {
            filename: self.workspace.read_input(filename)
            for filename in artifact_def.input_filenames
            if self.workspace.input_path(filename).exists()
        }

    def _write_log(self, artifact_def: ArtifactDefinition, sop: SopEntry, action: str) -> None:
        log_path = self.workspace.run_dir / "run_log.json"
        entries = []
        if log_path.exists():
            try:
                entries = json.loads(log_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                entries = []

        entries.append(
            {
                "timestamp": datetime.now(tz=timezone.utc).isoformat(),
                "action": action,
                "role": self.loader.role_name,
                "sop": sop.name,
                "sop_file": str(sop.path.relative_to(self.repo_root)),
                "artifact": artifact_def.name,
                "output_file": f"output/{artifact_def.output_filename}",
                "input_files": [f"input/{f}" for f in artifact_def.input_filenames],
            }
        )
        log_path.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
