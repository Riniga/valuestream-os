# Runtime Detail

This diagram adds selected attributes and methods for the core runtime classes.

Use it when you want to show how the orchestration is wired in code, not just conceptually.

## Scope

This is intentionally focused on the orchestration core:

- `RunWorkspace`
- `ProcessFlowLoader`
- `AgentContextLoader`
- `FrameworkPromptBuilder`
- `AgentRunner`
- `Orchestrator`

## Detailed class diagram

```mermaid
classDiagram
    class RunWorkspace {
        +str run_id
        +Path repo_root
        +Path run_dir
        +Path input_dir
        +Path output_dir
        +Path human_tasks_dir
        +validate_input(required_files) list~str~
        +read_input(filename) str
        +read_output(filename) str
        +output_exists(filename) bool
        +write_output(filename, content) Path
        +input_path(filename) Path
        +output_path(filename) Path
    }

    class ProcessFlowLoader {
        -Path _repo_root
        -Path _framework_root
        -Path _processes_root
        -dict _agent_definitions
        -dict _raci_role_index
        -AgentContextLoader _context_loader
        +load(process_file) ProcessFlow
    }

    class AgentContextLoader {
        +Path repo_root
        +Path framework_root
        +str agent_file
        +str role_name
        +str raci_role
        +load_role() str
        +load_agent_instructions() str
        +load_agent_purpose() str
        +load_sops_for_role() list~SopEntry~
        +load_sop(filename) SopEntry
        +load_artifact_description(name) str
        +load_artifact_template(filename) str
        +find_template_path(name) Path
        +find_description_path(name) Path
    }

    class FrameworkPromptBuilder {
        +build_generate_prompt(...) str
        +build_update_prompt(...) str
        +build_consultation_prompt(...) str
        +build_revision_prompt(...) str
        +build_approval_prompt(...) str
        +build_informing_prompt(...) str
        +build_expert_context_text(...) str
    }

    class AgentRunner {
        -str _name
        -str _instructions
        -object _client
        +run(prompt) str
        +run_async(prompt) str
    }

    class Orchestrator {
        -RunWorkspace _workspace
        -Path _repo_root
        -dict _agents
        -ProcessFlow _process_flow
        -list~FlowStep~ _steps
        -FrameworkPromptBuilder _prompt_builder
        +run(dry_run) list~StepResult~
        +run_async(dry_run) list~StepResult~
        +run_stream_async(dry_run) AsyncGenerator~StepResult~
    }

    class ProcessFlow
    class FlowStep
    class SopEntry
    class StepResult
    class Stores["RunStateStore + ArtifactStateStore + ConsultationStore + ApprovalStore + InformedRoleBriefStore + ExpertContextStore + HumanTaskStore + RunLog"]

    ProcessFlowLoader --> AgentContextLoader : loads SOPs and artifacts
    ProcessFlowLoader --> ProcessFlow : builds
    ProcessFlow --> FlowStep : contains
    AgentContextLoader --> SopEntry : returns

    Orchestrator --> RunWorkspace : uses
    Orchestrator --> ProcessFlow : executes
    Orchestrator --> FlowStep : iterates
    Orchestrator --> AgentContextLoader : builds step context
    Orchestrator --> FrameworkPromptBuilder : builds prompts
    Orchestrator --> AgentRunner : invokes LLM step
    Orchestrator --> Stores : persists runtime state
    Orchestrator --> StepResult : yields
```

## Key explanation points

- `ProcessFlowLoader` is the bridge from markdown framework definitions to executable flow objects.
- `AgentContextLoader` reads role descriptions, SOPs, artifact templates and artifact descriptions from the framework.
- `FrameworkPromptBuilder` turns loaded framework context into prompts for different phases.
- `AgentRunner` isolates Microsoft Agent Framework and provider configuration behind one thin runtime boundary.
- `Orchestrator` is the composition root for execution, state updates, pauses and output publishing.

## Good source links to open beside this

- [`src/orchestration/orchestrator.py`](../../src/orchestration/orchestrator.py)
- [`src/orchestration/process_loader.py`](../../src/orchestration/process_loader.py)
- [`src/framework/context_loader.py`](../../src/framework/context_loader.py)
- [`src/framework/prompt_builder.py`](../../src/framework/prompt_builder.py)
- [`src/framework/maf_adapter.py`](../../src/framework/maf_adapter.py)
