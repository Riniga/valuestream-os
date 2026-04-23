# ValueStream OS Framework – Central Index

Denna guide är din entrépunkt för att förstå och använda ValueStream OS-ramverket. Ramverket definierar roller, processer, artefakter och RACI-matriser för att driva produktutveckling från krav till leverans i en repetérbar, skalbar cirkulär modell.

---

## 🚀 Quick Navigation by Role

### I'm a...

| Rolle                  | Börja här                                                  | Andra viktiga resurser                                                                        |
| ---------------------- | ---------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **Business Analyst**   | [Kravställning Process](./processes/1.%20Kravställning.md) | [RACI för Kravställning](./RACI/1.%20Kravställning.md) \| [SOP Guides](./SOP/)                |
| **Product Owner**      | [RACI Matrix](./RACI/RACI.md)                              | [Målarkitektur](./processes/2.%20Målarkitektur.md) \| [Prioritering](./artifacts/)            |
| **Solution Architect** | [Målarkitektur Process](./processes/2.%20Målarkitektur.md) | [RACI för Målarkitektur](./RACI/2.%20Målarkitektur.md) \| [Artefakter](./artifacts/)          |
| **Developer**          | [SOP & Tekniska Guider](./SOP/)                            | [Tekniska Specifikationer](./processes/2.%20Målarkitektur.md) \| [Capabilities](./artifacts/) |
| **UX Designer**        | [User Journeys & Behov](./artifacts/)                      | [Kravställning](./processes/1.%20Kravställning.md) \| [Story Maps](./artifacts/)              |
| **Project Manager**    | [Process Overview](./processes/Process.md)                 | [Alla RACI-matriser](./RACI/) \| [Roadmap](./processes/3.%20Roadmap.md)                       |

---

## 📊 The 5-Step Circular Process

ValueStream OS organizes work into five interconnected phases that repeat in a cycle:

### 1. 🎯 Kravställning (WHAT)

Define business needs, user stories, and requirements.

- **What:** Understand what we need to build
- **Artifacts:** User stories, epics, vision, scope, stakeholder maps
- **RACI:** [Kravställning Responsibilities](./RACI/1.%20Kravställning.md)
- **Details:** [View full process](./processes/1.%20Kravställning.md)

### 2. 🏗️ Målarkitektur (HOW)

Design the target architecture and system solutions.

- **What:** How should the solution be structured?
- **Artifacts:** Architecture goals, system landscape, data models
- **RACI:** [Målarkitektur Responsibilities](./RACI/2.%20Målarkitektur.md)
- **Details:** [View full process](./processes/2.%20Målarkitektur.md)

### 3. 📅 Roadmap (WHEN)

Plan the sequence and timeline for delivery.

- **What:** When will features be released?
- **Artifacts:** Release roadmap, sequencing decisions
- **RACI:** [Roadmap Responsibilities](./RACI/3.%20Roadmap.md)
- **Details:** [View full process](./processes/3.%20Roadmap.md)

### 4. 🚀 Leverans (BUILD)

Build, test, and release the solution.

- **What:** How do we build and launch?
- **Artifacts:** Build plans, test results, release notes
- **RACI:** [Leverans Responsibilities](./RACI/4.%20Leverans.md)
- **Details:** [View full process](./processes/4.%20Leverans.md)

### 5. 🔄 Repeat (LEARN)

Reflect on results and adjust for the next iteration.

- **What:** What did we learn?
- **Artifacts:** Retrospectives, lessons learned, next iteration plan
- **RACI:** [Repeat Responsibilities](./RACI/5.%20Repeat.md)
- **Details:** [View full process](./processes/5.%20Repeat.md)

**🔁 Then the cycle repeats** → Return to Phase 1 with new learnings

---

## 📁 Framework Structure

Utforska ramverket enligt katalog:

### [📋 agents/](./agents/) – Roller i Systemet

Beskrivningar av alla roller: Business Analyst, Solution Architect, Developer, UX Designer, Product Owner, Project Manager, och fler.

**Snabblänk:** [Alla roller](./agents/)

### [⚙️ processes/](./processes/) – De 5 Processerna

Steg-för-steg processdefinitioner för varje fas (Kravställning → Målarkitektur → Roadmap → Leverans → Repeat).

**Snabblänk:** [Process Overview](./processes/Process.md)

### [📊 RACI/](./RACI/) – Ansvarsmatriser

För varje process: Vem är Ansvarig, Accountable, Consulted, och Informed?

**Snabblänk:** [RACI Main](./RACI/RACI.md)

### [📖 SOP/](./SOP/) – Standard Operating Procedures

Detaljerade how-to guider för varje aktivitet. Börja här för praktiska instruktioner.

**Snabblänk:** [SOP Overview](./SOP/sop-conventions-discovery.md)

### [🎁 artifacts/](./artifacts/) – Artefakter & Mallar

Beskrivningar av all indata och output från ramverket. Innehåller också mallar för att skapa nya artefakter.

**Snabblänk:** [Artifacts Overview](./artifacts/Artifacts.md)

---

## 📚 Glossary – Key Terms

### Core Framework Concepts

| Term           | Definition                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------ |
| **Agent**      | En roll som exekverar aktiviteter i ramverket (t.ex. Business Analyst, Solution Architect) |
| **RACI**       | Responsible, Accountable, Consulted, Informed – ansvarsbeslutningsmatris                   |
| **Artifact**   | En output/leverabel från en process-fas (t.ex. user stories, architecture diagram)         |
| **Capability** | En affärsfunktion eller systemkapabilitet som kan levereras                                |
| **Epic**       | En stor gruppering av relaterade user stories                                              |

### Process & Requirements

| Term                      | Definition                                                                                                   |
| ------------------------- | ------------------------------------------------------------------------------------------------------------ |
| **Kravställning**         | Fas 1: Define requirements (WHAT do we need?)                                                                |
| **User Story**            | En kortfattad beskrivning av en användares behov i formatet "As a [role], I want [feature], so that [value]" |
| **Vision & Målbild**      | En övergripande beskrivning av önskningsvärt framtida tillstånd                                              |
| **Scope & Avgränsningar** | Vad är IN-scope och vad är OUT-of-scope för ett initiativ?                                                   |

### Architecture & Design

| Term               | Definition                                                  |
| ------------------ | ----------------------------------------------------------- |
| **Målarkitektur**  | Fas 2: Design target architecture (HOW should it be built?) |
| **Systemlandskap** | En visualisering av alla system och deras relationer        |
| **Domänmodell**    | En konceptuell modell av affärsdomänen och dess enheter     |

### Execution & Lifecycle

| Term           | Definition                                                             |
| -------------- | ---------------------------------------------------------------------- |
| **Roadmap**    | Fas 3: Plan sequencing and releases (WHEN will features ship?)         |
| **Leverans**   | Fas 4: Build, test, release the solution                               |
| **Repeat**     | Fas 5: Reflect and adjust for next iteration                           |
| **Spårbarhet** | Ability to trace from business need → requirement → solution → release |

👉 **[Se full glossarie](./GLOSSARY.md)**

---

## 📖 How to Use This Framework

### Scenario 1: Starting a New Product Initiative

1. **Read:** [Process Overview](./processes/Process.md) (5 min)
2. **Execute Phase 1:** [Kravställning](./processes/1.%20Kravställning.md) (detailed step-by-step)
3. **Who does what?** Check [RACI for Kravställning](./RACI/1.%20Kravställning.md)
4. **Create artifacts:** Use [SOP Guides](./SOP/1.Kravställning/) and [Templates](./artifacts/templates/)
5. **Share results:** Outputs feed into Phase 2 (Målarkitektur)

### Scenario 2: Reviewing an Architecture Decision

1. Review: [Målarkitektur Process](./processes/2.%20Målarkitektur.md)
2. Check: [RACI for Målarkitektur](./RACI/2.%20Målarkitektur.md)
3. Examine: [Artifact descriptions](./artifacts/descriptions/2.%20Målarkitektur/)
4. Validate: Are all required artifacts present? Are they complete?

### Scenario 3: Finding Your Role's Responsibilities

1. Find your role: [Role Descriptions](./agents/)
2. See which phases you're Responsible/Accountable for
3. Review those [RACI matrices](./RACI/)
4. Read detailed [SOP guides](./SOP/) for your activities

### Scenario 4: Looking Up a Specific Artifact

1. Check: [Artifacts Overview](./artifacts/Artifacts.md)
2. Find your artifact in the dependency diagram
3. Read: [Artifact Description](./artifacts/descriptions/)
4. Use: [Template](./artifacts/templates/) to create your own

---

## 🎯 Framework Principles

- **Circular & Iterative** – Phases repeat in a cycle; each cycle incorporates learnings from the previous
- **Role-Based** – Clear responsibilities defined via RACI matrices (Responsible, Accountable, Consulted, Informed)
- **Artifact-Driven** – Each phase produces defined, tangible deliverables
- **Scalable** – Works for small team initiatives and large enterprise programs
- **Traceability** – Every artifact links back to the business need that triggered it
- **Transparent** – Open documentation allows anyone to understand the process

---

## 🔮 About Framework Variants

ValueStream OS is designed to support multiple variants for different contexts:

- **framework/standard/** – Full framework with all roles, processes, SOPs (current, this directory)
- **framework/light/** – Lightweight variant optimized for smaller teams (coming soon)

Future variants might focus on specific industries, organization types, or delivery methods. The directory structure allows multiple variants to coexist without collision.

[Learn more about framework variants →](../Roadmap.md)

---

## ❓ Getting Help

**Can't find what you're looking for?**

- Search by role: Start with [role descriptions](./agents/)
- Search by process: Browse the [5 process phases](./processes/Process.md)
- Search by artifact: Check [artifacts overview](./artifacts/Artifacts.md)
- Need a detailed how-to? Consult the [SOP guides](./SOP/)
- Looking for shared execution results? See the separate data repository `../valuestream-os-data`

**Want to give feedback?**

This framework evolves based on real-world use. Suggestions and improvements are welcome!

---

## 📝 Framework Metadata

| Property           | Value                                             |
| ------------------ | ------------------------------------------------- |
| **Framework Name** | ValueStream OS                                    |
| **Version**        | 1.0                                               |
| **Last Updated**   | 2026-04-01                                        |
| **Language**       | Swedish (frameworkdokumentation) / English (code) |
| **Variant**        | standard (full framework)                         |

---

**👈 Back to [Home](.)** | **📖 Read [Process Overview](./processes/Process.md)** | **🎯 Find [Your Role](./agents/)**

_Framework documentation is living documentation. It evolves as we learn how to better organize and deliver products._
