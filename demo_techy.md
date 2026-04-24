# Demo av ValueStream OS (tech edition)

Agent Orchestration Framework for end-to-end value delivery

Detta dokument är ett **presentatörsstöd för dig**, inte ett manus för åhörarna.

Använd det för att:

- hålla tempo och struktur
- veta vad du vill få fram i varje del
- ha stödord att tala fritt utifrån
- snabbt hitta tillbaka om du scrollar fel

---

# Presentationens fokus

## Målgrupp

- teknikintresserad publik
- vana vid kod, arkitektur, automation och AI/agent-koncept
- vill förstå struktur, styrning, spårbarhet och faktisk körbarhet

## Scope för denna presentation

Detta fokus ska vara tydligt direkt i början:

- visa att ValueStream OS är ett **sammanhängande system**
- visa hur **README -> ramverk -> körning -> resultat** hänger ihop
- visa att detta är **körbart i praktiken**, inte bara beskrivningar i markdown
- visa att struktur, roller, SOP:er, artefakter och runs ger **kontroll**

Detta är **inte** fokus i denna presentation:

- full teknisk implementation i `src/`
- all intern logik eller all kod bakom CLI:t
- full genomgång av varje enskild fil i ramverket

## Önskad känsla

- konkret
- lugn
- kontrollerad
- transparent
- text-first, repo-first, CLI-first

## Innehåll

Total tid: cirka **25 min**

1. Projektet README - **4 min**
2. Ramverket / Processen - **7 min**
3. Live demo - CLI - **6 min**
4. Resultatet - **5 min**
5. Tekniken - **3 min**

---

# 0. Intro och inramning

**Tid:** 2 min

**Syfte med sektionen:** Sätta målgrupp, scope och röd tråd innan du går in i detaljer.

## Punkt 0.1 - Vad publiken ska titta efter

**Tid:** 1 min

**Syfte:** Hjälpa publiken att förstå vad presentationen fokuserar på.

**Stödord:**

- detta är inte "bara AI"
- detta är ett arbetssätt + ramverk + körning
- fokus på struktur, styrning, spårbarhet
- jag visar sammanhang, inte varje detalj

## Punkt 0.2 - Röd tråd för resten av presentationen

**Tid:** 1 min

**Syfte:** Ge en enkel karta att återkomma till genom hela presentationen.

**Stödord:**

- från behov till levererat värde
- README sätter bilden
- ramverket beskriver modellen
- CLI visar att modellen går att köra
- resultatet visar vad en run faktiskt ger

---

# 1. Projektet README

**Tid:** 4 min

**Syfte med sektionen:** Förankra vad ValueStream OS är på hög nivå innan du zoomar in i detaljer.

**Visa:**

- [`README.md`](https://github.com/Riniga/valuestream-os/blob/prepare-demo-2/README.md)

## Punkt 1.1 - Vad projektet är

**Tid:** 1 min

**Syfte:** Sätta den övergripande definitionen av ValueStream OS.

**Stödord:**

- agent orchestration framework
- från idé till levererat värde
- inte bara prompts
- kontrollerad exekvering

## Punkt 1.2 - Den cirkulära modellen

**Tid:** 1 min

**Syfte:** Visa att modellen bygger på ett återkommande flöde, inte en engångskedja.

**Stödord:**

- `WHAT -> HOW -> WHEN -> BUILD -> LEARN -> WHAT`
- lärande tillbaka in i nästa cykel
- repeat som del av modellen

## Punkt 1.3 - Hur repot är uppdelat

**Tid:** 1 min

**Syfte:** Ge en enkel mental modell av repots huvuddelar.

**Stödord:**

- `framework/` = styrmodell
- `src/` = implementation/motor
- `runs/` = körningar, tillstånd, output
- `setup/` = setup och utvecklingsstöd

## Punkt 1.4 - Vad publiken ska ta med sig från README

**Tid:** 1 min

**Syfte:** Avsluta sektionen med en tydlig landning innan du går vidare.

**Stödord:**

- README beskriver varför och helheten
- nu går vi från idé till faktisk struktur
- nästa steg: hur ramverket organiserar arbetet

---

# 2. Ramverket / Processen

**Tid:** 7 min

**Syfte med sektionen:** Visa att ramverket är explicit uppbyggt kring process, ansvar, instruktioner och artefakter.

**Visa:**

- [`framework/standard/INDEX.md`](./framework/standard/INDEX.md)
- [Kravställning](./framework/standard/processes/1.%20Kravställning.md)
- [Målarkitektur](./framework/standard/processes/2.%20Målarkitektur.md)
- [Roadmap](./framework/standard/processes/3.%20Roadmap.md)
- [Leverans](./framework/standard/processes/4.%20Leverans.md)
- [Repeat](./framework/standard/processes/5.%20Repeat.md)

## Punkt 2.1 - De fem processstegen

**Tid:** 2 min

**Syfte:** Göra processlogiken tydlig och enkel att följa.

**Stödord:**

- vad behöver vi
- hur ska det fungera
- när gör vi vad
- hur bygger vi
- vad lärde vi oss

## Punkt 2.2 - Ramverkets delar

**Tid:** 2 min

**Syfte:** Visa att olika dokumenttyper har tydliga roller i samma system.

**Visa även vid behov:**

- [agents/](./framework/standard/agents/)
- [processes/](./framework/standard/processes/)
- [RACI/](./framework/standard/RACI/)
- [SOP/](./framework/standard/SOP/)
- [artifacts/](./framework/standard/artifacts/)

**Stödord:**

- process = flöde
- RACI = ansvar
- SOP = hur ett steg körs
- artifacts = input/output
- agents = roller som utför

## Punkt 2.3 - Ett konkret spår: Kravställning

**Tid:** 2 min

**Syfte:** Visa hur delarna faktiskt kopplas ihop i praktiken.

**Visa:**

- [process: Kravställning](./framework/standard/processes/1.%20Kravställning.md)
- [RACI: Kravställning](./framework/standard/RACI/1.%20Kravställning.md)
- [agent: Business Analyst](./framework/standard/agents/business-analyst.md)
- [SOP: Skapa beställning](./framework/standard/SOP/1.Kravställning/01_skapa_bestallning.md)
- [SOP: Sammanhållen kravanalys](./framework/standard/SOP/1.Kravställning/02_sammanhallen_kravanalys.md)
- [artefaktmall: bestallning.md](./framework/standard/artifacts/templates/1.Kravställning/bestallning.md)
- [artefaktbeskrivning: Beställning](./framework/standard/artifacts/descriptions/1.Kravställning/bestallning.md)

**Stödord:**

- process säger när/varför
- SOP säger hur
- RACI säger vem
- artefakt säger vad som produceras
- agenten utför i rätt kontext

## Punkt 2.4 - Kärnbudskapet i ramverket

**Tid:** 1 min

**Syfte:** Få publiken att förstå varför denna struktur är viktig.

**Stödord:**

- mindre improvisation
- mer explicit styrning
- bättre spårbarhet
- mer repeterbart arbetssätt

---

# 3. Live demo - CLI

**Tid:** 6 min

**Syfte med sektionen:** Visa att ramverket inte bara är beskrivet utan faktiskt går att köra.

**Visa:**

- terminal / kommandoprompt

**Bra länkar att ha redo:**

- [agentmanifest](./framework/standard/agents/manifest.json)
- [processöversikt](./framework/standard/processes/Process.md)
- [setup/README.md](./setup/README.md)

## Punkt 3.1 - CLI som exekveringsyta

**Tid:** 1 min

**Syfte:** Sätta förväntan på varför du visar terminalen.

**Stödord:**

- transparent
- snabbt för teknisk publik
- visar att modellen är körbar
- poängen är inte UI, poängen är exekvering

## Punkt 3.2 - Visa några grundkommandon

**Tid:** 2 min

**Syfte:** Ge känslan av att systemet har verkliga kommandon och tillstånd.

**Stödord:**

- lista agenter
- visa process/flöde
- starta run
- visa status

## Punkt 3.3 - Starta en enkel run

**Tid:** 3 min

**Syfte:** Visa hur en beställning blir input till en faktisk körning.

**Visa:**

- [mallen för `bestallning.md`](./framework/standard/artifacts/templates/1.Kravställning/bestallning.md)
- [input-exempel: `runs/test-01/input/bestallning.md`](./runs/test-01/input/bestallning.md)
- [process: Kravställning](./framework/standard/processes/1.%20Kravställning.md)
- [SOP: Skapa beställning](./framework/standard/SOP/1.Kravställning/01_skapa_bestallning.md)

**Stödord:**

- börja i behov, inte kod
- enkel mall
- lägg input i run
- starta körning
- ramverket tar över nästa steg

---

# 4. Resultatet

**Tid:** 5 min

**Syfte med sektionen:** Visa vad en run faktiskt producerar och varför resultatet är användbart.

**Visa:**

- [runs/test-01/output/INDEX.md](./runs/test-01/output/INDEX.md)

**Bra länkar att ha redo:**

- [run state](./runs/test-01/run_state.json)
- [artifact state](./runs/test-01/artifact_state.json)
- [run log](./runs/test-01/run_log.json)
- [approval decisions](./runs/test-01/approval_decisions.json)
- [consultation requests](./runs/test-01/consultation_requests.json)
- [consultation responses](./runs/test-01/consultation_responses.json)
- [informed role briefs](./runs/test-01/informed_role_briefs.json)
- [exempelartefakt: vision och målbild](./runs/test-01/output/vision_och_malbild.md)
- [exempelartefakt: målarkitektur](./runs/test-01/output/malarkitektur.md)
- [exempelartefakt: roadmap](./runs/test-01/output/Roadmap.md)

## Punkt 4.1 - Output-index som ingång

**Tid:** 2 min

**Syfte:** Visa att resultatet går att överblicka och navigera.

**Stödord:**

- run id
- status
- senaste process
- antal huvudartefakter
- snabb överblick

## Punkt 4.2 - Resultat grupperat per processsteg

**Tid:** 1 min

**Syfte:** Visa att outputen följer verksamhetsflödet, inte bara filstruktur.

**Stödord:**

- grupperat enligt processen
- mänskligt läsbart
- lätt att förstå vart man är

## Punkt 4.3 - Metadata och spårbarhet

**Tid:** 2 min

**Syfte:** Visa varför detta är mer robust än bara genererade dokument.

**Stödord:**

- `run_state.json`
- `artifact_state.json`
- `run_log.json`
- approvals
- consultations
- informed briefs

---

# 5. Tekniken

**Tid:** 3 min

**Syfte med sektionen:** Runda av med den tekniska betydelsen och visa tillräckligt mycket implementation för att det ska kännas verkligt för en teknisk publik.

## Punkt 5.1 - Kodstruktur: hur detta är uppbyggt i kod

**Tid:** 1 min

**Syfte:** Visa hur repots struktur går från markdown-ramverk till körbar orchestration i `src/`.

**Visa:**

- [`src/orchestration/orchestrator.py`](./src/orchestration/orchestrator.py)
- [`src/orchestration/process_loader.py`](./src/orchestration/process_loader.py)
- [`src/orchestration/agent_registry.py`](./src/orchestration/agent_registry.py)
- [`src/framework/models.py`](./src/framework/models.py)
- [AI-arkitektur och datalager](./setup/architecture/05-ai-architecture.md)

**Stödord:**

- `framework/` beskriver modellen
- `src/orchestration/` gör modellen körbar
- `process_loader` läser process + SOP + RACI
- `agent_registry` mappar roller till agenter via manifest
- `models.py` håller gemensamma kontrakt för run, steg, artefakter, approvals

## Punkt 5.2 - MAF: vad det är och hur det används här

**Tid:** 1 min

**Syfte:** Förklara kort varför Microsoft Agent Framework är relevant i lösningen.

**Visa:**

- [`src/framework/maf_adapter.py`](./src/framework/maf_adapter.py)
- [`src/agents/ux/agent.py`](./src/agents/ux/agent.py)

**Stödord:**

- MAF = Microsoft Agent Framework
- används som exekveringslager för agentanrop
- vi har lagt det bakom en tunn adapter
- preview-detaljer isoleras i en fil
- övrig orchestration behöver inte känna till SDK-detaljer

## Punkt 5.3 - Azure OpenAI och OpenAI: plattform och modellval

**Tid:** 1 min

**Syfte:** Visa att plattform och modell går att byta utan att skriva om orchestrationen.

**Visa:**

- [`src/framework/maf_adapter.py`](./src/framework/maf_adapter.py)
- [`setup/environment/.env.example`](./setup/environment/.env.example)

**Stödord:**

- stöd för både `Azure OpenAI` och `OpenAI`
- val sker via environment variables
- Azure: endpoint, deployment, API-version
- OpenAI: API key + modellnamn
- modellval är konfigurerat, inte hårdkodat i flödet

## Punkt 5.4 - Vad som skiljer detta från "bara prompts"

**Tid:** 1 min

**Syfte:** Tydliggöra differensen mot enklare AI-användning.

**Stödord:**

- mindre magi
- mer struktur
- mindre ad hoc
- mer kontroll
- lättare att följa upp

## Punkt 5.5 - Avslutande landning

**Tid:** 1 min

**Syfte:** Ge publiken ett tydligt sista budskap.

**Stödord:**

- exekverbart ramverk
- gemensam struktur för människor och agenter
- användbart + spårbart
- går att börja enkelt och skala upp

---

# Om tiden blir knapp

Prioritera i denna ordning:

1. [README.md](./README.md)
2. [framework/standard/INDEX.md](./framework/standard/INDEX.md)
3. [Kravställning](./framework/standard/processes/1.%20Kravställning.md)
4. CLI-körning
5. [runs/test-01/output/INDEX.md](./runs/test-01/output/INDEX.md)

Hoppa över:

- djupdykning i alla RACI-varianter
- för många detaljer i enskilda SOP:er
- för mycket implementation i `src/`

---

# Om publiken vill gå djupare tekniskt

Bra spår att öppna:

- hur optional artifacts fungerar
- hur approvals / consultations / informed briefs lagras
- hur output index byggs upp
- hur ett processsteg laddas från `framework/standard`
- skillnaden mellan ramverk (`framework/`) och exekvering (`runs/`)
- hur agentval och RACI-roll kopplas via manifest
- hur provider- och modellval styrs via `.env`
- hur AI-lagren hänger ihop med ramverk och kod

Relevanta länkar:

- [AI-arkitektur och datalager](./setup/architecture/05-ai-architecture.md)
- [Output-indexspec](./framework/standard/Output_INDEX.md)
- [exempel på output-index](./runs/test-01/output/INDEX.md)
- [glossary](./framework/standard/GLOSSARY.md)
- [agentmanifest](./framework/standard/agents/manifest.json)
- [`src/framework/maf_adapter.py`](./src/framework/maf_adapter.py)
- [`src/orchestration/orchestrator.py`](./src/orchestration/orchestrator.py)
- [`src/orchestration/process_loader.py`](./src/orchestration/process_loader.py)
- [`setup/environment/.env.example`](./setup/environment/.env.example)

---

# Snabb minnesregel

Om du tappar tråden, gå tillbaka hit:

**README -> Process -> Roller -> SOP -> Körning -> Resultat -> Teknisk poäng**
