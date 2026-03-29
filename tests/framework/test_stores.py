"""
Tests for file-based state stores.

Verify that RunStateStore, ArtifactStateStore, AgentMemoryStore and RunLog
round-trip their data correctly and produce readable JSON files.
No LLM or network calls are made.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from src.framework.models import (
    ApprovalDecision,
    ArtifactStatus,
    ConsultationRequest,
    ConsultationResponse,
    ExpertContext,
    InformedRoleBrief,
    RunStatus,
    StepStatus,
)
from src.framework.stores import (
    ApprovalStore,
    AgentMemoryStore,
    ArtifactStateStore,
    ConsultationStore,
    ExpertContextStore,
    InformedRoleBriefStore,
    RunLog,
    RunStateStore,
)


@pytest.fixture()
def run_dir(tmp_path: Path) -> Path:
    d = tmp_path / "runs" / "test-run"
    d.mkdir(parents=True)
    return d


# ---------------------------------------------------------------------------
# RunStateStore
# ---------------------------------------------------------------------------

def test_run_state_initialize_creates_file(run_dir):
    store = RunStateStore(run_dir)
    state = store.initialize("test-run", "test-flow", ["step-a", "step-b"])
    assert (run_dir / "run_state.json").exists()
    assert state.run_id == "test-run"
    assert state.status == RunStatus.running
    assert state.step_statuses["step-a"] == StepStatus.pending.value


def test_run_state_save_and_load_roundtrip(run_dir):
    store = RunStateStore(run_dir)
    state = store.initialize("test-run", "test-flow", ["step-a"])
    state.step_statuses["step-a"] = StepStatus.completed.value
    state.status = RunStatus.completed
    store.save(state)

    loaded = store.load()
    assert loaded is not None
    assert loaded.status == RunStatus.completed
    assert loaded.step_statuses["step-a"] == StepStatus.completed.value


def test_run_state_load_returns_none_when_missing(run_dir):
    store = RunStateStore(run_dir)
    assert store.load() is None


# ---------------------------------------------------------------------------
# ArtifactStateStore
# ---------------------------------------------------------------------------

def test_artifact_state_initialize_creates_file(run_dir):
    store = ArtifactStateStore(run_dir)
    state = store.initialize("test-run")
    assert (run_dir / "artifact_state.json").exists()
    assert state.run_id == "test-run"
    assert state.artifacts == {}


def test_artifact_state_record_produced(run_dir):
    store = ArtifactStateStore(run_dir)
    state = store.initialize("test-run")
    store.record_produced(state, "vision.md", "Vision & målbild", "ba-vision")
    assert "vision.md" in state.artifacts
    assert state.artifacts["vision.md"].status == ArtifactStatus.produced


def test_artifact_state_record_failed(run_dir):
    store = ArtifactStateStore(run_dir)
    state = store.initialize("test-run")
    store.record_failed(state, "vision.md", "Vision & målbild", "ba-vision")
    assert state.artifacts["vision.md"].status == ArtifactStatus.failed


def test_artifact_state_roundtrip(run_dir):
    store = ArtifactStateStore(run_dir)
    state = store.initialize("test-run")
    store.record_status(
        state,
        "vision.md",
        "Vision & målbild",
        "ba-vision",
        ArtifactStatus.approved_with_notes,
        consult_agent_ids=["verksamhetsexperter"],
        approver_agent_id="produktagare",
        informed_agent_ids=["utvecklare"],
        latest_phase="approval",
        approval_decision="approved_with_notes",
    )

    loaded = store.load()
    assert loaded is not None
    assert loaded.artifacts["vision.md"].status == ArtifactStatus.approved_with_notes
    assert loaded.artifacts["vision.md"].producer_step_id == "ba-vision"
    assert loaded.artifacts["vision.md"].consult_agent_ids == ["verksamhetsexperter"]
    assert loaded.artifacts["vision.md"].approver_agent_id == "produktagare"
    assert loaded.artifacts["vision.md"].informed_agent_ids == ["utvecklare"]
    assert loaded.artifacts["vision.md"].latest_phase == "approval"
    assert loaded.artifacts["vision.md"].approval_decision == "approved_with_notes"


# ---------------------------------------------------------------------------
# AgentMemoryStore
# ---------------------------------------------------------------------------

def test_agent_memory_load_returns_empty_when_missing(run_dir):
    store = AgentMemoryStore(run_dir)
    mem = store.load("business-analyst", "test-run")
    assert mem.agent_id == "business-analyst"
    assert mem.entries == {}


def test_agent_memory_set_and_load(run_dir):
    store = AgentMemoryStore(run_dir)
    mem = store.load("ux", "test-run")
    store.set_entry(mem, "last_artifact", "user_journeys.md")

    loaded = store.load("ux", "test-run")
    assert loaded.entries["last_artifact"] == "user_journeys.md"


def test_agent_memory_file_created(run_dir):
    store = AgentMemoryStore(run_dir)
    mem = store.load("business-analyst", "test-run")
    store.save(mem)
    assert (run_dir / "agent_memory_business-analyst.json").exists()


def test_consultation_store_roundtrip(run_dir):
    store = ConsultationStore(run_dir)
    store.append_request(
        ConsultationRequest(
            request_id="req-1",
            step_id="backlog",
            artifact_name="Prioriterad backlog",
            artifact_filename="prioriterad_backlog.md",
            requester_agent_id="business-analyst",
            consultant_agent_ids=["verksamhetsexperter"],
            questions=["Vad bör justeras?"],
            draft_summary="Kort sammanfattning",
        )
    )
    store.append_response(
        ConsultationResponse(
            request_id="req-1",
            step_id="backlog",
            artifact_name="Prioriterad backlog",
            consultant_agent_id="verksamhetsexperter",
            response_text="Bra riktning men förtydliga beroenden.",
            summary="Förtydliga beroenden.",
        )
    )

    requests = store.load_requests()
    responses = store.load_responses_for_step("backlog")

    assert len(requests) == 1
    assert requests[0].consultant_agent_ids == ["verksamhetsexperter"]
    assert len(responses) == 1
    assert responses[0].summary == "Förtydliga beroenden."


def test_approval_store_roundtrip(run_dir):
    store = ApprovalStore(run_dir)
    store.append(
        ApprovalDecision(
            step_id="backlog",
            artifact_name="Prioriterad backlog",
            artifact_filename="prioriterad_backlog.md",
            approver_agent_id="produktagare",
            decision="approved_with_notes",
            summary="Godkänd med kommentarer.",
            rationale="Bra riktning.",
            changes_requested=["Förtydliga MVP"],
        )
    )

    decision = store.load_for_step("backlog")

    assert decision is not None
    assert decision.decision == "approved_with_notes"
    assert decision.changes_requested == ["Förtydliga MVP"]


def test_informed_role_brief_store_roundtrip(run_dir):
    store = InformedRoleBriefStore(run_dir)
    store.append(
        InformedRoleBrief(
            step_id="backlog",
            artifact_name="Prioriterad backlog",
            artifact_filename="prioriterad_backlog.md",
            role_agent_id="utvecklare",
            brief_text="Fokusera på högsta prioritet i första leveransen.",
            relevance="Påverkar kommande implementation.",
        )
    )

    briefs = store.load_for_step("backlog")

    assert len(briefs) == 1
    assert briefs[0].role_agent_id == "utvecklare"


def test_expert_context_store_roundtrip(run_dir):
    store = ExpertContextStore(run_dir)
    store.save(
        ExpertContext(
            agent_id="verksamhetsexperter",
            run_id="test-run",
            artifact_name="Prioriterad backlog",
            context_text="Viktig verksamhetskontext.",
            source_filenames=["vision_och_malbild.md"],
        )
    )

    context = store.load("verksamhetsexperter", "test-run", "Prioriterad backlog")

    assert context is not None
    assert context.context_text == "Viktig verksamhetskontext."
    assert context.source_filenames == ["vision_och_malbild.md"]


# ---------------------------------------------------------------------------
# RunLog
# ---------------------------------------------------------------------------

def test_run_log_append_and_load(run_dir):
    log = RunLog(run_dir)
    log.append({"event": "run_started", "run_id": "test-run"})
    log.append({"event": "step_completed", "step_id": "ba-vision"})

    entries = log.load()
    assert len(entries) == 2
    assert entries[0]["event"] == "run_started"
    assert entries[1]["event"] == "step_completed"
    assert "timestamp" in entries[0]


def test_run_log_empty_when_missing(run_dir):
    log = RunLog(run_dir)
    assert log.load() == []
