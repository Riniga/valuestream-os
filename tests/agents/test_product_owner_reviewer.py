import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.agents.agent_contract import AgentArtifactOutput
from src.agents.product_owner_reviewer import ProductOwnerReviewer
from src.orchestration.run_context import RunContext


class ProductOwnerReviewerTests(unittest.TestCase):
    def test_review_marks_approved_when_all_required_headings_exist(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            context = RunContext.from_repo_root(run_id="demo-001", repo_root=repo_root)
            context.initialize()

            artifact_path = context.work_path / "vision_malbild.md"
            artifact_path.write_text(
                "# Vision och malbild\n\n## Malbild\n\n## Affarsbehov\n",
                encoding="utf-8",
            )
            output = AgentArtifactOutput(
                artifact_id="vision_malbild",
                artifact_path=artifact_path,
                produced_by="business_analyst",
                source_artifact_ids=("overgripande_behov",),
                required_headings=("# Vision och malbild", "## Malbild", "## Affarsbehov"),
            )

            reviewer = ProductOwnerReviewer()
            decision = reviewer.review(output, context)

            self.assertEqual("approved", decision.review_status)
            self.assertTrue(decision.can_publish)
            self.assertEqual((), decision.missing_headings)

            state = context.load_state()
            self.assertEqual("approved", state["status"])
            self.assertEqual(
                "approved",
                state["artifact_reviews"]["vision_malbild"]["review_status"],
            )
            published_path = context.output_path / "vision_malbild.md"
            self.assertTrue(published_path.exists())
            self.assertEqual(
                artifact_path.read_text(encoding="utf-8"),
                published_path.read_text(encoding="utf-8"),
            )
            self.assertEqual(
                "output/vision_malbild.md",
                state["artifact_reviews"]["vision_malbild"]["published_artifact_path"],
            )
            self.assertIn(
                "published_at",
                state["artifact_reviews"]["vision_malbild"],
            )
            notifications_path = context.logs_path / "notifications.md"
            self.assertTrue(notifications_path.exists())
            notifications = notifications_path.read_text(encoding="utf-8")
            self.assertIn("Role: business_analyst", notifications)
            self.assertIn("Role: solution_architect", notifications)
            self.assertIn("Role: project_manager", notifications)
            self.assertIn("Role: developers", notifications)
            self.assertIn("Event: artifact_approved_and_published", notifications)

    def test_review_marks_changes_requested_when_heading_is_missing(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            context = RunContext.from_repo_root(run_id="demo-002", repo_root=repo_root)
            context.initialize()

            artifact_path = context.work_path / "ux_koncept.md"
            artifact_path.write_text(
                "# UX koncept\n\n## Malgrupper och behov\n",
                encoding="utf-8",
            )
            output = AgentArtifactOutput(
                artifact_id="ux_koncept",
                artifact_path=artifact_path,
                produced_by="ux",
                source_artifact_ids=("vision_malbild",),
                required_headings=("# UX koncept", "## Malgrupper och behov", "## Nyckelfloden"),
            )

            reviewer = ProductOwnerReviewer()
            decision = reviewer.review(output, context)

            self.assertEqual("changes_requested", decision.review_status)
            self.assertFalse(decision.can_publish)
            self.assertEqual(("## Nyckelfloden",), decision.missing_headings)

            state = context.load_state()
            self.assertEqual("changes_requested", state["status"])
            self.assertEqual(
                ["## Nyckelfloden"],
                state["artifact_reviews"]["ux_koncept"]["missing_headings"],
            )
            self.assertFalse((context.output_path / "ux_koncept.md").exists())
            self.assertFalse((context.logs_path / "notifications.md").exists())


if __name__ == "__main__":
    unittest.main()
