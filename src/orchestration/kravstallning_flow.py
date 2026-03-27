from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from src.agents.business_analyst_agent import BusinessAnalystAgent
from src.agents.product_owner_reviewer import ProductOwnerReviewer, ReviewDecision
from src.agents.ux_agent import UXAgent
from src.orchestration.run_context import RunContext


@dataclass(frozen=True)
class KravstallningFlowResult:
    run_id: str
    status: str
    executed_steps: tuple[str, ...]
    produced_artifacts: tuple[str, ...]
    review_decisions: tuple[ReviewDecision, ...]


class KravstallningFlow:
    """Executes deterministic BA -> UX -> PO orchestration."""

    def __init__(
        self,
        *,
        business_analyst: BusinessAnalystAgent | None = None,
        ux_agent: UXAgent | None = None,
        product_owner: ProductOwnerReviewer | None = None,
    ) -> None:
        self._business_analyst = business_analyst or BusinessAnalystAgent()
        self._ux_agent = ux_agent or UXAgent()
        self._product_owner = product_owner or ProductOwnerReviewer()

    def run(self, context: RunContext) -> KravstallningFlowResult:
        context.initialize()

        executed_steps: list[str] = []
        produced_artifacts: list[str] = []
        review_decisions: list[ReviewDecision] = []

        ba_input_path = self._require_artifact(
            context.input_path / "overgripande_behov.md",
            artifact_id=self._business_analyst.required_input_id,
        )
        ba_output = self._business_analyst.produce(
            input_artifacts={
                self._business_analyst.required_input_id: ba_input_path
            },
            context=context,
        )
        context.record_lineage(
            artifact_id=ba_output.artifact_id,
            artifact_path=ba_output.artifact_path,
            source_files=(ba_input_path,),
            produced_by=ba_output.produced_by,
        )
        executed_steps.append("business_analyst_produce")
        produced_artifacts.append(ba_output.artifact_id)
        self._append_step_log(
            context=context,
            step_name="business_analyst_produce",
            detail=f"Produced {ba_output.artifact_id} at {self._to_run_relative(context, ba_output.artifact_path)}.",
        )

        ux_output = self._ux_agent.produce(
            input_artifacts={self._ux_agent.required_input_id: ba_output.artifact_path},
            context=context,
        )
        context.record_lineage(
            artifact_id=ux_output.artifact_id,
            artifact_path=ux_output.artifact_path,
            source_files=(ba_output.artifact_path,),
            produced_by=ux_output.produced_by,
        )
        executed_steps.append("ux_produce")
        produced_artifacts.append(ux_output.artifact_id)
        self._append_step_log(
            context=context,
            step_name="ux_produce",
            detail=f"Produced {ux_output.artifact_id} at {self._to_run_relative(context, ux_output.artifact_path)}.",
        )

        for artifact_output in (ba_output, ux_output):
            decision = self._product_owner.review(artifact_output, context)
            review_decisions.append(decision)
            executed_steps.append(f"product_owner_review:{artifact_output.artifact_id}")
            self._append_step_log(
                context=context,
                step_name=f"product_owner_review:{artifact_output.artifact_id}",
                detail=f"Decision={decision.review_status}.",
            )
            if decision.review_status != "approved":
                self._append_step_log(
                    context=context,
                    step_name="flow_stopped",
                    detail="Stopped after PO requested changes.",
                )
                break

        state = context.load_state()
        return KravstallningFlowResult(
            run_id=context.run_id,
            status=str(state.get("status", "initialized")),
            executed_steps=tuple(executed_steps),
            produced_artifacts=tuple(produced_artifacts),
            review_decisions=tuple(review_decisions),
        )

    @staticmethod
    def _require_artifact(path: Path, *, artifact_id: str) -> Path:
        if path.exists():
            return path
        raise ValueError(
            "Missing required input artifact "
            f"'{artifact_id}'. Expected file at '{path.as_posix()}'."
        )

    @staticmethod
    def _to_run_relative(context: RunContext, artifact_path: Path) -> str:
        try:
            return artifact_path.relative_to(context.run_path).as_posix()
        except ValueError:
            return artifact_path.as_posix()

    @staticmethod
    def _append_step_log(*, context: RunContext, step_name: str, detail: str) -> None:
        step_log_path = context.logs_path / "step_log.md"
        existing_log = ""
        if step_log_path.exists():
            existing_log = step_log_path.read_text(encoding="utf-8")
            # Idempotency guard: do not duplicate the same step name across reruns.
            if re.search(
                rf"^- Name: {re.escape(step_name)}$",
                existing_log,
                flags=re.MULTILINE,
            ):
                return

        step_index = existing_log.count("## Step ") + 1 if existing_log else 1

        block = (
            f"## Step {step_index}\n"
            f"- Name: {step_name}\n"
            f"- Detail: {detail}\n\n"
        )
        with step_log_path.open("a", encoding="utf-8") as step_log:
            step_log.write(block)
