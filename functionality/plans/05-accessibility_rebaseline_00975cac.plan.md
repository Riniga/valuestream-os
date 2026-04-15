---
name: Accessibility Rebaseline
overview: Ta fram en ombaserad plan för MVP 05 som utgår från vad branchen `accessibility-landing-pages` redan har levererat och fokuserar nästa steg på resultatlagret, dokumentationskonsistens och eventuell externisering av `runs/`.
todos:
  - id: rebaseline-docs
    content: Synka MVP-, plan- och implementation-notes-dokumenten med vad branchen faktiskt redan levererat.
    status: completed
  - id: finish-runs-interim
    content: Definiera och implementera ett verkligt interim-läge för resultatnavigation innan extern repo-separation.
    status: completed
  - id: align-readme-runtime
    content: Justera README och centrala referenser så att repo-struktur och runtime-beteende berättar samma historia.
    status: completed
  - id: spec-external-repo
    content: Dokumentera kontrakt och migrationssteg för framtida `valuestream-os-data`.
    status: completed
  - id: verify-close-mvp
    content: Verifiera stakeholder-navigering och stäng MVP 05 med tydliga kvarvarande risker.
    status: completed
isProject: false
---

# MVP 05 Rebaseline Plan

## Nuläge

Branchen `accessibility-landing-pages` har redan genomfört större delen av den ursprungliga strukturförändringen:

- `framework/standard/` och `framework/light/` finns och innehåller landningssidor, glossary och README-breadcrumbs, bland annat i [D:/github/riniga/valuestream-os/framework/standard/INDEX.md](D:/github/riniga/valuestream-os/framework/standard/INDEX.md), [D:/github/riniga/valuestream-os/framework/light/INDEX.md](D:/github/riniga/valuestream-os/framework/light/INDEX.md) och under respektive underkatalog.
- Runtime har redan börjat stödja framework-varianter via [D:/github/riniga/valuestream-os/src/framework/repo_layout.py](D:/github/riniga/valuestream-os/src/framework/repo_layout.py), [D:/github/riniga/valuestream-os/src/framework/context_loader.py](D:/github/riniga/valuestream-os/src/framework/context_loader.py) och [D:/github/riniga/valuestream-os/src/orchestration/process_loader.py](D:/github/riniga/valuestream-os/src/orchestration/process_loader.py).
- Ursprunglig plan i [D:/github/riniga/valuestream-os/functionality/plans/05-plan-accessibilityLandingPages.prompt.md](D:/github/riniga/valuestream-os/functionality/plans/05-plan-accessibilityLandingPages.prompt.md) beskriver fortfarande mycket som “att göra”, trots att mycket redan är gjort.
- MVP-beskrivningen i [D:/github/riniga/valuestream-os/functionality/mvp/05-accessibility-landing-pages.md](D:/github/riniga/valuestream-os/functionality/mvp/05-accessibility-landing-pages.md), implementation notes i [D:/github/riniga/valuestream-os/functionality/plans/05-IMPLEMENTATION_NOTES.md](D:/github/riniga/valuestream-os/functionality/plans/05-IMPLEMENTATION_NOTES.md) och root-dokumentation i [D:/github/riniga/valuestream-os/README.md](D:/github/riniga/valuestream-os/README.md) är inte längre helt synkade.
- Den största kvarvarande luckan är att resultatlagret inte är färdigställt: branchen innehåller templates för `runs` men inte ett tydligt, förankrat slutläge för `runs/INDEX.md` eller extern repo-separation.

## Målbild

Slutför MVP 05 som ett konsekvent och implementerbart presentationslager där:

- framework-navigationen är etablerad och konsekvent dokumenterad,
- resultatnavigationen har ett tydligt interim- eller slutläge,
- Definition of Done speglar faktisk leverans,
- kod, dokumentation och nästa steg mot `valuestream-os-data` hänger ihop.

## Genomförande

### Steg 1: Re-baseline scope och acceptera faktisk leverans

Syfte: sluta planera om sådant som redan är klart och göra MVP 05 styrbar igen.

- Jämför faktisk leverans i `framework/` mot plan- och MVP-dokumenten.
- Uppdatera [D:/github/riniga/valuestream-os/functionality/mvp/05-accessibility-landing-pages.md](D:/github/riniga/valuestream-os/functionality/mvp/05-accessibility-landing-pages.md) så att Definition of Done separerar:
  - klart i denna branch,
  - kvar i repo,
  - beroenden till extern repo.
- Uppdatera eller ersätt [D:/github/riniga/valuestream-os/functionality/plans/05-plan-accessibilityLandingPages.prompt.md](D:/github/riniga/valuestream-os/functionality/plans/05-plan-accessibilityLandingPages.prompt.md) så att den blir en nulägesplan i stället för en “greenfield”-plan.
- Säkerställ att [D:/github/riniga/valuestream-os/functionality/plans/05-IMPLEMENTATION_NOTES.md](D:/github/riniga/valuestream-os/functionality/plans/05-IMPLEMENTATION_NOTES.md) inte påstår fullständig completion om externa beroenden fortfarande blockerar delar av DoD.

Acceptance:

- Dokumentationen skiljer tydligt mellan “redan levererat”, “återstår i detta repo” och “kräver `valuestream-os-data`”.
- Ingen central plantext beskriver `framework/standard/INDEX.md` som ogjord.

### Steg 2: Färdigställ resultatlagrets interim-läge i detta repo

Syfte: göra resultatdelen användbar även innan extern repo-separation är på plats.

- Besluta att MVP 05 tills vidare använder ett interim-läge: antingen ett verkligt `runs/INDEX.md` i detta repo eller ett tydligt dokumenterat placeholder-flöde som länkar vidare från framework-landningssidan.
- Återanvänd befintliga templates under `framework/*/artifacts/templates/`, särskilt `runs-INDEX.md.template` och `run-README.md.template`, som grund för verklig navigation.
- Om exempeldata finns, exponera minst ett konkret körningsresultat via en navigerbar index-sida.
- Lägg in tydliga länkar mellan framework-ingången och resultat-ingången så att stakeholder-resan blir sammanhängande.

Acceptance:

- Det finns ett tydligt svar på frågan “var hittar jag körningsresultat nu?”.
- Resultatdelen är navigerbar utan att vänta på extern repo-setup.

### Steg 3: Synka toppnivå-dokumentation och runtime-beteende

Syfte: minska glappet mellan faktisk struktur och hur repo samt CLI beskriver sig själva.

- Uppdatera [D:/github/riniga/valuestream-os/README.md](D:/github/riniga/valuestream-os/README.md) från `docs/`-centrisk struktur till `framework/`-centrisk struktur.
- Inventera övriga centrala referenser till `docs/` och avgör om de ska:
  - migreras till `framework/standard`, eller
  - märkas som legacy/backward compatibility.
- Gå igenom fallback-beteendet i [D:/github/riniga/valuestream-os/src/framework/repo_layout.py](D:/github/riniga/valuestream-os/src/framework/repo_layout.py) och dokumentera om `docs/`-fallback ska vara kvar temporärt eller tas bort i ett senare steg.
- Bekräfta att CLI- och processladdning fortsatt pekar mot rätt framework-variant via [D:/github/riniga/valuestream-os/src/cli/run.py](D:/github/riniga/valuestream-os/src/cli/run.py) och [D:/github/riniga/valuestream-os/src/orchestration/process_loader.py](D:/github/riniga/valuestream-os/src/orchestration/process_loader.py).

Acceptance:

- README och centrala repo-beskrivningar speglar faktisk struktur.
- Legacy-beteende runt `docs/` är ett medvetet beslut, inte en oklar rest.

### Steg 4: Förbered externisering till `valuestream-os-data` som separat leverans

Syfte: bryta ut extern repo-separation till ett kontrollerat nästa steg i stället för ett diffust krav.

- Dokumentera minsta kontrakt för `valuestream-os-data`:
  - förväntad katalogstruktur,
  - obligatoriska metadatafiler,
  - hur länkar tillbaka till framework ska se ut.
- Basera kontraktet på redan etablerade templates och de run-state-filer som CLI/orchestrator producerar.
- Lägg till en kort migrationschecklista för när det externa repot väl finns.

Acceptance:

- Det finns en konkret “ready-to-execute” plan för extern repo-separation.
- MVP 05 blockeras inte längre av att det externa repot ännu inte finns.

### Steg 5: Verifiering och stängning av MVP 05

Syfte: avsluta med en verifierbar, review-bar leverans.

- Kör en riktad markdown- och länkreview för landningssidor, README och resultatnavigation.
- Verifiera stakeholder-flöden för minst:
  - framework-orientering,
  - hitta en process/SOP,
  - hitta ett run-resultat eller dess interim-ingång.
- Sammanfatta kvarvarande risker som uttryckliga “post-MVP” eller “Phase 2”-punkter i stället för gömda avvikelser.

Acceptance:

- MVP 05 kan beskrivas med ett kort, sant PR-sammanhang.
- Återstående arbete är tydligt avgränsat till nästa steg, inte blandat med redan levererad funktion.

## Rekommenderad implementationsordning

1. Dokument-rebaseline i `functionality/`.
2. Verkligt interim-läge för `runs`.
3. README- och referensstädning.
4. Extern repo-kontrakt och migrationschecklista.
5. Slutverifiering.

## Antaganden

- `framework/standard` och `framework/light` ska behållas som gällande struktur.
- `docs/`-fallback får leva kvar kortsiktigt om den fortfarande behövs av runtime eller äldre flöden.
- `valuestream-os-data` finns inte ännu, så planen optimerar för ett fungerande mellanläge först.
