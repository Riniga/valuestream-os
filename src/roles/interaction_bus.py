from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from src.orchestration.run_context import RunContext


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


class InteractionBus:
    """File-backed support role interaction helper."""

    def __init__(
        self,
        responder: Callable[[str, str, RunContext], str] | None = None,
    ) -> None:
        self._responder = responder or self._default_responder

    def ask(self, role: str, question: str, context: RunContext) -> str:
        response = self._responder(role, question, context)
        entry = self._build_entry(role=role, question=question, response=response)
        self._append_response_entry(context=context, entry=entry)
        self._append_qa_log(context=context, entry=entry)
        return response

    def inform(
        self,
        *,
        role: str,
        event: str,
        artifact_ref: str,
        context: RunContext,
    ) -> None:
        entry = {
            "timestamp": _utc_timestamp(),
            "role": role,
            "event": event,
            "artifact_ref": artifact_ref,
        }
        self._append_notification_log(context=context, entry=entry)

    @staticmethod
    def _default_responder(role: str, question: str, context: RunContext) -> str:
        del context
        normalized_role = role.strip().lower()
        if normalized_role == "business_experts":
            return (
                "Prioritera behov med tydligast verksamhetsnytta och kortast tid till beslut."
            )
        if normalized_role == "project_manager":
            return "Behall scope till en levererbar forsta version for att minska risk."
        if normalized_role == "developers":
            return "Bekrafta tekniska beroenden tidigt och undvik antaganden utan verifiering."
        if normalized_role == "user_representatives":
            return "Borja med det arbetsflode som anvands dagligen av flest anvandare."
        if normalized_role == "ux":
            return "Validera antagandet med en snabb prototyp och ett anvandartest."
        return f"Inget standardsvar for rollen '{role}'. Fraga fortydligad: {question}"

    @staticmethod
    def _build_entry(*, role: str, question: str, response: str) -> dict[str, str]:
        return {
            "timestamp": _utc_timestamp(),
            "role": role,
            "question": question,
            "response": response,
        }

    @staticmethod
    def _responses_path(context: RunContext) -> Path:
        return context.work_path / "support_responses.json"

    @staticmethod
    def _qa_log_path(context: RunContext) -> Path:
        return context.work_path / "qa_log.md"

    @staticmethod
    def _notifications_log_path(context: RunContext) -> Path:
        return context.logs_path / "notifications.md"

    def _append_response_entry(self, *, context: RunContext, entry: dict[str, str]) -> None:
        responses_path = self._responses_path(context)
        existing = self._read_existing_entries(responses_path)
        existing.append(entry)
        responses_path.write_text(
            f"{json.dumps(existing, indent=2, sort_keys=True)}\n",
            encoding="utf-8",
        )

    @staticmethod
    def _read_existing_entries(path: Path) -> list[dict[str, str]]:
        if not path.exists():
            return []
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(loaded, list):
            return [item for item in loaded if isinstance(item, dict)]
        return []

    def _append_qa_log(self, *, context: RunContext, entry: dict[str, str]) -> None:
        qa_log_path = self._qa_log_path(context)
        question_index = self._existing_question_count(qa_log_path) + 1
        block = (
            f"## Q{question_index}\n"
            f"- Timestamp: {entry['timestamp']}\n"
            f"- Role: {entry['role']}\n"
            f"- Question: {entry['question']}\n"
            f"- Answer: {entry['response']}\n\n"
        )
        with qa_log_path.open("a", encoding="utf-8") as qa_file:
            qa_file.write(block)

    @staticmethod
    def _existing_question_count(path: Path) -> int:
        if not path.exists():
            return 0
        return path.read_text(encoding="utf-8").count("## Q")

    def _append_notification_log(
        self,
        *,
        context: RunContext,
        entry: dict[str, str],
    ) -> None:
        notifications_path = self._notifications_log_path(context)
        notification_index = self._existing_notification_count(notifications_path) + 1
        block = (
            f"## Notification {notification_index}\n"
            f"- Timestamp: {entry['timestamp']}\n"
            f"- Role: {entry['role']}\n"
            f"- Event: {entry['event']}\n"
            f"- Artifact: {entry['artifact_ref']}\n\n"
        )
        with notifications_path.open("a", encoding="utf-8") as notifications_file:
            notifications_file.write(block)

    @staticmethod
    def _existing_notification_count(path: Path) -> int:
        if not path.exists():
            return 0
        return path.read_text(encoding="utf-8").count("## Notification")
