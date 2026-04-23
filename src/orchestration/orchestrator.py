"""
Central orchestrator for the Agent Orchestration Framework.

Supports both automated and human actors. Human work is handed off through
transparent JSON task files under runs/<run-id>/human_tasks/.
"""
from __future__ import annotations

import asyncio
import shutil
from collections.abc import AsyncGenerator
from pathlib import Path
from uuid import uuid4

from src.capabilities.run_workspace import RunWorkspace
from src.framework.context_loader import AgentContextLoader
from src.framework.maf_adapter import AgentRunner
from src.framework.models import (
    ActorKind,
    AgentDefinition,
    ApprovalDecision,
    ArtifactState,
    ArtifactStatus,
    ConsultationRequest,
    ConsultationResponse,
    ExpertContext,
    FlowStep,
    HumanTask,
    HumanTaskStatus,
    InformedRoleBrief,
    ProcessFlow,
    RunState,
    RunStatus,
    StepResult,
    StepStatus,
)
from src.framework.orchestration_support import (
    build_dry_run_output_filename,
    default_consultation_questions,
    format_approval_feedback_for_revision,
    map_approval_decision_to_artifact_status,
    parse_approval_decision_from_llm_text,
    summarize_plain_text,
    update_status_cell_in_markdown_table,
)
from src.framework.prompt_builder import FrameworkPromptBuilder
from src.framework.stores import (
    ApprovalStore,
    ArtifactStateStore,
    ConsultationStore,
    ExpertContextStore,
    HumanTaskStore,
    InformedRoleBriefStore,
    RunLog,
    RunStateStore,
)
from src.orchestration.agent_registry import load_agent_definitions
from src.orchestration.output_index import publish_output_index
from src.orchestration.process_loader import DEFAULT_PROCESS_FILE, ProcessFlowLoader


class HumanTaskPendingError(RuntimeError):
    """Raised when orchestration must pause for a human task."""

    def __init__(self, task: HumanTask, task_path: Path) -> None:
        super().__init__(f"Avvaktar mänsklig uppgift: {task.task_id}")
        self.task = task
        self.task_path = task_path


class Orchestrator:
    """Runs a process-driven multi-actor flow for a given run workspace."""

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
        self._agents = agent_definitions if agent_definitions is not None else load_agent_definitions(repo_root)
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
        self._human_task_store = HumanTaskStore(run_dir)
        self._log = RunLog(run_dir)

    def run(self, dry_run: bool = False) -> list[StepResult]:
        return asyncio.run(self.run_async(dry_run=dry_run))

    async def run_async(self, dry_run: bool = False) -> list[StepResult]:
        return [result async for result in self.run_stream_async(dry_run=dry_run)]

    async def run_stream_async(self, dry_run: bool = False) -> AsyncGenerator[StepResult, None]:
        run_state, artifact_state, is_resume = self._load_or_initialize_state()
        run_state.status = RunStatus.running
        self._run_state_store.save(run_state)
        self._log.append(
            {
                "event": "run_resumed" if is_resume else "run_started",
                "run_id": self._workspace.run_id,
                "dry_run": dry_run,
            }
        )

        for step in self._steps:
            prior_status = run_state.step_statuses.get(step.step_id, StepStatus.pending.value)
            if prior_status == StepStatus.completed.value:
                continue

            result = await self._run_step_async(step, run_state, artifact_state, dry_run=dry_run)
            self._publish_output_index(run_state)
            yield result

            if result.status == StepStatus.failed:
                run_state.status = RunStatus.failed
                self._run_state_store.save(run_state)
                self._log.append({"event": "run_failed", "step_id": step.step_id})
                self._publish_output_index(run_state)
                break

            if result.status == StepStatus.paused:
                run_state.status = RunStatus.paused
                self._run_state_store.save(run_state)
                self._log.append(
                    {
                        "event": "run_paused",
                        "step_id": step.step_id,
                        "human_task_id": result.human_task_id,
                    }
                )
                self._publish_output_index(run_state)
                break

        if run_state.status == RunStatus.running:
            run_state.status = RunStatus.completed
            run_state.current_step_id = None
            run_state.current_phase = None
            run_state.pending_human_task_id = None
            self._run_state_store.save(run_state)
            self._log.append({"event": "run_finished", "status": run_state.status.value})
            self._publish_output_index(run_state)

    def _load_or_initialize_state(self) -> tuple[RunState, ArtifactState, bool]:
        existing_run_state = self._run_state_store.load()
        existing_artifact_state = self._artifact_state_store.load()
        if (
            existing_run_state is not None
            and existing_run_state.status == RunStatus.paused
            and existing_run_state.flow_id == self._process_flow.flow_id
        ):
            return (
                existing_run_state,
                existing_artifact_state or self._artifact_state_store.initialize(self._workspace.run_id),
                True,
            )

        return (
            self._run_state_store.initialize(
                run_id=self._workspace.run_id,
                flow_id=self._process_flow.flow_id,
                process_file=self._process_flow.process_file,
                step_ids=[step.step_id for step in self._steps],
            ),
            self._artifact_state_store.initialize(run_id=self._workspace.run_id),
            False,
        )

    async def _run_step_async(
        self,
        step: FlowStep,
        run_state: RunState,
        artifact_state: ArtifactState,
        dry_run: bool,
    ) -> StepResult:
        run_state.current_step_id = step.step_id
        run_state.current_phase = "draft" if step.use_raci_workflow else None
        run_state.pending_human_task_id = None
        run_state.step_statuses[step.step_id] = StepStatus.running.value
        self._run_state_store.save(run_state)

        missing = self._workspace.validate_input(step.input_filenames)
        if missing:
            reason = f"Saknar input: {', '.join(missing)}"
            run_state.step_statuses[step.step_id] = StepStatus.skipped.value
            self._run_state_store.save(run_state)
            self._log.append({"event": "step_skipped", "step_id": step.step_id, "reason": reason})
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
            if step.use_raci_workflow:
                output_path, approval_decision = await self._execute_raci_step_async(
                    step,
                    run_state,
                    artifact_state,
                    dry_run=dry_run,
                )
            else:
                output_path = await self._execute_step_async(step, dry_run=dry_run)
        except HumanTaskPendingError as exc:
            run_state.status = RunStatus.paused
            run_state.current_phase = exc.task.phase
            run_state.pending_human_task_id = exc.task.task_id
            run_state.step_statuses[step.step_id] = StepStatus.paused.value
            self._artifact_state_store.record_status(
                artifact_state,
                step.output_filename,
                step.artifact_name,
                step.step_id,
                ArtifactStatus.awaiting_human_input,
                agent_actor_kind=step.agent_actor_kind,
                consult_agent_ids=step.consult_agent_ids,
                consult_actor_kinds=step.consult_actor_kinds,
                approver_agent_id=step.approver_agent_id,
                approver_actor_kind=step.approver_actor_kind,
                informed_agent_ids=step.informed_agent_ids,
                informed_actor_kinds=step.informed_actor_kinds,
                latest_phase=exc.task.phase,
                pending_human_task_id=exc.task.task_id,
                pending_human_phase=exc.task.phase,
            )
            self._run_state_store.save(run_state)
            self._log.append(
                {
                    "event": "human_task_pending",
                    "step_id": step.step_id,
                    "human_task_id": exc.task.task_id,
                    "phase": exc.task.phase,
                    "path": str(exc.task_path),
                }
            )
            return StepResult(
                step_id=step.step_id,
                agent_id=step.agent_id,
                artifact_name=step.artifact_name,
                status=StepStatus.paused,
                delprocess_title=step.delprocess_title,
                phase=exc.task.phase,
                human_task_id=exc.task.task_id,
                human_task_path=exc.task_path,
            )
        except Exception as exc:  # noqa: BLE001
            error_msg = f"{type(exc).__name__}: {exc}"
            run_state.step_statuses[step.step_id] = StepStatus.failed.value
            run_state.current_phase = None
            run_state.pending_human_task_id = None
            self._artifact_state_store.record_failed(
                artifact_state,
                step.output_filename,
                step.artifact_name,
                step.step_id,
            )
            self._run_state_store.save(run_state)
            self._log.append({"event": "step_failed", "step_id": step.step_id, "error": error_msg})
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
        run_state.pending_human_task_id = None
        self._run_state_store.save(run_state)
        try:
            output_rel = str(output_path.relative_to(self._repo_root))
        except ValueError:
            output_rel = str(output_path)
        self._log.append(
            {
                "event": "step_completed",
                "step_id": step.step_id,
                "artifact": step.artifact_name,
                "output": output_rel,
                "dry_run": dry_run,
                "approval_decision": approval_decision,
            }
        )
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
        seeded_artifact = self._load_seeded_artifact(step)
        if seeded_artifact is not None:
            _, path = seeded_artifact
            return path

        if step.agent_actor_kind == ActorKind.human:
            _, path = await self._run_human_responsible_phase(step=step, dry_run=dry_run)
            return path

        loader = self._make_loader(step.agent_id)
        role_text = loader.load_role()
        sop = loader.load_sop(step.sop_filename)
        description = loader.load_artifact_description(step.artifact_name)
        template = loader.load_artifact_template(step.output_filename)
        input_content = self._read_step_inputs(step)

        if self._workspace.output_exists(step.output_filename) and not dry_run:
            existing = self._workspace.read_output(step.output_filename)
            prompt = self._prompt_builder.build_update_prompt(
                role_name=loader.raci_role,
                role_text=role_text,
                sop_text=sop.content,
                artifact_description=description,
                artifact_template=template,
                input_content=input_content,
                existing_content=existing,
            )
        else:
            prompt = self._prompt_builder.build_generate_prompt(
                role_name=loader.raci_role,
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
        revised_content, revised_path = draft_content, draft_path
        self._artifact_state_store.record_status(
            artifact_state,
            step.output_filename,
            step.artifact_name,
            step.step_id,
            ArtifactStatus.draft,
            agent_actor_kind=step.agent_actor_kind,
            consult_agent_ids=step.consult_agent_ids,
            consult_actor_kinds=step.consult_actor_kinds,
            approver_agent_id=step.approver_agent_id,
            approver_actor_kind=step.approver_actor_kind,
            informed_agent_ids=step.informed_agent_ids,
            informed_actor_kinds=step.informed_actor_kinds,
            latest_phase="draft",
            pending_human_task_id="",
            pending_human_phase="",
        )

        consultation_feedback: dict[str, str] = {}
        if step.consult_agent_ids:
            self._set_phase(run_state, step, "consultation")
            request = ConsultationRequest(
                request_id=str(uuid4()),
                step_id=step.step_id,
                artifact_name=step.artifact_name,
                artifact_filename=step.output_filename,
                requester_agent_id=step.agent_id,
                consultant_agent_ids=step.consult_agent_ids,
                questions=default_consultation_questions(step.artifact_name),
                draft_summary=summarize_plain_text(draft_content),
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
                pending_human_task_id="",
                pending_human_phase="",
            )

            if consultation_feedback:
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
                    pending_human_task_id="",
                    pending_human_phase="",
                )

        decision: ApprovalDecision | None = None
        mapped_status = ArtifactStatus.produced
        if step.approver_agent_id:
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
            mapped_status = map_approval_decision_to_artifact_status(decision.decision)
            self._artifact_state_store.record_status(
                artifact_state,
                step.output_filename,
                step.artifact_name,
                step.step_id,
                mapped_status,
                latest_phase="approval",
                approval_decision=decision.decision,
                pending_human_task_id="",
                pending_human_phase="",
            )
            if decision.decision == "rejected":
                raise RuntimeError(
                    f"Artifakten {step.artifact_name} avslogs av {step.approver_agent_id}: "
                    f"{decision.summary or decision.rationale}"
                )

            if decision.decision == "approved_with_notes" and decision.changes_requested:
                self._set_phase(run_state, step, "approval_revision")
                revised_content, revised_path = await self._run_revision_phase(
                    step=step,
                    dry_run=dry_run,
                    input_content=input_content,
                    existing_content=revised_content,
                    consultation_feedback=consultation_feedback,
                    approval_feedback=format_approval_feedback_for_revision(decision),
                    dry_run_suffix="approval_revision",
                )

            if not dry_run:
                revised_content = update_status_cell_in_markdown_table(revised_content, decision.decision)
                revised_path = self._workspace.write_output(step.output_filename, revised_content)

        if step.informed_agent_ids:
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
                ArtifactStatus.published_to_informed_roles,
                latest_phase="informing",
                approval_decision=decision.decision if decision is not None else None,
                pending_human_task_id="",
                pending_human_phase="",
            )
        elif decision is None:
            self._artifact_state_store.record_status(
                artifact_state,
                step.output_filename,
                step.artifact_name,
                step.step_id,
                mapped_status,
                latest_phase="revision" if consultation_feedback else "draft",
                pending_human_task_id="",
                pending_human_phase="",
            )

        if not dry_run:
            dest = self._workspace.input_dir / step.output_filename
            shutil.copy(revised_path, dest)

        return revised_path, decision.decision if decision is not None else None

    async def _run_draft_phase(
        self,
        step: FlowStep,
        dry_run: bool,
        input_content: dict[str, str],
    ) -> tuple[str, Path]:
        seeded_artifact = self._load_seeded_artifact(step)
        if seeded_artifact is not None:
            return seeded_artifact

        if step.agent_actor_kind == ActorKind.human:
            return await self._run_human_responsible_phase(step=step, dry_run=dry_run)

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
            actor_kind = step.consult_actor_kinds.get(consultant_agent_id, ActorKind.automated)
            if actor_kind == ActorKind.human:
                response_text = self._collect_human_consultation_response(
                    step=step,
                    consultant_agent_id=consultant_agent_id,
                    artifact_content=artifact_content,
                    request=request,
                    input_content=input_content,
                )
            else:
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
                    summary=summarize_plain_text(response_text),
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
        if step.agent_actor_kind == ActorKind.human:
            return await self._run_human_responsible_phase(
                step=step,
                dry_run=dry_run,
                existing_content=existing_content,
                consultation_feedback=consultation_feedback,
                approval_feedback=approval_feedback,
                phase=dry_run_suffix,
            )

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
        approver_actor_kind = step.approver_actor_kind or ActorKind.automated
        if approver_actor_kind == ActorKind.human:
            return self._collect_human_approval_decision(
                step=step,
                approver_agent_id=approver_agent_id,
                artifact_content=artifact_content,
                consultation_feedback=consultation_feedback,
            )

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
        return parse_approval_decision_from_llm_text(
            step_id=step.step_id,
            artifact_name=step.artifact_name,
            artifact_filename=step.output_filename,
            approver_agent_id=approver_agent_id,
            raw_text=approval_text,
            dry_run=dry_run,
        )

    async def _run_informing_phase(
        self,
        step: FlowStep,
        dry_run: bool,
        artifact_content: str,
        decision: ApprovalDecision | None,
    ) -> None:
        decision_summary = (
            decision.summary or decision.rationale or decision.decision
            if decision is not None
            else "Artefakten är färdigställd och tillgänglig för kännedom."
        )
        for informed_agent_id in step.informed_agent_ids:
            actor_kind = step.informed_actor_kinds.get(informed_agent_id, ActorKind.automated)
            if actor_kind == ActorKind.human:
                brief_text = self._deliver_human_informing_task(
                    step=step,
                    informed_agent_id=informed_agent_id,
                    artifact_content=artifact_content,
                    decision_summary=decision_summary,
                )
            else:
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
                    actor_kind=actor_kind,
                    relevance=summarize_plain_text(brief_text),
                )
            )

    async def _run_human_responsible_phase(
        self,
        step: FlowStep,
        dry_run: bool,
        existing_content: str = "",
        consultation_feedback: dict[str, str] | None = None,
        approval_feedback: str = "",
        phase: str = "draft",
    ) -> tuple[str, Path]:
        loader = self._make_loader(step.agent_id)
        sop = loader.load_sop(step.sop_filename)
        request_payload = {
            "phase": phase,
            "task_kind": "responsible",
            "artifact_name": step.artifact_name,
            "artifact_filename": step.output_filename,
            "suggested_artifact_path": str(self._workspace.input_path(step.output_filename)),
            "action_required": self._describe_human_responsible_action(phase),
            "role_name": loader.raci_role,
            "dry_run": dry_run,
            "sop_text": sop.content,
            "role_text": loader.load_role(),
            "artifact_description": loader.load_artifact_description(step.artifact_name),
            "artifact_template": loader.load_artifact_template(step.output_filename),
            "input_content": self._read_step_inputs(step),
            "existing_content": existing_content,
            "consultation_feedback": consultation_feedback or {},
            "approval_feedback": approval_feedback,
            "instructions": (
                "Antingen: 1) fyll i response_payload.artifact_content med det kompletta "
                "artefaktinnehållet, eller 2) ange response_payload.artifact_path som pekar på "
                "en fil. Sätt sedan toppnivåfältet status till 'completed' för att låta "
                "körningen fortsätta."
            ),
            "next_step_hint": self._describe_human_responsible_next_step(phase),
        }
        task = self._require_human_task(
            step=step,
            phase=phase,
            agent_id=step.agent_id,
            request_payload=request_payload,
        )
        artifact_content = self._resolve_human_artifact_content(task, step.output_filename)
        path = self._workspace.write_output(step.output_filename, artifact_content)
        return artifact_content, path

    def _collect_human_consultation_response(
        self,
        step: FlowStep,
        consultant_agent_id: str,
        artifact_content: str,
        request: ConsultationRequest,
        input_content: dict[str, str],
    ) -> str:
        loader = self._make_loader(consultant_agent_id)
        expert_context = self._build_expert_context(step, consultant_agent_id, input_content)
        task = self._require_human_task(
            step=step,
            phase="consultation",
            agent_id=consultant_agent_id,
            request_payload={
                "task_kind": "consultation",
                "artifact_name": step.artifact_name,
                "artifact_filename": step.output_filename,
                "role_name": loader.raci_role,
                "action_required": "Lämna återkoppling och rekommenderade ändringar.",
                "artifact_content": artifact_content,
                "questions": request.questions,
                "expert_context": expert_context.context_text,
                "instructions": (
                    "Fyll i response_payload.response_text med din återkoppling "
                    "och sätt toppnivåfältet status till 'completed'."
                ),
                "next_step_hint": "När återkopplingen är sparad kan ansvarig roll revidera artefakten.",
            },
        )
        response_text = task.response_payload.get("response_text")
        if not isinstance(response_text, str) or not response_text.strip():
            raise ValueError(
                f"Mänsklig konsultationsuppgift '{task.task_id}' saknar response_payload.response_text"
            )
        return response_text

    def _collect_human_approval_decision(
        self,
        step: FlowStep,
        approver_agent_id: str,
        artifact_content: str,
        consultation_feedback: dict[str, str],
    ) -> ApprovalDecision:
        loader = self._make_loader(approver_agent_id)
        task = self._require_human_task(
            step=step,
            phase="approval",
            agent_id=approver_agent_id,
            request_payload={
                "task_kind": "approval",
                "artifact_name": step.artifact_name,
                "artifact_filename": step.output_filename,
                "role_name": loader.raci_role,
                "action_required": "Godkänn, godkänn med kommentarer eller avslå artefakten.",
                "artifact_content": artifact_content,
                "consultation_feedback": consultation_feedback,
                "instructions": (
                    "Sätt toppnivåfältet status till 'completed' och fyll i "
                    "response_payload.decision med 'approved', 'approved_with_notes' eller "
                    "'rejected'."
                ),
                "next_step_hint": (
                    "Om du väljer approved_with_notes eller rejected bör du även ange "
                    "summary, rationale och eventuella changes_requested."
                ),
            },
        )
        decision = task.response_payload.get("decision")
        if decision not in {"approved", "approved_with_notes", "rejected"}:
            raise ValueError(
                f"Mänsklig approval-uppgift '{task.task_id}' måste ange response_payload.decision"
            )
        changes_requested = task.response_payload.get("changes_requested", [])
        if not isinstance(changes_requested, list):
            changes_requested = []
        return ApprovalDecision(
            step_id=step.step_id,
            artifact_name=step.artifact_name,
            artifact_filename=step.output_filename,
            approver_agent_id=approver_agent_id,
            decision=decision,
            actor_kind=ActorKind.human,
            summary=self._coerce_string(task.response_payload.get("summary")),
            rationale=self._coerce_string(task.response_payload.get("rationale")),
            changes_requested=[item for item in changes_requested if isinstance(item, str)],
        )

    def _deliver_human_informing_task(
        self,
        step: FlowStep,
        informed_agent_id: str,
        artifact_content: str,
        decision_summary: str,
    ) -> str:
        loader = self._make_loader(informed_agent_id)
        brief_text = (
            f"Information till {loader.raci_role}\n\n"
            f"Artefakt: {step.artifact_name}\n"
            f"Fil: {step.output_filename}\n\n"
            f"Beslut/sammanfattning:\n{decision_summary}\n\n"
            f"Innehåll:\n{artifact_content}\n"
        )
        task_id = f"{step.step_id}-informing-{informed_agent_id}"
        existing = self._human_task_store.load(task_id)
        task = existing or HumanTask(
            task_id=task_id,
            step_id=step.step_id,
            artifact_name=step.artifact_name,
            artifact_filename=step.output_filename,
            agent_id=informed_agent_id,
            role_name=loader.raci_role,
            phase="informing",
            status=HumanTaskStatus.completed,
            request_payload={
                "task_kind": "informing",
                "artifact_name": step.artifact_name,
                "artifact_filename": step.output_filename,
                "brief_text": brief_text,
            },
            response_payload={},
            completion_summary="Informationsuppgift skapad.",
        )
        task.status = HumanTaskStatus.completed
        task.completion_summary = "Informationsuppgift skapad."
        self._human_task_store.save(task)
        return brief_text

    def _require_human_task(
        self,
        step: FlowStep,
        phase: str,
        agent_id: str,
        request_payload: dict[str, object],
    ) -> HumanTask:
        existing = self._human_task_store.load_for_step_and_phase(step.step_id, phase, agent_id)
        if existing is None:
            loader = self._make_loader(agent_id)
            task = HumanTask(
                task_id=f"{step.step_id}-{phase}-{agent_id}",
                step_id=step.step_id,
                artifact_name=step.artifact_name,
                artifact_filename=step.output_filename,
                agent_id=agent_id,
                role_name=loader.raci_role,
                phase=phase,
                task_kind=self._coerce_string(request_payload.get("task_kind")),
                action_required=self._coerce_string(request_payload.get("action_required")),
                next_step_hint=self._coerce_string(request_payload.get("next_step_hint")),
                status=HumanTaskStatus.pending,
                request_payload=request_payload,
                response_payload={},
            )
            task_path = self._human_task_store.save(task)
            raise HumanTaskPendingError(task, task_path)

        if existing.status != HumanTaskStatus.completed:
            raise HumanTaskPendingError(existing, self._human_task_store.path_for(existing.task_id))

        return existing

    def _make_loader(self, agent_id: str) -> AgentContextLoader:
        if agent_id not in self._agents:
            raise KeyError(f"Okänd agent_id i orkestreringen: {agent_id}")
        agent_def = self._agents[agent_id]
        return AgentContextLoader(
            repo_root=self._repo_root,
            agent_file=agent_def.agent_file,
            raci_role_id=agent_def.raci_role_id,
        )

    def _read_step_inputs(self, step: FlowStep) -> dict[str, str]:
        all_input_filenames = step.input_filenames + step.optional_input_filenames
        return {
            filename: self._workspace.read_input(filename)
            for filename in all_input_filenames
            if self._workspace.input_path(filename).exists()
        }

    def _load_seeded_artifact(self, step: FlowStep) -> tuple[str, Path] | None:
        if step.input_filenames:
            return None

        expected_path = self._workspace.input_path(step.output_filename)
        if expected_path.is_file():
            content = expected_path.read_text(encoding="utf-8")
            return content, self._workspace.write_output(step.output_filename, content)

        available_markdown_files = sorted(path.name for path in self._workspace.input_dir.glob("*.md"))
        if available_markdown_files:
            available_list = ", ".join(available_markdown_files)
            raise FileNotFoundError(
                f"Artifakt med namn '{step.output_filename}' saknas i input-mappen "
                f"'{self._workspace.input_dir}'. Tillgängliga filer: {available_list}"
            )

        return None

    async def _run_agent_prompt_async(
        self,
        agent_id: str,
        prompt: str,
        dry_run: bool,
        output_filename: str,
        dry_run_suffix: str,
    ) -> tuple[str, Path]:
        if dry_run:
            dry_run_filename = build_dry_run_output_filename(output_filename, dry_run_suffix)
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

    @staticmethod
    def _coerce_string(value: object) -> str:
        return value if isinstance(value, str) else ""

    def _publish_output_index(self, run_state: RunState) -> None:
        publish_output_index(
            repo_root=self._repo_root,
            workspace=self._workspace,
            run_state=run_state,
        )

    @staticmethod
    def _describe_human_responsible_action(phase: str) -> str:
        if phase == "draft":
            return "Skapa första versionen av artefakten."
        if phase in {"revision", "approval_revision"}:
            return "Uppdatera artefakten utifrån mottagen feedback."
        return "Uppdatera eller komplettera artefakten."

    @staticmethod
    def _describe_human_responsible_next_step(phase: str) -> str:
        if phase == "draft":
            return "När artefakten är klar går den vidare till konsultation och eventuellt godkännande."
        if phase in {"revision", "approval_revision"}:
            return "När revideringen är klar går artefakten vidare till nästa kontrollsteg."
        return "När uppgiften är slutförd återupptas orkestreringen från denna fas."

    def _resolve_human_artifact_content(self, task: HumanTask, artifact_filename: str) -> str:
        inline_content = task.response_payload.get("artifact_content")
        if isinstance(inline_content, str) and inline_content.strip():
            return inline_content

        artifact_path_value = task.response_payload.get("artifact_path")
        if isinstance(artifact_path_value, str) and artifact_path_value.strip():
            path = self._resolve_human_artifact_path(artifact_path_value)
            if path.is_file():
                return path.read_text(encoding="utf-8")
            raise FileNotFoundError(
                f"Mänsklig uppgift '{task.task_id}' pekar på en saknad fil: {path}"
            )

        # Convenience fallback: if the human has already placed the artifact in the run input/output,
        # allow the run to continue as soon as the task itself is marked completed.
        fallback_candidates = [
            self._workspace.input_path(artifact_filename),
            self._workspace.output_path(artifact_filename),
        ]
        for candidate in fallback_candidates:
            if candidate.is_file():
                return candidate.read_text(encoding="utf-8")

        raise ValueError(
            f"Mänsklig uppgift '{task.task_id}' saknar response_payload.artifact_content "
            f"eller response_payload.artifact_path"
        )

    def _resolve_human_artifact_path(self, artifact_path: str) -> Path:
        candidate = Path(artifact_path)
        if candidate.is_absolute():
            return candidate

        repo_relative = self._repo_root / candidate
        if repo_relative.exists():
            return repo_relative

        run_relative = self._workspace.run_dir / candidate
        if run_relative.exists():
            return run_relative

        return repo_relative
