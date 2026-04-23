# Roadmap

## PR 1: Initial kärnfunktionalitet

- **Branch**: 01-business-analyst-agent
- **Mål**: Göra nuvarande ramverk robust och användbart.
  [X] Agent körs via terminal
  [X] LLM-agentadapter används
  [X] LLM används för generering
  [X] Minst 1 artifakt genereras korrekt
  [X] Output sparas som markdown

## PR 2 Orkestring med ramverk

- **Branch**: agent-orchestration-framework
- **Mål**: Nyttja Microsoft Agent Framework och MS Foundry

[X] Microsoft Agent Framework används i implementationen
[X] Minst en andra agentroll finns och kan köras i samma flöde
[X] Nyttjar ramverk i docs för orkestrering av agenter och artifakter
[X] Enkel agentminnesmodell används i körningen
[X] Körning och resultat är spårbara i `runs/`

## PR 3: Agenter för komplett RACI

- **Branch**: raci-consultation-approval-and-informing
- **Mål**: Konsultering och godkännande flöde på plats

[X] RACI används aktivt av orchestratorn för att styra konsultation, godkännande och informing
[X] `Verksamhetsexperter` kan använda run-specifik expertkontext
[X] `Produktägare` kan fatta explicit beslut med motivering
[X] Minnesfiler och statefiler sparas under `runs/`

## PR 4: Målarkitektur som processsteg

- **Branch**: malarkitektur-process-step
- **Mål**: Generaliserar processen för ramverksfunktionalitet

[X] **ett end-to-end-spår** producerar och lagrar artefakter för Målarkitektur enligt filkonventioner som redan gäller för Kravställning.
[X] Resultat och val av processsteg är **spårbara** i `runs/<run-id>/`

## PR 5: ?

- **Branch**:
- **Mål**: Göra ramverk och resultat lättare att ta till sig som åhörare

[ ] Flytta runs folder till eget github repo ligger i ../valuestream-os-data
[X] Gränssnitt Landningssida i markdown för att läsa och navigera framework-ramverket
[X] Gränssnitt Landningssida i markdown för att läsa och navigera run-resultatet via interim `runs/INDEX.md`
[X] Möjliggöra flera ramverk (standard och light) - docs döps om till framework/standard

## Etapp 4: Plattform och skala

Mål: göra lösningen mer flexibel och driftsbar.
[ ] Välja model(er) och förstå kostnader, qoutas etc.... Kunna exekvera gratis
[ ] Stöd för OpenAI
[ ] Stöd för OpenRouter och MiniMax https://openrouter.ai/models?q=minimax
[ ] Modellval, kostnadsstyrning och fallback-strategier

## Roadmap

[ ] Fungerande flöde för Roadmap

## Etapp 5: Bygg övergripande behov

[ ] Skapa Övergripande Behov genom att ställa massor av frågor till användaren

## Etapp 5: Bygga och publicera fungerande kod

[ ] Planering steg 1 och 2
[ ] Bygga kod: branch, koda och testa (använda claude?), commit, pull request
[ ] Piplineflöde: Kodgranskning, test, integration och bygg, demo, release
[ ] Uppdaterad dokumentation

## Etapp 6: Retrospektiv och feedback

[ ]

## Övrigt

[ ] Beroenden av artifakter skall kunna vara frivilligt, alltså inte tvingande för vissa. Om dom finns så används dom annars försöker agenten klara sig utan.
