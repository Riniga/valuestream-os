# ValueStream OS – Runs Index

Den här sidan är den nuvarande ingången till körningsresultat i `valuestream-os`.

I dagsläget fungerar `runs/` som ett **interim-läge**:

- runtime skriver lokala körningsfiler under `runs/<run-id>/`
- repo:t versionshanterar endast den dokumenterade ingången till resultatdelen
- målbilden är att publicerade resultat senare flyttas till `valuestream-os-data`

---

## Vad finns här nu?

### 1. Lokal runtime-yta

När orchestratorn körs skapas en run-katalog under:

```text
runs/<run-id>/
```

Typiska filer som skrivs av runtime:

- `run_state.json`
- `artifact_state.json`
- `run_log.json`
- `consultation_requests.json`
- `consultation_responses.json`
- `approval_decisions.json`
- `informed_role_briefs.json`
- `expert_context.json`
- `input/`
- `output/`

Dessa filer är lokala arbetsfiler och ignoreras normalt av git.

### 2. Dokumenterad referensyta

För att göra resultatdelen begriplig även utan committade run-data finns här en referensyta:

- [Runs README](./README.md) – syfte och principer för `runs/`
- [Example run navigation](./examples/README.md) – exempel på hur en publicerad run ska förstås

---

## Hur läser man ett run-resultat?

En run representerar en exekvering av ramverket för ett initiativ, en förändring eller en produktfråga.

En typisk läsordning är:

1. Starta i en `README.md` för runnen
2. Läs artefakter under `artifacts/` eller `output/`
3. Granska beslut i `approval_decisions.json` och konsultationsfiler
4. Kontrollera status i `artifact_state.json` och `run_state.json`
5. Läs `run_log.json` för tidslinje och händelser

---

## Rekommenderad katalogstruktur

```text
runs/
  INDEX.md
  README.md
  examples/
    README.md
  <run-id>/
    input/
    output/
    run_state.json
    artifact_state.json
    run_log.json
    consultation_requests.json
    consultation_responses.json
    approval_decisions.json
    informed_role_briefs.json
    expert_context.json
```

---

## Koppling till framework

Frameworket beskriver **vad** en run betyder och hur den ska tolkas:

- [Framework overview](../framework/standard/INDEX.md)
- [Process overview](../framework/standard/processes/Process.md)
- [RACI](../framework/standard/RACI/)
- [Artifacts](../framework/standard/artifacts/)

Kort sagt:

- `framework/` beskriver modellen, rollerna och artefakterna
- `runs/` visar vad som hände i en specifik exekvering

---

## Nuvarande status

- Framework-landningssidorna är implementerade
- `runs/` fungerar just nu som lokal runtime-yta plus dokumenterad navigationsingång
- framtida publicering i separat repo är planerad, men inte ett krav för att förstå strukturen nu

---

## Nästa steg

När `valuestream-os-data` etableras ska denna struktur kunna flyttas eller speglas dit:

- `runs/INDEX.md` blir publicerad indexyta
- en eller flera verkliga runs exponeras som läsbar dokumentation
- länkar tillbaka till `framework/standard/` behålls
