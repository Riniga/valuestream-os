"""
Tests for the Orchestrator without external LLM calls.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from src.capabilities.run_workspace import RunWorkspace
from src.framework.models import (
    ActorKind,
    AgentDefinition,
    ApprovalDecision,
    ArtifactStatus,
    ConsultationResponse,
    FlowStep,
    HumanTaskStatus,
    RunStatus,
    StepStatus,
)
from src.framework.orchestration_support import update_status_cell_in_markdown_table
from src.framework.stores import (
    ApprovalStore,
    ArtifactStateStore,
    ConsultationStore,
    HumanTaskStore,
    InformedRoleBriefStore,
    RunStateStore,
)
from src.orchestration.orchestrator import HumanTaskPendingError, Orchestrator
from src.orchestration.process_loader import DEFAULT_PROCESS_FILE, ProcessFlowLoader

REPO_ROOT = Path(__file__).resolve().parents[2]


def _make_flow() -> list[FlowStep]:
    return [
        FlowStep(
            step_id="ba-vision",
            agent_id="business-analyst",
            sop_filename="02_sammanhallen_kravanalys.md",
            artifact_name="Vision & målbild",
            output_filename="vision_och_malbild.md",
            input_filenames=["beställning.md"],
        ),
        FlowStep(
            step_id="ux-journeys",
            agent_id="ux",
            sop_filename="07_user_journeys.md",
            artifact_name="User journeys",
            output_filename="user_journeys.md",
            input_filenames=["vision_och_malbild.md"],
        ),
    ]


def _make_flow_with_optional_input() -> list[FlowStep]:
    return [
        FlowStep(
            step_id="ba-vision-optional",
            agent_id="business-analyst",
            sop_filename="02_sammanhallen_kravanalys.md",
            artifact_name="Vision & målbild",
            output_filename="vision_och_malbild.md",
            input_filenames=["beställning.md"],
            optional_input_filenames=["cykelstart-brief.md"],
        )
    ]


def _make_agents() -> dict[str, AgentDefinition]:
    return {
        "business-analyst": AgentDefinition(
            agent_id="business-analyst",
            agent_file="business-analyst.md",
            raci_role_id="Business Analyst",
            actor_kind=ActorKind.automated,
        ),
        "ux": AgentDefinition(
            agent_id="ux",
            agent_file="ux.md",
            raci_role_id="UX",
            actor_kind=ActorKind.automated,
        ),
        "bestallare": AgentDefinition(
            agent_id="bestallare",
            agent_file="beställare.md",
            raci_role_id="Beställare",
            actor_kind=ActorKind.human,
        ),
        "produktagare": AgentDefinition(
            agent_id="produktagare",
            agent_file="produktägare.md",
            raci_role_id="Produktägare",
            actor_kind=ActorKind.automated,
        ),
        "verksamhetsexperter": AgentDefinition(
            agent_id="verksamhetsexperter",
            agent_file="verksamhetsexperter.md",
            raci_role_id="Verksamhetsexperter",
            actor_kind=ActorKind.automated,
        ),
        "utvecklare": AgentDefinition(
            agent_id="utvecklare",
            agent_file="utvecklare.md",
            raci_role_id="Utvecklare",
            actor_kind=ActorKind.automated,
        ),
    }


def _make_raci_flow() -> list[FlowStep]:
    return [
        FlowStep(
            step_id="ba-backlog",
            agent_id="business-analyst",
            sop_filename="02_sammanhallen_kravanalys.md",
            artifact_name="Omfattning och Strukturerad Backlog",
            output_filename="omfattning_och_strukturerad_backlog.md",
            input_filenames=["beställning.md"],
            agent_actor_kind=ActorKind.automated,
            consult_agent_ids=["verksamhetsexperter"],
            consult_actor_kinds={"verksamhetsexperter": ActorKind.automated},
            approver_agent_id="produktagare",
            approver_actor_kind=ActorKind.automated,
            informed_agent_ids=["utvecklare"],
            informed_actor_kinds={"utvecklare": ActorKind.automated},
            use_raci_workflow=True,
        )
    ]


def _make_human_responsible_flow() -> list[FlowStep]:
    return [
        FlowStep(
            step_id="bestallning",
            agent_id="bestallare",
            sop_filename="01_skapa_bestallning.md",
            artifact_name="Beställning",
            output_filename="bestallning.md",
            input_filenames=[],
            agent_actor_kind=ActorKind.human,
        )
    ]


def _make_seeded_raci_flow() -> list[FlowStep]:
    return [
        FlowStep(
            step_id="seeded-bestallning",
            agent_id="bestallare",
            sop_filename="01_skapa_bestallning.md",
            artifact_name="Beställning",
            output_filename="bestallning.md",
            input_filenames=[],
            agent_actor_kind=ActorKind.automated,
            approver_agent_id="produktagare",
            approver_actor_kind=ActorKind.automated,
            use_raci_workflow=True,
        )
    ]


@pytest.fixture()
def workspace_with_input(tmp_path) -> RunWorkspace:
    run_id = "test-run"
    input_dir = tmp_path / "runs" / run_id / "input"
    input_dir.mkdir(parents=True)
    (input_dir / "beställning.md").write_text("# Beställning\n\nTestunderlag.", encoding="utf-8")
    return RunWorkspace(run_id=run_id, repo_root=tmp_path)


@pytest.fixture()
def workspace_with_backlog_input(tmp_path) -> RunWorkspace:
    run_id = "raci-run"
    input_dir = tmp_path / "runs" / run_id / "input"
    input_dir.mkdir(parents=True)
    (input_dir / "beställning.md").write_text(
        "# Beställning\n\nPrioritera det som ger mest verksamhetsvärde.",
        encoding="utf-8",
    )
    return RunWorkspace(run_id=run_id, repo_root=tmp_path)


def test_dry_run_first_step_completes(workspace_with_input):
    orch = Orchestrator(
        workspace=workspace_with_input,
        repo_root=REPO_ROOT,
        flow_steps=_make_flow(),
        agent_definitions=_make_agents(),
    )
    results = orch.run(dry_run=True)

    assert results[0].step_id == "ba-vision"
    assert results[0].status == StepStatus.completed
    assert results[0].output_path is not None
    assert results[0].output_path.exists()


def test_dry_run_downstream_skipped_when_no_chained_input(workspace_with_input):
    orch = Orchestrator(
        workspace=workspace_with_input,
        repo_root=REPO_ROOT,
        flow_steps=_make_flow(),
        agent_definitions=_make_agents(),
    )
    results = orch.run(dry_run=True)

    assert results[1].status == StepStatus.skipped
    assert results[1].skipped_reason is not None
    assert "vision_och_malbild.md" in results[1].skipped_reason


def test_run_state_written_after_dry_run(workspace_with_input):
    orch = Orchestrator(
        workspace=workspace_with_input,
        repo_root=REPO_ROOT,
        flow_steps=_make_flow(),
        agent_definitions=_make_agents(),
    )
    orch.run(dry_run=True)

    state = RunStateStore(workspace_with_input.run_dir).load()
    assert state is not None
    assert state.status == RunStatus.completed
    assert state.step_statuses["ba-vision"] == StepStatus.completed.value


def test_artifact_state_not_updated_in_dry_run_for_non_raci_step(workspace_with_input):
    orch = Orchestrator(
        workspace=workspace_with_input,
        repo_root=REPO_ROOT,
        flow_steps=_make_flow(),
        agent_definitions=_make_agents(),
    )
    orch.run(dry_run=True)

    state = ArtifactStateStore(workspace_with_input.run_dir).load()
    assert state is not None
    assert "vision_och_malbild.md" not in state.artifacts


def test_step_skipped_when_input_missing(tmp_path):
    run_id = "no-input-run"
    (tmp_path / "runs" / run_id / "input").mkdir(parents=True)
    workspace = RunWorkspace(run_id=run_id, repo_root=tmp_path)
    orch = Orchestrator(
        workspace=workspace,
        repo_root=REPO_ROOT,
        flow_steps=_make_flow(),
        agent_definitions=_make_agents(),
    )
    results = orch.run(dry_run=True)

    assert results[0].status == StepStatus.skipped
    assert "beställning.md" in results[0].skipped_reason


def test_dry_run_prompt_contains_expected_sections(workspace_with_input):
    orch = Orchestrator(
        workspace=workspace_with_input,
        repo_root=REPO_ROOT,
        flow_steps=_make_flow()[:1],
        agent_definitions=_make_agents(),
    )
    results = orch.run(dry_run=True)

    content = results[0].output_path.read_text(encoding="utf-8")
    assert "Business Analyst" in content
    assert "Vision" in content
    assert "Designunderlag" in content
    assert "Rendermall" in content


def test_optional_input_missing_does_not_skip_step(workspace_with_input):
    orch = Orchestrator(
        workspace=workspace_with_input,
        repo_root=REPO_ROOT,
        flow_steps=_make_flow_with_optional_input(),
        agent_definitions=_make_agents(),
    )

    results = orch.run(dry_run=True)

    assert results[0].status == StepStatus.completed


def test_optional_input_is_included_when_available(tmp_path):
    run_id = "optional-input-run"
    input_dir = tmp_path / "runs" / run_id / "input"
    input_dir.mkdir(parents=True)
    (input_dir / "beställning.md").write_text("# Beställning\n\nTestunderlag.", encoding="utf-8")
    (input_dir / "cykelstart-brief.md").write_text(
        "# Cykelstart-brief\n\nHär finns frivillig input från Repeat.",
        encoding="utf-8",
    )
    workspace = RunWorkspace(run_id=run_id, repo_root=tmp_path)
    orch = Orchestrator(
        workspace=workspace,
        repo_root=REPO_ROOT,
        flow_steps=_make_flow_with_optional_input(),
        agent_definitions=_make_agents(),
    )

    results = orch.run(dry_run=True)

    assert results[0].status == StepStatus.completed
    assert results[0].output_path is not None
    prompt = results[0].output_path.read_text(encoding="utf-8")
    assert "cykelstart-brief.md" in prompt
    assert "frivillig input från Repeat" in prompt


def test_default_orchestrator_loads_process_driven_flow(workspace_with_input):
    orch = Orchestrator(
        workspace=workspace_with_input,
        repo_root=REPO_ROOT,
    )

    flow = ProcessFlowLoader(REPO_ROOT).load(DEFAULT_PROCESS_FILE)

    assert orch._process_flow.flow_id == flow.flow_id
    assert len(orch._process_flow.steps) == len(flow.steps)
    assert orch._process_flow.steps[0].sop_filename == "01_skapa_bestallning.md"


def test_process_loader_parses_optional_input_marker_for_delivery():
    flow = ProcessFlowLoader(REPO_ROOT).load("4. Leverans.md")

    assert flow.steps[0].sop_filename == "01_backlog_refinement.md"
    assert "cykelstart-brief.md" not in flow.steps[0].input_filenames
    assert "cykelstart-brief.md" in flow.steps[0].optional_input_filenames


def test_automated_product_owner_approval_completes_raci_step(workspace_with_backlog_input):
    orch = Orchestrator(
        workspace=workspace_with_backlog_input,
        repo_root=REPO_ROOT,
        flow_steps=_make_raci_flow(),
        agent_definitions=_make_agents(),
    )

    results = orch.run(dry_run=True)

    assert results[0].status == StepStatus.completed
    assert results[0].human_task_id is None

    run_state = RunStateStore(workspace_with_backlog_input.run_dir).load()
    assert run_state is not None
    assert run_state.status == RunStatus.completed

    artifact_state = ArtifactStateStore(workspace_with_backlog_input.run_dir).load()
    assert artifact_state is not None
    record = artifact_state.artifacts["omfattning_och_strukturerad_backlog.md"]
    assert record.status == ArtifactStatus.published_to_informed_roles
    assert record.approver_agent_id == "produktagare"
    assert record.approval_decision == "approved_with_notes"

def test_automated_product_owner_approval_is_persisted(workspace_with_backlog_input):
    orch = Orchestrator(
        workspace=workspace_with_backlog_input,
        repo_root=REPO_ROOT,
        flow_steps=_make_raci_flow(),
        agent_definitions=_make_agents(),
    )
    results = orch.run(dry_run=True)

    assert results[0].status == StepStatus.completed
    assert results[0].approval_decision == "approved_with_notes"

    approval_decision = ApprovalStore(workspace_with_backlog_input.run_dir).load_for_step("ba-backlog")
    assert approval_decision is not None
    assert approval_decision.actor_kind == ActorKind.automated
    assert approval_decision.decision == "approved_with_notes"

    briefs = InformedRoleBriefStore(workspace_with_backlog_input.run_dir).load_for_step("ba-backlog")
    assert len(briefs) == 1
    assert briefs[0].role_agent_id == "utvecklare"


def test_human_responsible_step_pauses_then_completes(tmp_path):
    run_id = "human-responsible"
    (tmp_path / "runs" / run_id / "input").mkdir(parents=True)
    workspace = RunWorkspace(run_id=run_id, repo_root=tmp_path)
    orch = Orchestrator(
        workspace=workspace,
        repo_root=REPO_ROOT,
        flow_steps=_make_human_responsible_flow(),
        agent_definitions=_make_agents(),
    )

    first_results = orch.run(dry_run=True)
    assert first_results[0].status == StepStatus.paused
    task_id = first_results[0].human_task_id
    assert task_id is not None

    task_store = HumanTaskStore(workspace.run_dir)
    task = task_store.load(task_id)
    assert task is not None
    task.status = HumanTaskStatus.completed
    task.response_payload = {
        "artifact_content": "# Beställning\n\nDetta är ett manuellt framtaget innehåll.",
    }
    task_store.save(task)

    resumed_results = orch.run(dry_run=True)

    assert resumed_results[0].status == StepStatus.completed
    assert resumed_results[0].output_path is not None
    assert "manuellt framtaget" in resumed_results[0].output_path.read_text(encoding="utf-8")


def test_human_responsible_step_can_resume_from_artifact_path(tmp_path):
    run_id = "human-responsible-path"
    input_dir = tmp_path / "runs" / run_id / "input"
    input_dir.mkdir(parents=True)
    workspace = RunWorkspace(run_id=run_id, repo_root=tmp_path)
    orch = Orchestrator(
        workspace=workspace,
        repo_root=REPO_ROOT,
        flow_steps=_make_human_responsible_flow(),
        agent_definitions=_make_agents(),
    )

    first_results = orch.run(dry_run=True)
    task_id = first_results[0].human_task_id
    assert task_id is not None

    artifact_path = input_dir / "bestallning.md"
    artifact_path.write_text("# Beställning\n\nInnehåll från filreferens.", encoding="utf-8")

    task_store = HumanTaskStore(workspace.run_dir)
    task = task_store.load(task_id)
    assert task is not None
    task.status = HumanTaskStatus.completed
    task.response_payload = {
        "artifact_path": str(artifact_path),
    }
    task_store.save(task)

    resumed_results = orch.run(dry_run=True)

    assert resumed_results[0].status == StepStatus.completed
    assert resumed_results[0].output_path is not None
    assert "filreferens" in resumed_results[0].output_path.read_text(encoding="utf-8")


def test_human_revision_task_describes_revision_clearly(tmp_path):
    run_id = "human-revision"
    input_dir = tmp_path / "runs" / run_id / "input"
    input_dir.mkdir(parents=True)
    workspace = RunWorkspace(run_id=run_id, repo_root=tmp_path)
    orch = Orchestrator(
        workspace=workspace,
        repo_root=REPO_ROOT,
        flow_steps=_make_human_responsible_flow(),
        agent_definitions=_make_agents(),
    )

    first_results = orch.run(dry_run=True)
    task_store = HumanTaskStore(workspace.run_dir)
    draft_task = task_store.load(first_results[0].human_task_id)
    assert draft_task is not None
    draft_task.status = HumanTaskStatus.completed
    draft_task.response_payload = {
        "artifact_content": "# Beställning\n\nFörsta version.",
    }
    task_store.save(draft_task)

    step = _make_human_responsible_flow()[0]
    import asyncio

    with pytest.raises(HumanTaskPendingError):
        asyncio.run(
            orch._run_revision_phase(
                step=step,
                dry_run=True,
                input_content={},
                existing_content="# Beställning\n\nFörsta version.",
                consultation_feedback={"verksamhetsexperter": "Förtydliga målbilden."},
                approval_feedback="",
                dry_run_suffix="revision",
            )
        )

    revision_task = task_store.load_for_step_and_phase(step.step_id, "revision", step.agent_id)
    assert revision_task is not None
    assert revision_task.task_kind == "responsible"
    assert "Uppdatera artefakten" in revision_task.action_required
    assert "nästa kontrollsteg" in revision_task.next_step_hint


def test_human_responsible_step_uses_existing_run_input_file_when_completed(tmp_path):
    run_id = "human-responsible-fallback"
    input_dir = tmp_path / "runs" / run_id / "input"
    input_dir.mkdir(parents=True)
    workspace = RunWorkspace(run_id=run_id, repo_root=tmp_path)
    orch = Orchestrator(
        workspace=workspace,
        repo_root=REPO_ROOT,
        flow_steps=_make_human_responsible_flow(),
        agent_definitions=_make_agents(),
    )

    first_results = orch.run(dry_run=True)
    task_id = first_results[0].human_task_id
    assert task_id is not None

    (input_dir / "bestallning.md").write_text(
        "# Beställning\n\nInnehåll från befintlig input-fil.",
        encoding="utf-8",
    )

    task_store = HumanTaskStore(workspace.run_dir)
    task = task_store.load(task_id)
    assert task is not None
    task.status = HumanTaskStatus.completed
    task.response_payload = {}
    task_store.save(task)

    resumed_results = orch.run(dry_run=True)

    assert resumed_results[0].status == StepStatus.completed
    assert resumed_results[0].output_path is not None
    assert "befintlig input-fil" in resumed_results[0].output_path.read_text(encoding="utf-8")


def test_raci_step_uses_seeded_artifact_from_input_dir(tmp_path):
    run_id = "seeded-raci"
    input_dir = tmp_path / "runs" / run_id / "input"
    input_dir.mkdir(parents=True)
    seeded_content = "# Beställning\n\nDetta innehåll kommer från förinlagd bestallning.md."
    (input_dir / "bestallning.md").write_text(seeded_content, encoding="utf-8")
    workspace = RunWorkspace(run_id=run_id, repo_root=tmp_path)
    orch = Orchestrator(
        workspace=workspace,
        repo_root=REPO_ROOT,
        flow_steps=_make_seeded_raci_flow(),
        agent_definitions=_make_agents(),
    )

    results = orch.run(dry_run=True)

    assert results[0].status == StepStatus.completed
    assert results[0].output_path is not None
    assert results[0].output_path.read_text(encoding="utf-8") == seeded_content


def test_raci_step_reports_missing_expected_seeded_artifact_filename(tmp_path):
    run_id = "seeded-raci-missing"
    input_dir = tmp_path / "runs" / run_id / "input"
    input_dir.mkdir(parents=True)
    (input_dir / "beställning.md").write_text("# Beställning\n\nFel filnamn.", encoding="utf-8")
    workspace = RunWorkspace(run_id=run_id, repo_root=tmp_path)
    orch = Orchestrator(
        workspace=workspace,
        repo_root=REPO_ROOT,
        flow_steps=_make_seeded_raci_flow(),
        agent_definitions=_make_agents(),
    )

    results = orch.run(dry_run=True)

    assert results[0].status == StepStatus.failed
    assert results[0].error is not None
    assert "bestallning.md" in results[0].error
    assert "beställning.md" in results[0].error
    assert "saknas" in results[0].error


def test_update_document_status_maps_approval_decisions():
    content = (
        "# Prioriterad backlog\n\n"
        "## Metadata\n"
        "| Fält | Värde |\n"
        "|------|------|\n"
        "| Status | Pågående |\n"
    )

    approved = update_status_cell_in_markdown_table(content, "approved")
    approved_with_notes = update_status_cell_in_markdown_table(content, "approved_with_notes")
    rejected = update_status_cell_in_markdown_table(content, "rejected")

    assert "| Status | Godkänd |" in approved
    assert "| Status | Godkänd med kommentarer |" in approved_with_notes
    assert "| Status | Avslagen |" in rejected


def test_expert_context_is_filtered_to_same_artifact(workspace_with_backlog_input):
    orch = Orchestrator(
        workspace=workspace_with_backlog_input,
        repo_root=REPO_ROOT,
        flow_steps=_make_raci_flow(),
        agent_definitions=_make_agents(),
    )
    step = _make_raci_flow()[0]

    orch._approval_store.append(
        ApprovalDecision(
            step_id="same-artifact",
            artifact_name="Omfattning och Strukturerad Backlog",
            artifact_filename="omfattning_och_strukturerad_backlog.md",
            approver_agent_id="produktagare",
            decision="approved_with_notes",
            summary="Behov av förtydligad MVP.",
            actor_kind=ActorKind.automated,
        )
    )
    orch._approval_store.append(
        ApprovalDecision(
            step_id="other-artifact",
            artifact_name="Vision & målbild",
            artifact_filename="vision_och_malbild.md",
            approver_agent_id="produktagare",
            decision="approved",
            summary="Annan artefakt ska inte läcka in.",
            actor_kind=ActorKind.automated,
        )
    )
    orch._consultation_store.append_response(
        ConsultationResponse(
            request_id="req-1",
            step_id="same-artifact",
            artifact_name="Omfattning och Strukturerad Backlog",
            consultant_agent_id="verksamhetsexperter",
            response_text="Förtydliga beroenden.",
            summary="Förtydliga beroenden.",
        )
    )
    orch._consultation_store.append_response(
        ConsultationResponse(
            request_id="req-2",
            step_id="other-artifact",
            artifact_name="Vision & målbild",
            consultant_agent_id="verksamhetsexperter",
            response_text="Annat svar.",
            summary="Annat svar.",
        )
    )

    context = orch._build_expert_context(
        step=step,
        consultant_agent_id="verksamhetsexperter",
        input_content={"beställning.md": "Beställningstext"},
    )

    assert "Omfattning och Strukturerad Backlog" in context.context_text
    assert "Förtydliga beroenden." in context.context_text
    assert "Behov av förtydligad MVP." in context.context_text
    assert "Annan artefakt ska inte läcka in." not in context.context_text
