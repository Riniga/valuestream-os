from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SopEntry:
    name: str
    path: Path
    content: str
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)


class FrameworkContextLoader:

    ROLE_NAME = "Business Analyst"
    PROCESS_STEP = "1.Kravställning"
    AGENT_FILE = "business-analyst.md"

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.docs_root = repo_root / "docs"

    def load_role(self) -> str:
        return (self.docs_root / "agents" / self.AGENT_FILE).read_text(encoding="utf-8")

    def load_agent_instructions(self) -> str:
        content = self.load_role()
        return self._extract_raw_section(content, "Agentinstruktioner").strip()

    def load_sops_for_role(self) -> list[SopEntry]:
        sop_dir = self.docs_root / "SOP" / self.PROCESS_STEP
        return [
            SopEntry(
                name=self._extract_sop_name(content, sop_file.stem),
                path=sop_file,
                content=content,
                inputs=self._extract_section_items(content, "3. Input"),
                outputs=self._extract_section_items(content, "4. Output"),
            )
            for sop_file in sorted(sop_dir.glob("*.md"))
            if self._is_responsible(content := sop_file.read_text(encoding="utf-8"))
        ]

    def load_sop(self, filename: str) -> SopEntry:
        path = self.docs_root / "SOP" / self.PROCESS_STEP / filename
        content = path.read_text(encoding="utf-8")
        return SopEntry(
            name=self._extract_sop_name(content, Path(filename).stem),
            path=path,
            content=content,
            inputs=self._extract_section_items(content, "3. Input"),
            outputs=self._extract_section_items(content, "4. Output"),
        )

    def load_artifact_description(self, artifact_name: str) -> str:
        desc_dir = self.docs_root / "Artifakter" / "Descriptions" / self.PROCESS_STEP
        path = self._find_file_by_name(desc_dir, artifact_name)
        if path is None:
            raise FileNotFoundError(
                f"Artifact description not found for '{artifact_name}' in {desc_dir}"
            )
        return path.read_text(encoding="utf-8")

    def load_artifact_template(self, artifact_filename: str) -> str:
        path = (
            self.docs_root
            / "Artifakter"
            / "Innehåll"
            / self.PROCESS_STEP
            / artifact_filename
        )
        if not path.exists():
            raise FileNotFoundError(f"Artifact template not found: {path}")
        return path.read_text(encoding="utf-8")

    def _is_responsible(self, sop_content: str) -> bool:
        raci_section = self._extract_raw_section(sop_content, "5. RACI")
        if not raci_section:
            return False
        for line in raci_section.splitlines():
            stripped = line.strip()
            if re.match(r"-\s*R\s*:", stripped, re.IGNORECASE):
                role_value = re.sub(r"-\s*R\s*:\s*", "", stripped, flags=re.IGNORECASE)
                if self.ROLE_NAME.lower() in role_value.lower():
                    return True
        return False

    def _extract_sop_name(self, content: str, fallback: str) -> str:
        for line in content.splitlines():
            if line.startswith("# "):
                return line.lstrip("# ").strip()
        return fallback

    def _extract_section_items(self, content: str, section_heading: str) -> list[str]:
        raw = self._extract_raw_section(content, section_heading)
        return [
            line.strip()[2:].strip()
            for line in raw.splitlines()
            if line.strip().startswith("- ")
        ]

    def _extract_raw_section(self, content: str, section_heading: str) -> str:
        lines = content.splitlines()
        collecting = False
        result: list[str] = []
        for line in lines:
            if re.match(rf"^##\s+{re.escape(section_heading)}\s*$", line):
                collecting = True
                continue
            if collecting:
                if line.startswith("## "):
                    break
                result.append(line)
        return "\n".join(result)

    def _find_file_by_name(self, directory: Path, artifact_name: str) -> Path | None:
        if not directory.exists():
            return None
        normalized_target = self._normalize_name(artifact_name)
        for md_file in directory.glob("*.md"):
            if self._normalize_name(md_file.stem) == normalized_target:
                return md_file
        for md_file in directory.glob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            for line in content.splitlines():
                if line.startswith("# Artefakt:") or line.startswith("# Artifact:"):
                    title = re.sub(r"^#[^:]*:\s*", "", line).strip()
                    if self._normalize_name(title) == normalized_target:
                        return md_file
        return None

    @staticmethod
    def _normalize_name(name: str) -> str:
        return re.sub(r"[\s\-_&]", "", name).lower()
