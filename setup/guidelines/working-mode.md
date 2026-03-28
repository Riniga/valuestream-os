# Working Mode

This document defines the operational execution loop for work in the ValueStream OS repository.
`coding-strategy.md` defines the higher-level development policy. This file focuses on day-to-day execution.

## Core Flow

All work should follow this loop:

1. Define the task.
2. Create or refine a plan.
3. Break the work into small TODOs.
4. Implement one TODO at a time.
5. Verify the result before continuing.
6. Review the change.
7. Commit when the step is complete.
8. Repeat.

## Using Cursor

### Step 1 - Plan first

- Use the Cursor plan template when the task is not trivial.
- Keep the scope small and explicit.
- Do not implement during planning unless explicitly requested.

### Step 2 - Execute step by step

- Implement one TODO at a time.
- Do not batch multiple conceptual steps together.
- Verify each step before moving on.

### Step 3 - Keep control

- Review changes before accepting them.
- Preserve structure unless the task explicitly requires a change.
- Avoid unnecessary complexity and hidden behavior.

## Change Size

- Keep changes small.
- Keep one purpose per change.
- Prefer several reviewable changes over one large change.

## Source of Truth

- `docs/` = framework definition
- `src/` = implementation
- `setup/` = setup and development rules
- `runs/` = runtime state and generated output

Do not mix responsibilities between these areas.

## When in doubt

- choose the simpler solution
- choose the smaller step
- keep structure explicit
