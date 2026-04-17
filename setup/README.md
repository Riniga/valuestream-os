# ⚙️ Setup & Development

This folder contains everything needed to **set up, run, and contribute** to the ValueStream OS project.

It is intentionally separated from the framework content to distinguish between:

- **What the framework is** → `framework/`
- **How to run and build it** → `setup/`

---

## 📁 Structure
```
setup/
├── environment/ → Runtime and environment setup
├── guidelines/ → Development principles and instructions
```

---

## 🧪 Environment

Located in: `setup/environment/`

Contains:
- `development-environment.md` → How to install and configure the project
- `.env.example` → Example environment variables

👉 Start here if you want to **run the project locally**

---

## 📘 Guidelines

Located in: `setup/guidelines/`

Contains:
- `standards.md` → Primary coding policy, execution flow and repository conventions
- `framework-development-guidelines.md` → Conceptual framework model and structure

These documents describe:
- How the framework should evolve  
- How to structure work  
- How agents, SOPs and processes should be designed  

👉 Read this if you want to **contribute or extend the framework**

---

## 🚀 Getting Started

1. Set up your environment:
   - Follow `environment/development-environment.md`
   - Run `pwsh ./scripts/bootstrap.ps1` to create the `valuestream-os` conda environment
   - Copy `setup/environment/.env.example` to `.env` and fill in your LLM credentials

2. Understand how to work in the project:
   - Read `guidelines/standards.md`
   - Read `guidelines/framework-development-guidelines.md`

3. Explore the framework itself:
   - Start in `/framework/standard/INDEX.md`

---

## Köra orkestreringen

Kör via `src.cli.run` från repots rot (med `valuestream-os` conda-miljö aktiv):

```powershell
# Visa det processdrivna flödet (steg, agenter, artefakter)
python -m src.cli.run --run-id demo-001 flow

# Lista registrerade agenter
python -m src.cli.run --run-id demo-001 agents

# Kör hela flödet med LLM-anrop
python -m src.cli.run --run-id demo-001 run

# Kör utan LLM-anrop — skriver prompts till output/ för inspektion
python -m src.cli.run --run-id demo-001 run --dry-run

# Visa körningens status (stegstatus, artefakter)
python -m src.cli.run --run-id demo-001 status
```

Input-filer placeras i `runs/<run-id>/input/`. Output hamnar i `runs/<run-id>/output/`.
Körlogg och state sparas i `runs/<run-id>/`.

`runs/` är en lokal arbetsyta för runtime och ska inte versionshanteras i detta repo.

Om du vill dela eller publicera körningsresultat görs det i det separata syskonrepot `../valuestream-os-data`.

### Mänsklig interaktion i körningar

Vissa roller kan vara mänskliga i stället för automatiska LLM-agenter, till exempel `Beställare`.
När orkestreringen når ett sådant steg pausas körningen och en human task skapas under:

`runs/<run-id>/human_tasks/`

Använd följande kommandon för att se och slutföra mänskliga uppgifter:

```powershell
# Lista alla mänskliga uppgifter för en körning
python -m src.cli.run --run-id test-01 human-tasks

# Slutför en mänsklig uppgift med en fil som redan finns på disk
python -m src.cli.run --run-id test-01 complete-human-task 1-kravstallning-01-bestallning-draft-bestallare --artifact-file runs/test-01/input/beställning.md

# Slutför en mänsklig uppgift med inline-text (bra för kort feedback eller svar)
python -m src.cli.run --run-id test-01 complete-human-task 1-kravstallning-01-bestallning-draft-bestallare --artifact-content "# Beställning`n`n..."

# Fortsätt körningen efter att uppgiften markerats som completed
python -m src.cli.run --run-id test-01 run
```

Praktiska regler:

- För filproducerande mänskliga steg, som `Beställning`, är `--artifact-file` det rekommenderade sättet.
- För mänsklig återkoppling, frågor eller godkännanden används task-filen eller CLI-parametrar som `--response-text`, `--decision`, `--summary` och `--rationale`.
- Om du redigerar JSON-filen manuellt måste toppnivåfältet `status` sättas till `completed`. Det räcker inte att sätta `response_payload.status`.
- För mänskliga filsteg kan systemet även återuppta från en redan upplagd fil i `runs/<run-id>/input/` eller `runs/<run-id>/output/`, så länge tasken själv är markerad som `completed`.
- Körningens aktuella läge kan alltid ses med `python -m src.cli.run --run-id <run-id> status`.

Körtester (kräver ej LLM):
```powershell
python -m pytest tests/ -v
```

---

## 🧠 Philosophy

This project is built on a clear separation:

| Area | Purpose |
|------|--------|
| `framework/` | Defines the process, roles, SOPs, artifacts and framework variants |
| `setup/` | Defines how to run and develop the system |
| `src/` | Implements execution (agents, orchestration, capabilities) |
| `runs/` | Local private runtime state created by orchestrator runs |

---

## 🤝 Contributing

Before contributing:
- Read the guidelines
- Understand the process model in `/framework/standard`

This ensures consistency and keeps the framework scalable over time.
