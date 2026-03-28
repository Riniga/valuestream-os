"""
Tests for FrameworkContextLoader — document discovery and parsing.

These tests run against the real docs/ folder and require no LLM connection.
"""

from pathlib import Path

import pytest

from src.agents.business_analyst.context_loader import FrameworkContextLoader

REPO_ROOT = Path(__file__).resolve().parents[2]
loader = FrameworkContextLoader(REPO_ROOT)


def test_load_role_returns_content():
    role = loader.load_role()
    assert len(role) > 100
    assert "Business Analyst" in role


def test_load_sops_finds_ba_responsible_sops():
    sops = loader.load_sops_for_role()
    assert len(sops) >= 1
    names = [s.name for s in sops]
    assert any("Vision" in n for n in names), f"Expected Vision SOP, got: {names}"


def test_sop_has_inputs_and_outputs():
    sops = loader.load_sops_for_role()
    vision_sop = next(s for s in sops if "Vision" in s.name)
    assert len(vision_sop.inputs) >= 1
    assert len(vision_sop.outputs) >= 1


def test_load_sop_by_filename():
    sop = loader.load_sop("01_vision_och_malbild.md")
    assert "Vision" in sop.name
    assert sop.path.exists()


def test_load_artifact_description_vision():
    desc = loader.load_artifact_description("Vision & målbild")
    assert len(desc) > 50
    assert "Business Analyst" in desc


def test_load_artifact_template_vision():
    tmpl = loader.load_artifact_template("vision_och_malbild.md")
    assert "## 1. Vision" in tmpl
    assert "## Metadata" in tmpl


def test_load_artifact_template_scope():
    tmpl = loader.load_artifact_template("scope_och_avgransningar.md")
    assert "## 2. Scope" in tmpl


def test_only_ba_responsible_sops_returned():
    sops = loader.load_sops_for_role()
    for sop in sops:
        assert "Business Analyst" in sop.content, (
            f"SOP '{sop.name}' returned but BA is not R: {sop.path}"
        )
