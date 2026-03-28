# Cursor Plan Prompt Template

Use this template when asking Cursor to create an implementation plan.

---

## Template

You are working in the ValueStream OS repository.

Task:
[Describe the implementation goal clearly]

Context:

- The repository separates:
  - `docs/` for framework definitions
  - `setup/` for setup and development guidance
  - `src/` for implementation
  - `runs/` for runtime output
- Treat `setup/guidelines/coding-strategy.md` as the primary guideline if there is overlap
- Keep strategy, structure, and implementation separated
- Build step by step
- Do not overengineer

Requirements:

- Create a short implementation plan
- Break the work into small TODOs
- Each TODO should be concrete and verifiable
- Preserve current repository structure unless change is required
- Keep the solution minimal but extensible
- Do not implement yet unless explicitly asked

Output format:

1. Goal
2. Assumptions
3. Proposed file changes
4. Step-by-step TODO list
5. Risks / open questions

Optional constraints:

- [Add constraints here]
- [Example: use Python]
- [Example: keep orchestration explicit]
- [Example: avoid new dependencies]

---

## Example

You are working in the ValueStream OS repository.

Task:
Create the first implementation of a base agent interface in Python.

Context:

- `docs/` contains framework definitions
- `src/` contains implementation
- Keep strategy and implementation separated
- Build step by step
- Do not overengineer

Requirements:

- Create a short implementation plan
- Break the work into small TODOs
- Each TODO should be concrete and verifiable
- Do not implement yet

Output format:

1. Goal
2. Assumptions
3. Proposed file changes
4. Step-by-step TODO list
5. Risks / open questions
