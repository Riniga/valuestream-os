from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.agents.business_analyst_agent import BusinessAnalystAgent
from src.orchestration.kravstallning_flow import KravstallningFlow
from src.orchestration.run_context import RunContext


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="run_kravstallning",
        description="Run Kravstallning orchestration for a given run id.",
    )
    parser.add_argument(
        "--run-id",
        required=True,
        help="Run directory id under runs/<run-id>/.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate required inputs and run setup without executing orchestration.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help=argparse.SUPPRESS,
    )
    return parser.parse_args(argv)


def required_input_filenames() -> tuple[str, ...]:
    return (f"{BusinessAnalystAgent.required_input_id}.md",)


def validate_required_inputs(context: RunContext) -> list[str]:
    missing_files: list[str] = []
    for required_name in sorted(required_input_filenames()):
        if not (context.input_path / required_name).exists():
            missing_files.append(required_name)
    return missing_files


def run_cli(*, run_id: str, dry_run: bool, repo_root: Path) -> int:
    if not repo_root.exists():
        print(
            f"Repository root does not exist: {repo_root.as_posix()}",
            file=sys.stderr,
        )
        return 2

    context = RunContext.from_repo_root(run_id=run_id, repo_root=repo_root)
    context.initialize()

    missing_files = validate_required_inputs(context)
    if missing_files:
        print(
            f"Missing required input artifacts for run '{run_id}':",
            file=sys.stderr,
        )
        for name in missing_files:
            print(f"- input/{name}", file=sys.stderr)
        print(
            f"Expected input folder: {context.input_path.as_posix()}",
            file=sys.stderr,
        )
        return 2

    if dry_run:
        print(f"Dry-run OK for run-id '{run_id}'.")
        return 0

    flow = KravstallningFlow()
    try:
        result = flow.run(context)
    except ValueError as error:
        print(f"Kravstallning run failed: {error}", file=sys.stderr)
        return 2

    print(
        f"Run '{result.run_id}' finished with status '{result.status}' "
        f"after {len(result.executed_steps)} steps."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = args.repo_root.resolve()
    return run_cli(run_id=args.run_id, dry_run=args.dry_run, repo_root=repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
