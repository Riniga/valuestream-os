"""
Pure helpers for process-step orchestration.

JSON extraction, text summaries, dry-run filenames, and approval parsing live here
so they can be unit-tested without running the full Orchestrator or LLM calls.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from src.framework.models import ApprovalDecision, ArtifactStatus


def extract_first_json_object(raw_text: str) -> dict[str, object] | None:
    """Return the first top-level JSON object found in ``raw_text``, or None."""
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            data, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            return data
    return None


def summarize_plain_text(text: str, max_length: int = 180) -> str:
    """Collapse whitespace and truncate to ``max_length`` with an ellipsis."""
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= max_length:
        return compact
    return compact[: max_length - 3] + "..."


def default_consultation_questions(artifact_name: str) -> list[str]:
    return [
        f"Vad i {artifact_name} behöver förtydligas för att fungera i praktiken?",
        "Vilka risker, beroenden eller oklarheter ser du?",
        "Vilka justeringar skulle förbättra kvaliteten inför godkännande?",
    ]


def map_approval_decision_to_artifact_status(decision: str) -> ArtifactStatus:
    mapping = {
        "approved": ArtifactStatus.approved,
        "approved_with_notes": ArtifactStatus.approved_with_notes,
        "rejected": ArtifactStatus.rejected,
    }
    if decision not in mapping:
        raise ValueError(f"Okänt approval-beslut: {decision}")
    return mapping[decision]


def update_status_cell_in_markdown_table(content: str, decision: str) -> str:
    """
    Update the first markdown table cell after ``Status`` in metadata-style tables.

    Swedish labels match artifact templates (Godkänd, Godkänd med kommentarer, Avslagen).
    """
    decision_to_document_status = {
        "approved": "Godkänd",
        "approved_with_notes": "Godkänd med kommentarer",
        "rejected": "Avslagen",
    }
    document_status = decision_to_document_status.get(decision)
    if not document_status:
        return content

    updated_content, replacements = re.subn(
        r"(\|\s*Status\s*\|\s*)([^|]*)(\|)",
        rf"\g<1>{document_status} \g<3>",
        content,
        count=1,
        flags=re.IGNORECASE,
    )
    return updated_content if replacements else content


def build_dry_run_output_filename(output_filename: str, suffix: str) -> str:
    """Build the filename used when ``dry_run`` writes prompts to the output folder."""
    base = Path(output_filename)
    if suffix == "prompt":
        return f"{base.stem}_prompt_dry_run.txt"
    return f"{base.stem}_{suffix}_prompt_dry_run.txt"


def approval_value_as_string(value: object, default: str = "") -> str:
    return value if isinstance(value, str) else default


def approval_value_as_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def format_approval_feedback_for_revision(decision: ApprovalDecision) -> str:
    lines = [f"Beslut: {decision.decision}"]
    if decision.summary:
        lines.append(f"Sammanfattning: {decision.summary}")
    if decision.rationale:
        lines.append(f"Motivering: {decision.rationale}")
    if decision.changes_requested:
        lines.append("Begärda ändringar:")
        lines.extend(f"- {item}" for item in decision.changes_requested)
    return "\n".join(lines)


def parse_approval_decision_from_llm_text(
    *,
    step_id: str,
    artifact_name: str,
    artifact_filename: str,
    approver_agent_id: str,
    raw_text: str,
    dry_run: bool,
) -> ApprovalDecision:
    """Parse structured approval from model output; fall back to heuristics if JSON is missing."""
    parsed = None if dry_run else extract_first_json_object(raw_text)
    if dry_run:
        parsed = {
            "decision": "approved_with_notes",
            "summary": "Dry-run simulerade ett godkännande med kommentarer.",
            "rationale": "Ingen LLM kördes; approval-prompt genererades endast för granskning.",
            "changes_requested": [],
        }
    if parsed is None:
        lowered = raw_text.lower()
        if "rejected" in lowered:
            decision = "rejected"
        elif "approved_with_notes" in lowered:
            decision = "approved_with_notes"
        else:
            decision = "approved"
        parsed = {
            "decision": decision,
            "summary": summarize_plain_text(raw_text),
            "rationale": raw_text.strip(),
            "changes_requested": [],
        }
    decision_value = approval_value_as_string(parsed.get("decision"), default="approved")
    if decision_value not in {"approved", "approved_with_notes", "rejected"}:
        raise ValueError(f"Okänt approval-beslut från modelloutput: {decision_value}")
    return ApprovalDecision(
        step_id=step_id,
        artifact_name=artifact_name,
        artifact_filename=artifact_filename,
        approver_agent_id=approver_agent_id,
        decision=decision_value,
        summary=approval_value_as_string(parsed.get("summary")),
        rationale=approval_value_as_string(parsed.get("rationale")),
        changes_requested=approval_value_as_string_list(parsed.get("changes_requested")),
    )
