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

    AGENT_FILE = "business-analyst.md"

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.docs_root = repo_root / "docs"
        self._role_name: str | None = None

    @property
    def role_name(self) -> str:
        if self._role_name is None:
            content = self.load_role()
            for line in content.splitlines():
                if line.startswith("# Agent:"):
                    self._role_name = line[len("# Agent:"):].strip()
                    break
            else:
                self._role_name = "Business Analyst"
        return self._role_name

    def load_role(self) -> str:
        return (self.docs_root / "agents" / self.AGENT_FILE).read_text(encoding="utf-8")

    def load_agent_instructions(self) -> str:
        return self._extract_raw_section(self.load_role(), "Agentinstruktioner").strip()

    def load_sops_for_role(self) -> list[SopEntry]:
        return [
            SopEntry(
                name=self._extract_sop_name(content, sop_file.stem),
                path=sop_file,
                content=content,
                inputs=self._extract_section_items(content, "3. Input"),
                outputs=self._extract_section_items(content, "4. Output"),
            )
            for sop_file in sorted((self.docs_root / "SOP").rglob("*.md"))
            if self._is_responsible(content := sop_file.read_text(encoding="utf-8"))
        ]

    def load_sop(self, filename: str) -> SopEntry:
        matches = sorted((self.docs_root / "SOP").rglob(filename))
        if not matches:
            raise FileNotFoundError(f"SOP file not found: {filename}")
        path = matches[0]
        content = path.read_text(encoding="utf-8")
        return SopEntry(
            name=self._extract_sop_name(content, Path(filename).stem),
            path=path,
            content=content,
            inputs=self._extract_section_items(content, "3. Input"),
            outputs=self._extract_section_items(content, "4. Output"),
        )

    def load_artifact_description(self, artifact_name: str) -> str:
        desc_root = self.docs_root / "Artifakter" / "Descriptions"
        path = self._find_file_by_name(desc_root, artifact_name, recursive=True)
        if path is None:
            raise FileNotFoundError(
                f"Artifact description not found for '{artifact_name}' in {desc_root}"
            )
        return path.read_text(encoding="utf-8")

    def load_artifact_template(self, artifact_filename: str) -> str:
        matches = sorted((self.docs_root / "Artifakter" / "Innehåll").rglob(artifact_filename))
        if not matches:
            raise FileNotFoundError(f"Artifact template not found: {artifact_filename}")
        return matches[0].read_text(encoding="utf-8")

    def _is_responsible(self, sop_content: str) -> bool:
        raci_section = self._extract_raw_section(sop_content, "5. RACI")
        if not raci_section:
            return False
        for line in raci_section.splitlines():
            stripped = line.strip()
            if re.match(r"-\s*R\s*:", stripped, re.IGNORECASE):
                role_value = re.sub(r"-\s*R\s*:\s*", "", stripped, flags=re.IGNORECASE)
                if self.role_name.lower() in role_value.lower():
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

    def _find_file_by_name(
        self, directory: Path, artifact_name: str, recursive: bool = False
    ) -> Path | None:
        if not directory.exists():
            return None
        glob = directory.rglob("*.md") if recursive else directory.glob("*.md")
        normalized_target = self._normalize_name(artifact_name)
        candidates = sorted(glob)
        for md_file in candidates:
            if self._normalize_name(md_file.stem) == normalized_target:
                return md_file
        for md_file in candidates:
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
