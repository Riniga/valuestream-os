# Agent Framework Project

## Syfte
Bygga ett enkelt men fungerande ramverk för att hantera agenter som kan utföra uppgifter kopplade till utveckling, baserat på SOP:er (Standard Operating Procedures).

Fokus:
- Få något fungerande snabbt
- Iterera stegvis
- Undvika överdesign i början

---

## Grundprinciper
- Arbeta i små steg
- Bygg fungerande flöden före optimering
- All funktionalitet ska vara testbar i praktiken
- Enkelhet före flexibilitet (initialt)
- Textbaserade filer är kärnan i systemet

---

## Projektstruktur

### 1. Agent Core
Ansvar:
- Definiera agenter (roller)
- Enkel kommunikation mellan agenter
- Utföra uppgifter baserat på instruktioner

Teknik:
- Microsoft AutoGen (initialt)

---

### 2. Capabilities (Verktyg)
Ansvar:
- Exponera funktioner som agenter kan använda
- Enkla wrapper-funktioner (API:er, filer, scripts)

Exempel:
- Läsa/skriva filer
- Anropa API:er
- Generera innehåll

---

### 3. Orchestration (SOP-exekvering)
Ansvar:
- Köra SOP:er steg för steg
- Styra flöde mellan agenter
- Hantera enkel sekvensering (ingen komplex logik initialt)

Initial strategi:
- Kodbaserad orkestrering
- Ingen extern workflow-motor i början

---

### 4. Memory / State
Ansvar:
- Spara pågående arbete
- Lagra resultat från körningar
- Möjliggöra enkel återupptagning

Initial implementation:
- Filer (JSON / Markdown)
- Ingen databas i första versionen

---

## SOP-hantering

- SOP:er lagras som Markdown-filer
- Varje SOP beskriver:
  - Syfte
  - Steg
  - Förväntat resultat

Exempelstruktur:

```markdown
# SOP: Example

## Syfte
Beskriv vad denna SOP gör

## Steg
1. Gör detta
2. Gör detta
3. Gör detta

## Output
Vad ska produceras