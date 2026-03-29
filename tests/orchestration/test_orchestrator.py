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
    FlowStep,
    RunStatus,
    StepStatus,
)
from src.framework.stores import ArtifactStateStore, RunStateStore
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
    }


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
