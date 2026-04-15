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

Det som återstod efter branchgranskningen var framför allt att göra resultatdelen sanningsenlig och användbar, samt att synka styrdokument och README med den faktiska strukturen.

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

### 1. Resultatnavigationen var bara delvis verklig

Det fanns templates för `runs/INDEX.md` och individuella run-readmes, men ingen faktisk `runs/INDEX.md` committad i repot. Samtidigt påstod vissa dokument att denna del redan var färdig.

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

### Decision 2: Behandla `runs/` som interim-läge i detta repo

Innan `valuestream-os-data` finns ska repot ha en tydlig, mänskligt läsbar `runs/`-ingång för att förklara var runtime-resultat finns och hur de ska förstås.

### Decision 3: Dokumentera legacy explicit

Fallback till `docs/` ska beskrivas som bakåtkompatibilitet i runtime, inte som primär informationsarkitektur.

### Decision 4: Flytta externisering till en separat, konkret nästa leverans

Extern repo-separation är fortfarande en målbild, men ska inte blandas ihop med redan levererade delar av MVP 05.

---

## Vad rebaselinen nu har levererat

Efter denna rebaseline är följande på plats:

- verklig `runs/INDEX.md` i detta repo
- länkning mellan framework-ingången och resultat-ingången
- uppdaterad README och setup-/guideline-dokumentation
- dokumenterat kontrakt för framtida `valuestream-os-data`
- verifierad navigation på dokumentationsnivå

---

## Kända begränsningar

- `valuestream-os-data` är ännu inte etablerat
- `runs/` används både som lokal runtime-yta och som presentationsyta i väntan på externisering
- vissa äldre filer och referenser använder fortfarande `docs/`-språkbruk av kompatibilitetsskäl

---

## Nästa steg efter MVP 05

1. Etablera `valuestream-os-data`
2. Flytta eller publicera relevanta run-resultat dit
3. Uppdatera länkar mellan frameworkrepo och datarepo
4. Avgör om `docs/`-fallback kan avvecklas i kod

---

## Sammanfattning

MVP 05 är inte längre ett arbete med att skapa framework-landningssidor från grunden. Det är nu ett arbete med att:

- stänga gapet mellan levererat och dokumenterat,
- ge `runs/` en verklig interim-ingång,
- och definiera en kontrollerad väg vidare mot externt datarepo.
