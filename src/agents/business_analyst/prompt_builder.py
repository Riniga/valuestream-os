from __future__ import annotations


class PromptBuilder:

    def build_generate_prompt(
        self,
        role_text: str,
        sop_text: str,
        artifact_description: str,
        artifact_template: str,
        input_content: dict[str, str],
    ) -> str:
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

    @staticmethod
    def _format_inputs(input_content: dict[str, str]) -> str:
        if not input_content:
            return "_Ingen input tillgänglig._"
        parts = [f"### {filename}\n\n{content}" for filename, content in input_content.items()]
        return "\n\n---\n\n".join(parts)
