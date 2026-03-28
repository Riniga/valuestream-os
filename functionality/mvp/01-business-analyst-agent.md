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
- En tunn agentadapter för LLM-anrop
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

### Agentadapter + LLM-klient

Agenten implementeras i MVP:n som en tunn agentadapter i Python som laddar instruktioner från dokumentationen och anropar LLM via OpenAI Responses API eller Azure OpenAI Responses API.

Motivering:

- Ger en minimal men fungerande exekveringsyta för första agenten
- Håller integrationen enkel och explicit i MVP:n
- Bevarar möjligheten att senare kapsla in en mer avancerad agentplattform

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

- Roll: `docs/agents/business-analyst.md`
- Relevanta SOP:er: `docs/SOP/**/*`
- Artifaktbeskrivningar: `docs/artifacts/descriptions/**/*`
- Artifaktmallar: `docs/artifacts/templates/**/*`

---

### 4.2 Identifiera ansvar

Agenten skall:

- Identifiera SOP där den är Responsible
- Extrahera artifakter den ansvarar för

---

### 4.3 Hantera input

Input via terminal:

Exempel:

> info
> update
> run

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

> BA info
> BA update
> BA run

Terminalen visar en istruktion fö användaren hur man interagerar med agenter.

---

## 6. Informationsflöde

[User] → [Terminal] → [Agentadapter + LLM] → [Artifacts]

---

## 7. Definition of Done

- Agent körs via terminal
- LLM-agentadapter används
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
