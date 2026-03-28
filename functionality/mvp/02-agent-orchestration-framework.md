# Funktionalitet: 02 – Agent Orchestration Framework (MVP)

## Metadata

| Fält        | Värde                          |
| ----------- | ------------------------------ |
| ID          | 02                             |
| Namn        | Agent Orchestration Framework  |
| Version     | 0.1                            |
| Processsteg | Tvärgående / flera processsteg |
| Ägare       | Agent Core                     |

---

## 1. Syfte

Implementera ett första fungerande agentramverk som:

- Använder Microsoft Agent Framework som grund för agentexekvering
- Kan orkestrera flera agenter i ett kontrollerat flöde
- Hanterar artifakter som explicita objekt i ramverket
- Har enkel men tydlig state- och minneshantering
- Exponerar capabilities som återanvändbara byggblock
- Gör det möjligt att migrera befintlig `Business Analyst`-agent in i ramverket

Fokus: visa att grunden för ett verkligt multi-agent-system fungerar, inte att implementera alla framtida agenter direkt.

---

## 2. Scope (MVP)

### Ingår

- Microsoft Agent Framework som exekveringsgrund
- 1 central orchestrator
- 2 agentroller som bevisar arkitekturen
- Gemensam modell för agentdefinitioner
- Gemensam modell för artifakter
- Filbaserad state för körning och artefaktstatus
- Enkel agentminnesmodell för aktuell körning
- Capabilities för:
  - läsa framework-dokumentation
  - läsa och skriva artefakter
  - validera input
  - logga och spåra körning
  - bygga agentcontext från docs
- Enkel interaktion via terminal
- Minst ett end-to-end-flöde där output från en agent används av nästa agent
- Migrering av nuvarande `Business Analyst`-agent så att den körs via ramverket

### Ingår ej (senare)

- Alla framtida agentroller
- GUI eller webbgränssnitt
- Databas
- Vector store eller avancerad semantisk minnesmotor
- Självorganiserande agentnätverk
- Full autonom planering utan explicit orkestrering
- Realtidskommunikation mellan agenter

---

## 3. Arkitekturval (Viktiga beslut)

### Microsoft Agent Framework är obligatoriskt

Denna MVP skall använda Microsoft Agent Framework som grund för agentexekvering och agentinteraktion.
Källa: https://learn.microsoft.com/en-us/agent-framework/overview/?pivots=programming-language-python

Motivering:

- Vi vill etablera rätt teknisk grund innan fler agenter byggs
- Flera kommande roller kräver tydlig orkestrering, samspel och state
- Ramverket behöver kunna växa från en enkel agent till ett verkligt agentsystem

Det innebär:

- Den nuvarande tunna agentadaptern är inte slutarkitekturen
- `Business Analyst` skall migreras in i det nya ramverket
- Nya agentroller skall byggas ovanpå samma gemensamma grund

---

### Explicit orkestrering före autonom komplexitet

MVP:n skall använda en tydlig orchestrator som styr:

- vilken agent som körs
- när den körs
- vilka input den får
- hur output registreras
- hur nästa steg avgörs

Motivering:

- Ger kontroll och spårbarhet
- Är enklare att verifiera
- Följer repository standards om små explicita steg

---

### Filbaserad state och minne i MVP

State och minne skall i MVP:n vara filbaserat och transparent.

Motivering:

- Lätt att förstå och felsöka
- Kräver inte databas i första steget
- Räcker för att bevisa orkestrering, spårbarhet och agentkontext

Det innebär:

- körningsstate sparas i `runs/<run-id>/`
- artefaktstatus sparas explicit
- agentminne begränsas till aktuell körning eller aktuellt arbetsflöde

---

### Capabilities som separata moduler

Gemensamma funktioner skall kapslas som capabilities i stället för att byggas direkt in i varje agent.

Exempel:

- framework context loading
- artifact read/write
- state store
- memory store
- validation
- logging/tracing

Motivering:

- Minskar duplicering
- Gör fler agentroller billigare att implementera
- Skapar ett tydligt kontrakt mellan agent och omgivning

---

## 4. Funktionellt beteende

### 4.1 Initiering av ramverket

Ramverket laddar:

- agentdefinitioner
- rollbeskrivningar från `docs/agents/`
- SOP:er från `docs/SOP/`
- artifaktbeskrivningar från `docs/artifacts/descriptions/`
- artifaktmallar från `docs/artifacts/templates/`
- körningskontext från `runs/<run-id>/`

---

### 4.2 Agentdefinitioner

Varje agent i ramverket skall minst ha:

- identitet
- namn
- syfte
- instruktioner
- ansvarade artifakter
- förväntade input-artifakter
- tillgängliga capabilities
- minnesscope

Målet är att flera agenter skall kunna beskrivas konsekvent utan att varje agent får en egen speciallösning.

---

### 4.3 Orkestrering av agentflöde

Orchestratorn skall kunna:

1. Starta en run
2. Avgöra vilka agentsteg som kan köras
3. Kontrollera att nödvändiga input finns
4. Köra rätt agent via Microsoft Agent Framework
5. Spara producerad artefakt
6. Uppdatera state
7. Göra output tillgänglig för nästa steg
8. Fortsätta, pausa eller stoppa beroende på resultat

---

### 4.4 Artifakter som förstaklassobjekt

Ramverket skall behandla artifakter som explicita objekt, inte bara filer.

Minst följande information skall kunna hållas för en artifakt:

- namn
- filnamn/path
- producerande agent
- konsumerande agent(er)
- status
- version eller senaste uppdatering
- koppling till run

---

### 4.5 State och minne

MVP:n skall ha minst tre typer av state:

- `run state`
- `artifact state`
- `agent memory`

`run state` beskriver vad som händer i en körning.
`artifact state` beskriver vilka artifakter som finns och deras status.
`agent memory` beskriver det arbetsminne agenten behöver inom aktuell körning.

MVP-minnet behöver inte vara avancerat, men det skall vara explicit, läsbart och användbart.

---

### 4.6 Capabilities

Agenter skall inte själva direkt implementera all IO och all ramverkslogik.
De skall använda capabilities för att:

- läsa framework-källor
- läsa input-artifakter
- skriva output-artifakter
- läsa och skriva state
- läsa och skriva minne
- logga beslut och körning
- validera att arbete kan utföras

---

### 4.7 Samarbete mellan två agenter i MVP

MVP:n skall bevisa fleragentssamspel med två tydliga roller.

Exempel på acceptabla första par:

- `Business Analyst` + `UX Analyst`
- `Business Analyst` + `Product Owner`
- `Business Analyst` + en enkel review/godkännandeagent

Minst en agent skall producera en artefakt som nästa agent använder som input.

---

### 4.8 Terminalinteraktion

Interaktion i MVP:n sker via terminal.

Exempel på beteenden:

- visa vilka agenter som finns
- visa vilket flöde som körs
- starta en run
- visa status för steg och artefakter
- visa varför ett steg hoppades över eller stoppades

Exakta kommandon definieras senare i planeringen.

---

## 5. Informationsflöde

[User] → [Terminal] → [Orchestrator] → [Microsoft Agent Framework] → [Agents] → [Capabilities] → [State / Memory / Artifacts]

---

## 6. MVP-scope för första implementation

För att hålla detta till ett verkligt MVP skall första implementationen begränsas till:

- 1 orchestrator
- 2 agentroller
- 1 gemensam capability-modell
- 1 enkel state store
- 1 enkel memory store
- 1 end-to-end-flöde genom minst två steg

Det är uttryckligen **inte** målet att modellera hela organisationen eller alla RACI-roller i denna iteration.

---

## 7. Definition of Done

- Microsoft Agent Framework används i implementationen
- `Business Analyst` körs via det nya ramverket
- Minst en andra agentroll finns och kan köras i samma flöde
- En central orchestrator styr körningen
- Output från en agent används som input till nästa
- Artifakter registreras med explicit state
- Enkel agentminnesmodell används i körningen
- Capabilities används som separata återanvändbara moduler
- Körning och resultat är spårbara i `runs/`
- Flödet kan köras via terminal utan manuell specialhantering i kod

---

## 8. Designprinciper

- MAF-first
- Orchestrator-first
- Explicit state before advanced memory
- Capability-based composition
- Docs som källa för agentcontext
- Filbaserad transparens i MVP
- Små verifierbara steg
- Tydlig spårbarhet

---

## 9. Risker och avgränsningar

Risker:

- Microsoft Agent Framework kan kräva andra abstraktioner än nuvarande kod
- För mycket generalisering för tidigt kan göra MVP:n onödigt tung
- Fler än två agentroller i första steget riskerar att spränga scope

Avgränsningar:

- Om MAF kräver större omstrukturering skall vi ändå hålla första leveransen smal
- Minnesmodellen skall vara enkel först, inte smart först
- Orchestratorn skall vara tydlig och deterministisk i MVP:n

---

## 10. Nästa steg

- Välj vilka två agentroller som skall ingå i första ramverks-MVP:t
- Definiera första end-to-end-flödet
- Definiera agentkontrakt, artifaktkontrakt och statekontrakt
- Bestäm hur nuvarande `Business Analyst` migreras in i ramverket
- Ta fram en detaljerad Cursor-plan med små TODOs för implementation

## Extern styrande referens

Följande dokumentation skall användas som styrande extern referens under planering och implementation av Microsoft Agent Framework-integration:

- [Microsoft Agent Framework Overview (Python)](https://learn.microsoft.com/en-us/agent-framework/overview/?pivots=programming-language-python)
  Planen och implementationen skall särskilt verifiera:
- hur agents definieras i Python
- hur workflows används för multi-agent orchestration
- hur state/session hanteras
- vilka klienter och paket som faktiskt används i Python
- vilka delar som är preview och därför måste isoleras bakom tydliga abstraheringar
