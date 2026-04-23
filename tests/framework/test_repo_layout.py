"""Tests for repository root and framework discovery."""
from __future__ import annotations

from pathlib import Path

import pytest

from src.framework.repo_layout import find_repository_root, get_framework_root, get_framework_variant


def test_find_repository_root_from_src_subtree():
    repo_root = find_repository_root(Path(__file__).resolve().parent)
    assert (repo_root / "framework" / "standard").is_dir()
    assert (repo_root / "src").is_dir()


def test_get_framework_variant_prefers_framework_env(monkeypatch):
    monkeypatch.setenv("FRAMEWORK", "light")
    monkeypatch.setenv("FRAMWORK", "standard")

    assert get_framework_variant() == "light"


def test_get_framework_variant_supports_legacy_framwork_env(monkeypatch):
    monkeypatch.delenv("FRAMEWORK", raising=False)
    monkeypatch.setenv("FRAMWORK", "light")

    assert get_framework_variant() == "light"


def test_get_framework_root_raises_for_missing_variant(monkeypatch):
    repo_root = find_repository_root(Path(__file__).resolve().parent)
    monkeypatch.setenv("FRAMEWORK", "missing-variant")
    monkeypatch.delenv("FRAMWORK", raising=False)

    with pytest.raises(FileNotFoundError, match="Framework variant 'missing-variant' hittades inte"):
        get_framework_root(repo_root)
