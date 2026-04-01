# Implementeringsplan: MVP 05 – Accessibility & Landing Pages

## Mål

Implementera två markdown-baserade landningssidor som gör ramverket och körningsresultaten lätta att navigera för stakeholders. Omstrukturera `docs/` → `framework/standard/` för framtida mvp-varianter. Förbered separation av `runs/` till externt repo (implementationsdelen senare).

**Styrande dokument:** [functionality/mvp/05-accessibility-landing-pages.md](./05-accessibility-landing-pages.md)

---

## Systemflöde

```
Phase 1: Analys & Förberedelse
  ├─ Kartlägg docs-struktur
  ├─ Identifiera glossary-termer & personas
  └─ Verifiera externos repo-setup

Phase 2: Refaktorering (docs → framework/standard)
  ├─ Skapa framework/standard directory
  ├─ Kopiera alla docs-innehål
  ├─ Uppdatera alla interna links
  ├─ Reservera framework/light
  └─ Deprecate gamla docs/

Phase 3: Framework Landing Page
  ├─ Designa INDEX.md struktur
  ├─ Implementera INDEX.md med nav & glossary
  └─ Lägg till subdirectory back-links

Phase 4: Results Landing Page
  ├─ Förbered runs/ struktur
  ├─ Implementera runs/INDEX.md template
  └─ Designa run-metadata template

Phase 5: Testing & Verifiering
  ├─ Verifiera alla links
  ├─ Testa stakeholder-navigation
  ├─ Validera DONE-kriterier
  └─ Final review & PR

Phase 6: Dokumentation
  └─ Dokumentera beslut & notes
```

---

## Stegvis Genomförande

### **Phase 1: Preparation & Analysis (3 TODOs)**

#### TODO 1.1: Audit docs structure

- Kartlägga `docs/` directory-tree (agents/, processes/, RACI/, SOP/, artifacts/)
- Räkna totalt antal filer per subdirectory
- Använd `grep_search` för att lista alla interna links (`[text](../...)` mönster)
- Dokumentera findings i `/memories/session/` för senare referens
- **Acceptance:** Complete file inventory med link-count

#### TODO 1.2: Review navigation patterns

- Sök efter befintliga README.md, INDEX.md eller navigation i `docs/`
- Dokumentera namnkonventioner (kebab-case, link-format, file-struktur)
- Identifiera 10-15 glossary-termer från framework-vocabulary:
  - agent, role, SOP, RACI, artifact, capability, orchestration, process-step
  - run, RunState, expertise, consultation, approval, informing
- Lista 3-5 stakeholder personas: Executive, Architect, Operator, Product Owner, Business Analyst
- **Acceptance:** Glossary-termer och personas dokumenterade

#### TODO 1.3: Check valuestream-os-data repo

- Verifiera att `valuestream-os-data` repo existerar och är tillgänglig
- Kontrollera `runs/` katalog och dess nuvarande struktur
- Dokumentera alla metadata-filer: `run_log.json`, `artifact_state.json`, `approval_decisions.json`, etc.
- Bekräfta att ingen circular dependency finns mellan repos
- **Acceptance:** Repo-status, struktur och metadata bekräftade

---

### **Phase 2: Refactor docs → framework/standard (5 TODOs)**

#### TODO 2.1: Create framework/standard directory

- Skapa `framework/` katalog i root (om i saknas)
- Skapa `framework/standard/` innanför
- Verifiera med `list_dir` att båda existerar
- **Commit:** `chore(repo): create framework/standard directory`
- **Acceptance:** Directory visas i file explorer

#### TODO 2.2: Copy docs content to framework/standard

- Kopiera varje subdirectory från `docs/` till `framework/standard/`:
  - `docs/agents/` → `framework/standard/agents/`
  - `docs/processes/` → `framework/standard/processes/`
  - `docs/RACI/` → `framework/standard/RACI/`
  - `docs/SOP/` → `framework/standard/SOP/`
  - `docs/artifacts/` → `framework/standard/artifacts/`
- Bevara alla filinnehål exakt (ingen ändringar än)
- Verifiera med `list_dir` att alla filer är närvarande
- **Acceptance:** Alla docs/-filer finns i framework/standard/

#### TODO 2.3: Update internal links in framework/standard

- Använd `grep_search` för att hitta alla referensmönster: `../docs/`, `docs/`, `[link](../`
- Uppdatera paths: gamla `../docs/agents/foo.md` → nya `../agents/foo.md` eller `framework/standard/agents/foo.md`
- Testa 5-10 slumpmässiga filer: läs dem och verifiera links funktion
- Fixa eventuella bruten reference-mönster
- **Acceptance:** Zero bruten internal links

#### TODO 2.4: Create framework/light placeholder

- Skapa `framework/light/` direktory
- Lägg `framework/light/.gitkeep` fil innanför
- Lägg till kommentar i `.gitignore`: "framework/light reserved for future variant (light/compact version)"
- **Commit:** `chore(repo): reserve framework/light for future variants`
- **Acceptance:** Directory-struktur reserverad

#### TODO 2.5: Deprecate old docs directory

- Flytta `docs/` katalog till `docs.deprecated/` (för säkerhet)
- Uppdatera `README.md`: alla refs `docs/` → `framework/standard/`
- Sök i `src/`, `setup/`, `.gitignore` för docs-references och uppdatera
- **Commit:** `refactor(repo): deprecate docs/ in favor of framework/standard/`
- **Acceptance:** Gamla docs/ är inte längre aktiv

---

### **Phase 3: Create Framework Landing Page (4 TODOs)**

#### TODO 3.1: Design framework/standard/INDEX.md structure

Skapa outline för `framework/standard/INDEX.md`:

- **Header** (1-2 meningar): Systemets syfte & fokus
- **Quick Navigation** (lista): Agenter, Processer, Roller, RACI, SOP:er, Artifakter (med links)
- **Glossary** (5-10 termer): Mini-glossary för okända koncept
- **How to Use This Framework** (5-7 rad): Orientering för executive, architect, operator
- **Architecture Basics** (ASCII-diagram eller kort text): Agent → Orchestrator → Artifact-flöde
- **More Resources** (links): Länka till subdirektories och templates

Spara draft i `/memories/session/` för review innan implementation.

- **Acceptance:** Outline godkänd av user

#### TODO 3.2: Implement framework/standard/INDEX.md

- Skapa fil `framework/standard/INDEX.md` med all innehål från approved outline
- Verifiera att alla links pekar på faktiska filer (agents/foo.md, RACI/foo.md, etc.)
- Testa 10+ slumpmässiga links genom att navigera i VS Code editor
- Lägg till visuell formatering: emoji, dividers, bold headings för readability
- **Acceptance:** INDEX.md existerar, är läsbar, alla links verifierade

#### TODO 3.3: Create glossary

**Decision punkt:** Embed glossary i INDEX.md eller separat `GLOSSARY.md`?

- **Option A (embed):** Kort glossary (5-10 termer) direkt i INDEX under "Glossary"
- **Option B (separate):** Dedikerad `framework/standard/GLOSSARY.md` med 15-25 termer, linked från INDEX

Valda sektioner:

- Varje term: 1-2 meningar i ramverks-kontexct (inte generisk definition)
- Exempel: "**Agent** — An autonomous entity (powered by LLM) that produces artifacts following RACI roles."
- Inkludera: agent, role, orchestration, RACI (Responsible, Consulted, Approved, Informed), SOP, artifact, run, consultation, approval, informing, expertise, capability

- **Acceptance:** Glossary komplett och tillgänglig

#### TODO 3.4: Add navigation breadcrumbs

- Uppdatera `framework/standard/agents/README.md` (or create if missing) med back-link
  ```markdown
  📍 [Back to Framework Index](../INDEX.md)
  ```
- Gör samma för: `processes/`, `RACI/`, `SOP/`, `artifacts/`
- Håll minimal (1-2 rader)
- **Acceptance:** Alla subdirectories har back-links till INDEX

---

### **Phase 4: Set Up Results Landing Page (3 TODOs)**

#### TODO 4.1: Create runs structure in valuestream-os-data

- Navigera till `../valuestream-os-data/` repo
- Verifiera att `runs/` katalog existerar
- Förbered struktur för framtida `runs/<run-id>/` migrations (kopiera NO data än)
- **Acceptance:** Directory-struktur klar för framtida data migration

#### TODO 4.2: Implement runs/INDEX.md

Skapa `../valuestream-os-data/runs/INDEX.md`:

- **Header:** "Value Stream OS — Execution Results"
- **Recent Runs Table:**
  ```
  | Run ID | Date | Process Step | Status | Artifacts |
  |--------|------|--------------|--------|-----------|
  | middag-tillsammans | 2026-03-15 | Kravställning | completed | 3 |
  | sample-run | 2026-03-10 | Målarkitektur | draft | 2 |
  ```
- **How to Read Results:** Kort förklaring av run-struktur (processsteg, artifakter, decisions)
- **Run Files Legend:**
  - `run_log.json` — Execution timeline & events
  - `artifact_state.json` — Status för varje artifact
  - `approval_decisions.json` — Approval records
  - `consultation_responses.json` — Expert feedback
  - `informed_role_briefs.json` — Informing summaries
- **Navigation:** Link tillbaka till `framework/` INDEX för kontexct

- **Acceptance:** runs/INDEX.md existerar, är tydlig

#### TODO 4.3: Create run-metadata template

Skapa template för `framework/standard/artifacts/templates/run-summary.md`:

```markdown
# Run: [RUN_ID]

**Execution Date:** [TIMESTAMP]
**Process Step:** [Step Name, e.g., Kravställning]
**Status:** [draft | completed | rejected]

## Artifacts Produced

- [Artifact Name] — [path/to/artifact.md]
- ...

## Decisions

- **Approval:** [approved/rejected] by [Role]
- **Consultation Feedback:** [Yes/No]

## Key Findings

[Summary of important findings]

📍 [Back to Runs Index](../../runs/INDEX.md)
```

- **Acceptance:** Template designad & dokumenterad

---

### **Phase 5: Testing & Verification (4 TODOs)**

#### TODO 5.1: Verify all framework links

- Från `framework/standard/INDEX.md`, navigera till minst 10 olika filer (agents/, RACI/, SOP/, artifacts/)
- Använd `grep_search` för att hitta bruten link-mönster: `[text](#)`, `[text](./)`, `[text]()`
- Testa i VS Code editor (CMD+Click eller Ctrl+Click) och GitHub om möjligt
- Log alla fel och fixa dem
- **Acceptance:** Zero bruten links, all navigation functional

#### TODO 5.2: Test stakeholder navigation flow

Simulera tre personas:

- **Executive:** Kan förstå systemets syfte på 1 minut från INDEX? Tar < 30 sekunder att hitta "varför detta ramverk?"
- **Architect:** Kan hitta RACI, processer, artifakter enkelt? Kan navigera från INDEX → RACI → Kravställning → Godkännande?
- **Operator:** Kan förstå hur man läser ett run-resultat? Kan hitta från runs/INDEX → specifik run → artifacts & decisions?

Noter UX-issues och minor improvements. Iterera vid behov.

- **Acceptance:** Alla tre personas lyckas navigera

#### TODO 5.3: Validate Definition of Done

Checka alla MVP 05 DONE-kriterier:

- ✅ `docs/` refaktorerat till `framework/standard/` med samma innehål
- ✅ `runs/` förberedd för framtida separation (struktur, INDEX, template skapade)
- ✅ `framework/standard/INDEX.md` implementerad med navigation & glossary
- ✅ `runs/INDEX.md` struktur klar
- ✅ Alla interna links uppdaterade
- ✅ Glossary med 5-10 termer (minst)
- ✅ `framework/light/` reserverad för framtida variant

Skapa screenshot av ny folder-struktur för dokumentation.

- **Acceptance:** Alla DONE-kriterier verifierade

#### TODO 5.4: Final review and prepare PR

- Final staving & formatting-check på alla markdown-filer
- Uppdatera README.md i root: dokumentation-links peka på `framework/standard/` istället för `docs/`
- Skapa PR-summary:

  ```
  ## Changes
  - Moved docs/ → framework/standard/ for framework variant support
  - Added framework/standard/INDEX.md with navigation & glossary
  - Prepared runs/INDEX.md structure in valuestream-os-data repo
  - Updated all internal links & references
  - Created run-metadata template for future results documentation

  ## Testing
  - Verified 10+ links in framework navigation
  - Tested with 3 stakeholder personas
  - All Definition of Done criteria checked
  ```

- Committa alla remaining changes: `docs(framework): add landing pages and navigation`
- **Acceptance:** Allt committed, ready för PR review

---

### **Phase 6: Documentation & Handoff (1 TODO)**

#### TODO 6.1: Document implementation notes

Skapa kort notering (markdown) med:

- **Decisions Made:**
  - Glossary embedded vs. separate? (your choice)
  - Any link-format standardization applied?
- **Deviations from Original Plan:**
  - Any scope changes or technical discoveries?
- **Known Limitations:**
  - runs/ data migration not included (separate phase)
  - framework/light/ structure reserved but not populated
- **Suggestions for Next PR:**
  - Automated link checker?
  - Visual flowchart in INDEX?
  - Integration with GitHub Pages?

Spara under `functionality/plans/` eller `/memories/session/`

- **Acceptance:** Notes dokumenterade för framtida referens

---

## Viktiga Designval

1. **Markdown-Only Approach** — Ingen HTML-generator, webbserver eller databas. Gör det enkelt att versionshanta tillsammans med kod och accessible för alla stakeholders.

2. **Framework-Struktur Framtidssäker** — `framework/standard/` möjliggör enkla framtida varianter som `framework/light/` (compact version) utan behov av parallell kodbas.

3. **Data-Separation Planerad, Inte Implementerad** — `runs/` separation till `valuestream-os-data` repo är designad men INTE implementerad i denna MVP. Fokus på presentationslager först.

4. **Glossary in Context** — Alla termer förklaras i ramverk-sammanhang, inte generiska definitions. Gör det relevantare för användarna.

5. **Stakeholder-Testbar** — Navegation testad med konkreta personas (executive, architect, operator) för att säkerställa faktisk användarbarhet.

---

## Verifiering per Phase

| Phase       | Success Criteria                                                                                           |
| ----------- | ---------------------------------------------------------------------------------------------------------- |
| **Phase 1** | Docs-struktur kartlagd, glossary-termer & personas identifierade, externa repo-setup bekräftad             |
| **Phase 2** | docs/ → framework/standard/ refactoring klar, ALLA internal links uppdaterad & fungerar                    |
| **Phase 3** | Framework INDEX skapad med full navigation & glossary, subdirectory back-links på plats                    |
| **Phase 4** | runs/INDEX.md template design klar, run-metadata-template skapad                                           |
| **Phase 5** | ALLAsystem links verifierade (0 broken), stakeholder personas testa navigation, MVP DONE-kriterier checkat |
| **Phase 6** | Implementation notes dokumenterade, ready för handoff                                                      |

---

## Branch & Commit Strategy

**Feature Branch:** `05-accessibility-landing-pages`

**Expected Commits (in order):**

1. `chore(repo): create framework/standard directory`
2. `refactor(repo): move docs to framework/standard`
3. `docs(framework): update internal links for new structure`
4. `docs(framework): add INDEX landing page and glossary`
5. `chore(framework): reserve framework/light for future variants`
6. `docs(runs): add INDEX template and run-metadata structure`

Keep commits small & focused per standards.md execution loop.

---

## Rollback & Safety

- **If refactoring fails:** Old `docs/` backed up as `docs.deprecated/` — can restore
- **If external repo setup fails:** Keep results in main repo via runs/ folder (done later)
- **No production-code changes:** Safe to revert without breaking functionality
- **All changes markdown-based:** Easy to review & undo

---

## Success Criteria (MVP Completion)

✅ **Framework Accessible:** framework/standard/INDEX.md with zero broken links
✅ **Stakeholder-Ready:** Personas can navigate framework & results
✅ **Prepared for Scale:** framework/light/ reserved, runs/ separation structured
✅ **Well-Documented:** All landing pages clear & self-explanatory
✅ **Standards-Compliant:** Code committed siguiendo standards.md execution loop

---

**Plan created:** 2026-04-01
**Target completion:** 1-2 weeks (depending on parallel work)
