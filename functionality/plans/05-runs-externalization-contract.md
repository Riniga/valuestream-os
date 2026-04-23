# MVP 05 – Contract for `valuestream-os-data`

## Purpose

Detta dokument beskriver minsta kontrakt för att flytta eller publicera körningsresultat från `valuestream-os` till ett separat datarepo: `valuestream-os-data`.

Syftet är att göra nästa steg genomförbart utan ny upptäcktsfas.

---

## Målbild

`valuestream-os-data` ska innehålla publicerade och läsbara körningsresultat, medan `valuestream-os` fortsatt innehåller:

- framework-definitionen
- orchestratorn och runtime-koden
- lokalt körningsstöd

Det separata datarepot ska alltså vara presentations- och historikytan för delade runs.

---

## Chosen repository structure

Den nuvarande och rekommenderade målstrukturen utgår från projektmappar i repo-roten, eftersom `valuestream-os-data` redan använder en sådan struktur, till exempel `judotech-care/`.

I stället för att först tvinga fram en generell `runs/<run-id>/`-struktur väljer detta kontrakt:

- en projektmapp per initiativ eller kundkontext
- runtime-filer, `input/` och `output/` inne i den projektmappen
- möjlighet att senare införa ytterligare gruppering eller index ovanpå denna modell

## Minimum repository structure

```text
valuestream-os-data/
  <project-name>/
    README.md
    run_state.json
    artifact_state.json
    run_log.json
    consultation_requests.json
    consultation_responses.json
    approval_decisions.json
    informed_role_briefs.json
    expert_context.json
    input/
    output/
```

---

## Required files per published run

### Human-readable entry point

- `README.md`

Denna fil är den primära stakeholder-ingången och ska sammanfatta:

- syfte med runnen
- processsteg som körts
- status
- viktigaste artefakter
- viktiga beslut
- länkar tillbaka till frameworket

### Required machine-readable files

- `run_state.json`
- `artifact_state.json`
- `run_log.json`
- `approval_decisions.json`
- `consultation_responses.json`
- `informed_role_briefs.json`

### Optional but recommended files

- `consultation_requests.json`
- `expert_context.json`
- `input/`
- `output/`

Om vissa filer utelämnas ska `README.md` förklara varför.

---

## Link contract back to framework

Varje publicerad run ska kunna förstås tillsammans med frameworket i `valuestream-os`.

Minimikrav:

- länk till `framework/standard/INDEX.md`
- länk till relevant process eller processöversikt
- länk till relevanta artefaktbeskrivningar eller RACI-ytor när det hjälper läsaren

Om datarepot och frameworkrepot lever i olika GitHub-repos ska länkarna vara absoluta repo-länkar eller en tydligt definierad relativ strategi beroende på publiceringssätt.

---

## Optional repo-level index contract

Datarepot saknar i dag en gemensam indexyta. Den är valfri på kort sikt, men rekommenderad när flera projekt eller runs ska bli lättare att hitta.

Om en indexyta införs kan den ligga i repo-roten som exempelvis `README.md` eller `INDEX.md` och bör minst innehålla:

- vilka projekt eller run-ytor som finns
- status eller fokus per projekt
- länk tillbaka till frameworkets index

Bra miniminivå för tabell:

```text
| Project | Run ID | Process Step(s) | Status | Last Updated | Summary |
```

---

## Mapping from current runtime

Nuvarande runtime i `valuestream-os` skriver redan huvuddelen av de filer som behövs för publicering under `runs/<run-id>/`.

Det innebär att externisering primärt är:

1. välja vilket lokalt `runs/<run-id>/` som ska publiceras
2. välja eller skapa motsvarande projektmapp i `valuestream-os-data`
3. kopiera relevanta state-filer, `input/` och `output/`
4. lägga till eller komplettera `README.md` i projektmappen
5. säkerställa fungerande länkar tillbaka till frameworket

Ingen ny grundmodell för metadata behöver tas fram.

---

## Migration checklist

1. Välj första lokala `runs/<run-id>/` att publicera.
2. Mappa den till en projektmapp i `valuestream-os-data`, till exempel `judotech-care/`.
3. Kopiera relevanta runtime-filer från lokalt `runs/<run-id>/`.
4. Kopiera eller kurera `input/` och `output/` utifrån vad som ska delas.
5. Lägg till eller uppdatera en stakeholder-vänlig `README.md` i projektmappen.
6. Verifiera länkar tillbaka till `framework/standard/INDEX.md`.
7. Om behov finns, lägg till repo-level `README.md` eller `INDEX.md` i `valuestream-os-data` för översikt.

---

## Open decisions

Följande beslut kan tas i nästa steg utan att blockera MVP 05:

- om alla eller bara utvalda runs ska publiceras
- om ett projekt kan innehålla flera runs över tid och hur de i så fall namnges
- om `input/` och `output/` ska publiceras ofiltrerat eller kureras
- om datarepot ska innehålla enbart resultat eller även snapshots av centrala artefakter

---

## Summary

`valuestream-os-data` behöver inte en ny datamodell. Det behöver ett publiceringskontrakt ovanpå den struktur som runtime redan producerar.
