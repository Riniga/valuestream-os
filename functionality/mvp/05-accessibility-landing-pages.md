# Funktionalitet: 05 – Accessibility & Landing Pages (MVP)

## Metadata

| Fält        | Värde                           |
| ----------- | ------------------------------- |
| ID          | 05                              |
| Namn        | Accessibility & Landing Pages   |
| Version     | 0.2                             |
| Processsteg | Tvärgående / presentationslager |
| Ägare       | Agent Core                      |
| Status      | Rebaselined efter brancharbete  |

---

## 1. Syfte

Göra ValueStream OS lättare att förstå och navigera för stakeholders med varierande teknisk bakgrund genom ett markdown-baserat presentationslager för både ramverket och körningsresultat.

**Fokus:** Navigerbarhet och begriplighet i repo/editor. Ingen webbapplikation, server eller databas ingår i denna MVP.

---

## 2. Rebaselined scope

### Redan levererat i branchen

- `framework/standard/` är etablerad som primär presentationsyta för full framework-variant.
- `framework/light/` finns som parallell variantstruktur.
- Landningssidor och navigation finns i `framework/standard/INDEX.md` och `framework/light/INDEX.md`.
- Glossary och README-breadcrumbs finns på plats i framework-strukturen.
- Runtime stöder framework-varianter via `src/framework/repo_layout.py` och relaterade loaders.

### Kvar att färdigställa i detta repo

- Tydlig dokumentation om att lokal `runs/` är privat runtime-state och att delade/publicerade resultat hör hemma i `valuestream-os-data`.
- Synka README, guidelines och plan-/MVP-dokument med faktisk struktur (`framework/` i stället för äldre `docs/`-bild).
- Dokumentera kontraktet för framtida flytt till `valuestream-os-data`.

### Externt beroende / senare leverans

- Full flytt av `runs/` till separat repo `valuestream-os-data`.
- Permanent publicering av verkliga körningsresultat i separat datarepo.

### Ingår ej i denna MVP

- Interaktivt webbgränssnitt
- Databas eller dynamisk server
- Automatisk generering av landningssidor
- Visualisering av flöden utöver markdown-baserad struktur

---

## 3. Arkitekturval

### Markdown som presentationsformat

Landningssidorna ska vara markdown-filer som läses direkt i GitHub eller editor.

**Motivering:**
- Konsistent med befintlig dokumentation
- Ingen extra infrastruktur behövs
- Lätt att versionshantera tillsammans med kod och framework
- Transparent för både människor och agenter

### Framework-struktur med varianter

Framework-dokumentationen ligger under `framework/<variant>/` där `standard` är huvudspåret och `light` en lättare variant.

**Motivering:**
- Framtidssäker struktur för flera framework-varianter
- Tydlig separation mellan ramverksinnehåll och runtime-kod
- Möjliggör variantval i runtime utan separat kodbas

### Resultatdata separeras senare

Körningsresultat skapas lokalt under `runs/` i detta repo som privat runtime-state, medan delade eller publicerade resultat ska ligga i det separata repot `valuestream-os-data`.

**Motivering:**
- Runtime skriver redan filbaserad state till `runs/<run-id>/`
- Externt repo finns inte etablerat ännu
- Stakeholder-navigering kan ändå göras tydlig redan nu

---

## 4. Funktionellt beteende

### 4.1 Landningssida för ramverk

`framework/standard/INDEX.md` ska fungera som central ingång till:
- agenter
- processer
- RACI
- SOP:er
- artefakter
- glossary
- vidare länk till resultatnavigation

### 4.2 Resultatpublicering

I denna MVP ska dokumentationen tydligt beskriva att:
- runtime-resultat skapas lokalt i `runs/<run-id>/`
- lokal `runs/` inte versionshanteras
- delade eller publicerade run-resultat hör hemma i `../valuestream-os-data`
- templates och kontrakt i detta repo används som stöd för publicering till datarepot

### 4.3 Målbild för externisering

När `valuestream-os-data` etableras ska samma navigationsmodell kunna flyttas dit utan att ändra framework-koncepten.

Målbild:

```text
valuestream-os/
  framework/
    standard/
    light/
  src/
  setup/
  runs/
    <run-id>/
      ... privata runtime-filer lokalt

valuestream-os-data/
  <project-or-run>/
    README.md
    input/
    output/
    ... publicerade resultat och state-filer
```

---

## 5. Definition of Done

### Klart i denna branch

- [x] `framework/standard/` etablerat med motsvarande ramverksinnehåll
- [x] `framework/light/` etablerat som variantstruktur
- [x] Landningssida `framework/standard/INDEX.md` implementerad med navigering
- [x] Landningssida `framework/light/INDEX.md` implementerad
- [x] Intern navigation och glossary för framework finns på plats
- [x] Runtime har stöd för att läsa framework-variant från `framework/`

### Ska vara klart i detta repo för att stänga MVP 05

- [x] Dokumentationen beskriver att lokal `runs/` är privat runtime-state
- [x] README och centrala guidelines speglar `framework/`-först-strukturen
- [x] Delade/publicerade runs hänvisas till `valuestream-os-data`
- [x] Plan- och implementationsdokument beskriver sann leveransstatus

### Senare / extern leverans

- [ ] `runs/` flyttat till separat repo `valuestream-os-data`
- [ ] Publicerat minst ett fullständigt körningsresultat i det externa datarepot
