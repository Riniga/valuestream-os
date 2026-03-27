import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.agents.business_analyst_agent import BusinessAnalystAgent
from src.agents.ux_agent import UXAgent
from src.orchestration.run_context import RunContext


class ProducerAgentTests(unittest.TestCase):
    def test_business_analyst_produces_expected_headings(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            context = RunContext.from_repo_root(run_id="demo-001", repo_root=repo_root)
            context.initialize()

            source_path = context.input_path / "overgripande_behov.md"
            source_path.write_text(
                "# Overgripande behov\n\n- Kortare ledtid\n- Tydligare prioritering\n",
                encoding="utf-8",
            )

            agent = BusinessAnalystAgent()
            result = agent.produce(
                input_artifacts={"overgripande_behov": source_path},
                context=context,
            )

            self.assertEqual("vision_malbild", result.artifact_id)
            self.assertEqual(context.work_path / "vision_malbild.md", result.artifact_path)
            self.assertTrue(result.artifact_path.exists())
            content = result.artifact_path.read_text(encoding="utf-8")
            for heading in result.required_headings:
                self.assertIn(heading, content)

    def test_ux_agent_produces_expected_headings(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            context = RunContext.from_repo_root(run_id="demo-002", repo_root=repo_root)
            context.initialize()

            source_path = context.work_path / "vision_malbild.md"
            source_path.write_text(
                "# Vision och malbild\n\n## Affarsbehov\n- Kortare ledtid\n- Tydligare ansvar\n",
                encoding="utf-8",
            )

            agent = UXAgent()
            result = agent.produce(
                input_artifacts={"vision_malbild": source_path},
                context=context,
            )

            self.assertEqual("ux_koncept", result.artifact_id)
            self.assertEqual(context.work_path / "ux_koncept.md", result.artifact_path)
            self.assertTrue(result.artifact_path.exists())
            content = result.artifact_path.read_text(encoding="utf-8")
            for heading in result.required_headings:
                self.assertIn(heading, content)


if __name__ == "__main__":
    unittest.main()
