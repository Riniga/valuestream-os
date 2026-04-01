"""
ValueStream OS — Unified Orchestrator CLI

Usage:
    python -m src.cli.run --run-id <run-id> agents
    python -m src.cli.run --run-id <run-id> run    [--dry-run]
    python -m src.cli.run --run-id <run-id> status
    python -m src.cli.run --run-id <run-id> flow
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.capabilities.run_workspace import RunWorkspace
from src.framework.context_loader import AgentContextLoader
from src.framework.models import StepResult, StepStatus
from src.framework.repo_layout import find_repository_root, get_framework_root
from src.framework.stores import (
    ApprovalStore,
    ArtifactStateStore,
    ConsultationStore,
    InformedRoleBriefStore,
    RunStateStore,
)
from src.orchestration.agent_registry import AGENT_DEFINITIONS
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
    for agent_id, agent_def in AGENT_DEFINITIONS.items():
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
        print(f"    Agent      : {step.agent_id}")
        print(f"    SOP        : {step.sop_filename}")
        print(f"    Artefakt   : {step.artifact_name}")
        print(f"    Output     : {step.output_filename}")
        print(f"    Input      : {', '.join(step.input_filenames)}")
        if step.consult_agent_ids:
            print(f"    C-roller   : {', '.join(step.consult_agent_ids)}")
        if step.approver_agent_id:
            print(f"    A-roll     : {step.approver_agent_id}")
        if step.informed_agent_ids:
            print(f"    I-roller   : {', '.join(step.informed_agent_ids)}")
        if step.use_raci_workflow:
            print("    RACI-flöde : draft -> consultation -> revision -> approval -> informing")
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
    skipped = sum(1 for r in results if r.status == StepStatus.skipped)
    errors = sum(1 for r in results if r.status == StepStatus.failed)

    print("─" * CONSOLE_WIDTH)
    parts = [f"{ok} klara"]
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

    run_state = run_state_store.load()
    artifact_state = artifact_state_store.load()
    approval_decisions = approval_store.load()
    consultation_responses = consultation_store.load_responses()
    informed_briefs = brief_store.load()

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
