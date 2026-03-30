# Artefaktberoenden (Kravställning + Målarkitektur)

Skapande av artifakter sker i en bestämd ordning. Beroenden framgår av bilder i diagrammen nedan.

## Kravställning

```mermaid
flowchart LR
  subgraph mal[" "]
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
    DM["Domänmodell"]
    BM["Begreppsmodell"]
  end

    OB --> VM
    OB --> SA
    OB --> EC

    VM --> SA
    VM --> EC

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


```

## Målarkitektur

```mermaid
flowchart
  subgraph mal[" "]
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

  DM["Domänmodell"]
  BM["Begreppsmodell"]
  OB["Övergripande behov"]
  VM["Vision & målbild"]
  SA["Scope & avgränsningar"]
  BK["Beroendekarta"]


  OB --> AP
  OB --> SL
  OB --> AM

  VM --> AM
  SA --> AM

  VM --> AP
  SA --> AP
  AM --> SL

  BK --> SL
  SL --> DM
  BM --> DM
  SL --> BM
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
