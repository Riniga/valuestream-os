import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.agents.business_analyst_agent import BusinessAnalystAgent
from src.orchestration.run_context import RunContext
from src.roles.interaction_bus import InteractionBus


class InteractionBusTests(unittest.TestCase):
    def test_ask_persists_markdown_and_json_logs(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            context = RunContext.from_repo_root(run_id="demo-support-001", repo_root=repo_root)
            context.initialize()

            bus = InteractionBus()
            answer = bus.ask(
                role="developers",
                question="Vilken teknisk risk bor verifieras forst?",
                context=context,
            )

            self.assertIn("tekniska beroenden", answer)
            qa_log_path = context.work_path / "qa_log.md"
            responses_path = context.work_path / "support_responses.json"
            self.assertTrue(qa_log_path.exists())
            self.assertTrue(responses_path.exists())

            qa_log_content = qa_log_path.read_text(encoding="utf-8")
            self.assertIn("## Q1", qa_log_content)
            self.assertIn("Role: developers", qa_log_content)
            self.assertIn("Question: Vilken teknisk risk bor verifieras forst?", qa_log_content)

            responses = json.loads(responses_path.read_text(encoding="utf-8"))
            self.assertEqual(1, len(responses))
            self.assertEqual("developers", responses[0]["role"])
            self.assertEqual(answer, responses[0]["response"])

    def test_inform_appends_notifications_log(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            context = RunContext.from_repo_root(run_id="demo-notify-001", repo_root=repo_root)
            context.initialize()

            bus = InteractionBus()
            bus.inform(
                role="project_manager",
                event="artifact_approved_and_published",
                artifact_ref="output/vision_malbild.md",
                context=context,
            )

            notifications_path = context.logs_path / "notifications.md"
            self.assertTrue(notifications_path.exists())
            notifications = notifications_path.read_text(encoding="utf-8")
            self.assertIn("## Notification 1", notifications)
            self.assertIn("Role: project_manager", notifications)
            self.assertIn("Event: artifact_approved_and_published", notifications)
            self.assertIn("Artifact: output/vision_malbild.md", notifications)

    def test_business_analyst_asks_support_role_for_unresolved_assumption(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            context = RunContext.from_repo_root(run_id="demo-support-002", repo_root=repo_root)
            context.initialize()

            source_path = context.input_path / "overgripande_behov.md"
            source_path.write_text(
                (
                    "# Overgripande behov\n\n"
                    "- Minska handlaggningstid\n"
                    "- Osakerhet: vilken prioritering ger snabbast effekt?\n"
                ),
                encoding="utf-8",
            )

            agent = BusinessAnalystAgent(interaction_bus=InteractionBus())
            result = agent.produce(
                input_artifacts={"overgripande_behov": source_path},
                context=context,
            )

            produced = result.artifact_path.read_text(encoding="utf-8")
            self.assertIn("Stodfraga till Business Experts", produced)
            self.assertIn("Prioritera behov med tydligast verksamhetsnytta", produced)

            qa_log_content = (context.work_path / "qa_log.md").read_text(encoding="utf-8")
            self.assertIn("Role: business_experts", qa_log_content)
            self.assertIn("Vilket affarsbehov ska prioriteras forst", qa_log_content)


if __name__ == "__main__":
    unittest.main()
