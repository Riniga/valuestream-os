# Working Mode

This defines how work is performed in the ValueStream OS repository.

The goal is to keep development structured, incremental, and predictable.

---

## Core Flow

All work follows this loop:

1. Define the task
2. Create a plan (with Cursor)
3. Break into TODOs
4. Implement one TODO at a time
5. Verify result
6. Commit
7. Repeat

---

## Using Cursor

### Step 1 — Create a plan

- Use the cursor plan template
- Keep the scope small and clear
- Do not implement yet

### Step 2 — Execute step by step

- Ask Cursor to implement one TODO at a time
- Do not batch multiple steps
- Verify each step before continuing

### Step 3 — Keep control

- Review all changes before accepting
- Ensure structure is preserved
- Ensure no unnecessary complexity is introduced

---

## Change Size

- Keep changes small
- One purpose per change
- Prefer multiple small commits over one large

---

## Source of Truth

- `docs/` = framework definition
- `src/` = implementation
- `setup/` = setup and development rules

Do not mix responsibilities between these.

---

## When in doubt

- Choose the simpler solution
- Choose the smaller step
- Keep structure explicit
