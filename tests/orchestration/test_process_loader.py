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


def test_process_loader_builds_raci_metadata_for_prioriterad_backlog():
    flow = ProcessFlowLoader(REPO_ROOT, AGENT_DEFINITIONS).load(DEFAULT_PROCESS_FILE)
    backlog_step = next(
        step for step in flow.steps if step.output_filename == "prioriterad_backlog.md"
    )

    assert backlog_step.agent_id == "business-analyst"
    assert backlog_step.consult_agent_ids == ["verksamhetsexperter"]
    assert backlog_step.approver_agent_id == "produktagare"
    assert backlog_step.informed_agent_ids == ["utvecklare"]
    assert backlog_step.use_raci_workflow is True


def test_process_loader_enables_raci_workflow_for_all_steps_with_raci_participants():
    flow = ProcessFlowLoader(REPO_ROOT, AGENT_DEFINITIONS).load(DEFAULT_PROCESS_FILE)

    assert flow.steps
    assert all(
        step.use_raci_workflow
        for step in flow.steps
        if step.consult_agent_ids or step.approver_agent_id or step.informed_agent_ids
    )

    vision_step = next(
        step for step in flow.steps if step.output_filename == "vision_och_malbild.md"
    )
    assert vision_step.use_raci_workflow is True


def test_process_loader_requires_approver_for_raci_workflow_flag():
    assert ProcessFlowLoader._should_use_raci_workflow(["verksamhetsexperter"], None, ["utvecklare"]) is False
    assert ProcessFlowLoader._should_use_raci_workflow([], "produktagare", []) is True


# ---------------------------------------------------------------------------
# 2. Målarkitektur process
# ---------------------------------------------------------------------------

MALARKITEKTUR_PROCESS_FILE = "2. Målarkitektur.md"


def test_process_loader_reads_malarkitektur_process():
    flow = ProcessFlowLoader(REPO_ROOT).load(MALARKITEKTUR_PROCESS_FILE)

    assert flow.process_file == MALARKITEKTUR_PROCESS_FILE
    assert "Målarkitektur" in flow.process_title
    assert len(flow.steps) >= 11


def test_process_loader_malarkitektur_builds_steps_from_sop_outputs():
    flow = ProcessFlowLoader(REPO_ROOT).load(MALARKITEKTUR_PROCESS_FILE)
    normalized_outputs = {f.lower() for step in flow.steps for f in [step.output_filename]}

    assert "arkitekturmal.md" in normalized_outputs
    assert any("systemlandskap" in f for f in normalized_outputs)
    assert any("domanmodell" in f for f in normalized_outputs)
    assert "malarkitektur.md" in normalized_outputs


def test_process_loader_malarkitektur_maps_agents_from_raci():
    flow = ProcessFlowLoader(REPO_ROOT, AGENT_DEFINITIONS).load(MALARKITEKTUR_PROCESS_FILE)
    agent_ids = {step.agent_id for step in flow.steps}

    assert "losningsarkitekt" in agent_ids
    assert "business-analyst" in agent_ids
    assert "dataarkitekt" in agent_ids


def test_process_loader_malarkitektur_resolves_new_raci_roles():
    flow = ProcessFlowLoader(REPO_ROOT, AGENT_DEFINITIONS).load(MALARKITEKTUR_PROCESS_FILE)

    all_consult = {aid for step in flow.steps for aid in step.consult_agent_ids}
    all_approvers = {step.approver_agent_id for step in flow.steps if step.approver_agent_id}
    all_informed = {aid for step in flow.steps for aid in step.informed_agent_ids}

    assert "enterprise-arkitekt" in all_approvers
    assert "teknisk-lead" in all_consult
    assert "devops" in all_consult


def test_process_loader_malarkitektur_first_step_is_arkitekturmal():
    flow = ProcessFlowLoader(REPO_ROOT).load(MALARKITEKTUR_PROCESS_FILE)
    first_step = flow.steps[0]

    assert first_step.sop_filename == "01_etablera_arkitekturmal.md"
    assert "arkitekturmal" in first_step.output_filename


def test_process_loader_malarkitektur_uses_raci_workflow():
    flow = ProcessFlowLoader(REPO_ROOT, AGENT_DEFINITIONS).load(MALARKITEKTUR_PROCESS_FILE)

    assert all(step.use_raci_workflow for step in flow.steps)


def test_process_loader_malarkitektur_flow_id():
    flow = ProcessFlowLoader(REPO_ROOT).load(MALARKITEKTUR_PROCESS_FILE)

    assert flow.flow_id == "2-malarkitektur"
