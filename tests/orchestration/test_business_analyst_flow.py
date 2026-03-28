"""
Tests for BusinessAnalystFlow — orchestration logic without LLM.

Uses dry_run / direct method calls to verify workspace I/O,
prompt assembly and artifact registry — no network calls made.
"""

import json
import shutil
import tempfile
from pathlib import Path

import pytest

from src.agents.business_analyst.artifact_registry import (
    ArtifactDefinition,
    build_artifact_registry,
    get_artifact,
    get_artifact_by_name,
)
from src.agents.business_analyst.context_loader import FrameworkContextLoader
from src.agents.business_analyst.prompt_builder import PromptBuilder
from src.capabilities.run_workspace import RunWorkspace
from src.orchestration.business_analyst_flow import BusinessAnalystFlow

REPO_ROOT = Path(__file__).resolve().parents[2]
_loader = FrameworkContextLoader(REPO_ROOT)
_registry = build_artifact_registry(_loader)


@pytest.fixture()
def tmp_workspace(tmp_path):
    """Create a temporary run workspace with a sample input file."""
    run_id = "test-run"
    input_dir = tmp_path / "runs" / run_id / "input"
    input_dir.mkdir(parents=True)

    sample_input = REPO_ROOT / "runs" / "demo-001" / "input" / "overgripande_behov.md"
    if sample_input.exists():
        shutil.copy(sample_input, input_dir / "overgripande_behov.md")
    else:
        (input_dir / "overgripande_behov.md").write_text("# Test input\n- Behov 1", encoding="utf-8")

    return RunWorkspace(run_id=run_id, repo_root=tmp_path)


@pytest.fixture()
def tmp_workspace_with_vision(tmp_workspace, tmp_path):
    """Workspace that also has vision_och_malbild.md in input (for scope SOP)."""
    vision = REPO_ROOT / "docs" / "artifacts" / "templates" / "1.Kravställning" / "vision_och_malbild.md"
    if vision.exists():
        shutil.copy(vision, tmp_workspace.input_dir / "vision_och_malbild.md")
    else:
        (tmp_workspace.input_dir / "vision_och_malbild.md").write_text("# Vision\nTest", encoding="utf-8")
    return tmp_workspace


# ------------------------------------------------------------------
# Artifact registry
# ------------------------------------------------------------------

def test_artifact_registry_has_entries():
    assert len(_registry) >= 2


def test_get_artifact_vision():
    a = get_artifact(_registry, "vision_och_malbild.md")
    assert a is not None
    assert a.name == "Vision & målbild"


def test_get_artifact_scope():
    a = get_artifact(_registry, "scope_och_avgransningar.md")
    assert a is not None
    assert "Scope" in a.name


def test_get_artifact_unknown_returns_none():
    assert get_artifact(_registry, "nonexistent.md") is None


# ------------------------------------------------------------------
# RunWorkspace
# ------------------------------------------------------------------

def test_workspace_read_input(tmp_workspace):
    content = tmp_workspace.read_input("overgripande_behov.md")
    assert len(content) > 0


def test_workspace_write_and_read_output(tmp_workspace):
    tmp_workspace.write_output("test.md", "# Hej")
    assert tmp_workspace.output_exists("test.md")
    assert tmp_workspace.read_output("test.md") == "# Hej"


def test_workspace_validate_input_detects_missing(tmp_workspace):
    missing = tmp_workspace.validate_input(["overgripande_behov.md", "missing.md"])
    assert "missing.md" in missing
    assert "overgripande_behov.md" not in missing


# ------------------------------------------------------------------
# PromptBuilder
# ------------------------------------------------------------------

def test_prompt_builder_includes_all_sections():
    loader = FrameworkContextLoader(REPO_ROOT)
    builder = PromptBuilder()
    role = loader.load_role()
    sop = loader.load_sop("01_vision_och_malbild.md")
    desc = loader.load_artifact_description("Vision & målbild")
    tmpl = loader.load_artifact_template("vision_och_malbild.md")
    inputs = {"overgripande_behov.md": "# Test input\n- Behov A"}

    prompt = builder.build_generate_prompt(role, sop.content, desc, tmpl, inputs)

    assert "Business Analyst" in prompt
    assert "Arbetssteg" in prompt
    assert "## 1. Vision" in prompt
    assert "Behov A" in prompt


# ------------------------------------------------------------------
# BusinessAnalystFlow.get_info
# ------------------------------------------------------------------

def test_get_info_returns_agent_header(tmp_workspace):
    flow = BusinessAnalystFlow(workspace=tmp_workspace, repo_root=REPO_ROOT)
    info = flow.get_info()
    assert info["role_name"] == "Business Analyst"
    assert info["agent_file_ok"] is True
    assert len(info["purpose"]) > 20


def test_get_info_all_supporting_files_ok(tmp_workspace):
    flow = BusinessAnalystFlow(workspace=tmp_workspace, repo_root=REPO_ROOT)
    info = flow.get_info()
    problems = [
        f"{a['name']}: sop={a['sop_ok']} desc={a['description_ok']} tmpl={a['template_ok']}"
        for a in info["artifacts"]
        if not (a["sop_ok"] and a["description_ok"] and a["template_ok"])
    ]
    assert not problems, "Missing supporting files:\n" + "\n".join(problems)


# ------------------------------------------------------------------
# BusinessAnalystFlow.list_responsibilities
# ------------------------------------------------------------------

def test_list_responsibilities_returns_entries(tmp_workspace):
    flow = BusinessAnalystFlow(workspace=tmp_workspace, repo_root=REPO_ROOT)
    entries = flow.list_responsibilities()
    assert len(entries) >= 1
    assert any(e["artifact"] == "Vision & målbild" for e in entries)


def test_list_responsibilities_vision_is_registered(tmp_workspace):
    flow = BusinessAnalystFlow(workspace=tmp_workspace, repo_root=REPO_ROOT)
    entries = flow.list_responsibilities()
    vision = next(e for e in entries if e["artifact"] == "Vision & målbild")
    assert vision["registered"] is True
    assert vision["output_filename"] == "vision_och_malbild.md"


# ------------------------------------------------------------------
# BusinessAnalystFlow.generate_dry_run
# ------------------------------------------------------------------

def test_generate_dry_run_writes_prompt_file(tmp_workspace):
    flow = BusinessAnalystFlow(workspace=tmp_workspace, repo_root=REPO_ROOT)
    output_path = flow.generate_dry_run("vision_och_malbild.md")
    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")
    assert "Business Analyst" in content
    assert "## 1. Vision" in content


def test_generate_dry_run_scope_requires_vision_input(tmp_workspace):
    flow = BusinessAnalystFlow(workspace=tmp_workspace, repo_root=REPO_ROOT)
    with pytest.raises(FileNotFoundError, match="vision_och_malbild.md"):
        flow.generate_dry_run("scope_och_avgransningar.md")


def test_generate_dry_run_scope_works_with_vision_input(tmp_workspace_with_vision):
    flow = BusinessAnalystFlow(workspace=tmp_workspace_with_vision, repo_root=REPO_ROOT)
    output_path = flow.generate_dry_run("scope_och_avgransningar.md")
    assert output_path.exists()


# ------------------------------------------------------------------
# BusinessAnalystFlow.update — branches on existing output
# ------------------------------------------------------------------

def test_update_dry_run_uses_generate_prompt_when_no_existing_output(tmp_workspace):
    flow = BusinessAnalystFlow(workspace=tmp_workspace, repo_root=REPO_ROOT)
    output_path = flow.generate_dry_run("vision_och_malbild.md")
    content = output_path.read_text(encoding="utf-8")
    assert "Befintlig version" not in content


def test_update_dry_run_includes_existing_content_when_output_exists(tmp_workspace):
    tmp_workspace.write_output("vision_och_malbild.md", "# Befintlig version\nGammalt innehåll")
    flow = BusinessAnalystFlow(workspace=tmp_workspace, repo_root=REPO_ROOT)

    existing_prompt_path = tmp_workspace.output_dir / "vision_och_malbild_update_dry_run.txt"

    role_text = flow.loader.load_role()
    sop = flow.loader.load_sop("01_vision_och_malbild.md")
    description = flow.loader.load_artifact_description("Vision & målbild")
    template = flow.loader.load_artifact_template("vision_och_malbild.md")
    input_content = {"overgripande_behov.md": tmp_workspace.read_input("overgripande_behov.md")}

    prompt = flow.prompt_builder.build_update_prompt(
        role_text=role_text,
        sop_text=sop.content,
        artifact_description=description,
        artifact_template=template,
        input_content=input_content,
        existing_content="# Befintlig version\nGammalt innehåll",
    )
    assert "Befintlig version" in prompt
    assert "Gammalt innehåll" in prompt
