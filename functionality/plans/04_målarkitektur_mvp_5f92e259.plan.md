---
name: 04 målarkitektur mvp
overview: "Implementera stöd för att välja processsteg vid start och köra `2. Målarkitektur` med samma docs-drivna orkestreringsmönster som `1. Kravställning`, utan en separat specialmotor. Planen fokuserar på minsta säkra kodändring: CLI/processval, processladdning, agentregister för nya RACI-roller och tester för ett första körbart flöde."
todos:
  - id: cli-process-select
    content: Inför explicit val av processfil i CLI och använd den i `flow` och `run`
    status: pending
  - id: role-registry
    content: Identifiera minsta agentuppsättning för första Målarkitektur-spåret och uppdatera agentregister vid behov
    status: pending
  - id: process-loader-validation
    content: Verifiera att process_loader och context_loader kan ladda `2. Målarkitektur` utan specialfall; gör endast små blockerande robusthetsfixar
    status: pending
  - id: run-metadata
    content: Avgör om run-state behöver utökas med explicit processfil för bättre spårbarhet
    status: pending
  - id: tests
    content: Lägg till fokuserade tester för processladdning, RACI-resolve och CLI-val för `2. Målarkitektur`
    status: pending
isProject: false
---

# Plan För 04 Målarkitektur MVP

## Mål

Göra befintligt ramverk processstegsvalbart så att en run kan startas mot [src/cli/run.py](src/cli/run.py) med `2. Målarkitektur` som källa, och sedan använda samma laddning av SOP, RACI, artefaktbeskrivningar och mallar som redan används för `1. Kravställning`.

## Viktigaste ändringar

- Inför explicit processval i [src/cli/run.py](src/cli/run.py) och låt både `flow` och `run` skicka vald processfil vidare i stället för att alltid använda `DEFAULT_PROCESS_FILE` från [src/orchestration/process_loader.py](src/orchestration/process_loader.py).
- Håll [src/orchestration/orchestrator.py](src/orchestration/orchestrator.py) generisk: den tar redan `process_flow`; planen är att låta CLI bygga rätt `ProcessFlow` och bara i liten grad komplettera metadata/spårbarhet om det behövs.
- Utöka [src/orchestration/agent_registry.py](src/orchestration/agent_registry.py) med de roller som krävs för första körbara `Målarkitektur`-spåret, eftersom `ProcessFlowLoader` idag annars faller på `_resolve_agent_id()` när SOP:erna nämner roller som ännu inte finns registrerade.
- Verifiera att [src/framework/context_loader.py](src/framework/context_loader.py) klarar nya artefaktnamn och mallar utan specialfall. Om nödvändigt, gör en liten robusthetsändring för namnmatchning, men bara om ett faktiskt test visar behov.
- Lägg till fokuserade tester i [tests/orchestration/test_process_loader.py](tests/orchestration/test_process_loader.py) för att bevisa att `2. Målarkitektur` kan laddas, att steg genereras från dess outputs och att RACI-roller kan mappas för det valda MVP-spåret.

## Genomförande

1. Börja i CLI-lagret.
   Uppdatera [src/cli/run.py](src/cli/run.py) så att användaren kan ange processfil, lämpligen som en explicit parameter som används av både `flow` och `run`. Målet är att ersätta hårdkodningen här:

```126:137:src/cli/run.py
async def _cmd_run_async(workspace: RunWorkspace, repo_root: Path, dry_run: bool) -> None:
    process_flow = ProcessFlowLoader(repo_root).load(DEFAULT_PROCESS_FILE)
    total = len(process_flow.steps)
    mode = " (dry-run)" if dry_run else ""
    print(f"\nKör flöde: {process_flow.flow_id}{mode}  ({total} steg)")
    print("─" * CONSOLE_WIDTH)

    orchestrator = Orchestrator(workspace=workspace, repo_root=repo_root, process_flow=process_flow)
```

1. Behåll processladdaren som centrum för generalisering.
   [src/orchestration/process_loader.py](src/orchestration/process_loader.py) är redan nästan processagnostisk. Planen är att fortsätta använda `load(process_file)` och endast justera sådant som blockerar `2. Målarkitektur`, inte att bygga en ny loader.

```42:61:src/orchestration/process_loader.py
def load(self, process_file: str = DEFAULT_PROCESS_FILE) -> ProcessFlow:
    path = self._processes_root / process_file
    content = path.read_text(encoding="utf-8")
    sections = self._parse_sections(content)
    steps: list[FlowStep] = []

    for section in sections:
        sop = self._context_loader.load_sop(section.sop_filename)
        agent_id = self._resolve_agent_id(self._extract_raci_roles(sop.content, "R"))
        ...
        for output_name in sop.outputs:
            template_path = self._context_loader.find_template_path(output_name)
            if template_path is None:
                continue
```

1. Definiera minsta rolluppsättning för första `Målarkitektur`-flödet.
   Utgå från SOP:erna i [docs/SOP/2. Målarkitektur](docs/SOP/2.%20Målarkitektur) och lägg bara till de agenter som verkligen behövs för första körbara spår. Trolig minsta uppsättning är att komplettera befintlig `losningsarkitekt` med saknade roller som `enterprise-arkitekt`, `teknisk-lead`, `dataarkitekt` och eventuellt `devops`, tillsammans med motsvarande agentdokument under `docs/agents/` om de saknas.
2. Verifiera spårbarhet i run-state.
   [src/orchestration/orchestrator.py](src/orchestration/orchestrator.py) initierar idag `RunState` med `flow_id` och `step_ids`, men inte explicit processfil. Om det behövs för tydlighet i `status` och framtida återupptagning, lägg till minsta metadatautökning i modeller/store så att valt processsteg framgår i runnen. Detta är sekundärt efter att processvalet faktiskt fungerar.
3. Lägg till fokuserade tester före eller tillsammans med implementationen.
   Bygg vidare på [tests/orchestration/test_process_loader.py](tests/orchestration/test_process_loader.py), som idag bara säkrar `1. Kravställning`. Lägg till tester som verifierar:

- att `ProcessFlowLoader(...).load("2. Målarkitektur.md")` fungerar
- att minst ett förväntat outputsteg skapas från steg 2
- att de RACI-roller som behövs i MVP-spåret går att resolva
- att CLI/processvalet använder vald processfil i stället för default

## Avgränsning För Första Leveransen

- Ingen full parallellisering av `Målarkitektur`-grenarna.
- Ingen total utbyggnad av alla möjliga roller om de inte behövs för första körbara spåret.
- Ingen ny speciallogik per artefakt; problem ska i första hand lösas via befintlig docs-driven laddning och små robusthetsfixar.

## Verifiering

- Kör eller uppdatera enhetstesterna i [tests/orchestration/test_process_loader.py](tests/orchestration/test_process_loader.py).
- Kontrollera att `flow` mot `2. Målarkitektur.md` visar en rimlig steglista.
- Kontrollera att en `dry-run` kan startas med valt processsteg utan att falla på processladdning eller agentupplösning.
- Bekräfta att `status` eller run-state tydligt visar vilken process som kördes, om metadatautökningen tas med i implementationen.
