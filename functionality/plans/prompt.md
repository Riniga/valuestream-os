You are working in the ValueStream OS repository.

Task:
Create a step-by-step implementation plan for building an Agent Orchestration Framework focused on the "Kravställning" process.

The goal is to enable agents to:

- Read input documents from the runs/ folder
- Process them according to defined SOPs
- Generate new artifacts as output in the runs/ folder

The system should support a complete flow from:
User Stories → User Journeys → Övergripande behov → Epics & Capabilities → Funktionella block → Story Map → Prioriterad backlog → KPI → Uppföljning

Context:

- The repository separates:
  - `docs/` for framework definitions (SOPs, artifacts, roles)
  - `src/` for implementation (agents, orchestration)
  - `runs/` for runtime execution (input/output documents)

- The framework is already defined with:
  - SOPs per process step
  - Artifact templates (Markdown)
  - Roles and RACI mappings

- The runs/ folder acts as a "live workspace":
  - Input documents are placed here
  - Agents read from here
  - Agents write output artifacts here

- Agents should follow SOPs strictly:
  - Input artifacts
  - Output artifacts
  - Defined responsibilities

Agents to implement in this phase:

Core (produce artifacts):

- Business Analyst
- UX

Decision:

- Product Owner (review / approve)

Support (can be queried / provide input):

- User Representatives
- Project Manager
- Developers
- UX (as stakeholder as well)
- Business Experts

Inform:

- Business Analyst
- Solution Architect
- Project Manager
- Developers

Requirements:

- Create a COMPLETE but stepwise implementation plan
- Start simple (first working flow), then evolve
- Focus ONLY on Kravställning initially
- Use the existing SOPs and artifact structure (do not redesign them)

- The plan should:
  - Define how agents are structured
  - Define how orchestration works (simple first)
  - Define how files in runs/ are discovered and processed
  - Define how input/output mapping between artifacts works
  - Define how roles interact (ask / review / inform)

- Break everything into small, concrete TODOs
- Each TODO must be testable (e.g. "Given X file → Y output is created")

- Avoid:
  - Overengineering
  - Complex frameworks
  - External dependencies (unless absolutely needed)

Output format:

1. Goal
2. Assumptions
3. Proposed file / folder structure
4. Step-by-step TODO list (VERY concrete)
5. First minimal working scenario (example run)
6. Risks / open questions

Optional constraints:

- Use Python
- Keep orchestration explicit (no workflow engine initially)
- Use file-based state (Markdown + JSON if needed)
- Each agent should be independently testable
- Prefer clarity over abstraction
