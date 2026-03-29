#!/usr/bin/env python3
"""
Developer maintenance script — SOP convention discovery.

Scans docs/SOP/ and reports which SOPs follow the expected structure
(sections, RACI, inputs/outputs). Run manually during framework maintenance,
not as part of the agent orchestration pipeline.

Output is written to docs/SOP/sop-conventions-discovery.md and a CSV file.
Running this script intentionally mutates docs/ — it is a documentation
maintenance tool, not a production execution step.
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SOP_DIR = ROOT / "docs" / "SOP"

RE_SOP_TITLE = re.compile(r"^#\s*SOP\s*([0-9]+)\s*:\s*(.+)$", re.IGNORECASE)
RE_SECTION = re.compile(r"^##\s*([0-9]+)\.\s*(.+)$")
RE_RACI_LINE = re.compile(r"^-\s*([RACI]):\s*(.+)$", re.IGNORECASE)
RE_BULLET_ITEM = re.compile(r"^-\s*(.+)$")

EXPECTED_SECTIONS = ["1. Syfte", "2. Kontext", "3. Input", "4. Output", "5. RACI", "6. Arbetssteg"]


def split_raci_roles(role_text: str) -> list:
    """Split a RACI role field on commas; each trimmed non-empty part is one role."""
    return [p.strip() for p in role_text.split(",") if p.strip()]


def parse_sop_file(path: Path) -> dict:
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    sop_meta = {
        "path": str(path.relative_to(ROOT)),
        "sop_id": None,
        "sop_name": None,
        "sections": [],
        "process_step": None,
        "delprocess": None,
        "input": [],
        "output": [],
        "raci": {"R": [], "A": [], "C": [], "I": []},
        "unexpected_raci": [],
    }

    current_section = None
    current_section_title = None

    for line in lines:
        # SOP header
        m = RE_SOP_TITLE.match(line)
        if m:
            sop_meta["title_line"] = line.strip()
            sop_meta["sop_id"] = m.group(1).strip()
            sop_meta["sop_name"] = m.group(2).strip()
            continue

        # numbered section heading
        m = RE_SECTION.match(line)
        if m:
            current_section = m.group(1).strip()
            section_title = m.group(2).strip()
            sop_meta["sections"].append(f"{current_section}. {section_title}")
            continue

        # capture bullet list items inside Input/output/raci and Context
        if current_section in ("2", "3", "4", "5"):
            m = RE_BULLET_ITEM.match(line)
            if m:
                item = m.group(1).strip()
                if current_section == "2":
                    if item.lower().startswith("processteg:"):
                        sop_meta["process_step"] = item.split(":", 1)[1].strip()
                    elif item.lower().startswith("delprocess:"):
                        sop_meta["delprocess"] = item.split(":", 1)[1].strip()
                elif current_section == "3":
                    sop_meta["input"].append(item)
                elif current_section == "4":
                    sop_meta["output"].append(item)
                elif current_section == "5":
                    m2 = RE_RACI_LINE.match(line)
                    if m2:
                        cat = m2.group(1).upper()
                        role = m2.group(2).strip()
                        if cat in sop_meta["raci"]:
                            for r in split_raci_roles(role):
                                sop_meta["raci"][cat].append(r)
                        else:
                            sop_meta["unexpected_raci"].append((line.strip(), path.as_posix()))
    return sop_meta


def discover_sop_conventions() -> dict:
    sop_files = sorted(SOP_DIR.rglob("*.md"))
    all_meta = []
    section_freq = {}
    raci_roles = {"R": set(), "A": set(), "C": set(), "I": set()}
    artifacts_input = set()
    artifacts_output = set()

    for path in sop_files:
        meta = parse_sop_file(path)
        all_meta.append(meta)

        for section in meta["sections"]:
            section_freq[section] = section_freq.get(section, 0) + 1

        for cat in raci_roles.keys():
            for role in meta["raci"][cat]:
                raci_roles[cat].add(role)

        artifacts_input.update(meta["input"])
        artifacts_output.update(meta["output"])

    return {
        "sop_count": len(all_meta),
        "section_freq": section_freq,
        "raci_roles": {k: sorted(v) for k, v in raci_roles.items()},
        "artifacts_input": sorted(artifacts_input),
        "artifacts_output": sorted(artifacts_output),
        "sops": all_meta,
    }


def format_as_markdown(discovery: dict) -> str:
    lines = ["# SOP Conventions Discovery", "", f"Found {discovery['sop_count']} SOP file(s).", ""]
    lines.append("## Section frequency")
    for sec, freq in sorted(discovery["section_freq"].items()):
        lines.append(f"- {sec}: {freq}")
    lines.append("")

    lines.append("## RACI roles")
    for cat, roles in discovery["raci_roles"].items():
        lines.append(f"- {cat}: {', '.join(roles) if roles else '(none)'}")
    lines.append("")

    lines.append("## Artifacts (output)")
    for a in discovery["artifacts_output"]:
        lines.append(f"- {a}")
    lines.append("")

    lines.append("## Artifacts (input)")
    for a in discovery["artifacts_input"]:
        lines.append(f"- {a}")
    lines.append("")

    lines.append("## SOP files with missing expected sections")
    for m in discovery["sops"]:
        missing = [s for s in EXPECTED_SECTIONS if s not in m["sections"]]
        if missing:
            lines.append(f"- {m['path']}: missing {', '.join(missing)}")
    lines.append("")

    lines.append("## SOP samples")
    for m in discovery["sops"]:
        lines.append(f"### {m['path']}")
        lines.append(f"- title: {m.get('sop_name')}")
        lines.append(f"- sections: {', '.join(m['sections'])}")
        lines.append(f"- input: {', '.join(m['input']) or '(none)'}")
        lines.append(f"- output: {', '.join(m['output']) or '(none)'}")
        lines.append(f"- raci: {', '.join([f'{k}={len(v)}' for k, v in m['raci'].items()])}")
        if m["unexpected_raci"]:
            lines.append(f"- unexpected RACI lines: {m['unexpected_raci']}")
        lines.append("")

    return "\n".join(lines)


def write_roles_csv(sops, dest_dir):
    path = dest_dir / "Roles.csv"
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Role", "SOP", "Type of RACI"])
        for sop in sops:
            sop_ref = sop.get("path")
            for raci_type, roles in sop["raci"].items():
                for role in roles:
                    writer.writerow([role, sop_ref, raci_type])
    print(f"Written roles CSV to {path}")


def write_artifacts_csv(sops, dest_dir):
    path = dest_dir / "Artifacts.csv"
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Artifact", "SOP", "Input or output", "Responsible"])
        for sop in sops:
            sop_ref = sop.get("path")
            for artifact in sop.get("input", []):
                writer.writerow([artifact, sop_ref, "input", ""])
            for artifact in sop.get("output", []):
                responsible = ", ".join(sop["raci"]["R"])
                writer.writerow([artifact, sop_ref, "output", responsible])
    print(f"Written artifacts CSV to {path}")


def write_sop_txt(sops, dest_dir):
    path = dest_dir / "SOP.csv"
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["SOP", "Delprocess", "processsteg"])
        for sop in sops:
            writer.writerow([
                sop.get("path"),
                sop.get("delprocess") or "",
                sop.get("process_step") or "",
            ])
    print(f"Written SOP CSV to {path}")


def main() -> int:
    discovery = discover_sop_conventions()
    ctx_dir = ROOT / "docs"
    ctx_dir.mkdir(parents=True, exist_ok=True)

    # legacy report
    out = format_as_markdown(discovery)
    report_path = ctx_dir / "SOP" / "sop-conventions-discovery.md"
    report_path.write_text(out, encoding="utf-8")
    print(f"Written conventions discovery to {report_path}")

    # structured raw outputs
    write_roles_csv(discovery["sops"], ctx_dir / "agents")
    write_artifacts_csv(discovery["sops"], ctx_dir / "artifacts")
    write_sop_txt(discovery["sops"], ctx_dir / "SOP")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

