# Funktionalitet: 01 – Business Analyst Agent (MVP)

## Metadata

| Fält        | Värde                  |
| ----------- | ---------------------- |
| ID          | 01                     |
| Namn        | Business Analyst Agent |
| Version     | 0.2                    |
| Processsteg | Kravställning          |
| Ägare       | Agent Core             |

---

## 1. Syfte

Implementera en första fungerande agent som:

- Läser sina instruktioner från rollbeskrivning + SOP:er
- Identifierar vilka artifakter den ansvarar för (R i RACI)
- Kan generera eller uppdatera artifakter baserat på input
- Kan styras via terminal (enkelt gränssnitt)
- Använder LLM för att dynamiskt generera innehåll

Fokus: visa att hela kedjan fungerar, inte perfektion.

---

## 2. Scope (MVP)

### Ingår

- 1 agent: Business Analyst
- Integration med Microsoft Agent Framework
- LLM-baserad generering av artifakter
- Läsa:
  - Rollbeskrivning
  - SOP (två initialt)
  - Artifaktmall
- Generera:
  - 1 artifakt
- Enkel interaktion via terminal

### Ingår ej (senare)

- Flera agenter
- Avancerad orkestrering
- Realtids fillyssning
- Databas

---

## 3. Arkitekturval (Viktigt beslut)

### Microsoft Agent Framework

Agenten skall implementeras med Microsoft Agent Framework från start.

Motivering:

- Undviker omskrivning senare
- Ger naturlig modell för agenter och interaktion
- Passar målbilden med flera agenter

---

### LLM som kärnkomponent

All generering av artifakter skall ske via LLM.

Det innebär:

- Ingen statisk generering
- Ingen hårdkodad text
- All output skapas dynamiskt baserat på:
  - Input-artifakter
  - SOP-instruktioner
  - Artifaktmall

---

## 4. Funktionellt beteende

### 4.1 Initiering av agent

Agenten laddar:

- Roll: docs/Roller/Business Analyst.md
- Relevanta SOP:er: docs/SOP/\*_/_.md
- Artifaktbeskrivningar: docs/Artifakter/Descriptions/\*_/_.md
- Artifaktmallar: docs/Artifakter/Innehåll/\*_/_.md

---

### 4.2 Identifiera ansvar

Agenten skall:

- Identifiera SOP där den är Responsible
- Extrahera artifakter den ansvarar för

---

### 4.3 Hantera input

Input via terminal:

Exempel:

> generate
> update
> list

---

### 4.4 Generera artifakt (LLM)

Flöde:

1. Läs artifaktmall
2. Läs input-artifakter
3. Läs SOP-instruktion
4. Skapa prompt till LLM
5. Generera innehåll
6. Spara som markdown

---

### 4.5 Uppdatera artifakt

- Identifiera förändrade input
- Generera ny version via LLM
- Skriva över eller versionera

---

## 5. Interaktionsmodell

Terminal:

> BA generate
> BA update
> BA list

Terminalen visar en istruktion fö användaren hur man interagerar med agenter.

---

## 6. Informationsflöde

[User] → [Terminal] → [Agent (MAF + LLM)] → [Artifacts]

---

## 7. Definition of Done

- Agent körs via terminal
- Microsoft Agent Framework används
- LLM används för generering
- Minst 1 artifakt genereras korrekt
- Output sparas som markdown

---

## 8. Designprinciper

- LLM-first (ingen statisk logik)
- Filbaserad state
- Minimal implementation
- Tydlig spårbarhet

---

## 9. Nästa steg

- Välj första artifakt
- Definiera input/output
- Skapa första promptmall
