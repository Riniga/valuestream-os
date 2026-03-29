# Artefaktberoenden (Kravställning + Målarkitektur)

Diagrammet bygger på `## 3. Input` och `## 4. Output` i respektive SOP under `docs/SOP/`. Pil **A → B** betyder att artefakt **B** (output) i den aktuella SOP:en listar **A** som input.

**Obs:** I SOP `05_create_user_stories` anges *Affärsmål & värdebild* som input; SOP `02_affarsmal_och_vardebild` har i nuvarande text endast *Vision & målbild* som output. I diagrammet är det modellerat som att *Vision & målbild* täcker det behov som SOP 5 uttrycker (ev. dokumentationsglapp).

**Obs:** SOP `10_prioritera_backlog` nämner *Risker* som input utan motsvarande artefakt-output i andra SOP:er — den noden är utelämnad här.

```mermaid
flowchart TB
  subgraph krav ["1. Kravställning"]
    direction TB
    OB["Övergripande behov"]
    VM["Vision & målbild"]
    SA["Scope & avgränsningar"]
    SK["Stakeholderkarta"]
    BK["Beroendekarta"]
    US["User Stories"]
    DMk["Domänmodell"]
    BMk["Begreppsmodell"]
    UJ["User journeys"]
    SM["Story map"]
    FB["Funktionella block"]
    EC["Epics & Capabilities"]
    PB["Prioriterad backlog"]
    KPI["KPI / värdemått"]
    UM["Uppföljningsmodell"]
  end

  subgraph mal ["2. Målarkitektur"]
    direction TB
    AM["Arkitekturmål"]
    AP["Arkitekturprinciper"]
    SL["Systemlandskap"]
    DMm["Domänmodell"]
    BMm["Begreppsmodell"]
    IA["Integrationsarkitektur"]
    IP["Integrationspunkter"]
    API["API-specifikation"]
    DD["Datamodell"]
    DA["Dataägarskap"]
    SAK["Säkerhetsarkitektur"]
    SP["Säkerhetsprinciper"]
    NFR["Icke-funktionella krav (NFR)"]
    TP["Teknisk plattform"]
    MZ["Målarkitektur"]
  end

  OB --> VM
  OB --> VM
  VM --> SA
  OB --> SA
  VM --> EC
  OB --> EC
  SA --> SK
  VM --> SK
  SA --> BK
  VM --> BK
  VM --> US
  SA --> US
  SK --> US
  SK --> DMk
  US --> DMk
  SK --> BMk
  US --> BMk
  DMk --> UJ
  US --> UJ
  SK --> UJ
  UJ --> OB
  UJ --> SM
  DMk --> SM
  OB --> SM
  UJ --> FB
  DMk --> FB
  OB --> FB
  SM --> EC
  US --> EC
  EC --> PB
  VM --> PB
  VM --> KPI
  PB --> KPI
  SM --> KPI
  VM --> UM
  PB --> UM
  SM --> UM

  OB --> AM
  VM --> AM
  SA --> AM
  OB --> AP
  VM --> AP
  SA --> AP
  AM --> SL
  OB --> SL
  BK --> SL
  SL --> DMm
  BMm --> DMm
  SL --> BMm
  BMm --> BMm
  SL --> IA
  DMm --> IA
  DD --> IA
  SL --> IP
  DMm --> IP
  DD --> IP
  IA --> API
  DMm --> API
  DMm --> DD
  API --> DD
  IA --> DD
  DMm --> DA
  API --> DA
  IA --> DA
  DD --> SAK
  IA --> SAK
  AM --> SAK
  DD --> SP
  IA --> SP
  AM --> SP
  AM --> AP
  SAK --> AP
  IA --> AP
  DD --> AP
  API --> AP
  AP --> NFR
  DD --> NFR
  SAK --> NFR
  AP --> TP
  NFR --> TP
  IP --> TP
  AP --> MZ
  NFR --> MZ
  IP --> MZ
  SL --> MZ
  DMm --> MZ
  IA --> MZ
  API --> MZ
  DD --> MZ
  SAK --> MZ
  TP --> MZ

  DMk -.->|"samma begrepp som"| DMm
  BMk -.->|"samma begrepp som"| BMm
```

## Cykler och “rundgång” (kärnan i problemet)

Följande beroenden bildar **cykler** i målarkitekturdelen (siffror = SOP-ordning i `2. Målarkitektur`):

1. **Domänmodell ↔ Begreppsmodell** — SOP 3 tar in *Begreppsmodell* och producerar både *Domänmodell* och uppdaterad *Begreppsmodell* (`Begreppsmodell` → `Begreppsmodell`).
2. **Domänmodell ↔ Integrationsarkitektur ↔ Datamodell ↔ API-specifikation** — SOP 4 kräver *Datamodell* innan *Integrationsarkitektur*; SOP 5–6 kräver *Integrationsarkitektur* / *API-specifikation* för *Datamodell*. Det är en **klassisk parallell design-loop** som i praktiken kräver iteration, grov nivå först eller avgränsad “spike”.

Pilarna ovan är **alla** explicita input→output från SOP:erna; cyklerna syns som att samma noder nås via olika vägar fram och tillbaka.
