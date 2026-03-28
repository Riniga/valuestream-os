# Standards

This is the primary development guideline for the ValueStream OS repository.
If another guideline conflicts with this one, this document takes precedence.

ValueStream OS is built step by step.
Correctness is mandatory. Clarity, structure, and maintainability take priority over speed and cleverness.
Unnecessary complexity is never acceptable.

---

## Core Principles

- Follow SOLID principles when they improve clarity and separation of responsibility.
- Prefer clear and readable code over clever solutions.
- Logic that can be independently understood, tested, or reused should be separated into its own module.
- Remove duplication through shared modules or libraries when the duplication is real and recurring.
- Unit test reusable logic and code with meaningful branching or transformation.
- Do not introduce complexity before it is needed.

---

## Execution Flow

All work should follow this loop:

1. Define the task.
2. Create or refine a plan.
3. Break the work into small TODOs.
4. Implement one TODO at a time.
5. Verify the result before continuing.
6. Review the change.
7. Commit when the step is complete.
8. Repeat.

---

## Using Cursor

### Plan first

- Use the Cursor plan template when the task is not trivial.
- Keep the scope small and explicit.
- Do not implement during planning unless explicitly requested.

### Execute step by step

- Implement one TODO at a time.
- Do not batch multiple conceptual steps together.
- Verify each step before moving on.

### Keep control

- Review changes before accepting them.
- Preserve structure unless the task explicitly requires a change.
- Avoid unnecessary complexity and hidden behavior.
- Cursor should not redesign the whole project unless explicitly asked.

---

## Coding Workflow

1. Define a minimal, finite functionality and store the specification under `functionality/mvp/` using `<nn>-<functionality>.md`.
2. Create or refine the supporting specification: goal, scope, definition of done, user stories, and non-functional requirements.
3. Create a short-lived branch from `main` named `<nn>-<functionality>`.
4. Create a Cursor plan and store it under `functionality/plans/`.
5. Implement step by step from the plan, one small verified change at a time.
6. Review the result before moving on.
7. Commit the change when the step is complete and verified.
8. Open a pull request to `main` when the functionality is ready for review.
9. Let the deployment pipeline handle environment-specific deployment according to the deployment strategy.

---

## Branching Strategy

- `main` is protected and must remain production-ready.
- Development happens in short-lived feature branches created from `main`.
- Branch names must follow `<nn>-<functionality>`.
- Changes are merged to `main` through pull requests.
- Delete merged branches to keep the repository clean.

---

## Deployment Strategy

- These rules apply when a deployment pipeline is configured for the repository.
- Deployments are triggered from `main`.
- UAT deployment is handled by the deployment pipeline.
- Production deployment must be explicitly approved after validation.
- Rollback must be possible if a deployment fails or causes unexpected issues.

---

## Repository Structure

- `docs/` = framework definition
  - process, SOPs, roles, RACI, artifacts
- `src/` = implementation
  - agents, orchestration, capabilities, memory/state
- `setup/` = setup and development rules
  - environment setup, development guidelines, Cursor-related instructions
- `runs/` = runtime state and generated output
  - must never be committed

Do not mix responsibilities between these areas.

---

## Naming

### Files

- Keep names explicit and readable.
- Follow existing repository conventions instead of forcing one naming style everywhere.
- For agent definition documents under `docs/agents/`, use `kebab-case.md`.
- For artifact templates and descriptions, keep the established artifact-facing names if they are already part of the framework vocabulary.
- For implementation files, follow the language convention of that area, for example `snake_case.py` in Python.

### Code

- Prefer clear names over short names.
- Avoid unnecessary abbreviations.
- Use names that reflect the framework vocabulary: agent, role, SOP, artifact, process step, orchestration, capability.

---

## Pull Request Scope

- Keep changes small and reviewable.
- One purpose per PR.
- Update documentation when behavior or structure changes.
- Do not include generated runtime data.

---

## Commit Guidance

Use a light conventional format:

`<type>(<scope>): <message>`

Examples:

- `feat(agents): add base agent interface`
- `feat(orchestration): add SOP loader`
- `docs(setup): add cursor plan template`
- `chore(repo): update gitignore`

Types: `feat` `fix` `docs` `chore` `refactor` `test`

---

## Recommended Tools

- Cursor for planning, implementation, and review support.
- Claude Code from a Cursor terminal when a second implementation agent is helpful.
- Context7 for external documentation lookup when needed.
- GitHub review tooling for final review support.

---

## Runtime and Sensitive Data

- Never commit files from `runs/`.
- Never commit secrets.
- Never use runtime output as permanent documentation.
- Keep the public repository free from customer or company-specific data.

---

## Decision Rule

When in doubt:

- choose the simpler design
- choose the smaller step
- choose the more explicit structure
