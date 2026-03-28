"""
RunWorkspace — filbaserat arbetsyta-lager för agent-körningar.

Varje körning lever under runs/<run-id>/ och hanteras via denna klass.
Reads from input/, writes to output/. Never touches docs/.
"""

from __future__ import annotations

from pathlib import Path


class RunWorkspace:
    """
    Manages the file-based workspace for a single agent run.

    Directory layout:
        runs/<run_id>/
            input/      — placed by user before run
            output/     — written by agents during run
    """

    def __init__(self, run_id: str, repo_root: Path) -> None:
        self.run_id = run_id
        self.repo_root = repo_root
        self.run_dir = repo_root / "runs" / run_id
        self.input_dir = self.run_dir / "input"
        self.output_dir = self.run_dir / "output"

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_input(self, required_files: list[str]) -> list[str]:
        """Return list of required input filenames that are missing."""
        missing = []
        for filename in required_files:
            if not (self.input_dir / filename).exists():
                missing.append(filename)
        return missing

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def read_input(self, filename: str) -> str:
        """Read a file from the input directory and return its text content."""
        path = self.input_dir / filename
        if not path.exists():
            raise FileNotFoundError(
                f"Input file not found: {path}\n"
                f"Expected input folder: {self.input_dir}"
            )
        return path.read_text(encoding="utf-8")

    def read_output(self, filename: str) -> str:
        """Read an existing output artifact."""
        path = self.output_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Output file not found: {path}")
        return path.read_text(encoding="utf-8")

    def output_exists(self, filename: str) -> bool:
        return (self.output_dir / filename).exists()

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def write_output(self, filename: str, content: str) -> Path:
        """Write content to the output directory, creating it if needed."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / filename
        path.write_text(content, encoding="utf-8")
        return path

    # ------------------------------------------------------------------
    # Paths (for callers that need the raw Path)
    # ------------------------------------------------------------------

    def input_path(self, filename: str) -> Path:
        return self.input_dir / filename

    def output_path(self, filename: str) -> Path:
        return self.output_dir / filename
