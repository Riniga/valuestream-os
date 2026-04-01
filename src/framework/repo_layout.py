"""
Repository layout helpers.

Locates the ValueStream OS repository root (directory containing framework documentation)
from a starting path, used by the CLI and other entry points.

The framework location is configurable via the FRAMWORK environment variable (defaults to "standard").
This allows support for multiple framework variants (e.g., framework/standard, framework/light).
"""
from __future__ import annotations

import os
from pathlib import Path

_DEFAULT_MAX_PARENT_HOPS = 8
_DEFAULT_FRAMEWORK = "standard"


def get_framework_variant() -> str:
    """
    Get the configured framework variant from FRAMWORK environment variable.
    Defaults to "standard" if not set.
    
    Returns
    -------
    str
        The framework variant name (e.g., "standard", "light").
    """
    return os.environ.get("FRAMWORK", _DEFAULT_FRAMEWORK)


def get_framework_root(repo_root: Path) -> Path:
    """
    Get the path to the framework directory based on the configured variant.
    
    Parameters
    ----------
    repo_root : Path
        The repository root path.
    
    Returns
    -------
    Path
        Path to the framework variant (e.g., repo_root / "framework" / "standard").
    """
    variant = get_framework_variant()
    framework_path = repo_root / "framework" / variant
    
    # For backward compatibility, fall back to "docs" if framework variant doesn't exist
    if not framework_path.exists():
        docs_path = repo_root / "docs"
        if docs_path.exists():
            return docs_path
    
    return framework_path


def find_repository_root(start: Path | None = None, *, max_parent_hops: int = _DEFAULT_MAX_PARENT_HOPS) -> Path:
    """
    Walk parents from ``start`` until a directory containing framework documentation is found.
    
    Looks for either the configured framework variant (framework/standard, framework/light, etc.)
    or falls back to the legacy "docs/" directory.

    If none is found within ``max_parent_hops``, returns ``Path.cwd()``.
    """
    variant = get_framework_variant()
    candidate = (start or Path(__file__).resolve()).parent
    for _ in range(max_parent_hops):
        # Check for framework variant first
        framework_path = candidate / "framework" / variant
        if framework_path.is_dir():
            return candidate
        # Fall back to legacy docs/ for backward compatibility
        if (candidate / "docs").is_dir():
            return candidate
        candidate = candidate.parent
    return Path.cwd()
