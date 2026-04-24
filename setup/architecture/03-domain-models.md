# Domain Models

This diagram focuses on the shared runtime contracts in `src/framework/models.py`.

Use it when the audience wants to understand what a run actually consists of in memory and on disk.

## Focus

- flow definition
- runtime state
- consultation / approval / informing
- human handoff
- per-step result

## Class diagram

```mermaid
classDiagram
    class AgentDefinition {
        +agent_id
        +agent_file
        +raci_role_id
        +actor_kind
        +display_name
    }

    class FlowStep {
        +step_id
        +agent_id
        +sop_filename
        +artifact_name
        +output_filename
        +input_filenames
        +optional_input_filenames
        +delprocess_title
        +consult_agent_ids
        +approver_agent_id
        +informed_agent_ids
        +use_raci_workflow
    }

    class ProcessFlow {
        +flow_id
        +process_file
        +process_title
        +steps
    }

    class ArtifactRecord {
        +name
        +filename
        +producer_step_id
        +status
        +latest_phase
        +approval_decision
        +pending_human_task_id
    }

    class ArtifactState {
        +run_id
        +artifacts
    }

    class RunState {
        +run_id
        +flow_id
        +process_file
        +status
        +current_step_id
        +current_phase
        +pending_human_task_id
        +step_statuses
    }

    class AgentMemory {
        +agent_id
        +run_id
        +entries
    }

    class ConsultationRequest {
        +request_id
        +step_id
        +artifact_name
        +artifact_filename
        +requester_agent_id
        +consultant_agent_ids
        +questions
    }

    class ConsultationResponse {
        +request_id
        +step_id
        +artifact_name
        +consultant_agent_id
        +response_text
        +summary
    }

    class ApprovalDecision {
        +step_id
        +artifact_name
        +artifact_filename
        +approver_agent_id
        +decision
        +summary
        +rationale
        +changes_requested
    }

    class InformedRoleBrief {
        +step_id
        +artifact_name
        +artifact_filename
        +role_agent_id
        +brief_text
        +relevance
    }

    class ExpertContext {
        +agent_id
        +run_id
        +artifact_name
        +context_text
        +source_filenames
    }

    class HumanTask {
        +task_id
        +step_id
        +artifact_name
        +artifact_filename
        +agent_id
        +role_name
        +phase
        +status
        +request_payload
        +response_payload
    }

    class StepResult {
        +step_id
        +agent_id
        +artifact_name
        +status
        +output_path
        +error
        +phase
        +approval_decision
        +human_task_id
    }

    class StepStatus
    class ArtifactStatus
    class RunStatus
    class ActorKind
    class HumanTaskStatus

    ProcessFlow *-- FlowStep : steps
    ArtifactState *-- ArtifactRecord : artifacts

    FlowStep --> AgentDefinition : uses agent_id
    RunState --> RunStatus : status
    StepResult --> StepStatus : status
    ArtifactRecord --> ArtifactStatus : status
    AgentDefinition --> ActorKind : actor_kind
    HumanTask --> HumanTaskStatus : status

    ConsultationRequest --> FlowStep : for step
    ConsultationResponse --> ConsultationRequest : answers
    ApprovalDecision --> FlowStep : decision for step
    InformedRoleBrief --> FlowStep : brief for step
    HumanTask --> FlowStep : handoff for step
    StepResult --> FlowStep : result of step
```

## Reading guide

- `ProcessFlow` and `FlowStep` define what should happen.
- `RunState` and `ArtifactState` track where the current run is.
- `ConsultationRequest`, `ConsultationResponse`, `ApprovalDecision` and `InformedRoleBrief` make the RACI workflow explicit.
- `HumanTask` represents pauses where work must be completed by a person.
- `StepResult` is the result object emitted by the orchestrator while the flow runs.

## Main source

- [`src/framework/models.py`](../../src/framework/models.py)
