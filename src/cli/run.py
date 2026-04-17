"""
ValueStream OS — Unified Orchestrator CLI

Usage:
    python -m src.cli.run --run-id <run-id> agents
    python -m src.cli.run --run-id <run-id> run    [--dry-run]
    python -m src.cli.run --run-id <run-id> status
    python -m src.cli.run --run-id <run-id> flow
    python -m src.cli.run --run-id <run-id> human-tasks
    python -m src.cli.run --run-id <run-id> complete-human-task <task-id> [options]
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.capabilities.run_workspace import RunWorkspace
from src.framework.context_loader import AgentContextLoader
from src.framework.models import HumanTaskStatus, StepResult, StepStatus
from src.framework.repo_layout import find_repository_root, get_framework_root
from src.framework.stores import (
    ApprovalStore,
    ArtifactStateStore,
    ConsultationStore,
    HumanTaskStore,
    InformedRoleBriefStore,
    RunStateStore,
)
from src.orchestration.agent_registry import load_agent_definitions
from src.orchestration.orchestrator import Orchestrator
from src.orchestration.process_loader import DEFAULT_PROCESS_FILE, ProcessFlowLoader


CONSOLE_WIDTH = 64


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run",
        description="ValueStream OS — Agent Orchestration CLI",
    )
    parser.add_argument("--run-id", required=True, metavar="RUN_ID")
    parser.add_argument(
        "--process",
        default=DEFAULT_PROCESS_FILE,
        metavar="PROCESS_FILE",
        help=f"Process file under the configured framework (default: {DEFAULT_PROCESS_FILE})",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("agents", help="List registered agents and their SOPs")
    sub.add_parser("flow", help="Show process-driven flow steps and artifact chain")

    run_cmd = sub.add_parser("run", help="Run the full multi-agent flow")
    run_cmd.add_argument("--dry-run", action="store_true", help="Write prompts instead of calling LLM")

    sub.add_parser("status", help="Show current run state and artifact status")
    sub.add_parser("human-tasks", help="List human tasks for the run")

    complete_cmd = sub.add_parser("complete-human-task", help="Complete a pending human task")
    complete_cmd.add_argument("task_id", metavar="TASK_ID")
    complete_cmd.add_argument(
        "--decision",
        choices=["approved", "approved_with_notes", "rejected"],
        help="Decision for approval tasks",
    )
    complete_cmd.add_argument("--summary", default="", help="Short summary for the human response")
    complete_cmd.add_argument("--rationale", default="", help="Detailed rationale for approval tasks")
    complete_cmd.add_argument(
        "--changes-requested",
        action="append",
        default=[],
        help="Requested changes for approval tasks (repeatable)",
    )
    complete_cmd.add_argument(
        "--response-text",
        default="",
        help="Response text for consultation tasks",
    )
    complete_cmd.add_argument(
        "--artifact-content",
        default="",
        help="Artifact content for human-responsible tasks",
    )
    complete_cmd.add_argument(
        "--artifact-file",
        default="",
        help="Path to an artifact file for human-responsible tasks",
    )
    complete_cmd.add_argument(
        "--attachment-path",
        action="append",
        default=[],
        help="Optional attachment path to store on the human task (repeatable)",
    )

    return parser


# ---------------------------------------------------------------------------
# Command: agents
# ---------------------------------------------------------------------------

def _cmd_agents(repo_root: Path) -> None:
    print()
    print("═" * CONSOLE_WIDTH)
    print("  Registrerade agenter")
    print("═" * CONSOLE_WIDTH)
    framework_root = get_framework_root(repo_root)
    for agent_id, agent_def in load_agent_definitions(repo_root).items():
        loader = AgentContextLoader(
            repo_root=repo_root,
            agent_file=agent_def.agent_file,
            raci_role_id=agent_def.raci_role_id,
        )
        agent_path = framework_root / "agents" / agent_def.agent_file
        ok = "[OK]" if agent_path.exists() else "[SAKNAS]"
        rel_path = f"agents/{agent_def.agent_file}"
        print()
        print(f"  {agent_id}")
        print(f"    Fil        : {rel_path:<30} {ok}")
        print(f"    RACI-roll  : {agent_def.raci_role_id}")
        print(f"    Aktörstyp  : {agent_def.actor_kind.value}")
        try:
            sops = loader.load_sops_for_role()
            print(f"    SOPs       : {len(sops)} med R-ansvar")
        except Exception:  # noqa: BLE001
            print("    SOPs       : [kunde inte laddas]")
    print()


# ---------------------------------------------------------------------------
# Command: flow
# ---------------------------------------------------------------------------

def _cmd_flow(repo_root: Path, process_file: str) -> None:
    process_flow = ProcessFlowLoader(repo_root).load(process_file)
    print()
    print("═" * CONSOLE_WIDTH)
    print(f"  Flöde: {process_flow.flow_id}")
    print("═" * CONSOLE_WIDTH)
    print(f"  Källa: processes/{process_flow.process_file}")
    print()
    for i, step in enumerate(process_flow.steps, 1):
        print()
        title = step.delprocess_title or step.step_id
        print(f"  Steg {i}: {title}")
        print(f"    Agent      : {step.agent_id} ({step.agent_actor_kind.value})")
        print(f"    SOP        : {step.sop_filename}")
        print(f"    Artefakt   : {step.artifact_name}")
        print(f"    Output     : {step.output_filename}")
        print(f"    Input      : {', '.join(step.input_filenames)}")
        if step.consult_agent_ids:
            consult = ", ".join(
                f"{agent_id} ({step.consult_actor_kinds.get(agent_id).value})"
                for agent_id in step.consult_agent_ids
            )
            print(f"    C-roller   : {consult}")
        if step.approver_agent_id:
            actor_kind = step.approver_actor_kind.value if step.approver_actor_kind else "unknown"
            print(f"    A-roll     : {step.approver_agent_id} ({actor_kind})")
        if step.informed_agent_ids:
            informed = ", ".join(
                f"{agent_id} ({step.informed_actor_kinds.get(agent_id).value})"
                for agent_id in step.informed_agent_ids
            )
            print(f"    I-roller   : {informed}")
        if step.use_raci_workflow:
            print("    RACI-flöde : draft -> consultation -> revision -> approval? -> informing?")
    print()


# ---------------------------------------------------------------------------
# Command: run
# ---------------------------------------------------------------------------

async def _cmd_run_async(workspace: RunWorkspace, repo_root: Path, dry_run: bool, process_file: str) -> None:
    process_flow = ProcessFlowLoader(repo_root).load(process_file)
    total = len(process_flow.steps)
    mode = " (dry-run)" if dry_run else ""
    print(f"\nKör flöde: {process_flow.flow_id}{mode}  ({total} steg)")
    print("─" * CONSOLE_WIDTH)

    orchestrator = Orchestrator(workspace=workspace, repo_root=repo_root, process_flow=process_flow)

    # Use __anext__() so we can print "pågår..." before awaiting each step.
    # run_stream_async yields results in the same order as process_flow.steps.
    results: list[StepResult] = []
    stream = orchestrator.run_stream_async(dry_run=dry_run)
    for i, step in enumerate(process_flow.steps, 1):
        title = step.delprocess_title or step.step_id
        name = f"{title:<30} ({step.artifact_name})"
        print(f"  [{i}/{total}]  {name}  pågår...", flush=True)
        try:
            r = await stream.__anext__()
        except StopAsyncIteration:
            break
        results.append(r)
        if r.status == StepStatus.completed:
            rel = str(r.output_path.relative_to(repo_root)) if r.output_path else ""
            print(f"           {'':30}  OK  →  {rel}")
        elif r.status == StepStatus.paused:
            task_path = str(r.human_task_path.relative_to(repo_root)) if r.human_task_path else ""
            print(f"           {'':30}  PAUSAD  →  {task_path}")
            break
        elif r.status == StepStatus.skipped:
            print(f"           {'':30}  HOPPAS ÖVER  —  {r.skipped_reason}")
        else:
            print(f"           {'':30}  FEL  —  {r.error}")
            break
        if r.approval_decision:
            print(f"           {'':30}  Approval  : {r.approval_decision}")

    # Advance the async generator one final time so it can persist run_finished
    # and the terminal status sees the completed run state.
    try:
        await stream.__anext__()
    except StopAsyncIteration:
        pass

    ok = sum(1 for r in results if r.status == StepStatus.completed)
    paused = sum(1 for r in results if r.status == StepStatus.paused)
    skipped = sum(1 for r in results if r.status == StepStatus.skipped)
    errors = sum(1 for r in results if r.status == StepStatus.failed)

    print("─" * CONSOLE_WIDTH)
    parts = [f"{ok} klara"]
    if paused:
        parts.append(f"{paused} pauserade")
    if skipped:
        parts.append(f"{skipped} hoppade över")
    if errors:
        parts.append(f"{errors} fel")
    print(f"  {', '.join(parts)}")
    print()


# ---------------------------------------------------------------------------
# Command: status
# ---------------------------------------------------------------------------

def _cmd_status(workspace: RunWorkspace) -> None:
    run_dir = workspace.run_dir
    run_state_store = RunStateStore(run_dir)
    artifact_state_store = ArtifactStateStore(run_dir)
    consultation_store = ConsultationStore(run_dir)
    approval_store = ApprovalStore(run_dir)
    brief_store = InformedRoleBriefStore(run_dir)
    human_task_store = HumanTaskStore(run_dir)

    run_state = run_state_store.load()
    artifact_state = artifact_state_store.load()
    approval_decisions = approval_store.load()
    consultation_responses = consultation_store.load_responses()
    informed_briefs = brief_store.load()
    human_tasks = human_task_store.load_all()

    print()
    print("═" * CONSOLE_WIDTH)
    print(f"  Status: run {workspace.run_id}")
    print("═" * CONSOLE_WIDTH)

    if run_state is None:
        print("\n  Ingen körning hittades för detta run-id.")
        print()
        return

    print(f"\n  Flöde   : {run_state.flow_id}")
    if run_state.process_file:
        print(f"  Process : {run_state.process_file}")
    print(f"  Status  : {run_state.status.value.upper()}")
    if run_state.current_step_id:
        print(f"  Aktivt  : {run_state.current_step_id}")
    if run_state.current_phase:
        print(f"  Fas     : {run_state.current_phase}")

    print("\n  Steg:")
    for step_id, status_val in run_state.step_statuses.items():
        print(f"    {step_id:<22} {status_val}")

    if artifact_state and artifact_state.artifacts:
        print("\n  Artefakter:")
        for filename, rec in artifact_state.artifacts.items():
            print(f"    {filename:<35} {rec.status.value}")
            if rec.consult_agent_ids:
                print(f"      C: {', '.join(rec.consult_agent_ids)}")
            if rec.approver_agent_id:
                print(f"      A: {rec.approver_agent_id}")
            if rec.informed_agent_ids:
                print(f"      I: {', '.join(rec.informed_agent_ids)}")
            if rec.latest_phase:
                print(f"      Senaste fas: {rec.latest_phase}")
            if rec.approval_decision:
                print(f"      Beslut: {rec.approval_decision}")
            if rec.pending_human_task_id:
                print(f"      Väntar på människa: {rec.pending_human_task_id}")
    else:
        print("\n  Artefakter: inga registrerade ännu")

    if consultation_responses:
        print("\n  Konsultationssvar:")
        for response in consultation_responses:
            print(f"    {response.step_id:<22} {response.consultant_agent_id:<20} {response.summary}")

    if approval_decisions:
        print("\n  Godkännanden:")
        for decision in approval_decisions:
            print(f"    {decision.step_id:<22} {decision.decision:<20} {decision.summary}")

    if informed_briefs:
        print("\n  Informationsbriefs:")
        for brief in informed_briefs:
            print(f"    {brief.step_id:<22} {brief.role_agent_id:<20} {brief.relevance}")

    if human_tasks:
        print("\n  Mänskliga uppgifter:")
        for task in human_tasks:
            print(f"    {task.task_id:<36} {task.status.value:<12} {task.phase:<16} {task.role_name}")

    print()


# ---------------------------------------------------------------------------
# Command: human-tasks
# ---------------------------------------------------------------------------

def _cmd_human_tasks(workspace: RunWorkspace) -> None:
    store = HumanTaskStore(workspace.run_dir)
    tasks = store.load_all()

    print()
    print("═" * CONSOLE_WIDTH)
    print(f"  Mänskliga uppgifter: run {workspace.run_id}")
    print("═" * CONSOLE_WIDTH)

    if not tasks:
        print("\n  Inga mänskliga uppgifter hittades.\n")
        return

    for task in tasks:
        print()
        print(f"  {task.task_id}")
        print(f"    Status     : {task.status.value}")
        print(f"    Fas        : {task.phase}")
        if task.task_kind:
            print(f"    Typ        : {task.task_kind}")
        if task.action_required:
            print(f"    Gör nu     : {task.action_required}")
        print(f"    Roll       : {task.role_name}")
        print(f"    Artefakt   : {task.artifact_name}")
        print(f"    Fil        : human_tasks/{task.task_id}.json")
        suggested_path = task.request_payload.get("suggested_artifact_path")
        if isinstance(suggested_path, str) and suggested_path:
            print(f"    Föreslagen fil : {suggested_path}")
        if task.next_step_hint:
            print(f"    Nästa steg : {task.next_step_hint}")
        if task.completion_summary:
            print(f"    Kommentar  : {task.completion_summary}")
    print()


def _cmd_complete_human_task(workspace: RunWorkspace, args: argparse.Namespace) -> None:
    store = HumanTaskStore(workspace.run_dir)
    task = store.load(args.task_id)
    if task is None:
        raise FileNotFoundError(f"Mänsklig uppgift hittades inte: {args.task_id}")

    response_payload = dict(task.response_payload)
    if args.decision:
        response_payload["decision"] = args.decision
    if args.summary:
        response_payload["summary"] = args.summary
    if args.rationale:
        response_payload["rationale"] = args.rationale
    if args.changes_requested:
        response_payload["changes_requested"] = args.changes_requested
    if args.response_text:
        response_payload["response_text"] = args.response_text
    if args.artifact_content:
        response_payload["artifact_content"] = args.artifact_content
    if args.artifact_file:
        response_payload["artifact_path"] = args.artifact_file
    if args.attachment_path:
        response_payload["attachment_paths"] = args.attachment_path

    task.response_payload = response_payload
    task.status = HumanTaskStatus.completed
    task.completion_summary = args.summary or "Slutförd via CLI."
    store.save(task)

    print()
    print(f"Human task '{task.task_id}' markerades som completed.")
    print(f"Fortsätt körningen med: python -m src.cli.run --run-id {workspace.run_id} run")
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def _main_async(argv: list[str] | None = None) -> int:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8")

    parser = _build_parser()
    args = parser.parse_args(argv)

    repo_root = find_repository_root(Path(__file__).resolve().parent)
    load_dotenv(repo_root / ".env")

    workspace = RunWorkspace(run_id=args.run_id, repo_root=repo_root)

    try:
        if args.command == "agents":
            _cmd_agents(repo_root)
        elif args.command == "flow":
            _cmd_flow(repo_root, args.process)
        elif args.command == "run":
            await _cmd_run_async(workspace, repo_root, dry_run=args.dry_run, process_file=args.process)
        elif args.command == "status":
            _cmd_status(workspace)
        elif args.command == "human-tasks":
            _cmd_human_tasks(workspace)
        elif args.command == "complete-human-task":
            _cmd_complete_human_task(workspace, args)
    except FileNotFoundError as exc:
        print(f"\nFel: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"\nFel: {exc}", file=sys.stderr)
        return 1
    except EnvironmentError as exc:
        print(f"\nMiljöfel: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        exc_type = type(exc).__name__
        if "RateLimit" in exc_type or "Authentication" in exc_type or "APIError" in exc_type:
            print(f"\nLLM-fel ({exc_type}): {exc}", file=sys.stderr)
            return 1
        raise

    return 0


def main(argv: list[str] | None = None) -> int:
    return asyncio.run(_main_async(argv))


if __name__ == "__main__":
    sys.exit(main())
