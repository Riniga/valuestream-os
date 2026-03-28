"""
PromptBuilder — constructs LLM prompts for the Business Analyst agent.

Prompts are built entirely from framework documents and run-time input.
No hardcoded artifact text — all content comes from docs/ and runs/.
"""

from __future__ import annotations


class PromptBuilder:
    """
    Assembles the generate prompt from:
        - role definition (docs/Roller/Business Analyst.md)
        - SOP instructions (docs/SOP/...)
        - artifact description (docs/Artifakter/Descriptions/...)
        - artifact template (docs/Artifakter/Innehåll/...)
        - run input files (runs/<run-id>/input/...)
    """

    def build_generate_prompt(
        self,
        role_text: str,
        sop_text: str,
        artifact_description: str,
        artifact_template: str,
        input_content: dict[str, str],
    ) -> str:
        """
        Return a complete prompt string for artifact generation.

        Args:
            role_text: Full role definition markdown.
            sop_text: Full SOP markdown.
            artifact_description: Artifact description markdown.
            artifact_template: Artifact template markdown (structure to fill in).
            input_content: Dict of {filename: content} for each input artifact.
        """
        input_section = self._format_inputs(input_content)

        return f"""Du är en Business Analyst som arbetar enligt ValueStream OS-ramverket.

## Din roll
{role_text}

## SOP — instruktion att följa
{sop_text}

## Artifaktbeskrivning — vad du ska producera
{artifact_description}

## Artifaktmall — fyll i denna struktur
Nedan är mallen du ska fylla i. Behåll alla rubriker exakt som de är.
Ersätt platshållartext med verkligt innehåll baserat på inputen nedan.
Lägg inte till eller ta bort rubriker.

{artifact_template}

## Input — underlag att basera artifakten på
{input_section}

## Uppgift
Generera artifakten enligt mallen ovan baserat på inputen.
Returnera bara det färdiga markdown-dokumentet — inget annat.
"""

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _format_inputs(input_content: dict[str, str]) -> str:
        if not input_content:
            return "_Ingen input tillgänglig._"
        parts = []
        for filename, content in input_content.items():
            parts.append(f"### {filename}\n\n{content}")
        return "\n\n---\n\n".join(parts)
