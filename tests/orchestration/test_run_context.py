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

    def test_record_and_update_lineage(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            context = RunContext.from_repo_root(run_id="demo-002", repo_root=repo_root)
            context.initialize()

            source_path = context.input_path / "overgripande_behov.md"
            artifact_path = context.work_path / "vision_malbild.md"
            source_path.write_text("# Input\n", encoding="utf-8")
            artifact_path.write_text("# Output\n", encoding="utf-8")

            context.record_lineage(
                artifact_id="vision_malbild",
                artifact_path=artifact_path,
                source_files=(source_path,),
                produced_by="business_analyst",
            )
            context.update_lineage_review_status(
                artifact_id="vision_malbild",
                review_status="approved",
            )

            lineage = context.load_lineage()
            self.assertIn("vision_malbild", lineage)
            self.assertEqual(
                ["input/overgripande_behov.md"],
                lineage["vision_malbild"]["source_files"],
            )
            self.assertEqual("business_analyst", lineage["vision_malbild"]["produced_by"])
            self.assertEqual("approved", lineage["vision_malbild"]["review_status"])
            self.assertIn("timestamp", lineage["vision_malbild"])


if __name__ == "__main__":
    unittest.main()

