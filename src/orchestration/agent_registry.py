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
    "produktagare": AgentDefinition(
        agent_id="produktagare",
        agent_file="produktägare.md",
        raci_role_id="Beställare",
    ),
    "verksamhetsexperter": AgentDefinition(
        agent_id="verksamhetsexperter",
        agent_file="verksamhetsexperter.md",
        raci_role_id="Verksamhetsexperter",
    ),
    "projektledare": AgentDefinition(
        agent_id="projektledare",
        agent_file="projektledare.md",
        raci_role_id="Projektledare",
    ),
    "losningsarkitekt": AgentDefinition(
        agent_id="losningsarkitekt",
        agent_file="lösningsarkitekt.md",
        raci_role_id="Lösningsarkitekt",
    ),
    "utvecklare": AgentDefinition(
        agent_id="utvecklare",
        agent_file="utvecklare.md",
        raci_role_id="Utvecklare",
    ),
    "anvandarrepresentanter": AgentDefinition(
        agent_id="anvandarrepresentanter",
        agent_file="användarrepresentanter.md",
        raci_role_id="Användarrepresentanter",
    ),
    "enterprise-arkitekt": AgentDefinition(
        agent_id="enterprise-arkitekt",
        agent_file="enterprise-arkitekt.md",
        raci_role_id="Enterprise Arkitekt",
    ),
    "teknisk-lead": AgentDefinition(
        agent_id="teknisk-lead",
        agent_file="teknisk-lead.md",
        raci_role_id="Teknisk Lead",
    ),
    "dataarkitekt": AgentDefinition(
        agent_id="dataarkitekt",
        agent_file="dataarkitekt.md",
        raci_role_id="Dataarkitekt",
    ),
    "devops": AgentDefinition(
        agent_id="devops",
        agent_file="devops.md",
        raci_role_id="DevOps",
    ),
}
