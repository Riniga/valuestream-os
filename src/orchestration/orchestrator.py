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
import json
import re
import shutil
from collections.abc import AsyncGenerator
from pathlib import Path
from uuid import uuid4

from src.capabilities.run_workspace import RunWorkspace
from src.framework.context_loader import AgentContextLoader
from src.framework.maf_adapter import AgentRunner
from src.framework.models import (
    AgentDefinition,
    ApprovalDecision,
    ArtifactState,
    ArtifactStatus,
    ConsultationRequest,
    ConsultationResponse,
    ExpertContext,
    FlowStep,
    InformedRoleBrief,
    ProcessFlow,
    RunState,
    RunStatus,
    StepResult,
    StepStatus,
)
from src.framework.prompt_builder import FrameworkPromptBuilder
from src.framework.stores import (
    ApprovalStore,
    ArtifactStateStore,
    ConsultationStore,
    ExpertContextStore,
    InformedRoleBriefStore,
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
        self._consultation_store = ConsultationStore(run_dir)
        self._approval_store = ApprovalStore(run_dir)
        self._brief_store = InformedRoleBriefStore(run_dir)
        self._expert_context_store = ExpertContextStore(run_dir)
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

    async def run_stream_async(self, dry_run: bool = False) -> AsyncGenerator[StepResult, None]:
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
        run_state.current_phase = None
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
        run_state.current_phase = "draft" if step.use_raci_workflow else None
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
            approval_decision = None
            if step.use_raci_workflow and step.approver_agent_id:
                output_path, approval_decision = await self._execute_raci_step_async(
                    step,
                    run_state,
                    artifact_state,
                    dry_run=dry_run,
                )
            else:
                output_path = await self._execute_step_async(step, dry_run=dry_run)
        except Exception as exc:  # noqa: BLE001
            error_msg = f"{type(exc).__name__}: {exc}"
            run_state.step_statuses[step.step_id] = StepStatus.failed.value
            run_state.current_phase = None
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
                phase=run_state.current_phase,
            )

        if not dry_run and not step.use_raci_workflow:
            dest = self._workspace.input_dir / step.output_filename
            shutil.copy(output_path, dest)
            self._artifact_state_store.record_produced(
                artifact_state, step.output_filename, step.artifact_name, step.step_id
            )

        run_state.step_statuses[step.step_id] = StepStatus.completed.value
        run_state.current_phase = None
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
            "approval_decision": approval_decision,
        })
        return StepResult(
            step_id=step.step_id,
            agent_id=step.agent_id,
            artifact_name=step.artifact_name,
            status=StepStatus.completed,
            output_path=output_path,
            delprocess_title=step.delprocess_title,
            phase="informing" if step.use_raci_workflow else None,
            approval_decision=approval_decision,
        )

    async def _execute_step_async(self, step: FlowStep, dry_run: bool) -> Path:
        loader = self._make_loader(step.agent_id)
        role_name = loader.raci_role
        role_text = loader.load_role()
        sop = loader.load_sop(step.sop_filename)
        description = loader.load_artifact_description(step.artifact_name)
        template = loader.load_artifact_template(step.output_filename)
        input_content = self._read_step_inputs(step)

        if self._workspace.output_exists(step.output_filename) and not dry_run:
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

        _, path = await self._run_agent_prompt_async(
            agent_id=step.agent_id,
            prompt=prompt,
            dry_run=dry_run,
            output_filename=step.output_filename,
            dry_run_suffix="prompt",
        )
        return path

    async def _execute_raci_step_async(
        self,
        step: FlowStep,
        run_state: RunState,
        artifact_state: ArtifactState,
        dry_run: bool,
    ) -> tuple[Path, str | None]:
        input_content = self._read_step_inputs(step)
        draft_content, draft_path = await self._run_draft_phase(step, dry_run, input_content)
        self._artifact_state_store.record_status(
            artifact_state,
            step.output_filename,
            step.artifact_name,
            step.step_id,
            ArtifactStatus.draft,
            consult_agent_ids=step.consult_agent_ids,
            approver_agent_id=step.approver_agent_id,
            informed_agent_ids=step.informed_agent_ids,
            latest_phase="draft",
        )

        self._set_phase(run_state, step, "consultation")
        request = ConsultationRequest(
            request_id=str(uuid4()),
            step_id=step.step_id,
            artifact_name=step.artifact_name,
            artifact_filename=step.output_filename,
            requester_agent_id=step.agent_id,
            consultant_agent_ids=step.consult_agent_ids,
            questions=self._default_consultation_questions(step.artifact_name),
            draft_summary=self._summarize_text(draft_content),
        )
        self._consultation_store.append_request(request)
        consultation_feedback = await self._run_consultation_phase(
            step=step,
            dry_run=dry_run,
            artifact_content=draft_content,
            request=request,
            input_content=input_content,
        )
        self._artifact_state_store.record_status(
            artifact_state,
            step.output_filename,
            step.artifact_name,
            step.step_id,
            ArtifactStatus.in_consultation,
            latest_phase="consultation",
        )

        self._set_phase(run_state, step, "revision")
        revised_content, revised_path = await self._run_revision_phase(
            step=step,
            dry_run=dry_run,
            input_content=input_content,
            existing_content=draft_content,
            consultation_feedback=consultation_feedback,
        )
        self._artifact_state_store.record_status(
            artifact_state,
            step.output_filename,
            step.artifact_name,
            step.step_id,
            ArtifactStatus.revision_requested,
            latest_phase="revision",
        )

        self._set_phase(run_state, step, "approval")
        self._artifact_state_store.record_status(
            artifact_state,
            step.output_filename,
            step.artifact_name,
            step.step_id,
            ArtifactStatus.awaiting_approval,
            latest_phase="awaiting_approval",
        )
        decision = await self._run_approval_phase(
            step=step,
            dry_run=dry_run,
            artifact_content=revised_content,
            consultation_feedback=consultation_feedback,
        )
        self._approval_store.append(decision)
        mapped_status = self._approval_status_to_artifact_status(decision.decision)
        self._artifact_state_store.record_status(
            artifact_state,
            step.output_filename,
            step.artifact_name,
            step.step_id,
            mapped_status,
            latest_phase="approval",
            approval_decision=decision.decision,
        )
        if decision.decision == "rejected":
            raise RuntimeError(
                f"Artifakten {step.artifact_name} avslogs av {step.approver_agent_id}: {decision.summary or decision.rationale}"
            )

        if decision.decision == "approved_with_notes" and decision.changes_requested:
            self._set_phase(run_state, step, "approval_revision")
            revised_content, revised_path = await self._run_revision_phase(
                step=step,
                dry_run=dry_run,
                input_content=input_content,
                existing_content=revised_content,
                consultation_feedback=consultation_feedback,
                approval_feedback=self._format_approval_feedback(decision),
                dry_run_suffix="approval_revision",
            )

        if not dry_run:
            revised_content = self._update_document_status(revised_content, decision.decision)
            revised_path = self._workspace.write_output(step.output_filename, revised_content)

        self._set_phase(run_state, step, "informing")
        await self._run_informing_phase(
            step=step,
            dry_run=dry_run,
            artifact_content=revised_content,
            decision=decision,
        )
        self._artifact_state_store.record_status(
            artifact_state,
            step.output_filename,
            step.artifact_name,
            step.step_id,
            ArtifactStatus.published_to_informed_roles if step.informed_agent_ids else mapped_status,
            latest_phase="informing",
            approval_decision=decision.decision,
        )

        if not dry_run:
            dest = self._workspace.input_dir / step.output_filename
            shutil.copy(revised_path, dest)

        return revised_path, decision.decision

    async def _run_draft_phase(
        self,
        step: FlowStep,
        dry_run: bool,
        input_content: dict[str, str],
    ) -> tuple[str, Path]:
        loader = self._make_loader(step.agent_id)
        sop = loader.load_sop(step.sop_filename)
        prompt = self._prompt_builder.build_generate_prompt(
            role_name=loader.raci_role,
            role_text=loader.load_role(),
            sop_text=sop.content,
            artifact_description=loader.load_artifact_description(step.artifact_name),
            artifact_template=loader.load_artifact_template(step.output_filename),
            input_content=input_content,
        )
        return await self._run_agent_prompt_async(
            agent_id=step.agent_id,
            prompt=prompt,
            dry_run=dry_run,
            output_filename=step.output_filename,
            dry_run_suffix="draft",
        )

    async def _run_consultation_phase(
        self,
        step: FlowStep,
        dry_run: bool,
        artifact_content: str,
        request: ConsultationRequest,
        input_content: dict[str, str],
    ) -> dict[str, str]:
        responses: dict[str, str] = {}
        for consultant_agent_id in step.consult_agent_ids:
            loader = self._make_loader(consultant_agent_id)
            expert_context = self._build_expert_context(step, consultant_agent_id, input_content)
            prompt = self._prompt_builder.build_consultation_prompt(
                role_name=loader.raci_role,
                role_text=loader.load_role(),
                artifact_name=step.artifact_name,
                artifact_content=artifact_content,
                questions=request.questions,
                expert_context=expert_context.context_text,
            )
            response_text, _ = await self._run_agent_prompt_async(
                agent_id=consultant_agent_id,
                prompt=prompt,
                dry_run=dry_run,
                output_filename=f"{Path(step.output_filename).stem}_consultation_{consultant_agent_id}.md",
                dry_run_suffix="consultation",
            )
            self._consultation_store.append_response(
                ConsultationResponse(
                    request_id=request.request_id,
                    step_id=step.step_id,
                    artifact_name=step.artifact_name,
                    consultant_agent_id=consultant_agent_id,
                    response_text=response_text,
                    summary=self._summarize_text(response_text),
                )
            )
            responses[consultant_agent_id] = response_text
        return responses

    async def _run_revision_phase(
        self,
        step: FlowStep,
        dry_run: bool,
        input_content: dict[str, str],
        existing_content: str,
        consultation_feedback: dict[str, str],
        approval_feedback: str = "",
        dry_run_suffix: str = "revision",
    ) -> tuple[str, Path]:
        loader = self._make_loader(step.agent_id)
        prompt = self._prompt_builder.build_revision_prompt(
            role_name=loader.raci_role,
            role_text=loader.load_role(),
            artifact_name=step.artifact_name,
            artifact_description=loader.load_artifact_description(step.artifact_name),
            artifact_template=loader.load_artifact_template(step.output_filename),
            existing_content=existing_content,
            consultation_feedback=consultation_feedback,
            input_content=input_content,
            approval_feedback=approval_feedback,
        )
        return await self._run_agent_prompt_async(
            agent_id=step.agent_id,
            prompt=prompt,
            dry_run=dry_run,
            output_filename=step.output_filename,
            dry_run_suffix=dry_run_suffix,
        )

    async def _run_approval_phase(
        self,
        step: FlowStep,
        dry_run: bool,
        artifact_content: str,
        consultation_feedback: dict[str, str],
    ) -> ApprovalDecision:
        approver_agent_id = step.approver_agent_id or ""
        loader = self._make_loader(approver_agent_id)
        prompt = self._prompt_builder.build_approval_prompt(
            role_name=loader.raci_role,
            role_text=loader.load_role(),
            artifact_name=step.artifact_name,
            artifact_content=artifact_content,
            consultation_feedback=consultation_feedback,
        )
        approval_text, _ = await self._run_agent_prompt_async(
            agent_id=approver_agent_id,
            prompt=prompt,
            dry_run=dry_run,
            output_filename=f"{Path(step.output_filename).stem}_approval_{approver_agent_id}.json",
            dry_run_suffix="approval",
        )
        return self._parse_approval_decision(
            step=step,
            approver_agent_id=approver_agent_id,
            raw_text=approval_text,
            dry_run=dry_run,
        )

    async def _run_informing_phase(
        self,
        step: FlowStep,
        dry_run: bool,
        artifact_content: str,
        decision: ApprovalDecision,
    ) -> None:
        decision_summary = decision.summary or decision.rationale or decision.decision
        for informed_agent_id in step.informed_agent_ids:
            loader = self._make_loader(informed_agent_id)
            prompt = self._prompt_builder.build_informing_prompt(
                role_name=loader.raci_role,
                role_text=loader.load_role(),
                artifact_name=step.artifact_name,
                artifact_content=artifact_content,
                decision_summary=decision_summary,
            )
            brief_text, _ = await self._run_agent_prompt_async(
                agent_id=informed_agent_id,
                prompt=prompt,
                dry_run=dry_run,
                output_filename=f"{Path(step.output_filename).stem}_brief_{informed_agent_id}.md",
                dry_run_suffix="brief",
            )
            self._brief_store.append(
                InformedRoleBrief(
                    step_id=step.step_id,
                    artifact_name=step.artifact_name,
                    artifact_filename=step.output_filename,
                    role_agent_id=informed_agent_id,
                    brief_text=brief_text,
                    relevance=self._summarize_text(brief_text),
                )
            )

    def _make_loader(self, agent_id: str) -> AgentContextLoader:
        agent_def = self._agents[agent_id]
        return AgentContextLoader(
            repo_root=self._repo_root,
            agent_file=agent_def.agent_file,
            raci_role_id=agent_def.raci_role_id,
        )

    def _read_step_inputs(self, step: FlowStep) -> dict[str, str]:
        return {
            filename: self._workspace.read_input(filename)
            for filename in step.input_filenames
            if self._workspace.input_path(filename).exists()
        }

    async def _run_agent_prompt_async(
        self,
        agent_id: str,
        prompt: str,
        dry_run: bool,
        output_filename: str,
        dry_run_suffix: str,
    ) -> tuple[str, Path]:
        if dry_run:
            dry_run_filename = self._build_dry_run_filename(output_filename, dry_run_suffix)
            return prompt, self._workspace.write_output(dry_run_filename, prompt)

        loader = self._make_loader(agent_id)
        runner = AgentRunner(name=agent_id, instructions=loader.load_agent_instructions())
        content = await runner.run_async(prompt)
        return content, self._workspace.write_output(output_filename, content)

    def _set_phase(self, run_state: RunState, step: FlowStep, phase: str) -> None:
        run_state.current_phase = phase
        self._run_state_store.save(run_state)
        self._log.append({"event": "step_phase_started", "step_id": step.step_id, "phase": phase})

    def _build_expert_context(
        self,
        step: FlowStep,
        consultant_agent_id: str,
        input_content: dict[str, str],
    ) -> ExpertContext:
        existing = self._expert_context_store.load(
            agent_id=consultant_agent_id,
            run_id=self._workspace.run_id,
            artifact_name=step.artifact_name,
        )
        if existing is not None:
            return existing

        prior_notes = []
        for response in self._consultation_store.load_responses():
            if response.artifact_name == step.artifact_name:
                prior_notes.append(f"{response.artifact_name}/{response.consultant_agent_id}: {response.summary}")

        for decision in self._approval_store.load():
            if decision.artifact_name == step.artifact_name:
                prior_notes.append(f"{decision.artifact_name}: {decision.summary or decision.rationale}")

        context_text = self._prompt_builder.build_expert_context_text(
            artifact_name=step.artifact_name,
            input_content=input_content,
            prior_notes=prior_notes,
        )
        context = ExpertContext(
            agent_id=consultant_agent_id,
            run_id=self._workspace.run_id,
            artifact_name=step.artifact_name,
            context_text=context_text,
            source_filenames=sorted(input_content.keys()),
        )
        self._expert_context_store.save(context)
        return context

    def _parse_approval_decision(
        self,
        step: FlowStep,
        approver_agent_id: str,
        raw_text: str,
        dry_run: bool,
    ) -> ApprovalDecision:
        parsed = None if dry_run else self._extract_json_object(raw_text)
        if dry_run:
            parsed = {
                "decision": "approved_with_notes",
                "summary": "Dry-run simulerade ett godkännande med kommentarer.",
                "rationale": "Ingen LLM kördes; approval-prompt genererades endast för granskning.",
                "changes_requested": [],
            }
        if parsed is None:
            lowered = raw_text.lower()
            if "rejected" in lowered:
                decision = "rejected"
            elif "approved_with_notes" in lowered:
                decision = "approved_with_notes"
            else:
                decision = "approved"
            parsed = {
                "decision": decision,
                "summary": self._summarize_text(raw_text),
                "rationale": raw_text.strip(),
                "changes_requested": [],
            }
        return ApprovalDecision(
            step_id=step.step_id,
            artifact_name=step.artifact_name,
            artifact_filename=step.output_filename,
            approver_agent_id=approver_agent_id,
            decision=self._as_string(parsed.get("decision"), default="approved"),
            summary=self._as_string(parsed.get("summary")),
            rationale=self._as_string(parsed.get("rationale")),
            changes_requested=self._as_string_list(parsed.get("changes_requested")),
        )

    @staticmethod
    def _extract_json_object(raw_text: str) -> dict[str, object] | None:
        text = raw_text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        decoder = json.JSONDecoder()
        for index, char in enumerate(text):
            if char != "{":
                continue
            try:
                data, _ = decoder.raw_decode(text[index:])
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict):
                return data
        return None

    @staticmethod
    def _approval_status_to_artifact_status(decision: str) -> ArtifactStatus:
        mapping = {
            "approved": ArtifactStatus.approved,
            "approved_with_notes": ArtifactStatus.approved_with_notes,
            "rejected": ArtifactStatus.rejected,
        }
        return mapping.get(decision, ArtifactStatus.approved)

    @staticmethod
    def _default_consultation_questions(artifact_name: str) -> list[str]:
        return [
            f"Vad i {artifact_name} behöver förtydligas för att fungera i praktiken?",
            "Vilka risker, beroenden eller oklarheter ser du?",
            "Vilka justeringar skulle förbättra kvaliteten inför godkännande?",
        ]

    @staticmethod
    def _summarize_text(text: str, max_length: int = 180) -> str:
        compact = re.sub(r"\s+", " ", text).strip()
        if len(compact) <= max_length:
            return compact
        return compact[: max_length - 3] + "..."

    @staticmethod
    def _update_document_status(content: str, decision: str) -> str:
        decision_to_document_status = {
            "approved": "Godkänd",
            "approved_with_notes": "Godkänd med kommentarer",
            "rejected": "Avslagen",
        }
        document_status = decision_to_document_status.get(decision)
        if not document_status:
            return content

        updated_content, replacements = re.subn(
            r"(\|\s*Status\s*\|\s*)([^|]*)(\|)",
            rf"\g<1>{document_status} \g<3>",
            content,
            count=1,
            flags=re.IGNORECASE,
        )
        return updated_content if replacements else content

    @staticmethod
    def _as_string(value: object, default: str = "") -> str:
        return value if isinstance(value, str) else default

    @staticmethod
    def _as_string_list(value: object) -> list[str]:
        if not isinstance(value, list):
            return []
        return [item for item in value if isinstance(item, str)]

    @staticmethod
    def _format_approval_feedback(decision: ApprovalDecision) -> str:
        lines = [f"Beslut: {decision.decision}"]
        if decision.summary:
            lines.append(f"Sammanfattning: {decision.summary}")
        if decision.rationale:
            lines.append(f"Motivering: {decision.rationale}")
        if decision.changes_requested:
            lines.append("Begärda ändringar:")
            lines.extend(f"- {item}" for item in decision.changes_requested)
        return "\n".join(lines)

    @staticmethod
    def _build_dry_run_filename(output_filename: str, suffix: str) -> str:
        base = Path(output_filename)
        if suffix == "prompt":
            return f"{base.stem}_prompt_dry_run.txt"
        return f"{base.stem}_{suffix}_prompt_dry_run.txt"
