# Architecture Diagrams for `src/`

This folder contains presentation-friendly architecture documentation for the implementation under `src/`.

The diagrams focus on the runtime orchestration path:

- how the CLI enters the system
- how the framework in markdown is loaded into executable steps
- how orchestration runs and persists state
- how output is published for inspection

`src/normalize/` is intentionally excluded from these diagrams because it is not part of the main runtime orchestration path.

## Why several diagrams?

One large class diagram quickly becomes hard to read in a live walkthrough.

This documentation therefore uses:

- one simplified overview without fields and methods
- one more detailed class diagram for the orchestration core
- one focused diagram for runtime contracts
- one focused diagram for persistence and output publishing

## Diagram index

1. [`01-overview.md`](./01-overview.md)
   - Big-picture runtime view
   - Best first stop in a demo

2. [`02-runtime-detail.md`](./02-runtime-detail.md)
   - Detailed class diagram with selected attributes and methods
   - Best when someone asks "how is this actually wired?"

3. [`03-domain-models.md`](./03-domain-models.md)
   - Core dataclasses and enums from `src/framework/models.py`
   - Best for explaining run state, artifacts and handoffs

4. [`04-persistence-and-output.md`](./04-persistence-and-output.md)
   - File-backed stores and output index publishing
   - Best for explaining transparency and traceability

## Suggested presentation order

1. Start with [`01-overview.md`](./01-overview.md)
2. Jump to [`02-runtime-detail.md`](./02-runtime-detail.md)
3. Use [`03-domain-models.md`](./03-domain-models.md) if the audience asks about runtime state
4. Use [`04-persistence-and-output.md`](./04-persistence-and-output.md) if the audience asks about traceability or run files

## Source references

Main code paths visualized here:

- [`src/cli/run.py`](../../src/cli/run.py)
- [`src/orchestration/orchestrator.py`](../../src/orchestration/orchestrator.py)
- [`src/orchestration/process_loader.py`](../../src/orchestration/process_loader.py)
- [`src/orchestration/agent_registry.py`](../../src/orchestration/agent_registry.py)
- [`src/framework/context_loader.py`](../../src/framework/context_loader.py)
- [`src/framework/maf_adapter.py`](../../src/framework/maf_adapter.py)
- [`src/framework/models.py`](../../src/framework/models.py)
- [`src/framework/stores.py`](../../src/framework/stores.py)
- [`src/orchestration/output_index.py`](../../src/orchestration/output_index.py)
