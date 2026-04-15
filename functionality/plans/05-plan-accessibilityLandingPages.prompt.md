# Implementeringsplan: MVP 05 – Accessibility & Landing Pages

## Mål

Den här filen är nu en rebaseline av MVP 05. Branchen har redan genomfört större delen av den ursprungliga leveransen: `framework/standard/`, `framework/light/`, landningssidor, glossary, breadcrumbs och runtime-stöd för framework-varianter finns redan på plats.

Det återstående arbetet fokuserar därför på att:

- synka dokumentation och Definition of Done med faktisk leverans,
- beskriva korrekt separation mellan privat lokal `runs/` och delade resultat i `valuestream-os-data`,
- uppdatera repo- och setup-dokumentation till `framework/`-först,
- dokumentera nästa steg mot `valuestream-os-data`.

**Styrande dokument:** [functionality/mvp/05-accessibility-landing-pages.md](./05-accessibility-landing-pages.md)

---

## Nuläge

### Redan gjort i branchen

- `framework/standard/INDEX.md` och `framework/light/INDEX.md` finns
- `framework/*/GLOSSARY.md` finns
- README-breadcrumbs finns i centrala framework-kataloger
- runtime stöder framework-variant via `src/framework/repo_layout.py`
- stora delar av framework-innehållet har flyttats från äldre struktur till `framework/`

### Inte klart ännu

- dokumentationen behöver fullt ut säga att `runs/` här är privat lokal state
- flera dokument beskriver fortfarande arbetet som om landningssidorna inte vore implementerade
- README och setup-guidelines är fortfarande delvis `docs/`-centriska
- extern repo-separation till `valuestream-os-data` är ännu inte specificerad som färdig leverans

---

## Rebaselined genomförande

### Phase 1: Rebaseline dokumentationen

Syfte: få MVP-, plan- och implementationsdokument att beskriva samma verkliga läge.

- Uppdatera MVP 05-dokumentet så att det skiljer mellan:
  - levererat i denna branch
  - kvar att göra i detta repo
  - senare extern leverans
- Uppdatera denna planfil så att den beskriver nuläget i stället för greenfield-implementation.
- Uppdatera implementation notes så att de inte påstår full completion om `runs`-delen eller externisering återstår.

**Acceptance:** centrala styrdokument är sanningsenliga och konsekventa.

### Phase 2: Beskriv runs på rätt nivå

Syfte: ge stakeholders ett tydligt svar utan att göra lokal `runs/` publik i detta repo.

- Beskriv att runtime skriver lokala resultat under `runs/<run-id>/` som privat arbetsyta.
- Beskriv att delade eller publicerade runs hör hemma i `../valuestream-os-data`.
- Låt `valuestream-os` innehålla templates, kontrakt och instruktioner, men inte committade run-indexfiler.
- Uppdatera framework-index så att det pekar konceptuellt mot datarepot i stället för lokal `runs/`.

**Acceptance:** frågan “var hittar jag körningsresultat idag?” har ett tydligt och sanningsenligt svar.

### Phase 3: Synka README, setup och runtime-berättelsen

Syfte: minska glappet mellan repo-struktur, runtime-beteende och dokumentation.

- Uppdatera `README.md` till `framework/`-först-struktur.
- Uppdatera `setup/README.md` och `setup/guidelines/framework-development-guidelines.md`.
- Förklara `docs/`-fallback som backward compatibility där det fortfarande gäller, inte som primär modell.
- Bekräfta att CLI och loader-beskrivning fortsatt matchar faktisk kod.

**Acceptance:** top-level och setup-dokumentation är konsekvent med runtime och struktur.

### Phase 4: Förbered externisering till valuestream-os-data

Syfte: bryta ut extern repo-separation som en egen, tydlig nästa leverans.

- Dokumentera önskad struktur i `valuestream-os-data`.
- Dokumentera vilka metadatafiler som hör till en publicerad run.
- Dokumentera hur länkar mellan datarepo och frameworkrepo ska fungera.
- Lägg till en kort migrationschecklista.

**Acceptance:** externiseringen kan plockas upp senare utan ny upptäcktsfas.

### Phase 5: Verifiering och stängning

Syfte: avsluta MVP 05 med verifierbar navigation och tydliga restpunkter.

- Verifiera centrala markdown-länkar mellan framework, setup, README och runs.
- Testa stakeholder-flöden för framework-orientering, process/SOP-navigation och run-navigering.
- Dokumentera kvarvarande risker som post-MVP eller nästa PR.

**Acceptance:** MVP 05 kan sammanfattas sanningsenligt i en PR eller release note.

---

## Viktiga designval

1. **Markdown-first** — hela presentationslagret ska kunna läsas direkt i repo och editor.
2. **Framework-varianter i samma repo** — `framework/standard` och `framework/light` möjliggör flera ramverksnivåer utan separat kodbas.
3. **Runs interim före externisering** — ett fungerande lokalt mellanläge är bättre än att vänta på externt repo.
4. **Legacy ska vara explicit** — äldre `docs/`-referenser och fallback-beteenden ska beskrivas som övergångslösningar.

---

## Success Criteria

✅ Framework-landningssidorna är etablerade och behålls som huvudingång.

✅ Dokumentationen berättar samma historia om vad som är gjort och vad som återstår.

✅ `runs/` beskrivs korrekt som privat lokal runtime-yta, medan delade resultat hör hemma i `valuestream-os-data`.

✅ Nästa steg mot `valuestream-os-data` är dokumenterat som separat leverans.

---

**Original plan created:** 2026-04-01
**Rebaselined:** 2026-04-15
