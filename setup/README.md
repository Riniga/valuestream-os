# ⚙️ Setup & Development

This folder contains everything needed to **set up, run, and contribute** to the ValueStream OS project.

It is intentionally separated from `docs/` to distinguish between:

- **What the framework is** → `docs/`
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
- `framework-development-guidelines.md` → Core principles for developing the framework

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
   - Read `guidelines/framework-development-guidelines.md`

3. Explore the framework itself:
   - Go to `/docs`

---

## Business Analyst Agent

Kör BA-agenten via terminal från repots rot (med `valuestream-os` conda-miljö aktiv):

```powershell
# Visa vilka SOP:er och artefakter BA ansvarar för
python -m src.cli.ba --run-id demo-001 list

# Generera en artefakt med LLM
python -m src.cli.ba --run-id demo-001 generate
python -m src.cli.ba --run-id demo-001 generate --artifact scope_och_avgransningar.md

# Uppdatera en redan genererad artefakt
python -m src.cli.ba --run-id demo-001 update --artifact vision_och_malbild.md

# Testa utan LLM-anrop (inspektera prompten)
python -m src.cli.ba --run-id demo-001 generate --dry-run
```

Input-filer placeras i `runs/<run-id>/input/`. Output hamnar i `runs/<run-id>/output/`.
Spårbarhet loggas i `runs/<run-id>/run_log.json`.

Körtester (kräver ej LLM):
```powershell
python -m pytest tests/ -v
```

---

## 🧠 Philosophy

This project is built on a clear separation:

| Area | Purpose |
|------|--------|
| `docs/` | Defines the process, roles, SOPs and artifacts |
| `setup/` | Defines how to run and develop the system |
| `src/` | Implements execution (agents, orchestration, capabilities) |

---

## 🤝 Contributing

Before contributing:
- Read the guidelines  
- Understand the process model in `/docs`  

This ensures consistency and keeps the framework scalable over time.
