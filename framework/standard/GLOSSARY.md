# ValueStream OS Framework – Fullständig Glossarie

En omfattande ordbok över alla termer, begrepp och koncept som används i ValueStream OS-ramverket.

---

## 📋 Core Framework Concepts

### Agent
En **roll** som exekverar aktiviteter inom ramverket. Agenter har definierade ansvarsområden, perspektiv och arbetsprinciper. Exempel: Business Analyst, Solution Architect, Developer, UX Designer.

**Se också:** [Alla agenter](./agents/)

### RACI (Responsible, Accountable, Consulted, Informed)
En **ansvarsmatris** som definierar för varje artefakt/beslut:
- **R (Responsible)** – Vem gör jobbet?
- **A (Accountable)** – Vem fattar det slutgiltiga beslutet?
- **C (Consulted)** – Vem bör klassas in innan beslut?
- **I (Informed)** – Vem måste informeras efter beslut?

Varje process-fas har sin egen RACI-matris.

**Se också:** [RACI-matriser](./RACI/RACI.md)

### Artifact (Artefakt)
En **output/leverabel** från en process-fas. Artefakter är konkretioner som kan granskas, godkännas och spåras.

Exempel:
- User stories (från Kravställning)
- System landscape diagram (från Målarkitektur)
- Release roadmap (från Roadmap-fasen)

**Se också:** [Alla artefakter](./artifacts/Artifacts.md)

### Capability (Kapabilitet / Förmåga)
En **affärsfunktion** eller **systemförmåga** som kan levereras och värdesättas. Capabilities är ofta grupperade i Epics.

Exempel: "Customer self-service registration", "Real-time payment processing"

**Relaterat:** Epic, User Story

### Epic
En **stor, värdedefinierad gruppering** av relaterade user stories. Epics representerar ett betydande steg mot en capability och kan ofta inte levereras i en enda spurt.

**Relaterat:** Capability, User Story

### Run
En **körning** eller **instans** av ramverket mot ett specifikt initiativ. Varje run producerar ett eget set artefakter, beslut och lärdomar.

**Se även:** Repeat-fasen

---

## 🎯 5-Phase Process Concepts

### Kravställning (WHAT – Phase 1)
**Vad behöver vi bygga?** Fasen där man samlar affärsbehov, användarenas perspektiv och definierar vad som ska byggas.

**Artifacts:**
- Vision & målbild
- Scope & avgränsningar
- User stories
- Epics & capabilities
- User journeys
- Story map
- Prioriterad backlog
- KPI / värdemått

**Se aussi:** [Kravställning Process](./processes/1.%20Kravställning.md)

### Målarkitektur (HOW – Phase 2)
**Hur ska lösningen se ut?** Fasen där man designar den framtida arkitekturen – både tekniskt och strukturellt.

**Artifacts:**
- Arkitekturmål
- Arkitekturprinciper
- Systemlandskap
- Domänmodell
- Begreppsmodell
- Datamodell
- Security model

**Se aussi:** [Målarkitektur Process](./processes/2.%20Målarkitektur.md)

### Roadmap (WHEN – Phase 3)
**När ska det levereras?** Fasen där man planerar sekvens­ering, prioritering och tidsplan för leveranser.

**Artifacts:**
- Release roadmap
- Delivery timeline
- Dependency mapping
- Phase gate criteria

**Se aussi:** [Roadmap Process](./processes/3.%20Roadmap.md)

### Leverans (BUILD – Phase 4)
**Hur bygger vi det?** Fasen där utveckling, testning och lansering genomförs.

**Artifacts:**
- Build plans
- Test cases & results
- Release notes
- Deployment guides

**Se aussi:** [Leverans Process](./processes/4.%20Leverans.md)

### Repeat (LEARN – Phase 5)
**Vad lärde vi oss?** Fasen där man reflekterar, analyserar resultat och planerar nästa iteration.

**Artifacts:**
- Retrospective notes
- Lessons learned
- Decision log
- Adjusted roadmap

**Se aussi:** [Repeat Process](./processes/5.%20Repeat.md)

---

## 📊 Requirement & Analysis Concepts

### User Story
En **kortfattad, strukturerad beskrivning** av ett användarebehov.

Standardformat: "As a [role], I want [feature], so that [value]"

Exempel: "As a customer, I want to reset my password, so that I can regain access to my account"

**Se även:** Epic, Capability, Backlog

### Backlog (Prioriterad Backlog)
En **lista av user stories och features** som är sorterad efter prioritet.

Den prioriterade backloggen är en artefakt från Kravställning som dokumenterar vad som ska byggas först.

**Se även:** User Story, Epic

### User Journey
En **slut-till-slut visualisering** av hur en användare interagerar med ett system för att uppnå ett mål.

User journeys hjälper till att identifiera:
- Användares steg och touchpoints
- Frustration- och glädjemoment
- Möjligheter för improvement

**Se även:** User Story, Capability

### Story Map
En **visuell organisering** av user stories efter användarens perspektiv och prioritet.

Story maps hjälper till att:
- Förstå sambanden mellan stories
- Identifiera kritiska steg
- Planera releases

**Se även:** User Story, Backlog

### Domänmodell
En **konceptuell representation** av affärsdomänen – de enheter, attribut och relationer som är centrala för systemet.

Exempel för en e-commerce domän: Customer, Order, Product, Payment, Inventory

**Se även:** Begreppsmodell, Data Model

### Begreppsmodell
En **abstrakt modell** av de huvudsakliga koncept och relationer utan tekniska detaljer.

En begreppsmodell fokuserar på "VAD" snarare än "HUR".

**Se även:** Domänmodell

---

## 🏗️ Architecture & Design Concepts

### Målarkitektur (Target Architecture)
En **design av den framtida systemarkitekturen** som beskriver hur komponenter, systems och data hänger ihop för att stödja de önskade capabilities.

**Se även:** Systemlandskap, Arkitekturprinciper

### Arkitekturmål (Architecture Goals)
**Strategiska mål** som arkitekturen måste uppfylla.

Exempel: "Achieve 99.99% uptime", "Support 1M concurrent users", "Enable single-sign-on"

### Arkitekturprinciper (Architecture Principles)
**Riktlinjer och regler** som styr arkitekturella beslut.

Exempel: "Prefer open standards", "Minimize external dependencies", "Design for horizontal scalability"

### Systemlandskap (System Landscape)
En **visuell representation** av alla system, tjänster och deras relationer.

Systemlandskapet visar:
- Vilka system vi använder
- Hur de interagerar
- Data flows mellan system

**Se även:** Målarkitektur

### Capability
Se definition under "Core Framework Concepts"

---

## 📈 Metrics & Success Concepts

### KPI (Key Performance Indicator)
En **mätbar indikator** på framgång för ett initiativ.

Exempel KPIs:
- Customer satisfaction score (>8.0)
- Page load time (<2 sec)
- User adoption rate (>50% target users)
- Defect rate (<1%)

### Värdemått (Value Metrics)
Kvantitativa eller kvalitativa **mål** som visar nyttan av en lösning.

Värdemål skiljer sig från KPIs genom att de fokuserar på AFFÄRSVÄRDE snarare än operationell prestanda.

**Se även:** KPI

### Framgångskriterier (Success Criteria)
En **definierad lista av villkor** som måste uppfyllas för att ett initiativ ska anses lyckat.

Framgångskriterier är ofta baserade på KPIs och värdemål.

---

## 🔄 Governance & Workflow Concepts

### Spårbarhet (Traceability)
Förmågan att **länka från affärsbehov → krav → lösning → leverans → resultat**.

God spårbarhet säkerställer:
- Alla krav länkas till ett affärsbehov
- Alla design beslut kan motiveras
- Alla test kan länkas till krav

**Se även:** Artifact, RACI

### Scope & Avgränsningar
Definition av **vad som ingår (IN-scope)** och **vad som inte ingår (OUT-of-scope)** för ett initiativ.

Tydlig scope hjälper till att:
- Hålla fokus på prioriteringar
- Undvika scope creep
- Förstå beroenden

**Se även:** Vision & målbild

### Beroendekarta (Dependency Map)
En **visualisering av beroenden** mellan komponenter, team, system eller leveranser.

Beroendekartor hjälper till att:
- Identifiera kritiska vägar
- Förstå kopplingspunkter
- Planera parallell arbete

---

## 👥 Role & Responsibility Concepts

### Role (Roll)
En **funktion** eller **position** som en person fyller inom ramverket.

Exempel roller: Business Analyst, Solution Architect, Developer, UX Designer, Product Owner, Project Manager

**Se även:** Agent, RACI

### Stakeholder (Intressent)
En **person eller grupp** som är påverkad av eller har intresse i initiativet.

Stakeholders kan vara:
- Slutanvändare
- Affärsägare
- Utvecklare
- Regulatorer

**Se även:** Stakeholder Map

### Stakeholder Map (Stakeholderkarta)
En **matris** som identifierar och klassificerar alla stakeholders baserat på:
- Intresse (high/low)
- Inflytande (high/low)

Stakeholder maps hjälper till att planera **engagemang och kommunikation** för varje grupp.

---

## 📚 Documentation & Process Concepts

### SOP (Standard Operating Procedure)
En **detaljerad how-to guide** för att genomföra en specifik aktivitet.

SOPs är praktiska instruktioner med steg-för-steg anvisningar, mallar och checklistor.

**Se även:** [SOP guides](./SOP/)

### Process Step (Process-steg)
En av de fem **huvudfaserna** i den cirkulära processen:
1. Kravställning
2. Målarkitektur
3. Roadmap
4. Leverans
5. Repeat

**Se även:** [Process Overview](./processes/Process.md)

### Version Control & Traceability
System för att **hålla reda på ändringar** av artifacts över tid.

Version control säkerställer:
- Vi kan se vad som ändrades
- Vi kan förstå VARFÖR det ändrades
- Vi kan rulla tillbaka om behov

---

## 🎯 Decision & Governance Concepts

### Decision Log
En **registrering** av alla större beslut som fattades, med:
- Vad beslutades
- Vem fattade beslutet (Accountable)
- Grund för beslutet
- Datum

**Se även:** RACI, Approval

### Approval (Godkännande)
En **validering** att en artefakt är klar, korrekt och kan användas.

Approvals är ofta definierade i RACI-matriserna.

**Godkännare** är ofta den som är "Accountable" för en artefakt.

---

## 🚀 Delivery & Release Concepts

### Release
En **leverans av en ny version** av ett system till production/användare.

Releases planeras i Roadmap-fasen och genomförs i Leverans-fasen.

**Se även:** Roadmap, Leverans

### Deployment
Det **tekniska** arbetet att installera/lansera en ny version i en miljö (dev, test, prod).

Deployments är en del av Leverans-fasen.

---

## 💡 Quality & Learning Concepts

### Retrospective (Retro)
En **möte** efter en iteration/release där teamet reflekterar över:
- Vad gick bra?
- Vad gick dåligt?
- Vad kan vi förbättra?

Retrospectives är en del av Repeat-fasen.

### Lessons Learned (Lärdomar)
**Insikter och kunskap** som erhålls från en körning/iteration/projekt.

Lärdomar dokumenteras och används för nästa iteration.

**Se även:** Repeat, Retrospective

### Continuous Improvement (Ständig förbättring)
En **kultur och process** för att systematiskt förbättra arbetssätt, kvalitet och resultat.

ValueStream OS-ramverket stöder ständig förbättring genom den cirkulära processen (Repeat → Kravställning → ...).

---

## 📖 Navigation Tips

**Vill du veta mer om ett ord?** Här är många länkade termer – klicka för mer information.

**Fetstilt termer** kan sökas i denna glossarie. **[Länkade termer]** pekar på relaterat innehål i ramverket.

---

**👈 Tillbaka till [Huvudindex](./INDEX.md)**

*Sista uppdatering: 2026-04-01*
