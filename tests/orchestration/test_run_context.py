import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.orchestration.run_context import RunContext


class RunContextInitializationTests(unittest.TestCase):
    def test_initialize_creates_contract_and_state_file(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            run_id = "demo-001"
            input_dir = repo_root / "runs" / run_id / "input"
            input_dir.mkdir(parents=True, exist_ok=True)

            context = RunContext.from_repo_root(run_id=run_id, repo_root=repo_root)
            state = context.initialize()

            self.assertTrue(context.input_path.exists())
            self.assertTrue(context.work_path.exists())
            self.assertTrue(context.output_path.exists())
            self.assertTrue(context.logs_path.exists())
            self.assertEqual("initialized", state["status"])
            self.assertTrue(context.state_path.exists())

            persisted_state = json.loads(context.state_path.read_text(encoding="utf-8"))
            self.assertEqual("initialized", persisted_state["status"])
            self.assertEqual(run_id, persisted_state["run_id"])


if __name__ == "__main__":
    unittest.main()

