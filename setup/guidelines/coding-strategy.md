# Coding Strategy

This document is the primary development guideline for AI-assisted coding in the ValueStream OS repository.
If another guideline conflicts with this one, this document takes precedence.

## Goal

All code must be easy to understand, maintain, and safely change over time.
Correctness is mandatory. Maintainability is the primary design priority.
Unnecessary complexity is never acceptable.

## Core Principles

- Follow SOLID principles when they improve clarity and separation of responsibility.
- Prefer clear and readable code over clever solutions.
- Logic that can be independently understood, tested, or reused should be separated into its own module.
- Remove duplication through shared modules or libraries when the duplication is real and recurring.
- Unit test reusable logic and code with meaningful branching or transformation.

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

## Branching Strategy

- `main` is protected and must remain production-ready.
- Development happens in short-lived feature branches created from `main`.
- Branch names must follow `<nn>-<functionality>`.
- Changes are merged to `main` through pull requests.
- Delete merged branches to keep the repository clean.

## Deployment Strategy

- Deployments are triggered from `main`.
- UAT deployment is handled by the deployment pipeline.
- Production deployment must be explicitly approved after validation.
- Rollback must be possible if a deployment fails or causes unexpected issues.

## Recommended Tools

- Cursor for planning, implementation, and review support
- Claude Code from a Cursor terminal when a second implementation agent is helpful
- Context7 for external documentation lookup when needed
- GitHub review tooling for final review support

## General Decision Rule

When in doubt:

- choose the simpler design
- choose the smaller step
- choose the more explicit structure
