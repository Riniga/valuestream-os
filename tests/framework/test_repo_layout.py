"""Tests for repository root discovery."""
from __future__ import annotations

from pathlib import Path

from src.framework.repo_layout import find_repository_root


def test_find_repository_root_from_src_subtree():
    repo_root = find_repository_root(Path(__file__).resolve().parent)
    assert (repo_root / "docs").is_dir()
    assert (repo_root / "src").is_dir()
