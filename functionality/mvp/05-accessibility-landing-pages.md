# Funktionalitet: 05 – Accessibility & Landing Pages (MVP)

## Metadata

| Fält        | Värde                          |
| ----------- | ------------------------------ |
| ID          | 05                             |
| Namn        | Accessibility & Landing Pages  |
| Version     | 0.1                            |
| Processsteg | Tvärgående / presentationslager |
| Ägare       | Agent Core                     |

---

## 1. Syfte

Göra ramverket och dess resultat lättare att förstå och navigera för stakeholders med varierande teknisk bakgrund. Implementera ett presentationslager som en central ingångspunkt för att utforska både ramverksdokumentation och körningsresultat.

**Fokus:** Navigerbarhet och förståelse för externa stakeholders — inte visualisering eller interaktivitet utan markdown.

---

## 2. Scope

### Ingår

- Landningssida för ramverksdokumentation (`docs/`)
  - Översikt över agenter, processer, RACI, SOP:er
  - Navigering till relevanta dokumentdelar
  - Förklarande text för okända koncept
- Landningssida för körningsresultat (`runs/`)
  - Visa senaste körningar och deras status
  - Tillgång till artifakter och beslut per körning
  - Förklarande sammanhang för vad som hände
- Strukturering: docs döps om till `framework/standard`
- Separation av resultat: `runs/` flyttas till eget repo (`valuestream-os-data`)
- Möjliggöra flera ramverk-varianter (minst struktur för `framework/light`)

### Ingår ej (senare)

- Interaktiv webbgränssnitt
- Databas eller dynamisk server
- Automatisk generering av landningssidor
- Visualisering av flöden (kan läggas på framtida landing pages)

---

## 3. Arkitekturval

### Markdown som presentations-format

Landningssidorna ska vara markdown-filer, inte HTML eller andra format. De läses direkt i GitHub/editor.

**Motivering:**
- Konsistent med befintlig dokumentation
- Ingen extra infrastruktur behövs
- Lätt att versionshanteras tillsammans med innehållet
- Stakeholders redan vana vid markdown

### Extern data-repo för runs

`runs/` flyttas till `valuestream-os-data` repo för att separera kod från resultat.

**Motivering:**
- Repohistorik väl använd för kod, inte data
- Resultat kan växa mycket större än kod
- Tydlig separation av ansvar

### Framework-struktur med varianter

`docs/` blir `framework/standard/` för att möjliggöra framtida varianter utan filkollisioner.

**Motivering:**
- Framtidssäker design
- Tydlig struktur för "standard" vs. framtida "light" variant
- En-till-en mappning mellan docs och framework-katalog

---

## 4. Funktionellt beteende

### 4.1 Landningssida för ramverk

En fil `framework/standard/INDEX.md` (eller `README.md`) som:
- Förklarar systemets syfte i 1-2 meningar
- Listar huvudkategorier: Agenter, Processer, Roller, RACI, SOP:er, Artifakter
- Länkar till respektive undersidor
- Innehåller mini-glossary för nyckelord

### 4.2 Landningssida för resultat

En fil `../valuestream-os-data/runs/INDEX.md` som:
- Visar senaste körningar i tidsordning
- Per körning: processsteg, status, nyckeldatum
- Länk till körningsspecifika resultat (artifakter, beslut, expertsammanhang)
- Förklaring av vilka filer som finns och vad de innehåller

### 4.3 Repo-strukturering

Efter denna MVP:
```
valuestream-os/
  framework/
    standard/
      agents/
      processes/
      roles/
      raci/
      sop/
      artifacts/
      INDEX.md
  src/
  tests/
  ...

valuestream-os-data/ (separat repo)
  runs/
    INDEX.md
    <run-id>/
      ...
```

---

## 5. Definition of Done

- [ ] `docs/` refaktorerat till `framework/standard/` med samma innehål
- [ ] `runs/` flyttat till separat repo `valuestream-os-data`
- [ ] Landningssida `framework/standard/INDEX.md` implementerad med navigering
- [ ] Landningssida `runs/INDEX.md` implementerad med körningsöversikt
- [ ] Alla interna länkar uppdaterade för nya sökvägar
- [ ] Glossary med 5-10 nyckelkoncept inkluderat i ramverks-INDEX
- [ ] Minst ett körningsresultat synligt och navigerbart via runs-INDEX
