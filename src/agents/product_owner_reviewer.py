from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from src.agents.agent_contract import AgentArtifactOutput
from src.orchestration.run_context import RunContext
from src.roles.interaction_bus import InteractionBus


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class ReviewDecision:
    artifact_id: str
    review_status: str
    missing_headings: tuple[str, ...]
    can_publish: bool


class ProductOwnerReviewer:
    """Evaluates artifacts and writes review status into run state."""

    reviewer_name = "product_owner"
    inform_roles = (
        "business_analyst",
        "solution_architect",
        "project_manager",
        "developers",
    )

    def __init__(self, interaction_bus: InteractionBus | None = None) -> None:
        self._interaction_bus = interaction_bus or InteractionBus()

    def review(self, artifact_output: AgentArtifactOutput, context: RunContext) -> ReviewDecision:
        artifact_path = artifact_output.artifact_path
        content = artifact_path.read_text(encoding="utf-8") if artifact_path.exists() else ""
        missing_headings = tuple(
            heading
            for heading in artifact_output.required_headings
            if heading not in content
        )
        review_status = "changes_requested" if missing_headings else "approved"

        state = context.load_state()
        artifact_reviews = dict(state.get("artifact_reviews", {}))
        artifact_reviews[artifact_output.artifact_id] = {
            "artifact_id": artifact_output.artifact_id,
            "artifact_path": self._to_run_relative_path(artifact_path=artifact_path, context=context),
            "produced_by": artifact_output.produced_by,
            "reviewed_by": self.reviewer_name,
            "review_status": review_status,
            "missing_headings": list(missing_headings),
            "reviewed_at": _utc_timestamp(),
        }

        state["artifact_reviews"] = artifact_reviews
        state["status"] = self._compute_run_status(artifact_reviews=artifact_reviews)

        if review_status == "approved":
            published_path = self._publish_artifact(
                artifact_path=artifact_path,
                context=context,
            )
            artifact_reviews[artifact_output.artifact_id]["published_artifact_path"] = (
                self._to_run_relative_path(artifact_path=published_path, context=context)
            )
            artifact_reviews[artifact_output.artifact_id]["published_at"] = _utc_timestamp()
            self._inform_roles_after_publication(
                artifact_ref=self._to_run_relative_path(
                    artifact_path=published_path,
                    context=context,
                ),
                context=context,
            )

        context.update_lineage_review_status(
            artifact_id=artifact_output.artifact_id,
            review_status=review_status,
        )
        context.save_state(state)

        return ReviewDecision(
            artifact_id=artifact_output.artifact_id,
            review_status=review_status,
            missing_headings=missing_headings,
            can_publish=review_status == "approved",
        )

    @staticmethod
    def _compute_run_status(*, artifact_reviews: dict[str, dict[str, object]]) -> str:
        if not artifact_reviews:
            return "initialized"

        statuses = [entry.get("review_status") for entry in artifact_reviews.values()]
        if any(status == "changes_requested" for status in statuses):
            return "changes_requested"
        if all(status == "approved" for status in statuses):
            return "approved"
        return "in_review"

    @staticmethod
    def _to_run_relative_path(*, artifact_path: Path, context: RunContext) -> str:
        try:
            return artifact_path.relative_to(context.run_path).as_posix()
        except ValueError:
            return artifact_path.as_posix()

    @staticmethod
    def _publish_artifact(*, artifact_path: Path, context: RunContext) -> Path:
        published_path = context.output_path / artifact_path.name
        shutil.copy2(artifact_path, published_path)
        return published_path

    def _inform_roles_after_publication(self, *, artifact_ref: str, context: RunContext) -> None:
        event = "artifact_approved_and_published"
        for role in self.inform_roles:
            if self._notification_exists(
                role=role,
                event=event,
                artifact_ref=artifact_ref,
                context=context,
            ):
                continue
            self._interaction_bus.inform(
                role=role,
                event=event,
                artifact_ref=artifact_ref,
                context=context,
            )

    @staticmethod
    def _notification_exists(
        *,
        role: str,
        event: str,
        artifact_ref: str,
        context: RunContext,
    ) -> bool:
        notifications_path = context.logs_path / "notifications.md"
        if not notifications_path.exists():
            return False
        content = notifications_path.read_text(encoding="utf-8")
        for block in content.split("## Notification "):
            if (
                f"- Role: {role}" in block
                and f"- Event: {event}" in block
                and f"- Artifact: {artifact_ref}" in block
            ):
                return True
        return False
