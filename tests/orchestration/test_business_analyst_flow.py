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
    ARTIFACT_REGISTRY,
    get_artifact,
    get_artifact_by_name,
)
from src.agents.business_analyst.context_loader import FrameworkContextLoader
from src.agents.business_analyst.prompt_builder import PromptBuilder
from src.capabilities.run_workspace import RunWorkspace
from src.orchestration.business_analyst_flow import BusinessAnalystFlow

REPO_ROOT = Path(__file__).resolve().parents[2]


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
    vision = REPO_ROOT / "docs" / "Artifakter" / "Innehåll" / "1.Kravställning" / "vision_och_malbild.md"
    if vision.exists():
        shutil.copy(vision, tmp_workspace.input_dir / "vision_och_malbild.md")
    else:
        (tmp_workspace.input_dir / "vision_och_malbild.md").write_text("# Vision\nTest", encoding="utf-8")
    return tmp_workspace


# ------------------------------------------------------------------
# Artifact registry
# ------------------------------------------------------------------

def test_artifact_registry_has_entries():
    assert len(ARTIFACT_REGISTRY) >= 2


def test_get_artifact_vision():
    a = get_artifact("vision_och_malbild.md")
    assert a is not None
    assert a.name == "Vision & målbild"


def test_get_artifact_scope():
    a = get_artifact("scope_och_avgransningar.md")
    assert a is not None
    assert "Scope" in a.name


def test_get_artifact_unknown_returns_none():
    assert get_artifact("nonexistent.md") is None


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
