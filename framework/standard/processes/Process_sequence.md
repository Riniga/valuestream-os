## Processflöde

Detta sekvensdiagram visar **hur roller/agenter tar vid och skapar huvudartefakterna i ordning** genom en hel processcykel.

Det är en förenklad bild som fokuserar på:

- vilken roll som driver nästa steg
- vilka huvudartefakter som skapas
- hur resultat från ett steg blir input till nästa

```mermaid
sequenceDiagram
    participant BE as Beställare
    participant PO as Produktägare
    participant BA as Business Analyst
    participant LA as Lösningsarkitekt
    participant TL as Teknisk Lead
    participant SM as Scrum Master
    participant UT as Utvecklare
    participant TE as Testare
    participant DE as DevOps
    participant EA as Enterprise Arkitekt

    rect rgb(245,248,255)
        Note over BE,PO: 1. Kravställning
        BE->>BE: Skapar Beställning
        BE->>BA: Överlämnar Beställning
        BA->>BA: Skapar Vision & målbild
        BA->>BA: Skapar Omfattning och Strukturerad Backlog
        BA->>BA: Skapar Stakeholderkarta
        BA->>BA: Skapar KPI / värdemått
        BA->>PO: Förankrar kravbild
        PO-->>BA: Godkännande / återkoppling
    end

    rect rgb(248,255,248)
        Note over BA,EA: 2. Målarkitektur
        BA->>LA: Överlämnar kravunderlag
        LA->>LA: Skapar Arkitekturmål
        LA->>LA: Skapar Systemlandskap
        BA->>BA: Skapar Domänmodell
        BA->>LA: Överlämnar Domänmodell
        LA->>TL: Inhämtar teknisk input
        TL-->>LA: Beroenden och genomförbarhet
        LA->>LA: Skapar Integrationsarkitektur
        LA->>LA: Uppdaterar Arkitekturprinciper
        LA->>LA: Definierar Icke-funktionella krav
        LA->>LA: Sammanställer Målarkitektur
        LA->>EA: Förankrar målarkitektur
        EA-->>LA: Godkännande / återkoppling
    end

    rect rgb(255,250,240)
        Note over BA,TL: 3. Roadmap
        LA->>BA: Överlämnar Målarkitektur
        BA->>BA: Skapar Roadmap
        BA->>TL: Beställer teknisk plan
        TL->>TL: Skapar Teknisk plan
        TL-->>BA: Teknisk plan
        BA->>BE: Förankrar Roadmap
        BE-->>BA: Prioritering / godkännande
    end

    rect rgb(255,245,245)
        Note over BA,DE: 4. Leverans
        BA->>SM: Överlämnar Roadmap och backlog
        SM->>SM: Skapar Sprint backlog
        SM->>UT: Planerar iteration
        UT->>UT: Skapar Produktinkrement
        UT->>TE: Överlämnar för test
        TE->>TE: Skapar Testresultat
        TE-->>UT: Verifierad leverans
        UT->>DE: Överlämnar releasbart inkrement
        DE->>DE: Skapar Releasepaket och genomför release
        DE-->>BE: Levererad funktionalitet
        BA->>BA: Uppdaterar Dokumentation
        SM->>SM: Skapar Förbättringsförslag
    end

    rect rgb(245,245,255)
        Note over BA,EA: 5. Repeat
        BA->>BA: Skapar Leveransutvärdering
        SM->>SM: Skapar Processförbättringar
        LA->>LA: Skapar Arkitekturinsikter
        BA->>BA: Skapar Cykelstart-brief
        BA-->>BE: Underlag för nästa cykel
    end
```

## Att tänka på i presentation

- Diagrammet visar **process- och artefaktflödet**, inte kodflödet.
- Fokus är på huvudartefakterna, inte alla möjliga mellanleverabler.
- Samma logik kan användas både när rollerna utförs av människor och när de utförs av agenter.
- Den viktiga rörelsen är: **behov -> kravbild -> målarkitektur -> roadmap -> leverans -> lärande -> nästa cykel**.
