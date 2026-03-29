"""
Generalized prompt builder for any agent role.

Produces the same prompt structure used by the Business Analyst agent,
but parameterised by role name so it works for UX, BA, and future roles.
"""
from __future__ import annotations


class FrameworkPromptBuilder:

    def build_generate_prompt(
        self,
        role_name: str,
        role_text: str,
        sop_text: str,
        artifact_description: str,
        artifact_template: str,
        input_content: dict[str, str],
    ) -> str:
        preamble = self._build_context_section(role_name, role_text, sop_text, artifact_description)
        input_section = self._format_inputs(input_content)

        return f"""{preamble}

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

    def build_update_prompt(
        self,
        role_name: str,
        role_text: str,
        sop_text: str,
        artifact_description: str,
        artifact_template: str,
        input_content: dict[str, str],
        existing_content: str,
    ) -> str:
        preamble = self._build_context_section(role_name, role_text, sop_text, artifact_description)
        input_section = self._format_inputs(input_content)

        return f"""{preamble}

## Artifaktmall — struktur att följa
Nedan är mallen du ska följa. Behåll alla rubriker exakt som de är.
Lägg inte till eller ta bort rubriker.

{artifact_template}

## Befintlig version — uppdatera denna
Nedan är den befintliga versionen av artefakten.
Behåll det som fortfarande stämmer. Uppdatera det som har förändrats baserat på ny input.

{existing_content}

## Input — underlag att basera uppdateringen på
{input_section}

## Uppgift
Generera en uppdaterad version av artefakten baserat på befintlig version och ny input.
Returnera bara det färdiga markdown-dokumentet — inget annat.
"""

    @staticmethod
    def _build_context_section(
        role_name: str,
        role_text: str,
        sop_text: str,
        artifact_description: str,
    ) -> str:
        return (
            f"Du är en {role_name} som arbetar enligt ValueStream OS-ramverket.\n\n"
            f"## Din roll\n{role_text}\n\n"
            f"## SOP — instruktion att följa\n{sop_text}\n\n"
            f"## Artifaktbeskrivning — vad du ska producera\n{artifact_description}"
        )

    @staticmethod
    def _format_inputs(input_content: dict[str, str]) -> str:
        if not input_content:
            return "_Ingen input tillgänglig._"
        parts = [f"### {filename}\n\n{content}" for filename, content in input_content.items()]
        return "\n\n---\n\n".join(parts)
