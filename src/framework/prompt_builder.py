"""
Generalized prompt builder for any agent role.

Parameterised by role name so it works for Business Analyst, UX, and future roles.
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
        render_section = self._build_render_section(artifact_template)
        input_section = self._format_inputs(input_content)
        output_rules = self._build_output_rules()

        return (
            f"{preamble}\n\n"
            f"{render_section}\n\n"
            f"## Input — underlag att basera artifakten på\n{input_section}\n\n"
            f"## Outputregler\n{output_rules}\n\n"
            f"## Uppgift\n"
            f"Generera artifakten enligt rendermallen ovan baserat på inputen.\n"
            f"Returnera bara det färdiga markdown-dokumentet — inget annat.\n"
        )

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
        render_section = self._build_render_section(artifact_template)
        input_section = self._format_inputs(input_content)
        output_rules = self._build_output_rules()

        return (
            f"{preamble}\n\n"
            f"{render_section}\n\n"
            f"## Befintlig version — uppdatera denna\n"
            f"Behåll det som fortfarande stämmer. Uppdatera det som har förändrats baserat på ny input.\n\n"
            f"{existing_content}\n\n"
            f"## Input — underlag att basera uppdateringen på\n{input_section}\n\n"
            f"## Outputregler\n{output_rules}\n\n"
            f"## Uppgift\n"
            f"Generera en uppdaterad version av artefakten baserat på befintlig version, inputen och rendermallen.\n"
            f"Returnera bara det färdiga markdown-dokumentet — inget annat.\n"
        )

    @staticmethod
    def _build_render_section(artifact_template: str) -> str:
        return (
            "## Rendermall — slutlig struktur att producera\n"
            "Använd endast denna mall som slutlig struktur för dokumentet.\n"
            "Behåll rubrikerna, fyll sektionerna med verkligt innehåll och returnera ett färdigt markdown-dokument.\n"
            "Ingen instruktionstext, inga frågor och inga exempelrader får finnas kvar i slutresultatet.\n\n"
            f"{artifact_template}"
        )

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
