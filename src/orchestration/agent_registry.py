from __future__ import annotations

import json
from pathlib import Path

from src.framework.models import ActorKind, AgentDefinition
from src.framework.repo_layout import get_framework_root

MANIFEST_FILENAME = "manifest.json"

# Deprecated compatibility alias. Runtime configuration now comes from the framework manifest.
AGENT_DEFINITIONS: dict[str, AgentDefinition] = {}


def load_agent_definitions(repo_root: Path) -> dict[str, AgentDefinition]:
    """Load role and agent definitions from the configured framework."""
    framework_root = get_framework_root(repo_root)
    manifest_path = framework_root / "agents" / MANIFEST_FILENAME
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"Agent manifest saknas i frameworket: {manifest_path}"
        )

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    items = data.get("agents")
    if not isinstance(items, list) or not items:
        raise ValueError(f"Ogiltigt agentmanifest i {manifest_path}: 'agents' måste vara en icke-tom lista")

    definitions: dict[str, AgentDefinition] = {}
    role_index: dict[str, str] = {}
    for item in items:
        if not isinstance(item, dict):
            raise ValueError(f"Ogiltig agentpost i {manifest_path}: varje post måste vara ett objekt")
        agent_id = _require_non_empty_string(item, "agent_id", manifest_path)
        agent_file = _require_non_empty_string(item, "agent_file", manifest_path)
        raci_role_id = _require_non_empty_string(item, "raci_role_id", manifest_path)
        display_name = _optional_string(item.get("display_name")) or raci_role_id
        actor_kind = ActorKind(_optional_string(item.get("actor_kind")) or ActorKind.automated.value)

        if agent_id in definitions:
            raise ValueError(f"Dubblett av agent_id i {manifest_path}: {agent_id}")

        normalized_role = normalize_raci_role(raci_role_id)
        if normalized_role in role_index:
            existing_agent_id = role_index[normalized_role]
            raise ValueError(
                f"Dubblett av RACI-roll i {manifest_path}: '{raci_role_id}' används av både "
                f"{existing_agent_id} och {agent_id}"
            )

        agent_path = framework_root / "agents" / agent_file
        if not agent_path.exists():
            raise FileNotFoundError(
                f"Agentfil saknas för '{agent_id}' i manifestet: {agent_path}"
            )

        definitions[agent_id] = AgentDefinition(
            agent_id=agent_id,
            agent_file=agent_file,
            raci_role_id=raci_role_id,
            actor_kind=actor_kind,
            display_name=display_name,
        )
        role_index[normalized_role] = agent_id

    return definitions


def build_raci_role_index(agent_definitions: dict[str, AgentDefinition]) -> dict[str, str]:
    """Build an exact-match lookup from normalized RACI role to agent id."""
    role_index: dict[str, str] = {}
    for agent_id, definition in agent_definitions.items():
        normalized = normalize_raci_role(definition.raci_role_id)
        if normalized in role_index:
            raise ValueError(
                f"Dubblett av RACI-roll i agentdefinitionerna: {definition.raci_role_id}"
            )
        role_index[normalized] = agent_id
    return role_index


def normalize_raci_role(value: str) -> str:
    return " ".join(value.strip().casefold().split())


def _require_non_empty_string(item: dict[str, object], key: str, manifest_path: Path) -> str:
    value = _optional_string(item.get(key))
    if not value:
        raise ValueError(f"Ogiltigt agentmanifest i {manifest_path}: '{key}' måste vara en icke-tom sträng")
    return value


def _optional_string(value: object) -> str | None:
    return value if isinstance(value, str) and value.strip() else None
