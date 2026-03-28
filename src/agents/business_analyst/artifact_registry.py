"""
ArtifactRegistry — maps artifact names to their template filenames and output filenames.

This is the single source of truth for name→file mappings.
Add entries here as more artifacts are covered by the BA agent.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ArtifactDefinition:
    name: str
    template_filename: str
    output_filename: str
    sop_filename: str
    input_filenames: list[str]


ARTIFACT_REGISTRY: list[ArtifactDefinition] = [
    ArtifactDefinition(
        name="Vision & målbild",
        template_filename="vision_och_malbild.md",
        output_filename="vision_och_malbild.md",
        sop_filename="01_vision_och_malbild.md",
        input_filenames=["overgripande_behov.md"],
    ),
    ArtifactDefinition(
        name="Scope & avgränsningar",
        template_filename="scope_och_avgransningar.md",
        output_filename="scope_och_avgransningar.md",
        sop_filename="03_scope_och_avgransningar.md",
        input_filenames=["vision_och_malbild.md", "overgripande_behov.md"],
    ),
]


def get_artifact(output_filename: str) -> ArtifactDefinition | None:
    for artifact in ARTIFACT_REGISTRY:
        if artifact.output_filename == output_filename:
            return artifact
    return None


def get_artifact_by_name(name: str) -> ArtifactDefinition | None:
    normalized = name.strip().lower()
    for artifact in ARTIFACT_REGISTRY:
        if artifact.name.lower() == normalized:
            return artifact
    return None
