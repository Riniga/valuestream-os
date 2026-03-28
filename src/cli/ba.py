"""
BA CLI

Usage:
    python -m src.cli.ba --run-id <run-id> list
    python -m src.cli.ba --run-id <run-id> generate [--artifact <filename>] [--dry-run]
    python -m src.cli.ba --run-id <run-id> update   [--artifact <filename>] [--dry-run]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv


def _find_repo_root() -> Path:
    candidate = Path(__file__).resolve().parent
    for _ in range(8):
        if (candidate / "docs").is_dir():
            return candidate
        candidate = candidate.parent
    return Path.cwd()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="BA", description="Business Analyst Agent — ValueStream OS")
    parser.add_argument("--run-id", required=True, metavar="RUN_ID")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list")

    gen = sub.add_parser("generate")
    gen.add_argument("--artifact", default="vision_och_malbild.md", metavar="FILENAME")
    gen.add_argument("--dry-run", action="store_true")

    upd = sub.add_parser("update")
    upd.add_argument("--artifact", default="vision_och_malbild.md", metavar="FILENAME")
    upd.add_argument("--dry-run", action="store_true")

    return parser


def _cmd_list(flow) -> None:
    from src.agents.business_analyst.artifact_registry import ARTIFACT_REGISTRY

    responsibilities = flow.list_responsibilities()

    print("\nBusiness Analyst — ansvariga artefakter (R i RACI)")
    print("=" * 60)

    seen = set()
    for entry in responsibilities:
        key = (entry["sop"], entry["artifact"])
        if key in seen:
            continue
        seen.add(key)
        status = "[OK]" if entry["registered"] else "[ej registrerad]"
        print(f"\n  SOP      : {entry['sop']}")
        print(f"  Artefakt : {entry['artifact']}  {status}")
        if entry["registered"]:
            print(f"  Fil      : output/{entry['output_filename']}")
            if entry["input_required"]:
                print(f"  Kräver   : {', '.join(entry['input_required'])}")

    unique_keys = {(e["sop"], e["artifact"]) for e in responsibilities}
    registered_count = sum(
        1 for key in unique_keys
        if any(e["registered"] for e in responsibilities if (e["sop"], e["artifact"]) == key)
    )
    print(f"\nRegistrerade och körbara: {registered_count} / {len(unique_keys)}")


def _cmd_generate(flow, artifact_filename: str, dry_run: bool = False) -> None:
    print(f"\nGenererar: {artifact_filename}")
    if dry_run:
        output_path = flow.generate_dry_run(artifact_filename)
        print(f"\nDry-run OK — prompt sparad: {output_path}")
    else:
        print("Laddar framework-kontext...")
        print("Bygger prompt...")
        print("Anropar LLM...")
        output_path = flow.generate(artifact_filename)
        print(f"\nKlar! Output sparad: {output_path}")


def _cmd_update(flow, artifact_filename: str, dry_run: bool = False) -> None:
    print(f"\nUppdaterar: {artifact_filename}")
    if dry_run:
        output_path = flow.generate_dry_run(artifact_filename)
        print(f"\nDry-run OK — prompt sparad: {output_path}")
    else:
        output_path = flow.update(artifact_filename)
        print(f"\nKlar! Output uppdaterad: {output_path}")


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    repo_root = _find_repo_root()
    load_dotenv(repo_root / ".env")

    from src.capabilities.run_workspace import RunWorkspace
    from src.orchestration.business_analyst_flow import BusinessAnalystFlow

    workspace = RunWorkspace(run_id=args.run_id, repo_root=repo_root)
    flow = BusinessAnalystFlow(workspace=workspace, repo_root=repo_root)

    try:
        if args.command == "list":
            _cmd_list(flow)
        elif args.command == "generate":
            _cmd_generate(flow, args.artifact, dry_run=getattr(args, "dry_run", False))
        elif args.command == "update":
            _cmd_update(flow, args.artifact, dry_run=getattr(args, "dry_run", False))
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
        if type(exc).__name__ in ("RateLimitError", "AuthenticationError"):
            print(f"\nLLM-fel: {exc}", file=sys.stderr)
            return 1
        raise

    return 0


if __name__ == "__main__":
    sys.exit(main())
