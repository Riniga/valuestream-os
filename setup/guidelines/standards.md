# Standards

The purpose of this document is to keep development simple, consistent, and scalable.

ValueStream OS is built step by step.
Clarity, structure, and traceability take priority over speed and cleverness.

---

## Core Principles

- Build in small steps
- Keep docs and implementation separated
- Prefer explicit structure over implicit behavior
- Keep changes easy to review
- Do not introduce complexity before it is needed

---

## Repository Structure

- `docs/` contains the framework model:
  - process
  - SOPs
  - roles
  - RACI
  - artifacts

- `setup/` contains:
  - environment setup
  - development guidelines
  - Cursor-related instructions

- `src/` contains implementation:
  - agents
  - orchestration
  - capabilities
  - memory/state

- `runs/` contains runtime output and execution data
  - must never be committed

---

## Naming

### Files

- Use `PascalCase` for core framework documents when they are primary named artifacts
- Use `kebab-case` for technical and implementation-oriented files where appropriate
- Keep names explicit and readable

### Code

- Prefer clear names over short names
- Avoid unnecessary abbreviations
- Use names that reflect the framework vocabulary:
  - agent
  - role
  - SOP
  - artifact
  - process step
  - orchestration
  - capability

---

## Development Approach

- Implement one small, testable step at a time
- Do not mix multiple architectural decisions in one change
- Start with the simplest working solution
- Refactor only when structure clearly improves
- Keep orchestration logic explicit

---

## Cursor Usage

- Cursor should work from a clear plan
- Each plan should be broken into small TODOs
- Each TODO should produce a concrete result
- Cursor should not redesign the whole project unless explicitly asked
- Cursor should preserve existing structure unless the task requires change

---

## Pull Request Scope

- Keep changes small and reviewable
- One purpose per PR
- Update documentation when behavior or structure changes
- Do not include generated runtime data

---

## Commit Guidance

Use a light conventional format:

`<type>(<scope>): <message>`

Examples:

- `feat(agents): add base agent interface`
- `feat(orchestration): add SOP loader`
- `docs(setup): add cursor plan template`
- `chore(repo): update gitignore`

Types:

- `feat`
- `fix`
- `docs`
- `chore`
- `refactor`
- `test`

---

## Runtime and Sensitive Data

- Never commit files from `runs/`
- Never commit secrets
- Never use runtime output as permanent documentation
- Keep the public repository free from customer or company-specific data

---

## Decision Rule

When in doubt:

- choose the simpler design
- choose the more explicit structure
- choose the smaller implementation step
