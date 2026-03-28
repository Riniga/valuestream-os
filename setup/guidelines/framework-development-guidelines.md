# Framework Development Guidelines

This document describes the framework model and repository structure for ValueStream OS.
It is intentionally conceptual.
For coding policy and execution guidance, use `standards.md`.

## Purpose

ValueStream OS is an agent orchestration framework for end-to-end value delivery.
The framework is built around explicit process steps, SOPs, roles, RACI mappings, and artifacts.

The goal is to build working flows first, then improve them iteratively.

## Foundational Principles

- Keep the flow explicit and traceable.
- Model work through process steps, SOPs, roles, and artifacts.
- Use text-based files as the primary system of record.
- Keep orchestration simple and code-driven in the early stages.
- Prefer incremental evolution over large redesigns.

## Repository Model

### `docs/`

Framework definition lives in `docs/`.
This includes:

- process descriptions
- SOPs
- agents
- RACI mappings
- artifact descriptions
- artifact templates

### `src/`

Implementation lives in `src/`.
This includes:

- agents
- orchestration
- capabilities
- runtime/state helpers

### `runs/`

Runtime execution data lives in `runs/`.
This includes:

- input files for a run
- generated output
- logs and execution traces

Runtime data must not become the permanent source of truth for the framework itself.

## Framework Concepts

### Process Steps

The framework is organized as a repeatable process from:

`1. Kravställning -> 2. Målarkitektur -> 3. Roadmap -> 4. Leverans -> 5. Repeat`

Each process step explains what the step is meant to achieve.

### SOPs

SOPs describe how a role or agent performs a specific step.
Each SOP should make the following explicit:

- purpose
- context
- input artifacts
- output artifacts
- RACI
- concrete work steps

### Agents and Roles

Agent definitions are stored under `docs/agents/`.
They describe the role, purpose, and operating instructions for the agent.

### Artifacts

Artifacts are the inputs and outputs used across SOPs.
They are documented in two parts:

- descriptions under `docs/artifacts/descriptions/`
- templates under `docs/artifacts/templates/`

Artifact descriptions explain what an artifact is and why it exists.
Artifact templates define the structure an agent is expected to produce.

## Implementation Direction

- Keep orchestration explicit rather than implicit.
- Start with file-based state before introducing heavier infrastructure.
- Add automation only when the framework structure is already clear.
- Let SOP inputs and outputs drive execution order.
