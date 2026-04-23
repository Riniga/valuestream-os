from __future__ import annotations

from pathlib import Path


class RunWorkspace:

    def __init__(self, run_id: str, repo_root: Path) -> None:
        self.run_id = run_id
        self.repo_root = repo_root
        self.run_dir = repo_root / "runs" / run_id
        self.input_dir = self.run_dir / "input"
        self.output_dir = self.run_dir / "output"
        self.human_tasks_dir = self.run_dir / "human_tasks"

    def validate_input(self, required_files: list[str]) -> list[str]:
        return [f for f in required_files if not (self.input_dir / f).exists()]

    def read_input(self, filename: str) -> str:
        path = self.input_dir / filename
        if not path.exists():
            raise FileNotFoundError(
                f"Input file not found: {path}\n"
                f"Expected input folder: {self.input_dir}"
            )
        return path.read_text(encoding="utf-8")

    def read_output(self, filename: str) -> str:
        path = self.output_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Output file not found: {path}")
        return path.read_text(encoding="utf-8")

    def output_exists(self, filename: str) -> bool:
        return (self.output_dir / filename).exists()

    def write_output(self, filename: str, content: str) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / filename
        path.write_text(content, encoding="utf-8")
        return path

    def input_path(self, filename: str) -> Path:
        return self.input_dir / filename

    def output_path(self, filename: str) -> Path:
        return self.output_dir / filename
