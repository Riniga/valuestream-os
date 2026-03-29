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

    def build_consultation_prompt(
        self,
        role_name: str,
        role_text: str,
        artifact_name: str,
        artifact_content: str,
        questions: list[str],
        expert_context: str = "",
    ) -> str:
        question_lines = "\n".join(f"- {question}" for question in questions) or "- Ge din viktigaste återkoppling."
        expert_section = f"\n\n## Run-specifik expertkontext\n{expert_context}" if expert_context else ""
        return (
            f"Du agerar som {role_name} i en konsultationsfas enligt ValueStream OS.\n\n"
            f"## Din roll\n{role_text}{expert_section}\n\n"
            f"## Artifakt att granska\n"
            f"Namn: {artifact_name}\n\n"
            f"{artifact_content}\n\n"
            f"## Frågor att besvara\n{question_lines}\n\n"
            f"## Outputregler\n"
            f"- Svara på svenska.\n"
            f"- Var konkret, saklig och fokuserad på förbättringar.\n"
            f"- Strukturera svaret med rubrikerna `## Sammanfattning`, `## Styrkor`, `## Risker`, `## Rekommenderade ändringar`.\n"
            f"- Referera till verksamhetskontext eller användarbehov när det är relevant.\n"
        )

    def build_revision_prompt(
        self,
        role_name: str,
        role_text: str,
        artifact_name: str,
        artifact_description: str,
        artifact_template: str,
        existing_content: str,
        consultation_feedback: dict[str, str],
        input_content: dict[str, str],
    ) -> str:
        feedback_sections = "\n\n---\n\n".join(
            f"### {agent_id}\n\n{content}" for agent_id, content in consultation_feedback.items()
        ) or "_Ingen konsultationsfeedback tillgänglig._"
        return (
            f"Du är en {role_name} som reviderar artifakten `{artifact_name}` efter konsultation.\n\n"
            f"## Din roll\n{role_text}\n\n"
            f"## Designunderlag\n{artifact_description}\n\n"
            f"## Rendermall\n{artifact_template}\n\n"
            f"## Nuvarande version\n{existing_content}\n\n"
            f"## Konsultationsfeedback\n{feedback_sections}\n\n"
            f"## Underlag\n{self._format_inputs(input_content)}\n\n"
            f"## Outputregler\n{self._build_output_rules()}\n\n"
            f"## Uppgift\n"
            f"Revidera artifakten så att relevant konsultationsfeedback arbetas in utan att lämna malltext kvar i resultatet.\n"
            f"Returnera bara det färdiga markdown-dokumentet.\n"
        )

    def build_approval_prompt(
        self,
        role_name: str,
        role_text: str,
        artifact_name: str,
        artifact_content: str,
        consultation_feedback: dict[str, str],
    ) -> str:
        feedback_sections = "\n\n---\n\n".join(
            f"### {agent_id}\n\n{content}" for agent_id, content in consultation_feedback.items()
        ) or "_Ingen konsultationsfeedback tillgänglig._"
        return (
            f"Du är en {role_name} och har A-ansvar för artifakten `{artifact_name}`.\n\n"
            f"## Din roll\n{role_text}\n\n"
            f"## Artifakt att besluta om\n{artifact_content}\n\n"
            f"## Konsultationsunderlag\n{feedback_sections}\n\n"
            f"## Uppgift\n"
            f"Bedöm om artifakten ska godkännas.\n"
            f"Returnera ENDAST JSON enligt detta schema:\n"
            f'{{"decision":"approved|approved_with_notes|rejected","summary":"kort sammanfattning","rationale":"motivering","changes_requested":["punkt 1","punkt 2"]}}\n'
        )

    def build_informing_prompt(
        self,
        role_name: str,
        role_text: str,
        artifact_name: str,
        artifact_content: str,
        decision_summary: str,
    ) -> str:
        return (
            f"Du agerar som {role_name} och ska ta emot information om artifakten `{artifact_name}`.\n\n"
            f"## Din roll\n{role_text}\n\n"
            f"## Godkänd artifakt\n{artifact_content}\n\n"
            f"## Beslutssammanfattning\n{decision_summary}\n\n"
            f"## Uppgift\n"
            f"Skapa en kort rollanpassad brief på svenska med rubrikerna `## Sammanfattning`, `## Relevans för rollen`, `## Att ha i åtanke`.\n"
            f"Fokusera på vad denna roll behöver känna till inför kommande arbete.\n"
        )

    def build_expert_context_prompt(
        self,
        artifact_name: str,
        input_content: dict[str, str],
        prior_notes: list[str],
    ) -> str:
        note_block = "\n\n---\n\n".join(prior_notes) if prior_notes else "_Inga tidigare noter._"
        return (
            f"Bygg ett kort expertunderlag för artifakten `{artifact_name}`.\n\n"
            f"## Input från runnen\n{self._format_inputs(input_content)}\n\n"
            f"## Tidigare noter\n{note_block}\n\n"
            f"## Uppgift\n"
            f"Sammanfatta verksamhetskontext, viktiga regler, antaganden och risker som en verksamhetsexpert bör känna till i denna run.\n"
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
