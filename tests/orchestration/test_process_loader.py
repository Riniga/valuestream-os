from __future__ import annotations

from pathlib import Path

from src.orchestration.agent_registry import AGENT_DEFINITIONS
from src.orchestration.process_loader import DEFAULT_PROCESS_FILE, ProcessFlowLoader


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_process_loader_reads_kravstallning_process():
    flow = ProcessFlowLoader(REPO_ROOT).load(DEFAULT_PROCESS_FILE)

    assert flow.process_file == "1. Kravställning.md"
    assert "Kravställning" in flow.process_title
    assert len(flow.steps) >= 10


def test_process_loader_builds_steps_from_sop_outputs():
    flow = ProcessFlowLoader(REPO_ROOT).load(DEFAULT_PROCESS_FILE)
    outputs = {step.output_filename for step in flow.steps}

    assert "vision_och_malbild.md" in outputs
    assert "user_journeys.md" in outputs
    assert "story_map.md" in outputs
    assert "epics_och_capabilities.md" in outputs


def test_process_loader_maps_agents_from_raci():
    flow = ProcessFlowLoader(REPO_ROOT, AGENT_DEFINITIONS).load(DEFAULT_PROCESS_FILE)
    agent_ids = {step.agent_id for step in flow.steps}

    assert "business-analyst" in agent_ids
    assert "ux" in agent_ids


def test_process_loader_uses_process_section_order():
    flow = ProcessFlowLoader(REPO_ROOT).load(DEFAULT_PROCESS_FILE)
    first_step = flow.steps[0]

    assert first_step.sop_filename == "01_vision_och_malbild.md"
    assert first_step.output_filename == "vision_och_malbild.md"


def test_process_loader_expands_multi_output_sop_to_multiple_steps():
    flow = ProcessFlowLoader(REPO_ROOT).load(DEFAULT_PROCESS_FILE)
    stakeholder_steps = [
        step for step in flow.steps if step.sop_filename == "04_stakeholderkarta.md"
    ]

    assert len(stakeholder_steps) == 2
    assert {step.output_filename for step in stakeholder_steps} == {
        "Stakeholderkarta.md",
        "Beroendekarta.md",
    }


def test_process_loader_deduplicates_repeated_outputs_in_same_sop():
    flow = ProcessFlowLoader(REPO_ROOT).load(DEFAULT_PROCESS_FILE)
    scope_steps = [
        step for step in flow.steps if step.sop_filename == "03_scope_och_avgransningar.md"
    ]

    assert [step.output_filename for step in scope_steps] == [
        "scope_och_avgransningar.md",
        "epics_och_capabilities.md",
    ]
