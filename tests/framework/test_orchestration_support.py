"""Unit tests for pure orchestration helpers (no orchestrator or LLM)."""
from __future__ import annotations

from src.framework.models import ApprovalDecision, ArtifactStatus
from src.framework.orchestration_support import (
    build_dry_run_output_filename,
    extract_first_json_object,
    format_approval_feedback_for_revision,
    map_approval_decision_to_artifact_status,
    parse_approval_decision_from_llm_text,
    summarize_plain_text,
)


def test_extract_first_json_object_strips_fenced_block():
    raw = """Here is the JSON:
```json
{"decision": "approved", "summary": "OK"}
```
"""
    parsed = extract_first_json_object(raw)
    assert parsed == {"decision": "approved", "summary": "OK"}


def test_extract_first_json_object_finds_embedded_object():
    raw = 'Prefix text {"decision": "rejected"} trailing'
    parsed = extract_first_json_object(raw)
    assert parsed == {"decision": "rejected"}


def test_summarize_plain_text_truncates():
    long = "word " * 100
    out = summarize_plain_text(long, max_length=20)
    assert len(out) == 20
    assert out.endswith("...")


def test_map_approval_decision_to_artifact_status_defaults_to_approved():
    assert map_approval_decision_to_artifact_status("approved") == ArtifactStatus.approved
    assert map_approval_decision_to_artifact_status("unknown") == ArtifactStatus.approved


def test_build_dry_run_output_filename_prompt_suffix():
    assert build_dry_run_output_filename("vision.md", "prompt") == "vision_prompt_dry_run.txt"


def test_build_dry_run_output_filename_phase_suffix():
    assert build_dry_run_output_filename("vision.md", "draft") == "vision_draft_prompt_dry_run.txt"


def test_parse_approval_decision_dry_run_shape():
    decision = parse_approval_decision_from_llm_text(
        step_id="s1",
        artifact_name="A",
        artifact_filename="a.md",
        approver_agent_id="produktagare",
        raw_text="ignored",
        dry_run=True,
    )
    assert decision.decision == "approved_with_notes"
    assert decision.changes_requested == []


def test_parse_approval_decision_from_json_string():
    raw = '{"decision":"approved_with_notes","summary":"S","rationale":"R","changes_requested":["x"]}'
    decision = parse_approval_decision_from_llm_text(
        step_id="s1",
        artifact_name="A",
        artifact_filename="a.md",
        approver_agent_id="pa",
        raw_text=raw,
        dry_run=False,
    )
    assert decision.decision == "approved_with_notes"
    assert decision.summary == "S"
    assert decision.changes_requested == ["x"]


def test_format_approval_feedback_for_revision_in_support_module():
    text = format_approval_feedback_for_revision(
        ApprovalDecision(
            step_id="s",
            artifact_name="A",
            artifact_filename="a.md",
            approver_agent_id="pa",
            decision="approved_with_notes",
            summary="Sum",
            rationale="Why",
            changes_requested=["One"],
        )
    )
    assert "Beslut: approved_with_notes" in text
    assert "Sammanfattning: Sum" in text
    assert "Begärda ändringar:" in text
    assert "- One" in text
