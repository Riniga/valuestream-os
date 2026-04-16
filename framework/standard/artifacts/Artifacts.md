# Artefaktberoenden

Skapande av artifakter sker i en bestämd ordning. Beroenden framgår av bilder i diagrammen nedan.

## Kravställning

```mermaid
flowchart

  OB["Beställning"]
  subgraph mal[" "]

    VM["Vision & målbild"]
    SA["Scope & avgränsningar"]
    SK["Stakeholderkarta"]
    SB["Strukturerad backlog"]
    KPI["KPI / värdemått"]

  end

    OB --> VM
    VM --> SA

    SA --> SK

    VM --> SB
    SA --> SB

    VM --> KPI


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

## Roadmap

```mermaid
flowchart
  subgraph mal[" "]
    MP["MVP-definition"]
    RP["Releasepaket"]
    RPl["Releaseplan"]
    RM["Roadmap"]
    SP["Sekvensplan"]
  end

  SM["Story map"]
  EC["Epics & Capabilities"]
  VM["Vision & målbild"]
  BK["Beroendekarta"]
  PB["Prioriterad backlog"]

  DM["Domänmodell"]
  IA["Integrationsarkitektur"]


  SM --> MP
  EC --> MP
  VM --> MP
  SM --> RP
  MP --> RP
  EC --> RP
  RP --> RPl
  MP --> RPl
  BK --> RPl
  RP --> RM
  PB --> RM
  BK --> RM
  RP --> PB

  MP --> PB

  RP --> SP
  DM --> SP
  IA --> SP

  SP --> BK





```
