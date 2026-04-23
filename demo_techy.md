# Demo av ValueStream OS (tech edition)

Agent Orchestration Framework for end-to-end value delivery

## Syfte med denna demo

På cirka 25 minuter ska du få en tekniskt trovärdig och inspirerande bild av:

- vad ValueStream OS faktiskt är
- hur `framework/standard` hänger ihop
- hur CLI och körning fungerar i praktiken
- vad en run faktiskt producerar

Efter demon ska du ha en tydlig bild av att detta inte bara är "några agenter", utan ett explicit system där process, roller, ansvar, artefakter och körning hänger ihop.

## Målgrupp och ton

- Teknikintresserad publik
- Van vid kod, arkitektur, automatisering och AI/agent-koncept
- Intresserad av struktur, spårbarhet och hur lösningen faktiskt fungerar

Presentationen bör upplevas som:

- konkret
- transparent
- ingen powerpoint, bara repo, markdown och CLI
- visa att lösningen är begriplig och praktiskt användbar

## Agenda

1. **Varför denna lösning finns**
2. **Den övergripande modellen**: process + repo + text-first
3. **Hur standardramverket är uppbyggt**
4. **Hur ansvar och exekvering kopplas ihop**: RACI -> roller -> agenter -> SOP -> artefakter
5. **Hur det körs i CLI**
6. **Vad man faktiskt får ut av en run**

---

# Upplägg: 25 minuter

## 0. Öppning och framing - 2 min

### Visa

- [`README.md`](https://github.com/Riniga/valuestream-os/blob/prepare-demo-2/README.md)

### Budskap

"Det här är ett ramverk för att gå från idé till levererat värde med hjälp av agenter, men på ett kontrollerat sätt."

### Det här ska du få med dig

"Här blir det tydligt att det inte bara handlar om att generera dokument med AI. Det intressanta är att vi har byggt ett sammanhängande system där process, roller, ansvar, instruktioner och resultat hänger ihop."

"Det innebär att utvecklingsarbete kan bedrivas på ett mer strukturerat, spårbart och repeterbart sätt."

### Lyft fram i README

- syftet
- den cirkulära modellen
- `WHAT -> HOW -> WHEN -> BUILD -> LEARN -> WHAT`
- repository-strukturen:
  - `framework/`
  - `src/`
  - `runs/`
  - `setup/`

### Kärnpoäng att landa i

- `framework/` är hjärnan
- `src/` är motorn
- `runs/` är exekveringen och tillståndet

---

## 1. Förklaring av ramverket: standard - 6 min

### Visa

- `framework/standard/INDEX.md`

### Det här ska du förstå

"README beskriver idén. Standardramverket beskriver hur arbetet faktiskt ska gå till."

"Det viktiga här är att utgångspunkten inte är kod, utan verksamhetsflöde, ansvar och definierade resultat."

### Gå igenom i denna ordning

#### A. De 5 processstegen

Lyft fram:

- Kravställning
- Målarkitektur
- Roadmap
- Leverans
- Repeat

Poängen här är:

"De här fem stegen motsvarar egentligen fem olika frågor:
vad behöver vi, hur ska det fungera, när gör vi vad, hur bygger vi, och vad lärde vi oss."

"Det fina är att Repeat inte är slutet, utan input till nästa cykel."

#### B. Strukturen i ramverket

Lyft fram:

- `agents/`
- `processes/`
- `RACI/`
- `SOP/`
- `artifacts/`

Poängen här är:

"Det här är den viktiga modellen:
processen beskriver flödet,
RACI beskriver ansvar,
SOP beskriver hur ett steg utförs,
artefakterna beskriver vad som kommer in och ut,
och agenterna är de roller som utför arbetet."

#### C. Förklarar begreppen i rätt relation

En enkel förklaring att använda:

- **Process** = i vilken ordning saker händer
- **RACI** = vem som ansvarar, godkänner, konsulteras och informeras
- **Agent/roll** = vem som faktiskt utför ett steg
- **SOP** = instruktionen för en sittning
- **Artefakt** = resultatet eller underlaget

Poängen här är:

"Det viktiga är att de här inte är separata dokumenttyper. De är kopplade till varandra."

"En agent kör en SOP, inom ett processsteg, med en viss RACI-kontext, och producerar definierade artefakter."

---

## 2. Visa ett konkret spår i ramverket - 4 min

### Visa

- `framework/standard/processes/1. Kravställning.md`
- gärna kort ett RACI-dokument
- gärna en agentfil, till exempel Business Analyst
- gärna artefaktmall för `bestallning.md`

### Det här ska publiken förstå

"Nu zoomar vi in på ett enda konkret spår, så att man ser hur allt hänger ihop i praktiken."

### Rekommenderad ordning

1. Visa processfilen för `1. Kravställning`
2. Visa att delprocess pekar mot SOP
3. Visa RACI för samma område
4. Visa agent/roll, till exempel Business Analyst
5. Visa artefaktmall eller artefaktbeskrivning

### Det publiken ska förstå

- Processen beskriver _varför och i vilken ordning_
- SOP beskriver _hur_
- RACI beskriver _vem_
- Artefakten beskriver _vad som produceras_

### Formulering att kunna använda

"Om man bara har prompts får man ofta magi men låg styrning. Här försöker vi i stället göra exekveringen explicit."

"Det är därför vi kan få både bättre kvalitet och bättre spårbarhet."

---

## 3. Introducera CLI och hur man kör - 3 min

### Visa

- terminal / kommandoprompt

### Det här ska publiken förstå

"All exekvering sker idag via CLI. Det är medvetet. För en teknisk publik är det här det snabbaste sättet att visa att systemet faktiskt fungerar och att allt är transparent."

### Visa några kommandon

Välj det som finns tillgängligt hos dig, men håll det kort.

Exempel på vad du kan visa:

- att lista agenter
- att visa process/flöde
- att starta en run
- att visa status för en run

### Viktigt budskap

"Poängen är inte CLI:t i sig. Poängen är att ramverket är körbart."

"Det här är alltså inte bara dokumentation, utan en exekverbar modell."

---

## 4. Live demo: skapa beställning och starta run - 4 min

### Visa

- en ny run
- `bestallning.md`
- kommandot för att köra

### Rekommenderat upplägg

1. Börja från ett behov
2. Visa att du använder mallen för `bestallning.md`
3. Lägg filen i en ny runs input-mapp
4. Starta körningen i CLI

### Det här ska publiken få se

"Demot börjar inte i kod, utan i ett verkligt verksamhetsbehov."

"Det första steget är att formulera en beställning i en enkel mall. Den blir startpunkten för hela flödet."

"När den läggs in i en run kan ramverket ta vid och producera nästa lager av underlag."

### Tips

Försök inte läsa hela beställningen i detalj. Visa bara att:

- den är enkel att förstå
- den är tillräckligt strukturerad
- den kan användas som input till körningen

---

## 5. Medan runnen kör: hoppa till tidigare resultat - 4 min

### Visa

- `runs/test-01/output/INDEX.md`

### Det här ska publiken förstå

"I stället för att vänta på att allt ska köras klart kan vi titta på en tidigare körning och se vad systemet faktiskt producerar."

"Det här är en viktig poäng: outputen är inte bara en hög med filer. Vi har nu ett index som gör runnen begriplig."

### Gå igenom output-INDEX i denna ordning

#### A. Runsammanfattning

Lyft fram:

- run id
- status
- senaste process
- antal huvudartefakter
- approvals / consultations / briefs

Det här visar:

"Det här ger direkt en överblick över vad som faktiskt hänt i runnen."

#### B. Genererat innehåll per processsteg

Lyft fram att output är grupperat enligt de fem processerna.

Det här visar:

"Det här är viktigt för att resultatet ska vara läsbart även för människor. Vi ser inte bara filer, utan resultat grupperat enligt verksamhetsflödet."

#### C. Metadata och spårbarhet

Lyft kort fram:

- `run_state.json`
- `artifact_state.json`
- `run_log.json`
- approvals
- consultations
- informed briefs

Det här visar:

"För techfolk är det här kanske den mest intressanta delen: vi har inte bara producerat artefakter, utan också spår av beslut, konsultationer och status."

"Det gör lösningen mer användbar i verkligheten än om man bara genererar slutdokument."

---

## 6. Avslutning: vad som är nytt och varför det spelar roll - 2 min

### Sammanfatta med 3 poänger

1. **Det här är ett exekverbart ramverk, inte bara dokumentation**
2. **AI används inom en tydlig struktur med roller, SOP:er, RACI och artefakter**
3. **Resultatet blir både användbart och spårbart**

### Det här ska publiken ta med sig

"Det centrala att ta med sig är att detta inte handlar om att låta en agent improvisera fram utvecklingsarbete."

"Det handlar om att göra utvecklingsflödet explicit nog för att både människor och agenter ska kunna arbeta inom samma struktur."

"Det gör det möjligt att börja enkelt och sedan successivt öka robusthet, standardisering och automation."

---

## Om tiden blir knapp

Prioritera i denna ordning:

1. `README.md`
2. `framework/standard/INDEX.md`
3. ett konkret exempel i `Kravställning`
4. CLI-körning
5. `runs/test-01/output/INDEX.md`

Hoppa över djupdykning i enskilda RACI-tabeller eller enskilda artifact templates om du märker att publiken redan förstått modellen.

## Om publiken vill gå djupare tekniskt

Bra spår att öppna vid frågor:

- hur optional artifacts fungerar
- hur approvals / consultations / informed briefs lagras
- hur output index byggs upp
- hur ett processsteg laddas från `framework/standard`
- skillnaden mellan ramverk (`framework/`) och exekvering (`runs/`)

## En enkel minnesregel under presentationen

Om du känner att du tappar tråden, gå tillbaka till denna sekvens:

**Varför -> Process -> Ansvar -> Instruktion -> Körning -> Resultat**

Det är den röda tråden i hela demon.
