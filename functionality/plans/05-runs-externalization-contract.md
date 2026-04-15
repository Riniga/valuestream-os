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

## Minimum repository structure

```text
valuestream-os-data/
  runs/
    INDEX.md
    <run-id>/
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

## Runs index contract

`runs/INDEX.md` i datarepot ska minst innehålla:

- vad en run är
- hur en run-katalog är uppbyggd
- lista över publicerade runs
- status eller processsteg per run
- länk tillbaka till frameworkets index

Bra miniminivå för tabell:

```text
| Run ID | Process Step(s) | Status | Last Updated | Summary |
```

---

## Mapping from current runtime

Nuvarande runtime i `valuestream-os` skriver redan huvuddelen av de filer som behövs för publicering under `runs/<run-id>/`.

Det innebär att externisering primärt är:

1. välja vilka runs som ska publiceras
2. lägga till eller komplettera `README.md` per run
3. skapa eller uppdatera `runs/INDEX.md`
4. säkerställa fungerande länkar tillbaka till frameworket

Ingen ny grundmodell för metadata behöver tas fram.

---

## Migration checklist

1. Skapa repot `valuestream-os-data`.
2. Skapa `runs/INDEX.md` med samma informationsarkitektur som i interim-läget.
3. Välj första run att publicera.
4. Kopiera relevanta runtime-filer från lokalt `runs/<run-id>/`.
5. Lägg till en stakeholder-vänlig `README.md` för runnen.
6. Verifiera länkar tillbaka till `framework/standard/INDEX.md`.
7. Uppdatera `valuestream-os` så att `runs/INDEX.md` pekar vidare till datarepot när det är etablerat.

---

## Open decisions

Följande beslut kan tas i nästa steg utan att blockera MVP 05:

- om alla eller bara utvalda runs ska publiceras
- om `input/` och `output/` ska publiceras ofiltrerat eller kureras
- om datarepot ska innehålla enbart resultat eller även snapshots av centrala artefakter

---

## Summary

`valuestream-os-data` behöver inte en ny datamodell. Det behöver ett publiceringskontrakt ovanpå den struktur som runtime redan producerar.
