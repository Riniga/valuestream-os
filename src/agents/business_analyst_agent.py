from __future__ import annotations

from pathlib import Path
from typing import Mapping

from src.agents.agent_contract import AgentArtifactOutput
from src.orchestration.run_context import RunContext
from src.roles.interaction_bus import InteractionBus


class BusinessAnalystAgent:
    """Produces a first Vision and goal image draft from needs input."""

    producer_name = "business_analyst"
    required_input_id = "overgripande_behov"
    output_artifact_id = "vision_malbild"
    output_filename = "vision_malbild.md"
    required_headings = (
        "# Vision och malbild",
        "## Malbild",
        "## Affarsbehov",
        "## Avgransningar och antaganden",
    )

    def __init__(self, interaction_bus: InteractionBus | None = None) -> None:
        self.interaction_bus = interaction_bus or InteractionBus()

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
        needs = self._extract_needs(source_text)
        support_answer = None
        if self._has_unresolved_assumption(source_text):
            support_answer = self.interaction_bus.ask(
                role="business_experts",
                question="Vilket affarsbehov ska prioriteras forst for att minska osakerhet?",
                context=context,
            )

        output_text = self._build_output(
            needs=needs,
            source_path=source_path,
            support_answer=support_answer,
        )

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
    def _extract_needs(source_text: str) -> list[str]:
        bullet_needs = [line.strip()[2:].strip() for line in source_text.splitlines() if line.strip().startswith("- ")]
        if bullet_needs:
            return bullet_needs

        fallback = [line.strip() for line in source_text.splitlines() if line.strip()]
        return fallback[:5] if fallback else ["Behovsunderlag saknar detaljer."]

    @staticmethod
    def _has_unresolved_assumption(source_text: str) -> bool:
        normalized = source_text.lower()
        return "?" in source_text or "antagande" in normalized or "osakerhet" in normalized

    def _build_output(
        self,
        *,
        needs: list[str],
        source_path: Path,
        support_answer: str | None,
    ) -> str:
        needs_block = "\n".join(f"- {need}" for need in needs)
        support_section = ""
        if support_answer:
            support_section = (
                "- Stodfraga till Business Experts: Vilket affarsbehov ska prioriteras forst?\n"
                f"- Svar: {support_answer}\n"
            )
        return (
            f"{self.required_headings[0]}\n\n"
            "Första utkast till vision och målbild baserat pa inkomna behov.\n\n"
            f"{self.required_headings[1]}\n\n"
            "Vi skapar en tydlig och vardedriven riktning for losningen.\n\n"
            f"{self.required_headings[2]}\n\n"
            f"{needs_block}\n\n"
            f"{self.required_headings[3]}\n\n"
            f"- Kalla: `{source_path.name}`\n"
            "- Antagande: prioritering bekraftas med Product Owner.\n"
            f"{support_section}"
        )
