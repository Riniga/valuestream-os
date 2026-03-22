# ValueStream OS
Agent Orchestration Framework for end-to-end value delivery.


## Syfte
Bygga ett fungerande ramverk för att hantera agenter som kan utföra uppgifter kopplade till mjukvaruutvecking.
ramverket levererar samtliga komponenter i form av artifakter som behövs för stabil och kvalitativ leverans av värde i organisationen

Fokus:
- Bygg fungerande flöden före optimering
- Tydligt mål -> Iterera stegvis
- Undvika överdesign i början

---

## Grundprinciper
- Mycket mycket tydligt flöde, hårt kopplat till
  - Processsteg
  - SOP:er
  - Roller i RACI
  - Artifakter som input och output
- Textbaserade filer är kärnan i systemet
- Agenter kodas för att tydligt genomföra SOP:er med input och leverarar output

---

## Projektstruktur

### 1. Agent Core
Ansvar:
- Definiera agenter (roller)
- Enkel kommunikation mellan agenter
- Utföra uppgifter baserat på instruktioner

Teknik:
- Microsoft Agent Framework

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

## Processstruktur

### Process uppdelad i processsteg
En repeterbar, hållbar och skalbar process för att gå från 1.Kravställning → 2. Målarkitektur → 3. Roadmap → 4. Leverans → 5. Repeat → ny iteration.
Dokumentation: /Process.md

### Processsteg uppdlat i delprocesser
Tydlig beskrivning VAD steget syftar till att uppnå i processen
Länk till SOP som sedan beskriver HUR.
Dokumentation: /Processer/N.Processstegnamn.md

### SOP (Standard Operating Procedure)
Används för att beskriva hur en roll (eller agent) skall arbeta för att uppnå målet med processsteget.
  - Syfte: VAd är syftet med denna process
  - Context: Vilket processsteg är det vi skall slutföra poå formen Processteg/Delprocess
  - Input och Output: Vilka artifakter använder vi och vilka skall vi leverera
  - RACI: Vilka roller behöver agera och informeras för att slutföra steget
  - Arbetssteg: Konkret arbetslista
Dokumentation: /SOP/N.Processstegnamn/M.SOP.md
  
### Artifakter
Detta är filer, media, referenser, kodpaket etc som nytjas av agenter och mäniskor.

#### Artifaktbeskrivng 
Samtliga artifakter beskrivs med förljande egenskaper
- Artifaktnamn
- Typ: markdown, kodreferens, etc
- Beskrivning
- Ägare (referens till den som skapar R i RACI)
- Skapad i: SOP (referens till SOP, som skapar artifakten)
- Används i: Lista på SOP som behöver denna artifakt
- Format: Textdokument (Markdown), Kodrefersn
Dokumentation: /Artifakter/Beskrivning/N.Processstegnamn/Artifaktnamn.md

#### Artifaktmall
Mall med rubriker och innehåll som förväntas av agenten att fylla i, men några generalla fält är
- Artifakttyp
- Skapara
- Datum och tid
- Syfte
Dokumentation: /Artifakter/Mallar/N.Processstegnamn/Artifaktnamn.md

### Roller
De roller som vi identifierats som behövs för att kunna genomföra arbete i SOP:er
Följande egenskaper dokumnteras för dessa:
- Namn
- Beskrivning
- Kompetens
Dokumentation: /Roller/Rollnamn.md

### RACI
Tydliggörande för mappningen mellan SOP:er och Roller
Med tabell och Diagram
Dokumentation: /RACI/N.Processstegnamn.md