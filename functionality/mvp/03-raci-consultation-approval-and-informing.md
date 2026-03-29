# Funktionalitet: 03 – RACI Consultation, Approval and Informing (MVP)

## Metadata

| Fält        | Värde                                     |
| ----------- | ----------------------------------------- |
| ID          | 03                                        |
| Namn        | RACI Consultation, Approval and Informing |
| Version     | 0.1                                       |
| Processsteg | Kravställning                             |
| Ägare       | Agent Core                                |

---

## 1. Syfte

Utöka agentramverket så att det inte bara producerar artifakter enligt `R` i RACI, utan också använder övriga delar av ansvarsmatrisen i själva arbetsflödet:

- `C`: Business Analyst och UX skall kunna konsultera relevanta experter innan artifakter färdigställs
- `A`: Produktägaren skall kunna granska och godkänna eller avslå en artifakt
- `I`: berörda roller skall hållas informerade genom explicita, sparade sammanfattningar som kan användas senare i arbetet
- run-specifik expertkontext skall kunna byggas upp och återanvändas inom aktuell körning

Fokus: visa att RACI kan påverka hur arbetet faktiskt utförs i ramverket, inte bara beskriva ansvar i dokumentation.

---

## 2. Scope (MVP)

### Ingår

- RACI-aware orkestrering för `Kravställning`
- Stöd för att ett producerande steg kan gå igenom faserna:
  - draft
  - consultation
  - revision
  - approval
  - informing
- Konsultation med minst två konkreta `C`-roller:
  - `Verksamhetsexperter`
  - `UX`
- Godkännandeflöde med `Produktägare`
- Informeringsflöde för minst följande `I`-roller:
  - `Projektledare`
  - `Lösningsarkitekt`
  - `Utvecklare`
- Run-specifikt expertunderlag i `runs/<run-id>/` som kan användas av konsultativa agenter inom samma körning
- Filbaserat minne för:
  - konsultationssvar
  - godkännandebeslut
  - informerande sammanfattningar
- Tydlig state för artifaktens livscykel
- Minst ett end-to-end-flöde där en artifakt:
  - skapas av ansvarig agent
  - konsulteras med relevant expert
  - godkänns av produktägare
  - publiceras till informerande roller

### Ingår ej (senare)

- Automatisk upplärning av experter över flera runs
- Globalt delat minne mellan olika runs
- Vector store eller avancerad semantisk retrieval
- Obegränsade feedback-loopar mellan roller
- Fullt stöd för alla RACI-kombinationer i alla processsteg
- Automatisk proaktiv handling från informerade agenter

---

## 3. Arkitekturval (Viktiga beslut)

### RACI skall styra flödet explicit

RACI skall i denna MVP inte bara vara referensdokumentation. Den skall användas av orchestratorn för att avgöra:

- vem som producerar en artifakt
- vilka roller som skall konsulteras
- vem som måste godkänna
- vilka roller som skall informeras efter beslut

Motivering:

- Gör ansvarsmatrisen operativ i stället för passiv
- Ger bättre spårbarhet i varför ett steg väntar, går vidare eller stoppas
- Minskar behovet av hårdkodade specialflöden per artifakt

---

### Konsultation före godkännande

Ett producerande steg skall inte gå direkt från draft till klart när RACI anger `C`.
Artifakten skall först kunna granskas av konsultativa roller och revideras innan den skickas till `A`.

Motivering:

- Förbättrar kvaliteten på underlaget innan beslut tas
- Speglar verkligt arbetssätt bättre än att låta `A` göra all kvalitetskontroll
- Gör `Verksamhetsexperter` och `UX` till verkliga deltagare i flödet

---

### Produktägaren är ett beslutsgate

`Produktägare` skall i MVP:n fungera som ett explicit beslutsgate för utvalda artifakter.

Beslut i MVP:

- `approved`
- `approved_with_notes`
- `rejected`

Motivering:

- Gör `A` tydligt separerad från `R`
- Skapar ett verifierbart stopp eller fortsatt flöde
- Möjliggör tydlig spårbarhet av varför en artifakt accepterades eller skickades tillbaka

---

### Informering skall sparas som rollanpassat minne

`I` i RACI skall i MVP:n inte vara enbart loggning eller utskrift i terminal.
Ramverket skall skapa explicita informationspaket för informerande roller och spara dem i runnen som rollspecifikt minne.

Exempel på innehåll:

- vad som beslutats
- vad som förändrats
- varför det är relevant för rollen
- vilka artifakter rollen bör känna till senare

Motivering:

- Gör informerandet användbart i senare processsteg
- Ger agenter ett kontrollerat sätt att "komma ihåg" viktiga beslut
- Håller minnet filbaserat och transparent

---

### Expertkunskap skall vara run-specifik i MVP

Verksamhetsexpertens kunskap skall i denna MVP byggas upp från underlag i aktuell run och inte som global permanent kunskapsbas.

Det innebär:

- expertrelaterad kontext sparas under `runs/<run-id>/`
- kontexten kan återanvändas i samma run
- kontexten skall vara läsbar och möjlig att justera manuellt

Motivering:

- Följer repository-regeln att runtime data inte blir permanent source of truth
- Minskar risken att blanda kund- eller initiativspecifik kunskap mellan olika körningar
- Räcker för att bevisa värdet av en upplärd expert i första steget

---

## 4. Funktionellt beteende

### 4.1 Initiering av RACI-aware run

När en run startar skall ramverket ladda:

- agentdefinitioner för berörda roller
- RACI för aktuellt processsteg och aktuell artifakt
- input-artifakter för runnen
- run-specifik expertkontext
- tidigare sparade rollsammanfattningar inom samma run

---

### 4.2 Förbereda expertkontext

Innan `Verksamhetsexperter` används skall ramverket kunna bygga en enkel expertkontext från run-specifikt material.

Exempel på källor:

- input-dokument för runnen
- domänspecifika anteckningar
- tidigare konsultationssvar i samma run
- sammanfattningar av redan godkända artifakter

MVP:n behöver inte skapa ett smart expertminne. Den skall skapa ett explicit och återanvändbart expertunderlag för aktuell körning.

---

### 4.3 Producera första utkast

Ansvarig agent enligt `R` producerar ett utkast till artifakten.

I första implementationen skall detta minst fungera för ett `Business Analyst`-drivet flöde.
MVP:n skall dock utformas så att samma konsultations- och godkännandemönster senare kan användas även när `UX` är ansvarig agent.

---

### 4.4 Konsultation med C-roller

När RACI anger `C` skall orchestratorn kunna:

1. Identifiera vilka konsultativa roller som gäller för artifakten
2. Skapa en konsultationsförfrågan med aktuell artifakt och relevanta frågor
3. Köra konsultativa agenter
4. Spara deras svar som explicita konsultationsartefakter eller konsultationsminne
5. Låta producerande agent revidera utkastet baserat på svaren

Första MVP:n skall verifiera detta med:

- `Verksamhetsexperter` för verksamhetsförankring
- `UX` för användbarhet och användarperspektiv där det är relevant

---

### 4.5 Godkännande av A-rollen

När konsultationsfasen är klar skall artifakten skickas till `Produktägare`.

Produktägaren skall kunna:

- godkänna
- godkänna med kommentarer
- avslå och skicka tillbaka för revidering

Beslutet skall sparas explicit tillsammans med motivering.

---

### 4.6 Informera I-roller

När en artifakt är godkänd skall ramverket identifiera alla roller i `I` och skapa rollanpassad information för dem.

För varje informerande roll skall systemet kunna spara:

- roll
- vilka artifakter som är relevanta
- kort sammanfattning
- betydelse för kommande arbete
- eventuell rekommenderad uppmärksamhetspunkt

Första MVP:n skall bevisa detta för:

- `Projektledare`
- `Lösningsarkitekt`
- `Utvecklare`

---

### 4.7 Minne och state

MVP:n skall ha minst följande state- och minnestyper:

- `run state`
- `artifact state`
- `consultation memory`
- `approval memory`
- `informed role memory`

`consultation memory` beskriver vad experter och andra konsultativa roller har bidragit med.
`approval memory` beskriver beslut och motivering från ansvarig beslutsroll.
`informed role memory` beskriver vad informerande roller bör bära med sig senare i runnen.

---

### 4.8 Artifaktstatus

En artifakt i detta flöde skall minst kunna ha följande status:

- `draft`
- `in_consultation`
- `revision_requested`
- `awaiting_approval`
- `approved`
- `approved_with_notes`
- `rejected`
- `published_to_informed_roles`

---

### 4.9 Terminalinteraktion

Interaktion i MVP:n sker fortsatt via terminal.

Exempel på beteenden:

- starta run med konsultation och approval aktiverat
- visa vilka roller som deltar för aktuell artifakt enligt RACI
- visa pågående status för consultation, approval och informing
- visa sparade beslut och rollbriefs

Exakta kommandon definieras senare i planeringen.

---

## 5. Informationsflöde

[User] → [Terminal] → [Orchestrator] → [R-agent] → [C-agenter] → [R-agent revision] → [A-agent] → [I-rollers minne / briefs]

---

## 6. MVP-scope för första implementation

För att hålla detta till ett verkligt MVP skall första implementationen begränsas till:

- 1 processsteg: `Kravställning`
- 1 producerande huvudflöde med `Business Analyst`
- konsultationsmönster som verifieras med:
  - `Verksamhetsexperter`
  - `UX`
- 1 godkännandeagent: `Produktägare`
- 3 informerande roller:
  - `Projektledare`
  - `Lösningsarkitekt`
  - `Utvecklare`
- run-specifik expertkontext lagrad i `runs/<run-id>/`
- filbaserat minne och state utan extern databas

Det är uttryckligen **inte** målet att i denna iteration göra alla roller fullt autonoma eller stödja alla artifakter i hela `Kravställning`.

---

## 7. Definition of Done

- RACI används aktivt av orchestratorn för att styra konsultation, godkännande och informing
- Minst en artifakt går igenom hela kedjan:
  - producerad
  - konsulterad
  - reviderad
  - godkänd
  - informerande publicerad
- `Verksamhetsexperter` kan använda run-specifik expertkontext
- `Produktägare` kan fatta explicit beslut med motivering
- Rollanpassade informationspaket skapas för informerande roller
- Minnesfiler och statefiler sparas under `runs/`
- Flödet är spårbart och kan följas via terminal

---

## 8. Designprinciper

- RACI-aware orchestration
- Consultation before approval
- Approval as explicit gate
- Informing as reusable role memory
- Run-scoped expert context
- Filbaserad transparens i MVP
- Små verifierbara steg
- Tydlig spårbarhet

---

## 9. Risker och avgränsningar

Risker:

- För många roller i första steget kan göra flödet tungt och svårt att verifiera
- Konsultation kan bli för fri om svaren inte struktureras tydligt
- Om informerande minne blir för stort kan det bli svårt att avgöra vad som faktiskt är relevant senare
- Run-specifik expertkontext kan bli för svag om inputunderlaget är otillräckligt

Avgränsningar:

- Expertkunskap skall först vara enkel, explicit och lokal till runnen
- Informerade roller skall i MVP:n få minne och sammanfattningar, inte autonom bevakning
- Produktägaren skall fatta beslut om artifaktstatus, inte skriva om hela artifakten
- Konsultationsloopar skall vara begränsade och spårbara

---

## 10. Nästa steg

- Välj vilka konkreta artifakter i `Kravställning` som skall användas för första verifieringen
- Definiera format för:
  - konsultationsförfrågan
  - konsultationssvar
  - godkännandebeslut
  - informeringsbrief
- Definiera hur run-specifik expertkontext skapas och lagras
- Bestäm hur `Business Analyst` och senare `UX` skall använda samma konsultationsmönster
- Ta fram en detaljerad Cursor-plan med små TODOs för implementation
