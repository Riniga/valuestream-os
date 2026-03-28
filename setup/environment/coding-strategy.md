# Coding Strategy

this document describes how I develop code using AI tools.

## Goal

All code must be easy to understand, maintain, and safely change over time.
Maintainability is the primary priority, while correctness of functionality is mandatory.
Unnecessary complexity is never acceptable.

## Principles (In development mode)

All deliverys should always comply to S.O.L.I.D principles
Any code reused twice is unit tested
Blocks that could be isolated should be seprated into modules
Code that is reused in modules should be in a common library

## 5 Development Principles

- Follow SOLID principles in all design and implementation.
- Prefer clear and readable code over clever solutions.
- Logic that can be independently understood, tested, or reused must be separated into its own module.
- Eliminate duplication through shared components and libraries.
- Unit test all reusable logic.

## Coding workflow

1. Define a finite and minimal functionality and store it under `mvp/functionality` using the name `<nn>-<functionality>`.
2. Use ChatGPT to create the supporting specification: description, definition of done, user stories, and non-functional requirements.
3. Create a new branch named `feat-<nn>-<functionality>`.
4. Use the specification to create a Cursor plan and store it under `plans`.
5. Implement the functionality step by step using either:
   - Claude Code
   - Cursor Build based on the plan
6. Review the code using the Review Agent and the review documentation, or do it your self, to be sure...
7. Commit and push the changes.
8. When pleased. merge branch and let deployment pipline handle integration tests, and deployment to UAT and production
9. When approved, merge the branch and let the deployment pipeline handle integration tests and deployment according to the deployment strategy.

## Branching strategy

We use a simple feature branch strategy based on a single main branch.

- `main` is always production-ready and protected, no commits to `main` are not allowed.
- All development is done in short-lived feature branches created from `main`.
- Branch naming must follow: `<nn>-<functionality>`.
- Merges to `main` should be done using pull requests.
- Delete branches after merge to keep the repository clean.

## Deployment strategy

We use a controlled pipeline-based deployment strategy with manual approval for release decisions.

- All deployments are triggered from `main`.
- Deployment to UAT environment is handled by the deployment pipeline.
- Production deployment must always be explicitly approved after validation.
- Rollback must be possible if a deployment fails or causes unexpected issues.

## Coding Tools

Cursor
Claude Code - Within a Cursor Terminal

## Models

For planing in Cursor use GPT-5.1 High
For execution: Sonnet 4.6
Whisper - För demo eller för att viba lite lugnt
Ultrathink: lägg till ultrathink i claude code to get better result (kan fungera i sonnet också?)
MCP-Servers context7 (för dokumentation) and supabase (setup projects from scratch)
Bug Bot in github to review code on
