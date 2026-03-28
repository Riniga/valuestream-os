"""
BusinessAnalystFlow — explicit step-by-step orchestration for the BA agent.

Implements three commands:
    list     — show SOPs and artifacts the BA is responsible for
    generate — produce a new artifact using LLM
    update   — regenerate an existing artifact with the latest input
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from src.agents.business_analyst.agent import BusinessAnalystAgent
from src.agents.business_analyst.artifact_registry import (
    ARTIFACT_REGISTRY,
    ArtifactDefinition,
    get_artifact,
)
from src.agents.business_analyst.context_loader import FrameworkContextLoader
from src.agents.business_analyst.prompt_builder import PromptBuilder
from src.capabilities.run_workspace import RunWorkspace


class BusinessAnalystFlow:
    """
    Orchestrates the Business Analyst agent through list / generate / update.

    Each method is independently callable and produces a concrete, verifiable result.
    """

    def __init__(self, workspace: RunWorkspace, repo_root: Path) -> None:
        self.workspace = workspace
        self.repo_root = repo_root
        self.loader = FrameworkContextLoader(repo_root)
        self.prompt_builder = PromptBuilder()

    # ------------------------------------------------------------------
    # list
    # ------------------------------------------------------------------

    def list_responsibilities(self) -> list[dict]:
        """
        Return a list of dicts describing the SOPs and artifacts the BA owns.
        Each entry: {sop, outputs, registered, input_required}
        """
        sops = self.loader.load_sops_for_role()
        registered_outputs = {a.output_filename for a in ARTIFACT_REGISTRY}

        results = []
        for sop in sops:
            for output_name in sop.outputs:
                artifact_def = next(
                    (a for a in ARTIFACT_REGISTRY if a.name == output_name), None
                )
                results.append(
                    {
                        "sop": sop.name,
                        "artifact": output_name,
                        "registered": artifact_def is not None,
                        "output_filename": artifact_def.output_filename
                        if artifact_def
                        else None,
                        "input_required": artifact_def.input_filenames
                        if artifact_def
                        else [],
                    }
                )
        return results

    # ------------------------------------------------------------------
    # generate
    # ------------------------------------------------------------------

    def generate(self, artifact_filename: str = "vision_och_malbild.md") -> Path:
        """
        Generate an artifact from scratch using the LLM.

        Steps:
            1. Resolve artifact definition from registry
            2. Validate required input files exist in workspace
            3. Load framework context (role, SOP, description, template)
            4. Read run input files
            5. Build prompt
            6. Call LLM via BusinessAnalystAgent
            7. Write output to runs/<run-id>/output/
            8. Write run log entry
        """
        artifact_def = get_artifact(artifact_filename)
        if artifact_def is None:
            raise ValueError(
                f"Artifact '{artifact_filename}' is not registered.\n"
                f"Registered artifacts: {[a.output_filename for a in ARTIFACT_REGISTRY]}"
            )

        self._validate_inputs(artifact_def)

        role_text = self.loader.load_role()
        sop = self.loader.load_sop(artifact_def.sop_filename)
        description = self.loader.load_artifact_description(artifact_def.name)
        template = self.loader.load_artifact_template(artifact_def.template_filename)
        input_content = self._read_inputs(artifact_def)

        prompt = self.prompt_builder.build_generate_prompt(
            role_text=role_text,
            sop_text=sop.content,
            artifact_description=description,
            artifact_template=template,
            input_content=input_content,
        )

        agent = BusinessAnalystAgent()
        generated_content = agent.run(prompt)

        output_path = self.workspace.write_output(artifact_filename, generated_content)
        self._write_log(artifact_def, sop, action="generate")

        return output_path

    # ------------------------------------------------------------------
    # generate_dry_run
    # ------------------------------------------------------------------

    def generate_dry_run(self, artifact_filename: str = "vision_och_malbild.md") -> Path:
        """
        Build the full prompt and save it to output/ without calling the LLM.
        Useful for verifying context loading and prompt assembly before going live.
        """
        artifact_def = get_artifact(artifact_filename)
        if artifact_def is None:
            raise ValueError(
                f"Artifact '{artifact_filename}' is not registered.\n"
                f"Registered artifacts: {[a.output_filename for a in ARTIFACT_REGISTRY]}"
            )

        self._validate_inputs(artifact_def)

        role_text = self.loader.load_role()
        sop = self.loader.load_sop(artifact_def.sop_filename)
        description = self.loader.load_artifact_description(artifact_def.name)
        template = self.loader.load_artifact_template(artifact_def.template_filename)
        input_content = self._read_inputs(artifact_def)

        prompt = self.prompt_builder.build_generate_prompt(
            role_text=role_text,
            sop_text=sop.content,
            artifact_description=description,
            artifact_template=template,
            input_content=input_content,
        )

        dry_run_filename = artifact_filename.replace(".md", "_prompt_dry_run.txt")
        output_path = self.workspace.write_output(dry_run_filename, prompt)
        return output_path

    # ------------------------------------------------------------------
    # update
    # ------------------------------------------------------------------

    def update(self, artifact_filename: str = "vision_och_malbild.md") -> Path:
        """
        Regenerate an existing artifact based on the latest input.
        Overwrites the existing output file.
        """
        if not self.workspace.output_exists(artifact_filename):
            raise FileNotFoundError(
                f"No existing output for '{artifact_filename}'. Run generate first."
            )
        output_path = self.generate(artifact_filename)
        self._append_log(artifact_filename, action="update")
        return output_path

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _validate_inputs(self, artifact_def: ArtifactDefinition) -> None:
        missing = self.workspace.validate_input(artifact_def.input_filenames)
        if missing:
            raise FileNotFoundError(
                f"Missing required input files for '{artifact_def.name}':\n"
                + "\n".join(f"  - input/{f}" for f in missing)
            )

    def _read_inputs(self, artifact_def: ArtifactDefinition) -> dict[str, str]:
        """Return dict mapping filename → content for each input file."""
        return {
            filename: self.workspace.read_input(filename)
            for filename in artifact_def.input_filenames
            if self.workspace.input_path(filename).exists()
        }

    def _write_log(
        self,
        artifact_def: ArtifactDefinition,
        sop,
        action: str,
    ) -> None:
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
                "role": "Business Analyst",
                "sop": sop.name,
                "sop_file": str(sop.path.relative_to(self.repo_root)),
                "artifact": artifact_def.name,
                "output_file": f"output/{artifact_def.output_filename}",
                "input_files": [f"input/{f}" for f in artifact_def.input_filenames],
            }
        )
        log_path.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")

    def _append_log(self, artifact_filename: str, action: str) -> None:
        artifact_def = get_artifact(artifact_filename)
        if artifact_def:
            sop = self.loader.load_sop(artifact_def.sop_filename)
            self._write_log(artifact_def, sop, action=action)
