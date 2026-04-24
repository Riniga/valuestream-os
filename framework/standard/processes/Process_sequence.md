## Processflöde

Detta sekvensdiagram visar **hur en run faktiskt exekveras i dagens lösning**.

Fokus här är inte en idealiserad persona-kedja, utan hur:

- en användare startar en körning
- process och SOP:er laddas från `framework/standard`
- orchestration kör steg för steg
- roller konsulteras och godkänner vid behov
- state, logg och output sparas i `runs/`

```mermaid
sequenceDiagram
    participant U as Beställare / användare
    participant CLI as CLI
    participant PFL as ProcessFlowLoader
    participant FW as framework/standard
    participant O as Orchestrator
    participant RR as Ansvarig roll / agent
    participant CR as Konsulterande roller
    participant AR as A-roll / godkännare
    participant RUN as runs/<run-id>

    U->>CLI: Starta run med input
    CLI->>PFL: load(process_file)
    PFL->>FW: Läs process, SOP, RACI och artefaktmallar
    FW-->>PFL: ProcessFlow + FlowSteps
    CLI->>O: Kör flödet för aktuell run
    O->>RUN: Initiera run_state, artifact_state och run_log

    loop För varje processsteg
        O->>O: Validera input och välj nästa steg
        O->>RR: Bygg prompt och kör ansvarig roll
        RR-->>O: Utkast / artefakt
        O->>RUN: Spara output och uppdatera state

        alt Steget använder RACI-flöde
            O->>CR: Skicka konsultationsunderlag
            CR-->>O: Återkoppling
            O->>RR: Begär revidering
            RR-->>O: Reviderad artefakt

            opt A-roll finns
                O->>AR: Begär beslut / godkännande
                AR-->>O: approved / approved_with_notes / rejected
            end

            O->>RUN: Spara consultations, approvals och briefs
        end

        alt Mänsklig uppgift krävs
            O->>RUN: Skapa human_tasks/*.json
            O-->>CLI: Pausa körningen
            U->>CLI: complete-human-task
            CLI->>O: Återuppta run
        end

        O->>RUN: Publicera eller uppdatera output/INDEX.md
    end

    CLI-->>U: Visa status, resultat och nästa steg
```

## Att tänka på i presentation

- Diagrammet visar **runtime-flödet**, inte hela organisationssamspelet.
- Roller som `Business Analyst`, `UX` eller `Lösningsarkitekt` uppträder här som **ansvariga eller konsulterande roller i ett steg**.
- Samma struktur kan användas både för automatiserade agentroller och för mänskliga handoffs.
- `runs/<run-id>` är navet för spårbarhet: input, output, state, logg, approvals och human tasks.
