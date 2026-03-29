# Artefaktberoenden (Kravställning + Målarkitektur)

Diagrammet bygger på `## 3. Input` och `## 4. Output` i respektive SOP under `docs/SOP/`. Pil **A → B** betyder att artefakt **B** (output) i den aktuella SOP:en listar **A** som input.

**Obs:** I SOP `05_create_user_stories` anges *Affärsmål & värdebild* som input; SOP `02_affarsmal_och_vardebild` har i nuvarande text endast *Vision & målbild* som output. I diagrammet antas att *Vision & målbild* täcker det behov som SOP 5 uttrycker (ev. dokumentationsglapp).

**Obs:** SOP `10_prioritera_backlog` nämner *Risker* som input utan motsvarande artefakt-output i andra SOP:er — den noden är utelämnad här.

**Domänmodell** och **Begreppsmodell** är **en nod vardera** (samma artefakt förekommer i både Kravställning och Målarkitektur).

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
    UJ["User journeys"]
    SM["Story map"]
    FB["Funktionella block"]
    EC["Epics & Capabilities"]
    PB["Prioriterad backlog"]
    KPI["KPI / värdemått"]
    UM["Uppföljningsmodell"]
  end

  DM["Domänmodell"]
  BM["Begreppsmodell"]

  subgraph mal ["2. Målarkitektur"]
    direction TB
    AM["Arkitekturmål"]
    AP["Arkitekturprinciper"]
    SL["Systemlandskap"]
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
  SK --> DM
  US --> DM
  SK --> BM
  US --> BM
  DM --> UJ
  US --> UJ
  SK --> UJ
  UJ --> OB
  UJ --> SM
  DM --> SM
  OB --> SM
  UJ --> FB
  DM --> FB
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
  SL --> DM
  BM --> DM
  SL --> BM
  BM --> BM
  SL --> IA
  DM --> IA
  DD --> IA
  SL --> IP
  DM --> IP
  DD --> IP
  IA --> API
  DM --> API
  DM --> DD
  API --> DD
  IA --> DD
  DM --> DA
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
  DM --> MZ
  IA --> MZ
  API --> MZ
  DD --> MZ
  SAK --> MZ
  TP --> MZ
```

## Cykler och “rundgång”

| Cykel | Förklaring |
|--------|------------|
| **BM → BM** | SOP *Definiera domänmodell* (målarkitektur) listar *Begreppsmodell* som både input och output — iteration av samma artefakt. |
| **DM ↔ BM ↔ SL** | *Systemlandskap* matar *Domänmodell* / *Begreppsmodell*; *Domänmodell* och *Begreppsmodell* återkopplar till varandra via samma SOP. |
| **DM → IA → API → DD → IA** (och varianter) | SOP *Integrationsarkitektur* kräver *Datamodell*; *API-struktur* kräver *Integrationsarkitektur* och *Domänmodell*; *Datamodell* kräver *API-specifikation* och *Integrationsarkitektur*. Det är en **större cykel** mellan integration, API och data som kräver grov→fin iteration eller parallellt arbete med temporära antaganden. |
| **AP → … → AP** | *Arkitekturprinciper* produceras tidigt (SOP 1) och **fastställs** igen i SOP 8 med input från bl.a. *Säkerhetsarkitektur*, *Datamodell*, *API-specifikation* — samma artefaktnamn, två “varv”. |
| **MZ → (indirekt)** | *Målarkitektur* (slutartefakt) sammanför alla tidigare; *Teknisk plattform* (SOP 10) producerar också *Målarkitektur* som output — överlapp/två varv mot samma slutdokument. |

Kravställning har dessutom **UJ → OB** (*User journeys* producerar *Övergripande behov*), vilket skapar återkoppling till tidigare kravsteg (behov fördjupas efter journeys).
