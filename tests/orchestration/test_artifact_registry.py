import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.orchestration.artifact_registry import ArtifactRegistry


class ArtifactRegistryTests(unittest.TestCase):
    def test_resolves_next_outputs_from_known_input_artifacts(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            docs_root = repo_root / "docs"
            sop_dir = docs_root / "SOP" / "1.Kravställning"
            sop_dir.mkdir(parents=True, exist_ok=True)

            sop_file = sop_dir / "01_vision_och_malbild.md"
            sop_file.write_text(
                "\n".join(
                    [
                        "# SOP 1: Vision & målbild",
                        "",
                        "## 2. Kontext",
                        "",
                        "- Processteg: Kravställning",
                        "- Delprocess: Vision & målbild",
                        "",
                        "## 3. Input",
                        "",
                        "- Övergripande behov",
                        "",
                        "## 4. Output",
                        "",
                        "- Vision & målbild",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            run_root = repo_root / "runs" / "demo-001"
            input_path = run_root / "input"
            work_path = run_root / "work"
            output_path = run_root / "output"
            input_path.mkdir(parents=True, exist_ok=True)
            work_path.mkdir(parents=True, exist_ok=True)
            output_path.mkdir(parents=True, exist_ok=True)
            (input_path / "overgripande_behov.md").write_text(
                "# Övergripande behov\n", encoding="utf-8"
            )

            registry = ArtifactRegistry.from_repo_root(repo_root)
            resolved = registry.resolve_next_outputs(
                input_path=input_path, work_path=work_path, output_path=output_path
            )

            self.assertEqual(1, len(resolved))
            self.assertEqual("vision_malbild", resolved[0].artifact_id)
            self.assertEqual(work_path / "vision_malbild.md", resolved[0].work_path)
            self.assertEqual(output_path / "vision_malbild.md", resolved[0].output_path)

    def test_does_not_return_already_existing_output_artifact(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            docs_root = repo_root / "docs"
            sop_dir = docs_root / "SOP" / "1.Kravställning"
            sop_dir.mkdir(parents=True, exist_ok=True)

            sop_file = sop_dir / "01_vision_och_malbild.md"
            sop_file.write_text(
                "\n".join(
                    [
                        "# SOP 1: Vision & målbild",
                        "",
                        "## 2. Kontext",
                        "",
                        "- Processteg: Kravställning",
                        "- Delprocess: Vision & målbild",
                        "",
                        "## 3. Input",
                        "",
                        "- Övergripande behov",
                        "",
                        "## 4. Output",
                        "",
                        "- Vision & målbild",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            run_root = repo_root / "runs" / "demo-001"
            input_path = run_root / "input"
            work_path = run_root / "work"
            output_path = run_root / "output"
            input_path.mkdir(parents=True, exist_ok=True)
            work_path.mkdir(parents=True, exist_ok=True)
            output_path.mkdir(parents=True, exist_ok=True)
            (input_path / "overgripande_behov.md").write_text(
                "# Övergripande behov\n", encoding="utf-8"
            )
            (work_path / "vision_malbild.md").write_text("# Vision\n", encoding="utf-8")

            registry = ArtifactRegistry.from_repo_root(repo_root)
            resolved = registry.resolve_next_outputs(
                input_path=input_path, work_path=work_path, output_path=output_path
            )

            self.assertEqual([], resolved)


if __name__ == "__main__":
    unittest.main()
