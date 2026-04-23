from __future__ import annotations

from pathlib import Path

import pytest

from src.framework.models import ActorKind
from src.orchestration.agent_registry import load_agent_definitions
from src.orchestration.process_loader import DEFAULT_PROCESS_FILE, ProcessFlowLoader


REPO_ROOT = Path(__file__).resolve().parents[2]
MALARKITEKTUR_PROCESS_FILE = "2. Målarkitektur.md"


def test_process_loader_reads_kravstallning_process():
    flow = ProcessFlowLoader(REPO_ROOT).load(DEFAULT_PROCESS_FILE)

    assert flow.process_file == "1. Kravställning.md"
    assert "Kravställning" in flow.process_title
    assert len(flow.steps) >= 5


def test_process_loader_builds_steps_from_kravstallning_outputs():
    flow = ProcessFlowLoader(REPO_ROOT).load(DEFAULT_PROCESS_FILE)
    outputs = {step.output_filename for step in flow.steps}

    assert "bestallning.md" in outputs
    assert "vision_och_malbild.md" in outputs
    assert "omfattning_och_strukturerad_backlog.md" in outputs
    assert "stakeholderkarta.md" in outputs
    assert "kpi_vardematt.md" in outputs


def test_process_loader_uses_manifest_driven_agents():
    flow = ProcessFlowLoader(REPO_ROOT).load(DEFAULT_PROCESS_FILE)
    agent_ids = {step.agent_id for step in flow.steps}

    assert "business-analyst" in agent_ids
    assert "bestallare" in agent_ids
    assert "produktagare" not in agent_ids


def test_process_loader_resolves_human_roles_from_manifest():
    flow = ProcessFlowLoader(REPO_ROOT).load(DEFAULT_PROCESS_FILE)
    bestallning_step = next(step for step in flow.steps if step.output_filename == "bestallning.md")
    vision_step = next(step for step in flow.steps if step.output_filename == "vision_och_malbild.md")

    assert bestallning_step.agent_id == "bestallare"
    assert bestallning_step.agent_actor_kind == ActorKind.automated
    assert bestallning_step.approver_agent_id == "produktagare"
    assert bestallning_step.approver_actor_kind == ActorKind.automated

    assert vision_step.agent_id == "business-analyst"
    assert vision_step.agent_actor_kind == ActorKind.automated
    assert vision_step.approver_agent_id == "produktagare"
    assert vision_step.approver_actor_kind == ActorKind.automated


def test_process_loader_uses_process_section_order():
    flow = ProcessFlowLoader(REPO_ROOT).load(DEFAULT_PROCESS_FILE)
    first_step = flow.steps[0]

    assert first_step.sop_filename == "01_skapa_bestallning.md"
    assert first_step.output_filename == "bestallning.md"


def test_process_loader_builds_raci_metadata_for_backlog():
    flow = ProcessFlowLoader(REPO_ROOT).load(DEFAULT_PROCESS_FILE)
    backlog_step = next(
        step for step in flow.steps if step.output_filename == "omfattning_och_strukturerad_backlog.md"
    )

    assert backlog_step.agent_id == "business-analyst"
    assert backlog_step.consult_agent_ids == ["verksamhetsexperter", "anvandarrepresentanter"]
    assert backlog_step.approver_agent_id == "produktagare"
    assert backlog_step.approver_actor_kind == ActorKind.automated
    assert backlog_step.informed_agent_ids == ["losningsarkitekt", "utvecklare", "projektledare"]
    assert backlog_step.use_raci_workflow is True


def test_process_loader_enables_raci_workflow_for_all_steps_with_raci_participants():
    flow = ProcessFlowLoader(REPO_ROOT).load(DEFAULT_PROCESS_FILE)

    assert flow.steps
    assert all(
        step.use_raci_workflow
        for step in flow.steps
        if step.consult_agent_ids or step.approver_agent_id or step.informed_agent_ids
    )


def test_process_loader_requires_any_raci_participant_for_raci_workflow_flag():
    assert ProcessFlowLoader._should_use_raci_workflow(["verksamhetsexperter"], None, []) is True
    assert ProcessFlowLoader._should_use_raci_workflow([], "bestallare", []) is True
    assert ProcessFlowLoader._should_use_raci_workflow([], None, ["utvecklare"]) is True
    assert ProcessFlowLoader._should_use_raci_workflow([], None, []) is False


def test_process_loader_reads_malarkitektur_process():
    flow = ProcessFlowLoader(REPO_ROOT).load(MALARKITEKTUR_PROCESS_FILE)

    assert flow.process_file == MALARKITEKTUR_PROCESS_FILE
    assert "Målarkitektur" in flow.process_title
    assert len(flow.steps) >= 5


def test_process_loader_malarkitektur_maps_agents_from_manifest():
    flow = ProcessFlowLoader(REPO_ROOT).load(MALARKITEKTUR_PROCESS_FILE)
    agent_ids = {step.agent_id for step in flow.steps}

    assert "losningsarkitekt" in agent_ids
    assert "business-analyst" in agent_ids
    assert "dataarkitekt" in agent_ids


def test_process_loader_manifest_can_be_loaded_directly():
    definitions = load_agent_definitions(REPO_ROOT)

    assert definitions["bestallare"].actor_kind == ActorKind.human
    assert definitions["bestallare"].agent_file == "beställare.md"
    assert definitions["produktagare"].actor_kind == ActorKind.automated
    assert definitions["produktagare"].agent_file == "produktägare.md"
    assert definitions["business-analyst"].actor_kind == ActorKind.automated


def test_process_loader_missing_raci_mapping_raises(tmp_path):
    repo_root = tmp_path
    framework_root = repo_root / "framework" / "standard"
    (framework_root / "agents").mkdir(parents=True)
    (framework_root / "processes").mkdir(parents=True)
    (framework_root / "SOP" / "1.Test").mkdir(parents=True)
    (framework_root / "artifacts" / "templates" / "1.Test").mkdir(parents=True)
    (framework_root / "artifacts" / "descriptions" / "1.Test").mkdir(parents=True)

    (framework_root / "agents" / "manifest.json").write_text(
        """
{
  "agents": [
    {
      "agent_id": "business-analyst",
      "display_name": "Business Analyst",
      "raci_role_id": "Business Analyst",
      "agent_file": "business-analyst.md",
      "actor_kind": "automated"
    }
  ]
}
""".strip(),
        encoding="utf-8",
    )
    (framework_root / "agents" / "business-analyst.md").write_text("# Roll: Business Analyst", encoding="utf-8")
    (framework_root / "processes" / "1. Test.md").write_text(
        "# Test\n\n## Delprocess 1: Test\n\n➡ **Se [SOP](../SOP/1.Test/01_test.md).**\n",
        encoding="utf-8",
    )
    (framework_root / "SOP" / "1.Test" / "01_test.md").write_text(
        "# SOP: Test\n\n## 3. Input\n\n## 4. Output\n\n- Testartefakt\n\n## 5. RACI\n\n- R: Okänd Roll\n",
        encoding="utf-8",
    )
    (framework_root / "artifacts" / "templates" / "1.Test" / "testartefakt.md").write_text(
        "# Testartefakt\n",
        encoding="utf-8",
    )
    (framework_root / "artifacts" / "descriptions" / "1.Test" / "testartefakt.md").write_text(
        "# Testartefakt\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Okänd Roll"):
        ProcessFlowLoader(repo_root).load("1. Test.md")
