# Output Index

Denna fil beskriver hur `INDEX.md` ska se ut när den publiceras i en run under `runs/<run-id>/output/`.

Syftet är att ge en enkel ingång till run-resultatet utan att läsaren först behöver förstå alla tekniska metadatafiler eller öppna varje outputfil manuellt.

---

## Vad filen ska innehålla

Den publicerade indexfilen ska sammanfatta:

- run-id, status och senast körd process
- vilka huvudartefakter som har genererats
- hur resultatet fördelar sig över processens fem steg
- vilka metadatafiler som finns i run-roten
- en enkel sammanfattning av approvals, consultations och briefs utan att alla dessa filer måste listas i detalj

---

## Struktur för publicerad fil

### 1. Runsammanfattning

En kort tabell med till exempel:

- `Run ID`
- `Status`
- `Senast körd process`
- antal huvudartefakter
- antal approval-filer
- antal consultation-filer
- antal brief-filer

### 2. Run-metadata

En enkel lista över de viktigaste metadatafilerna i run-roten, till exempel:

- `run_state.json`
- `artifact_state.json`
- `run_log.json`
- `approval_decisions.json`
- `consultation_requests.json`
- `consultation_responses.json`
- `expert_context.json`
- `informed_role_briefs.json`
- `human_tasks/` om sådana finns

Här ska varje fil beskrivas kort så att läsaren förstår varför den finns.

### 3. Genererat innehåll per processsteg

Resultatet ska grupperas enligt processens fem steg:

- `1. Kravställning`
- `2. Målarkitektur`
- `3. Roadmap`
- `4. Leverans`
- `5. Repeat`

För varje processsteg ska filen visa:

- vilka huvudartefakter som finns för steget
- vilken delprocess de hör till
- en enkel sammanfattning av kompletterande filer:
  - approval-filer
  - consultation-filer
  - brief-filer

Om inget ännu har publicerats för ett processsteg ska det framgå tydligt.

### 4. Övriga filer i output

Om det finns filer i `output/` som inte är huvudartefakter eller standardiserade approval/consultation/brief-filer ska de listas i en separat sektion.

### 5. Att läsa först

Avsluta med kort vägledning:

- börja med huvudartefakterna
- använd metadatafilerna för status, spårbarhet och körhistorik
- gå till approval-, consultation- och brief-filer först när fördjupning behövs

---

## Publicering

Denna indexfil ska publiceras automatiskt under körning till:

`runs/<run-id>/output/INDEX.md`

Den ska uppdateras löpande så att den speglar runnens aktuella läge.

---

## Principer

- Visa allt viktigt som genereras i en run, men utan att överlasta läsaren.
- Lyft huvudartefakter först, detaljspårbarhet sen.
- Gruppera alltid enligt processens fem steg.
- Använd enkla relativa länkar så att indexfilen går att använda direkt i run-mappen.
