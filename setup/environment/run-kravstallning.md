# Run Kravstallning Orchestration

This guide describes how to run the first Kravstallning orchestration slice and what files are expected and produced.

## Prerequisites

- Development environment is set up (see `setup/environment/development-environment.md`).
- Python commands are run from repository root.

## Required run input

Create a run folder with the required input artifact:

```text
runs/<run-id>/
  input/
    overgripande_behov.md
```

`overgripande_behov.md` is required by the Business Analyst agent.  
If it is missing, the CLI exits with a non-zero status and prints missing artifacts.

## Command usage

Run a full orchestration:

```powershell
python -m src.cli.run_kravstallning --run-id demo-001
```

Validate setup and required inputs only (no orchestration execution):

```powershell
python -m src.cli.run_kravstallning --run-id demo-001 --dry-run
```

## Run folder contract

The CLI initializes missing folders automatically:

```text
runs/<run-id>/
  input/
  work/
  output/
  logs/
```

## Expected artifacts and state after execution

On a successful run (approved outputs), the following files are expected:

- `work/state.json`
  - Includes run-level status (`initialized`, `in_review`, `approved`, or `changes_requested`)
  - Includes `artifact_reviews` with reviewer decision per artifact
- `work/lineage.json`
  - Stores per-artifact lineage (`source_files`, `produced_by`, `review_status`, timestamp)
- `work/vision_malbild.md`
  - Produced by Business Analyst from `input/overgripande_behov.md`
- `work/ux_koncept.md`
  - Produced by UX from `work/vision_malbild.md`
- `output/vision_malbild.md` and `output/ux_koncept.md`
  - Published only when Product Owner review status is `approved`
- `logs/step_log.md`
  - Ordered execution log of orchestration steps and review results
- `logs/notifications.md`
  - Inform-role notifications emitted after approved publication

## Conditional support-role artifacts

When unresolved assumptions are detected in `overgripande_behov.md`, the Business Analyst asks support roles and these files are created:

- `work/qa_log.md`
- `work/support_responses.json`

## Quick verification checklist

After running:

1. Confirm `runs/<run-id>/work/state.json` exists.
2. Confirm `status` in `state.json` is set by Product Owner review.
3. Confirm at least one approved artifact exists in `runs/<run-id>/output/`.
4. Confirm `runs/<run-id>/work/lineage.json` references input and producer metadata.
5. Confirm `runs/<run-id>/logs/step_log.md` exists with recorded steps.
