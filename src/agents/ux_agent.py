from __future__ import annotations

from pathlib import Path
from typing import Mapping

from src.agents.agent_contract import AgentArtifactOutput
from src.orchestration.run_context import RunContext


class UXAgent:
    """Produces a UX concept draft from Vision and goal image."""

    producer_name = "ux"
    required_input_id = "vision_malbild"
    output_artifact_id = "ux_koncept"
    output_filename = "ux_koncept.md"
    required_headings = (
        "# UX koncept",
        "## Malgrupper och behov",
        "## Nyckelfloden",
        "## UX-principer",
    )

    def produce(
        self,
        input_artifacts: Mapping[str, Path],
        context: RunContext,
    ) -> AgentArtifactOutput:
        if self.required_input_id not in input_artifacts:
            raise ValueError(
                f"Missing required input artifact: {self.required_input_id}"
            )

        source_path = input_artifacts[self.required_input_id]
        source_text = source_path.read_text(encoding="utf-8")
        assumptions = self._extract_assumptions(source_text)
        output_text = self._build_output(assumptions=assumptions, source_path=source_path)

        output_path = context.work_path / self.output_filename
        output_path.write_text(output_text, encoding="utf-8")

        return AgentArtifactOutput(
            artifact_id=self.output_artifact_id,
            artifact_path=output_path,
            produced_by=self.producer_name,
            source_artifact_ids=(self.required_input_id,),
            required_headings=self.required_headings,
        )

    @staticmethod
    def _extract_assumptions(source_text: str) -> list[str]:
        assumptions: list[str] = []
        for line in source_text.splitlines():
            stripped = line.strip()
            if stripped.startswith("- "):
                assumptions.append(stripped[2:].strip())
        return assumptions[:4] if assumptions else ["Visionen behover verifieras med slutanvandare."]

    def _build_output(self, *, assumptions: list[str], source_path: Path) -> str:
        assumptions_block = "\n".join(f"- {item}" for item in assumptions)
        return (
            f"{self.required_headings[0]}\n\n"
            "Utkast till UX-inriktning som konkretiserar visionen.\n\n"
            f"{self.required_headings[1]}\n\n"
            "- Primar anvandare: verksamhetsrepresentant.\n"
            "- Sekundar anvandare: beslutsfattare.\n\n"
            f"{self.required_headings[2]}\n\n"
            "- Skapa underlag\n"
            "- Granska prioritering\n"
            "- Godkann scope\n\n"
            f"{self.required_headings[3]}\n\n"
            f"{assumptions_block}\n\n"
            f"- Kalla: `{source_path.name}`\n"
        )
