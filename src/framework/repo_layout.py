"""
Repository layout helpers.

Locates the ValueStream OS repository root (directory containing ``docs/``)
from a starting path, used by the CLI and other entry points.
"""
from __future__ import annotations

from pathlib import Path

_DEFAULT_MAX_PARENT_HOPS = 8


def find_repository_root(start: Path | None = None, *, max_parent_hops: int = _DEFAULT_MAX_PARENT_HOPS) -> Path:
    """
    Walk parents from ``start`` until a directory containing ``docs/`` is found.

    If none is found within ``max_parent_hops``, returns ``Path.cwd()``.
    """
    candidate = (start or Path(__file__).resolve()).parent
    for _ in range(max_parent_hops):
        if (candidate / "docs").is_dir():
            return candidate
        candidate = candidate.parent
    return Path.cwd()
