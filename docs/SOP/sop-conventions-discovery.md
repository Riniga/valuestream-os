# SOP Conventions Discovery

Found 45 SOP file(s).

## Section frequency

- 1. Syfte: 44
- 2. Kontext: 44
- 3. Input: 44
- 4. Output: 44
- 5. RACI: 44
- 6. Arbetssteg: 44

## RACI roles

- R: Business Analyst, Dataarkitekt, DevOps, Lösningsarkitekt, Scrum Master, Teknisk Lead, Testare, UX, Utvecklare
- A: Enterprise Arkitekt, Lösningsarkitekt, Produktägare, Teknisk Lead
- C: Användarrepresentanter, Dataarkitekt, DevOps, Lösningsarkitekt, Produktägare, Projektledare, Teknisk Lead, UX, Utvecklare, Verksamhetsexperter
- I: Business Analyst, Lösningsarkitekt, Produktägare, Projektledare, Utvecklare, Verksamhetsexperter

## Artifacts (output)

- API-specifikation
- Arkitekturinsikter
- Arkitekturmål
- Arkitekturprinciper
- Begreppsmodell
- Beroendekarta
- Cykelstart-brief
- Datamodell
- Dataägarskap
- Demo-underlag
- Deployment
- Dokumentation
- Domänmodell
- Epics & Capabilities
- Feedback
- Funktionella block
- Funktionella förbättringar
- Förbättringsförslag
- Icke-funktionella krav (NFR)
- Integrationsarkitektur
- Integrationspunkter
- KPI / värdemått
- Kod för granskning
- Kodförbättringar
- Kravställningsunderlag
- Leveransutvärdering
- MVP-definition
- Målarkitektur
- Prioriterad backlog
- Processförbättringar
- Produktinkrement
- Ready backlog
- Release notes
- Releasepaket
- Releaseplan
- Retrospektiv
- Roadmap
- Roadmap-input
- Roadmap-justering
- Scope & avgränsningar
- Sekvensplan
- Sprint backlog
- Sprintmål
- Stakeholderkarta
- Story map
- Systemlandskap
- Säkerhetsarkitektur
- Säkerhetsprinciper
- Teknisk plattform
- Tekniska förbättringar
- Testresultat
- Uppföljningsmodell
- User Stories
- User journeys
- Verifierad funktionalitet
- Vision & målbild
- Övergripande behov

## Artifacts (input)

- API-specifikation
- Arkitekturinsikter
- Arkitekturmål
- Arkitekturprinciper
- Begreppsmodell
- Beroendekarta
- CI/CD-pipeline
- Datamodell
- Deployment
- Dokumentation
- Domänmodell
- Epics & Capabilities
- Feedback
- Förbättringsförslag
- Icke-funktionella krav (NFR)
- Integrationsarkitektur
- Integrationspunkter
- KPI / värdemått
- Kod för granskning
- Leveransutvärdering
- MVP-definition
- Miljökonfiguration
- Prioriterad backlog
- Produktinkrement
- Ready backlog
- Release notes
- Releasepaket
- Releaseplan
- Retrospektiv
- Risker
- Roadmap-input
- Scope & avgränsningar
- Sprint backlog
- Sprintmål
- Stakeholderkarta
- Story map
- Systemlandskap
- Säkerhetsarkitektur
- Teamkapacitet (behåll som egen artefakt)
- Teknisk plattform
- Tekniska hinder
- Teststrategi
- User Stories
- User journeys
- Verifierad funktionalitet
- Verksamhetsregler
- Vision & målbild
- Övergripande behov

## SOP files with missing expected sections

- docs\SOP\sop-conventions-discovery.md: missing 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg

## SOP samples

### docs\SOP\1.Kravställning\01_vision_och_malbild.md

- title: Vision & målbild
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Övergripande behov
- output: Vision & målbild
- raci: R=1, A=1, C=1, I=1

### docs\SOP\1.Kravställning\02_affarsmal_och_vardebild.md

- title: Affärsmål & värdebild
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Övergripande behov
- output: Vision & målbild
- raci: R=1, A=1, C=1, I=1

### docs\SOP\1.Kravställning\03_scope_och_avgransningar.md

- title: Scope & avgränsningar
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Vision & målbild, Övergripande behov
- output: Scope & avgränsningar, Epics & Capabilities, Scope & avgränsningar
- raci: R=1, A=1, C=2, I=1

### docs\SOP\1.Kravställning\04_stakeholderkarta.md

- title: Stakeholder-karta
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Scope & avgränsningar, Vision & målbild
- output: Stakeholderkarta, Beroendekarta
- raci: R=1, A=1, C=2, I=1

### docs\SOP\1.Kravställning\05_domananalys.md

- title: Domänanalys
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Stakeholderkarta, User Stories, Verksamhetsregler
- output: Domänmodell, Begreppsmodell
- raci: R=1, A=1, C=1, I=1

### docs\SOP\1.Kravställning\06_user_journeys.md

- title: User Journeys / huvudflöden
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Domänmodell, User Stories, Stakeholderkarta
- output: User journeys, Övergripande behov
- raci: R=1, A=1, C=2, I=1

### docs\SOP\1.Kravställning\07_skapa_story_map.md

- title: Skapa Story Map
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: User journeys, Domänmodell, Övergripande behov
- output: Story map, Funktionella block
- raci: R=1, A=1, C=2, I=1

### docs\SOP\1.Kravställning\08_gruppera_i_epics_och_capabilities.md

- title: Gruppera i epics & capabilities
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Story map, User Stories
- output: Epics & Capabilities
- raci: R=1, A=1, C=1, I=1

### docs\SOP\1.Kravställning\09_prioritera_backlog.md

- title: Prioritera backlog (hög nivå)
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Epics & Capabilities, Vision & målbild, Risker
- output: Prioriterad backlog
- raci: R=1, A=1, C=1, I=1

### docs\SOP\1.Kravställning\10_definiera_framgangskriterier.md

- title: Definiera framgångskriterier (KPI)
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Vision & målbild, Prioriterad backlog, Story map
- output: KPI / värdemått, Uppföljningsmodell
- raci: R=1, A=1, C=1, I=1

### docs\SOP\2. Målarkitektur\01_Etablera arkitekturmål.md

- title: Etablera arkitekturmål
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Övergripande behov, Vision & målbild, Scope & avgränsningar
- output: Arkitekturmål, Arkitekturprinciper
- raci: R=1, A=1, C=2, I=1

### docs\SOP\2. Målarkitektur\02_Definiera systemlandskap.md

- title: Definiera systemlandskap
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Arkitekturmål, Övergripande behov, Beroendekarta
- output: Systemlandskap
- raci: R=1, A=1, C=2, I=1

### docs\SOP\2. Målarkitektur\03_Definiera domänmodell.md

- title: Definiera domänmodell
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Systemlandskap, Begreppsmodell, Verksamhetsregler
- output: Domänmodell, Begreppsmodell
- raci: R=1, A=1, C=1, I=1

### docs\SOP\2. Målarkitektur\04_Definiera integrationsarkitektu.md

- title: Definiera integrationsarkitektur
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Systemlandskap, Domänmodell, Datamodell
- output: Integrationsarkitektur, Integrationspunkter
- raci: R=1, A=1, C=1, I=1

### docs\SOP\2. Målarkitektur\05_Definiera API‑struktur.md

- title: Definiera API-struktur
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Integrationsarkitektur, Domänmodell
- output: API-specifikation
- raci: R=1, A=1, C=2, I=1

### docs\SOP\2. Målarkitektur\06_Definiera datamodell.md

- title: Definiera datamodell (hög nivå)
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Domänmodell, API-specifikation, Integrationsarkitektur
- output: Datamodell, Dataägarskap
- raci: R=1, A=1, C=1, I=1

### docs\SOP\2. Målarkitektur\07_Definiera säkerhetsarkitektur.md

- title: Definiera säkerhetsarkitektur
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Datamodell, Integrationsarkitektur, Arkitekturmål
- output: Säkerhetsarkitektur, Säkerhetsprinciper
- raci: R=1, A=1, C=2, I=1

### docs\SOP\2. Målarkitektur\08_Fastställ arkitekturprinciper.md

- title: Fastställ arkitekturprinciper
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Arkitekturmål, Säkerhetsarkitektur, Integrationsarkitektur, Datamodell, API-specifikation
- output: Arkitekturprinciper
- raci: R=1, A=1, C=2, I=1

### docs\SOP\2. Målarkitektur\09_Definiera NFR.md

- title: Definiera NFR
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Arkitekturprinciper, Datamodell, Säkerhetsarkitektur
- output: Icke-funktionella krav (NFR)
- raci: R=1, A=1, C=2, I=1

### docs\SOP\2. Målarkitektur\10_Definiera teknisk plattform.md

- title: Definiera teknisk plattform
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Arkitekturprinciper, Icke-funktionella krav (NFR), Integrationspunkter
- output: Teknisk plattform, Målarkitektur
- raci: R=1, A=1, C=2, I=1

### docs\SOP\2. Målarkitektur\11\_ Dokumentera målarkitektur.md

- title: Dokumentera målarkitektur
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Systemlandskap, Domänmodell, Integrationsarkitektur, API-specifikation, Datamodell, Säkerhetsarkitektur, Teknisk plattform
- output: Målarkitektur
- raci: R=1, A=1, C=2, I=1

### docs\SOP\3. Roadmap\01_skapa_mvp.md

- title: Skapa MVP
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Story map, Epics & Capabilities, Vision & målbild
- output: MVP-definition
- raci: R=1, A=1, C=2, I=1

### docs\SOP\3. Roadmap\02_Strukturera story map till leveranspaket.md

- title: Strukturera story map till leveranspaket
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Story map, MVP-definition, Epics & Capabilities
- output: Releasepaket
- raci: R=1, A=1, C=1, I=1

### docs\SOP\3. Roadmap\03_Skapa releaseplan.md

- title: Skapa releaseplan
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Releasepaket, MVP-definition, Beroendekarta
- output: Releaseplan
- raci: R=1, A=1, C=2, I=1

### docs\SOP\3. Roadmap\04_Skapa produktroadmap.md

- title: Skapa produktroadmap
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Releaseplan, Prioriterad backlog, Beroendekarta
- output: Roadmap
- raci: R=1, A=1, C=2, I=1

### docs\SOP\3. Roadmap\05_Prioritera funktionalitet.md

- title: Prioritera funktionalitet
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Releasepaket, Beroendekarta, MVP-definition, KPI / värdemått
- output: Prioriterad backlog
- raci: R=1, A=1, C=2, I=1

### docs\SOP\3. Roadmap\06_Identifiera tekniska beroenden.md

- title: Identifiera tekniska beroenden
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Releasepaket, Domänmodell, Integrationsarkitektur
- output: Beroendekarta, Sekvensplan
- raci: R=1, A=1, C=1, I=1

### docs\SOP\4. Leverans\01_backlog_refinement.md

- title: Backlog refinement
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Prioriterad backlog, Feedback, Arkitekturinsikter
- output: User Stories, Ready backlog
- raci: R=1, A=1, C=1, I=1

### docs\SOP\4. Leverans\02_sprintplanering.md

- title: Sprintplanering
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Ready backlog, Teamkapacitet (behåll som egen artefakt), Prioriterad backlog
- output: Sprintmål, Sprint backlog
- raci: R=1, A=1, C=1, I=1

### docs\SOP\4. Leverans\03_utveckling.md

- title: Utveckling
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Sprint backlog, Arkitekturprinciper, Arkitekturprinciper
- output: Produktinkrement, Kod för granskning
- raci: R=1, A=1, C=1, I=1

### docs\SOP\4. Leverans\04_kodgranskning.md

- title: Kodgranskning
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Kod för granskning, Arkitekturprinciper, Arkitekturprinciper
- output: Verifierad funktionalitet, Kodförbättringar
- raci: R=1, A=1, C=1, I=1

### docs\SOP\4. Leverans\05_test.md

- title: Test
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Verifierad funktionalitet, User Stories, Teststrategi
- output: Testresultat, Verifierad funktionalitet
- raci: R=1, A=1, C=1, I=1

### docs\SOP\4. Leverans\06_integration_och_bygg.md

- title: Integration & bygg (CI/CD)
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Verifierad funktionalitet, CI/CD-pipeline, Miljökonfiguration
- output: Produktinkrement, Demo-underlag
- raci: R=1, A=1, C=1, I=1

### docs\SOP\4. Leverans\07_demo.md

- title: Demo
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Produktinkrement, Sprintmål
- output: Feedback, Verifierad funktionalitet
- raci: R=1, A=1, C=1, I=1

### docs\SOP\4. Leverans\08_release.md

- title: Release
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Verifierad funktionalitet, Releasepaket
- output: Releasepaket, Release notes
- raci: R=1, A=1, C=2, I=1

### docs\SOP\4. Leverans\09_deployments.md

- title: Deployments
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Releasepaket, Miljökonfiguration
- output: Produktinkrement, Deployment
- raci: R=1, A=1, C=1, I=1

### docs\SOP\4. Leverans\10_uppdatera_dokumentation.md

- title: Uppdatera dokumentation
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Release notes, Produktinkrement, API-specifikation
- output: Dokumentation
- raci: R=1, A=1, C=1, I=1

### docs\SOP\4. Leverans\11_uppfoljning_och_forbattring.md

- title: Uppföljning & förbättring
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Deployment, Dokumentation, Feedback, Produktinkrement
- output: Förbättringsförslag, Retrospektiv
- raci: R=1, A=1, C=1, I=1

### docs\SOP\5. Repeat\01_utvardera_leveransresultat.md

- title: Utvärdera leveransresultat
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Produktinkrement, Feedback, Release notes, KPI / värdemått
- output: Leveransutvärdering, Funktionella förbättringar
- raci: R=1, A=1, C=1, I=1

### docs\SOP\5. Repeat\02_utvardera_process_och_arbetssatt.md

- title: Utvärdera process & arbetssätt
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Produktinkrement, Tekniska hinder, Leveransutvärdering
- output: Retrospektiv, Processförbättringar
- raci: R=1, A=1, C=1, I=1

### docs\SOP\5. Repeat\03_samla_input_for_uppdaterad_kravstallning.md

- title: Samla input för uppdaterad kravställning
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Leveransutvärdering, Retrospektiv, Feedback, Förbättringsförslag, Övergripande behov, Förbättringsförslag
- output: Kravställningsunderlag
- raci: R=1, A=1, C=1, I=1

### docs\SOP\5. Repeat\04_identifiera_arkitekturella_lardomar.md

- title: Identifiera arkitekturella lärdomar
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Tekniska hinder, Tekniska hinder, Leveransutvärdering
- output: Arkitekturinsikter, Tekniska förbättringar
- raci: R=1, A=1, C=1, I=1

### docs\SOP\5. Repeat\05_Förbereda nästa roadmap‑iteration.md

- title: Förbereda nästa roadmap-iteration
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Arkitekturinsikter, Beroendekarta, Risker, Prioriterad backlog
- output: Roadmap-input, Roadmap-justering
- raci: R=1, A=1, C=2, I=1

### docs\SOP\5. Repeat\06_Förbereda nästa cykel.md

- title: Förbereda nästa cykel
- sections: 1. Syfte, 2. Kontext, 3. Input, 4. Output, 5. RACI, 6. Arbetssteg
- input: Arkitekturinsikter, Roadmap-input, Förbättringsförslag
- output: Kravställningsunderlag, Cykelstart-brief
- raci: R=1, A=1, C=2, I=1

### docs\SOP\sop-conventions-discovery.md

- title: None
- sections:
- input: (none)
- output: (none)
- raci: R=0, A=0, C=0, I=0
