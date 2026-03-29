"""
Tests for the Orchestrator — without LLM calls.

Uses dry_run=True throughout so no network connection is needed.
Verifies step sequencing, input validation, state updates,
artifact chaining, and skip/fail behaviour.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from src.capabilities.run_workspace import RunWorkspace
from src.framework.models import (
    AgentDefinition,
    ArtifactStatus,
    FlowStep,
    RunStatus,
    StepStatus,
)
from src.framework.stores import (
    ApprovalStore,
    ArtifactStateStore,
    ConsultationStore,
    InformedRoleBriefStore,
    RunStateStore,
)
from src.orchestration.orchestrator import Orchestrator
from src.orchestration.process_loader import DEFAULT_PROCESS_FILE, ProcessFlowLoader

REPO_ROOT = Path(__file__).resolve().parents[2]


def _make_flow() -> list[FlowStep]:
    return [
        FlowStep(
            step_id="ba-vision",
            agent_id="business-analyst",
            sop_filename="01_vision_och_malbild.md",
            artifact_name="Vision & målbild",
            output_filename="vision_och_malbild.md",
            input_filenames=["overgripande_behov.md"],
        ),
        FlowStep(
            step_id="ux-journeys",
            agent_id="ux",
            sop_filename="07_user_journeys.md",
            artifact_name="User journeys",
            output_filename="user_journeys.md",
            input_filenames=["vision_och_malbild.md", "overgripande_behov.md"],
        ),
        FlowStep(
            step_id="ba-storymap",
            agent_id="business-analyst",
            sop_filename="08_skapa_story_map.md",
            artifact_name="Story map",
            output_filename="story_map.md",
            input_filenames=["user_journeys.md", "vision_och_malbild.md"],
        ),
    ]


def _make_agents() -> dict[str, AgentDefinition]:
    return {
        "business-analyst": AgentDefinition(
            agent_id="business-analyst",
            agent_file="business-analyst.md",
            raci_role_id="Business Analyst",
        ),
        "ux": AgentDefinition(
            agent_id="ux",
            agent_file="ux.md",
            raci_role_id="UX",
        ),
        "produktagare": AgentDefinition(
            agent_id="produktagare",
            agent_file="produktägare.md",
            raci_role_id="Produktägare",
        ),
        "verksamhetsexperter": AgentDefinition(
            agent_id="verksamhetsexperter",
            agent_file="verksamhetsexperter.md",
            raci_role_id="Verksamhetsexperter",
        ),
        "utvecklare": AgentDefinition(
            agent_id="utvecklare",
            agent_file="utvecklare.md",
            raci_role_id="Utvecklare",
        ),
    }


def _make_raci_flow() -> list[FlowStep]:
    return [
        FlowStep(
            step_id="ba-backlog",
            agent_id="business-analyst",
            sop_filename="10_prioritera_backlog.md",
            artifact_name="Prioriterad backlog",
            output_filename="prioriterad_backlog.md",
            input_filenames=["epics_och_capabilities.md", "vision_och_malbild.md"],
            consult_agent_ids=["verksamhetsexperter"],
            approver_agent_id="produktagare",
            informed_agent_ids=["utvecklare"],
            use_raci_workflow=True,
        )
    ]


@pytest.fixture()
def workspace_with_input(tmp_path) -> RunWorkspace:
    run_id = "test-run"
    input_dir = tmp_path / "runs" / run_id / "input"
    input_dir.mkdir(parents=True)

    sample = REPO_ROOT / "runs" / "demo-001" / "input" / "overgripande_behov.md"
    if sample.exists():
        shutil.copy(sample, input_dir / "overgripande_behov.md")
    else:
        (input_dir / "overgripande_behov.md").write_text("# Test behov\n- Behov A", encoding="utf-8")

    return RunWorkspace(run_id=run_id, repo_root=tmp_path)


@pytest.fixture()
def workspace_with_backlog_input(tmp_path) -> RunWorkspace:
    run_id = "raci-run"
    input_dir = tmp_path / "runs" / run_id / "input"
    input_dir.mkdir(parents=True)

    (input_dir / "epics_och_capabilities.md").write_text(
        "# Epics & Capabilities\n\n## Capability\n- Hantera prioritering",
        encoding="utf-8",
    )
    (input_dir / "vision_och_malbild.md").write_text(
        "# Vision & målbild\n\nPrioritera det som ger mest verksamhetsvärde.",
        encoding="utf-8",
    )
    return RunWorkspace(run_id=run_id, repo_root=tmp_path)


# ---------------------------------------------------------------------------
# Dry-run: first step completes, downstream steps skip (no input)
# ---------------------------------------------------------------------------

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

    # dry_run does NOT copy output to input, so downstream steps must skip
    assert results[1].status == StepStatus.skipped
    assert results[2].status == StepStatus.skipped
    assert results[1].skipped_reason is not None
    assert "vision_och_malbild.md" in results[1].skipped_reason


# ---------------------------------------------------------------------------
# State persistence
# ---------------------------------------------------------------------------

def test_run_state_written_after_dry_run(workspace_with_input):
    orch = Orchestrator(
        workspace=workspace_with_input,
        repo_root=REPO_ROOT,
        flow_steps=_make_flow(),
        agent_definitions=_make_agents(),
    )
    orch.run(dry_run=True)

    store = RunStateStore(workspace_with_input.run_dir)
    state = store.load()
    assert state is not None
    assert state.status == RunStatus.completed
    assert state.step_statuses["ba-vision"] == StepStatus.completed.value


def test_artifact_state_NOT_updated_in_dry_run(workspace_with_input):
    orch = Orchestrator(
        workspace=workspace_with_input,
        repo_root=REPO_ROOT,
        flow_steps=_make_flow(),
        agent_definitions=_make_agents(),
    )
    orch.run(dry_run=True)

    store = ArtifactStateStore(workspace_with_input.run_dir)
    state = store.load()
    assert state is not None
    assert "vision_och_malbild.md" not in state.artifacts


# ---------------------------------------------------------------------------
# Missing input: single step flow
# ---------------------------------------------------------------------------

def test_step_skipped_when_input_missing(tmp_path):
    run_id = "no-input-run"
    input_dir = tmp_path / "runs" / run_id / "input"
    input_dir.mkdir(parents=True)

    workspace = RunWorkspace(run_id=run_id, repo_root=tmp_path)
    flow = [
        FlowStep(
            step_id="ba-vision",
            agent_id="business-analyst",
            sop_filename="01_vision_och_malbild.md",
            artifact_name="Vision & målbild",
            output_filename="vision_och_malbild.md",
            input_filenames=["overgripande_behov.md"],
        )
    ]
    orch = Orchestrator(workspace=workspace, repo_root=REPO_ROOT, flow_steps=flow, agent_definitions=_make_agents())
    results = orch.run(dry_run=True)

    assert results[0].status == StepStatus.skipped
    assert "overgripande_behov.md" in results[0].skipped_reason


# ---------------------------------------------------------------------------
# Prompt content
# ---------------------------------------------------------------------------

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
    assert "Outputregler" in content


# ---------------------------------------------------------------------------
# AgentContextLoader via orchestrator: UX role
# ---------------------------------------------------------------------------

def test_ux_dry_run_prompt_contains_ux_context(tmp_path):
    run_id = "ux-test"
    input_dir = tmp_path / "runs" / run_id / "input"
    input_dir.mkdir(parents=True)

    vision = REPO_ROOT / "docs" / "artifacts" / "templates" / "1.Kravställning" / "vision_och_malbild.md"
    shutil.copy(vision, input_dir / "vision_och_malbild.md")

    sample = REPO_ROOT / "runs" / "demo-001" / "input" / "overgripande_behov.md"
    if sample.exists():
        shutil.copy(sample, input_dir / "overgripande_behov.md")
    else:
        (input_dir / "overgripande_behov.md").write_text("# Test\n- behov", encoding="utf-8")

    workspace = RunWorkspace(run_id=run_id, repo_root=tmp_path)
    flow = [
        FlowStep(
            step_id="ux-journeys",
            agent_id="ux",
            sop_filename="07_user_journeys.md",
            artifact_name="User journeys",
            output_filename="user_journeys.md",
            input_filenames=["vision_och_malbild.md", "overgripande_behov.md"],
        )
    ]
    orch = Orchestrator(workspace=workspace, repo_root=REPO_ROOT, flow_steps=flow, agent_definitions=_make_agents())
    results = orch.run(dry_run=True)

    assert results[0].status == StepStatus.completed
    content = results[0].output_path.read_text(encoding="utf-8")
    assert "UX" in content
    assert "User journeys" in content


def test_default_orchestrator_loads_process_driven_flow(workspace_with_input):
    orch = Orchestrator(
        workspace=workspace_with_input,
        repo_root=REPO_ROOT,
    )

    flow = ProcessFlowLoader(REPO_ROOT).load(DEFAULT_PROCESS_FILE)

    assert orch._process_flow.flow_id == flow.flow_id
    assert len(orch._process_flow.steps) == len(flow.steps)
    assert orch._process_flow.steps[0].sop_filename == "01_vision_och_malbild.md"


def test_raci_dry_run_creates_consultation_approval_and_informing_state(workspace_with_backlog_input):
    orch = Orchestrator(
        workspace=workspace_with_backlog_input,
        repo_root=REPO_ROOT,
        flow_steps=_make_raci_flow(),
        agent_definitions=_make_agents(),
    )

    results = orch.run(dry_run=True)

    assert results[0].status == StepStatus.completed
    assert results[0].approval_decision == "approved_with_notes"

    artifact_state = ArtifactStateStore(workspace_with_backlog_input.run_dir).load()
    assert artifact_state is not None
    record = artifact_state.artifacts["prioriterad_backlog.md"]
    assert record.status == ArtifactStatus.published_to_informed_roles
    assert record.consult_agent_ids == ["verksamhetsexperter"]
    assert record.approver_agent_id == "produktagare"
    assert record.informed_agent_ids == ["utvecklare"]
    assert record.approval_decision == "approved_with_notes"

    consultation_responses = ConsultationStore(workspace_with_backlog_input.run_dir).load_responses_for_step("ba-backlog")
    assert len(consultation_responses) == 1
    assert consultation_responses[0].consultant_agent_id == "verksamhetsexperter"

    approval_decision = ApprovalStore(workspace_with_backlog_input.run_dir).load_for_step("ba-backlog")
    assert approval_decision is not None
    assert approval_decision.decision == "approved_with_notes"

    briefs = InformedRoleBriefStore(workspace_with_backlog_input.run_dir).load_for_step("ba-backlog")
    assert len(briefs) == 1
    assert briefs[0].role_agent_id == "utvecklare"


def test_raci_dry_run_writes_phase_prompt_files(workspace_with_backlog_input):
    orch = Orchestrator(
        workspace=workspace_with_backlog_input,
        repo_root=REPO_ROOT,
        flow_steps=_make_raci_flow(),
        agent_definitions=_make_agents(),
    )

    orch.run(dry_run=True)

    output_dir = workspace_with_backlog_input.output_dir
    expected = {
        "prioriterad_backlog_draft_prompt_dry_run.txt",
        "prioriterad_backlog_consultation_verksamhetsexperter_consultation_prompt_dry_run.txt",
        "prioriterad_backlog_revision_prompt_dry_run.txt",
        "prioriterad_backlog_approval_produktagare_approval_prompt_dry_run.txt",
        "prioriterad_backlog_brief_utvecklare_brief_prompt_dry_run.txt",
    }
    assert expected.issubset({path.name for path in output_dir.iterdir()})


def test_update_document_status_maps_approval_decisions():
    content = (
        "# Prioriterad backlog\n\n"
        "## Metadata\n"
        "| Fält | Värde |\n"
        "|------|------|\n"
        "| Status | Pågående |\n"
    )

    approved = Orchestrator._update_document_status(content, "approved")
    approved_with_notes = Orchestrator._update_document_status(content, "approved_with_notes")
    rejected = Orchestrator._update_document_status(content, "rejected")

    assert "| Status | Godkänd |" in approved
    assert "| Status | Godkänd med kommentarer |" in approved_with_notes
    assert "| Status | Avslagen |" in rejected
