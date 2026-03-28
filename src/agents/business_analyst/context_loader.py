"""
FrameworkContextLoader — reads framework documents from docs/ for the Business Analyst agent.

All reads are read-only. This module never writes to docs/.
Sources:
    docs/Roller/Business Analyst.md
    docs/SOP/1.Kravställning/*.md
    docs/Artifakter/Descriptions/1.Kravställning/*.md
    docs/Artifakter/Innehåll/1.Kravställning/*.md
"""

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
    """
    Loads framework context (role, SOPs, artifact descriptions and templates)
    from the docs/ directory.

    Parsing strategy: simple section-based text extraction.
    No external markdown libraries required.
    """

    ROLE_NAME = "Business Analyst"
    PROCESS_STEP = "1.Kravställning"

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.docs_root = repo_root / "docs"

    # ------------------------------------------------------------------
    # Role
    # ------------------------------------------------------------------

    def load_role(self) -> str:
        """Return the full text of the Business Analyst role definition."""
        path = self.docs_root / "Roller" / "Business Analyst.md"
        return path.read_text(encoding="utf-8")

    # ------------------------------------------------------------------
    # SOPs
    # ------------------------------------------------------------------

    def load_sops_for_role(self) -> list[SopEntry]:
        """
        Return all SOPs in 1.Kravställning where Business Analyst is R (Responsible).
        Parses each SOP file for Input, Output and RACI sections.
        """
        sop_dir = self.docs_root / "SOP" / self.PROCESS_STEP
        entries: list[SopEntry] = []
        for sop_file in sorted(sop_dir.glob("*.md")):
            content = sop_file.read_text(encoding="utf-8")
            if self._is_responsible(content):
                entries.append(
                    SopEntry(
                        name=self._extract_sop_name(content, sop_file.stem),
                        path=sop_file,
                        content=content,
                        inputs=self._extract_section_items(content, "3. Input"),
                        outputs=self._extract_section_items(content, "4. Output"),
                    )
                )
        return entries

    def load_sop(self, filename: str) -> SopEntry:
        """Load a specific SOP file by filename (e.g. '01_vision_och_malbild.md')."""
        path = self.docs_root / "SOP" / self.PROCESS_STEP / filename
        content = path.read_text(encoding="utf-8")
        return SopEntry(
            name=self._extract_sop_name(content, Path(filename).stem),
            path=path,
            content=content,
            inputs=self._extract_section_items(content, "3. Input"),
            outputs=self._extract_section_items(content, "4. Output"),
        )

    # ------------------------------------------------------------------
    # Artifact descriptions and templates
    # ------------------------------------------------------------------

    def load_artifact_description(self, artifact_name: str) -> str:
        """
        Return the artifact description text from docs/Artifakter/Descriptions/.
        artifact_name: e.g. 'Vision & målbild'
        """
        desc_dir = self.docs_root / "Artifakter" / "Descriptions" / self.PROCESS_STEP
        path = self._find_file_by_name(desc_dir, artifact_name)
        if path is None:
            raise FileNotFoundError(
                f"Artifact description not found for '{artifact_name}' in {desc_dir}"
            )
        return path.read_text(encoding="utf-8")

    def load_artifact_template(self, artifact_filename: str) -> str:
        """
        Return the artifact template/content from docs/Artifakter/Innehåll/.
        artifact_filename: e.g. 'vision_och_malbild.md'
        """
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

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _is_responsible(self, sop_content: str) -> bool:
        """Return True if Business Analyst is listed as R in the RACI section."""
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
        """Extract SOP name from the first heading line."""
        for line in content.splitlines():
            if line.startswith("# "):
                return line.lstrip("# ").strip()
        return fallback

    def _extract_section_items(self, content: str, section_heading: str) -> list[str]:
        """
        Extract bullet-point items from a named section.
        E.g. section_heading='3. Input' returns ['Övergripande behov']
        """
        raw = self._extract_raw_section(content, section_heading)
        items = []
        for line in raw.splitlines():
            stripped = line.strip()
            if stripped.startswith("- "):
                items.append(stripped[2:].strip())
        return items

    def _extract_raw_section(self, content: str, section_heading: str) -> str:
        """
        Return the raw text of a section (from its heading until the next ## heading).
        """
        lines = content.splitlines()
        collecting = False
        result: list[str] = []
        target = f"## {section_heading}"
        for line in lines:
            if line.strip() == target:
                collecting = True
                continue
            if collecting:
                if line.startswith("## ") and line.strip() != target:
                    break
                result.append(line)
        return "\n".join(result)

    def _find_file_by_name(self, directory: Path, artifact_name: str) -> Path | None:
        """
        Find a markdown file in directory whose filename (without extension)
        matches artifact_name closely (case-insensitive, ignores punctuation).
        Falls back to checking content for matching artifact name.
        """
        if not directory.exists():
            return None
        normalized_target = self._normalize_name(artifact_name)
        for md_file in directory.glob("*.md"):
            if self._normalize_name(md_file.stem) == normalized_target:
                return md_file
        # Second pass: match by content title
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
        """Lowercase, strip whitespace and common punctuation for loose matching."""
        return re.sub(r"[\s\-_&]", "", name).lower()
