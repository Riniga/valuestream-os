# Funktionalitet: 04 – Målarkitektur som valbart processsteg (MVP)

## Metadata

| Fält        | Värde                         |
| ----------- | ----------------------------- |
| ID          | 04                            |
| Namn        | Målarkitektur som processsteg |
| Version     | 0.1                           |
| Processsteg | 2. Målarkitektur              |
| Ägare       | Agent Core                    |

---

## 1. Syfte

Generalisera befintligt agent- och orkestreringsramverk så att **användaren vid start av en körning uttryckligen väljer vilket processsteg** som ska köras (t.ex. `Kravställning` eller `2. Målarkitektur`).

För valt processsteg `2. Målarkitektur` ska flödet i övrigt fungera **på samma sätt** som för `Kravställning`: samma typer av steg (initiering, beroenden mellan artefakter, agentkörning, state/artefaktspårning, terminalinteraktion där så är implementerat), men **driven av dokumentationen** för det valda steget i stället för hårdkodning eller parallell speciallogik.

Fokus: **generalisering och konfiguration** (SOP-sökvägar, artefaktuppsättning, roller) — inte nya specialfall per artefakt i kod.

---

## 2. Scope (MVP)

### Ingår

- **Processstegval vid start**: användaren anger processsteg när en run startar (t.ex. flagga, prompt eller motsvarande); valet ska vara explicit och sparas i körningskontext (`runs/<run-id>/`) så att orkestrering och loggar är spårbara.
- **Dokumentationsdriven körning för Målarkitektur**:
  - SOP:er under `docs/SOP/2. Målarkitektur/`
  - Artefaktbeskrivningar under `docs/artifacts/descriptions/2. Målarkitektur/`
  - Artifaktmallar under `docs/artifacts/templates/2. Målarkitektur/`
- **Samma orkestreringsmönster som Kravställning**: ordning och beroenden hämtas från process-/SOP-struktur och artefaktmetadata, inte från separata hårdkodade pipelines för varje artefakt.
- **Minimalt end-to-end**: minst ett spår genom steget där nödvändig input (enligt SOP) kan komma från `runs/<run-id>/input/` eller motsvarande befintlig mekanism, och producerade artefakter skrivs enligt samma konventioner som för Kravställning.

### Ingår ej (senare)

- Optimerad parallellisering av alla grenar i processdiagrammet
- Full RACI-automation för alla roller i Målarkitektur (följer prioritering från tidigare MVP:er)
- Nya capabilities som bara gäller Målarkitektur om samma behov inte redan täcks av generiska capabilities

---

## 3. Arkitekturval (viktiga beslut)

### Ett ramverk, flera processsteg

Processsteg ska vara en **parameter i körningen** (konfiguration), inte en separat kodbas. Skillnader mellan `Kravställning` och `2. Målarkitektur` ska främst uttryckas i `docs/` (SOP:er, artefaktbeskrivningar, mallar) och i ev. lättviktsmanifest som pekar ut kataloger.

### Dokumentation ska vara tillräckligt komplett

För att flödet ska kunna fungera utan specialfall ska varje artefakt i steget ha:

- en **beskrivning** under `docs/artifacts/descriptions/2. Målarkitektur/` (syfte, typ, ägare, koppling till SOP)
- där det är relevant en **mall** under `docs/artifacts/templates/2. Målarkitektur/`

Underlåtenhet här tvingar fram tillfälliga hårdkodade undantag och bryter mot syftet med MVP:n.

---

## 4. Funktionellt beteende

### 4.1 Start av körning

1. Användaren **väljer processsteg** (obligatoriskt steg vid start).
2. Ramverket laddar **endast** den dokumentationsprofil som hör till valt steg (SOP-katalog, artefaktbeskrivningar, mallar).
3. Körningsmetadata registrerar valt processsteg för spårbarhet.

### 4.2 Orkestrering

- Samma orchestrator-komponenter som för `Kravställning` används; skillnaden är **vilken uppsättning SOP:er och artefakter** som är aktiv.
- Beroenden mellan artefakter ska kunna härledas från SOP **Input**/**Output** (och vid behov artefaktbeskrivningar), i linje med befintlig design i tidigare MVP:er.

### 4.3 Agenter och roller

- Agenter identifierar ansvar enligt RACI i relevanta SOP:er för det **valda** processsteget.
- Ingen ny agentklass krävs i MVP om befintliga roller kan mappas via dokumentation; tillägg av t.ex. Lösningsarkitekt sker först när det behövs för DoD, och ska återanvända samma agentmönster.

### 4.4 Artefakter

- Artefakter behandlas som förstaklassobjekt på samma sätt som i MVP 02 (namn, path, status, koppling till run).
- Mallar och beskrivningar för Målarkitektur används vid generering/uppdatering på samma sätt som för Kravställning.

---

## 5. Informationsflöde

[User] → [Val av processsteg vid start] → [Terminal / Orchestrator] → [Microsoft Agent Framework] → [Agents] → [Capabilities] → [State / Memory / Artifacts]

Källdata: `docs/SOP/2. Målarkitektur/`, `docs/artifacts/descriptions/2. Målarkitektur/`, `docs/artifacts/templates/2. Målarkitektur/`, samt input under `runs/<run-id>/` (utan att committa `runs/`).

---

## 6. Definition of Done

- Användaren kan **explicit välja `2. Målarkitektur`** vid start av en körning.
- Orchestratorn kör flödet med **samma grundmönster** som för `Kravställning` (ingen parallell “specialmotor” för steget).
- Dokumentationen för steget är **komplett nog** för verktygsstöd: beskrivningar under `docs/artifacts/descriptions/2. Målarkitektur/` för artefakter i MVP-spåret, och motsvarande mallar under `docs/artifacts/templates/2. Målarkitektur/` (en fil per artefakt i spåret, t.ex. `arkitekturmal.md`, `systemlandskap.md`, `domanmodell.md`, `malarkitektur.md`).
- Minst **ett end-to-end-spår** producerar och lagrar artefakter för Målarkitektur enligt filkonventioner som redan gäller för Kravställning.
- Resultat och val av processsteg är **spårbara** i `runs/<run-id>/` (utan att checka in `runs/` i git).

---

## 7. Designprinciper

- **Konfiguration före specialfall** — välj processsteg, ladda rätt `docs/`-profil.
- **Samma orkestreringssemantik** för alla processsteg i MVP.
- **Docs som källa** för kontext, beroenden och mallar.
- **Små, verifierbara steg**; undvik duplicerad logik per processsteg.

---

## 8. Risker och avgränsningar

**Risker:**

- Vissa SOP:er listar input från Kravställning som måste finnas i `input/` för ett realistiskt spår; brist på input kan stoppa flödet (förväntat tills steg kedjas i senare iteration).
- Flera parallella grenar i processdiagrammet kan förenklas sekventiellt i första implementation.

**Avgränsningar:**

- MVP bevisar **generalisering och ett spår**, inte full täckning av alla RACI-kombinationer eller alla grenar dag ett.

---

## 9. Nästa steg

- Implementera processstegval i befintlig orchestrator-initiering.
- Koppla manifest eller sökvägskonvention till `docs/SOP/2. Målarkitektur/` och artefaktkatalogerna.
- Välj minsta agentuppsättning som täcker Responsible enligt SOP för det första end-to-end-spåret.
- Verifiera mot artefaktlistan i `docs/artifacts/Artifacts.md` och processbeskrivningen i `docs/processes/2. Målarkitektur.md`.
