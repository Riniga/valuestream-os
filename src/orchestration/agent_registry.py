from __future__ import annotations

from src.framework.models import AgentDefinition


AGENT_DEFINITIONS: dict[str, AgentDefinition] = {
    "business-analyst": AgentDefinition(
        agent_id="business-analyst",
        agent_file="business-analyst.md",
        raci_role_id="Business Analyst",
    ),
    "ux": AgentDefinition(
        agent_id="ux",
        agent_file="ux.md",
        raci_role_id="UX",
    ),
}
