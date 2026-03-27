import unittest
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from src.agents.agent_contract import AgentArtifactOutput
from src.agents.ux_agent import UXAgent
from src.orchestration.kravstallning_flow import KravstallningFlow
from src.orchestration.run_context import RunContext


class BrokenUXAgent(UXAgent):
    def produce(
        self,
        input_artifacts: dict[str, Path],
        context: RunContext,
    ) -> AgentArtifactOutput:
        result = super().produce(input_artifacts=input_artifacts, context=context)
        # Force a review failure to verify the PO gate stop path.
        return AgentArtifactOutput(
            artifact_id=result.artifact_id,
            artifact_path=result.artifact_path,
            produced_by=result.produced_by,
            source_artifact_ids=result.source_artifact_ids,
            required_headings=result.required_headings + ("## Saknad obligatorisk rubrik",),
        )


class KravstallningFlowTests(unittest.TestCase):
    def test_run_executes_linear_flow_and_publishes_on_approval(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            context = RunContext.from_repo_root(run_id="demo-001", repo_root=repo_root)
            context.initialize()
            (context.input_path / "overgripande_behov.md").write_text(
                "# Overgripande behov\n\n- Kortare ledtid\n- Tydligare scope\n",
                encoding="utf-8",
            )

            flow = KravstallningFlow()
            result = flow.run(context)

            self.assertEqual("approved", result.status)
            self.assertEqual(("vision_malbild", "ux_koncept"), result.produced_artifacts)
            self.assertEqual(2, len(result.review_decisions))
            self.assertTrue((context.output_path / "vision_malbild.md").exists())
            self.assertTrue((context.output_path / "ux_koncept.md").exists())
            self.assertTrue(context.lineage_path.exists())
            lineage = json.loads(context.lineage_path.read_text(encoding="utf-8"))
            self.assertIn("vision_malbild", lineage)
            self.assertIn("ux_koncept", lineage)
            self.assertEqual(
                ["input/overgripande_behov.md"],
                lineage["vision_malbild"]["source_files"],
            )
            self.assertEqual(
                ["work/vision_malbild.md"],
                lineage["ux_koncept"]["source_files"],
            )
            self.assertEqual("approved", lineage["vision_malbild"]["review_status"])
            self.assertEqual("approved", lineage["ux_koncept"]["review_status"])
            self.assertIn("timestamp", lineage["vision_malbild"])
            self.assertIn("timestamp", lineage["ux_koncept"])

            step_log = (context.logs_path / "step_log.md").read_text(encoding="utf-8")
            self.assertIn("Name: business_analyst_produce", step_log)
            self.assertIn("Name: ux_produce", step_log)
            self.assertIn("Name: product_owner_review:vision_malbild", step_log)
            self.assertIn("Name: product_owner_review:ux_koncept", step_log)

    def test_run_stops_after_po_changes_requested(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            context = RunContext.from_repo_root(run_id="demo-002", repo_root=repo_root)
            context.initialize()
            (context.input_path / "overgripande_behov.md").write_text(
                "# Overgripande behov\n\n- Otydlig prioritering\n- Flera antaganden?\n",
                encoding="utf-8",
            )

            flow = KravstallningFlow(ux_agent=BrokenUXAgent())
            result = flow.run(context)

            self.assertEqual("changes_requested", result.status)
            self.assertEqual(2, len(result.review_decisions))
            self.assertEqual("approved", result.review_decisions[0].review_status)
            self.assertEqual("changes_requested", result.review_decisions[1].review_status)
            self.assertTrue((context.output_path / "vision_malbild.md").exists())
            self.assertFalse((context.output_path / "ux_koncept.md").exists())
            lineage = json.loads(context.lineage_path.read_text(encoding="utf-8"))
            self.assertEqual("approved", lineage["vision_malbild"]["review_status"])
            self.assertEqual("changes_requested", lineage["ux_koncept"]["review_status"])

            step_log = (context.logs_path / "step_log.md").read_text(encoding="utf-8")
            self.assertIn("Name: flow_stopped", step_log)
            self.assertIn("Stopped after PO requested changes.", step_log)

    def test_run_is_idempotent_for_step_log_and_notifications(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            context = RunContext.from_repo_root(run_id="demo-003", repo_root=repo_root)
            context.initialize()
            (context.input_path / "overgripande_behov.md").write_text(
                "# Overgripande behov\n\n- Kortare ledtid\n- Tydligare scope\n",
                encoding="utf-8",
            )
            flow = KravstallningFlow()

            flow.run(context)
            flow.run(context)

            step_log = (context.logs_path / "step_log.md").read_text(encoding="utf-8")
            self.assertEqual(1, step_log.count("Name: business_analyst_produce"))
            self.assertEqual(1, step_log.count("Name: ux_produce"))
            self.assertEqual(1, step_log.count("Name: product_owner_review:vision_malbild"))
            self.assertEqual(1, step_log.count("Name: product_owner_review:ux_koncept"))

            notifications_log = (context.logs_path / "notifications.md").read_text(
                encoding="utf-8"
            )
            self.assertEqual(8, notifications_log.count("## Notification"))


if __name__ == "__main__":
    unittest.main()
