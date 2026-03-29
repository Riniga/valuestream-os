"""
Central orchestrator for the Agent Orchestration Framework.

The Orchestrator drives a multi-agent flow step by step:
  1. Validate that required input artifacts exist.
  2. Load the agent's docs context (role, SOP, artifact description + template).
  3. Build the generation or update prompt.
  4. Run the agent via the MAF adapter.
  5. Save the output artifact.
  6. Copy the output to the run workspace input dir (so downstream steps can use it).
  7. Update run state and artifact state after each step.
  8. Append a structured log entry.

Supports dry_run=True for testing without LLM calls (writes the prompt instead).
"""
from __future__ import annotations

import asyncio
import shutil
from pathlib import Path

from src.capabilities.run_workspace import RunWorkspace
from src.framework.context_loader import AgentContextLoader
from src.framework.models import AgentDefinition, ArtifactState, FlowStep, ProcessFlow, RunState, RunStatus, StepResult, StepStatus
from src.framework.prompt_builder import FrameworkPromptBuilder
from src.framework.stores import (
    AgentMemoryStore,
    ArtifactStateStore,
    RunLog,
    RunStateStore,
)
from src.orchestration.agent_registry import AGENT_DEFINITIONS
from src.orchestration.process_loader import DEFAULT_PROCESS_FILE, ProcessFlowLoader


class Orchestrator:
    """
    Runs a process-driven multi-agent flow for a given run workspace.

    Parameters
    ----------
    workspace:
        The run workspace (handles input/output file I/O).
    repo_root:
        Path to the repository root (used to locate docs/).
    process_flow:
        Resolved process flow to execute. If omitted, the default process file in
        docs/processes/ is loaded and converted into executable steps.
    agent_definitions:
        Registry of AgentDefinition objects (defaults to AGENT_DEFINITIONS).
    """

    def __init__(
        self,
        workspace: RunWorkspace,
        repo_root: Path,
        process_flow: ProcessFlow | None = None,
        flow_steps: list[FlowStep] | None = None,
        agent_definitions: dict[str, AgentDefinition] | None = None,
    ) -> None:
        self._workspace = workspace
        self._repo_root = repo_root
        self._agents = agent_definitions if agent_definitions is not None else AGENT_DEFINITIONS
        if process_flow is not None:
            self._process_flow = process_flow
            self._steps = process_flow.steps
        elif flow_steps is not None:
            self._steps = flow_steps
            self._process_flow = ProcessFlow(
                flow_id="custom-flow",
                process_file="<custom>",
                process_title="Custom flow",
                steps=flow_steps,
            )
        else:
            self._process_flow = ProcessFlowLoader(
                repo_root=repo_root,
                agent_definitions=self._agents,
            ).load(DEFAULT_PROCESS_FILE)
            self._steps = self._process_flow.steps
        self._prompt_builder = FrameworkPromptBuilder()

        run_dir = workspace.run_dir
        self._run_state_store = RunStateStore(run_dir)
        self._artifact_state_store = ArtifactStateStore(run_dir)
        self._memory_store = AgentMemoryStore(run_dir)
        self._log = RunLog(run_dir)

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def run(self, dry_run: bool = False) -> list[StepResult]:
        """Execute all flow steps synchronously using one event loop."""
        return asyncio.run(self.run_async(dry_run=dry_run))

    async def run_async(self, dry_run: bool = False) -> list[StepResult]:
        """Execute all flow steps and return all StepResults when done."""
        return [r async for r in self.run_stream_async(dry_run=dry_run)]

    async def run_stream_async(self, dry_run: bool = False):
        """
        Execute all flow steps and yield each StepResult as soon as it completes.

        Allows the caller to print progress in real time via `async for`.
        """
        run_state = self._run_state_store.initialize(
            run_id=self._workspace.run_id,
            flow_id=self._process_flow.flow_id,
            step_ids=[s.step_id for s in self._steps],
        )
        artifact_state = self._artifact_state_store.initialize(
            run_id=self._workspace.run_id,
        )
        self._log.append({"event": "run_started", "run_id": self._workspace.run_id, "dry_run": dry_run})

        for step in self._steps:
            result = await self._run_step_async(step, run_state, artifact_state, dry_run=dry_run)
            yield result
            if result.status == StepStatus.failed:
                run_state.status = RunStatus.failed
                self._run_state_store.save(run_state)
                self._log.append({"event": "run_failed", "step_id": step.step_id})
                break

        if run_state.status == RunStatus.running:
            run_state.status = RunStatus.completed
        run_state.current_step_id = None
        self._run_state_store.save(run_state)
        self._log.append({"event": "run_finished", "status": run_state.status.value})

    # ------------------------------------------------------------------
    # Private: step execution
    # ------------------------------------------------------------------

    async def _run_step_async(
        self,
        step: FlowStep,
        run_state: RunState,
        artifact_state: ArtifactState,
        dry_run: bool,
    ) -> StepResult:
        run_state.current_step_id = step.step_id
        run_state.step_statuses[step.step_id] = StepStatus.running.value
        self._run_state_store.save(run_state)

        missing = self._workspace.validate_input(step.input_filenames)
        if missing:
            reason = f"Saknar input: {', '.join(missing)}"
            run_state.step_statuses[step.step_id] = StepStatus.skipped.value
            self._run_state_store.save(run_state)
            self._log.append({
                "event": "step_skipped",
                "step_id": step.step_id,
                "reason": reason,
            })
            return StepResult(
                step_id=step.step_id,
                agent_id=step.agent_id,
                artifact_name=step.artifact_name,
                status=StepStatus.skipped,
                skipped_reason=reason,
                delprocess_title=step.delprocess_title,
            )

        try:
            output_path = await self._execute_step_async(step, dry_run=dry_run)
        except Exception as exc:  # noqa: BLE001
            error_msg = f"{type(exc).__name__}: {exc}"
            run_state.step_statuses[step.step_id] = StepStatus.failed.value
            self._artifact_state_store.record_failed(
                artifact_state, step.output_filename, step.artifact_name, step.step_id
            )
            self._run_state_store.save(run_state)
            self._log.append({
                "event": "step_failed",
                "step_id": step.step_id,
                "error": error_msg,
            })
            return StepResult(
                step_id=step.step_id,
                agent_id=step.agent_id,
                artifact_name=step.artifact_name,
                status=StepStatus.failed,
                error=error_msg,
                delprocess_title=step.delprocess_title,
            )

        if not dry_run:
            dest = self._workspace.input_dir / step.output_filename
            shutil.copy(output_path, dest)
            self._artifact_state_store.record_produced(
                artifact_state, step.output_filename, step.artifact_name, step.step_id
            )

        run_state.step_statuses[step.step_id] = StepStatus.completed.value
        self._run_state_store.save(run_state)
        try:
            output_rel = str(output_path.relative_to(self._repo_root))
        except ValueError:
            output_rel = str(output_path)
        self._log.append({
            "event": "step_completed",
            "step_id": step.step_id,
            "artifact": step.artifact_name,
            "output": output_rel,
            "dry_run": dry_run,
        })
        return StepResult(
            step_id=step.step_id,
            agent_id=step.agent_id,
            artifact_name=step.artifact_name,
            status=StepStatus.completed,
            output_path=output_path,
            delprocess_title=step.delprocess_title,
        )

    async def _execute_step_async(self, step: FlowStep, dry_run: bool) -> Path:
        agent_def = self._agents[step.agent_id]
        loader = AgentContextLoader(
            repo_root=self._repo_root,
            agent_file=agent_def.agent_file,
            raci_role_id=agent_def.raci_role_id,
        )

        role_name = loader.raci_role
        role_text = loader.load_role()
        sop = loader.load_sop(step.sop_filename)
        description = loader.load_artifact_description(step.artifact_name)
        template = loader.load_artifact_template(step.output_filename)
        input_content = {
            f: self._workspace.read_input(f)
            for f in step.input_filenames
            if self._workspace.input_path(f).exists()
        }

        if dry_run:
            prompt = self._prompt_builder.build_generate_prompt(
                role_name=role_name,
                role_text=role_text,
                sop_text=sop.content,
                artifact_description=description,
                artifact_template=template,
                input_content=input_content,
            )
            dry_run_filename = step.output_filename.replace(".md", "_prompt_dry_run.txt")
            return self._workspace.write_output(dry_run_filename, prompt)

        instructions = loader.load_agent_instructions()
        if self._workspace.output_exists(step.output_filename):
            existing = self._workspace.read_output(step.output_filename)
            prompt = self._prompt_builder.build_update_prompt(
                role_name=role_name,
                role_text=role_text,
                sop_text=sop.content,
                artifact_description=description,
                artifact_template=template,
                input_content=input_content,
                existing_content=existing,
            )
        else:
            prompt = self._prompt_builder.build_generate_prompt(
                role_name=role_name,
                role_text=role_text,
                sop_text=sop.content,
                artifact_description=description,
                artifact_template=template,
                input_content=input_content,
            )

        from src.framework.maf_adapter import AgentRunner
        runner = AgentRunner(name=agent_def.agent_id, instructions=instructions)
        content = await runner.run_async(prompt)

        return self._workspace.write_output(step.output_filename, content)
