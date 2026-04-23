"""
AgentContextLoader — role-agnostic document loader for the framework.

Loads role descriptions, SOPs, artifact descriptions, and artifact templates
from the configured framework directory for any agent role.
Parameterised by agent_file and raci_role_id so that the same code works for
Business Analyst, UX, and future roles.

The framework location is configurable via the FRAMEWORK environment variable
(legacy FRAMWORK is also supported; defaults to "framework/standard").
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote

from src.framework.repo_layout import get_framework_root


@dataclass
class SopEntry:
    name: str
    path: Path
    content: str
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)


class AgentContextLoader:
    """
    Loads framework docs for one agent role.

    Parameters
    ----------
    repo_root:
        Absolute path to the repository root.
    agent_file:
        Filename inside the agents directory, e.g. "business-analyst.md" or "ux.md".
    raci_role_id:
        The role identifier as it appears in SOP RACI sections (e.g. "Business Analyst"
        or "UX"). When None the role name extracted from the agent file is used.
    """

    def __init__(
        self,
        repo_root: Path,
        agent_file: str,
        raci_role_id: str | None = None,
    ) -> None:
        self.repo_root = repo_root
        self.framework_root = get_framework_root(repo_root)
        self.agent_file = agent_file
        self._raci_role_id = raci_role_id
        self._role_name: str | None = None

    # ------------------------------------------------------------------
    # Public: role identity
    # ------------------------------------------------------------------

    @property
    def role_name(self) -> str:
        if self._role_name is None:
            content = self.load_role()
            for line in content.splitlines():
                for prefix in ("# Agent:", "# Roll:"):
                    if line.startswith(prefix):
                        self._role_name = line[len(prefix):].strip()
                        break
                if self._role_name:
                    break
            if not self._role_name:
                self._role_name = self.agent_file.replace(".md", "").replace("-", " ").title()
        return self._role_name

    @property
    def raci_role(self) -> str:
        """Role identifier used when matching RACI fields in SOPs."""
        return self._raci_role_id if self._raci_role_id is not None else self.role_name

    # ------------------------------------------------------------------
    # Public: role and agent docs
    # ------------------------------------------------------------------

    def load_role(self) -> str:
        path = self.framework_root / "agents" / self.agent_file
        return path.read_text(encoding="utf-8")

    def load_agent_instructions(self) -> str:
        content = self.load_role()
        section = self._extract_raw_section(content, "Agentinstruktioner").strip()
        if not section:
            return content.strip()
        return section

    def load_agent_purpose(self) -> str:
        content = self.load_role()
        section = self._extract_raw_section(content, "Syfte").strip()
        return section if section else ""

    # ------------------------------------------------------------------
    # Public: SOPs
    # ------------------------------------------------------------------

    def load_sops_for_role(self) -> list[SopEntry]:
        result: list[SopEntry] = []
        for sop_file in sorted((self.framework_root / "SOP").rglob("*.md")):
            content = sop_file.read_text(encoding="utf-8")
            if self._is_responsible(content):
                result.append(
                    SopEntry(
                        name=self._extract_sop_name(content, sop_file.stem),
                        path=sop_file,
                        content=content,
                        inputs=self._extract_section_items(content, "3. Input"),
                        outputs=self._extract_section_items(content, "4. Output"),
                    )
                )
        return result

    def load_sop(self, filename: str) -> SopEntry:
        normalized_filename = unquote(filename)
        matches = sorted((self.framework_root / "SOP").rglob(normalized_filename))
        if not matches:
            raise FileNotFoundError(f"SOP file not found: {normalized_filename}")
        path = matches[0]
        content = path.read_text(encoding="utf-8")
        return SopEntry(
            name=self._extract_sop_name(content, Path(normalized_filename).stem),
            path=path,
            content=content,
            inputs=self._extract_section_items(content, "3. Input"),
            outputs=self._extract_section_items(content, "4. Output"),
        )

    # ------------------------------------------------------------------
    # Public: artifacts
    # ------------------------------------------------------------------

    def load_artifact_description(self, artifact_name: str) -> str:
        path = self._find_file_by_name(
            self.framework_root / "artifacts" / "descriptions", artifact_name, recursive=True
        )
        if path is None:
            raise FileNotFoundError(
                f"Artifact description not found for '{artifact_name}'"
            )
        return path.read_text(encoding="utf-8")

    def load_artifact_template(self, artifact_filename: str) -> str:
        matches = sorted(
            (self.framework_root / "artifacts" / "templates").rglob(artifact_filename)
        )
        if not matches:
            raise FileNotFoundError(f"Artifact template not found: {artifact_filename}")
        return matches[0].read_text(encoding="utf-8")

    def find_template_path(self, artifact_name: str) -> Path | None:
        return self._find_file_by_name(
            self.framework_root / "artifacts" / "templates", artifact_name, recursive=True
        )

    def find_description_path(self, artifact_name: str) -> Path | None:
        return self._find_file_by_name(
            self.framework_root / "artifacts" / "descriptions", artifact_name, recursive=True
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _is_responsible(self, sop_content: str) -> bool:
        raci_section = self._extract_raw_section(sop_content, "5. RACI")
        if not raci_section:
            return False
        normalized_role = self._normalize_role_value(self.raci_role)
        for line in raci_section.splitlines():
            stripped = line.strip()
            if re.match(r"-\s*R\s*:", stripped, re.IGNORECASE):
                role_value = re.sub(r"-\s*R\s*:\s*", "", stripped, flags=re.IGNORECASE)
                roles = [
                    self._normalize_role_value(part)
                    for part in role_value.split(",")
                    if part.strip()
                ]
                if normalized_role in roles:
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
        glob_fn = directory.rglob if recursive else directory.glob
        normalized_target = self._normalize_name(artifact_name)
        candidates = sorted(glob_fn("*.md"))

        for f in candidates:
            if self._normalize_name(f.stem) == normalized_target:
                return f

        for f in candidates:
            title = self._extract_file_title(f)
            if title and self._normalize_name(title) == normalized_target:
                return f

        return None

    @staticmethod
    def _extract_file_title(path: Path) -> str | None:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return (
                    re.sub(r"^#[^:]*:\s*", "", line).strip()
                    if ":" in line[2:]
                    else line[2:].strip()
                )
        return None

    @staticmethod
    def _normalize_name(name: str) -> str:
        ascii_name = (
            unicodedata.normalize("NFKD", name)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
        return re.sub(r"[\s\-_&]", "", ascii_name).lower()

    @staticmethod
    def _normalize_role_value(value: str) -> str:
        return " ".join(value.strip().casefold().split())
