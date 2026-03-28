from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.agents.business_analyst.context_loader import FrameworkContextLoader


@dataclass(frozen=True)
class ArtifactDefinition:
    name: str
    template_filename: str
    output_filename: str
    sop_filename: str
    input_filenames: list[str]


def build_artifact_registry(loader: "FrameworkContextLoader") -> list[ArtifactDefinition]:
    registry: list[ArtifactDefinition] = []
    seen: set[str] = set()

    for sop in loader.load_sops_for_role():
        for output_name in sop.outputs:
            if output_name in seen:
                continue
            seen.add(output_name)

            template_path = loader.find_template_path(output_name)
            if template_path is None:
                continue

            input_filenames = [
                p.name
                for input_name in sop.inputs
                if (p := loader.find_template_path(input_name)) is not None
            ]

            registry.append(
                ArtifactDefinition(
                    name=output_name,
                    template_filename=template_path.name,
                    output_filename=template_path.name,
                    sop_filename=sop.path.name,
                    input_filenames=input_filenames,
                )
            )

    return registry


def get_artifact(
    registry: list[ArtifactDefinition], output_filename: str
) -> ArtifactDefinition | None:
    return next((a for a in registry if a.output_filename == output_filename), None)


def get_artifact_by_name(
    registry: list[ArtifactDefinition], name: str
) -> ArtifactDefinition | None:
    normalized = name.strip().lower()
    return next((a for a in registry if a.name.lower() == normalized), None)
