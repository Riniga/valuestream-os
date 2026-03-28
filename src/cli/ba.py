"""
BA CLI

Usage:
    python -m src.cli.ba --run-id <run-id> info
    python -m src.cli.ba --run-id <run-id> run    [--dry-run]
    python -m src.cli.ba --run-id <run-id> update --artifact <filename> [--dry-run]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.capabilities.run_workspace import RunWorkspace
from src.orchestration.business_analyst_flow import BusinessAnalystFlow


def _find_repo_root() -> Path:
    candidate = Path(__file__).resolve().parent
    for _ in range(8):
        if (candidate / "docs").is_dir():
            return candidate
        candidate = candidate.parent
    return Path.cwd()


_W = 62  # output width


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="BA", description="Business Analyst Agent — ValueStream OS")
    parser.add_argument("--run-id", required=True, metavar="RUN_ID")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("info")

    run = sub.add_parser("run")
    run.add_argument("--dry-run", action="store_true")

    upd = sub.add_parser("update")
    upd.add_argument("--artifact", default="vision_och_malbild.md", metavar="FILENAME")
    upd.add_argument("--dry-run", action="store_true")

    return parser


def _status(ok: bool) -> str:
    return "[OK]" if ok else "[SAKNAS]"


def _rel(path, repo_root) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def _cmd_info(flow, repo_root) -> None:
    info = flow.get_info()

    print()
    print("═" * _W)
    print(f"  {info['role_name']}")
    print("═" * _W)

    agent_rel = _rel(info["agent_file"], repo_root)
    print(f"  Fil     : {agent_rel:<42} {_status(info['agent_file_ok'])}")

    purpose_lines = info["purpose"].split("\n")
    print(f"  Uppdrag : {purpose_lines[0]}")
    for line in purpose_lines[1:]:
        if line.strip():
            print(f"            {line.strip()}")

    print()
    print("  ARTIFAKTER  (R i RACI)")
    print("  " + "─" * (_W - 2))

    total_checks = 0
    ok_checks = 0

    for artifact in info["artifacts"]:
        print()
        print(f"  {artifact['name']}")

        sop_ok = artifact["sop_ok"]
        print(f"    SOP         : {artifact['sop_name']:<38} {_status(sop_ok)}")
        if sop_ok:
            print(f"                  {_rel(artifact['sop_path'], repo_root)}")
        total_checks += 1
        ok_checks += int(sop_ok)

        desc_ok = artifact["description_ok"]
        desc_label = artifact["description_path"].name if artifact["description_path"] else "—"
        print(f"    Beskrivning : {desc_label:<38} {_status(desc_ok)}")
        if desc_ok:
            print(f"                  {_rel(artifact['description_path'], repo_root)}")
        total_checks += 1
        ok_checks += int(desc_ok)

        tmpl_ok = artifact["template_ok"]
        tmpl_label = artifact["template_path"].name if artifact["template_path"] else "—"
        print(f"    Mall        : {tmpl_label:<38} {_status(tmpl_ok)}")
        if tmpl_ok:
            print(f"                  {_rel(artifact['template_path'], repo_root)}")
        total_checks += 1
        ok_checks += int(tmpl_ok)

        if artifact["input_files"]:
            print(f"    Input       : {', '.join(artifact['input_files'])}")
        if artifact["output_file"]:
            print(f"    Output      : {artifact['output_file']}")

    print()
    print("  " + "─" * (_W - 2))
    summary_color = "" if ok_checks == total_checks else "  *** PROBLEM DETECTED ***"
    print(f"  Stödfiler: {ok_checks}/{total_checks} OK{summary_color}")
    print()


def _cmd_run(flow, dry_run: bool = False) -> None:
    mode = " (dry-run)" if dry_run else ""
    print(f"\nKör alla artefakter{mode}...")
    print("─" * _W)

    results = flow.run_all(dry_run=dry_run)
    total = len(results)

    for i, r in enumerate(results, 1):
        prefix = f"  [{i:>{len(str(total))}}/{total}]"
        name = r["artifact"]
        if r["status"] in ("ok", "dry-run"):
            print(f"{prefix}  {name:<40}  OK")
        elif r["status"] == "skipped":
            missing = ", ".join(r["missing_inputs"])
            print(f"{prefix}  {name:<40}  SAKNAR INPUT: {missing}")
        else:
            print(f"{prefix}  {name:<40}  FEL: {r['reason']}")

    ok = sum(1 for r in results if r["status"] in ("ok", "dry-run"))
    skipped = sum(1 for r in results if r["status"] == "skipped")
    errors = sum(1 for r in results if r["status"] == "error")

    print("─" * _W)
    parts = [f"{ok} genererade"]
    if skipped:
        parts.append(f"{skipped} hoppades över (saknar input)")
    if errors:
        parts.append(f"{errors} fel")
    print(f"  {', '.join(parts)}")
    print()


def _cmd_update(flow, artifact_filename: str, dry_run: bool = False) -> None:
    print(f"\n{artifact_filename}")
    if dry_run:
        output_path = flow.generate_dry_run(artifact_filename)
        print(f"Dry-run OK — prompt sparad: {output_path}")
    else:
        output_path = flow.update(artifact_filename)
        print(f"Klar! Output: {output_path}")


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    repo_root = _find_repo_root()
    load_dotenv(repo_root / ".env")

    workspace = RunWorkspace(run_id=args.run_id, repo_root=repo_root)
    flow = BusinessAnalystFlow(workspace=workspace, repo_root=repo_root)

    try:
        if args.command == "info":
            _cmd_info(flow, repo_root)
        elif args.command == "run":
            _cmd_run(flow, dry_run=args.dry_run)
        elif args.command == "update":
            _cmd_update(flow, args.artifact, dry_run=args.dry_run)
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
