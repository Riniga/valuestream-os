# Implementation Notes – MVP 05: Accessibility & Landing Pages

**Date:** 2026-04-15  
**Status:** Rebaselined after branch review

---

## Executive Summary

Branchen har redan levererat större delen av den ursprungliga ambitionen för MVP 05:

- framework-dokumentationen är flyttad till `framework/`
- landningssidor finns för både `standard` och `light`
- glossary och breadcrumb-navigation finns på plats
- runtime kan läsa från framework-varianter

Det som återstod efter branchgranskningen var framför allt att göra resultatdelen sanningsenlig och användbar utan att publicera lokal `runs/` i detta repo, samt att synka styrdokument och README med den faktiska strukturen.

---

## Vad branchen faktiskt hade levererat

### Framework som primär yta

`framework/standard/` är den faktiska huvudingången för ramverket, och `framework/light/` finns redan som parallell variantstruktur.

### Navigation och orientering

Det finns centrala INDEX-filer, glossary och README-breadcrumbs som gör frameworket navigerbart för stakeholders.

### Runtime-stöd för framework-varianter

`src/framework/repo_layout.py` och relaterade loaders använder `framework/<variant>/` som primär källa, med fallback till äldre `docs/` där det fortfarande behövs för bakåtkompatibilitet.

---

## Branchens största gap

### 1. Resultatnavigationen var felplacerad

Det fanns templates för run-navigation, men lokal `runs/` ska enligt repo-reglerna inte committas. Den tidigare lösningen blandade därför ihop privat runtime-state med delbar dokumentation.

### 2. Styrdokumenten beskrev olika verkligheter

- MVP-dokumentet beskrev flera delar som ogjorda trots att de fanns i branchen.
- Den gamla implementationsplanen var i praktiken en greenfield-plan.
- Tidigare implementation notes påstod i stort sett full completion, trots att `runs`-delen och externisering återstod.

### 3. README och setup-dokumentation släpade efter

Root README och delar av setup-guidelines beskrev fortfarande `docs/` som primär struktur, trots att branchen redan flyttat huvuddelen av frameworket till `framework/`.

---

## Rebaseline-beslut

### Decision 1: Acceptera `framework/` som nuvarande sanningskälla

Dokumentation och navigation ska beskriva `framework/standard` och `framework/light` som gällande struktur.

### Decision 2: Behåll `runs/` privat i detta repo

`runs/` i `valuestream-os` ska förbli lokal runtime-state och inte versionshanteras. Delade eller publicerade resultat ska ligga i `valuestream-os-data`.

### Decision 3: Dokumentera legacy explicit

Fallback till `docs/` ska beskrivas som bakåtkompatibilitet i runtime, inte som primär informationsarkitektur.

### Decision 4: Flytta externisering till en separat, konkret nästa leverans

Extern repo-separation är fortfarande en målbild, men ska inte blandas ihop med redan levererade delar av MVP 05.

---

## Vad rebaselinen nu har levererat

Efter denna rebaseline är följande på plats:

- cleanup av committade `runs/`-entrypoints i detta repo
- dokumentation som skiljer på privat lokal `runs/` och delade resultat i `valuestream-os-data`
- uppdaterad README och setup-/guideline-dokumentation
- dokumenterat kontrakt för framtida `valuestream-os-data`
- verifierad navigation på dokumentationsnivå

---

## Kända begränsningar

- `valuestream-os-data` är ännu inte etablerat
- runtime skriver fortfarande lokalt till `runs/` i detta repo
- vissa äldre filer och referenser använder fortfarande `docs/`-språkbruk av kompatibilitetsskäl

---

## Nästa steg efter MVP 05

1. Etablera `valuestream-os-data`
2. Publicera relevanta lokala runs manuellt dit via projektmappar, till exempel `judotech-care/`
3. Uppdatera eller lägg till stakeholder-vänlig `README.md` i respektive projektmapp
4. Uppdatera länkar mellan frameworkrepo och datarepo
5. Avgör om run-root senare ska göras konfigurerbar i kod

---

## Sammanfattning

MVP 05 är inte längre ett arbete med att skapa framework-landningssidor från grunden. Det är nu ett arbete med att:

- stänga gapet mellan levererat och dokumenterat,
- behålla `runs/` privat och flytta delbar run-berättelse till datarepot,
- och definiera en kontrollerad väg vidare mot externt datarepo.

## Publiceringsflöde just nu

Det rekommenderade flödet efter denna omplanering är:

1. kör orchestratorn lokalt så att privat state skrivs under `runs/<run-id>/`
2. välj vilka filer från den lokala runnen som ska delas
3. kopiera dem manuellt till relevant projektmapp i `../valuestream-os-data`
4. komplettera med en mänskligt läsbar `README.md` i datarepot
5. låt `valuestream-os` fortsätta vara hem för framework, mallar och instruktioner

Detta gör att MVP 05 inte kräver någon ny kod för direkt export till datarepot nu. En eventuell framtida förbättring är att göra run-root konfigurerbar i runtime.
