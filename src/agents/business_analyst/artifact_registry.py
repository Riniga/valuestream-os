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
    return next((a for a in ARTIFACT_REGISTRY if a.output_filename == output_filename), None)


def get_artifact_by_name(name: str) -> ArtifactDefinition | None:
    normalized = name.strip().lower()
    return next((a for a in ARTIFACT_REGISTRY if a.name.lower() == normalized), None)
