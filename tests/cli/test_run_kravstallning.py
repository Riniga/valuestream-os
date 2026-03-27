import unittest
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from src.cli.run_kravstallning import run_cli
from src.orchestration.run_context import RunContext


class RunKravstallningCliTests(unittest.TestCase):
    def test_cli_returns_non_zero_when_required_input_is_missing(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            stderr = StringIO()
            with patch("sys.stderr", stderr):
                exit_code = run_cli(
                    run_id="demo-missing",
                    dry_run=False,
                    repo_root=repo_root,
                )

            self.assertEqual(2, exit_code)
            message = stderr.getvalue()
            self.assertIn("Missing required input artifacts for run", message)
            self.assertIn("input/overgripande_behov.md", message)
            self.assertIn("Expected input folder:", message)

    def test_cli_dry_run_validates_inputs_without_running_flow(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            context = RunContext.from_repo_root(run_id="demo-dry", repo_root=repo_root)
            context.initialize()
            (context.input_path / "overgripande_behov.md").write_text(
                "# Overgripande behov\n\n- Kortare ledtid\n",
                encoding="utf-8",
            )

            stdout = StringIO()
            with patch("sys.stdout", stdout):
                exit_code = run_cli(
                    run_id="demo-dry",
                    dry_run=True,
                    repo_root=repo_root,
                )

            self.assertEqual(0, exit_code)
            self.assertIn("Dry-run OK", stdout.getvalue())
            self.assertFalse((context.output_path / "vision_malbild.md").exists())

    def test_cli_executes_flow_for_valid_run(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            context = RunContext.from_repo_root(run_id="demo-run", repo_root=repo_root)
            context.initialize()
            (context.input_path / "overgripande_behov.md").write_text(
                "# Overgripande behov\n\n- Tydligare prioritering\n",
                encoding="utf-8",
            )

            stdout = StringIO()
            with patch("sys.stdout", stdout):
                exit_code = run_cli(
                    run_id="demo-run",
                    dry_run=False,
                    repo_root=repo_root,
                )

            self.assertEqual(0, exit_code)
            self.assertIn("finished with status", stdout.getvalue())
            self.assertTrue((context.output_path / "vision_malbild.md").exists())


if __name__ == "__main__":
    unittest.main()
