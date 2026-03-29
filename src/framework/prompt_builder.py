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
        output_rules = self._build_output_rules()

        return f"""{preamble}

## Rendermall — slutlig struktur att producera
Använd endast denna mall som slutlig struktur för dokumentet.
Behåll rubrikerna, fyll sektionerna med verkligt innehåll och returnera ett färdigt markdown-dokument.
Ingen instruktionstext, inga frågor och inga exempelrader får finnas kvar i slutresultatet.

{artifact_template}

## Input — underlag att basera artifakten på
{input_section}

## Outputregler
{output_rules}

## Uppgift
Generera artifakten enligt rendermallen ovan baserat på inputen.
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
        output_rules = self._build_output_rules()

        return f"""{preamble}

## Rendermall — slutlig struktur att producera
Använd endast denna mall som slutlig struktur för dokumentet.
Behåll rubrikerna, fyll sektionerna med verkligt innehåll och returnera ett färdigt markdown-dokument.
Ingen instruktionstext, inga frågor och inga exempelrader får finnas kvar i slutresultatet.

{artifact_template}

## Befintlig version — uppdatera denna
Nedan är den befintliga versionen av artefakten.
Behåll det som fortfarande stämmer. Uppdatera det som har förändrats baserat på ny input.

{existing_content}

## Input — underlag att basera uppdateringen på
{input_section}

## Outputregler
{output_rules}

## Uppgift
Generera en uppdaterad version av artefakten baserat på befintlig version, inputen och rendermallen.
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
            f"## Designunderlag — vad artefakten ska åstadkomma\n"
            f"Detta är vägledning för innehåll, kvalitet och syfte.\n"
            f"Text från designunderlaget får inte kopieras som instruktioner till slutdokumentet.\n\n"
            f"{artifact_description}"
        )

    @staticmethod
    def _build_output_rules() -> str:
        return (
            "- Returnera bara det färdiga markdown-dokumentet.\n"
            "- Behåll endast rubriker, tabeller och sektioner som hör till slutdokumentet.\n"
            "- Lämna inte kvar instruktioner som 'Beskriv', 'Lista', 'Frågor att besvara' eller liknande hjälptext.\n"
            "- Lämna inte kvar platshållare eller exempeltext som '[Namn]', 'YYYY-MM-DD', "
            "'Utkast / Pågående / Klar' eller exempelrader som visar format.\n"
            "- Om en sektion saknar säkert underlag, skriv en kort saklig formulering i stället för att lämna kvar malltext."
        )

    @staticmethod
    def _format_inputs(input_content: dict[str, str]) -> str:
        if not input_content:
            return "_Ingen input tillgänglig._"
        parts = [f"### {filename}\n\n{content}" for filename, content in input_content.items()]
        return "\n\n---\n\n".join(parts)
