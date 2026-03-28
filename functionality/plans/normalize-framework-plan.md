## Plan: Normalize framework docs + generate artifacts

Goal

- Build a minimal, explicit Python-based pre-agent processor for SOP docs that creates normalized RACI and artifact catalogues, plus artifact description/template artifacts.

Assumptions

- SOPs live under docs/SOP/{process}/ and use a stable convention:
  - Header '# SOP x: ...'
  - Sections '## 3. Input', '## 4. Output', '## 5. RACI'
  - RACI lines are '- R: Role', '- A: Role', '- C: Role', '- I: Role'
- Artifact details in this step are derived from SOP I/O and not from existing Artifakter files.
- Artifact description template exists at docs/Artifakter/Descriptions/Template_ArtifactDescription.md; user requirement mentions Artifakter/Template_ArtifactDescription.md, so script should support both location and fallback.
- Existing repository structure remains and generated files go under docs/ and /runs or dedicated generated folder; no new top-level changes unless required.
- No new dependencies beyond Python standard library; avoid markdown libs.

Proposed file changes

- Add new script(s) under src/tools or scripts:
  - src/tools/sop_normalizer.py (main ETL) + optional module src/tools/sop_parser.py
  - src/tools/sop_validator.py (validation and consistency checks)
- Update README/docs with a short usage section (docs/Process.md or setup guidelines).
- Generated output files in docs/RACI/RACI.md, docs/Artifakter/artifakter.md, docs/Artifakter/Descriptions/{artifact}.md, docs/Artifakter/Templates/{artifact}.md
- Keep source files under docs/SOP unchanged.

Step-by-step TODO list

1. Discover and codify SOP conventions (quick review of sample SOPs and working format). Verifiable by listing patterns.
2. Create SOP parser in Python:
   - Scans docs/SOP recursively.
   - Extracts SOP key (name + path), RACI entries, input artifact list, output artifact list.
   - Normalize names (strip whitespace, lower/upper for role keys, unify duplicates).
   - Fail fast on non-expected formats (e.g. missing RACI or I/O sections).
3. Implement RACI aggregation script:
   - Build role-index mapping with R/A/C/I sets of SOP references.
   - Emit docs/RACI/RACI.md with heading and markdown table: Role / R / A / C / I.
   - Include reproducible sorting rule (role alphabetical, SOP path alphabetical).
4. Implement artifact aggregation script:
   - Build artifact-index mapping with Output-from and Input-in SOP reference lists.
   - Emit docs/Artifakter/artifakter.md with table: Artifact / Output from / Input in.
   - Define artifact identity normalization (trim, case, alias handling from same names).
5. Implement artifact descriptor generation:
   - Read Template_ArtifactDescription.md (given path or fallback).
   - For each artifact, create docs/Artifakter/Descriptions/{artifact_name}.md from template with placeholder replacements: artifact name, inferred type, sample SOPs, and minimal sections.
   - If same artifact exists, maybe update or skip with warning.
6. Implement artifact template generation:
   - Use first simple rule engine:
     - If artifact name contains 'vision' or 'målbild' => type: product-scope document and default headings.
     - If artifact is in output list from SOP named '...analys...' => type: analysis report.
     - Else default to generic structure with '## Purpose', '## Content', '## Notes'.
   - Write docs/Artifakter/Templates/{artifact_name}.md
7. Add validation hooks / normalize checks:
   - ensure every artifact appears as output in at least one SOP (if appears only in input, log as external dependency).
   - check for inconsistent role casing or duplicates.
   - identify missing RACI role categories in any SOP (warn if R/A/C/I incomplete).
   - check for SOP references that include nonexistent files.
8. Add a simple CLI wrapper under src/tools/sop_normalizer.py:
   - actions: `--generate-raci`, `--generate-artifacts`, `--generate-descriptions`, `--generate-templates`, `--validate`, `--dry-run`.
   - include `--source=docs/SOP` and output directories.
9. Add doc section in README or docs explaining invocation and expected generated files.

Risks / open questions

- Role naming variations may produce duplicate rows; need canonical role mapping. Should we create a role reference table outside script? (Yes likely from docs/Roller).
- Artifact naming conventions might not be unique (same artifact name in different contexts). Should we namespace by process? The requirement says row per artifact; one row may combine.
- A template exists in docs/Artifakter/Descriptions, not root. Need clarify canonical path.
- Determinism and no dependencies are satisfied by sorting and localized paths.
- Must include explicit distinction between source files (docs/SOP/_) and generated (docs/RACI/RACI.md, docs/Artifakter/_).
- Do we need to support existing `docs/Artifakter/Artifacts.md` as source? Not now; source is SOP.
- About file format of generated markdown (table column width etc), we can keep simple.
